#!/usr/bin/env python3
"""Workstation bootstrap preflight checker.

Detects macOS architecture, Homebrew prefix, user home, and development prerequisites
without hardcoding machine-local paths. Standard library only.
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass
class PrerequisiteCheck:
    name: str
    status: str  # "PASS" or "FAIL"
    details: str
    required: bool = True
    path: str | None = None


@dataclass
class PreflightReport:
    status: str  # "PASS" or "FAIL"
    system: dict[str, str]
    prerequisites: dict[str, dict[str, Any]]
    failed_checks: list[str]


def detect_system_info(
    arch_override: str | None = None,
    home_override: str | None = None,
    brew_prefix_override: str | None = None,
    workspace_root_override: str | None = None,
    store_root_override: str | None = None,
    os_override: str | None = None,
) -> dict[str, str]:
    """Derive system paths and architecture dynamically."""
    os_name = os_override or os.environ.get("WORKSTATION_OS") or platform.system()
    arch = arch_override or os.environ.get("WORKSTATION_ARCH") or platform.machine()

    # Normalize architecture
    if arch in ("arm64", "aarch64"):
        norm_arch = "arm64"
    elif arch in ("x86_64", "amd64"):
        norm_arch = "x86_64"
    else:
        norm_arch = arch

    home = home_override or os.environ.get("WORKSTATION_HOME") or os.environ.get("HOME") or str(Path.home())

    # Homebrew prefix logic:
    # 1. Explicit override or environment variable
    # 2. On arm64 -> /opt/homebrew
    # 3. On x86_64 -> /usr/local
    if brew_prefix_override:
        brew_prefix = brew_prefix_override
    elif arch_override:
        brew_prefix = "/opt/homebrew" if norm_arch == "arm64" else "/usr/local"
    elif os.environ.get("HOMEBREW_PREFIX"):
        brew_prefix = os.environ["HOMEBREW_PREFIX"]
    elif norm_arch == "arm64":
        brew_prefix = "/opt/homebrew"
    else:
        brew_prefix = "/usr/local"

    workspace_root = workspace_root_override or os.environ.get("WORKSPACE_ROOT") or str(Path(home) / "Developer")
    store_root = store_root_override or os.environ.get("OPENSPEC_STORE_ROOT") or str(Path(workspace_root) / "platform" / "openspec-store")

    return {
        "os": os_name,
        "arch": norm_arch,
        "home": home,
        "homebrew_prefix": brew_prefix,
        "workspace_root": workspace_root,
        "openspec_store_root": store_root,
    }


def check_prerequisites(
    sys_info: dict[str, str],
    mock_missing: set[str] | None = None,
) -> tuple[dict[str, PrerequisiteCheck], list[str]]:
    """Verify presence of core development prerequisites."""
    mock = mock_missing or set()
    checks: dict[str, PrerequisiteCheck] = {}
    failed: list[str] = []

    # 1. OS check
    if "os" in mock or sys_info["os"] != "Darwin":
        checks["os_darwin"] = PrerequisiteCheck(
            name="os_darwin",
            status="FAIL",
            details=f"Unsupported OS: '{sys_info['os']}'. Only macOS (Darwin) is supported.",
        )
        failed.append("os_darwin")
    else:
        checks["os_darwin"] = PrerequisiteCheck(
            name="os_darwin",
            status="PASS",
            details="macOS (Darwin) confirmed",
        )

    # 2. Architecture check
    if "arch" in mock or sys_info["arch"] not in ("arm64", "x86_64"):
        checks["arch_supported"] = PrerequisiteCheck(
            name="arch_supported",
            status="FAIL",
            details=f"Unsupported architecture: '{sys_info['arch']}'. Supported: arm64, x86_64.",
        )
        failed.append("arch_supported")
    else:
        arch_label = "Apple Silicon" if sys_info["arch"] == "arm64" else "Intel"
        checks["arch_supported"] = PrerequisiteCheck(
            name="arch_supported",
            status="PASS",
            details=f"{sys_info['arch']} ({arch_label}) confirmed",
        )

    # 3. Xcode Command Line Tools
    if "xcode" in mock:
        checks["xcode_cli_tools"] = PrerequisiteCheck(
            name="xcode_cli_tools",
            status="FAIL",
            details="Xcode Command Line Tools not detected (simulated missing)",
        )
        failed.append("xcode_cli_tools")
    else:
        xcode_path = None
        try:
            res = subprocess.run(["xcode-select", "-p"], capture_output=True, text=True, timeout=5)
            if res.returncode == 0 and res.stdout.strip():
                xcode_path = res.stdout.strip()
        except Exception:
            pass

        if not xcode_path:
            # Fallback check standard locations
            for candidate in ("/Library/Developer/CommandLineTools", "/Applications/Xcode.app/Contents/Developer"):
                if Path(candidate).is_dir():
                    xcode_path = candidate
                    break

        if xcode_path and Path(xcode_path).is_dir():
            checks["xcode_cli_tools"] = PrerequisiteCheck(
                name="xcode_cli_tools",
                status="PASS",
                details=f"Installed at {xcode_path}",
                path=xcode_path,
            )
        else:
            checks["xcode_cli_tools"] = PrerequisiteCheck(
                name="xcode_cli_tools",
                status="FAIL",
                details="Xcode Command Line Tools not found. Run 'xcode-select --install'.",
            )
            failed.append("xcode_cli_tools")

    # 4. Homebrew executable
    if "brew" in mock:
        checks["homebrew"] = PrerequisiteCheck(
            name="homebrew",
            status="FAIL",
            details="Homebrew not found (simulated missing)",
        )
        failed.append("homebrew")
    else:
        brew_bin = Path(sys_info["homebrew_prefix"]) / "bin" / "brew"
        resolved_brew = str(brew_bin) if brew_bin.exists() else shutil.which("brew")
        if resolved_brew and Path(resolved_brew).exists():
            checks["homebrew"] = PrerequisiteCheck(
                name="homebrew",
                status="PASS",
                details=f"Homebrew installed at {resolved_brew}",
                path=resolved_brew,
            )
        else:
            checks["homebrew"] = PrerequisiteCheck(
                name="homebrew",
                status="FAIL",
                details=f"Homebrew executable not found at {brew_bin} or in PATH",
            )
            failed.append("homebrew")

    # 5. Python 3
    if "python3" in mock:
        checks["python3"] = PrerequisiteCheck(
            name="python3",
            status="FAIL",
            details="Python 3 not found (simulated missing)",
        )
        failed.append("python3")
    else:
        py_bin = shutil.which("python3")
        if py_bin:
            version_str = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
            checks["python3"] = PrerequisiteCheck(
                name="python3",
                status="PASS",
                details=f"Python {version_str} at {py_bin}",
                path=py_bin,
            )
        else:
            checks["python3"] = PrerequisiteCheck(
                name="python3",
                status="FAIL",
                details="python3 binary not found in PATH",
            )
            failed.append("python3")

    # 6. Git
    if "git" in mock:
        checks["git"] = PrerequisiteCheck(
            name="git",
            status="FAIL",
            details="Git not found (simulated missing)",
        )
        failed.append("git")
    else:
        git_bin = shutil.which("git")
        if git_bin:
            checks["git"] = PrerequisiteCheck(
                name="git",
                status="PASS",
                details=f"Git installed at {git_bin}",
                path=git_bin,
            )
        else:
            checks["git"] = PrerequisiteCheck(
                name="git",
                status="FAIL",
                details="git binary not found in PATH",
            )
            failed.append("git")

    return checks, failed


def run_preflight(
    arch_override: str | None = None,
    home_override: str | None = None,
    brew_prefix_override: str | None = None,
    workspace_root_override: str | None = None,
    store_root_override: str | None = None,
    os_override: str | None = None,
    mock_missing: set[str] | None = None,
    fixture_path: str | None = None,
) -> PreflightReport:
    """Run full preflight evaluation, supporting fixtures or live detection."""
    if fixture_path:
        with open(fixture_path, encoding="utf-8") as f:
            fixture = json.load(f)
        sys_info = fixture.get("system", {})
        # If fixture defines mock_missing or overrides
        f_mock = set(fixture.get("mock_missing", []))
        if mock_missing:
            f_mock.update(mock_missing)
        checks, failed = check_prerequisites(sys_info, f_mock)
    else:
        sys_info = detect_system_info(
            arch_override=arch_override,
            home_override=home_override,
            brew_prefix_override=brew_prefix_override,
            workspace_root_override=workspace_root_override,
            store_root_override=store_root_override,
            os_override=os_override,
        )
        checks, failed = check_prerequisites(sys_info, mock_missing)

    status = "FAIL" if failed else "PASS"
    prereqs_dict = {k: asdict(v) for k, v in checks.items()}
    return PreflightReport(
        status=status,
        system=sys_info,
        prerequisites=prereqs_dict,
        failed_checks=failed,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Workstation bootstrap preflight checker.")
    parser.add_argument("--json", action="store_true", help="Output JSON report")
    parser.add_argument("--arch", help="Override detected architecture (arm64, x86_64)")
    parser.add_argument("--home", help="Override user home directory")
    parser.add_argument("--homebrew-prefix", help="Override Homebrew prefix")
    parser.add_argument("--workspace-root", help="Override workspace root")
    parser.add_argument("--openspec-store-root", help="Override openspec store root")
    parser.add_argument("--os", help="Override OS name (Darwin, Linux, etc.)")
    parser.add_argument("--mock-missing", help="Comma-separated missing prerequisites to simulate")
    parser.add_argument("--fixture", help="Path to synthetic preflight test fixture JSON")

    args = parser.parse_args()

    mock_set = set(filter(None, args.mock_missing.split(","))) if args.mock_missing else None

    report = run_preflight(
        arch_override=args.arch,
        home_override=args.home,
        brew_prefix_override=args.homebrew_prefix,
        workspace_root_override=args.workspace_root,
        store_root_override=args.openspec_store_root,
        os_override=args.os,
        mock_missing=mock_set,
        fixture_path=args.fixture,
    )

    if args.json:
        print(json.dumps(asdict(report), indent=2))
    else:
        print("=== Workstation Bootstrap Preflight ===")
        print(f"Status:             {report.status}")
        print(f"OS:                 {report.system.get('os')}")
        print(f"Architecture:       {report.system.get('arch')}")
        print(f"User Home:          {report.system.get('home')}")
        print(f"Homebrew Prefix:    {report.system.get('homebrew_prefix')}")
        print(f"Workspace Root:     {report.system.get('workspace_root')}")
        print(f"OpenSpec Store:     {report.system.get('openspec_store_root')}")
        print("\nPrerequisites:")
        for name, item in report.prerequisites.items():
            status_tag = f"[{item['status']}]"
            print(f"  {status_tag:8} {name:20} -> {item['details']}")
        if report.failed_checks:
            print("\nFAILED CHECKS:")
            for f in report.failed_checks:
                print(f"  - {f}")

    return 0 if report.status == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
