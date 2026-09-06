#!/usr/bin/env python3
"""Metadata-only inode recount for project trees (task 4.1 reproducibility)."""
import json
import os
import time

EVIDENCE = "/Users/androidteam/Developer/openspec-store/openspec/changes/cleanup-icloud-project-artifacts/evidence"
BASE = json.load(open(f"{EVIDENCE}/baseline-inode-counts.json"))


def count_all(path):
    n = 0
    stack = [path]
    while stack:
        cur = stack.pop()
        try:
            with os.scandir(cur) as it:
                entries = list(it)
            n += len(entries)
            stack.extend(e.path for e in entries if e.is_dir(follow_symlinks=False))
        except OSError:
            pass
    return n


ms = count_all("/Users/androidteam/Library/Mobile Documents/com~apple~CloudDocs/project/microservices")
vd = count_all("/Users/androidteam/Library/Mobile Documents/com~apple~CloudDocs/project/vds")
out = {
    "capturedAt": time.strftime("%Y-%m-%dT%H:%M:%S"),
    "baseline": BASE,
    "post": {"microservices": ms, "vds": vd},
    "removed": {
        "microservices": BASE["microservices"] - ms,
        "vds": BASE["vds"] - vd,
        "total": (BASE["microservices"] - ms) + (BASE["vds"] - vd),
    },
}
json.dump(out, open(f"{EVIDENCE}/post-cleanup-inode-counts.json", "w"), indent=2)
print(json.dumps(out["post"]), "removed:", out["removed"])
