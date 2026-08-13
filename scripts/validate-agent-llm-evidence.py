#!/usr/bin/env python3
"""Validate retained agent-LLM integration evidence against local identity.

The validator is intentionally standard-library-only and read-only by default.
It never imports a target package, resolves dependencies, invokes a provider or
consumer, or reads environment values.  The only optional write is one atomic
JSON result beneath the change-owned ``evidence/results`` directory.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import os
import re
import secrets
import shutil
import subprocess
import sys
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any

CHANGE_NAME = "complete-agent-llm-config-integration"
SCHEMA_VERSION = "1.0.0"
GATES = (
    "handoff_acceptance",
    "evidence_reuse",
    "downstream_unblock",
    "task_completion",
    "live_authorization",
    "live_launch",
    "spec_sync",
    "archive_readiness",
)
LIVE_GATES = {"live_authorization", "live_launch"}
EXIT_CODES = {"current": 0, "stale": 2, "blocked": 3, "invalid": 4}
DECISION_RANK = {"current": 0, "stale": 1, "blocked": 2, "invalid": 3}
HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
CHANGE_RELATIVE = PurePosixPath("openspec") / "changes" / CHANGE_NAME
RESULTS_RELATIVE = CHANGE_RELATIVE / "evidence" / "results"
EXPECTED_ARTIFACTS = {
    "proposal": (CHANGE_RELATIVE / "proposal.md",),
    "specs": tuple(
        CHANGE_RELATIVE / "specs" / capability / "spec.md"
        for capability in (
            "agent-config-resolution",
            "agent-core-model-resolution",
            "agent-docs-sync",
            "cli-provider-profile-resolution",
            "provider-model-profile-resolution",
        )
    ),
    "design": (CHANGE_RELATIVE / "design.md",),
    "tasks": (CHANGE_RELATIVE / "tasks.md",),
}
DIRT_CATEGORIES = {
    "product",
    "test",
    "acceptance_script",
    "generated",
    "other_non_secret",
}
READ_ONLY_GIT_SUBCOMMANDS = {
    "branch",
    "cat-file",
    "merge-base",
    "rev-parse",
    "status",
}


class ContractError(Exception):
    """Raised for malformed or contradictory validator input."""


class LocalIdentityUnavailable(Exception):
    """Raised when required current local identity cannot be resolved."""


class ContractArgumentParser(argparse.ArgumentParser):
    """Raise a redacted contract error instead of printing user input."""

    def error(self, message: str) -> None:
        del message
        raise ContractError("cli_arguments_invalid")


@dataclass(frozen=True)
class Comparison:
    field: str
    expected: Any
    current: Any
    decision: str
    source: str
    code: str
    repository: str | None = None
    global_scope: bool = False
    propagate_repository: bool = False

    def as_json(self) -> dict[str, Any]:
        result = {
            "code": self.code,
            "current": self.current,
            "decision": self.decision,
            "expected": self.expected,
            "field": self.field,
            "source": self.source,
        }
        if self.repository is not None:
            result["repository"] = self.repository
        return result


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


def canonical_output(value: Mapping[str, Any]) -> bytes:
    return canonical_bytes(value) + b"\n"


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ContractError(f"unreadable_json:{type(exc).__name__}") from None
    if not isinstance(value, dict):
        raise ContractError("json_root_not_object")
    return value


def json_type_matches(value: Any, expected: str) -> bool:
    if expected == "object":
        return isinstance(value, dict)
    if expected == "array":
        return isinstance(value, list)
    if expected == "string":
        return isinstance(value, str)
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "null":
        return value is None
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    return False


def resolve_schema_ref(root: Mapping[str, Any], reference: str) -> Mapping[str, Any]:
    if not reference.startswith("#/"):
        raise ContractError("external_schema_ref_forbidden")
    current: Any = root
    for raw_part in reference[2:].split("/"):
        part = raw_part.replace("~1", "/").replace("~0", "~")
        if not isinstance(current, dict) or part not in current:
            raise ContractError("unresolved_schema_ref")
        current = current[part]
    if not isinstance(current, dict):
        raise ContractError("schema_ref_not_object")
    return current


def validate_schema_value(
    value: Any,
    schema: Mapping[str, Any],
    root_schema: Mapping[str, Any],
    *,
    path: str = "$",
) -> list[str]:
    """Validate the JSON-Schema subset used by the versioned contract."""

    if "$ref" in schema:
        referenced = resolve_schema_ref(root_schema, str(schema["$ref"]))
        sibling = {key: item for key, item in schema.items() if key != "$ref"}
        errors = validate_schema_value(value, referenced, root_schema, path=path)
        if sibling:
            errors.extend(validate_schema_value(value, sibling, root_schema, path=path))
        return errors

    if "anyOf" in schema:
        candidates = schema["anyOf"]
        if not isinstance(candidates, list):
            return [f"{path}:schema_anyof_invalid"]
        if any(
            not validate_schema_value(value, candidate, root_schema, path=path)
            for candidate in candidates
            if isinstance(candidate, dict)
        ):
            return []
        return [f"{path}:no_anyof_match"]

    errors: list[str] = []
    expected_type = schema.get("type")
    if expected_type is not None:
        expected_types = (
            [expected_type] if isinstance(expected_type, str) else expected_type
        )
        if not isinstance(expected_types, list) or not all(
            isinstance(item, str) for item in expected_types
        ):
            return [f"{path}:schema_type_invalid"]
        if not any(json_type_matches(value, item) for item in expected_types):
            return [f"{path}:wrong_type"]

    if "const" in schema and value != schema["const"]:
        errors.append(f"{path}:const_mismatch")
    enum = schema.get("enum")
    if isinstance(enum, list) and value not in enum:
        errors.append(f"{path}:enum_mismatch")

    if isinstance(value, str):
        min_length = schema.get("minLength")
        if isinstance(min_length, int) and len(value) < min_length:
            errors.append(f"{path}:too_short")
        pattern = schema.get("pattern")
        if isinstance(pattern, str) and re.search(pattern, value) is None:
            errors.append(f"{path}:pattern_mismatch")

    if isinstance(value, list):
        min_items = schema.get("minItems")
        if isinstance(min_items, int) and len(value) < min_items:
            errors.append(f"{path}:too_few_items")
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for index, item in enumerate(value):
                errors.extend(
                    validate_schema_value(
                        item, item_schema, root_schema, path=f"{path}[{index}]"
                    )
                )

    if isinstance(value, dict):
        required = schema.get("required", [])
        if isinstance(required, list):
            for key in required:
                if isinstance(key, str) and key not in value:
                    errors.append(f"{path}.{key}:missing")
        properties = schema.get("properties", {})
        if not isinstance(properties, dict):
            properties = {}
        additional = schema.get("additionalProperties", True)
        for key, item in value.items():
            child_path = f"{path}.{key}"
            if key in properties and isinstance(properties[key], dict):
                errors.extend(
                    validate_schema_value(
                        item, properties[key], root_schema, path=child_path
                    )
                )
            elif additional is False:
                errors.append(f"{child_path}:additional_property")
            elif isinstance(additional, dict):
                errors.extend(
                    validate_schema_value(
                        item, additional, root_schema, path=child_path
                    )
                )
    return errors


def forbidden_keys(schema: Mapping[str, Any]) -> set[str]:
    policy = schema.get("x-credential-policy")
    if not isinstance(policy, dict):
        return set()
    keys = policy.get("forbidden_keys")
    if not isinstance(keys, list):
        return set()
    return {str(key).casefold() for key in keys}


def find_forbidden_keys(value: Any, forbidden: set[str], path: str = "$") -> list[str]:
    found: list[str] = []
    if isinstance(value, dict):
        for key, item in value.items():
            child = f"{path}.{key}"
            normalized = re.sub(r"[-\s]+", "_", str(key).casefold())
            if normalized in forbidden:
                found.append(f"{child}:forbidden_key")
            found.extend(find_forbidden_keys(item, forbidden, child))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            found.extend(find_forbidden_keys(item, forbidden, f"{path}[{index}]"))
    return found


def run_local(
    argv: Sequence[str],
    *,
    cwd: Path,
    text: bool = True,
    accepted: Iterable[int] = (0,),
) -> subprocess.CompletedProcess[Any]:
    if not argv:
        raise ContractError("subprocess_command_missing")
    executable = Path(str(argv[0])).name
    if executable == "git":
        if len(argv) < 2 or argv[1] not in READ_ONLY_GIT_SUBCOMMANDS:
            raise ContractError("git_subcommand_forbidden")
    elif executable == "openspec":
        if list(argv[1:]) != [
            "status",
            "--change",
            CHANGE_NAME,
            "--json",
            "--store",
            "openspec-store",
        ]:
            raise ContractError("openspec_command_forbidden")
    else:
        raise ContractError("subprocess_executable_forbidden")
    try:
        process = subprocess.run(
            list(argv),
            cwd=cwd,
            check=False,
            capture_output=True,
            text=text,
            stdin=subprocess.DEVNULL,
            timeout=30,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise LocalIdentityUnavailable(type(exc).__name__) from None
    if process.returncode not in set(accepted):
        raise LocalIdentityUnavailable(f"exit_{process.returncode}")
    return process


def git_text(root: Path, *args: str, accepted: Iterable[int] = (0,)) -> str:
    return run_local(
        ["git", *args], cwd=root, text=True, accepted=accepted
    ).stdout.strip()


def git_head(root: Path) -> str:
    return git_text(root, "rev-parse", "HEAD")


def git_branch(root: Path) -> str:
    return git_text(root, "branch", "--show-current")


def normalize_relative_path(value: str) -> PurePosixPath:
    if not isinstance(value, str) or not value:
        raise ContractError("relative_path_missing")
    candidate = PurePosixPath(value)
    if candidate.is_absolute() or ".." in candidate.parts or "." in candidate.parts:
        raise ContractError("unsafe_relative_path")
    return candidate


def path_under(path: Path, root: Path) -> bool:
    try:
        path.resolve(strict=False).relative_to(root.resolve(strict=False))
    except ValueError:
        return False
    return True


def resolved_repository_path(
    root: Path, relative: PurePosixPath, *, require_exists: bool = True
) -> Path:
    try:
        resolved_root = root.resolve(strict=True)
        candidate = (resolved_root / Path(relative)).resolve(strict=require_exists)
    except OSError as exc:
        raise LocalIdentityUnavailable(type(exc).__name__) from None
    if not path_under(candidate, resolved_root):
        raise ContractError("repository_path_escape")
    return candidate


def parse_porcelain_v1_z(payload: bytes) -> list[tuple[bytes, tuple[bytes, ...]]]:
    records = payload.split(b"\0")
    parsed: list[tuple[bytes, tuple[bytes, ...]]] = []
    index = 0
    while index < len(records):
        record = records[index]
        index += 1
        if not record:
            continue
        if len(record) < 4 or record[2:3] != b" ":
            raise LocalIdentityUnavailable("git_status_record_invalid")
        status_bytes = record[:2]
        paths = [record[3:]]
        if b"R" in status_bytes or b"C" in status_bytes:
            if index >= len(records) or not records[index]:
                raise LocalIdentityUnavailable("git_status_pair_invalid")
            paths.append(records[index])
            index += 1
        parsed.append((status_bytes, tuple(paths)))
    return parsed


def porcelain_v1_z_bytes(records: Sequence[tuple[bytes, tuple[bytes, ...]]]) -> bytes:
    parts: list[bytes] = []
    for status_bytes, paths in records:
        parts.append(status_bytes + b" " + paths[0])
        parts.extend(paths[1:])
    return b"" if not parts else b"\0".join(parts) + b"\0"


def git_status_bytes(root: Path, excluded_output: Path | None = None) -> bytes:
    process = run_local(
        ["git", "status", "--porcelain=v1", "-z", "--untracked-files=all"],
        cwd=root,
        text=False,
    )
    payload = bytes(process.stdout)
    if excluded_output is None or not path_under(excluded_output, root):
        return payload
    try:
        excluded = (
            excluded_output.resolve(strict=False)
            .relative_to(root.resolve(strict=True))
            .as_posix()
        )
    except (OSError, ValueError):
        return payload
    excluded_bytes = excluded.encode("utf-8", errors="surrogateescape")
    kept = [
        item
        for item in parse_porcelain_v1_z(payload)
        if excluded_bytes not in set(item[1])
    ]
    return porcelain_v1_z_bytes(kept)


def decoded_porcelain_records(
    payload: bytes,
) -> list[tuple[str, tuple[str, ...]]]:
    return [
        (
            status_bytes.decode("ascii"),
            tuple(path.decode("utf-8", errors="surrogateescape") for path in paths),
        )
        for status_bytes, paths in parse_porcelain_v1_z(payload)
    ]


def current_dirt_inventory(
    *,
    root: Path,
    payload: bytes,
    expected_inventory: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    retained: dict[tuple[str, tuple[str, ...]], Mapping[str, Any]] = {}
    for raw in expected_inventory:
        entry = require_mapping(raw, "dirt_inventory_entry")
        status_text = str(entry.get("status", ""))
        paths = tuple(
            str(path) for path in require_list(entry.get("paths"), "dirt_paths")
        )
        key = (status_text, paths)
        if key in retained:
            raise ContractError("dirt_inventory_duplicate")
        category = str(entry.get("category", ""))
        content_classification = str(entry.get("content_classification", ""))
        if category not in DIRT_CATEGORIES:
            raise ContractError("dirt_category_invalid")
        if content_classification not in {"non_secret", "metadata_only"}:
            raise ContractError("dirt_content_classification_invalid")
        if content_classification == "non_secret" and not isinstance(
            entry.get("content_sha256"), str
        ):
            raise ContractError("dirt_non_secret_hash_missing")
        if (
            content_classification == "metadata_only"
            and entry.get("content_sha256") is not None
        ):
            raise ContractError("dirt_metadata_hash_forbidden")
        retained[key] = entry

    current_records = decoded_porcelain_records(payload)
    current: list[dict[str, Any]] = []
    for status_text, paths in sorted(current_records):
        entry = retained.get((status_text, paths))
        if entry is None:
            current.append(
                {
                    "category": "unclassified",
                    "content_classification": "metadata_only",
                    "content_sha256": None,
                    "paths": list(paths),
                    "status": status_text,
                }
            )
            continue
        item: dict[str, Any] = {
            "category": entry["category"],
            "content_classification": entry["content_classification"],
            "paths": list(paths),
            "status": status_text,
        }
        if entry["content_classification"] == "non_secret":
            content_lines: list[str] = []
            for raw_path in paths:
                relative = normalize_relative_path(raw_path)
                try:
                    path = resolved_repository_path(root, relative)
                    digest = sha256_file(path) if path.is_file() else "missing"
                except LocalIdentityUnavailable:
                    digest = "missing"
                content_lines.append(f"{relative.as_posix()}\0{digest}\n")
            item["content_sha256"] = sha256_bytes(
                "".join(content_lines).encode("utf-8", errors="surrogateescape")
            )
        else:
            item["content_sha256"] = None
        current.append(item)
    return current


def normalized_dirt_inventory(
    expected_inventory: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    return sorted(
        [dict(entry) for entry in expected_inventory],
        key=lambda entry: (
            str(entry.get("status", "")),
            tuple(str(path) for path in entry.get("paths", [])),
        ),
    )


def dirt_is_dependency_relevant(
    item: Mapping[str, Any], known_local_paths: set[str]
) -> bool:
    category = item.get("category")
    if category == "product":
        return True
    if category != "unclassified":
        return False
    paths = tuple(str(path) for path in item.get("paths", []))
    if len(paths) == 1 and paths[0] in known_local_paths:
        return False
    return not (
        len(paths) == 2
        and "R" in str(item.get("status", ""))
        and paths[1] in known_local_paths
    )


def compare(
    comparisons: list[Comparison],
    *,
    field: str,
    expected: Any,
    current: Any,
    source: str,
    mismatch: str = "stale",
    code: str = "identity_match",
    repository: str | None = None,
    global_scope: bool = False,
    propagate_repository: bool = False,
) -> None:
    decision = "current" if expected == current else mismatch
    comparisons.append(
        Comparison(
            field=field,
            expected=expected,
            current=current,
            decision=decision,
            source=source,
            code=code if decision == "current" else f"{code}_mismatch",
            repository=repository,
            global_scope=global_scope,
            propagate_repository=propagate_repository,
        )
    )


def unavailable(
    comparisons: list[Comparison],
    *,
    field: str,
    expected: Any,
    source: str,
    code: str,
    repository: str | None = None,
    global_scope: bool = False,
    propagate_repository: bool = False,
) -> None:
    comparisons.append(
        Comparison(
            field=field,
            expected=expected,
            current=None,
            decision="blocked",
            source=source,
            code=code,
            repository=repository,
            global_scope=global_scope,
            propagate_repository=propagate_repository,
        )
    )


def invalid_comparison(field: str, code: str) -> Comparison:
    return Comparison(
        field=field,
        expected=None,
        current=None,
        decision="invalid",
        source="input_contract",
        code=code,
    )


def require_mapping(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ContractError(f"{label}_not_object")
    return value


def require_list(value: Any, label: str) -> list[Any]:
    if not isinstance(value, list):
        raise ContractError(f"{label}_not_array")
    return value


def repository_roots(repository_map: Mapping[str, Any]) -> dict[str, Path]:
    entries = require_mapping(repository_map.get("repositories"), "repositories")
    result: dict[str, Path] = {}
    for identifier, entry in entries.items():
        if not isinstance(identifier, str) or SAFE_ID.fullmatch(identifier) is None:
            raise ContractError("repository_id_invalid")
        root = Path(str(require_mapping(entry, "repository_entry").get("root", "")))
        if not root.is_absolute():
            raise ContractError("repository_root_not_absolute")
        result[identifier] = root.resolve(strict=False)
    if len(set(result.values())) != len(result):
        raise ContractError("repository_root_identity_collapse")
    return result


def record_inventory(
    repository_map: Mapping[str, Any],
) -> tuple[dict[str, dict[str, Any]], dict[str, str]]:
    entries = require_list(repository_map.get("records"), "records")
    records: dict[str, dict[str, Any]] = {}
    repositories: dict[str, str] = {}
    for raw in entries:
        entry = require_mapping(raw, "record_inventory_entry")
        identifier = entry.get("id")
        repository = entry.get("repository")
        if not isinstance(identifier, str) or identifier in records:
            raise ContractError("record_inventory_id_duplicate_or_invalid")
        if not isinstance(repository, str):
            raise ContractError("record_inventory_repository_invalid")
        records[identifier] = entry
        repositories[identifier] = repository
    return records, repositories


def load_openspec_status(*, store_root: Path) -> dict[str, Any]:
    process = run_local(
        [
            "openspec",
            "status",
            "--change",
            CHANGE_NAME,
            "--json",
            "--store",
            "openspec-store",
        ],
        cwd=store_root,
        text=True,
    )
    try:
        value = json.loads(process.stdout)
    except json.JSONDecodeError:
        raise LocalIdentityUnavailable("openspec_status_not_json") from None
    if not isinstance(value, dict):
        raise LocalIdentityUnavailable("openspec_status_not_object")
    return value


def current_artifact_paths(status: Mapping[str, Any]) -> dict[str, list[Path]]:
    if status.get("changeName") != CHANGE_NAME:
        raise ContractError("openspec_change_name_mismatch")
    artifact_paths = require_mapping(status.get("artifactPaths"), "artifact_paths")
    result: dict[str, list[Path]] = {}
    for identifier in ("proposal", "specs", "design", "tasks"):
        entry = require_mapping(
            artifact_paths.get(identifier), f"artifact_{identifier}"
        )
        paths = require_list(entry.get("existingOutputPaths"), "existing_output_paths")
        parsed = [Path(str(path)).resolve(strict=False) for path in paths]
        result[identifier] = sorted(parsed, key=lambda item: str(item))
    return result


def expected_artifact_paths(store_root: Path) -> dict[str, list[Path]]:
    return {
        identifier: sorted(
            [
                resolved_repository_path(store_root, relative)
                for relative in relative_paths
            ],
            key=str,
        )
        for identifier, relative_paths in EXPECTED_ARTIFACTS.items()
    }


def corrective_tree_digest(store_root: Path) -> str:
    change_root = resolved_repository_path(
        store_root, CHANGE_RELATIVE, require_exists=True
    )
    lines: list[str] = []
    for directory, names, filenames in os.walk(change_root, followlinks=False):
        directory_path = Path(directory)
        for name in [*names, *filenames]:
            candidate = directory_path / name
            if candidate.is_symlink():
                raise ContractError("corrective_tree_symlink_forbidden")
        relative_directory = directory_path.relative_to(store_root.resolve(strict=True))
        if relative_directory == RESULTS_RELATIVE:
            names.clear()
            continue
        names[:] = [
            name for name in names if relative_directory / name != RESULTS_RELATIVE
        ]
        for name in sorted(filenames):
            path = directory_path / name
            relative = path.relative_to(store_root.resolve(strict=True)).as_posix()
            lines.append(f"{relative}\0{sha256_file(path)}\n")
    return sha256_bytes("".join(sorted(lines)).encode("utf-8"))


def planning_digest(
    store_root: Path,
    artifacts: Sequence[Mapping[str, Any]],
    schema_expectation: Mapping[str, Any],
) -> str:
    lines: list[str] = []
    for entry in [*artifacts, schema_expectation]:
        relative = normalize_relative_path(str(entry["path"]))
        current_path = resolved_repository_path(store_root, relative)
        digest = sha256_file(current_path)
        lines.append(f"{relative.as_posix()}\0{digest}\n")
    return sha256_bytes("".join(sorted(lines)).encode("utf-8"))


def evaluate_planning(
    *,
    record: Mapping[str, Any],
    store_root: Path,
    status: Mapping[str, Any],
    comparisons: list[Comparison],
) -> tuple[str, str]:
    planning = require_mapping(record.get("planning"), "planning")
    baseline = str(planning["baseline_sha"])
    observed_head = git_head(store_root)
    baseline_exists = (
        run_local(
            ["git", "cat-file", "-e", f"{baseline}^{{commit}}"],
            cwd=store_root,
            text=True,
            accepted=(0, 1, 128),
        ).returncode
        == 0
    )
    is_ancestor = False
    if baseline_exists:
        is_ancestor = (
            run_local(
                ["git", "merge-base", "--is-ancestor", baseline, observed_head],
                cwd=store_root,
                text=True,
                accepted=(0, 1),
            ).returncode
            == 0
        )
    compare(
        comparisons,
        field="planning.baseline_ancestor",
        expected=True,
        current=baseline_exists and is_ancestor,
        source="git",
        code="baseline_ancestor",
        global_scope=True,
    )

    retained_observed = str(planning["observed_store_sha"])
    observed_exists = (
        run_local(
            ["git", "cat-file", "-e", f"{retained_observed}^{{commit}}"],
            cwd=store_root,
            text=True,
            accepted=(0, 1, 128),
        ).returncode
        == 0
    )
    observed_is_descendant = False
    retained_is_after_baseline = False
    if observed_exists and baseline_exists:
        observed_is_descendant = (
            run_local(
                [
                    "git",
                    "merge-base",
                    "--is-ancestor",
                    retained_observed,
                    observed_head,
                ],
                cwd=store_root,
                text=True,
                accepted=(0, 1),
            ).returncode
            == 0
        )
        retained_is_after_baseline = (
            run_local(
                ["git", "merge-base", "--is-ancestor", baseline, retained_observed],
                cwd=store_root,
                text=True,
                accepted=(0, 1),
            ).returncode
            == 0
        )
    compare(
        comparisons,
        field="planning.observed_store_ancestry",
        expected=True,
        current=(
            observed_exists and observed_is_descendant and retained_is_after_baseline
        ),
        source="git",
        code="observed_store_ancestry",
        global_scope=True,
    )

    expected_tree = str(planning["baseline_tree_sha"])
    current_tree: str | None = None
    if baseline_exists:
        try:
            current_tree = git_text(
                store_root, "rev-parse", f"{baseline}:{CHANGE_RELATIVE.as_posix()}"
            )
        except LocalIdentityUnavailable:
            current_tree = None
    if current_tree is None:
        comparisons.append(
            Comparison(
                field="planning.baseline_tree_sha",
                expected=expected_tree,
                current=None,
                decision="stale",
                source="git",
                code="baseline_tree_unresolved",
                global_scope=True,
            )
        )
    else:
        compare(
            comparisons,
            field="planning.baseline_tree_sha",
            expected=expected_tree,
            current=current_tree,
            source="git",
            code="baseline_tree",
            global_scope=True,
        )

    artifacts = [
        require_mapping(item, "planning_artifact")
        for item in require_list(planning.get("artifacts"), "planning_artifacts")
    ]
    schema_expectation = require_mapping(
        planning.get("evidence_schema"), "evidence_schema"
    )
    status_paths = current_artifact_paths(status)
    authoritative_paths = expected_artifact_paths(store_root)
    expected_paths: dict[str, list[Path]] = {
        identifier: [] for identifier in ("proposal", "specs", "design", "tasks")
    }
    for entry in artifacts:
        identifier = str(entry["artifact_id"])
        relative = normalize_relative_path(str(entry["path"]))
        path = resolved_repository_path(store_root, relative)
        expected_paths.setdefault(identifier, []).append(path)
        try:
            current_hash = sha256_file(path)
        except OSError:
            unavailable(
                comparisons,
                field=f"planning.artifact.{identifier}.{relative.as_posix()}",
                expected=entry["sha256"],
                source="filesystem",
                code="planning_artifact_unavailable",
                global_scope=True,
            )
        else:
            compare(
                comparisons,
                field=f"planning.artifact.{identifier}.{relative.as_posix()}",
                expected=entry["sha256"],
                current=current_hash,
                source="filesystem",
                code="planning_artifact_hash",
                global_scope=True,
            )
    for paths in expected_paths.values():
        paths.sort(key=lambda item: str(item))
    expected_path_json = {
        key: [str(path) for path in expected_paths.get(key, [])]
        for key in sorted(expected_paths)
    }
    authoritative_path_json = {
        key: [str(path) for path in authoritative_paths[key]]
        for key in sorted(authoritative_paths)
    }
    if expected_path_json != authoritative_path_json:
        raise ContractError("planning_artifact_contract_incomplete")
    status_path_json = {
        key: [str(path) for path in status_paths.get(key, [])]
        for key in sorted(status_paths)
    }
    if status_path_json != authoritative_path_json:
        raise ContractError("openspec_artifact_contract_mismatch")
    compare(
        comparisons,
        field="planning.artifact_paths",
        expected=authoritative_path_json,
        current=status_path_json,
        source="openspec_status",
        mismatch="invalid",
        code="artifact_path_set",
        global_scope=True,
    )

    schema_relative = normalize_relative_path(str(schema_expectation["path"]))
    try:
        current_schema_hash = sha256_file(
            resolved_repository_path(store_root, schema_relative)
        )
    except OSError:
        unavailable(
            comparisons,
            field="planning.evidence_schema",
            expected=schema_expectation["sha256"],
            source="filesystem",
            code="evidence_schema_unavailable",
            global_scope=True,
        )
    else:
        compare(
            comparisons,
            field="planning.evidence_schema",
            expected=schema_expectation["sha256"],
            current=current_schema_hash,
            source="filesystem",
            code="evidence_schema_hash",
            global_scope=True,
        )

    try:
        current_corrective_tree = corrective_tree_digest(store_root)
    except (OSError, LocalIdentityUnavailable):
        unavailable(
            comparisons,
            field="planning.corrective_tree_sha256",
            expected=planning["corrective_tree_sha256"],
            source="filesystem",
            code="corrective_tree_unavailable",
            global_scope=True,
        )
    else:
        compare(
            comparisons,
            field="planning.corrective_tree_sha256",
            expected=planning["corrective_tree_sha256"],
            current=current_corrective_tree,
            source="filesystem",
            code="corrective_tree",
            global_scope=True,
        )

    try:
        current_digest = planning_digest(store_root, artifacts, schema_expectation)
    except (OSError, ContractError):
        unavailable(
            comparisons,
            field="planning.digest_sha256",
            expected=planning["planning_digest_sha256"],
            source="filesystem",
            code="planning_digest_unavailable",
            global_scope=True,
        )
    else:
        compare(
            comparisons,
            field="planning.digest_sha256",
            expected=planning["planning_digest_sha256"],
            current=current_digest,
            source="filesystem",
            code="planning_digest",
            global_scope=True,
        )
    return baseline, observed_head


def evaluate_repositories(
    *,
    record: Mapping[str, Any],
    roots: Mapping[str, Path],
    store_repository: str,
    baseline_sha: str,
    excluded_output: Path | None,
    comparisons: list[Comparison],
) -> None:
    local_mechanism_paths: dict[str, set[str]] = {}
    for item in require_list(record.get("mechanisms"), "mechanisms"):
        mechanism = require_mapping(item, "mechanism")
        local_mechanism_paths.setdefault(str(mechanism["repository"]), set()).add(
            normalize_relative_path(str(mechanism["path"])).as_posix()
        )
    upstream_repositories: set[str] = {
        str(require_mapping(dep, "dependency")["upstream_repository"])
        for dep in require_list(record.get("dependencies"), "record_dependencies")
    }
    seen: set[str] = set()
    for raw in require_list(record.get("repositories"), "record_repositories"):
        entry = require_mapping(raw, "repository_expectation")
        identifier = str(entry["id"])
        if identifier in seen:
            raise ContractError("record_repository_duplicate")
        seen.add(identifier)
        root = roots.get(identifier)
        if root is None:
            unavailable(
                comparisons,
                field=f"repository.{identifier}.root",
                expected=entry["worktree_path"],
                source="repository_map",
                code="repository_unmapped",
                repository=identifier,
            )
            continue
        compare(
            comparisons,
            field=f"repository.{identifier}.worktree_path",
            expected=str(Path(str(entry["worktree_path"])).resolve(strict=False)),
            current=str(root),
            source="repository_map",
            code="worktree_path",
            repository=identifier,
            propagate_repository=(identifier != store_repository),
        )
        if not root.is_dir():
            unavailable(
                comparisons,
                field=f"repository.{identifier}.head_sha",
                expected=entry["head_sha"],
                source="git",
                code="repository_unavailable",
                repository=identifier,
            )
            continue
        try:
            actual_root = Path(git_text(root, "rev-parse", "--show-toplevel")).resolve(
                strict=True
            )
            if actual_root != root.resolve(strict=True):
                raise ContractError("repository_root_not_git_toplevel")
            head = git_head(root)
            branch = git_branch(root)
            dirt_payload = git_status_bytes(
                root,
                excluded_output if identifier == store_repository else None,
            )
            dirt = sha256_bytes(dirt_payload)
            current_inventory = current_dirt_inventory(
                root=root,
                payload=dirt_payload,
                expected_inventory=require_list(
                    entry.get("dirt_inventory"), "dirt_inventory"
                ),
            )
        except LocalIdentityUnavailable:
            unavailable(
                comparisons,
                field=f"repository.{identifier}.identity",
                expected="locally_resolvable",
                source="git",
                code="repository_identity_unavailable",
                repository=identifier,
            )
            continue
        if identifier == store_repository:
            compare(
                comparisons,
                field=f"repository.{identifier}.head_descends_from_baseline",
                expected=True,
                current=run_local(
                    ["git", "merge-base", "--is-ancestor", baseline_sha, head],
                    cwd=root,
                    text=True,
                    accepted=(0, 1, 128),
                ).returncode
                == 0,
                source="git",
                code="store_head_ancestry",
                repository=identifier,
                global_scope=True,
            )
        else:
            compare(
                comparisons,
                field=f"repository.{identifier}.head_sha",
                expected=entry["head_sha"],
                current=head,
                source="git",
                code="repository_head",
                repository=identifier,
            )
        compare(
            comparisons,
            field=f"repository.{identifier}.branch",
            expected=entry["branch"],
            current=branch,
            source="git",
            code="repository_branch",
            repository=identifier,
            propagate_repository=False,
        )
        known_local_paths = local_mechanism_paths.get(identifier, set())
        expected_product_dirt = [
            item
            for item in normalized_dirt_inventory(
                require_list(entry["dirt_inventory"], "dirt_inventory")
            )
            if dirt_is_dependency_relevant(item, known_local_paths)
        ]
        current_product_dirt = [
            item
            for item in current_inventory
            if dirt_is_dependency_relevant(item, known_local_paths)
        ]
        compare(
            comparisons,
            field=f"repository.{identifier}.dependency_relevant_dirt",
            expected=expected_product_dirt,
            current=current_product_dirt,
            source="classified_git_dirt",
            code="repository_dependency_relevant_dirt",
            repository=identifier,
            propagate_repository=identifier in upstream_repositories,
        )
        compare(
            comparisons,
            field=f"repository.{identifier}.dirt_inventory",
            expected=normalized_dirt_inventory(
                require_list(entry["dirt_inventory"], "dirt_inventory")
            ),
            current=current_inventory,
            source="git_status_porcelain_v1_z_and_filesystem",
            code="repository_dirt_inventory",
            repository=identifier,
            propagate_repository=False,
        )
        compare(
            comparisons,
            field=f"repository.{identifier}.dirt_sha256",
            expected=entry["dirt_sha256"],
            current=dirt,
            source="git_status_porcelain_v1_z",
            code="repository_dirt",
            repository=identifier,
            propagate_repository=False,
        )


def evaluate_file_expectation(
    *,
    entry: Mapping[str, Any],
    roots: Mapping[str, Path],
    field_prefix: str,
    comparisons: list[Comparison],
) -> None:
    identifier = str(entry["repository"])
    root = roots.get(identifier)
    relative = normalize_relative_path(str(entry["path"]))
    field = f"{field_prefix}.{entry['id']}"
    if root is None:
        unavailable(
            comparisons,
            field=field,
            expected=entry["sha256"],
            source="repository_map",
            code="file_repository_unmapped",
            repository=identifier,
        )
        return
    try:
        path = resolved_repository_path(root, relative)
        current = sha256_file(path)
    except LocalIdentityUnavailable:
        missing_path = False
        try:
            unresolved = resolved_repository_path(root, relative, require_exists=False)
            unresolved.lstat()
        except FileNotFoundError:
            missing_path = True
        except OSError:
            pass
        if missing_path:
            relative_text = relative.as_posix()
            try:
                path_is_explicit_dirt = any(
                    relative_text in paths
                    for _, paths in decoded_porcelain_records(git_status_bytes(root))
                )
            except LocalIdentityUnavailable:
                path_is_explicit_dirt = False
            if path_is_explicit_dirt:
                compare(
                    comparisons,
                    field=field,
                    expected=entry["sha256"],
                    current="missing",
                    source="git_status_porcelain_v1_z_and_filesystem",
                    code="file_hash",
                    repository=identifier,
                )
                return
        unavailable(
            comparisons,
            field=field,
            expected=entry["sha256"],
            source="filesystem",
            code="file_unavailable",
            repository=identifier,
        )
        return
    compare(
        comparisons,
        field=field,
        expected=entry["sha256"],
        current=current,
        source="filesystem",
        code="file_hash",
        repository=identifier,
    )


def normalized_distribution_name(value: str) -> str:
    return re.sub(r"[-_.]+", "-", value).casefold()


def owned_distribution_paths(site_root: Path, distribution: str) -> set[PurePosixPath]:
    expected = normalized_distribution_name(distribution)
    matches = [
        candidate
        for candidate in importlib.metadata.distributions(path=[str(site_root)])
        if normalized_distribution_name(candidate.metadata.get("Name", "")) == expected
    ]
    if len(matches) != 1:
        raise LocalIdentityUnavailable("distribution_metadata_ambiguous_or_missing")
    files = matches[0].files
    if files is None:
        raise LocalIdentityUnavailable("distribution_file_ownership_unavailable")
    return {PurePosixPath(str(path)) for path in files}


def discover_import_origin(
    environment: Mapping[str, Any], distribution: str, import_name: str
) -> Path:
    components = import_name.split(".")
    for raw_root in require_list(environment.get("site_packages"), "site_packages"):
        root = Path(str(raw_root))
        if not root.is_absolute() or not root.is_dir():
            continue
        try:
            owned_paths = owned_distribution_paths(root, distribution)
        except (LocalIdentityUnavailable, OSError, ValueError):
            continue
        module = root.joinpath(*components)
        package_init = module / "__init__.py"
        module_file = module.with_suffix(".py")
        package_relative = PurePosixPath(*components) / "__init__.py"
        module_relative = PurePosixPath(*components[:-1], f"{components[-1]}.py")
        if package_relative in owned_paths and package_init.is_file():
            return package_init.resolve(strict=True)
        if module_relative in owned_paths and module_file.is_file():
            return module_file.resolve(strict=True)
    raise LocalIdentityUnavailable("installed_origin_unresolved")


def repository_for_path(origin: Path, roots: Mapping[str, Path]) -> str | None:
    matches = [
        (len(root.parts), identifier)
        for identifier, root in roots.items()
        if path_under(origin, root)
    ]
    if not matches:
        return None
    return max(matches)[1]


def enclosing_git_identity(origin: Path) -> tuple[Path, str]:
    """Resolve the containing checkout directly from an installed origin path."""

    start = origin if origin.is_dir() else origin.parent
    root = Path(git_text(start, "rev-parse", "--show-toplevel")).resolve(strict=True)
    return root, git_head(root)


def evaluate_dependencies(
    *,
    record: Mapping[str, Any],
    repository_map: Mapping[str, Any],
    roots: Mapping[str, Path],
    comparisons: list[Comparison],
) -> dict[str, tuple[str, str, Path]]:
    environments = require_mapping(
        repository_map.get("python_environments"), "python_environments"
    )
    seen: set[str] = set()
    resolved: dict[str, tuple[str, str, Path]] = {}
    for raw in require_list(record.get("dependencies"), "dependencies"):
        entry = require_mapping(raw, "dependency")
        identifier = str(entry["id"])
        if identifier in seen:
            raise ContractError("dependency_id_duplicate")
        seen.add(identifier)
        consumer = str(entry["consumer_repository"])
        upstream = str(entry["upstream_repository"])
        if consumer not in roots or upstream not in roots:
            raise ContractError("dependency_repository_unmapped")
        declaration = require_mapping(entry["declaration"], "dependency_declaration")
        if declaration.get("repository") != consumer:
            raise ContractError("dependency_declaration_consumer_mismatch")
        evaluate_file_expectation(
            entry=declaration,
            roots=roots,
            field_prefix=f"dependency.{identifier}.declaration",
            comparisons=comparisons,
        )
        lock = entry.get("lock")
        if lock is not None:
            lock_entry = require_mapping(lock, "dependency_lock")
            if lock_entry.get("repository") != consumer:
                raise ContractError("dependency_lock_consumer_mismatch")
            evaluate_file_expectation(
                entry=lock_entry,
                roots=roots,
                field_prefix=f"dependency.{identifier}.lock",
                comparisons=comparisons,
            )

        checkout = require_mapping(entry["source_checkout"], "source_checkout")
        if checkout.get("repository") != upstream:
            raise ContractError("dependency_checkout_upstream_mismatch")
        upstream_root = roots.get(upstream)
        if upstream_root is None or not upstream_root.is_dir():
            unavailable(
                comparisons,
                field=f"dependency.{identifier}.source_checkout",
                expected=checkout["head_sha"],
                source="repository_map",
                code="source_checkout_unavailable",
                repository=upstream,
            )
        else:
            compare(
                comparisons,
                field=f"dependency.{identifier}.source_checkout.path",
                expected=str(Path(str(checkout["path"])).resolve(strict=False)),
                current=str(upstream_root),
                source="repository_map",
                code="source_checkout_path",
                repository=upstream,
            )
            try:
                current_checkout_sha = git_head(upstream_root)
            except LocalIdentityUnavailable:
                unavailable(
                    comparisons,
                    field=f"dependency.{identifier}.source_checkout.head_sha",
                    expected=checkout["head_sha"],
                    source="git",
                    code="source_checkout_head_unavailable",
                    repository=upstream,
                )
            else:
                compare(
                    comparisons,
                    field=f"dependency.{identifier}.source_checkout.head_sha",
                    expected=checkout["head_sha"],
                    current=current_checkout_sha,
                    source="git",
                    code="source_checkout_head",
                    repository=upstream,
                )

        installed = require_mapping(entry["installed"], "installed_dependency")
        if installed.get("origin_repository") != upstream:
            raise ContractError("installed_origin_upstream_mismatch")
        environment_id = str(installed["environment"])
        environment = environments.get(environment_id)
        if not isinstance(environment, dict):
            unavailable(
                comparisons,
                field=f"dependency.{identifier}.installed.origin",
                expected=installed["origin_path"],
                source="repository_map",
                code="python_environment_unavailable",
                repository=consumer,
            )
            continue
        try:
            origin = discover_import_origin(
                environment,
                str(installed["distribution"]),
                str(installed["import_name"]),
            )
        except LocalIdentityUnavailable:
            unavailable(
                comparisons,
                field=f"dependency.{identifier}.installed.origin",
                expected=installed["origin_path"],
                source="distribution_metadata",
                code="installed_origin_unavailable",
                repository=consumer,
            )
            continue
        actual_repository = repository_for_path(origin, roots)
        actual_git_root: Path | None = None
        actual_sha: str | None = None
        try:
            actual_git_root, actual_sha = enclosing_git_identity(origin)
        except (LocalIdentityUnavailable, OSError):
            pass
        compare(
            comparisons,
            field=f"dependency.{identifier}.installed.origin_path",
            expected=str(Path(str(installed["origin_path"])).resolve(strict=False)),
            current=str(origin),
            source="distribution_metadata",
            code="installed_origin_path",
            repository=consumer,
        )
        compare(
            comparisons,
            field=f"dependency.{identifier}.installed.origin_repository",
            expected=installed["origin_repository"],
            current=actual_repository
            or (str(actual_git_root) if actual_git_root is not None else None),
            source="repository_map",
            code="installed_origin_repository",
            repository=consumer,
        )
        if actual_sha is None:
            unavailable(
                comparisons,
                field=f"dependency.{identifier}.installed.origin_sha",
                expected=installed["origin_sha"],
                source="git",
                code="installed_origin_git_unavailable",
                repository=consumer,
            )
        else:
            compare(
                comparisons,
                field=f"dependency.{identifier}.installed.origin_sha",
                expected=installed["origin_sha"],
                current=actual_sha,
                source="git",
                code="installed_origin_sha",
                repository=consumer,
            )
        resolved[identifier] = (consumer, upstream, origin)
    inventory, _repositories = record_inventory(repository_map)
    record_id = str(record["record_id"])
    inventory_entry = inventory.get(record_id)
    if inventory_entry is None:
        raise ContractError("dependency_record_inventory_missing")
    required_observations = {
        str(require_mapping(item, "dependency_observation")["id"]): require_mapping(
            item, "dependency_observation"
        )
        for item in require_list(
            repository_map.get("dependency_observations"),
            "dependency_observations",
        )
        if require_mapping(item, "dependency_observation").get("downstream_record")
        == record_id
    }
    required_dependencies = set(required_observations)
    if seen != required_dependencies:
        raise ContractError("dependency_contract_incomplete_or_extra")
    expected_consumer = str(inventory_entry["repository"])
    for identifier, (consumer, upstream, _origin) in resolved.items():
        observation = required_observations[identifier]
        if consumer != expected_consumer:
            raise ContractError("dependency_consumer_record_mismatch")
        if upstream != observation.get("upstream_repository"):
            raise ContractError("dependency_observation_upstream_mismatch")
    return resolved


def evaluate_dependency_observations(
    *,
    repository_map: Mapping[str, Any],
    roots: Mapping[str, Path],
    comparisons: list[Comparison],
) -> list[tuple[str, str]]:
    environments = require_mapping(
        repository_map.get("python_environments"), "python_environments"
    )
    inventory, _ = record_inventory(repository_map)
    edges: set[tuple[str, str]] = set()
    seen: set[str] = set()
    for raw in require_list(
        repository_map.get("dependency_observations"), "dependency_observations"
    ):
        entry = require_mapping(raw, "dependency_observation")
        identifier = str(entry["id"])
        if identifier in seen:
            raise ContractError("dependency_observation_duplicate")
        seen.add(identifier)
        downstream_record = str(entry["downstream_record"])
        upstream = str(entry["upstream_repository"])
        if downstream_record not in inventory or upstream not in roots:
            raise ContractError("dependency_observation_unknown_endpoint")
        environment = environments.get(str(entry["environment"]))
        if not isinstance(environment, dict):
            unavailable(
                comparisons,
                field=f"dependency_observation.{identifier}.origin",
                expected=entry["origin_path"],
                source="repository_map",
                code="dependency_environment_unavailable",
                repository=upstream,
                propagate_repository=True,
            )
            edges.add((upstream, downstream_record))
            continue
        try:
            origin = discover_import_origin(
                environment,
                str(entry["distribution"]),
                str(entry["import_name"]),
            )
        except LocalIdentityUnavailable:
            unavailable(
                comparisons,
                field=f"dependency_observation.{identifier}.origin",
                expected=entry["origin_path"],
                source="distribution_metadata",
                code="dependency_observation_origin_unavailable",
                repository=upstream,
                propagate_repository=True,
            )
            edges.add((upstream, downstream_record))
            continue
        actual_repository = repository_for_path(origin, roots)
        expected_origin = Path(str(entry["origin_path"])).resolve(strict=False)
        compare(
            comparisons,
            field=f"dependency_observation.{identifier}.origin_path",
            expected=str(expected_origin),
            current=str(origin),
            source="distribution_metadata",
            code="dependency_observation_origin_path",
            repository=upstream,
            propagate_repository=True,
        )
        compare(
            comparisons,
            field=f"dependency_observation.{identifier}.origin_repository",
            expected=upstream,
            current=actual_repository,
            source="repository_map",
            code="dependency_observation_origin_repository",
            repository=upstream,
            propagate_repository=True,
        )
        try:
            _git_root, actual_sha = enclosing_git_identity(origin)
        except (LocalIdentityUnavailable, OSError):
            unavailable(
                comparisons,
                field=f"dependency_observation.{identifier}.origin_sha",
                expected=entry["origin_sha"],
                source="git",
                code="dependency_observation_sha_unavailable",
                repository=upstream,
                propagate_repository=True,
            )
        else:
            compare(
                comparisons,
                field=f"dependency_observation.{identifier}.origin_sha",
                expected=entry["origin_sha"],
                current=actual_sha,
                source="git",
                code="dependency_observation_sha",
                repository=upstream,
                propagate_repository=True,
            )
        if actual_repository is not None:
            edges.add((actual_repository, downstream_record))
    return sorted(edges)


def evaluate_prerequisites(
    *,
    record: Mapping[str, Any],
    repository_map: Mapping[str, Any],
    roots: Mapping[str, Path],
    comparisons: list[Comparison],
) -> None:
    attestations = require_mapping(repository_map.get("attestations"), "attestations")
    seen: set[str] = set()
    for raw in require_list(record.get("prerequisites"), "prerequisites"):
        entry = require_mapping(raw, "prerequisite")
        identifier = str(entry["id"])
        if identifier in seen:
            raise ContractError("prerequisite_id_duplicate")
        seen.add(identifier)
        kind = str(entry["kind"])
        field = f"prerequisite.{identifier}"
        if kind == "environment_presence":
            name = str(entry.get("environment_name", ""))
            if not name or "expected_present" not in entry:
                raise ContractError("environment_prerequisite_incomplete")
            compare(
                comparisons,
                field=field,
                expected=bool(entry["expected_present"]),
                current=name in os.environ,
                source=f"environment_presence:{name}",
                code="environment_presence",
            )
        elif kind == "executable":
            name = str(entry.get("executable_name", ""))
            if not name:
                raise ContractError("executable_prerequisite_incomplete")
            current_path = shutil.which(name)
            if current_path is None:
                unavailable(
                    comparisons,
                    field=field,
                    expected=entry.get("expected_path"),
                    source="executable_path",
                    code="executable_unavailable",
                )
                continue
            if "expected_path" in entry:
                compare(
                    comparisons,
                    field=f"{field}.path",
                    expected=str(
                        Path(str(entry["expected_path"])).resolve(strict=False)
                    ),
                    current=str(Path(current_path).resolve(strict=True)),
                    source="executable_path",
                    code="executable_path",
                )
            if "expected_sha256" in entry:
                try:
                    current_hash = sha256_file(Path(current_path))
                except OSError:
                    unavailable(
                        comparisons,
                        field=f"{field}.sha256",
                        expected=entry["expected_sha256"],
                        source="filesystem",
                        code="executable_hash_unavailable",
                    )
                else:
                    compare(
                        comparisons,
                        field=f"{field}.sha256",
                        expected=entry["expected_sha256"],
                        current=current_hash,
                        source="filesystem",
                        code="executable_hash",
                    )
        elif kind == "path_exists":
            repository = str(entry.get("repository", ""))
            root = roots.get(repository)
            raw_path = str(entry.get("path", ""))
            if root is None or not raw_path or "expected_exists" not in entry:
                raise ContractError("path_prerequisite_incomplete")
            relative = normalize_relative_path(raw_path)
            candidate = root / Path(relative)
            if candidate.exists():
                resolved_repository_path(root, relative)
            else:
                parent_relative = PurePosixPath(*relative.parts[:-1])
                resolved_repository_path(
                    root,
                    parent_relative if parent_relative.parts else PurePosixPath("."),
                )
            compare(
                comparisons,
                field=field,
                expected=bool(entry["expected_exists"]),
                current=(root / Path(relative)).exists(),
                source="filesystem_presence",
                code="path_presence",
                repository=repository,
            )
        elif kind == "attestation":
            attestation_id = str(entry.get("attestation_id", ""))
            if not attestation_id or "expected_state" not in entry:
                raise ContractError("attestation_prerequisite_incomplete")
            current = attestations.get(attestation_id)
            if not isinstance(current, dict):
                unavailable(
                    comparisons,
                    field=field,
                    expected=entry["expected_state"],
                    source="presence_attestation",
                    code="attestation_unavailable",
                )
                continue
            compare(
                comparisons,
                field=f"{field}.state",
                expected=entry["expected_state"],
                current=current.get("state"),
                source="presence_attestation",
                code="attestation_state",
            )
            if "expected_source_id" in entry:
                compare(
                    comparisons,
                    field=f"{field}.source_id",
                    expected=entry["expected_source_id"],
                    current=current.get("source_id"),
                    source="presence_attestation",
                    code="attestation_source_id",
                )
            if "expected_source_sha256" in entry:
                compare(
                    comparisons,
                    field=f"{field}.source_sha256",
                    expected=entry["expected_source_sha256"],
                    current=current.get("source_sha256"),
                    source="presence_attestation",
                    code="attestation_source_hash",
                )
        else:
            raise ContractError("prerequisite_kind_invalid")


def evaluate_live(
    *,
    record: Mapping[str, Any],
    gate: str,
    inventory_entry: Mapping[str, Any],
    repository_map: Mapping[str, Any],
    comparisons: list[Comparison],
) -> None:
    live = record.get("live")
    if record["record_kind"] == "deterministic_handoff":
        if live is not None:
            raise ContractError("deterministic_record_has_live_payload")
        return
    payload = require_mapping(live, "live")
    boundary = require_mapping(payload["consumer_boundary"], "consumer_boundary")
    if boundary.get("repository") != inventory_entry.get("repository"):
        raise ContractError("live_consumer_repository_mismatch")
    expected_kind = {
        "ai-harness-skills": "contained_generation",
        "ai-review": "reviewer",
    }.get(str(inventory_entry.get("repository")))
    if expected_kind is None or boundary.get("kind") != expected_kind:
        raise ContractError("live_consumer_boundary_invalid")
    for key in ("id", "repository", "kind"):
        compare(
            comparisons,
            field=f"live.consumer_boundary.{key}",
            expected=boundary[key],
            current=boundary[key],
            source="retained_live_record",
            code="live_consumer_boundary",
        )
    authorization = require_mapping(payload["authorization"], "live_authorization")
    attestations = require_mapping(repository_map.get("attestations"), "attestations")
    authorization_attestation = attestations.get(str(authorization["attestation_id"]))
    if not isinstance(authorization_attestation, dict):
        unavailable(
            comparisons,
            field="live.authorization",
            expected="authorized",
            source="presence_attestation",
            code="live_authorization_unavailable",
        )
    else:
        compare(
            comparisons,
            field="live.authorization.source_id",
            expected=authorization["source_id"],
            current=authorization_attestation.get("source_id"),
            source="presence_attestation",
            code="live_authorization_source_id",
        )
        compare(
            comparisons,
            field="live.authorization.source_sha256",
            expected=authorization["source_sha256"],
            current=authorization_attestation.get("source_sha256"),
            source="presence_attestation",
            code="live_authorization_source_sha256",
        )
        compare(
            comparisons,
            field="live.authorization.attested_status",
            expected="authorized",
            current=authorization_attestation.get("state"),
            source="presence_attestation",
            mismatch="blocked",
            code="live_authorization_attested_status",
        )
    compare(
        comparisons,
        field="live.authorization.status",
        expected="authorized",
        current=authorization["status"],
        source="presence_attestation",
        mismatch="blocked",
        code="live_authorization",
    )
    route = require_mapping(payload["provider_route"], "provider_route")
    if route["cli_adapter_id"] == route["canonical_provider_id"]:
        raise ContractError("live_provider_identities_collapsed")
    for key in (
        "cli_adapter_id",
        "canonical_provider_id",
        "canonical_alias",
        "wire_model",
        "behavior_sha256",
    ):
        compare(
            comparisons,
            field=f"live.provider_route.{key}",
            expected=route[key],
            current=route[key],
            source="retained_live_record",
            code="live_provider_route",
        )
    mechanism = require_mapping(payload["mechanism"], "live_mechanism")
    if mechanism["id"] not in {
        require_mapping(item, "mechanism")["id"]
        for item in require_list(record["mechanisms"], "mechanisms")
    }:
        raise ContractError("live_mechanism_identity_unbound")
    command_shape = require_list(
        mechanism["redacted_command_shape"],
        "redacted_command_shape",
    )
    if not command_shape:
        raise ContractError("live_command_shape_empty")
    compare(
        comparisons,
        field="live.mechanism.command_shape_sha256",
        expected=mechanism["command_shape_sha256"],
        current=sha256_bytes(canonical_bytes(command_shape)),
        source="retained_live_record",
        mismatch="invalid",
        code="live_command_shape",
    )

    execution = payload.get("execution")
    execution_required = gate not in LIVE_GATES
    if execution_required and not isinstance(execution, dict):
        raise ContractError("live_execution_required")
    if execution_required and isinstance(execution, dict):
        nested = require_mapping(execution["nested_outcome"], "nested_outcome")
        preservation = require_mapping(
            execution["target_preservation"], "target_preservation"
        )
        proof = require_mapping(execution["proof"], "live_proof")
        successful = (
            execution["process_reachable"] is True
            and execution["process_exit_code"] == 0
            and nested["status"] == "succeeded"
            and nested["provider_error"] is False
            and nested["completion_state"] == "complete"
            and proof["observed"] is True
            and preservation["status"] == "preserved"
            and execution["row_status"] == "passed"
        )
        compare(
            comparisons,
            field="live.execution.acceptance",
            expected=True,
            current=successful,
            source="retained_live_result",
            mismatch="blocked",
            code="live_execution_acceptance",
        )
        retained_fields = {
            "process_reachable": execution["process_reachable"],
            "process_exit_code": execution["process_exit_code"],
            "monotonic_duration_ms": execution["monotonic_duration_ms"],
            "nested_status": nested["status"],
            "nested_provider_error": nested["provider_error"],
            "nested_completion_state": nested["completion_state"],
            "proof_observed": proof["observed"],
            "target_preservation_status": preservation["status"],
            "row_status": execution["row_status"],
        }
        for key, value in retained_fields.items():
            compare(
                comparisons,
                field=f"live.execution.{key}",
                expected=value,
                current=value,
                source="retained_live_result",
                code="live_execution_field",
            )


def highest_decision(comparisons: Sequence[Comparison]) -> str:
    return max(
        (comparison.decision for comparison in comparisons),
        key=lambda decision: DECISION_RANK[decision],
        default="current",
    )


def affected_records(
    *,
    record_id: str,
    comparisons: Sequence[Comparison],
    repository_map: Mapping[str, Any],
    dependency_edges: Sequence[tuple[str, str]],
) -> list[str]:
    inventory, record_repositories = record_inventory(repository_map)
    noncurrent = [item for item in comparisons if item.decision != "current"]
    if not noncurrent:
        return []
    if any(item.global_scope for item in noncurrent):
        return sorted(inventory)

    affected: set[str] = {record_id} if record_id in inventory else set()
    drifted_repositories = {
        item.repository
        for item in noncurrent
        if item.repository is not None and item.propagate_repository
    }
    active_upstreams = set(drifted_repositories)
    changed = True
    while changed:
        changed = False
        for upstream, downstream in dependency_edges:
            if upstream not in active_upstreams or downstream in affected:
                continue
            affected.add(downstream)
            downstream_repository = record_repositories.get(downstream)
            if downstream_repository is not None:
                active_upstreams.add(downstream_repository)
            changed = True
    return sorted(affected)


def safe_record_identity(
    raw_record: Mapping[str, Any] | None,
) -> tuple[str | None, str | None]:
    if raw_record is None:
        return None, None
    record_id = raw_record.get("record_id")
    record_kind = raw_record.get("record_kind")
    safe_id = (
        record_id
        if isinstance(record_id, str) and SAFE_ID.fullmatch(record_id)
        else None
    )
    safe_kind = (
        record_kind if record_kind in {"deterministic_handoff", "live_row"} else None
    )
    return safe_id, safe_kind


def build_result(
    *,
    record_id: str | None,
    record_kind: str | None,
    gate: str,
    baseline_sha: str | None,
    observed_head: str | None,
    comparisons: Sequence[Comparison],
    affected: Sequence[str],
    observed_at: str | None,
) -> dict[str, Any]:
    ordered = sorted(comparisons, key=lambda item: item.field)
    decision = highest_decision(ordered)
    exit_code = EXIT_CODES[decision]
    comparison_json = [item.as_json() for item in ordered]
    digest_payload = {
        "affected_records": list(affected),
        "comparisons": comparison_json,
        "decision": decision,
        "gate": gate,
        "planning_baseline_sha": baseline_sha,
        "record_id": record_id,
        "record_kind": record_kind,
        "schema_version": SCHEMA_VERSION,
    }
    diagnostics = [
        f"{item.field}:{item.decision}:{item.code}"
        for item in ordered
        if item.decision != "current"
    ]
    result: dict[str, Any] = {
        "affected_records": list(affected),
        "comparison_digest": sha256_bytes(canonical_bytes(digest_payload)),
        "comparisons": comparison_json,
        "decision": decision,
        "diagnostics": diagnostics,
        "downstream_invalidations": [
            {"decision": decision, "record_id": identifier} for identifier in affected
        ],
        "exit_code": exit_code,
        "gate": gate,
        "observed_store_head": observed_head,
        "planning_baseline_sha": baseline_sha,
        "record_id": record_id,
        "record_kind": record_kind,
        "schema_version": SCHEMA_VERSION,
    }
    if observed_at is not None:
        result["observed_at"] = observed_at
    return result


def validate_output_path(output: Path, store_root: Path) -> Path:
    resolved_store = store_root.resolve(strict=True)
    lexical_results_root = resolved_store / Path(RESULTS_RELATIVE)
    current = resolved_store
    for part in RESULTS_RELATIVE.parts:
        current = current / part
        if current.is_symlink():
            raise ContractError("output_parent_symlink_forbidden")
    results_root = lexical_results_root.resolve(strict=False)
    if not path_under(results_root, resolved_store):
        raise ContractError("output_results_root_escape")
    if output.is_symlink():
        raise ContractError("output_symlink_forbidden")
    resolved_output = output.resolve(strict=False)
    if resolved_output.parent != results_root or not SAFE_ID.fullmatch(
        resolved_output.name
    ):
        raise ContractError("output_outside_change_results")
    return resolved_output


def atomic_write(path: Path, payload: bytes) -> None:
    try:
        path.parent.mkdir(mode=0o700)
    except FileExistsError:
        pass
    directory_flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
    directory_flags |= getattr(os, "O_NOFOLLOW", 0)
    directory_fd = os.open(path.parent, directory_flags)
    temporary_name = f".{path.name}.{secrets.token_hex(16)}"
    try:
        descriptor = os.open(
            temporary_name,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0),
            0o600,
            dir_fd=directory_fd,
        )
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(
            temporary_name,
            path.name,
            src_dir_fd=directory_fd,
            dst_dir_fd=directory_fd,
        )
        os.fsync(directory_fd)
    finally:
        try:
            os.unlink(temporary_name, dir_fd=directory_fd)
        except FileNotFoundError:
            pass
        os.close(directory_fd)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = ContractArgumentParser(
        description="Validate retained agent-LLM evidence against local identity"
    )
    parser.add_argument("--record", type=Path, required=True)
    parser.add_argument("--schema", type=Path, required=True)
    parser.add_argument("--gate", required=True)
    parser.add_argument("--repository-map", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--observed-at")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    raw_argv = list(argv) if argv is not None else sys.argv[1:]
    gate_hint = "invalid"
    if "--gate" in raw_argv:
        index = raw_argv.index("--gate")
        if index + 1 < len(raw_argv) and raw_argv[index + 1] in GATES:
            gate_hint = raw_argv[index + 1]
    try:
        args = parse_args(raw_argv)
    except ContractError as exc:
        result = build_result(
            record_id=None,
            record_kind=None,
            gate=gate_hint,
            baseline_sha=None,
            observed_head=None,
            comparisons=[invalid_comparison("input.arguments", str(exc))],
            affected=[],
            observed_at=None,
        )
        sys.stdout.buffer.write(canonical_output(result))
        return int(result["exit_code"])
    raw_record: dict[str, Any] | None = None
    comparisons: list[Comparison] = []
    baseline_sha: str | None = None
    observed_head: str | None = None
    affected: list[str] = []
    output_path: Path | None = None
    roots: dict[str, Path] = {}
    repository_map: dict[str, Any] | None = None
    dependency_edges: list[tuple[str, str]] = []
    try:
        if args.gate not in GATES:
            comparisons.append(invalid_comparison("input.gate", "gate_invalid"))
            raise ContractError("gate_invalid")
        schema = load_json(args.schema)
        raw_record = load_json(args.record)
        repository_map = load_json(args.repository_map)
        schema_errors = validate_schema_value(raw_record, schema, schema)
        schema_errors.extend(find_forbidden_keys(raw_record, forbidden_keys(schema)))
        schema_errors.extend(
            find_forbidden_keys(repository_map, forbidden_keys(schema), "$map")
        )
        map_contract = schema.get("x-repository-map-contract")
        if not isinstance(map_contract, dict):
            schema_errors.append("$.x-repository-map-contract:missing")
        else:
            schema_errors.extend(
                validate_schema_value(repository_map, map_contract, schema, path="$map")
            )
        if schema_errors:
            comparisons.extend(
                invalid_comparison(f"input.schema[{index}]", error.rsplit(":", 1)[-1])
                for index, error in enumerate(sorted(set(schema_errors)))
            )
            raise ContractError("schema_validation_failed")

        record_id, record_kind = safe_record_identity(raw_record)
        if record_id is None or record_kind is None:
            raise ContractError("record_identity_invalid")
        if args.gate in LIVE_GATES and record_kind != "live_row":
            comparisons.append(
                invalid_comparison("input.gate", "live_gate_requires_live_row")
            )
            raise ContractError("gate_record_kind_mismatch")

        roots = repository_roots(repository_map)
        inventory, _ = record_inventory(repository_map)
        if record_id not in inventory:
            raise ContractError("record_missing_from_inventory")
        inventory_entry = inventory[record_id]
        if inventory_entry.get("kind") != record_kind:
            raise ContractError("record_inventory_kind_mismatch")
        if inventory_entry.get("repository") not in roots:
            raise ContractError("record_inventory_repository_unmapped")

        planning = require_mapping(raw_record["planning"], "planning")
        store_repository = str(planning["store_repository"])
        store_root = roots.get(store_repository)
        if store_root is None:
            raise ContractError("store_repository_unmapped")
        output_path = (
            validate_output_path(args.output, store_root)
            if args.output is not None
            else None
        )
        status = load_openspec_status(store_root=store_root)
        baseline_sha, observed_head = evaluate_planning(
            record=raw_record,
            store_root=store_root,
            status=status,
            comparisons=comparisons,
        )
        evaluate_repositories(
            record=raw_record,
            roots=roots,
            store_repository=store_repository,
            baseline_sha=baseline_sha,
            excluded_output=output_path,
            comparisons=comparisons,
        )
        for raw in require_list(raw_record.get("sources"), "sources"):
            evaluate_file_expectation(
                entry=require_mapping(raw, "source"),
                roots=roots,
                field_prefix="source",
                comparisons=comparisons,
            )
        for raw in require_list(raw_record.get("mechanisms"), "mechanisms"):
            evaluate_file_expectation(
                entry=require_mapping(raw, "mechanism"),
                roots=roots,
                field_prefix="mechanism",
                comparisons=comparisons,
            )
        evaluate_dependencies(
            record=raw_record,
            repository_map=repository_map,
            roots=roots,
            comparisons=comparisons,
        )
        dependency_edges = evaluate_dependency_observations(
            repository_map=repository_map,
            roots=roots,
            comparisons=comparisons,
        )
        evaluate_prerequisites(
            record=raw_record,
            repository_map=repository_map,
            roots=roots,
            comparisons=comparisons,
        )
        evaluate_live(
            record=raw_record,
            gate=args.gate,
            inventory_entry=inventory_entry,
            repository_map=repository_map,
            comparisons=comparisons,
        )
        affected = affected_records(
            record_id=record_id,
            comparisons=comparisons,
            repository_map=repository_map,
            dependency_edges=dependency_edges,
        )
    except ContractError as exc:
        comparisons.append(invalid_comparison("input.contract", str(exc)))
    except LocalIdentityUnavailable as exc:
        comparisons.append(
            Comparison(
                field="local.identity",
                expected="resolvable",
                current=None,
                decision="blocked",
                source="local_preflight",
                code=str(exc),
                global_scope=True,
            )
        )
    # The CLI boundary must always emit the contracted redacted JSON shape, even
    # for an unexpected implementation defect. Exception values are never used.
    except Exception as exc:  # noqa: BLE001
        comparisons.append(
            invalid_comparison("validator.internal", f"internal_{type(exc).__name__}")
        )

    record_id, record_kind = safe_record_identity(raw_record)
    if repository_map is not None and roots and comparisons and not affected:
        try:
            affected = affected_records(
                record_id=record_id or "",
                comparisons=comparisons,
                repository_map=repository_map,
                dependency_edges=dependency_edges,
            )
        except ContractError:
            affected = []
    result = build_result(
        record_id=record_id,
        record_kind=record_kind,
        gate=args.gate,
        baseline_sha=baseline_sha,
        observed_head=observed_head,
        comparisons=comparisons,
        affected=affected,
        observed_at=args.observed_at,
    )
    payload = canonical_output(result)
    if output_path is not None and result["decision"] != "invalid":
        try:
            atomic_write(output_path, payload)
        except OSError:
            result = build_result(
                record_id=record_id,
                record_kind=record_kind,
                gate=args.gate,
                baseline_sha=baseline_sha,
                observed_head=observed_head,
                comparisons=[
                    *comparisons,
                    invalid_comparison("output.write", "atomic_write_failed"),
                ],
                affected=affected,
                observed_at=args.observed_at,
            )
            payload = canonical_output(result)
    sys.stdout.buffer.write(payload)
    return int(result["exit_code"])


if __name__ == "__main__":
    raise SystemExit(main())
