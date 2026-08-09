#!/usr/bin/env python3
"""Run two-gate, native-status reviews for seven coding-agent CLIs."""

from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import locale
import os
import platform
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
FIXTURE = ROOT / "review-context.md"
SCHEMA = "seven-cli-evidence/v1"
PARSER_VERSION = "seven-cli-parser/v1"
MAX_FIXTURE_BYTES = 20_000
MAX_STREAM_BYTES = 1_048_576
VERDICT_RE = re.compile(
    r"^\s*(?:[-*•]\s*)?\*{0,2}VERDICT\s*:\s*(APPROVE_WITH_CONDITIONS|APPROVE|REJECT)\*{0,2}\s*$",
    re.IGNORECASE | re.MULTILINE,
)
FATAL_INVOCATION = ("usage:", "unknown option", "unrecognized option", "invalid value")
FATAL_CONFIG = (
    "authentication failed", "unauthorized", "unknown provider", "model not found",
    "model unavailable", "connection refused",
)
SECRET_PATTERNS = (
    re.compile(r"\b(mcpr_[A-Za-z0-9_-]+)\b"),
    re.compile(r"\b(sk-[A-Za-z0-9_-]{8,})\b"),
    re.compile(r"(?i)(api[_-]?key|token|secret|password)(\s*[=:]\s*)([^\s,;]+)"),
)


@dataclass(frozen=True)
class CliSpec:
    name: str
    executable: str
    argv: tuple[str, ...]
    version_argv: tuple[str, ...]
    review_timeout: int


SPECS: dict[str, CliSpec] = {
    "claude": CliSpec("claude", "claude", ("claude", "-p", "{prompt}", "--max-turns", "10", "--output-format", "text", "--no-session-persistence"), ("claude", "--version"), 600),
    "codex": CliSpec("codex", "codex", ("codex", "exec", "--ephemeral", "{prompt}"), ("codex", "--version"), 600),
    "agy": CliSpec("agy", "agy", ("agy", "-p", "{prompt}", "--output-format", "text", "--print-timeout", "5m"), ("agy", "--version"), 600),
    "kimi": CliSpec("kimi", "kimi", ("kimi", "-p", "{prompt}", "--output-format", "text"), ("kimi", "--version"), 600),
    "opencode": CliSpec("opencode", "opencode", ("opencode", "run", "{prompt}"), ("opencode", "--version"), 600),
    "pi": CliSpec("pi", "pi", ("pi", "-p", "--no-session", "--no-tools", "--no-extensions", "{prompt}"), ("pi", "--version"), 900),
    "goose": CliSpec("goose", "goose", ("goose", "run", "--no-session", "-q", "--max-turns", "10", "-t", "{prompt}"), ("goose", "--version"), 600),
}
BATCHES = (("claude", "agy", "goose"), ("opencode", "codex", "kimi"), ("pi",))


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_json(data: Any) -> bytes:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def redact(data: bytes) -> tuple[bytes, int]:
    text = data.decode("utf-8", errors="replace")
    hits = 0
    for pattern in SECRET_PATTERNS:
        def repl(match: re.Match[str]) -> str:
            nonlocal hits
            hits += 1
            if match.lastindex and match.lastindex >= 3:
                return f"{match.group(1)}{match.group(2)}[REDACTED]"
            return "[REDACTED]"
        text = pattern.sub(repl, text)
    return text.encode("utf-8"), hits


def executable_identity(path: str | None) -> dict[str, Any]:
    if not path:
        return {"path": None, "sha256": None, "size": None}
    p = Path(path).resolve()
    try:
        data = p.read_bytes()
        return {"path": str(p), "sha256": sha256_bytes(data), "size": len(data)}
    except OSError:
        stat = p.stat()
        return {"path": str(p), "sha256": None, "size": stat.st_size}


def version(spec: CliSpec) -> dict[str, Any]:
    try:
        proc = subprocess.run(spec.version_argv, capture_output=True, timeout=30, stdin=subprocess.DEVNULL)
        raw = proc.stdout or proc.stderr
        text = raw.decode("utf-8", errors="replace").strip().splitlines()
        return {"exit_code": proc.returncode, "text": text[0] if text else "", "sha256": sha256_bytes(raw)}
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"exit_code": None, "text": f"UNAVAILABLE:{type(exc).__name__}", "sha256": None}


def argv_for(spec: CliSpec, prompt: str) -> list[str]:
    return [prompt if part == "{prompt}" else part for part in spec.argv]


def public_argv(argv: list[str], prompt: str) -> list[str]:
    marker = f"<PROMPT bytes={len(prompt.encode('utf-8'))} sha256={sha256_bytes(prompt.encode())}>"
    return [marker if part == prompt else part for part in argv]


def run_process(argv: list[str], timeout_seconds: int) -> dict[str, Any]:
    started_utc = utc_now()
    started_mono = time.monotonic_ns()
    return_code: int | None = None
    timed_out = False
    termination_stage: str | None = None
    raw_stdout = b""
    raw_stderr = b""
    try:
        proc = subprocess.Popen(
            argv, cwd=ROOT, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, start_new_session=True,
        )
        try:
            raw_stdout, raw_stderr = proc.communicate(timeout=timeout_seconds)
        except subprocess.TimeoutExpired:
            timed_out = True
            termination_stage = "SIGTERM"
            os.killpg(proc.pid, signal.SIGTERM)
            try:
                raw_stdout, raw_stderr = proc.communicate(timeout=10)
            except subprocess.TimeoutExpired:
                termination_stage = "SIGKILL"
                os.killpg(proc.pid, signal.SIGKILL)
                raw_stdout, raw_stderr = proc.communicate()
        return_code = proc.returncode
    except FileNotFoundError as exc:
        return_code = 127
        raw_stderr = str(exc).encode()

    elapsed_ms = round((time.monotonic_ns() - started_mono) / 1_000_000, 3)
    output_limited = len(raw_stdout) > MAX_STREAM_BYTES or len(raw_stderr) > MAX_STREAM_BYTES
    retained_stdout, stdout_secret_hits = redact(raw_stdout[:MAX_STREAM_BYTES])
    retained_stderr, stderr_secret_hits = redact(raw_stderr[:MAX_STREAM_BYTES])
    return {
        "started_utc": started_utc,
        "finished_utc": utc_now(),
        "elapsed_ms": elapsed_ms,
        "timeout_seconds": timeout_seconds,
        "timed_out": timed_out,
        "termination_stage": termination_stage,
        "return_code": return_code,
        "signal": -return_code if return_code is not None and return_code < 0 else None,
        "output_limited": output_limited,
        "raw_stdout_bytes": len(raw_stdout),
        "raw_stderr_bytes": len(raw_stderr),
        "raw_stdout_sha256": sha256_bytes(raw_stdout),
        "raw_stderr_sha256": sha256_bytes(raw_stderr),
        "retained_stdout": retained_stdout,
        "retained_stderr": retained_stderr,
        "retained_stdout_sha256": sha256_bytes(retained_stdout),
        "retained_stderr_sha256": sha256_bytes(retained_stderr),
        "secret_hits": stdout_secret_hits + stderr_secret_hits,
    }


def process_status(result: dict[str, Any]) -> str | None:
    code = result["return_code"]
    stderr = result["retained_stderr"].decode("utf-8", errors="replace").lower()
    if code == 127:
        return "MISSING"
    if result["timed_out"]:
        return "TIMEOUT"
    if code is not None and code < 0:
        return "SIGNAL_TERMINATION"
    if result["output_limited"]:
        return "OUTPUT_LIMIT"
    if code not in (0, None):
        if any(token in stderr for token in FATAL_INVOCATION):
            return "INVOCATION_ERROR"
        if any(token in stderr for token in FATAL_CONFIG):
            return "CONFIG_ERROR"
        return "PROCESS_ERROR"
    return None


def smoke_status(result: dict[str, Any]) -> str:
    failure = process_status(result)
    if failure:
        return failure
    text = (result["retained_stdout"] + b"\n" + result["retained_stderr"]).decode("utf-8", errors="replace")
    if not text.strip():
        return "EMPTY_OUTPUT"
    return "PASS" if "CONNECTION_OK" in text else "SEMANTIC_FAILURE"


def review_status(result: dict[str, Any]) -> tuple[str, str | None]:
    failure = process_status(result)
    if failure:
        return failure, None
    stdout = result["retained_stdout"].decode("utf-8", errors="replace")
    if len(stdout.strip()) < 40:
        return "EMPTY_OUTPUT", None
    verdicts = VERDICT_RE.findall(stdout)
    findings = re.findall(r"^\s*(?:[-*•]\s*)?\*{0,2}FINDINGS\s*:\*{0,2}", stdout, re.IGNORECASE | re.MULTILINE)
    recommendations = re.findall(r"^\s*(?:[-*•]\s*)?\*{0,2}RECOMMENDATIONS\s*:\*{0,2}", stdout, re.IGNORECASE | re.MULTILINE)
    if len(verdicts) != 1 or len(findings) != 1 or len(recommendations) != 1:
        return "SEMANTIC_FAILURE", None
    upper = stdout.upper().replace("**FINDINGS:**", "FINDINGS:").replace("**RECOMMENDATIONS:**", "RECOMMENDATIONS:")
    finding_text = upper.split("FINDINGS:", 1)[1].split("RECOMMENDATIONS:", 1)[0].strip()
    recommendation_text = upper.split("RECOMMENDATIONS:", 1)[1].strip()
    if len(finding_text) < 4 or len(recommendation_text) < 4:
        return "SEMANTIC_FAILURE", None
    verdict = verdicts[0].upper()
    if verdict == "REJECT":
        return "REJECTED", verdict
    if verdict == "APPROVE_WITH_CONDITIONS":
        return "PASS_WITH_FINDINGS", verdict
    clean = re.search(r"\b(NONE|NO FINDINGS|NO ISSUES)\b", finding_text) is not None
    return ("PASS" if clean else "PASS_WITH_FINDINGS"), verdict


def persist_probe(cli_dir: Path, probe: str, result: dict[str, Any], metadata: dict[str, Any]) -> list[dict[str, Any]]:
    cli_dir.mkdir(parents=True, exist_ok=True)
    artifacts = []
    streams = {
        f"{probe}.stdout.txt": result["retained_stdout"],
        f"{probe}.stderr.txt": result["retained_stderr"],
    }
    for name, data in streams.items():
        path = cli_dir / name
        path.write_bytes(data)
        artifacts.append({"path": str(path.relative_to(cli_dir.parent.parent)), "bytes": len(data), "sha256": sha256_bytes(data)})
    meta_path = cli_dir / f"{probe}.meta.json"
    rendered = json.dumps(metadata, indent=2, sort_keys=True).encode() + b"\n"
    meta_path.write_bytes(rendered)
    artifacts.append({"path": str(meta_path.relative_to(cli_dir.parent.parent)), "bytes": len(rendered), "sha256": sha256_bytes(rendered)})
    return artifacts


def run_cli(spec: CliSpec, round_dir: Path, fixture: str, fixture_hash: str) -> dict[str, Any]:
    cli_dir = round_dir / spec.name
    exe_path = shutil.which(spec.executable)
    identity = executable_identity(exe_path)
    ver = version(spec)
    common = {
        "schema": SCHEMA,
        "parser_version": PARSER_VERSION,
        "cli": spec.name,
        "executable": identity,
        "version": ver,
        "default_assurance": "NO_OVERRIDE_SUPPLIED",
        "working_directory": str(ROOT),
    }

    smoke_prompt = "Provide one sentence containing CONNECTION_OK. Do not use tools."
    smoke_argv = argv_for(spec, smoke_prompt)
    smoke = run_process(smoke_argv, min(spec.review_timeout, 300))
    smoke_state = smoke_status(smoke)
    smoke_meta = {
        **common,
        "probe": "smoke",
        "status": smoke_state,
        "argv": public_argv(smoke_argv, smoke_prompt),
        "prompt_bytes": len(smoke_prompt.encode()),
        "prompt_sha256": sha256_bytes(smoke_prompt.encode()),
        **{k: v for k, v in smoke.items() if not k.startswith("retained_")},
    }
    artifacts = persist_probe(cli_dir, "smoke", smoke, smoke_meta)

    if smoke_state != "PASS":
        return {"cli": spec.name, "smoke_status": smoke_state, "review_status": "SKIPPED_PREFLIGHT", "verdict": None, "artifacts": artifacts}

    instruction = (
        "Review the following contract. Do not use tools or discuss CLI flags. "
        "Return exactly one VERDICT line and exactly one non-empty FINDINGS and RECOMMENDATIONS section."
    )
    review_prompt = instruction + "\n\n" + fixture
    review_argv = argv_for(spec, review_prompt)
    review = run_process(review_argv, spec.review_timeout)
    review_state, verdict = review_status(review)
    review_meta = {
        **common,
        "probe": "review",
        "status": review_state,
        "verdict": verdict,
        "argv": public_argv(review_argv, review_prompt),
        "prompt_bytes": len(review_prompt.encode()),
        "prompt_sha256": sha256_bytes(review_prompt.encode()),
        "fixture_sha256": fixture_hash,
        **{k: v for k, v in review.items() if not k.startswith("retained_")},
    }
    artifacts.extend(persist_probe(cli_dir, "review", review, review_meta))
    return {
        "cli": spec.name,
        "smoke_status": smoke_state,
        "review_status": review_state,
        "verdict": verdict,
        "review_return_code": review["return_code"],
        "review_elapsed_ms": review["elapsed_ms"],
        "artifacts": artifacts,
    }


def atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, prefix=f".{path.name}.", delete=False) as handle:
        handle.write(data)
        temp = Path(handle.name)
    os.replace(temp, path)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--round", required=True)
    parser.add_argument("--only", nargs="*", choices=tuple(SPECS))
    args = parser.parse_args()

    fixture_bytes = FIXTURE.read_bytes()
    if len(fixture_bytes) >= MAX_FIXTURE_BYTES:
        raise SystemExit("fixture exceeds 20,000 UTF-8 bytes")
    fixture = fixture_bytes.decode("utf-8")
    fixture_hash = sha256_bytes(fixture_bytes)
    selected = set(args.only or SPECS)
    round_dir = ROOT / "results" / args.round
    round_dir.mkdir(parents=True, exist_ok=True)
    summaries: list[dict[str, Any]] = []

    for batch in BATCHES:
        names = [name for name in batch if name in selected]
        if not names:
            continue
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(names)) as pool:
            futures = {pool.submit(run_cli, SPECS[name], round_dir, fixture, fixture_hash): name for name in names}
            for future in concurrent.futures.as_completed(futures):
                try:
                    summaries.append(future.result())
                except Exception as exc:
                    summaries.append({"cli": futures[future], "smoke_status": "HARNESS_ERROR", "review_status": "HARNESS_ERROR", "error": repr(exc), "artifacts": []})

    if sha256_bytes(FIXTURE.read_bytes()) != fixture_hash:
        raise SystemExit("fixture mutated during round")
    summaries.sort(key=lambda item: tuple(SPECS).index(item["cli"]))
    artifact_inventory = [artifact for item in summaries for artifact in item.get("artifacts", [])]
    summary = {
        "schema": SCHEMA,
        "parser_version": PARSER_VERSION,
        "round": args.round,
        "generated_utc": utc_now(),
        "fixture": {"path": str(FIXTURE), "bytes": len(fixture_bytes), "sha256": fixture_hash},
        "runner_sha256": sha256_bytes(Path(__file__).read_bytes()),
        "host": {"system": platform.system(), "release": platform.release(), "machine": platform.machine()},
        "locale": locale.setlocale(locale.LC_ALL, None),
        "workdir": str(ROOT),
        "batch_order": [list(batch) for batch in BATCHES],
        "results": summaries,
        "artifacts": artifact_inventory,
    }
    summary_bytes = json.dumps(summary, indent=2, sort_keys=True).encode() + b"\n"
    atomic_write(round_dir / "summary.json", summary_bytes)
    atomic_write(round_dir / "summary.sha256", sha256_bytes(canonical_json(summary)).encode() + b"\n")
    print(summary_bytes.decode())
    accepted = {"PASS", "PASS_WITH_FINDINGS"}
    passed = len(summaries) == len(selected) and all(
        item.get("smoke_status") == "PASS" and item.get("review_status") in accepted
        for item in summaries
    )
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
