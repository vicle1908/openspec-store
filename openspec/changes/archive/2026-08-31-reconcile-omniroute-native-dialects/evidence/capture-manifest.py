#!/opt/homebrew/bin/python3
"""Capture a value-blind configuration manifest for the reconciliation.

Only paths, existence, mode, byte hashes, provider identifiers, and default
selectors are retained. File contents and credential values are never emitted.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import subprocess
import tomllib
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None

HOME = Path.home()


def jsonc_load(path: Path) -> Any:
    text = path.read_text()
    out: list[str] = []
    i = 0
    in_string = False
    escaped = False
    while i < len(text):
        ch = text[i]
        if in_string:
            out.append(ch)
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == '"':
                in_string = False
            i += 1
            continue
        if ch == '"':
            in_string = True
            out.append(ch)
            i += 1
            continue
        if ch == "/" and i + 1 < len(text) and text[i + 1] == "/":
            i += 2
            while i < len(text) and text[i] != "\n":
                i += 1
            continue
        if ch == "/" and i + 1 < len(text) and text[i + 1] == "*":
            i += 2
            while i + 1 < len(text) and text[i : i + 2] != "*/":
                i += 1
            i += 2
            continue
        out.append(ch)
        i += 1
    return json.loads("".join(out))


def yaml_load(path: Path) -> Any:
    if yaml is not None:
        return yaml.safe_load(path.read_text())
    completed = subprocess.run(
        ["/usr/bin/ruby", "-rjson", "-ryaml", "-e", "puts JSON.generate(YAML.load_file(ARGV[0]))", str(path)],
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )
    if completed.returncode != 0:
        return None
    return json.loads(completed.stdout)

TARGETS: dict[str, list[Path]] = {
    "claude-code": [HOME / ".claude/settings.json", HOME / ".claude/profiles/omniroute.json", HOME / ".claude/helpers/omniroute-key.sh", HOME / ".zshrc"],
    "codex": [HOME / ".codex/config.toml", HOME / ".codex/omniroute.config.toml"],
    "grok": [HOME / ".grok/config.toml"],
    "goose": [HOME / ".config/goose/config.yaml", HOME / ".config/goose/custom_providers/custom_omniroute.json", HOME / ".config/goose/custom_providers/custom_omniroute_sh.json", HOME / ".config/goose/custom_providers/custom_omniroute_anthropic.json", HOME / ".config/goose/custom_providers/custom_omniroute_responses.json"],
    "kimi-code": [HOME / ".kimi-code/config.toml"],
    "kilo": [HOME / ".config/kilo/kilo.jsonc"],
    "opencode": [HOME / ".config/opencode/opencode.json"],
    "pi": [HOME / ".pi/agent/models.json", HOME / ".pi/agent/settings.json"],
    "prime-agent": [HOME / ".prime/agent/models.json", HOME / ".prime/agent/settings.json"],
    "droid": [HOME / ".factory/settings.json"],
    "omp": [HOME / ".omp/agent/models.yml", HOME / ".omp/agent/config.yml"],
    "cline": [HOME / ".cline/data/settings/providers.json"],
}


def target_paths(product: str, paths: list[Path]) -> list[Path]:
    expanded = list(paths)
    if product == "claude-code":
        expanded.extend(sorted((HOME / ".claude/profiles").glob("*.json")))
        expanded.extend(sorted((HOME / ".claude/helpers").glob("*.sh")))
    elif product == "goose":
        expanded.extend(sorted((HOME / ".config/goose/custom_providers").glob("*.json")))
    elif product == "prime-agent":
        expanded.extend(sorted((HOME / ".prime/agent").glob("*.json")))
    unique: dict[str, Path] = {str(path): path for path in expanded}
    return [unique[key] for key in sorted(unique)]


def parse(path: Path) -> Any:
    text = path.read_text(errors="replace")
    if path.suffix == ".json":
        return json.loads(text)
    if path.suffix == ".toml":
        return tomllib.loads(text)
    if path.suffix in {".yaml", ".yml"}:
        return yaml_load(path)
    if path.suffix == ".jsonc":
        return jsonc_load(path)


def file_metadata(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {"exists": False, "mode": None, "sha256": None, "bytes": 0}
    raw = path.read_bytes()
    return {
        "exists": True,
        "mode": oct(stat.S_IMODE(path.stat().st_mode)),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "bytes": len(raw),
    }


def provider_ids(data: Any, path: Path) -> list[str]:
    if not isinstance(data, dict):
        return []
    if path.name == "config.toml" and path.parent.name in {".codex", ".grok", ".kimi-code"}:
        for key in ("model_providers", "providers"):
            value = data.get(key)
            if isinstance(value, dict):
                return sorted(str(x) for x in value)
    if path.parent.name == "profiles" and path.suffix == ".json":
        profile_id = path.stem
        model = data.get("model")
        values = [f"profile:{profile_id}"]
        if isinstance(model, str) and model:
            values.append(f"profile:{profile_id}:model:{model}")
        return values
    if path.name in {"models.json", "opencode.json", "kilo.jsonc", "settings.json"}:
        for key in ("providers", "provider"):
            value = data.get(key)
            if isinstance(value, dict):
                return sorted(str(x) for x in value)
        if path.name == "settings.json" and isinstance(data.get("customModels"), list):
            ids = {str(x.get("provider")) for x in data["customModels"] if isinstance(x, dict) and x.get("provider")}
            ids.update(
                f"{x.get('provider')}:{x.get('model')}"
                for x in data["customModels"]
                if isinstance(x, dict) and x.get("provider") and x.get("model")
            )
            ids.update(
                f"{x.get('provider')}:{x.get('id')}"
                for x in data["customModels"]
                if isinstance(x, dict) and x.get("provider") and x.get("id")
            )
            return sorted(ids)
    if path.name == "config.yaml":
        value = data.get("providers") if isinstance(data, dict) else None
        if isinstance(value, dict):
            return sorted(str(x) for x in value)
    if path.parent.name == "custom_providers" and path.suffix == ".json":
        name = data.get("name")
        return [str(name)] if isinstance(name, str) and name else []
    if path.name == "models.yml":
        value = data.get("providers") if isinstance(data, dict) else None
        if isinstance(value, dict):
            return sorted(str(x) for x in value)
    if path.name == "providers.json":
        value = data.get("providers")
        if isinstance(value, dict):
            return sorted(str(x) for x in value)
    return []


def defaults(data: Any, path: Path) -> dict[str, Any]:
    if not isinstance(data, dict):
        return {}
    # A named profile is selectable route metadata, not the CLI's default.
    if path.name == "omniroute.config.toml" or path.parent.name == "profiles":
        return {}
    result: dict[str, Any] = {}
    scalar_keys = (
        "default", "default_model", "defaultModel", "defaultProvider",
        "defaultThinkingLevel", "model_provider", "model", "active_provider",
        "lastUsedProvider", "default_reasoning_effort",
    )
    for key in scalar_keys:
        value = data.get(key)
        if isinstance(value, (str, int, float, bool)) or value is None and key in data:
            result[key] = value
    if isinstance(data.get("models"), dict):
        for key in ("default", "web_search", "session_summary"):
            if key in data["models"]:
                result[f"models.{key}"] = data["models"][key]
    if isinstance(data.get("sessionDefaultSettings"), dict):
        for key in ("model", "reasoningEffort", "autonomyLevel", "autonomyMode", "interactionMode"):
            if key in data["sessionDefaultSettings"]:
                result[f"sessionDefaultSettings.{key}"] = data["sessionDefaultSettings"][key]
    if isinstance(data.get("providers"), dict):
        provider_defaults = {}
        for name, provider in data["providers"].items():
            if isinstance(provider, dict):
                selected = {}
                for key in ("model", "enabled", "configured", "api", "baseUrl", "base_url", "wire_api", "api_backend"):
                    if key in provider and isinstance(provider[key], (str, int, float, bool)):
                        selected[key] = provider[key]
                if selected:
                    provider_defaults[str(name)] = selected
        if provider_defaults:
            result["provider_metadata"] = provider_defaults
    if path.name in {"config.yml", "config.yaml"}:
        for key in ("modelRoles", "retry"):
            if key in data:
                result[key] = data[key]
    if path.name in {"custom_omniroute.json", "custom_omniroute_sh.json"} and isinstance(data.get("name"), str):
        result["provider_name"] = data["name"]
    return result


def model_ids(data: Any, path: Path) -> list[str]:
    if not isinstance(data, dict):
        return []
    values: set[str] = set()
    models = data.get("models")
    if isinstance(models, dict):
        values.update(str(key) for key in models)
    aliases = data.get("model")
    if isinstance(aliases, dict):
        values.update(str(key) for key in aliases)
    custom = data.get("customModels")
    if isinstance(custom, list):
        for item in custom:
            if isinstance(item, dict):
                for key in ("id", "model"):
                    if isinstance(item.get(key), str):
                        values.add(item[key])
    providers = data.get("providers")
    if isinstance(providers, dict):
        for provider_name, provider in providers.items():
            if isinstance(provider, dict):
                nested = provider.get("models")
                if isinstance(nested, dict):
                    values.update(f"{provider_name}:{key}" for key in nested)
                if isinstance(provider.get("model"), str):
                    values.add(f"{provider_name}:{provider['model']}")
    if path.parent.name == "profiles" and isinstance(data.get("model"), str):
        values.add(f"profile:{path.stem}:{data['model']}")
    return sorted(values)


def launcher_metadata(path: Path) -> list[str]:
    if path.name != ".zshrc" or not path.is_file():
        return []
    text = path.read_text(errors="replace")
    functions = re.findall(r"(?m)^([A-Za-z_][A-Za-z0-9_-]*)\s*\(\)\s*\{", text)
    env_surfaces = re.findall(r"(?m)\b(COPILOT_PROVIDER_[A-Z0-9_]+|COPILOT_MODEL)\b", text)
    return sorted(set(functions + env_surfaces))


def parse_mode_map(entries: list[str]) -> dict[str, str]:
    result: dict[str, str] = {}
    for entry in entries:
        if "=" not in entry:
            raise SystemExit(f"expected mode must use PATH=MODE: {entry}")
        path, mode = entry.split("=", 1)
        mode = mode.strip()
        if mode not in {"0o600", "0o700"}:
            raise SystemExit(f"unsupported expected mode {mode!r} for {path}")
        result[path] = mode
    return result


def rollback_metadata(
    files: dict[str, Any],
    baseline_files: dict[str, Any] | None,
    backup_root: str | None = None,
    deferred: set[str] | None = None,
    changed: set[str] | None = None,
) -> dict[str, dict[str, Any]]:
    """Rollback metadata anchored to the baseline, not the live state.

    Classification per path (baseline-anchored):
      - deferred (credential-rotation gate): baseline-existing, backup/apply
        postponed — status deferred-pending-credential-rotation, backup-free;
      - changed: baseline-existing and in the changed set — backup required;
        with a backup root the recorded hash must equal the on-disk backup;
      - preserved: baseline-existing, not changed, not deferred — status
        not-required-preserved, no backup claim (the file is not written by
        this change);
      - created: baseline-absent — delete-created-file, no backup.

    Without a baseline (planning-only captures), classification falls back to
    the live state exactly as before.
    """
    result = {}
    root = Path(backup_root).expanduser() if backup_root else None
    deferred = deferred or set()
    changed = changed or set()
    # Fail closed BEFORE the loop: a deferred target that is not part of the
    # captured file set must abort the capture — previously it was silently
    # ignored (rc 0), which the D9 fixture exposed (2026-08-31).
    unknown_deferred = deferred - set(files)
    if unknown_deferred:
        raise SystemExit(
            f"deferred target not captured in this manifest's file set: {sorted(unknown_deferred)}")
    for path in sorted(files):
        name = Path(path).name or "target"
        backup_name = hashlib.sha256(path.encode()).hexdigest()[:16] + "-" + name
        if baseline_files is not None:
            base_record = baseline_files.get(path)
            exists = bool(base_record.get("exists")) if isinstance(base_record, dict) else False
        else:
            exists = bool(files[path].get("exists"))
        expected_new_mode = "0o700" if name.endswith("-key.sh") else "0o600"
        is_deferred = path in deferred
        is_changed = path in changed
        if is_deferred:
            if not exists:
                raise SystemExit(f"deferred target is not a baseline-existing file: {path}")
            record: dict[str, Any] = {
                "transition": "existing-to-modified-or-preserved",
                "rollback_action": "restore-baseline-bytes",
                "expected_new_mode": None,
                "backup_required": False,
                "backup_mode": None,
                "backup_location_template": None,
                "backup_status": "deferred-pending-credential-rotation",
                "backup_sha256": None,
            }
        elif exists and is_changed:
            record = {
                "transition": "existing-to-modified-or-preserved",
                "rollback_action": "restore-baseline-bytes",
                "expected_new_mode": None,
                "backup_required": True,
                "backup_mode": "0o600",
                "backup_location_template": "$HOME/.hermes/backups/reconcile-omniroute-native-dialects/" + backup_name,
                "backup_status": "not-created-planning-only",
                "backup_sha256": None,
            }
            if root is not None:
                location = root / backup_name
                record["backup_location"] = str(location)
                if location.is_file():
                    record["backup_mode"] = oct(stat.S_IMODE(location.stat().st_mode))
                    record["backup_sha256"] = hashlib.sha256(location.read_bytes()).hexdigest()
                    record["backup_status"] = "created" if record["backup_mode"] == "0o600" else "invalid-mode"
                else:
                    record["backup_status"] = "missing"
        elif exists:
            record = {
                "transition": "existing-to-preserved",
                "rollback_action": "restore-baseline-bytes",
                "expected_new_mode": None,
                "backup_required": False,
                "backup_mode": None,
                "backup_location_template": None,
                "backup_status": "not-required-preserved",
                "backup_sha256": None,
            }
        else:
            record = {
                "transition": "absent-to-created",
                "rollback_action": "delete-created-file",
                "expected_new_mode": expected_new_mode,
                "backup_required": False,
                "backup_mode": None,
                "backup_location_template": None,
                "backup_status": "not-applicable-new-file",
                "backup_sha256": None,
            }
        result[path] = record
    return result


def selector_hashes(default_values: dict[str, Any]) -> dict[str, str]:
    grouped: dict[str, dict[str, Any]] = {}
    for key, value in default_values.items():
        if "." not in key:
            continue
        product, field = key.split(".", 1)
        protected = (
            field in {"default", "default_model", "defaultModel", "defaultProvider", "defaultThinkingLevel", "model", "model_provider", "active_provider", "lastUsedProvider", "default_reasoning_effort"}
            or field.startswith("models.")
            or field.startswith("sessionDefaultSettings.")
            or field in {"modelRoles", "retry"}
        )
        if protected:
            grouped.setdefault(product, {})[field] = value
    return {
        product: hashlib.sha256(json.dumps(values, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        for product, values in sorted(grouped.items())
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--changed-path", action="append", default=[])
    parser.add_argument("--allowed-mode-tightening", action="append", default=[])
    parser.add_argument("--expected-new-file-mode", action="append", default=[])
    parser.add_argument("--backup-root", type=Path)
    parser.add_argument(
        "--deferred-target",
        action="append",
        default=[],
        help="Baseline-existing path whose backup/apply is deferred (credential-rotation gate); repeatable",
    )
    parser.add_argument(
        "--baseline-manifest",
        type=Path,
        help="Baseline manifest whose files map anchors rollback classification",
    )
    args = parser.parse_args()
    baseline_files: dict[str, Any] | None = None
    if args.baseline_manifest:
        baseline_data = json.loads(args.baseline_manifest.read_text())
        if not isinstance(baseline_data, dict) or not isinstance(baseline_data.get("files"), dict):
            raise SystemExit("baseline manifest must contain a files map")
        baseline_schema = baseline_data.get("schema", 1)
        if baseline_schema not in {1, 2}:
            raise SystemExit(f"unsupported baseline manifest schema {baseline_schema!r}")
        baseline_files = baseline_data["files"]
    files: dict[str, Any] = {}
    providers: dict[str, list[str]] = {}
    models_inventory: dict[str, list[str]] = {}
    default_values: dict[str, Any] = {}
    launchers: dict[str, list[str]] = {}
    for product, paths in TARGETS.items():
        product_provider_ids: set[str] = set()
        for path in target_paths(product, paths):
            key = str(path)
            files[key] = file_metadata(path)
            if not path.is_file():
                continue
            try:
                data = parse(path)
            except Exception:
                data = None
            product_provider_ids.update(provider_ids(data, path))
            product_model_ids = model_ids(data, path)
            if product_model_ids:
                models_inventory.setdefault(product, []).extend(product_model_ids)
            launcher_ids = launcher_metadata(path)
            if launcher_ids:
                launchers[str(path)] = launcher_ids
            for name, value in defaults(data, path).items():
                default_values[f"{product}.{name}"] = value
        providers[product] = sorted(product_provider_ids)
    models_inventory = {product: sorted(set(values)) for product, values in models_inventory.items()}
    output = {
        "schema": 2,
        "value_blind": True,
        "changed_paths": sorted(set(args.changed_path)),
        "deferred_targets": sorted(set(args.deferred_target)),
        "allowed_mode_tightenings": sorted(set(args.allowed_mode_tightening)),
        "expected_new_file_modes": parse_mode_map(args.expected_new_file_mode),
        "rollback": rollback_metadata(
            files,
            baseline_files,
            str(args.backup_root) if args.backup_root else None,
            deferred=set(args.deferred_target),
            changed=set(args.changed_path),
        ),
        "files": files,
        "provider_ids": providers,
        "model_ids": models_inventory,
        "defaults": default_values,
        "default_selector_hashes": selector_hashes(default_values),
        "launchers": launchers,
    }
    args.output.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")
    print(f"MANIFEST_CAPTURED output={args.output} files={len(files)} value_blind=true")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
