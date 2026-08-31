#!/opt/homebrew/bin/python3
"""Run value-blind, bounded CLI probes from a declarative JSON manifest.

The manifest contains executable-plus-argument-array records; no shell is
invoked and no credential value may appear in argv. Each row is run with only
an explicit environment allowlist. Raw stdout/stderr are never written to the
result; only sizes, hashes, sentinel booleans, and classified diagnostics are
retained.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import pty
import re
import select
import signal
import subprocess
import time
from pathlib import Path
from typing import Any

SECRET_RE = re.compile(r"(?i)(?:sk-|xai-|pmv_|token=|api[_-]?key=|authorization:)\S+")
ERROR_RE = re.compile(r"(?i)(?:authentication|unauthorized|invalid api key|reconnect|serialization error|provider error|stream decode|timed out|timeout)")
FORBIDDEN_ARG_RE = re.compile(r"(?i)(?:--api-key|--apikey|--key|-k$|authorization|bearer\s+|sk-|xai-|pmv_)")


def classify_diagnostic(text: str, *, timed_out: bool = False) -> str:
    """Return an enumerated class; never retain free-form CLI output."""
    if timed_out:
        return "timeout"
    lowered = text.lower()
    if "serialization" in lowered:
        return "serialization_error"
    if "stream decode" in lowered or "failed to parse" in lowered:
        return "stream_decode_error"
    if "authentication" in lowered or "unauthorized" in lowered or "api key" in lowered:
        return "authentication_error"
    if "reconnect" in lowered:
        return "reconnect_error"
    if "provider error" in lowered or "provider" in lowered and "error" in lowered:
        return "provider_error"
    if "permission" in lowered or "denied" in lowered:
        return "permission_error"
    if "not found" in lowered or "no such file" in lowered:
        return "missing_executable_or_file"
    if "manifest/probe error" in lowered:
        return "manifest_or_probe_error"
    return "other_output"


def digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", "replace")).hexdigest()[:16]


ANSI_RE = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]")


FINAL_CONTAINER_KEYS = {"result", "final", "output"}
# 2026-08-31 strictness tightening: the sentinel may never be credited from
# these containers even inside an assistant message — metadata/signature
# fields and thinking/tool blocks can echo the prompt; only final assistant
# text proves the route works.
NON_ASSISTANT_CONTAINER_TYPES = {"thinking", "tool_use", "tool_result"}
NON_ASSISTANT_KEYS = {"metadata", "signature"}
# 2026-08-31 JSONL (kilo --format json) contract: trailing records after
# the final formal text carrier may only be end-of-turn control records;
# any content-bearing record (text, thinking, tool) after the last carrier
# is a false accept. Control record observed in kilo output: step_finish.
JSONL_CONTROL_TYPES = {"step_finish", "step-finish"}
# 2026-08-31 grok session-envelope contract: `grok --output-format json`
# emits one JSON document whose top-level "text" string IS the final
# assistant reply; the "thought" field is reasoning and is never credited.
GROK_ENVELOPE_KEYS = {"text", "stopReason", "num_turns"}


def _jsonl_text_carrier(record: Any) -> str | None:
    """Formal kilo text carrier: record.type == "text" with
    record.part.type == "text" and a string record.part.text."""
    if (isinstance(record, dict) and record.get("type") == "text"
            and isinstance(record.get("part"), dict)
            and record["part"].get("type") == "text"
            and isinstance(record["part"].get("text"), str)):
        return record["part"]["text"]
    return None


def _jsonl_verdict(records: list, expected: str) -> bool | None:
    """Carrier-anchored JSONL verdict. None = no formal carriers, so the
    caller falls through to the generic legacy contract unchanged."""
    carriers = [(i, t) for i, r in enumerate(records)
                if (t := _jsonl_text_carrier(r)) is not None]
    if not carriers:
        return None
    last_i, last_text = carriers[-1]
    if last_text != expected:
        return False
    for rec in records[last_i + 1:]:
        if not (isinstance(rec, dict) and rec.get("type") in JSONL_CONTROL_TYPES):
            return False
    return True


def contains_final_assistant_text(value: Any, expected: str, *, assistant_context: bool = False) -> bool:
    """TRUE only when the FINAL assistant content block is exactly the sentinel.

    Final-block semantics (2026-08-31): inside an assistant/final/result
    message carrying a content list, the LAST content block must BE the
    sentinel — a text block (or plain string) equal to it. A sentinel text
    followed by ANY later block (more text, thinking, tool_use, or
    tool_result) is a false accept and is rejected; this is stricter than
    scanning only text-bearing blocks, which would credit a sentinel echoed
    before a trailing tool block. Without a content list the recursive
    role/type/key contract applies as before; sentinel strings in user
    prompts, thinking, tool blocks, metadata, or signatures are never
    credited.
    """
    if isinstance(value, str):
        return assistant_context and value == expected
    if isinstance(value, dict):
        if GROK_ENVELOPE_KEYS <= set(value):
            # grok session envelope: the top-level "text" string is the
            # final assistant reply; thought/usage/session metadata are
            # never credited.
            return value.get("text") == expected
        if value.get("type") in NON_ASSISTANT_CONTAINER_TYPES:
            return False
        role = value.get("role")
        is_assistant = (assistant_context or role == "assistant"
                        or value.get("type") in {"result", "final", "assistant"})
        if is_assistant and isinstance(value.get("content"), list):
            content = value["content"]
            if not content:
                return False
            last = content[-1]
            if isinstance(last, str):
                return last == expected
            if (isinstance(last, dict) and last.get("type") == "text"
                    and isinstance(last.get("text"), str)):
                return last["text"] == expected
            return False
        for key, item in value.items():
            if key in NON_ASSISTANT_KEYS:
                continue
            child_context = is_assistant or key in FINAL_CONTAINER_KEYS
            if contains_final_assistant_text(item, expected, assistant_context=child_context):
                return True
        return False
    if isinstance(value, list):
        # Final-message semantics (2026-08-31): in a list of message objects,
        # only the LAST assistant/result message may credit the sentinel — an
        # earlier assistant echo followed by a different final message is a
        # false accept. Non-message lists keep the any() contract.
        msg_idx = [i for i, item in enumerate(value)
                   if isinstance(item, dict)
                   and (item.get("role") == "assistant"
                        or item.get("type") in {"result", "final", "assistant"})]
        if msg_idx:
            return contains_final_assistant_text(value[msg_idx[-1]], expected,
                                                 assistant_context=assistant_context)
        return any(contains_final_assistant_text(item, expected, assistant_context=assistant_context) for item in value)
    return False


def exact_sentinel(expected: str, output: str) -> bool:
    """Accept only final assistant text, never prompt/tool/metadata substrings.

    Whole-output JSON parse first (goose pretty session JSON), then a JSONL
    path (kilo --format json: one JSON record per line — the sentinel is
    credited only from the LAST formal text carrier, with only end-of-turn
    control records allowed after it), then the original line-based paths
    (plain sentinel line, single-line JSON record) which still fail
    conservatively on trailing logs or duplicates. The strict context
    contract is enforced by contains_final_assistant_text (tightened
    2026-08-31): the sentinel is accepted only as an assistant/final/
    result text value — never from prompt, thinking, metadata, signature,
    or tool blocks.
    """
    cleaned = ANSI_RE.sub("", output).replace("\r", "")
    stripped = cleaned.strip()
    if not stripped:
        return False
    try:
        parsed = json.loads(stripped)
    except (TypeError, ValueError):
        parsed = None
    if parsed is not None:
        return contains_final_assistant_text(parsed, expected)
    lines = [line.strip() for line in cleaned.splitlines() if line.strip()]
    if not lines:
        return False
    # JSONL path (kilo --format json): every non-empty line is one JSON
    # record (step_start / text / step_finish events). The sentinel is
    # credited ONLY from the last formal text carrier, and only end-of-turn
    # control records may trail it (2026-08-31). Outputs with no formal
    # carriers fall through to the generic contract below unchanged.
    if len(lines) > 1:
        records = []
        all_json = True
        for line in lines:
            try:
                records.append(json.loads(line))
            except (TypeError, ValueError):
                all_json = False
                break
        if all_json:
            verdict = _jsonl_verdict(records, expected)
            if verdict is not None:
                return verdict
    if lines[-1] == expected:
        return lines.count(expected) == 1 and not any("Reply with exactly:" in line for line in lines[:-1])
    try:
        parsed = json.loads(lines[-1])
    except (TypeError, ValueError):
        return False
    return contains_final_assistant_text(parsed, expected)


def validate_row(row: dict[str, Any]) -> None:
    argv = row.get("argv")
    if not isinstance(argv, list) or not argv or not all(isinstance(x, str) for x in argv):
        raise ValueError("argv must be a non-empty string array")
    for arg in argv:
        if FORBIDDEN_ARG_RE.search(arg):
            raise ValueError(f"credential-bearing or forbidden argument in row {row.get('id')}")
    if not isinstance(row.get("cwd"), str):
        raise ValueError(f"cwd missing in row {row.get('id')}")
    if not isinstance(row.get("expected"), str) or not row["expected"]:
        raise ValueError(f"expected sentinel missing in row {row.get('id')}")
    if not isinstance(row.get("endpoint_path"), str) or not row["endpoint_path"].startswith("/"):
        raise ValueError(f"endpoint_path missing in row {row.get('id')}")
    if not isinstance(row.get("timeout", 0), (int, float)) or row["timeout"] <= 0:
        raise ValueError(f"positive timeout missing in row {row.get('id')}")
    if not isinstance(row.get("env_allow", []), list) or not all(isinstance(x, str) for x in row["env_allow"]):
        raise ValueError(f"env_allow must be a string array in row {row.get('id')}")
    if not isinstance(row.get("env_set", {}), dict) or not all(isinstance(k, str) and isinstance(v, str) for k, v in row.get("env_set", {}).items()):
        raise ValueError(f"env_set must be a string map in row {row.get('id')}")
    for key, value in row.get("env_set", {}).items():
        if re.search(r"(?i)(api.?key|token$|^token_|_token$|secret|password|authorization)", key) or SECRET_RE.search(value):
            raise ValueError(f"secret-bearing env_set entry in row {row.get('id')}")
    if row.get("fallback") is True:
        if not row.get("native_failure_class") or str(row["native_failure_class"]).startswith("pending-"):
            raise ValueError(f"fallback row lacks captured native_failure_class: {row.get('id')}")
        if row.get("endpoint_path") != "/chat/completions":
            raise ValueError(f"fallback row must declare versionless /chat/completions: {row.get('id')}")
        if row.get("classification") == "chat-fallback-only-client":
            if row.get("fallback_for") is not None:
                raise ValueError(f"chat-only client row must not declare fallback_for: {row.get('id')}")
        elif not row.get("fallback_for"):
            raise ValueError(f"fallback row lacks fallback_for: {row.get('id')}")


def run_pty(row: dict[str, Any], env: dict[str, str]) -> dict[str, Any]:
    started = time.monotonic()
    master, slave = pty.openpty()
    process = subprocess.Popen(
        row["argv"],
        cwd=row["cwd"],
        env=env,
        stdin=slave,
        stdout=slave,
        stderr=slave,
        start_new_session=True,
        close_fds=True,
    )
    os.close(slave)
    chunks = bytearray()
    timed_out = False
    deadline = started + float(row["timeout"])
    try:
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                timed_out = True
                try:
                    os.killpg(process.pid, signal.SIGTERM)
                except ProcessLookupError:
                    pass
                try:
                    process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    try:
                        os.killpg(process.pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                    process.wait(timeout=3)
                break
            readable, _, _ = select.select([master], [], [], min(0.25, remaining))
            if readable:
                try:
                    chunks.extend(os.read(master, 8192))
                except OSError:
                    pass
            if process.poll() is not None:
                while True:
                    readable, _, _ = select.select([master], [], [], 0)
                    if not readable:
                        break
                    try:
                        chunks.extend(os.read(master, 8192))
                    except OSError:
                        break
                break
    finally:
        os.close(master)
    output = bytes(chunks).decode("utf-8", "replace")
    return {
        "id": row["id"],
        "route": row.get("route"),
        "phase": row.get("phase"),
        "classification": row.get("classification"),
        "fallback": row.get("fallback", False),
        "native_failure_class": row.get("native_failure_class"),
        "fallback_for": row.get("fallback_for"),
        "endpoint_path": row.get("endpoint_path"),
        "returncode": None if timed_out else process.returncode,
        "timeout": timed_out,
        "duration_seconds": round(time.monotonic() - started, 3),
        "stdout_bytes": len(output.encode("utf-8", "replace")),
        "stderr_bytes": 0,
        "stdout_sha256_16": digest(output),
        "stderr_sha256_16": digest(""),
        "sentinel": exact_sentinel(row["expected"], output),
        "sentinel_substring": row["expected"] in output,
        "error_text": bool(ERROR_RE.search(output)),
        "diagnostic_class": classify_diagnostic(output, timed_out=timed_out),
    }


def run_row(row: dict[str, Any]) -> dict[str, Any]:
    validate_row(row)
    env = {"PATH": os.environ.get("PATH", ""), "HOME": os.environ.get("HOME", "")}
    for name in ("TERM", "TMPDIR", "USER", "LOGNAME", "SHELL", "LANG", "LC_ALL", "XDG_CONFIG_HOME", "XDG_DATA_HOME", "XDG_STATE_HOME", "NO_COLOR"):
        if name in os.environ:
            env[name] = os.environ[name]
    for name in row["env_allow"]:
        if name in os.environ:
            env[name] = os.environ[name]
    for name, value in row.get("env_set", {}).items():
        env[name] = value
    if row.get("pty") is True:
        return run_pty(row, env)
    started = time.monotonic()
    try:
        completed = subprocess.run(
            row["argv"],
            cwd=row["cwd"],
            env=env,
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            timeout=float(row["timeout"]),
            check=False,
        )
        stdout = completed.stdout or ""
        stderr = completed.stderr or ""
        merged = stdout + "\n" + stderr
        return {
            "id": row["id"],
            "route": row.get("route"),
            "phase": row.get("phase"),
            "classification": row.get("classification"),
            "fallback": row.get("fallback", False),
            "native_failure_class": row.get("native_failure_class"),
            "fallback_for": row.get("fallback_for"),
            "endpoint_path": row.get("endpoint_path"),
            "returncode": completed.returncode,
            "timeout": False,
            "duration_seconds": round(time.monotonic() - started, 3),
            "stdout_bytes": len(stdout.encode("utf-8", "replace")),
            "stderr_bytes": len(stderr.encode("utf-8", "replace")),
            "stdout_sha256_16": digest(stdout),
            "stderr_sha256_16": digest(stderr),
            "sentinel": exact_sentinel(row["expected"], stdout),
            "sentinel_substring": row["expected"] in stdout,
            "error_text": bool(ERROR_RE.search(merged)),
            "diagnostic_class": classify_diagnostic(stderr or stdout),
        }
    except subprocess.TimeoutExpired as exc:
        out = exc.stdout or ""
        err = exc.stderr or ""
        if isinstance(out, bytes):
            out = out.decode("utf-8", "replace")
        if isinstance(err, bytes):
            err = err.decode("utf-8", "replace")
        return {
            "id": row["id"],
            "route": row.get("route"),
            "phase": row.get("phase"),
            "classification": row.get("classification"),
            "fallback": row.get("fallback", False),
            "native_failure_class": row.get("native_failure_class"),
            "fallback_for": row.get("fallback_for"),
            "endpoint_path": row.get("endpoint_path"),
            "returncode": None,
            "timeout": True,
            "duration_seconds": round(time.monotonic() - started, 3),
            "stdout_bytes": len(out.encode("utf-8", "replace")),
            "stderr_bytes": len(err.encode("utf-8", "replace")),
            "stdout_sha256_16": digest(out),
            "stderr_sha256_16": digest(err),
            "sentinel": False,
            "error_text": True,
            "diagnostic_class": "timeout",
        }


def load_dispositions(manifest_path: Path, rows: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    evidence_path = manifest_path.parent / "cli-disposition-results.json"
    if not evidence_path.is_file():
        return {}
    try:
        data = json.loads(evidence_path.read_text())
    except Exception:
        return {}
    records = {}
    for record in data.get("results", []):
        if not isinstance(record, dict):
            continue
        record_id = record.get("id")
        if not isinstance(record_id, str):
            continue
        source = record.get("source")
        source_ok = False
        if isinstance(source, str):
            source_path = manifest_path.parent.parent / source
            source_ok = source_path.is_file() and hashlib.sha256(source_path.read_bytes()).hexdigest() == record.get("source_sha256")
        row = rows.get(record.get("id"))
        row_ok = False
        if row is not None:
            row_ok = hashlib.sha256(json.dumps(row, sort_keys=True, separators=(",", ":")).encode()).hexdigest() == record.get("manifest_row_sha256")
        if source_ok and row_ok:
            records[record["id"]] = record
    return records


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--phase", choices=["baseline", "candidate"], required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    manifest = json.loads(args.manifest.read_text())
    rows = manifest.get("probes", [])
    if not isinstance(rows, list):
        raise SystemExit("manifest.probes must be an array")
    manifest_by_id: dict[str, dict[str, Any]] = {}
    for row in rows:
        if not isinstance(row, dict):
            raise SystemExit("every manifest.probes item must be an object")
        try:
            validate_row(row)
        except Exception as exc:
            raise SystemExit(f"invalid manifest row {row.get('id')}: {exc}") from exc
        row_id = row.get("id")
        if not isinstance(row_id, str) or not row_id:
            raise SystemExit("every manifest row requires a unique id")
        if row_id in manifest_by_id:
            raise SystemExit(f"duplicate manifest row id: {row_id}")
        manifest_by_id[row_id] = row

    dispositions = load_dispositions(args.manifest, manifest_by_id)
    selected = [row for row in rows if row.get("phase") == args.phase and row.get("enabled", True)]
    results = []
    for row in selected:
        try:
            result = run_row(row)
        except Exception as exc:
            result = {
                "id": row.get("id"),
                "route": row.get("route"),
                "phase": args.phase,
                "classification": row.get("classification"),
                "fallback": row.get("fallback", False),
                "native_failure_class": row.get("native_failure_class"),
                "fallback_for": row.get("fallback_for"),
                "endpoint_path": row.get("endpoint_path"),
                "returncode": None,
                "timeout": False,
                "sentinel": False,
                "sentinel_substring": False,
                "error_text": True,
                "diagnostic_class": classify_diagnostic(f"manifest/probe error: {type(exc).__name__}: {exc}"),
            }
        results.append(result)
        print(
            f"PROBE {result['id']} phase={args.phase} rc={result.get('returncode')} "
            f"timeout={result.get('timeout')} sentinel={result.get('sentinel')} "
            f"error_text={result.get('error_text')}"
        )

    required = [row for row in selected if row.get("required", True)]
    by_id = {result.get("id"): result for result in results}

    def successful(result: dict[str, Any] | None) -> bool:
        return bool(result) and result.get("returncode") == 0 and result.get("sentinel") is True and result.get("error_text") is False

    fallback_pairs_ok = True
    for row in required:
        if row.get("fallback") is not True:
            continue
        if row.get("classification") == "chat-fallback-only-client":
            fallback_pairs_ok = fallback_pairs_ok and row.get("fallback_for") is None
            continue
        native_id = row.get("fallback_for")
        native_decl = manifest_by_id.get(native_id)
        native_result = by_id.get(native_id)
        if native_decl is None or native_decl.get("phase") != args.phase:
            fallback_pairs_ok = False
            continue
        if native_result is not None:
            record = dispositions.get(native_id)
            fallback_pairs_ok = fallback_pairs_ok and not successful(native_result) and bool(record) and (
                record.get("fallback_id") == row.get("id")
                and record.get("native_failure_class") == row.get("native_failure_class")
                and record.get("diagnostic_class") == native_result.get("diagnostic_class")
            )
        else:
            # A disabled native row is an intentional, evidence-backed control;
            # its retained structured record is the precondition for the fallback.
            record = dispositions.get(native_id)
            fallback_pairs_ok = fallback_pairs_ok and (
                native_decl.get("enabled", True) is False
                and str(native_decl.get("native_failure_class", "")).startswith("fbc-")
                and native_decl.get("native_failure_class") == row.get("native_failure_class")
                and bool(native_decl.get("disabled_reason"))
                and bool(record)
                and record.get("fallback_id") == row.get("id")
                and record.get("native_failure_class") == row.get("native_failure_class")
                and record.get("fallback_endpoint_path") == row.get("endpoint_path")
                and record.get("fallback_returncode") == 0
                and record.get("fallback_sentinel") is True
            )
    passed = bool(selected) and bool(required) and fallback_pairs_ok and all(successful(by_id.get(row.get("id"))) for row in required)
    output = {
        "phase": args.phase,
        "value_blind": True,
        "manifest_rows": len(rows),
        "disabled_rows": sum(not row.get("enabled", True) for row in rows),
        "dispositions_loaded": len(dispositions),
        "selected": len(selected),
        "required": len(required),
        "passed": passed,
        "results": results,
    }
    if args.output:
        args.output.write_text(json.dumps(output, indent=2) + "\n")
    print(f"SUMMARY phase={args.phase} {'PASS' if passed else 'FAIL'} selected={len(selected)} required={len(required)}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
