#!/usr/bin/env python3
"""Measure Git-backed snapshot store growth, evaluate against ceilings, and report repack actions.

Standard library only. Read-only by contract: never executes repack or deletion.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


def parse_size_bytes(size_str: str) -> int:
    """Parse human readable size string like '9.67 GiB', '17.41 MiB', '1G' into bytes."""
    s = size_str.strip()
    match = re.match(r"^([\d.]+)\s*([A-Za-z]+)?$", s)
    if not match:
        return 0
    val = float(match.group(1))
    unit = (match.group(2) or "").upper()
    multiplier = 1
    if unit in ("K", "KB", "KIB"):
        multiplier = 1024
    elif unit in ("M", "MB", "MIB"):
        multiplier = 1024**2
    elif unit in ("G", "GB", "GIB"):
        multiplier = 1024**3
    elif unit in ("T", "TB", "TIB"):
        multiplier = 1024**4
    return int(val * multiplier)


def format_bytes(n: int) -> str:
    """Format bytes into human-readable string."""
    if n < 1024:
        return f"{n} B"
    for unit in ("KiB", "MiB", "GiB", "TiB"):
        n /= 1024
        if n < 1024:
            return f"{n:.2f} {unit}"
    return f"{n:.2f} PiB"


@dataclass
class SnapshotMeasurement:
    store_path: str
    resolved_path: str
    declared_ceiling: str
    ceiling_bytes: int
    total_bytes: int
    total_size_human: str
    loose_bytes: int
    loose_size_human: str
    packed_bytes: int
    packed_size_human: str
    loose_object_count: int
    packed_object_count: int
    commit_count: int
    oldest_commit_date: str
    newest_commit_date: str
    status: str  # 'within_bounds' or 'exceeded'
    reclaimable_by_repack: bool
    estimated_reclaimable_bytes: int
    estimated_reclaimable_human: str
    owner_repack_command: str
    prohibited_actions: list[str]


def measure_store(store_path_str: str, ceiling_str: str, owner_cmd: str) -> SnapshotMeasurement:
    resolved = Path(os.path.expanduser(store_path_str)).resolve()
    if not resolved.is_dir() or not (resolved / ".git").is_dir():
        raise FileNotFoundError(f"Snapshot store not found or not a git repository: {resolved}")

    # Run git count-objects -vH
    res = subprocess.run(
        ["git", "-C", str(resolved), "count-objects", "-vH"],
        capture_output=True,
        text=True,
        check=True,
    )
    raw_kv = {}
    for line in res.stdout.splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            raw_kv[k.strip()] = v.strip()

    loose_count = int(raw_kv.get("count", 0))
    loose_str = raw_kv.get("size", "0")
    loose_bytes = parse_size_bytes(loose_str)

    packed_count = int(raw_kv.get("in-pack", 0))
    packed_str = raw_kv.get("size-pack", "0")
    packed_bytes = parse_size_bytes(packed_str)

    total_bytes = loose_bytes + packed_bytes
    ceiling_bytes = parse_size_bytes(ceiling_str)

    # Commits count & dates
    log_res = subprocess.run(
        ["git", "-C", str(resolved), "log", "--format=%cd", "--date=short"],
        capture_output=True,
        text=True,
        check=True,
    )
    commit_dates = [line.strip() for line in log_res.stdout.splitlines() if line.strip()]
    commit_count = len(commit_dates)
    newest_date = commit_dates[0] if commit_dates else "unknown"
    oldest_date = commit_dates[-1] if commit_dates else "unknown"

    status = "exceeded" if total_bytes > ceiling_bytes else "within_bounds"
    reclaimable = loose_bytes > (packed_bytes * 2) or (total_bytes > ceiling_bytes and loose_bytes > packed_bytes)
    est_reclaim = max(0, loose_bytes - (packed_bytes // 2))

    return SnapshotMeasurement(
        store_path=store_path_str,
        resolved_path=str(resolved),
        declared_ceiling=ceiling_str,
        ceiling_bytes=ceiling_bytes,
        total_bytes=total_bytes,
        total_size_human=format_bytes(total_bytes),
        loose_bytes=loose_bytes,
        loose_size_human=format_bytes(loose_bytes),
        packed_bytes=packed_bytes,
        packed_size_human=format_bytes(packed_bytes),
        loose_object_count=loose_count,
        packed_object_count=packed_count,
        commit_count=commit_count,
        oldest_commit_date=oldest_date,
        newest_commit_date=newest_date,
        status=status,
        reclaimable_by_repack=reclaimable,
        estimated_reclaimable_bytes=est_reclaim,
        estimated_reclaimable_human=format_bytes(est_reclaim),
        owner_repack_command=owner_cmd,
        prohibited_actions=[
            "rm -rf .git/objects",
            "Direct deletion of loose Git objects",
            "Filesystem unlink of snapshot revisions without Git gc/repack",
        ],
    )


def load_config(config_path: Path) -> list[tuple[str, str, str]]:
    entries = []
    if not config_path.is_file():
        return [("~/.agentmemory/snapshots", "1G", "git -C ~/.agentmemory/snapshots repack -a -d -f --depth=250 --window=250")]
    for line in config_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split("	")
        if len(parts) >= 3:
            entries.append((parts[0].strip(), parts[1].strip(), parts[2].strip()))
    return entries


def main() -> int:
    parser = argparse.ArgumentParser(description="Measure Git snapshot store growth and bounds.")
    parser.add_argument("--config", default="config/snapshot-store-bounds.tsv", help="Path to bounds TSV config")
    parser.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    parser.add_argument("--strict", action="store_true", help="Exit non-zero if any store exceeds ceiling")
    args = parser.parse_args()

    config_path = Path(args.config)
    if not config_path.is_absolute():
        repo_root = Path(__file__).resolve().parents[1]
        config_path = repo_root / config_path

    entries = load_config(config_path)
    measurements = []
    any_exceeded = False

    for store_path, ceiling, owner_cmd in entries:
        try:
            m = measure_store(store_path, ceiling, owner_cmd)
            measurements.append(m)
            if m.status == "exceeded":
                any_exceeded = True
        except Exception as e:
            sys.stderr.write(f"Error measuring {store_path}: {e}\n")
            return 1

    if args.json:
        print(json.dumps([asdict(m) for m in measurements], indent=2))
    else:
        for m in measurements:
            print(f"Snapshot Store: {m.store_path} ({m.resolved_path})")
            print(f"  Status: {m.status.upper()} (Ceiling: {m.declared_ceiling}, Total: {m.total_size_human})")
            print(f"  Split: Loose={m.loose_size_human} ({m.loose_object_count} objects) vs Packed={m.packed_size_human} ({m.packed_object_count} objects in 1 pack)")
            print(f"  History: {m.commit_count} commits (Oldest: {m.oldest_commit_date}, Newest: {m.newest_commit_date})")
            if m.reclaimable_by_repack:
                print(f"  Reclaimable by Repack: YES (~{m.estimated_reclaimable_human})")
                print(f"  Owner Repack Command: {m.owner_repack_command}")
                print("  Prohibited: " + ", ".join(m.prohibited_actions))

    if args.strict and any_exceeded:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
