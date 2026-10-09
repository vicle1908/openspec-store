#!/usr/bin/env python3
"""Workstation toolchain candidate classification report generator.

Categorizes installed toolchain items into:
1. Retained (clean, approved in current or isolated root)
2. Repair/Normalize (requires owner cutover, deduplication, or targeted upgrade)
3. Manual Review (requires environmental investigation or operator decision)

Matches the retention decision table defined in design.md Section 10.
Read-only by contract: never modifies any file, directory, or process on disk.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass
class CandidateClassification:
    candidate: str
    current_resolution: str
    action_classification: str  # "Retained", "Repair/Normalize", "Manual Review"
    action_subtype: str
    rationale: str
    gated_preconditions: list[str]
    requires_external_gate: bool
    mutation_planned: bool = False


# Canonical retention decision table matching design.md Section 10
CANONICAL_DECISION_TABLE: list[CandidateClassification] = [
    CandidateClassification(
        candidate="codex",
        current_resolution="~/.npm-global/bin/codex (active), standalone copy",
        action_classification="Repair/Normalize",
        action_subtype="Normalize / Retain npm-global",
        rationale="OpenAI documentation supports npm-global; single active owner avoids updater conflicts. No native update verb exists.",
        gated_preconditions=[
            "Verify npm executable resolution in PATH",
            "Perform references check across agent configs",
            "Stage standalone copy removal under explicit approval packet",
        ],
        requires_external_gate=True,
    ),
    CandidateClassification(
        candidate="qoder",
        current_resolution="~/.local/bin/qodercli + dispatcher, npm shadow",
        action_classification="Repair/Normalize",
        action_subtype="Normalize / Retain Standalone",
        rationale="Vendor quick-start specifies standalone installer with dispatcher; npm bundle is a shadowing duplicate.",
        gated_preconditions=[
            "Verify ~/.qoder/entry dispatcher health and execution",
            "Verify no running process holds handle to npm package",
            "Stage removal of shadowing @qoder-ai/qodercli under explicit approval packet",
        ],
        requires_external_gate=True,
    ),
    CandidateClassification(
        candidate="gitnexus",
        current_resolution="~/.local/share/home-toolchain/bin/gitnexus",
        action_classification="Repair/Normalize",
        action_subtype="Normalize / Retain npm-global",
        rationale="Vendor README specifies npm-global install; no official Homebrew cask. Upstream docs recommend global npm to eliminate cold npx timeouts in MCP servers.",
        gated_preconditions=[
            "Native binding compilation (@ladybugdb/core, tree-sitter) verification",
            "Execute MCP server smoke test via mcp-router tool invocation",
            "Stage cutover from isolated toolchain under explicit approval packet",
        ],
        requires_external_gate=True,
    ),
    CandidateClassification(
        candidate="newman",
        current_resolution="~/.local/share/home-toolchain/bin/newman",
        action_classification="Retained",
        action_subtype="Retain (Isolated Toolchain)",
        rationale="Pinned to 6.2.2 with newman-reporter-htmlextra for Postman collection execution and Faker v5 compatibility.",
        gated_preconditions=[
            "Keep isolated toolchain lockfile intact",
            "Do not force global npm migration",
        ],
        requires_external_gate=False,
    ),
    CandidateClassification(
        candidate="bru",
        current_resolution="~/.local/share/home-toolchain/bin/bru",
        action_classification="Repair/Normalize",
        action_subtype="Targeted Upgrade Candidate",
        rationale="Registry reports 4.2.0 active, 4.2.1 available upstream; targeted minor patch in isolated toolchain.",
        gated_preconditions=[
            "Pre-upgrade smoke on Bruno collection run",
            "Post-upgrade verification of bru --version",
        ],
        requires_external_gate=True,
    ),
    CandidateClassification(
        candidate="opencode",
        current_resolution="/opt/homebrew/bin/opencode (brew), npm duplicate",
        action_classification="Repair/Normalize",
        action_subtype="Retain Homebrew / Prune npm",
        rationale="Homebrew formula is active and maintained; npm package is a duplicate install.",
        gated_preconditions=[
            "Verify Homebrew executable resolution",
            "Prune npm copy after five-point safety check",
        ],
        requires_external_gate=True,
    ),
    CandidateClassification(
        candidate="prime-agent",
        current_resolution="/opt/homebrew/lib/node_modules/prime-agent",
        action_classification="Retained",
        action_subtype="Retain Local Development",
        rationale="Upstream Rust divergence on origin/main; keep local TypeScript build linked. Excluded from automated update runner.",
        gated_preconditions=[
            "Exclude from automated daily update runner",
            "Maintain local TypeScript symlink architecture",
        ],
        requires_external_gate=False,
    ),
    CandidateClassification(
        candidate="python@3.10",
        current_resolution="/opt/homebrew/opt/python@3.10",
        action_classification="Manual Review",
        action_subtype="Manual Review Candidate",
        rationale="Formula deprecated in Homebrew; check if any active service or virtualenv depends on it before uninstallation.",
        gated_preconditions=[
            "Audit virtualenv dependencies across workspace roots",
            "Operator decision before proposing formula uninstallation",
        ],
        requires_external_gate=True,
    ),
    CandidateClassification(
        candidate="ollama",
        current_resolution="Port 11434 collision (background service vs runner)",
        action_classification="Manual Review",
        action_subtype="Manual Review Candidate",
        rationale="Competing background service claims default port; verify if external GPU daemon or Docker runner is primary.",
        gated_preconditions=[
            "Report port collision in quarantine report",
            "Do not stop or kill service automatically",
        ],
        requires_external_gate=True,
    ),
]

# Additional standard retained tools
STANDARD_RETAINED_TOOLS: list[CandidateClassification] = [
    CandidateClassification(
        candidate="claude",
        current_resolution="~/.local/bin/claude",
        action_classification="Retained",
        action_subtype="Retained (Standalone Native)",
        rationale="Official native standalone installer with vendor auto-update.",
        gated_preconditions=["Active smoke check passes"],
        requires_external_gate=False,
    ),
    CandidateClassification(
        candidate="uv",
        current_resolution="/opt/homebrew/bin/uv",
        action_classification="Retained",
        action_subtype="Retained (Homebrew Formula)",
        rationale="Astral uv package manager managed via Homebrew.",
        gated_preconditions=["Active smoke check passes"],
        requires_external_gate=False,
    ),
    CandidateClassification(
        candidate="git",
        current_resolution="/opt/homebrew/bin/git",
        action_classification="Retained",
        action_subtype="Retained (Homebrew Formula)",
        rationale="Core version control managed via Homebrew.",
        gated_preconditions=["Active smoke check passes"],
        requires_external_gate=False,
    ),
    CandidateClassification(
        candidate="node",
        current_resolution="/opt/homebrew/bin/node",
        action_classification="Retained",
        action_subtype="Retained (Homebrew Formula)",
        rationale="Node.js runtime managed via Homebrew.",
        gated_preconditions=["Active smoke check passes"],
        requires_external_gate=False,
    ),
]


def generate_candidate_report(
    include_standard_retained: bool = True,
    category_filter: str | None = None,
) -> dict[str, Any]:
    """Generate the candidate classification report."""
    candidates = list(CANONICAL_DECISION_TABLE)
    if include_standard_retained:
        candidates.extend(STANDARD_RETAINED_TOOLS)

    if category_filter:
        norm_filter = category_filter.strip().lower()
        if "retain" in norm_filter:
            candidates = [c for c in candidates if c.action_classification == "Retained"]
        elif "repair" in norm_filter or "normalize" in norm_filter:
            candidates = [c for c in candidates if c.action_classification == "Repair/Normalize"]
        elif "manual" in norm_filter or "review" in norm_filter:
            candidates = [c for c in candidates if c.action_classification == "Manual Review"]

    retained = [c for c in candidates if c.action_classification == "Retained"]
    repair_normalize = [c for c in candidates if c.action_classification == "Repair/Normalize"]
    manual_review = [c for c in candidates if c.action_classification == "Manual Review"]

    summary = {
        "total_candidates": len(candidates),
        "retained_count": len(retained),
        "repair_normalize_count": len(repair_normalize),
        "manual_review_count": len(manual_review),
        "read_only": True,
        "mutation_planned": False,
    }

    return {
        "summary": summary,
        "candidates": [asdict(c) for c in candidates],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Report toolchain candidate classifications.")
    parser.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    parser.add_argument("--category", choices=["retained", "repair", "manual"], help="Filter by action classification")
    parser.add_argument("--canonical-only", action="store_true", help="Include only the 9 canonical candidates from design.md")

    args = parser.parse_args()

    report = generate_candidate_report(
        include_standard_retained=not args.canonical_only,
        category_filter=args.category,
    )

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print("=== Workstation Toolchain Candidate Classification ===")
        print(f"Total Candidates:   {report['summary']['total_candidates']}")
        print(f"  Retained:         {report['summary']['retained_count']}")
        print(f"  Repair/Normalize: {report['summary']['repair_normalize_count']}")
        print(f"  Manual Review:    {report['summary']['manual_review_count']}")
        print(f"Read-Only:          {report['summary']['read_only']}")
        print("\nCandidate Table:")
        print(f"{'Candidate':15} {'Classification':18} {'Subtype':30} {'Current Resolution'}")
        print("-" * 90)
        for c in report["candidates"]:
            print(f"{c['candidate']:15} {c['action_classification']:18} {c['action_subtype']:30} {c['current_resolution']}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
