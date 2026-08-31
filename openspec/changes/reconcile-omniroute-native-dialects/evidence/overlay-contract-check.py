#!/opt/homebrew/bin/python3
"""Validate the non-destructive candidate overlay contract.

This is a planning/static check only. It never writes user configuration.
"""
from __future__ import annotations

import json
import re
import stat
import sys
import tomllib
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_ROOT = ROOT / "evidence/candidate-templates"
CONTRACT = ROOT / "evidence/overlay-contract.json"
SECRET = re.compile(r"(?i)\b(?:sk|xai|pmv|agt)_[A-Za-z0-9_-]{8,}\b|\b(?:sk|xai)-[A-Za-z0-9_-]{12,}\b|\bBearer\s+[A-Za-z0-9._-]{12,}")


def jsonc_load(text: str) -> Any:
    out: list[str] = []
    i = 0
    in_string = False
    escaped = False
    while i < len(text):
        char = text[i]
        if in_string:
            out.append(char)
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            i += 1
            continue
        if char == '"':
            in_string = True
            out.append(char)
            i += 1
            continue
        if char == "/" and i + 1 < len(text) and text[i + 1] == "/":
            i += 2
            while i < len(text) and text[i] != "\n":
                i += 1
            continue
        if char == "/" and i + 1 < len(text) and text[i + 1] == "*":
            i += 2
            while i + 1 < len(text) and text[i : i + 2] != "*/":
                i += 1
            i += 2
            continue
        out.append(char)
        i += 1
    return json.loads("".join(out))


def load(path: Path) -> Any:
    text = path.read_text(errors="replace")
    if path.suffix == ".json":
        return json.loads(text)
    if path.suffix == ".jsonc":
        return jsonc_load(text)
    if path.suffix == ".toml":
        return tomllib.loads(text)
    return text


def nested(data: Any, dotted: str) -> Any:
    value = data
    for part in dotted.split("."):
        if not isinstance(value, dict) or part not in value:
            return None
        value = value[part]
    return value


def strings(value: Any):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for key, item in value.items():
            yield from strings(key)
            yield from strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from strings(item)


def main() -> int:
    contract = json.loads(CONTRACT.read_text())
    entries = contract.get("entries")
    if not isinstance(entries, list) or not entries:
        raise SystemExit("overlay contract has no entries")
    failures: list[str] = []
    seen: set[str] = set()
    for entry in entries:
        rel = entry.get("template")
        if not isinstance(rel, str) or rel in seen:
            failures.append(f"duplicate or missing template entry: {rel!r}")
            continue
        seen.add(rel)
        path = ROOT / "evidence" / rel
        if not path.is_file():
            failures.append(f"template missing: {rel}")
            continue
        mode = stat.S_IMODE(path.stat().st_mode)
        expected_mode = int(entry.get("expected_mode", "0o600"), 8)
        if mode != expected_mode:
            failures.append(f"mode {mode:o} != {expected_mode:o}: {rel}")
        raw = path.read_text(errors="replace")
        if SECRET.search(raw):
            failures.append(f"credential-shaped literal: {rel}")
        if "sh/Claude-Fable" in raw:
            failures.append(f"stale Claude namespace: {rel}")
        if "dlg/" in raw:
            failures.append(f"retired route: {rel}")
        try:
            data = load(path)
        except Exception as exc:  # noqa: BLE001
            failures.append(f"parse {type(exc).__name__}: {rel}")
            continue
        allowed_top = entry.get("allowed_top_level_keys")
        if isinstance(allowed_top, list) and isinstance(data, dict):
            unexpected = sorted(set(data) - set(allowed_top))
            if unexpected:
                failures.append(f"unlisted top-level fields {unexpected}: {rel}")
        merge_key = entry.get("merge_key", "")
        if isinstance(data, dict) and isinstance(merge_key, str):
            for key_spec in merge_key.split(","):
                root_key = key_spec.split(".", 1)[0].split("[", 1)[0]
                if root_key and root_key not in data and not key_spec.startswith(("profile:", "helper:")):
                    failures.append(f"merge root {root_key!r} missing: {rel}")
        for protected in entry.get("forbidden_top_level_keys", []):
            if nested(data, protected) is not None:
                failures.append(f"protected field present in overlay ({protected}): {rel}")
        if not entry.get("merge_key"):
            failures.append(f"merge_key missing: {rel}")
        operation = entry.get("operation")
        if not isinstance(operation, str) or not operation:
            failures.append(f"operation missing: {rel}")
        if entry.get("format") == "shell-helper":
            if "OMNIROUTE_API_KEY" not in raw:
                failures.append(f"helper lacks env reference: {rel}")
            if not re.search(r"(?m)^print -r -- \"\$OMNIROUTE_API_KEY\"$", raw):
                failures.append(f"helper output is not one explicit credential line: {rel}")
            if re.search(r"(?m)(?:\btee\b|>>|\b(?:logger|syslog)\b|\bcurl\b|\bssh\b)", raw):
                failures.append(f"helper contains logging/network primitive: {rel}")
        if rel.endswith("cline/data/settings/providers.json"):
            if any(value == "pm/Claude-Fable" for value in strings(data)):
                failures.append("Cline overlay contains unproven PM model")
            providers = data.get("providers", {}) if isinstance(data, dict) else {}
            if "openai-omniroute-chat" not in providers:
                failures.append("Cline fallback provider missing")
        if rel.endswith(".codex/omniroute.config.toml"):
            if nested(data, "model") != "sh/gpt-5.6-sol" or nested(data, "model_provider") != "omniroute":
                failures.append("Codex profile binding mismatch")
        if rel.endswith(".omp/agent/models.yml") and "modelRoles:" in raw:
            failures.append("OMP overlay contains role assignment")
    actual_templates = {
        f"candidate-templates/{p.relative_to(TEMPLATE_ROOT)}"
        for p in TEMPLATE_ROOT.rglob("*")
        if p.is_file() and p.name != ".DS_Store" and "__pycache__" not in p.parts
    }
    for orphan in sorted(actual_templates - seen):
        failures.append(f"orphan template not referenced by contract: {orphan}")
    expected_count = len(entries)
    if len(seen) != expected_count:
        failures.append(f"contract entry accounting mismatch: {len(seen)} != {expected_count}")
    if failures:
        for failure in failures:
            print("FAIL", failure)
        print(f"SUMMARY FAIL findings={len(failures)}")
        return 1
    print(f"SUMMARY PASS overlays={expected_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
