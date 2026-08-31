#!/opt/homebrew/bin/python3
"""Validate the no-override default-probe contract without running probes."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MATRIX = ROOT / "evidence/default-probe-matrix.json"
INVENTORY = ROOT / "evidence/cli-inventory.json"
SECRET = re.compile(r"(?i)\b(?:sk|xai|pmv|agt)_[A-Za-z0-9_-]{8,}\b|\b(?:sk|xai)-[A-Za-z0-9_-]{12,}\b|\bBearer\s+[A-Za-z0-9._-]{12,}")
FORBIDDEN_OVERRIDE = {"--model", "-m", "--provider", "-P", "--profile"}


def main() -> int:
    matrix = json.loads(MATRIX.read_text())
    inventory = json.loads(INVENTORY.read_text())
    expected = {
        row["id"]: row
        for row in inventory.get("products", [])
        if row.get("classification") == "candidate"
    }
    rows = matrix.get("probes", [])
    failures: list[str] = []
    seen: set[str] = set()
    for row in rows:
        row_id = row.get("id")
        product = row.get("product")
        if not isinstance(row_id, str) or row_id in seen:
            failures.append(f"duplicate/missing id: {row_id!r}")
            continue
        seen.add(row_id)
        if product not in expected:
            failures.append(f"default probe product is not an installed candidate: {product!r}")
        argv = row.get("argv")
        if not isinstance(argv, list) or not argv or not all(isinstance(x, str) for x in argv):
            failures.append(f"invalid argv: {row_id}")
            continue
        if any(token in FORBIDDEN_OVERRIDE for token in argv):
            failures.append(f"provider/model override in default probe: {row_id}")
        if SECRET.search(" ".join(argv)):
            failures.append(f"credential-shaped argv: {row_id}")
        if row.get("working_directory") != "/tmp":
            failures.append(f"unsafe/default working directory: {row_id}")
        if not isinstance(row.get("expected"), str) or not row["expected"]:
            failures.append(f"missing expected sentinel: {row_id}")
        if not isinstance(row.get("acceptable_outcomes"), list) or not row["acceptable_outcomes"]:
            failures.append(f"missing acceptable outcomes: {row_id}")
        if not isinstance(row.get("timeout"), (int, float)) or row["timeout"] <= 0:
            failures.append(f"missing positive timeout: {row_id}")
    missing = sorted(set(expected) - {row.get("product") for row in rows})
    failures.extend(f"missing default probe: {product}" for product in missing)
    if failures:
        for failure in failures:
            print("FAIL", failure)
        print(f"SUMMARY FAIL findings={len(failures)}")
        return 1
    print(f"SUMMARY PASS default_probes={len(rows)} candidates={len(expected)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
