#!/usr/bin/env python3
"""Fresh-login smoke tests for provider launchers.

Usage:
  python .claude/scripts/provider_smoke.py
"""

import json
import re
import subprocess
import sys


def smoke(provider: str, sentinel: str, timeout: int = 120) -> bool:
    """Run fresh-login smoke for a provider launcher."""
    cmd = [
        "zsh", "-lic",
        f"{provider} --print --output-format json \"Return exactly {sentinel}\"",
    ]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=timeout,
    )

    # Strip iTerm2 OSC sequences
    clean = re.sub(r"\x1b\]1337;.*?\x07", "", result.stdout).strip()

    system_model = None
    result_text = None
    model_usage = None
    is_error = None

    try:
        items = json.loads(clean)
        if not isinstance(items, list):
            items = [items]
        for item in items:
            if item.get("type") == "system" and item.get("subtype") == "init":
                system_model = item.get("model")
            if item.get("type") == "result":
                result_text = item.get("result")
                is_error = item.get("is_error")
                model_usage = sorted((item.get("modelUsage") or {}).keys())
    except json.JSONDecodeError:
        result_text = clean[:200] if clean else "<empty>"

    ok = result.returncode == 0 and is_error is False and result_text is not None
    status = "PASS" if ok else "FAIL"

    print(f"\n{'='*50}")
    print(f"  {provider} — {status}")
    print(f"{'='*50}")
    print(f"  exit_code:    {result.returncode}")
    print(f"  system_model: {system_model}")
    print(f"  result:       {result_text!r}")
    print(f"  is_error:     {is_error}")
    print(f"  model_usage:  {model_usage}")

    return ok


def main() -> int:
    providers = [
        ("shopapikey", "SHOP_PROFILE_LIVE"),
        ("giaoduc", "GIAODUC_PROFILE_LIVE"),
        ("cockpit", "COCKPIT_PROFILE_LIVE"),
    ]

    results = [smoke(p, s) for p, s in providers]

    print(f"\n{'='*50}")
    print(f"  SUMMARY")
    print(f"{'='*50}")
    for (prov, _), ok in zip(providers, results):
        print(f"  {prov}: {'PASS' if ok else 'FAIL'}")

    if all(results):
        print("\n  ALL PASS")
        return 0
    else:
        print("\n  SOME FAILED — investigate")
        return 1


if __name__ == "__main__":
    sys.exit(main())
