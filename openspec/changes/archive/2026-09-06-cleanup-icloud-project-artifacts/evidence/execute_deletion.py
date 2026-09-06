#!/usr/bin/env python3
"""Fail-closed, fault-tolerant, idempotent deletion executor for cleanup-icloud-project-artifacts.

Authorization: requires --approved <manifest-sha256> matching the sha256 of the
manifest being executed; refuses to delete anything without it (spec: unapproved
deletion attempt fails closed). The authorization is recorded in
evidence/approval-record.json.

Fault tolerance: per-target try/except — FileNotFoundError => already-done (skip);
other OSError => recorded failure; run continues through the whole manifest.
Deletes ONLY paths listed in the approved dry-run manifest. Writes a report JSON.

NOTE (provenance): the original 2026-09-06 run used the pre-gate version of this
script (sha256 6b26e4ea05268ef732f5ac343806a8ecf302658dd2855f61a201102f0b4c0b6d),
invoked once under explicit in-session user authorization documented in
evidence/approval-record.json. The fail-closed gate below was added during
/opsx:verify so that any re-run of this evidence script is gated; the executed
run itself never ran unapproved (see approval-record.json presentation/authorization).
"""
import hashlib
import json
import os
import shutil
import sys
from datetime import datetime

EVIDENCE = "/Users/androidteam/Developer/openspec-store/openspec/changes/cleanup-icloud-project-artifacts/evidence"
MANIFEST = f"{EVIDENCE}/dry-run-manifest.json"
REPORT = f"{EVIDENCE}/deletion-report.json"

# --- Fail-closed authorization gate (spec: Unapproved deletion attempt fails closed)
args = sys.argv[1:]
if "--approved" not in args or len(args) != 2:
    print("REFUSED: no deletion performed. This executor deletes iCloud Drive content.")
    print("Re-run with: execute_deletion.py --approved <sha256-of-dry-run-manifest.json>")
    print("Authorization record: evidence/approval-record.json")
    sys.exit(2)
given_hash = args[args.index("--approved") + 1]
manifest_bytes = open(MANIFEST, "rb").read()
actual_hash = hashlib.sha256(manifest_bytes).hexdigest()
if given_hash != actual_hash:
    print(f"REFUSED: manifest hash mismatch (given {given_hash}, manifest {actual_hash}).")
    print("The manifest changed since authorization — re-present it and obtain new approval.")
    sys.exit(2)

m = json.loads(manifest_bytes)

deleted_dirs = already_dirs = 0
deleted_files = already_files = 0
failures = []

# Directories first (nested child targets, if any, then resolve as already-done)
for d in m["directoryTargets"]:
    p = d["path"]
    try:
        shutil.rmtree(p, ignore_errors=False)
        deleted_dirs += 1
    except FileNotFoundError:
        already_dirs += 1  # idempotent re-run or nested-in-deleted-parent
    except OSError as e:
        failures.append({"path": p, "kind": "dir", "errno": e.errno, "error": e.strerror})
    # progress marker every 100 dirs
    if (deleted_dirs + already_dirs) % 100 == 0:
        print(f"dirs done={deleted_dirs + already_dirs}/{len(m['directoryTargets'])}", flush=True)

for f in m["fileTargets"]:
    p = f["path"]
    try:
        os.remove(p)
        deleted_files += 1
    except FileNotFoundError:
        already_files += 1
    except OSError as e:
        failures.append({"path": p, "kind": "file", "errno": e.errno, "error": e.strerror})

report = {
    "executedAt": datetime.now().isoformat(timespec="seconds"),
    "manifest": MANIFEST,
    "manifestSha256": actual_hash,
    "dirTargets": len(m["directoryTargets"]),
    "fileTargets": len(m["fileTargets"]),
    "dirsDeleted": deleted_dirs,
    "dirsAlreadyGone": already_dirs,
    "filesDeleted": deleted_files,
    "filesAlreadyGone": already_files,
    "failures": failures,
    "failureCount": len(failures),
}
with open(REPORT, "w") as fh:
    json.dump(report, fh, indent=2)

print(json.dumps({k: report[k] for k in (
    "dirsDeleted", "dirsAlreadyGone", "filesDeleted", "filesAlreadyGone", "failureCount")}, indent=2))
if failures:
    print("FAILURES (first 20):")
    for f in failures[:20]:
        print(f"  [{f['kind']}] errno={f['errno']} {f['error']}: {f['path']}")
sys.exit(0 if not failures else 1)
