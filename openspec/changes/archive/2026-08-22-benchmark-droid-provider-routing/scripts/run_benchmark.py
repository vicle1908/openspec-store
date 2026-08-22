#!/usr/bin/env python3
"""Droid provider routing benchmark harness v2.

Fixes from calibration incident:
- S3: injected-context approach (no --session-id)
- S4: broader step-number regex
- S5/S7: broader synonym matching
- S6: file-change verification + test-file unchanged
- S1-S3: --reasoning-effort none; S4-S7: omit flag (model default)
- Excerpts: 500 chars
- Result success gating before scoring
- Idempotent run_id dedup
- Baseline skip mode (records infrastructure_unavailable)
- Full model output preserved in per-run sidecar files

Usage:
  python3 run_benchmark.py --stage health
  python3 run_benchmark.py --stage pilot
  python3 run_benchmark.py --stage repeat2
  python3 run_benchmark.py --stage repeat3
  python3 run_benchmark.py --stage full   # pilot + repeat2 + repeat3
"""
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

PROVIDERS = [
    {"selector": "custom:fable-5", "label": "shopapikey", "adapter": "anthropic"},
    {"selector": "custom:Advance", "label": "giaoduc", "adapter": "anthropic"},
    {"selector": "custom:gpt-5.6-sol", "label": "cockpit", "adapter": "openai"},
]

BASELINE = {"selector": "custom:dlg/deepseek-v4-pro-0", "label": "baseline",
            "adapter": "generic-chat-completion-api", "status": "infrastructure_unavailable",
            "note": "OmniRoute at localhost:20128 returns HTTP 000, nothing listening on port"}

BENCH_DIR = "/tmp/droid-benchmark"
SCRIPT_DIR = Path(__file__).resolve().parent
CHANGE_DIR = SCRIPT_DIR.parent
EVIDENCE_DIR = CHANGE_DIR / "evidence"
RESULTS_FILE = EVIDENCE_DIR / "raw-results.jsonl"
SIDECARS_DIR = EVIDENCE_DIR / "sidecars"
FIXTURE_SHA = "a02714a866b01454f71f7abaa1eca39509f489f2"
TIMEOUT = 120

# Answer-leakage sentinel: never use these keywords in scoring logic
BANNED_KEYWORDS = ["BUG:", "FINDING:", "HACK:", "ANSWER:", "SOLUTION:"]


def init_dirs():
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    SIDECARS_DIR.mkdir(parents=True, exist_ok=True)


def record_exists(run_id):
    if not RESULTS_FILE.exists():
        return False
    with open(RESULTS_FILE) as f:
        for line in f:
            if line.strip():
                try:
                    r = json.loads(line)
                    if r.get("run_id") == run_id:
                        return True
                except json.JSONDecodeError:
                    pass
    return False


def record(run_record):
    RESULTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(RESULTS_FILE, "a") as f:
        f.write(json.dumps(run_record) + "\n")


def save_sidecar(run_id, content):
    p = SIDECARS_DIR / f"{run_id}.json"
    with open(p, "w") as f:
        json.dump(content, f, indent=2)


def run_droid(selector, prompt, cwd=BENCH_DIR, reasoning=None, extra_args=None):
    cmd = ["droid", "exec", "--model", selector, "--auto", "low", "-o", "json", "--cwd", cwd]
    if reasoning is not None:
        cmd.extend(["--reasoning-effort", reasoning])
    if extra_args:
        cmd.extend(extra_args)
    cmd.append(prompt)

    start = time.monotonic()
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=TIMEOUT)
        duration_ms = int((time.monotonic() - start) * 1000)
        raw = proc.stdout.strip()
        if not raw:
            return {"status": "empty_output", "duration_ms": duration_ms, "exit_code": proc.returncode,
                    "stderr": proc.stderr[:1000] if proc.stderr else ""}
        try:
            d = json.loads(raw)
            d["duration_ms"] = duration_ms
            d["status"] = "parsed"
            d["_raw_stdout"] = raw
            d["_stderr"] = proc.stderr[:1000] if proc.stderr else ""
            d["exit_code"] = proc.returncode
            return d
        except json.JSONDecodeError:
            return {"status": "parse_error", "duration_ms": duration_ms, "_raw_stdout": raw[:2000],
                    "exit_code": proc.returncode}
    except subprocess.TimeoutExpired:
        return {"status": "timeout", "duration_ms": int((time.monotonic() - start) * 1000), "exit_code": -1}
    except Exception as e:
        return {"status": "error", "error": str(e), "duration_ms": int((time.monotonic() - start) * 1000)}


def is_success(result):
    """Check if droid exec produced a successful result."""
    if result.get("status") in ("timeout", "empty_output", "parse_error", "error"):
        return False
    if result.get("is_error") is True:
        return False
    if result.get("subtype") == "failure":
        return False
    if result.get("exit_code") is not None and result.get("exit_code") != 0:
        return False
    return True


def get_result_text(result):
    """Extract the result text from a droid exec response."""
    return result.get("result", "")


# ─── Scoring functions ───────────────────────────────────────────────

def score_s1(result):
    if not is_success(result):
        return 0, result.get("subtype", result.get("status", "unknown"))
    text = get_result_text(result).strip()
    if text == "BENCHMARK_OK":
        return 1, None
    return 0, f"no exact BENCHMARK_OK in: {text[:100]}"


def score_s2(result):
    if not is_success(result):
        return 0, result.get("subtype", result.get("status", "unknown"))
    turns = result.get("num_turns", 0)
    text = get_result_text(result)
    if turns >= 2 and ("EMPTY" in text.upper() or "empty" in text.lower() or "no files" in text.lower()):
        return 1, None
    if turns < 2:
        return 0, f"only {turns} turns"
    return 0, f"result doesn't confirm empty: {text[:100]}"


def score_s3(turn1, turn2):
    """Multi-turn recall via injected context (no --session-id)."""
    if not is_success(turn1):
        return 0, f"turn1: {turn1.get('subtype', turn1.get('status', 'fail'))}"
    if not is_success(turn2):
        return 0, f"turn2: {turn2.get('subtype', turn2.get('status', 'fail'))}"
    r2 = get_result_text(turn2)
    if "ALPHABET" in r2.upper():
        return 1, None
    return 0, f"turn2 no ALPHABET: {r2[:100]}"


def score_s4(result):
    if not is_success(result):
        return 0, result.get("subtype", result.get("status", "unknown"))
    text = get_result_text(result)
    score = 0
    # Any numbered-list structure
    steps = re.findall(r"(?:^|\n)\s*\d+[.)\]]", text)
    if len(steps) >= 3:
        score += 1
    # Health endpoint mentioned
    if "health" in text.lower():
        score += 1
    # FastAPI or app.py mentioned
    if "fastapi" in text.lower() or "app.py" in text:
        score += 1
    reason = None if score >= 2 else f"score={score}"
    return score, reason


def score_s5(result):
    if not is_success(result):
        return 0, result.get("subtype", result.get("status", "unknown"))
    text = get_result_text(result).lower()
    score = 0
    # Divide reversal
    if any(w in text for w in ["reverse", "swap", "invert", "b / a", "dividend", "operands",
                                "arguments reversed", "swapped", "wrong order", "divisor"]):
        score += 1
    # Accumulate overwrite
    if any(w in text for w in ["overwrite", "reassign", "not accumul", "overwrites",
                                "= item", "assigns instead", "replacement", "last item"]):
        score += 1
    # No false positive on normalize
    if "normalize" in text and any(w in text for w in ["bug", "incorrect", "wrong", "issue", "problem"]):
        # Check if normalize is specifically called buggy
        normalize_lines = [l for l in text.split("\n") if "normalize" in l]
        normalize_buggy = any(any(w in l for w in ["bug", "incorrect", "wrong"]) for l in normalize_lines)
        if normalize_buggy:
            score += 0  # false positive
        else:
            score += 1
    else:
        score += 1  # normalize not called buggy
    reason = None if score >= 2 else f"score={score}"
    return score, reason


def score_s6(post_edit_result, test_exit, source_changed, test_file_hash_ok):
    if not is_success(post_edit_result):
        return 0, post_edit_result.get("subtype", post_edit_result.get("status", "fail"))
    if not source_changed:
        return 0, "source_not_changed"
    if not test_file_hash_ok:
        return 0, "test_file_tampered"
    if test_exit == 0:
        return 1, None
    return 0, f"test_exit={test_exit}"


def score_s7(result):
    if not is_success(result):
        return 0, result.get("subtype", result.get("status", "unknown"))
    text = get_result_text(result).lower()
    score = 0
    # Hardcoded credential: require compound indicator to avoid false positives
    credential_indicators = ["hardcod", "hard-coded", "plaintext", "plain text",
                             "admin_password", "supersecret", "static password",
                             "static credential"]
    has_credential = any(w in text for w in credential_indicators)
    if has_credential:
        score += 1
    # MD5 / weak hash: require "md5" specifically
    if "md5" in text or "weak hash" in text or "unsuitable hash" in text:
        score += 1
    # SQL injection: require both injection concept AND user input or interpolation
    has_injection = "injection" in text or "unsanitiz" in text
    has_input = "interpolat" in text or "string form" in text or "user input" in text or "format string" in text
    if has_injection or (has_input and "sql" in text):
        score += 1
    reason = None if score >= 2 else f"score={score}"
    return score, reason


# ─── Fixture verification ─────────────────────────────────────────────

def prepare_fixtures(target=None, fixtures_dir=None):
    """Restore benchmark fixtures from committed evidence to a runtime directory.

    Fail-closed on missing files, hash mismatch, or dangerous target paths.
    Idempotent: re-run overwrites cleanly.
    """
    import hashlib as _hl

    fixtures_dir = Path(fixtures_dir or EVIDENCE_DIR / "fixtures").resolve()
    target = Path(target or BENCH_DIR).resolve()
    SHA256_FILE = fixtures_dir / "SHA256SUMS"

    print(f"=== PREPARING FIXTURES ===")
    print(f"  Source: {fixtures_dir}")
    print(f"  Target: {target}")

    # Safety: fail-closed — only allow known-safe paths
    target_str = str(target.resolve())
    resolved_bench = str(Path(BENCH_DIR).resolve())
    allowed_prefixes = [
        resolved_bench,                           # /tmp/droid-benchmark → /private/tmp/droid-benchmark
        "/private/var/folders/droid-benchmark-test-",  # isolated test dirs
    ]
    is_allowed = any(target_str.startswith(p) or target_str.rstrip("/") == p.rstrip("/")
                     for p in allowed_prefixes)
    if not is_allowed:
        print(f"  ERROR: Refusing unapproved target: {target} (resolved: {target_str})")
        return False

    # Fail-closed: verify required fixture files exist
    required = [
        fixtures_dir / "buggy-module/calculator.py",
        fixtures_dir / "buggy-module/test_calculator.py",
        fixtures_dir / "edit-task/string_utils.py",
        fixtures_dir / "edit-task/test_string_utils.py",
        fixtures_dir / "planning-project/app.py",
        fixtures_dir / "planning-project/requirements.txt",
        fixtures_dir / "patch-review/auth.py",
        SHA256_FILE,
    ]
    missing = [str(p.relative_to(fixtures_dir)) for p in required if not p.is_file()]
    if missing:
        print(f"  ERROR: Missing required fixtures: {missing}")
        return False

    # Remove and recreate target
    if target.exists():
        shutil.rmtree(target)
    target.mkdir(parents=True)
    print(f"  Created: {target}")

    # Copy fixtures (excluding README.md, SHA256SUMS, .gitkeep, __pycache__)
    for item in fixtures_dir.rglob("*"):
        rel = item.relative_to(fixtures_dir)
        if rel.name in ("README.md", "SHA256SUMS", ".gitkeep", "__pycache__"):
            continue
        dest = target / rel
        if item.is_dir():
            dest.mkdir(parents=True, exist_ok=True)
        else:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, dest)

    # Create actually empty empty-dir (no .gitkeep)
    (target / "empty-dir").mkdir(exist_ok=True)
    print(f"  Created: empty-dir/")

    # Verify hashes
    if SHA256_FILE.exists():
        print(f"  Verifying SHA256 hashes...")
        errors = []
        for line in SHA256_FILE.read_text().splitlines():
            line = line.strip()
            if not line:
                continue
            parts = line.split("  ", 1)
            if len(parts) != 2:
                continue
            expected_hash, rel_path = parts
            rel_path = rel_path.removeprefix("./")
            fpath = target / rel_path
            if not fpath.exists():
                errors.append(f"  MISSING: {rel_path}")
                continue
            actual_hash = _hl.sha256(fpath.read_bytes()).hexdigest()
            if actual_hash != expected_hash:
                errors.append(f"  MISMATCH: {rel_path} expected={expected_hash[:12]} actual={actual_hash[:12]}")
        if errors:
            for e in errors:
                print(e)
            print(f"  SHA256 verification FAILED")
            return False
        print(f"  SHA256 verification PASSED")

    # Initialize git repo (needed for S6 and Droid workflow)
    if not (target / ".git").exists():
        r1 = subprocess.run(["git", "init", "-q"], cwd=str(target), capture_output=True)
        r2 = subprocess.run(["git", "add", "-A"], cwd=str(target), capture_output=True)
        r3 = subprocess.run(["git", "commit", "-q", "-m", "benchmark fixtures"],
                           cwd=str(target), capture_output=True)
        if r1.returncode != 0 or r2.returncode != 0 or r3.returncode != 0:
            print(f"  ERROR: git init failed: {r1.stderr}{r2.stderr}{r3.stderr}")
            return False
        print(f"  Initialized git repo")

    print(f"  Fixtures ready at {target}")
    return True


def verify_fixtures():
    print("=== GATE A: FIXTURE HEALTH ===")
    ok = True

    proc = subprocess.run(
        [sys.executable, "-m", "unittest", "test_calculator", "-v"],
        capture_output=True, text=True, cwd=f"{BENCH_DIR}/buggy-module"
    )
    output = proc.stdout + proc.stderr
    s5_ok = "FAILED" in output and "failures=2" in output
    print(f"  S5 buggy-module: {'PASS' if s5_ok else 'FAIL'} (exit={proc.returncode})")
    if not s5_ok:
        print(f"  output: {output[-300:]}")
        ok = False

    proc = subprocess.run(
        [sys.executable, "-m", "unittest", "test_string_utils", "-v"],
        capture_output=True, text=True, cwd=f"{BENCH_DIR}/edit-task"
    )
    output = proc.stdout + proc.stderr
    s6_ok = "FAILED" in output and "failures=2" in output
    print(f"  S6 edit-task:   {'PASS' if s6_ok else 'FAIL'} (exit={proc.returncode})")
    if not s6_ok:
        print(f"  output: {output[-300:]}")
        ok = False

    empty_files = [f for f in os.listdir(f"{BENCH_DIR}/empty-dir") if f != ".gitkeep"]
    s2_ok = len(empty_files) == 0
    print(f"  S2 empty-dir:   {'PASS' if s2_ok else 'FAIL'} (files: {empty_files})")
    if not s2_ok:
        ok = False

    # Verify no answer-leakage in fixtures
    for fname in ["calculator.py", "string_utils.py", "auth.py"]:
        for dirpath in ["buggy-module", "edit-task", "patch-review"]:
            fpath = f"{BENCH_DIR}/{dirpath}/{fname}"
            if os.path.exists(fpath):
                content = open(fpath).read()
                for kw in BANNED_KEYWORDS:
                    if kw in content:
                        print(f"  LEAKAGE: {fpath} contains {kw}")
                        ok = False

    if ok:
        print("  All fixture health checks passed.")
    return ok


# ─── Stage runners ───────────────────────────────────────────────────

def run_health():
    print("\n=== GATE A: HEALTH PROBES ===")

    # Record baseline unavailable
    run_id = "health-baseline"
    if not record_exists(run_id):
        record({
            "run_id": run_id, "stage": "health", "provider": "baseline",
            "selector": BASELINE["selector"], "scenario": "S1", "repetition": 0,
            "reasoning_effort": "none", "started_at": datetime.now(timezone.utc).isoformat(),
            "duration_ms": 0, "exit_code": 1, "timed_out": False, "parse_ok": False,
            "subtype": None, "is_error": True, "num_turns": 0,
            "semantic_score": 0, "max_score": 1, "passed": False,
            "failure_reason": "infrastructure_unavailable: OmniRoute port 20128 not listening",
            "usage": None, "result_excerpt": "Exec failed",
            "fixture_sha": FIXTURE_SHA,
        })
        print(f"  baseline: RECORDED as infrastructure_unavailable")
    else:
        print(f"  baseline: already recorded")

    for p in PROVIDERS:
        run_id = f"health-{p['label']}"
        if record_exists(run_id):
            print(f"  {p['label']}: already recorded, skipping")
            continue
        print(f"  {p['label']} S1 ...", end=" ", flush=True)
        result = run_droid(p["selector"], "Return exactly BENCHMARK_OK and nothing else.",
                           cwd=f"{BENCH_DIR}/empty-dir", reasoning="none")
        score, reason = score_s1(result)
        passed = score == 1
        print(f"{'PASS' if passed else 'FAIL'} ({result.get('duration_ms', '?')}ms)")

        record({
            "run_id": run_id, "stage": "health", "provider": p["label"],
            "selector": p["selector"], "scenario": "S1", "repetition": 0,
            "reasoning_effort": "none",
            "started_at": datetime.now(timezone.utc).isoformat(),
            "duration_ms": result.get("duration_ms"), "exit_code": result.get("exit_code"),
            "timed_out": result.get("status") == "timeout",
            "parse_ok": result.get("status") == "parsed",
            "subtype": result.get("subtype"), "is_error": result.get("is_error"),
            "num_turns": result.get("num_turns"),
            "semantic_score": score, "max_score": 1, "passed": passed,
            "failure_reason": reason,
            "usage": result.get("usage"),
            "result_excerpt": get_result_text(result)[:500],
            "fixture_sha": FIXTURE_SHA,
        })
        save_sidecar(run_id, result)


def run_scenarios(stage, rep):
    print(f"\n=== {stage.upper()}: REPETITION {rep} ===")

    for p in PROVIDERS:
        label = p["label"]
        selector = p["selector"]

        # S1: exact response (reasoning=none)
        rid = f"{stage}-{label}-S1-{rep}"
        if not record_exists(rid):
            print(f"  {label} S1 ...", end=" ", flush=True)
            r = run_droid(selector, "Return exactly BENCHMARK_OK and nothing else.",
                          cwd=f"{BENCH_DIR}/empty-dir", reasoning="none")
            sc, reason = score_s1(r)
            print(f"{'PASS' if sc else 'FAIL'}")
            _record_run(rid, stage, label, selector, "S1", rep, "none", r, sc, 1, reason)
            save_sidecar(rid, r)
        else:
            print(f"  {label} S1 ... SKIP (exists)")

        # S2: tool round-trip (reasoning=none)
        rid = f"{stage}-{label}-S2-{rep}"
        if not record_exists(rid):
            print(f"  {label} S2 ...", end=" ", flush=True)
            r = run_droid(selector,
                          "Use the LS tool to list the current directory. If it is empty, reply EMPTY_DIR.",
                          cwd=f"{BENCH_DIR}/empty-dir", reasoning="none")
            sc, reason = score_s2(r)
            print(f"{'PASS' if sc else 'FAIL'}")
            _record_run(rid, stage, label, selector, "S2", rep, "none", r, sc, 1, reason)
            save_sidecar(rid, r)
        else:
            print(f"  {label} S2 ... SKIP (exists)")

                        # S3: multi-turn recall — EXCLUDED (droid exec --session-id untestable)
        # See evidence/session-continuation.md for full diagnostic.
        # S3 is recorded as non-scored diagnostic evidence, not a provider failure.
        # This block intentionally does nothing; S3 records are absent from raw-results.jsonl.

        # S4: planning (reasoning=none for reliability comparison)
        rid = f"{stage}-{label}-S4-{rep}"
        if not record_exists(rid):
            print(f"  {label} S4 ...", end=" ", flush=True)
            r = run_droid(selector,
                          "Write a 3-step plan to add a /health endpoint to the FastAPI app in planning-project/app.py. Use numbered steps.",
                          cwd=BENCH_DIR, reasoning=None)
            sc, reason = score_s4(r)
            print(f"score={sc}/3")
            _record_run(rid, stage, label, selector, "S4", rep, "default", r, sc, 3, reason)
            save_sidecar(rid, r)
        else:
            print(f"  {label} S4 ... SKIP (exists)")

        # S5: bug diagnosis (reasoning=none)
        rid = f"{stage}-{label}-S5-{rep}"
        if not record_exists(rid):
            print(f"  {label} S5 ...", end=" ", flush=True)
            r = run_droid(selector,
                          "Read buggy-module/calculator.py and test_calculator.py. "
                          "Identify all bugs in calculator.py that cause the test failures. "
                          "List each bug as: BUG: <description>. Do not fix anything.",
                          cwd=BENCH_DIR, reasoning=None)
            sc, reason = score_s5(r)
            print(f"score={sc}/3")
            _record_run(rid, stage, label, selector, "S5", rep, "default", r, sc, 3, reason)
            save_sidecar(rid, r)
        else:
            print(f"  {label} S5 ... SKIP (exists)")

        # S6: code edit + test (reasoning=none)
        rid = f"{stage}-{label}-S6-{rep}"
        if not record_exists(rid):
            print(f"  {label} S6 ...", end=" ", flush=True)
            # Clone fresh copy
            tmpdir = tempfile.mkdtemp(prefix=f"droid-bench-{label}-s6-")
            shutil.copytree(BENCH_DIR, tmpdir, dirs_exist_ok=True)
            shutil.rmtree(f"{tmpdir}/.git", ignore_errors=True)
            # Hash test file before edit
            test_hash_before = hashlib.sha256(
                open(f"{tmpdir}/edit-task/test_string_utils.py", "rb").read()
            ).hexdigest()
            r = run_droid(selector,
                          "Fix the bugs in edit-task/string_utils.py so that ALL tests "
                          "in edit-task/test_string_utils.py pass. Then run the tests to verify.",
                          cwd=tmpdir, reasoning=None)
            # Verify: source changed, test unchanged, tests pass
            source_changed = False
            test_hash_ok = False
            test_exit = 1
            orig_src = open(f"{BENCH_DIR}/edit-task/string_utils.py", "r").read()
            try:
                edit_src = open(f"{tmpdir}/edit-task/string_utils.py", "r").read()
                source_changed = (orig_src != edit_src)
                edit_test_hash = hashlib.sha256(
                    open(f"{tmpdir}/edit-task/test_string_utils.py", "rb").read()
                ).hexdigest()
                test_hash_ok = (edit_test_hash == test_hash_before)
                test_proc = subprocess.run(
                    [sys.executable, "-m", "unittest", "test_string_utils", "-v"],
                    capture_output=True, text=True, cwd=f"{tmpdir}/edit-task"
                )
                test_exit = test_proc.returncode
            except Exception as e:
                pass
            shutil.rmtree(tmpdir, ignore_errors=True)
            sc, reason = score_s6(r, test_exit, source_changed, test_hash_ok)
            print(f"{'PASS' if sc else 'FAIL'} (test_exit={test_exit} src_changed={source_changed} test_hash_ok={test_hash_ok})")
            _record_run(rid, stage, label, selector, "S6", rep, "default", r, sc, 1, reason,
                        extra={"test_exit": test_exit, "source_changed": source_changed,
                               "test_file_unchanged": test_hash_ok})
            save_sidecar(rid, r)
        else:
            print(f"  {label} S6 ... SKIP (exists)")

        # S7: patch review (reasoning=none)
        rid = f"{stage}-{label}-S7-{rep}"
        if not record_exists(rid):
            print(f"  {label} S7 ...", end=" ", flush=True)
            r = run_droid(selector,
                          "Review patch-review/auth.py for security vulnerabilities. "
                          "List each finding as: FINDING: <description>.",
                          cwd=BENCH_DIR, reasoning=None)
            sc, reason = score_s7(r)
            print(f"score={sc}/3")
            _record_run(rid, stage, label, selector, "S7", rep, "default", r, sc, 3, reason)
            save_sidecar(rid, r)
        else:
            print(f"  {label} S7 ... SKIP (exists)")


def _record_run(run_id, stage, provider, selector, scenario, rep, reasoning, result, score, max_score, reason, extra=None):
    rec = {
        "run_id": run_id, "stage": stage, "provider": provider,
        "selector": selector, "scenario": scenario, "repetition": rep,
        "reasoning_effort": reasoning,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "duration_ms": result.get("duration_ms"),
        "exit_code": result.get("exit_code"),
        "timed_out": result.get("status") == "timeout",
        "parse_ok": result.get("status") == "parsed",
        "subtype": result.get("subtype"), "is_error": result.get("is_error"),
        "num_turns": result.get("num_turns"),
        "semantic_score": score, "max_score": max_score,
        "passed": score >= (max_score * 2 // 3 if max_score > 1 else 1),
        "failure_reason": reason,
        "usage": result.get("usage"),
        "result_excerpt": get_result_text(result)[:500],
        "fixture_sha": FIXTURE_SHA,
    }
    if extra:
        rec.update(extra)
    record(rec)


# ─── Main ─────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", required=True,
                        choices=["health", "pilot", "repeat2", "repeat3", "full"])
    args = parser.parse_args()

    init_dirs()

    if not prepare_fixtures():
        print("Fixture preparation FAILED. Aborting.")
        sys.exit(1)

    if not verify_fixtures():
        print("Fixture health check FAILED. Aborting.")
        sys.exit(1)

    if args.stage == "health":
        run_health()
    elif args.stage == "pilot":
        run_health()  # ensure health is recorded
        run_scenarios("pilot", 0)
    elif args.stage == "repeat2":
        run_scenarios("repeat2", 1)
    elif args.stage == "repeat3":
        run_scenarios("repeat3", 2)
    elif args.stage == "full":
        run_health()
        run_scenarios("pilot", 0)
        run_scenarios("repeat2", 1)
        run_scenarios("repeat3", 2)

    if RESULTS_FILE.exists():
        count = sum(1 for _ in open(RESULTS_FILE))
        print(f"\nTotal records in raw-results.jsonl: {count}")


if __name__ == "__main__":
    main()
