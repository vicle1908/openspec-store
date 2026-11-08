#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.15"
# dependencies = []
# ///
"""Workstation toolchain native smoke check suite.

Runs tool-specific pre- and post-mutation native smoke checks (<tool> --version,
<tool> help, or verification_smoke_command from manifest). Standard library only.
Read-only: never mutates any files on disk.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

# Default path to workstation manifest
DEFAULT_MANIFEST_PATH = Path(__file__).resolve().parent.parent / "config" / "workstation-toolchain-manifest.json"

ERROR_PATTERN = re.compile(r"(?im)^\s*(error|fatal)[: ]|failed to [a-z]")
ANSI_ESCAPE_PATTERN = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")


def strip_ansi(text: str) -> str:
    """Remove ANSI escape sequences from command output."""
    return ANSI_ESCAPE_PATTERN.sub("", text)


@dataclass
class ToolSmokeResult:
    tool: str
    status: str  # 'PASS', 'FAIL', 'SKIPPED'
    command: str
    stage: str  # 'pre', 'post'
    exit_code: int | None
    output: str
    version_readback: str | None = None
    duration_ms: float = 0.0
    error: str | None = None
    already_target: bool = False


def extract_version_readback(output: str) -> str | None:
    """Extract a concise version readback string from command output."""
    clean = strip_ansi(output).strip()
    if not clean:
        return None
    for line in clean.splitlines():
        line = line.strip()
        if line and not ERROR_PATTERN.search(line):
            return line
    return None


def resolve_command_template(cmd_tmpl: str, home: str | None = None, brew_prefix: str | None = None) -> str:
    """Replace {{HOME}} and {{HOMEBREW_PREFIX}} placeholders in verification commands."""
    h = home or os.environ.get("HOME", str(Path.home()))
    bp = brew_prefix or ("/opt/homebrew" if os.uname().machine == "arm64" else "/usr/local")
    return cmd_tmpl.replace("{{HOME}}", h).replace("{{HOMEBREW_PREFIX}}", bp)


def execute_smoke_command(
    command: str,
    timeout: float = 15.0,
    env: dict[str, str] | None = None,
) -> tuple[int, str, str, float]:
    """Execute smoke command safely without modifying files."""
    start_time = time.perf_counter()
    run_env = os.environ.copy()
    if env:
        run_env.update(env)

    try:
        proc = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=run_env,
        )
        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
        out = strip_ansi(proc.stdout + ("\n" + proc.stderr if proc.stderr else "")).strip()
        return proc.returncode, out, "", duration_ms
    except subprocess.TimeoutExpired:
        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
        return 124, "", f"Command timed out after {timeout}s", duration_ms
    except Exception as e:
        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
        return 1, "", str(e), duration_ms


def run_tool_smoke_check(
    tool_name: str,
    tool_cfg: dict[str, Any] | None = None,
    stage: str = "pre",
    target_version: str | None = None,
    timeout: float = 15.0,
    runner: Any = None,
) -> ToolSmokeResult:
    """Execute smoke test for an individual tool.

    If runner is provided, uses runner(command, timeout) -> (returncode, output, error, duration_ms).
    """
    cmd = None
    if tool_cfg and isinstance(tool_cfg, dict):
        cmd = tool_cfg.get("verification_smoke_command")
    if not cmd:
        cmd = f"{tool_name} --version"

    resolved_cmd = resolve_command_template(cmd)
    if runner is not None:
        rc, out, err_msg, dur_ms = runner(resolved_cmd, timeout)
    else:
        if tool_cfg and isinstance(tool_cfg, dict) and tool_cfg.get("category") == "rust":
            active_pat = tool_cfg.get("active_path_pattern", "")
            resolved_bin = resolve_command_template(active_pat) if active_pat else ""
            if (not resolved_bin or not Path(resolved_bin).exists()) and not shutil.which(tool_name):
                return ToolSmokeResult(
                    tool=tool_name,
                    status="SKIPPED",
                    command=resolved_cmd,
                    stage=stage,
                    exit_code=0,
                    output="optional rust-dev profile not installed",
                    version_readback="not installed (optional profile)",
                    duration_ms=0.0,
                    error=None,
                    already_target=False,
                )
        rc, out, err_msg, dur_ms = execute_smoke_command(resolved_cmd, timeout=timeout)
    readback = extract_version_readback(out)

    # Evaluate pass/fail conditions
    is_pass = True
    error_reason: str | None = None
    already_target = False

    if rc != 0:
        is_pass = False
        error_reason = err_msg or f"Command failed with exit code {rc}"
    elif ERROR_PATTERN.search(out):
        # Spec requirement: Command failure with exit zero detected
        is_pass = False
        error_reason = "Command exited with status code 0 but reported error output"
    elif not readback:
        is_pass = False
        error_reason = "Smoke check succeeded but produced empty version readback"

    if is_pass and target_version:
        # Check target version alignment
        if readback and target_version in readback:
            already_target = True

    return ToolSmokeResult(
        tool=tool_name,
        status="PASS" if is_pass else "FAIL",
        command=resolved_cmd,
        stage=stage,
        exit_code=rc,
        output=out,
        version_readback=readback,
        duration_ms=dur_ms,
        error=error_reason,
        already_target=already_target,
    )


def load_manifest(manifest_path: Path) -> dict[str, Any]:
    """Load tools from manifest JSON."""
    if not manifest_path.is_file():
        return {}
    with open(manifest_path, encoding="utf-8") as f:
        return json.load(f)


def run_suite(
    manifest_path: Path = DEFAULT_MANIFEST_PATH,
    tools: list[str] | None = None,
    stage: str = "pre",
    target_version: str | None = None,
    timeout: float = 15.0,
    runner: Any = None,
) -> dict[str, Any]:
    """Run smoke checks across selected or all declared tools."""
    manifest_data = load_manifest(manifest_path)
    declared_tools: dict[str, Any] = manifest_data.get("tools", {})

    target_tools = tools or list(declared_tools.keys())
    results: dict[str, ToolSmokeResult] = {}

    for tool_name in target_tools:
        cfg = declared_tools.get(tool_name, {})
        res = run_tool_smoke_check(
            tool_name=tool_name,
            tool_cfg=cfg,
            stage=stage,
            target_version=target_version,
            timeout=timeout,
            runner=runner,
        )
        results[tool_name] = res

    failed_count = sum(1 for r in results.values() if r.status == "FAIL")
    passed_count = sum(1 for r in results.values() if r.status in ("PASS", "SKIPPED"))
    all_passed = failed_count == 0

    return {
        "status": "PASS" if all_passed else "FAIL",
        "stage": stage,
        "total": len(results),
        "passed": passed_count,
        "failed": failed_count,
        "results": {k: asdict(v) for k, v in results.items()},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Toolchain native smoke check suite")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST_PATH, help="Path to manifest JSON")
    parser.add_argument("--tools", type=str, default="", help="Comma-separated list of tools to test")
    parser.add_argument("--stage", choices=["pre", "post"], default="pre", help="Stage of mutation check")
    parser.add_argument("--target-version", type=str, default=None, help="Expected version string")
    parser.add_argument("--timeout", type=float, default=15.0, help="Per-tool timeout in seconds")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")

    args = parser.parse_args()

    tools_list = [t.strip() for t in args.tools.split(",") if t.strip()] if args.tools else None
    suite_result = run_suite(
        manifest_path=args.manifest,
        tools=tools_list,
        stage=args.stage,
        target_version=args.target_version,
        timeout=args.timeout,
    )

    if args.json:
        print(json.dumps(suite_result, indent=2))
    else:
        print(f"=== Toolchain Smoke Test Suite [{args.stage.upper()}] ===")
        print(f"Overall Status: {suite_result['status']} ({suite_result['passed']}/{suite_result['total']} passed)")
        print("-" * 60)
        for name, r in suite_result["results"].items():
            sym = "PASS" if r["status"] == "PASS" else ("SKIP" if r["status"] == "SKIPPED" else "FAIL")
            rb = f" [{r['version_readback']}]" if r["version_readback"] else ""
            err = f" - {r['error']}" if r["error"] else ""
            print(f"  [{sym}] {name:<15} ({r['duration_ms']}ms){rb}{err}")

    return 0 if suite_result["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
