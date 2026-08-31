#!/opt/homebrew/bin/python3
"""Validate the read-only CLI identity/classification inventory."""
from __future__ import annotations

import argparse
import json
import os
import shlex
import subprocess
import shutil
from pathlib import Path

ALLOWED = {"candidate", "unchanged", "blocked", "unconfigured", "alias", "separate-change-owned"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("inventory", type=Path)
    args = parser.parse_args()
    data = json.loads(args.inventory.read_text())
    products = data.get("products", [])
    failures = []
    seen = set()
    for product in products:
        ident = product.get("id")
        command = product.get("command")
        canonical = product.get("canonical")
        classification = product.get("classification")
        if not ident or not command or not canonical:
            failures.append(f"incomplete row:{ident}")
            continue
        if canonical in seen:
            failures.append(f"duplicate canonical executable:{canonical}")
        seen.add(canonical)
        if classification not in ALLOWED:
            failures.append(f"invalid classification:{ident}")
        resolved_proc = subprocess.run(
            ["zsh", "-lc", f"command -v {shlex.quote(command)}"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
        resolved = resolved_proc.stdout.strip().splitlines()[0] if resolved_proc.stdout.strip() else None
        if resolved is None:
            failures.append(f"command missing:{ident}")
            continue
        actual = os.path.realpath(resolved)
        expected = os.path.realpath(canonical)
        if actual != expected:
            failures.append(f"canonical drift:{ident}")
        print(f"IDENTITY {ident}: command={command} canonical_match={actual == expected} classification={classification}")
    alias_failures = []
    for name, paths in data.get("aliases", {}).items():
        resolved = {os.path.realpath(p) for p in paths}
        if len(resolved) > 1:
            alias_failures.append(name)
        print(f"ALIAS {name}: canonical_count={len(resolved)}")
    failures.extend(f"alias not deduplicated:{x}" for x in alias_failures)
    if failures:
        for failure in failures:
            print("FAIL", failure)
        print(f"SUMMARY FAIL findings={len(failures)}")
        return 1
    print(f"SUMMARY PASS products={len(products)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
