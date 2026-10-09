#!/usr/bin/env python3
"""AgentMemory health probe and engine alignment verifier.

Queries HTTP GET http://localhost:3111/agentmemory/health (avoiding root /)
and inspects installed package metadata to resolve the pinned iii-engine version.
Quarantines foreign or incompatible processes on ports 3111 and 49134 without
terminating any processes or mutating SQLite.

Contract:
- Queries /agentmemory/health, NEVER root /.
- Resolves pinned iii-engine (0.22.1 for agentmemory 0.9.30).
- Reports foreign processes on ports 3111 and 49134 in quarantine audit.
- Standard library only. Never executes un-gated process kills or writes SQLite.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

DEFAULT_HEALTH_URL = "http://localhost:3111/agentmemory/health"
DEFAULT_PINNED_ENGINE = "0.22.1"
DEFAULT_EXPECTED_PACKAGE = "0.9.30"


@dataclass
class EngineAlignment:
    installed_package_version: str | None
    pinned_engine_version: str | None
    reported_engine_version: str | None
    is_aligned: bool
    details: str


@dataclass
class QuarantineAuditEntry:
    port: int
    pid: int
    process_name: str
    command_line: str
    quarantined: bool
    reason: str


@dataclass
class AgentMemoryHealthReport:
    status: str  # 'HEALTHY', 'MISALIGNED', 'UNHEALTHY', 'QUARANTINED'
    endpoint_url: str
    http_status: int | None
    response_body: Any
    alignment: EngineAlignment
    quarantine: list[QuarantineAuditEntry]
    details: str


def sanitize_cmd(cmd: str) -> str:
    """Strip credential patterns value-blind."""
    return re.sub(r"(?i)(token|key|secret|password|bearer)=([^\s]+)", r"\1=[REDACTED]", cmd)[:120]


def find_agentmemory_package_json(custom_path: Path | None = None) -> Path | None:
    """Locate agentmemory package.json from custom path or standard npm locations."""
    if custom_path and custom_path.is_file():
        return custom_path

    home = Path(os.environ.get("HOME", str(Path.home())))
    candidates = [
        home / ".npm-global" / "lib" / "node_modules" / "@agentmemory" / "agentmemory" / "package.json",
        home / ".npm-global" / "lib" / "node_modules" / "agentmemory" / "package.json",
        Path("/opt/homebrew/lib/node_modules/@agentmemory/agentmemory/package.json"),
        Path("/usr/local/lib/node_modules/@agentmemory/agentmemory/package.json"),
    ]
    for c in candidates:
        if c.is_file():
            return c
    return None


def read_package_engine_pin(pkg_path: Path | None) -> tuple[str | None, str | None]:
    """Extract package version and pinned iii-engine version from package.json."""
    if not pkg_path or not pkg_path.is_file():
        return None, None

    try:
        with open(pkg_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        pkg_version = data.get("version")
        deps = data.get("dependencies", {})
        engine_ver = deps.get("iii-sdk") or deps.get("@iii-dev/helpers")
        if engine_ver:
            # Strip ^ or ~ prefix
            engine_ver = engine_ver.lstrip("^~")
        return pkg_version, engine_ver
    except Exception:
        return None, None


def inspect_pids_for_port(port: int) -> list[tuple[int, str, str]]:
    """Inspect listening processes for a port via lsof."""
    results: list[tuple[int, str, str]] = []
    try:
        proc = subprocess.run(
            ["lsof", "-n", "-P", f"-iTCP:{port}", "-sTCP:LISTEN", "-t"],
            capture_output=True,
            text=True,
            timeout=3.0,
        )
        if proc.returncode == 0 and proc.stdout.strip():
            for line in proc.stdout.strip().splitlines():
                if line.strip().isdigit():
                    pid = int(line.strip())
                    pname = f"pid_{pid}"
                    pcmd = ""
                    try:
                        p_info = subprocess.run(
                            ["ps", "-p", str(pid), "-o", "comm=,args="],
                            capture_output=True,
                            text=True,
                            timeout=2.0,
                        )
                        if p_info.returncode == 0 and p_info.stdout.strip():
                            parts = p_info.stdout.strip().split(None, 1)
                            pname = os.path.basename(parts[0])
                            pcmd = parts[1] if len(parts) > 1 else parts[0]
                    except Exception:
                        pass
                    results.append((pid, pname, sanitize_cmd(pcmd)))
    except Exception:
        pass
    return results


def check_health_and_alignment(
    url: str = DEFAULT_HEALTH_URL,
    package_json_path: Path | None = None,
    expected_engine: str = DEFAULT_PINNED_ENGINE,
    mock_http_response: tuple[int, Any] | None = None,
    mock_processes: dict[int, list[dict[str, Any]]] | None = None,
    timeout: float = 5.0,
) -> AgentMemoryHealthReport:
    """Evaluate AgentMemory health probe, engine pin alignment, and process quarantine."""
    # Strict validation: root / is strictly forbidden
    parsed_path = urllib.parse.urlparse(url).path
    if parsed_path in ("", "/"):
        raise ValueError("Root '/' endpoint is forbidden; health probe MUST target '/agentmemory/health'")

    # 1. Package metadata resolution
    resolved_pkg_path = find_agentmemory_package_json(package_json_path)
    pkg_ver, declared_engine = read_package_engine_pin(resolved_pkg_path)
    pinned_engine = declared_engine or expected_engine

    # 2. HTTP GET /agentmemory/health
    http_status = None
    response_data = None
    http_error_msg = None

    if mock_http_response is not None:
        http_status, response_data = mock_http_response
    else:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "AgentMemory-HealthProbe/1.0", "Accept": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                http_status = resp.status
                raw = resp.read().decode("utf-8", errors="ignore")
                try:
                    response_data = json.loads(raw)
                except Exception:
                    response_data = {"raw": raw}
        except urllib.error.HTTPError as e:
            http_status = e.code
            http_error_msg = f"HTTP {e.code}: {e.reason}"
        except urllib.error.URLError as e:
            http_status = None
            http_error_msg = f"Connection failed: {e.reason}"
        except Exception as e:
            http_status = None
            http_error_msg = str(e)

    # Extract reported engine version from response if present
    reported_engine = None
    if isinstance(response_data, dict):
        reported_engine = response_data.get("engine_version") or response_data.get("engine") or response_data.get("iii_engine")

    # 3. Process quarantine inspection for ports 3111 and 49134
    quarantine_entries: list[QuarantineAuditEntry] = []

    for port in (3111, 49134):
        p_list = []
        if mock_processes is not None and port in mock_processes:
            p_list = [(p["pid"], p["name"], p.get("command_line", p["name"])) for p in mock_processes[port]]
        else:
            p_list = inspect_pids_for_port(port)

        for pid, pname, pcmd in p_list:
            is_foreign = False
            reason = ""
            if port == 3111:
                # API port expects agentmemory / node / iii
                if not any(k in pname.lower() or k in pcmd.lower() for k in ("agentmemory", "node", "iii")):
                    is_foreign = True
                    reason = f"Unexpected process '{pname}' occupying API port 3111"
            elif port == 49134:
                # Engine port expects iii-engine or node; legacy versions must be quarantined
                if "legacy" in pname.lower() or "legacy" in pcmd.lower() or not any(k in pname.lower() or k in pcmd.lower() for k in ("iii-engine", "node")):
                    is_foreign = True
                    reason = f"Unexpected or legacy process '{pname}' occupying engine port 49134"

            if is_foreign:
                quarantine_entries.append(QuarantineAuditEntry(
                    port=port,
                    pid=pid,
                    process_name=pname,
                    command_line=pcmd,
                    quarantined=True,
                    reason=reason,
                ))

    # 4. Synthesize status
    # Check engine alignment
    engine_aligned = True
    align_details = "Engine generation aligns with pinned version"
    if reported_engine and pinned_engine and reported_engine != pinned_engine:
        engine_aligned = False
        align_details = f"Reported engine '{reported_engine}' diverges from pinned '{pinned_engine}'"
    elif not pinned_engine:
        engine_aligned = False
        align_details = "Pinned engine version could not be resolved from package metadata"

    alignment = EngineAlignment(
        installed_package_version=pkg_ver,
        pinned_engine_version=pinned_engine,
        reported_engine_version=reported_engine,
        is_aligned=engine_aligned,
        details=align_details,
    )

    if quarantine_entries:
        overall_status = "QUARANTINED"
        summary_details = f"{len(quarantine_entries)} conflicting process(es) quarantined on ports 3111/49134"
    elif http_status == 200 and engine_aligned:
        overall_status = "HEALTHY"
        summary_details = "AgentMemory API is healthy and engine is aligned"
    elif http_status == 200 and not engine_aligned:
        overall_status = "MISALIGNED"
        summary_details = f"AgentMemory responded 200 but engine generation misaligned: {align_details}"
    else:
        overall_status = "UNHEALTHY"
        summary_details = http_error_msg or f"Endpoint returned HTTP {http_status}"

    return AgentMemoryHealthReport(
        status=overall_status,
        endpoint_url=url,
        http_status=http_status,
        response_body=response_data,
        alignment=alignment,
        quarantine=quarantine_entries,
        details=summary_details,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="AgentMemory health probe and engine alignment verifier")
    parser.add_argument("--url", default=DEFAULT_HEALTH_URL, help="Health endpoint URL (must not be root /)")
    parser.add_argument("--package-json", type=Path, default=None, help="Path to agentmemory package.json")
    parser.add_argument("--pinned-engine", default=DEFAULT_PINNED_ENGINE, help="Expected pinned iii-engine version")
    parser.add_argument("--timeout", type=float, default=5.0, help="HTTP timeout in seconds")
    parser.add_argument("--json", action="store_true", help="Output report as JSON")

    args = parser.parse_args()

    try:
        report = check_health_and_alignment(
            url=args.url,
            package_json_path=args.package_json,
            expected_engine=args.pinned_engine,
            timeout=args.timeout,
        )
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2

    if args.json:
        data = asdict(report)
        print(json.dumps(data, indent=2))
    else:
        print("=== AgentMemory Health Probe ===")
        print(f"Status:       {report.status}")
        print(f"Endpoint:     {report.endpoint_url} (HTTP {report.http_status})")
        print(f"Package:      version={report.alignment.installed_package_version}, pinned_engine={report.alignment.pinned_engine_version}")
        print(f"Details:      {report.details}")
        if report.quarantine:
            print("\nQuarantine Audit:")
            for q in report.quarantine:
                print(f"  [QUARANTINED] Port {q.port} PID {q.pid} ({q.process_name}): {q.reason}")

    return 0 if report.status == "HEALTHY" else 1


if __name__ == "__main__":
    sys.exit(main())
