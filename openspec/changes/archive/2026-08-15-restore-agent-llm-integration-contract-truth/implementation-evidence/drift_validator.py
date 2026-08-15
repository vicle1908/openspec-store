#!/usr/bin/env python3
"""Read-only identity/dirt validator for restore-agent-llm integration evidence."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

EXPECTED = {
    "openspec-store": ("/Users/androidteam/Developer/.worktrees/restore-agent-llm-openspec-store", "7791792bc58a01168d5b2150ed499478742d5963", "openspec/restore-agent-llm-openspec-store"),
    "tdt-core": ("/Users/androidteam/Developer/.worktrees/restore-agent-llm-tdt-core", "a5cee90f20af0a20f7a1d2499884f713c1a29b2d", "openspec/restore-agent-llm-tdt-core"),
    "agent-core": ("/Users/androidteam/Developer/.worktrees/restore-agent-llm-agent-core", "3742e858f77a629f8fb119f2388d36f4f6201041", "openspec/restore-agent-llm-agent-core"),
    "agent-harness": ("/Users/androidteam/Developer/.worktrees/restore-agent-llm-agent-harness", "70d0da2fbdfa15c1382cec6a09468dfc7e86e7c1", "openspec/restore-agent-llm-agent-harness"),
    "agent-docs-sync": ("/Users/androidteam/Developer/.worktrees/restore-agent-llm-agent-docs-sync", "a189c50452015a06d4f63fc342fa22e7e31e34ad", "openspec/restore-agent-llm-agent-docs-sync"),
    "ai-harness-skills": ("/Users/androidteam/Developer/.worktrees/restore-agent-llm-ai-harness-skills", "fb21b093f0207bd40f4fd0d7d9cffdce682b0089", "openspec/restore-agent-llm-ai-harness-skills"),
    "ai-review": ("/Users/androidteam/Developer/.worktrees/restore-agent-llm-ai-review", "e71ce742cdb88b2a2c8c621eaed1c34f67f4a6ab", "openspec/restore-agent-llm-ai-review"),
}


def git(path: str, *args: str) -> str:
    return subprocess.check_output(["git", "-C", path, *args], text=True).strip()


def main() -> int:
    records = {}
    failures = []
    for name, (path, expected_sha, expected_branch) in EXPECTED.items():
        p = Path(path)
        record: dict[str, object] = {"path": path, "expected_sha": expected_sha, "expected_branch": expected_branch}
        if not p.is_dir():
            record["status"] = "FAIL"
            failures.append(f"{name}: missing worktree")
            records[name] = record
            continue
        actual_sha = git(path, "rev-parse", "HEAD")
        actual_branch = git(path, "branch", "--show-current")
        dirt = git(path, "status", "--short")
        record.update({"actual_sha": actual_sha, "actual_branch": actual_branch, "dirt": dirt, "clean": not dirt})
        if actual_sha != expected_sha:
            failures.append(f"{name}: SHA drift")
        if actual_branch != expected_branch:
            failures.append(f"{name}: branch drift")
        if dirt:
            failures.append(f"{name}: product dirt")
        record["status"] = "PASS" if actual_sha == expected_sha and actual_branch == expected_branch and not dirt else "FAIL"
        records[name] = record
    result = {"validator": "restore-agent-llm-final-drift", "status": "PASS" if not failures else "FAIL", "failures": failures, "records": records}
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if len(sys.argv) > 1:
        Path(sys.argv[1]).write_text(text, encoding="utf-8")
    print(text, end="")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
