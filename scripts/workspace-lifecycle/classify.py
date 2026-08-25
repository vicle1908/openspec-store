"""Deterministic classification precedence for workspace lifecycle cleanup.

Task 1.2 contract: ``PROTECTED`` > ``REVIEW_REQUIRED`` > ``RECLAIMABLE`` >
``RECLAIMED``. A more restrictive observation always wins; unknown ownership
fails closed and is never converted to ``RECLAIMABLE``. Retention protection
(task 0.2 handoff) is applied as an exclusion layer before authority signals.

Rules are derived from the spec scenarios and design Decision 2:

- PROTECTED: active OpenSpec change or untracked change/archive move,
  non-generated uncommitted content, Orca pin/working-or-interrupted agent/
  live terminal/attached PTY/host activity/child worktrees, active runtime
  owner, active index watcher.
- REVIEW_REQUIRED: unknown ownership, orphaned unresolved terminal, detached
  unique revision, unpushed history, unresolved squash equivalence,
  unavailable runtime check (UNKNOWN), unconfirmed generated dirt, retention
  review states, missing retention inventory (fail closed).
- RECLAIMABLE: preservation proven (ancestor of target, approved remote, or
  backup), clean or confirmed-generated-only dirt, no owner activity, and no
  retention protection.
- RECLAIMED: only after an approved lifecycle transition is recorded.

This module is read-only: it classifies correlated observations and never
mutates anything.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import retention
from observations import PathRecord

CLASSIFICATIONS = ("PROTECTED", "REVIEW_REQUIRED", "RECLAIMABLE", "RECLAIMED")

_ACTIVE_AGENT_STATES = ("working", "interrupted")


@dataclass(frozen=True)
class Classification:
    classification: str
    blockers: tuple  # reasons that forced the outcome, most restrictive first
    evidence: tuple  # proof references used for the result


def classify_path(
    record: PathRecord,
    retention_inventory: Optional[retention.RetentionInventory] = None,
) -> Classification:
    """Classify one correlated path record using strict precedence."""
    blockers: list[str] = []
    evidence: list[str] = []

    # RECLAIMED: only after an approved lifecycle transition is recorded.
    for obs in record.observations:
        if obs.facts.get("approved_retirement_recorded"):
            return Classification(
                "RECLAIMED",
                (),
                (f"approved_retirement_recorded:{obs.subject}",),
            )

    # Retention exclusion layer (task 0.2 handoff, design Decision 5).
    decision = retention.gate(retention_inventory, record.canonical_path)
    if decision.outcome == retention.EXCLUDED_PROTECTED:
        return Classification(
            "PROTECTED",
            (f"retention:{decision.reason}",),
            (f"retention_entry:{decision.entry.path}",),
        )
    if decision.outcome == retention.REVIEW_ONLY_CANDIDATE:
        blockers.append(f"retention:{decision.reason}")
    elif decision.outcome == retention.REVIEW_REQUIRED:
        blockers.append(f"retention:{decision.reason}")
    elif decision.outcome == retention.UNAVAILABLE:
        blockers.append("retention_inventory_unavailable")
    else:
        evidence.append("retention:not_governed")

    protected: list[str] = []
    review: list[str] = []

    if not record.observations:
        review.append("unknown_ownership")

    for obs in record.observations:
        facts = obs.facts
        if obs.authority == "openspec":
            change = facts.get("change") or obs.subject
            if int(facts.get("incomplete_tasks") or 0) > 0:
                protected.append(f"openspec_active_change:{change}")
            if facts.get("untracked"):
                if facts.get("archive_move"):
                    protected.append(f"openspec_untracked_archive_move:{change}")
                else:
                    protected.append(f"openspec_untracked_change_dir:{change}")
        elif obs.authority == "git":
            if facts.get("dirty") and not facts.get("generated_only"):
                protected.append("non_generated_uncommitted_content")
            if facts.get("unpushed"):
                review.append("unpushed_history")
            if (
                facts.get("detached")
                and not facts.get("ancestor_of_target")
                and not facts.get("remote_reachable")
                and not facts.get("backup_reachable")
            ):
                review.append(
                    f"detached_unique_revision:{obs.revision or 'unknown'}"
                )
            if facts.get("squash_merged") and not facts.get("content_equivalent"):
                review.append("squash_equivalence_unresolved")
        elif obs.authority == "orca":
            if facts.get("isPinned"):
                protected.append("orca_pinned")
            agent_state = facts.get("agent_state")
            if agent_state in _ACTIVE_AGENT_STATES:
                protected.append(f"orca_agent_{agent_state}:{obs.subject}")
            if facts.get("live_terminal"):
                protected.append(f"orca_live_terminal:{obs.subject}")
            if facts.get("attached_pty"):
                protected.append("orca_attached_pty")
            if facts.get("host_activity"):
                protected.append("orca_host_activity")
            if facts.get("child_worktrees"):
                protected.append("orca_child_worktrees")
            if facts.get("terminal_state") == "orphaned":
                review.append(f"orca_orphaned_terminal:{obs.subject}")
        elif obs.authority == "runtime":
            if facts.get("available") is False:
                review.append(
                    f"runtime_ownership_unknown:{facts.get('kind') or 'unknown'}"
                )
            elif facts.get("active"):
                protected.append(
                    f"runtime_owner:{facts.get('kind') or 'unknown'}:{obs.subject}"
                )
        elif obs.authority == "index":
            if facts.get("watcher_active"):
                protected.append(
                    f"index_watcher_active:{facts.get('provider') or 'unknown'}"
                )

    # Generated-only dirt is provable noise only when index ownership
    # metadata confirms it (design Decision 5); otherwise it fails closed.
    for obs in record.by_authority("git"):
        facts = obs.facts
        if facts.get("dirty") and facts.get("generated_only"):
            confirmed = any(
                index_obs.facts.get("provider")
                for index_obs in record.by_authority("index")
            )
            if confirmed:
                evidence.append("generated_only_dirt_confirmed_by_index_owner")
            else:
                review.append("generated_dirt_unconfirmed")

    if protected:
        return Classification(
            "PROTECTED", tuple(protected + blockers), tuple(evidence)
        )
    if review or blockers:
        return Classification(
            "REVIEW_REQUIRED", tuple(review + blockers), tuple(evidence)
        )

    # RECLAIMABLE: preservation proven, clean, no owner activity, and the
    # retention layer did not cap reclaimability.
    preservation: list[str] = []
    for obs in record.by_authority("git"):
        facts = obs.facts
        if facts.get("ancestor_of_target"):
            preservation.append(f"ancestor_of_target:{obs.revision or 'unknown'}")
        if facts.get("remote_reachable"):
            preservation.append(f"remote_reachable:{obs.revision or 'unknown'}")
        if facts.get("backup_reachable"):
            preservation.append(f"backup_reachable:{obs.revision or 'unknown'}")
    if preservation:
        return Classification("RECLAIMABLE", (), tuple(evidence + preservation))

    return Classification(
        "REVIEW_REQUIRED", ("reclaimability_not_proven",), tuple(evidence)
    )
