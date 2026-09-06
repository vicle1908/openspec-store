#!/usr/bin/env python3
"""Metadata-only preservation verification (task 4.2 reproducibility).

Content reads SHALL be limited to files already materialized; this script performs
none at all (metadata-only) and records dataless files as present-but-content-unverified.
"""
import json
import os
import time

EVIDENCE = "/Users/androidteam/Developer/openspec-store/openspec/changes/cleanup-icloud-project-artifacts/evidence"
MS = "/Users/androidteam/Library/Mobile Documents/com~apple~CloudDocs/project/microservices"
VD = "/Users/androidteam/Library/Mobile Documents/com~apple~CloudDocs/project/vds"

probes = {
    "source": [
        MS + "/services/inventory-service/build.gradle.kts",
        MS + "/common-events/build.gradle.kts",
        MS + "/services/orders-service/src",
        MS + "/buildSrc",
        MS + "/gradle",
        MS + "/.env",
        MS + "/.github/workflows/pinning-check.yml",
    ],
    "manifest": [MS + "/build.gradle.kts", MS + "/settings.gradle.kts"],
    "lockfile": [VD + "/bun.lock", MS + "/gradle/wrapper/gradle-wrapper.properties"],
    "docs": [VD + "/design-artifacts", VD + "/AGENTS.md", VD + "/CLAUDE.md", MS + "/CHANGELOG.md"],
}

results = []
for cat, paths in probes.items():
    for p in paths:
        try:
            st = os.lstat(p)
            dl = bool(st.st_flags & 0x40000000)
            results.append({
                "category": cat, "path": p, "present": True, "dataless": dl,
                "note": "present-but-content-unverified" if dl else "materialized",
            })
        except OSError as e:
            results.append({"category": cat, "path": p, "present": False, "error": e.strerror})

report = {
    "capturedAt": time.strftime("%Y-%m-%dT%H:%M:%S"),
    "method": "metadata-only lstat; no content reads",
    "probes": results,
    "missingCount": sum(1 for r in results if not r["present"]),
    "datalessCount": sum(1 for r in results if r.get("dataless")),
}
json.dump(report, open(f"{EVIDENCE}/preservation-verification.json", "w"), indent=2)
print("probes:", len(results), "missing:", report["missingCount"], "dataless:", report["datalessCount"])
