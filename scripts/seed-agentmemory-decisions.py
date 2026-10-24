#!/usr/bin/env python3
"""Idempotent toolchain decision seeding script for AgentMemory.

Publishes durable toolchain governance decisions into AgentMemory via the
HTTP REST API (/agentmemory/observations or /agentmemory/remember).
Suppresses duplicate observations by checking existing entries first.

Contract:
- Defaults to dry-run mode (--dry-run=True); requires --apply to perform writes.
- Communicates exclusively via HTTP REST API. NEVER modifies SQLite files directly.
- Standard library only.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any
lazy from collections.abc import Callable

DEFAULT_BASE_URL = "http://localhost:3111"

# Canonical durable toolchain decisions to seed
CANONICAL_DECISIONS = [
    {
        "id": "codex-update-authority",
        "title": "Codex Update Authority",
        "content": "Codex update authority is npm-global under ~/.npm-global (@openai/codex); native codex update verb is invalid and suppressed.",
        "concepts": ["workstation-governance", "codex-update-authority", "npm-global"],
    },
    {
        "id": "qoder-standalone-authority",
        "title": "Qoder Standalone Authority",
        "content": "Qoder update authority is standalone vendor installer owning ~/.local/bin/qodercli and ~/.qoder/entry dispatcher.",
        "concepts": ["workstation-governance", "qoder-standalone-authority", "standalone"],
    },
    {
        "id": "agentmemory-engine-pin",
        "title": "AgentMemory Engine Pin",
        "content": "AgentMemory 0.9.30 pins iii-engine 0.22.1; legacy engine processes on port 49134 are quarantined.",
        "concepts": ["workstation-governance", "agentmemory-engine-pin", "iii-engine"],
    },
    {
        "id": "isolated-toolchain-integrity",
        "title": "Isolated Toolchain Newman & Faker Pin",
        "content": "Isolated toolchain at ~/.local/share/home-toolchain retains Newman 6.2.2 with newman-reporter-htmlextra and Faker v5.",
        "concepts": ["workstation-governance", "isolated-toolchain", "newman"],
    },
    {
        "id": "docker-persistent-volumes",
        "title": "Docker Persistent Volume Protection",
        "content": "Docker volume hygiene protects omniroute_data and microservice database volumes against routine system pruning.",
        "concepts": ["workstation-governance", "docker-hygiene", "omniroute_data"],
    },
    {
        "id": "shell-path-precedence",
        "title": "Shell PATH Precedence Alignment",
        "content": "Documented PATH precedence places ~/.local/bin ahead of /opt/homebrew/bin and places /opt/homebrew/bin ahead of ~/.npm-global/bin and ~/.bun/bin across interactive and daily update environments.",
        "concepts": ["workstation-governance", "shell-path-precedence", "path-policy"],
    },
]


@dataclass
class DecisionSeedResult:
    decision_id: str
    action: str  # 'WOULD_SEED', 'SEEDED', 'DUPLICATE_SKIPPED', 'FAILED'
    content: str
    concepts: list[str]
    details: str


def fetch_existing_observations(
    base_url: str,
    secret: str | None = None,
    mock_existing: list[dict[str, Any]] | None = None,
    timeout: float = 5.0,
) -> list[dict[str, Any]]:
    """Query existing observations via REST API."""
    if mock_existing is not None:
        return mock_existing

    url = f"{base_url.rstrip('/')}/agentmemory/observations"
    headers = {"Accept": "application/json"}
    if secret:
        headers["Authorization"] = f"Bearer {secret}"

    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if isinstance(data, list):
                return data
            if isinstance(data, dict) and "observations" in data:
                return data["observations"]
            return []
    except Exception:
        # Fallback to empty if endpoint not yet initialized or offline
        return []


def is_duplicate(decision: dict[str, Any], existing_observations: list[dict[str, Any]]) -> bool:
    """Check if observation already exists in AgentMemory."""
    dec_id = decision["id"]
    dec_content = decision["content"].strip().lower()

    for obs in existing_observations:
        # Check concepts
        obs_concepts = obs.get("concepts", [])
        if dec_id in obs_concepts:
            return True
        # Check content match
        obs_content = obs.get("content", "").strip().lower()
        if dec_content in obs_content or obs_content in dec_content:
            return True

    return False


def post_observation(
    base_url: str,
    decision: dict[str, Any],
    secret: str | None = None,
    post_hook: Callable[[dict[str, Any]], bool] | None = None,
    timeout: float = 5.0,
) -> tuple[bool, str]:
    """Publish a single observation via REST API."""
    if post_hook is not None:
        success = post_hook(decision)
        return success, "Mock post succeeded" if success else "Mock post failed"

    url = f"{base_url.rstrip('/')}/agentmemory/remember"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    if secret:
        headers["Authorization"] = f"Bearer {secret}"

    payload = json.dumps({
        "content": decision["content"],
        "concepts": decision["concepts"],
        "metadata": {
            "source": "portable-workstation-manifest",
            "decision_id": decision["id"],
        },
    }).encode("utf-8")

    req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            if resp.status in (200, 201):
                return True, f"HTTP {resp.status} Created"
            return False, f"Unexpected HTTP status {resp.status}"
    except urllib.error.HTTPError as e:
        return False, f"HTTP {e.code}: {e.reason}"
    except Exception as e:
        return False, str(e)


def seed_decisions(
    base_url: str = DEFAULT_BASE_URL,
    dry_run: bool = True,
    secret: str | None = None,
    decisions: list[dict[str, Any]] | None = None,
    mock_existing: list[dict[str, Any]] | None = None,
    post_hook: Callable[[dict[str, Any]], bool] | None = None,
    timeout: float = 5.0,
) -> dict[str, Any]:
    """Idempotently seed decisions into AgentMemory via REST API."""
    sec = secret or os.environ.get("AGENTMEMORY_SECRET")
    target_decisions = decisions or CANONICAL_DECISIONS

    existing = fetch_existing_observations(
        base_url=base_url,
        secret=sec,
        mock_existing=mock_existing,
        timeout=timeout,
    )

    results: list[DecisionSeedResult] = []
    seeded_count = 0
    would_seed_count = 0
    duplicate_count = 0
    failed_count = 0

    for dec in target_decisions:
        if is_duplicate(dec, existing):
            duplicate_count += 1
            results.append(DecisionSeedResult(
                decision_id=dec["id"],
                action="DUPLICATE_SKIPPED",
                content=dec["content"],
                concepts=dec["concepts"],
                details="Observation already present in AgentMemory; duplicate suppressed",
            ))
        elif dry_run:
            would_seed_count += 1
            results.append(DecisionSeedResult(
                decision_id=dec["id"],
                action="WOULD_SEED",
                content=dec["content"],
                concepts=dec["concepts"],
                details="Dry-run active; observation would be published via REST API",
            ))
        else:
            success, msg = post_observation(
                base_url=base_url,
                decision=dec,
                secret=sec,
                post_hook=post_hook,
                timeout=timeout,
            )
            if success:
                seeded_count += 1
                results.append(DecisionSeedResult(
                    decision_id=dec["id"],
                    action="SEEDED",
                    content=dec["content"],
                    concepts=dec["concepts"],
                    details=f"Published successfully ({msg})",
                ))
            else:
                failed_count += 1
                results.append(DecisionSeedResult(
                    decision_id=dec["id"],
                    action="FAILED",
                    content=dec["content"],
                    concepts=dec["concepts"],
                    details=f"Publication failed: {msg}",
                ))

    return {
        "status": "PASS" if failed_count == 0 else "FAIL",
        "dry_run": dry_run,
        "base_url": base_url,
        "total": len(target_decisions),
        "seeded_count": seeded_count,
        "would_seed_count": would_seed_count,
        "duplicate_skipped_count": duplicate_count,
        "failed_count": failed_count,
        "decisions": [asdict(r) for r in results],
        "policy": "REST API only. Direct SQLite file access strictly prohibited.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Idempotent toolchain decision seeding for AgentMemory")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="AgentMemory server base URL")
    parser.add_argument("--apply", action="store_true", help="Apply seeding (default is dry-run)")
    parser.add_argument("--secret", default=None, help="AgentMemory secret for authentication")
    parser.add_argument("--mock-file", type=Path, default=None, help="Path to JSON fixture of existing observations")
    parser.add_argument("--json", action="store_true", help="Output summary as JSON")

    args = parser.parse_args()

    mock_existing = None
    if args.mock_file and args.mock_file.is_file():
        with open(args.mock_file, encoding="utf-8") as f:
            mock_existing = json.load(f)

    report = seed_decisions(
        base_url=args.base_url,
        dry_run=not args.apply,
        secret=args.secret,
        mock_existing=mock_existing,
    )

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        mode_str = "APPLY" if not report["dry_run"] else "DRY-RUN"
        print(f"=== AgentMemory Decision Seeding [{mode_str}] ===")
        print(f"Total Decisions:     {report['total']}")
        print(f"Seeded:              {report['seeded_count']}")
        print(f"Would Seed:          {report['would_seed_count']}")
        print(f"Duplicates Skipped:  {report['duplicate_skipped_count']}")
        print(f"Failed:              {report['failed_count']}")
        print("-" * 60)
        for d in report["decisions"]:
            sym = "OK" if d["action"] in ("SEEDED", "WOULD_SEED", "DUPLICATE_SKIPPED") else "ERR"
            print(f"  [{sym}] {d['decision_id']:<30} -> {d['action']:<18}: {d['details']}")

    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
