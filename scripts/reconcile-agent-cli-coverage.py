#!/usr/bin/env python3
"""Reconcile workstation agent CLI coverage declarations against installed binaries.

Standard library only. Read-only by contract: never executes update verbs or removes tools.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass
class AgentCLIRecord:
    name: str
    binary_path: str
    status: str  # 'covered', 'uncovered_declared', 'undeclared'
    source_type: str  # 'package_manager', 'ecosystem_manager', 'vendor_download'
    source_detail: str
    update_verb: str | None


def classify_source(binary_path: str) -> tuple[str, str]:
    resolved = str(Path(binary_path).resolve())
    if "/Cellar/" in resolved or "/Caskroom/" in resolved:
        return "package_manager", "Homebrew (formula/cask)"
    elif "/.npm-global/" in resolved or "/node_modules/" in resolved or "/home-toolchain/" in resolved:
        return "ecosystem_manager", "npm"
    elif "/.local/share/claude/" in resolved or "/.grok/downloads/" in resolved or "/.hermes/" in resolved:
        return "vendor_download", "vendor release channel"
    elif "/Applications/" in resolved:
        return "package_manager", "macOS Application bundle"
    return "vendor_download", "standalone binary"


def reconcile_agent_clis(declared_covered: dict[str, str], declared_uncovered: list[str]) -> list[AgentCLIRecord]:
    known_agents = [
        "claude",
        "codex",
        "opencode",
        "kilo",
        "auggie",
        "qoder",
        "pi",
        "prime-agent",
        "grok",
        "goose",
        "droid",
        "happy",
        "cursor-agent",
        "hermes-agent",
        "buzz",
        "cce",
    ]

    records: list[AgentCLIRecord] = []

    for name in sorted(known_agents):
        bin_path = shutil.which(name)
        if not bin_path:
            continue

        src_type, src_detail = classify_source(bin_path)

        if name in declared_covered:
            status = "covered"
            verb = declared_covered[name]
        elif name in declared_uncovered:
            status = "uncovered_declared"
            verb = None
        else:
            status = "undeclared"
            verb = None

        records.append(
            AgentCLIRecord(
                name=name,
                binary_path=bin_path,
                status=status,
                source_type=src_type,
                source_detail=src_detail,
                update_verb=verb,
            )
        )

    return records


def main() -> int:
    parser = argparse.ArgumentParser(description="Reconcile agent CLI coverage.")
    parser.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    parser.add_argument("--include-uncovered", default="droid,goose,grok,prime-agent,happy,cursor-agent,hermes-agent,buzz,cce", help="Comma-separated declared uncovered CLIs")
    parser.add_argument("--simulate-initial", action="store_true", help="Simulate initial state where happy, cursor-agent, hermes-agent, buzz, cce are undeclared")
    args = parser.parse_args()

    covered = {
        "claude": "claude update",
        "codex": "codex update",
        "opencode": "opencode upgrade",
        "kilo": "kilo update",
        "auggie": "auggie update --skip-confirmation",
        "qoder": "qoder update",
        "pi": "pi update --self",
    }

    if args.simulate_initial:
        uncovered = ["droid", "goose", "grok", "prime-agent"]
    else:
        uncovered = [x.strip() for x in args.include_uncovered.split(",") if x.strip()]

    records = reconcile_agent_clis(covered, uncovered)
    undeclared = [r for r in records if r.status == "undeclared"]

    if args.json:
        out = {
            "declared_covered": covered,
            "declared_uncovered": uncovered,
            "total_installed": len(records),
            "undeclared_count": len(undeclared),
            "records": [asdict(r) for r in records],
        }
        print(json.dumps(out, indent=2))
    else:
        print("=== Workstation Agent CLI Coverage Reconciliation ===")
        print(f"  Total Installed Agents: {len(records)}")
        print(f"  Declared Covered:       {len(covered)} ({', '.join(sorted(covered.keys()))})")
        print(f"  Declared Uncovered:     {len(uncovered)} ({', '.join(sorted(uncovered))})")
        print(f"  Undeclared Count:       {len(undeclared)}")
        print("\nInstalled Agent Roster:")
        for r in records:
            tag = f"[{r.status.upper()}]"
            verb = f" (verb: '{r.update_verb}')" if r.update_verb else ""
            print(f"  {r.name:15} -> {r.binary_path} {tag} ({r.source_type}: {r.source_detail}){verb}")
        if undeclared:
            print("\nUndeclared Installations Detected:")
            for u in undeclared:
                print(f"  - {u.name} ({u.binary_path})")

    return 1 if undeclared else 0


if __name__ == "__main__":
    sys.exit(main())
