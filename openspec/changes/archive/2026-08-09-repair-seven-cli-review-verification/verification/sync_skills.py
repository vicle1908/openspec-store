#!/usr/bin/env python3
"""Synchronize repair-owned canonical skill snapshots into ~/.hermes/skills."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / ".hermes" / "skills").is_dir() and (
            candidate / "openspec"
        ).is_dir():
            return candidate
    raise RuntimeError("unable to locate repository root containing .hermes/skills")


REPO_ROOT = find_repo_root(ROOT)
SOURCE = REPO_ROOT / ".hermes" / "skills"
MANIFEST = ROOT / "canonical-source-manifest.json"
EVIDENCE = ROOT / "sync-evidence"
INSTALL_ROOT = Path.home() / ".hermes" / "skills"
BACKUP_BASE = (
    Path.home()
    / ".hermes"
    / "skill-backups"
    / "repair-seven-cli-review-verification"
)
ALLOWED_PREFIXES = ("autonomous-ai-agents/", "software-development/")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", dir=path.parent, delete=False
    ) as handle:
        handle.write(content)
        temporary = Path(handle.name)
    os.replace(temporary, path)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="install tracked snapshots; default is check-only")
    args = parser.parse_args()

    manifest = json.loads(MANIFEST.read_text())
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup_root = BACKUP_BASE / stamp
    records = []

    for item in manifest["files"]:
        rel = item["relative_path"]
        if not rel.startswith(ALLOWED_PREFIXES) or ".." in Path(rel).parts:
            raise SystemExit(f"refusing unexpected path: {rel}")
        source = SOURCE / rel
        installed = INSTALL_ROOT / rel
        before = digest(installed) if installed.exists() else None
        source_hash = digest(source)
        if args.apply and before != source_hash:
            backup = backup_root / rel
            if installed.exists():
                backup.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(installed, backup)
            installed.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, installed)
        after = digest(installed) if installed.exists() else None
        records.append({
            "relative_path": rel,
            "source_sha256": source_hash,
            "installed_before_sha256": before,
            "installed_after_sha256": after,
            "matched_after": source_hash == after,
            "applied": bool(args.apply and before != source_hash),
        })

    EVIDENCE.mkdir(parents=True, exist_ok=True)
    report = {
        "generated_utc": (
            datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            if args.apply
            else None
        ),
        "mode": "apply" if args.apply else "check",
        "source_root": ".hermes/skills",
        "install_root": "~/.hermes/skills",
        "backup_root": (
            str(backup_root).replace(str(Path.home()), "~", 1)
            if args.apply
            else None
        ),
        "records": records,
    }
    report_path = EVIDENCE / f"latest-{'apply' if args.apply else 'check'}.json"
    atomic_write(report_path, json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    return 0 if all(record["matched_after"] for record in records) else 1


if __name__ == "__main__":
    raise SystemExit(main())
