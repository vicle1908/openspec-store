#!/opt/homebrew/bin/python3
"""Compare value-blind pre/post configuration manifests.

Schema contract:
  - baseline: the retained schema-v1 `pre-apply-manifest.json` (no `schema`
    field, no `model_ids`) or any schema-v2 producer capture; both accepted.
    A missing `model_ids` map in a v1 baseline normalizes to empty.
  - candidate: schema-v2 producer output only; a v1-shaped candidate is
    rejected.

The manifest producer extracts only provider/model/default identities,
endpoint/dialect metadata, file modes, and hashes. This comparator rejects
secret-named fields holding non-environment-reference values and any
secret-looking value. Credential-name enforcement applies to the terminal
field key of each walked path, so a provider identifier such as
``custom_shopapikey`` inside an ancestor path is a map key, not a secret
field.

Surface contracts (mutually exclusive per path):

  - registered (externally owned, `--drift-register`): the candidate must
    record exactly the registered current state (sha + mode); registered
    paths are exempt from this change's rollback/backup/creation contracts
    because their mutation and rollback belong to their owning change. Any
    drift beyond the registered state fails (re-register required). This
    covers baseline-existing drifted files, baseline-absent files created by
    their owner, and glob-captured extras outside the baseline files map.

  - deferred (credential-rotation gate): declared in
    `deferred_targets`, not in `changed_paths`, baseline-existing,
    backup-free, and live bytes/mode still equal the frozen baseline.

  - changed: declared in `changed_paths`; requires a baseline-anchored
    rollback record with a mode-600 backup whose hash equals the baseline
    bytes (or the pre-approved new-file mode for created files).

  - preserved: baseline-existing, none of the above; must remain byte-and-
    mode identical to the baseline with a `not-required-preserved` rollback
    record carrying no backup claim.

Rollback expectations are derived from the baseline `files` map (existence,
mode, sha256) — never from planning-only backup hashes in the baseline and
never from current live bytes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

SECRET_VALUE = re.compile(r"(?i)(?:sk-|xai-|pmv_|agt_|bearer\s+|authorization\s*:)")
SECRET_KEY = re.compile(r"(?i)(?:api.?key|token|secret|password|credential)")
ENV_REFERENCE = re.compile(r"^(?:\$\{?[A-Z][A-Z0-9_]*\}?|[A-Z][A-Z0-9_]*)$")
PROTECTED_SELECTOR_SCALARS = {
    "default", "default_model", "defaultModel", "defaultProvider",
    "defaultThinkingLevel", "model_provider", "model", "active_provider",
    "lastUsedProvider", "default_reasoning_effort",
}


def walk(obj: Any, path: str = "$") -> Any:
    if isinstance(obj, dict):
        for key, value in obj.items():
            yield from walk(value, f"{path}.{key}")
    elif isinstance(obj, list):
        for i, value in enumerate(obj):
            yield from walk(value, f"{path}[{i}]")
    else:
        yield path, obj


def terminal_key(path: str) -> str:
    """Return the actual dictionary key at the end of a walk path."""
    segment = path.rsplit(".", 1)[-1]
    return segment.split("[", 1)[0].rstrip("]")


def assert_safe(data: Any, label: str) -> None:
    for path, value in walk(data):
        key = terminal_key(path)
        if SECRET_KEY.search(key):
            if not isinstance(value, str) or not ENV_REFERENCE.fullmatch(value):
                raise SystemExit(f"{label}: secret-named field must be an environment reference: {path}")
        if isinstance(value, str) and SECRET_VALUE.search(value):
            raise SystemExit(f"{label}: secret-looking value is not allowed: {path}")


def normalize_str_map(value: Any, label: str, failures: list[str]) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    if not isinstance(value, dict):
        failures.append(f"{label} must be a product-to-string-array map")
        return out
    for product, ids in value.items():
        if isinstance(ids, list) and all(isinstance(item, str) for item in ids):
            out[product] = list(ids)
        else:
            failures.append(f"{label} entry must be a string array: {product}")
    return out


def expected_new_file_mode(path: str) -> str:
    return "0o700" if Path(path).name.endswith("-key.sh") else "0o600"


def load_register(path: Path | None) -> dict[str, dict[str, Any]]:
    if path is None:
        return {}
    if not path.is_file():
        raise SystemExit(f"drift register missing: {path}")
    data = json.loads(path.read_text())
    if not isinstance(data, dict) or not isinstance(data.get("entries"), list):
        raise SystemExit("drift register must contain an entries array")
    registered: dict[str, dict[str, Any]] = {}
    for entry in data["entries"]:
        if not isinstance(entry, dict):
            raise SystemExit("every drift-register entry must be an object")
        reg_path = entry.get("path")
        state = entry.get("current_state")
        if not isinstance(reg_path, str) or not isinstance(state, dict):
            raise SystemExit("every drift-register entry requires path and current_state")
        if not state.get("exists") or not isinstance(state.get("sha256"), str) or not isinstance(state.get("mode"), str):
            raise SystemExit(f"registered entry must record an existing current state: {reg_path}")
        if reg_path in registered:
            raise SystemExit(f"duplicate drift-register entry: {reg_path}")
        registered[reg_path] = state
    return registered


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument(
        "--drift-register",
        type=Path,
        default=None,
        help="value-blind drift register for externally owned surfaces (registered-paths acceptance)",
    )
    parser.add_argument(
        "--overlay-contract",
        type=Path,
        default=None,
        help="overlay contract carrying approved per-product provider-id migration allowlists",
    )
    args = parser.parse_args()
    baseline = json.loads(args.baseline.read_text())
    candidate = json.loads(args.candidate.read_text())
    if not isinstance(baseline, dict) or not isinstance(candidate, dict):
        raise SystemExit("manifests must be objects")
    assert_safe(baseline, "baseline")
    assert_safe(candidate, "candidate")

    base_schema = baseline.get("schema", 1)
    if base_schema not in {1, 2}:
        raise SystemExit(f"baseline manifest schema {base_schema!r} is not supported")
    cand_schema = candidate.get("schema", 1)
    if cand_schema != 2:
        raise SystemExit(f"candidate manifest must be schema 2, found {cand_schema!r}")

    failures: list[str] = []
    base_files = baseline.get("files", {})
    cand_files = candidate.get("files", {})
    if not isinstance(base_files, dict) or not isinstance(cand_files, dict):
        raise SystemExit("files must be path-to-metadata maps")

    raw_changed = candidate.get("changed_paths", baseline.get("changed_paths", []))
    if not isinstance(raw_changed, list) or not all(isinstance(x, str) for x in raw_changed):
        raise SystemExit("changed_paths must be a string array")
    changed_paths = set(raw_changed)

    raw_deferred = candidate.get("deferred_targets", [])
    if not isinstance(raw_deferred, list) or not all(isinstance(x, str) for x in raw_deferred):
        raise SystemExit("deferred_targets must be a string array")
    deferred_targets = set(raw_deferred)
    unknown_deferred = sorted(deferred_targets - set(base_files))
    if unknown_deferred:
        failures.append(f"deferred_targets outside baseline target set: {unknown_deferred}")
    for path in sorted(deferred_targets & changed_paths):
        failures.append(f"deferred target also declared in changed_paths: {path}")
    for path in sorted(deferred_targets):
        if base_files.get(path, {}).get("exists") is not True:
            failures.append(f"deferred target is not a baseline-existing file: {path}")

    registered = load_register(args.drift_register)

    expected_new_modes = candidate.get("expected_new_file_modes", {})
    if not isinstance(expected_new_modes, dict):
        failures.append("expected_new_file_modes must be a path-to-mode map")
        expected_new_modes = {}
    unknown_expected = sorted(set(expected_new_modes) - set(base_files))
    if unknown_expected:
        failures.append(f"expected_new_file_modes outside baseline target set: {unknown_expected}")
    unknown_changed = sorted(changed_paths - set(base_files))
    if unknown_changed:
        failures.append(f"changed_paths outside baseline target set: {unknown_changed}")

    extra_files = sorted(set(cand_files) - set(base_files) - set(registered))
    if extra_files:
        failures.append(f"candidate manifest contains undeclared files: {extra_files}")

    # Registered surfaces: the candidate must equal the registered current
    # state exactly; ownership contracts below are skipped for these paths.
    for path, reg_state in sorted(registered.items()):
        cand_meta = cand_files.get(path)
        if not isinstance(cand_meta, dict) or not cand_meta.get("exists"):
            failures.append(f"registered externally-owned path missing from candidate: {path}")
            continue
        if cand_meta.get("sha256") != reg_state.get("sha256") or cand_meta.get("mode") != reg_state.get("mode"):
            failures.append(f"registered path changed since register capture (re-register required): {path}")

    # Approved migration allowlists (overlay contract): the reconciliation
    # replaces Droid's stale cross-dialect route (sh/Claude-Fable on an OpenAI
    # provider) with the correct PM Anthropic Messages route. The contract
    # records the exact provider-id set the approved migration removes; the
    # comparator accepts those removals ONLY as an exact set, only for the
    # contract product, and only while that product's target file is in
    # changed_paths. Any other removal anywhere stays a hard failure, and a
    # declared-but-not-applied allowlist also fails.
    allowed_removals: dict[str, set[str]] = {}
    removal_targets: dict[str, str] = {}
    if args.overlay_contract is not None:
        contract = json.loads(args.overlay_contract.read_text())
        if not isinstance(contract, dict) or not isinstance(contract.get("entries"), list):
            raise SystemExit("overlay contract must contain an entries array")
        for entry in contract["entries"]:
            if not isinstance(entry, dict):
                raise SystemExit("every overlay contract entry must be an object")
            removals = entry.get("allowed_provider_id_removals")
            if removals is None:
                continue
            product = entry.get("product")
            target = entry.get("target")
            if not isinstance(product, str) or not product:
                raise SystemExit("overlay contract entry with allowed_provider_id_removals requires product")
            if not isinstance(target, str) or not target:
                raise SystemExit(f"overlay contract entry with allowed_provider_id_removals requires target: {product}")
            if not isinstance(removals, list) or not removals or not all(isinstance(x, str) for x in removals):
                raise SystemExit(f"allowed_provider_id_removals must be a non-empty string array: {product}")
            if product in allowed_removals:
                raise SystemExit(f"duplicate overlay contract product: {product}")
            expanded = str(Path.home()) + target[1:] if target.startswith("~") else target
            allowed_removals[product] = set(removals)
            removal_targets[product] = expanded

    base_providers = normalize_str_map(baseline.get("provider_ids", {}), "baseline provider_ids", failures)
    cand_providers = normalize_str_map(candidate.get("provider_ids", {}), "candidate provider_ids", failures)
    for product in sorted(set(allowed_removals) - set(base_providers)):
        failures.append(f"{product}: migration allowlist for a product absent from the baseline provider inventory")
    for product, ids in base_providers.items():
        missing_set = set(ids) - set(cand_providers.get(product, []))
        if product in allowed_removals:
            target = removal_targets[product]
            if target not in changed_paths:
                failures.append(f"{product}: provider-removal allowlist requires its target in changed_paths: {target}")
            if missing_set != allowed_removals[product]:
                failures.append(
                    f"{product}: provider removals {sorted(missing_set)} do not equal the approved migration set {sorted(allowed_removals[product])}"
                )
        elif missing_set:
            failures.append(f"{product}: providers removed: {sorted(missing_set)}")

    # A schema-v1 baseline carries no model inventory; model preservation is
    # vacuous against it and enforced whenever the baseline records models.
    base_models = normalize_str_map(baseline.get("model_ids", {}), "baseline model_ids", failures)
    cand_models = normalize_str_map(candidate.get("model_ids", {}), "candidate model_ids", failures)
    for product, ids in base_models.items():
        missing = sorted(set(ids) - set(cand_models.get(product, [])))
        if missing:
            failures.append(f"{product}: model IDs removed: {missing}")

    base_defaults = baseline.get("defaults", {})
    cand_defaults = candidate.get("defaults", {})
    if not isinstance(base_defaults, dict) or not isinstance(cand_defaults, dict):
        failures.append("defaults must be product-to-value maps")
        base_defaults = {}
        cand_defaults = {}
    for product, default in base_defaults.items():
        cand_value = cand_defaults.get(product)
        if isinstance(default, dict):
            # Nested default maps (provider_metadata, modelRoles, retry) use
            # subset preservation: every baseline entry must survive with an
            # equal value; additions are permitted because any addition
            # implies a byte change on that product's file, which is gated
            # elsewhere (changed_paths for write targets, byte equality for
            # preserved files, register equality for registered surfaces).
            if not isinstance(cand_value, dict):
                failures.append(f"{product}: default changed")
            else:
                for key, value in default.items():
                    if cand_value.get(key) != value:
                        failures.append(f"{product}: default changed ({key})")
                        break
        elif cand_value != default:
            failures.append(f"{product}: default changed")

    base_selector_hashes = baseline.get("default_selector_hashes", {})
    cand_selector_hashes = candidate.get("default_selector_hashes", {})
    if not isinstance(base_selector_hashes, dict) or not isinstance(cand_selector_hashes, dict):
        failures.append("default_selector_hashes must be maps")
        base_selector_hashes = {}
        cand_selector_hashes = {}
    def selector_group(defaults_map: dict, product: str) -> dict:
        """Mirror the producer's protected-field grouping for one product."""
        grouped = {}
        for key, value in defaults_map.items():
            if "." not in key:
                continue
            prod, field = key.split(".", 1)
            if prod != product:
                continue
            if (
                field in PROTECTED_SELECTOR_SCALARS
                or field.startswith("models.")
                or field.startswith("sessionDefaultSettings.")
                or field in {"modelRoles", "retry"}
            ):
                grouped[field] = value
        return grouped

    def selector_digest(group: dict) -> str:
        return hashlib.sha256(json.dumps(group, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

    def project_group(base_value, cand_value):
        """Recursive baseline projection for one selector value.

        dict: project only the baseline's keys recursively; candidate-side
        additions are ignored. scalar/list: take the candidate value whole.
        Returns None when a baseline key is missing or a dict/scalar shape
        is violated (caller treats None as a hard mismatch).
        """
        if isinstance(base_value, dict):
            if not isinstance(cand_value, dict):
                return None
            out = {}
            for key, sub_base in base_value.items():
                if key not in cand_value:
                    return None
                sub = project_group(sub_base, cand_value[key])
                if sub is None:
                    return None
                out[key] = sub
            return out
        return cand_value

    for product, digest in base_selector_hashes.items():
        # Baseline projection semantics: the candidate's protected selector
        # group may GAIN fields or nested keys (additions are gated by the
        # file-byte contracts: changed_paths / preserved byte equality /
        # register equality), but every baseline field must survive with an
        # equal value. The candidate's recorded hash must be self-consistent
        # with its own full group; the recursive baseline projection of that
        # group must reproduce the baseline digest.
        base_group = selector_group(base_defaults, product)
        if selector_digest(base_group) != digest:
            failures.append(f"{product}: baseline selector hash is not reproducible from baseline defaults")
            continue
        cand_group = selector_group(cand_defaults, product)
        cand_hash = cand_selector_hashes.get(product)
        if not isinstance(cand_hash, str) or cand_hash != selector_digest(cand_group):
            failures.append(f"{product}: candidate selector hash does not match its own defaults")
            continue
        missing = sorted(set(base_group) - set(cand_group))
        if missing:
            failures.append(f"{product}: protected selector fields removed: {missing}")
            continue
        projected = project_group(base_group, cand_group)
        if projected is None or selector_digest(projected) != digest:
            failures.append(f"{product}: protected selector fragment changed")
    for product in set(cand_selector_hashes) - set(base_selector_hashes):
        failures.append(f"{product}: unexpected protected selector fragment")

    base_launchers = normalize_str_map(baseline.get("launchers", {}), "baseline launchers", failures)
    cand_launchers = normalize_str_map(candidate.get("launchers", {}), "candidate launchers", failures)
    for path, identifiers in base_launchers.items():
        if path in registered:
            # externally owned shell surface: launcher inventory changes
            # belong to the owner; acceptance is register re-capture.
            continue
        missing = sorted(set(identifiers) - set(cand_launchers.get(path, [])))
        if missing:
            failures.append(f"{path}: launcher identifiers removed: {missing}")

    raw_tightenings = candidate.get("allowed_mode_tightenings", [])
    if not isinstance(raw_tightenings, list) or not all(isinstance(x, str) for x in raw_tightenings):
        failures.append("allowed_mode_tightenings must be a string array")
        raw_tightenings = []
    allowed_tightenings = set(raw_tightenings)
    for path in allowed_tightenings:
        base_mode = base_files.get(path, {}).get("mode")
        cand_mode = cand_files.get(path, {}).get("mode")
        if base_mode != "0o644" or cand_mode != "0o600":
            failures.append(f"invalid mode tightening declaration: {path}")

    # Rollback expectations derived from the baseline files map.
    cand_rollback = candidate.get("rollback", {})
    if not isinstance(cand_rollback, dict):
        failures.append("rollback must be a path-to-metadata map")
        cand_rollback = {}
    for path in base_files:
        if path in registered:
            continue  # externally owned: no rollback contract for this change
        base_meta = base_files[path]
        if not isinstance(base_meta, dict):
            failures.append(f"baseline file metadata must be an object: {path}")
            continue
        record = cand_rollback.get(path)
        if not isinstance(record, dict):
            failures.append(f"rollback metadata missing: {path}")
            continue
        if not base_meta.get("exists"):
            if record.get("backup_status") == "deferred-pending-credential-rotation":
                failures.append(f"baseline-absent file cannot be deferred: {path}")
            if record.get("rollback_action") != "delete-created-file":
                failures.append(f"new file rollback action is not delete-created-file: {path}")
            if record.get("backup_required") is not False or record.get("backup_sha256") is not None:
                failures.append(f"new file must not claim a backup: {path}")
            created = bool(cand_files.get(path, {}).get("exists"))
            declared = path in expected_new_modes or path in changed_paths
            if created or declared:
                expected = expected_new_file_mode(path)
                if expected_new_modes.get(path) != expected:
                    failures.append(f"created or declared new file lacks pre-approved mode {expected}: {path}")
                if created and cand_files[path].get("mode") != expected:
                    failures.append(f"created file has wrong pre-approved mode: {path}")
            continue
        if record.get("backup_status") == "deferred-pending-credential-rotation":
            cand_meta = cand_files.get(path, {})
            ok_deferred = (
                path in deferred_targets
                and path not in changed_paths
                and record.get("backup_required") is False
                and record.get("backup_sha256") is None
                and record.get("backup_mode") is None
                and cand_meta.get("sha256") == base_meta.get("sha256")
                and cand_meta.get("mode") == base_meta.get("mode")
            )
            if not ok_deferred:
                failures.append(
                    f"invalid deferred rollback record (must be declared, unchanged vs baseline, backup-free): {path}"
                )
            continue
        if path not in changed_paths:
            # Preserved baseline-existing file: no backup claim is required or
            # allowed; bytes/mode equality is enforced in the files loop.
            if record.get("backup_status") != "not-required-preserved":
                failures.append(f"preserved file must have not-required-preserved rollback status: {path}")
            if (
                record.get("backup_required") is not False
                or record.get("backup_sha256") is not None
                or record.get("backup_mode") is not None
                or record.get("backup_location") is not None
            ):
                failures.append(f"preserved file must not claim a backup: {path}")
            continue
        if record.get("rollback_action") != "restore-baseline-bytes":
            failures.append(f"existing file rollback action is not restore-baseline-bytes: {path}")
        if record.get("backup_mode") != "0o600":
            failures.append(f"rollback backup mode is not 600: {path}")
        status = record.get("backup_status")
        backup_hash = record.get("backup_sha256")
        if status != "created":
            failures.append(f"rollback backup not created (status={status!r}): {path}")
        if not isinstance(backup_hash, str) or not re.fullmatch(r"[0-9a-f]{64}", backup_hash):
            failures.append(f"rollback backup is not recorded with a full hash: {path}")
        elif backup_hash != base_meta.get("sha256"):
            failures.append(f"rollback backup does not match baseline bytes: {path}")

    for path, metadata in base_files.items():
        if path in registered:
            continue  # registered state equality already enforced above
        if path not in cand_files:
            failures.append(f"file missing from candidate manifest: {path}")
            continue
        if not isinstance(metadata, dict) or not isinstance(cand_files[path], dict):
            failures.append(f"file metadata must be an object: {path}")
            continue
        if not metadata.get("exists"):
            cand_exists = bool(cand_files[path].get("exists"))
            declared = path in expected_new_modes
            if path in changed_paths and not cand_exists:
                failures.append(f"changed_paths declares a baseline-absent file that was not created: {path}")
            if cand_exists and not declared:
                failures.append(f"created baseline-absent file lacks mode pre-approval: {path}")
            elif declared:
                expected = expected_new_file_mode(path)
                if expected_new_modes.get(path) != expected:
                    failures.append(f"declared new file mode does not match required {expected}: {path}")
                if cand_exists:
                    if cand_files[path].get("mode") != expected:
                        failures.append(f"created file has wrong pre-approved mode: {path}")
                else:
                    failures.append(f"expected new file missing: {path}")
            continue
        if cand_files[path].get("exists") is False:
            failures.append(f"file disappeared: {path}")
            continue
        if path in expected_new_modes:
            failures.append(f"existing file listed as expected-new: {path}")
        base_mode = metadata.get("mode")
        cand_mode = cand_files[path].get("mode")
        if base_mode != cand_mode:
            if path not in allowed_tightenings or not (base_mode == "0o644" and cand_mode == "0o600"):
                failures.append(f"file mode changed without approved tightening: {path}")
        if path not in changed_paths and metadata.get("sha256") != cand_files[path].get("sha256"):
            failures.append(f"unowned file bytes changed: {path}")

    print(f"MANIFEST baseline={args.baseline} candidate={args.candidate} value_blind=true registered={len(registered)}")
    failures = list(dict.fromkeys(failures))
    if failures:
        for failure in failures:
            print("FAIL", failure)
        print(f"SUMMARY FAIL findings={len(failures)}")
        return 1
    print("CHECK provider-preservation: PASS")
    print("CHECK default-preservation: PASS")
    print("CHECK file-existence-and-mode: PASS")
    print("CHECK rollback-anchored-to-baseline: PASS")
    print("CHECK registered-surfaces-equal-register: PASS")
    print("CHECK preserved-and-deferred-contracts: PASS")
    print("SUMMARY PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
