#!/opt/homebrew/bin/python3
"""Run sentinel extraction negative/positive fixtures."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("runner", ROOT / "cli-probe-runner.py")
if spec is None or spec.loader is None:
    raise SystemExit("unable to load runner")
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)
fixture = json.loads((ROOT / "sentinel-fixtures.json").read_text())
failures = []
for case in fixture["cases"]:
    actual = runner.exact_sentinel(fixture["expected"], case["output"])
    if actual is not case["expected"]:
        failures.append((case["name"], actual, case["expected"]))
if failures:
    for failure in failures:
        print("FAIL", failure)
    raise SystemExit(1)
print(f"SUMMARY PASS sentinel_cases={len(fixture['cases'])}")
