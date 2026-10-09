#!/usr/bin/env python3
"""Development service port collision and quarantine detector.

Checks standard development ports (Ollama: 11434, AgentMemory API: 3111,
AgentMemory Engine: 49134, Docker Desktop) and records foreign or colliding
processes in a value-blind quarantine report.

Contract:
- Read-only inspection; NEVER terminates, kills, or restarts processes.
- Value-blind: reports PIDs, process names, and ports; zero credentials.
- Fails closed with exit code 1 if collisions or foreign processes are found.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

# Standard expected service definitions
PORT_REGISTRY: dict[int, dict[str, Any]] = {
    11434: {
        "service": "ollama",
        "description": "Ollama local LLM runner",
        "allowed_process_names": ["ollama", "ollama_llama_server"],
        "disallowed_process_keywords": ["docker", "python", "curl"],
    },
    3111: {
        "service": "agentmemory-api",
        "description": "AgentMemory REST API service",
        "allowed_process_names": ["node", "agentmemory"],
        "disallowed_process_keywords": ["python", "ruby", "nginx"],
    },
    49134: {
        "service": "agentmemory-engine",
        "description": "AgentMemory iii-engine primitive",
        "allowed_process_names": ["iii-engine", "iii", "node"],
        "disallowed_process_keywords": ["python", "docker", "postgres"],
    },
}


@dataclass
class ProcessDetail:
    pid: int
    name: str
    command_line: str
    is_foreign: bool
    quarantine_reason: str | None = None


@dataclass
class PortStatus:
    port: int
    service: str
    status: str  # 'AVAILABLE', 'ALIGNED', 'COLLISION', 'FOREIGN_PROCESS'
    listeners: list[ProcessDetail]
    quarantined: bool
    details: str


def sanitize_command_line(cmd: str) -> str:
    """Sanitize command line value-blind, stripping potential secrets."""
    # Redact common credential patterns (token=..., key=..., password=...)
    redacted = re.sub(r"(?i)(token|key|secret|password|bearer)=([^\s]+)", r"\1=[REDACTED]", cmd)
    return redacted[:150]


def get_process_info_for_pid(pid: int) -> tuple[str, str]:
    """Get process name and sanitized command line for a PID."""
    try:
        proc = subprocess.run(
            ["ps", "-p", str(pid), "-o", "comm=,args="],
            capture_output=True,
            text=True,
            timeout=3.0,
        )
        if proc.returncode == 0 and proc.stdout.strip():
            lines = proc.stdout.strip().split(None, 1)
            pname = os.path.basename(lines[0])
            pargs = lines[1] if len(lines) > 1 else lines[0]
            return pname, sanitize_command_line(pargs)
    except Exception:
        pass
    return f"pid_{pid}", f"pid_{pid}"


def inspect_port_lsof(port: int) -> list[int]:
    """Use lsof to identify listening PIDs for a TCP port."""
    try:
        proc = subprocess.run(
            ["lsof", "-n", "-P", f"-iTCP:{port}", "-sTCP:LISTEN", "-t"],
            capture_output=True,
            text=True,
            timeout=3.0,
        )
        if proc.returncode == 0 and proc.stdout.strip():
            pids = []
            for line in proc.stdout.strip().splitlines():
                line = line.strip()
                if line.isdigit():
                    pids.append(int(line))
            return sorted(list(set(pids)))
    except Exception:
        pass
    return []


def check_docker_status() -> dict[str, Any]:
    """Check Docker Desktop socket availability and health value-blind."""
    home = Path(os.environ.get("HOME", str(Path.home())))
    sock_candidates = [
        home / ".docker" / "run" / "docker.sock",
        Path("/var/run/docker.sock"),
    ]

    found_sock = None
    for cand in sock_candidates:
        if cand.exists():
            found_sock = str(cand)
            break

    is_responsive = False
    details = "Docker socket not found"
    if found_sock:
        # Check if docker daemon responds
        try:
            proc = subprocess.run(
                ["docker", "info", "--format", "{{.ServerVersion}}"],
                capture_output=True,
                text=True,
                timeout=3.0,
            )
            if proc.returncode == 0:
                is_responsive = True
                details = f"Docker daemon active via {found_sock} (version: {proc.stdout.strip()[:20]})"
            else:
                details = f"Docker socket present at {found_sock} but daemon unresponsive"
        except Exception as e:
            details = f"Docker check error: {e}"

    return {
        "socket_path": found_sock,
        "active": is_responsive,
        "details": details,
    }


def inspect_service_ports(
    ports: list[int] | None = None,
    check_docker: bool = True,
    fixture_data: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Inspect specified ports and generate quarantine report."""
    target_ports = ports or list(PORT_REGISTRY.keys())
    port_results: dict[int, PortStatus] = {}
    quarantined_count = 0
    collisions_count = 0

    for port in target_ports:
        reg = PORT_REGISTRY.get(port, {
            "service": f"port-{port}",
            "allowed_process_names": [],
            "disallowed_process_keywords": [],
        })
        service_name = reg["service"]
        allowed_names = reg.get("allowed_process_names", [])

        # Check for simulated fixture or live system
        listeners: list[ProcessDetail] = []
        if fixture_data and "ports" in fixture_data and str(port) in fixture_data["ports"]:
            pdata_list = fixture_data["ports"][str(port)]
            for item in pdata_list:
                pname = item.get("name", "unknown")
                pcmd = item.get("command_line", pname)
                pid = item.get("pid", 0)
                is_allowed = any(an.lower() in pname.lower() or an.lower() in pcmd.lower() for an in allowed_names) if allowed_names else True
                is_foreign = item.get("is_foreign", not is_allowed)
                q_reason = item.get("quarantine_reason")
                if is_foreign and not q_reason:
                    q_reason = f"Process '{pname}' does not match allowed service '{service_name}' ({', '.join(allowed_names)})"
                listeners.append(ProcessDetail(
                    pid=pid,
                    name=pname,
                    command_line=sanitize_command_line(pcmd),
                    is_foreign=is_foreign,
                    quarantine_reason=q_reason if is_foreign else None,
                ))
        else:
            pids = inspect_port_lsof(port)
            for pid in pids:
                pname, pcmd = get_process_info_for_pid(pid)
                is_allowed = any(an.lower() in pname.lower() or an.lower() in pcmd.lower() for an in allowed_names) if allowed_names else True
                is_foreign = not is_allowed
                q_reason = None
                if is_foreign:
                    q_reason = f"Process '{pname}' (PID {pid}) is not expected for service '{service_name}'"
                listeners.append(ProcessDetail(
                    pid=pid,
                    name=pname,
                    command_line=pcmd,
                    is_foreign=is_foreign,
                    quarantine_reason=q_reason,
                ))

        if not listeners:
            port_results[port] = PortStatus(
                port=port,
                service=service_name,
                status="AVAILABLE",
                listeners=[],
                quarantined=False,
                details=f"Port {port} is free and available",
            )
        elif len(listeners) > 1:
            # Multiple listeners indicates collision
            collisions_count += 1
            quarantined_count += len(listeners)
            port_results[port] = PortStatus(
                port=port,
                service=service_name,
                status="COLLISION",
                listeners=listeners,
                quarantined=True,
                details=f"Multiple listeners detected on port {port}: {len(listeners)} processes competing",
            )
        elif listeners[0].is_foreign:
            quarantined_count += 1
            port_results[port] = PortStatus(
                port=port,
                service=service_name,
                status="FOREIGN_PROCESS",
                listeners=listeners,
                quarantined=True,
                details=listeners[0].quarantine_reason or f"Foreign process '{listeners[0].name}' occupying port {port}",
            )
        else:
            port_results[port] = PortStatus(
                port=port,
                service=service_name,
                status="ALIGNED",
                listeners=listeners,
                quarantined=False,
                details=f"Port {port} cleanly bound to expected service '{service_name}' (PID {listeners[0].pid})",
            )

    docker_info = check_docker_status() if check_docker else None

    has_quarantine = quarantined_count > 0 or collisions_count > 0
    return {
        "status": "PASS" if not has_quarantine else "COLLISION_QUARANTINED",
        "has_quarantine": has_quarantine,
        "quarantined_processes_count": quarantined_count,
        "collisions_count": collisions_count,
        "ports": {str(k): asdict(v) for k, v in port_results.items()},
        "docker": docker_info,
        "policy": "Read-only quarantine report. Verification NEVER terminates foreign processes.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Development service port collision detector")
    parser.add_argument("--ports", type=str, default="", help="Comma-separated list of ports to inspect")
    parser.add_argument("--no-docker", action="store_true", help="Skip Docker socket health check")
    parser.add_argument("--fixture", type=Path, default=None, help="Path to JSON test fixture simulating listeners")
    parser.add_argument("--json", action="store_true", help="Output quarantine report as JSON")

    args = parser.parse_args()

    ports_list = [int(p.strip()) for p in args.ports.split(",") if p.strip().isdigit()] if args.ports else None

    fixture_data = None
    if args.fixture and args.fixture.is_file():
        with open(args.fixture, "r", encoding="utf-8") as f:
            fixture_data = json.load(f)

    report = inspect_service_ports(
        ports=ports_list,
        check_docker=not args.no_docker,
        fixture_data=fixture_data,
    )

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print("=== Development Service Port Quarantine Report ===")
        print(f"Overall Status: {report['status']}")
        print(f"Quarantined Processes: {report['quarantined_processes_count']}")
        print(f"Collisions: {report['collisions_count']}")
        print("-" * 60)
        for port_str, pinfo in report["ports"].items():
            sym = "PASS" if not pinfo["quarantined"] else "QUARANTINED"
            print(f"  [{sym:<11}] Port {port_str:<5} ({pinfo['service']}): {pinfo['details']}")
            for l in pinfo["listeners"]:
                q_tag = " [FOREIGN/QUARANTINE]" if l["is_foreign"] else " [ALIGNED]"
                print(f"      -> PID {l['pid']}: {l['name']}{q_tag}")
        if report.get("docker"):
            d = report["docker"]
            print("-" * 60)
            print(f"  [DOCKER] {d['details']}")

    return 0 if not report["has_quarantine"] else 1


if __name__ == "__main__":
    sys.exit(main())
