"""Ordered retirement gates for workspace lifecycle cleanup.

Retirement follows ownership order (design Decision 4, spec "Ordered
retirement ownership"):

1. Orca reports no live session, agent, terminal, attached PTY, pin, child
   worktree, or host activity (task 3.1 preconditions).
2. Orca file-handle/workspace state is released before Git removal.
3. Git worktree removal is recorded only after step 1-2 pass (task 3.2
   preservation gates apply first).
4. Branch deletion is attempted only after the worktree transition is
   recorded.
5. OpenSpec paths are handled only by OpenSpec lifecycle commands.

This module gates and records; it never executes removal. Actual
worktree/branch retirement is performed by the owning lifecycle tool after
approval, and the first version performs no deletion at all.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Optional

from observations import PathRecord

# Terminal states: connected terminals block outright; orphaned terminals
# block as REVIEW_REQUIRED (spec: no filesystem removal is proposed while an
# orphaned terminal's ownership cannot be conclusively retired).
TERMINAL_BLOCKING = ("connected",)
TERMINAL_REVIEW = ("orphaned",)

AGENT_BLOCKING = ("working", "interrupted")

# Retirement state a child worktree must reach before its parent may retire.
CHILD_CLEARED_STATE = "RECLAIMED"


@dataclass(frozen=True)
class PreconditionResult:
    satisfied: bool
    blockers: tuple
    review_required: bool  # True when a block is REVIEW-class, not PROTECTED


def is_orca_managed(record: PathRecord) -> bool:
    return bool(record.by_authority("orca"))


def orca_preconditions(
    record: PathRecord,
    child_states: Optional[Mapping[str, str]] = None,
) -> PreconditionResult:
    """Evaluate Orca retirement preconditions for one correlated path.

    ``child_states`` maps child worktree identities to their current
    retirement classification. Children are retired before parents: any
    child not yet ``RECLAIMED`` blocks the parent. Without explicit states,
    listed children are assumed active (fail closed).

    File-handle release requires explicit evidence
    (``file_handles_released: true``); absent evidence fails closed.
    """
    orca_observations = record.by_authority("orca")
    if not orca_observations:
        return PreconditionResult(True, (), False)

    blockers: list[str] = []
    review_required = False

    for obs in orca_observations:
        facts = obs.facts
        if facts.get("isPinned"):
            blockers.append(f"orca_pinned:{obs.subject}")
        agent_state = facts.get("agent_state")
        if agent_state in AGENT_BLOCKING:
            blockers.append(f"orca_agent_{agent_state}:{obs.subject}")
        terminal_state = facts.get("terminal_state")
        if facts.get("live_terminal") or terminal_state in TERMINAL_BLOCKING:
            blockers.append(f"orca_terminal_connected:{obs.subject}")
        if terminal_state in TERMINAL_REVIEW:
            review_required = True
            blockers.append(f"orca_orphaned_terminal_unresolved:{obs.subject}")
        if facts.get("attached_pty"):
            blockers.append(f"orca_attached_pty:{obs.subject}")
        if facts.get("host_activity"):
            blockers.append(f"orca_host_activity:{obs.subject}")
        if facts.get("file_handles_released") is not True:
            blockers.append(f"orca_file_handles_held:{obs.subject}")

    listed_children = []
    for obs in orca_observations:
        for child in obs.facts.get("child_worktrees") or []:
            if child not in listed_children:
                listed_children.append(str(child))

    if listed_children:
        if child_states is None:
            active_children = listed_children
        else:
            active_children = [
                child
                for child in listed_children
                if child_states.get(child) != CHILD_CLEARED_STATE
            ]
        if active_children:
            blockers.append(
                "orca_active_child_worktrees:" + ",".join(sorted(active_children))
            )

    deduped = []
    for blocker in blockers:
        if blocker not in deduped:
            deduped.append(blocker)
    return PreconditionResult(
        satisfied=not deduped,
        blockers=tuple(deduped),
        review_required=review_required,
    )

# -----------------------------------------------------------------------
# Task 3.2 — Git preservation gates
# -----------------------------------------------------------------------

# A path is RECLAIMABLE only when its content is provably preserved
# by the target history, an approved remote or backup, or an explicitly
# retained archival artifact (spec "Merge and preservation proof").
# Squash-merged content requires content-equivalence evidence; unpushed
# history without an approved preservation record blocks reclaimability.
# All unsatisfied outcomes are REVIEW-class (never PROTECTED) because
# the preservation gate is a retirement-time check, not a classification.


@dataclass(frozen=True)
class PreservationResult:
    satisfied: bool
    blockers: tuple
    evidence: tuple
    review_required: bool  # always True when unsatisfied


def git_preservation_gate(record: PathRecord) -> PreservationResult:
    """Evaluate Git content preservation for one correlated path."""
    git_observations = record.by_authority("git")
    if not git_observations:
        return PreservationResult(False, ("git_no_observations",), (), True)

    blockers: list[str] = []
    evidence: list[str] = []
    has_preservation_proof = False

    index_observations = record.by_authority("index")
    index_confirms_generated = any(
        obs.facts.get("provider") for obs in index_observations
    )

    for obs in git_observations:
        facts = obs.facts
        rev = obs.revision or "unknown"

        if facts.get("dirty") and not facts.get("generated_only"):
            blockers.append("git_non_generated_dirt")
        elif facts.get("dirty") and facts.get("generated_only"):
            if index_confirms_generated:
                evidence.append(f"generated_only_dirt_confirmed:{rev}")
            else:
                blockers.append("git_generated_dirt_unconfirmed")

        if facts.get("squash_merged"):
            if facts.get("content_equivalent"):
                evidence.append(f"squash_equivalence_proven:{rev}")
                has_preservation_proof = True
            else:
                blockers.append("git_squash_equivalence_unresolved")

        if facts.get("unpushed"):
            blockers.append(f"git_unpushed_history:{rev}")

        if facts.get("detached"):
            if facts.get("ancestor_of_target"):
                evidence.append(f"detached_ancestor_proven:{rev}")
            elif facts.get("remote_reachable") or facts.get("backup_reachable"):
                pass
            else:
                blockers.append(f"git_detached_unique_revision:{rev}")

        if facts.get("ancestor_of_target") or facts.get("merged_into_target"):
            evidence.append(f"merge_ancestry:{rev}")
            has_preservation_proof = True
        if facts.get("remote_reachable"):
            evidence.append(f"remote_reachable:{rev}")
            has_preservation_proof = True
        if facts.get("backup_reachable"):
            evidence.append(f"backup_reachable:{rev}")
            has_preservation_proof = True

    if not has_preservation_proof:
        blockers.append("git_preservation_not_proven")

    satisfied = not blockers
    return PreservationResult(
        satisfied=satisfied,
        blockers=tuple(blockers),
        evidence=tuple(evidence),
        review_required=not satisfied,
    )

# -----------------------------------------------------------------------
# Task 3.3 — Ordered transition recording
# -----------------------------------------------------------------------

# Retirement is a sequence of independently verifiable transitions in
# ownership order (design Decision 4, spec "Ordered retirement
# ownership"): child Orca worktrees first, then parent Orca
# workspace/file-handle release, then Git worktree removal, and the
# branch reference last. OpenSpec paths are never retired through these
# generic steps.

STEP_PENDING = "PENDING"
STEP_COMPLETED = "COMPLETED"
STEP_FAILED = "FAILED"

RECORD_DEFERRED = "DEFERRED_TO_OPENSPEC"
RECORD_BLOCKED = "BLOCKED"
RECORD_IN_PROGRESS = "IN_PROGRESS"
RECORD_FAILED = "FAILED"
RECORD_COMPLETED = "COMPLETED"

ORCA_CHILDREN_STEP = "orca_children_retired"
ORCA_RELEASE_STEP = "orca_workspace_released"
GIT_WORKTREE_STEP = "git_worktree_removed"
GIT_BRANCH_STEP = "git_branch_deleted"

TRANSITION_STEPS = (
    ORCA_CHILDREN_STEP,
    ORCA_RELEASE_STEP,
    GIT_WORKTREE_STEP,
    GIT_BRANCH_STEP,
)


class TransitionError(ValueError):
    """Transition recording violates ownership order or record state."""


@dataclass
class RetirementRecord:
    """Auditable ordered retirement state for one approved candidate.

    The record is pure audit data: it tracks transitions and never
    performs removal. A failed transition leaves the completed and
    pending steps recorded; the workflow does not compensate by deleting
    the path directly.
    """

    canonical_path: str
    plan_id: str
    state: str
    classification: str
    steps: dict  # step name -> STEP_* status; insertion order = ownership order
    blockers: tuple
    audit: list  # (step, status, evidence) in recording order

    @property
    def completed_steps(self) -> tuple:
        return tuple(
            name for name, status in self.steps.items()
            if status == STEP_COMPLETED
        )

    @property
    def pending_steps(self) -> tuple:
        return tuple(
            name for name, status in self.steps.items()
            if status == STEP_PENDING
        )

    @property
    def failed_step(self) -> Optional[str]:
        for name, status in self.steps.items():
            if status == STEP_FAILED:
                return name
        return None

    def _next_actionable(self) -> Optional[str]:
        for name, status in self.steps.items():
            if status in (STEP_PENDING, STEP_FAILED):
                return name
        return None

    def record_transition(
        self, step: str, succeeded: bool, evidence: str = ""
    ) -> None:
        """Record one transition outcome, enforcing ownership order.

        Only the next pending step — or the failed step, for an explicit
        retry — may be recorded. Failure halts the sequence: remaining
        steps stay ``PENDING`` and the classification stays
        ``REVIEW_REQUIRED``. Success on the final step marks the record
        ``RECLAIMED``.
        """
        if self.state not in (RECORD_IN_PROGRESS, RECORD_FAILED):
            raise TransitionError(
                f"retirement record is not actionable: state={self.state}"
            )
        if step not in self.steps:
            raise TransitionError(f"unknown transition step: {step!r}")
        expected = self._next_actionable()
        if step != expected:
            raise TransitionError(
                f"out-of-order transition {step!r}; "
                f"next actionable is {expected!r}"
            )
        status = STEP_COMPLETED if succeeded else STEP_FAILED
        self.steps[step] = status
        self.audit.append((step, status, evidence))
        if not succeeded:
            self.state = RECORD_FAILED
            self.classification = "REVIEW_REQUIRED"
            return
        if all(value == STEP_COMPLETED for value in self.steps.values()):
            self.state = RECORD_COMPLETED
            self.classification = "RECLAIMED"
        else:
            self.state = RECORD_IN_PROGRESS


def plan_retirement(
    record: PathRecord,
    plan_id: str,
    child_states: Optional[Mapping[str, str]] = None,
) -> RetirementRecord:
    """Build the ordered retirement record for one correlated path.

    OpenSpec-governed paths defer to OpenSpec lifecycle commands and
    receive no generic transitions. Every other path must pass the Orca
    preconditions (task 3.1) and the Git preservation gates (task 3.2)
    before any transition becomes actionable; unsatisfied gates leave the
    record blocked with its blockers retained.
    """
    if record.by_authority("openspec"):
        return RetirementRecord(
            canonical_path=record.canonical_path,
            plan_id=plan_id,
            state=RECORD_DEFERRED,
            classification="REVIEW_REQUIRED",
            steps={},
            blockers=("openspec_lifecycle_deferral",),
            audit=[("plan", RECORD_DEFERRED,
                    "defer to OpenSpec lifecycle commands")],
        )

    pre = orca_preconditions(record, child_states)
    preservation = git_preservation_gate(record)
    blockers = tuple(pre.blockers) + tuple(preservation.blockers)
    if blockers:
        return RetirementRecord(
            canonical_path=record.canonical_path,
            plan_id=plan_id,
            state=RECORD_BLOCKED,
            classification="REVIEW_REQUIRED",
            steps={},
            blockers=blockers,
            audit=[("plan", RECORD_BLOCKED, "gates unsatisfied")],
        )

    steps: dict = {}
    if is_orca_managed(record):
        steps[ORCA_CHILDREN_STEP] = STEP_PENDING
        steps[ORCA_RELEASE_STEP] = STEP_PENDING
    steps[GIT_WORKTREE_STEP] = STEP_PENDING
    steps[GIT_BRANCH_STEP] = STEP_PENDING
    return RetirementRecord(
        canonical_path=record.canonical_path,
        plan_id=plan_id,
        state=RECORD_IN_PROGRESS,
        classification="REVIEW_REQUIRED",
        steps=steps,
        blockers=(),
        audit=[("plan", RECORD_IN_PROGRESS,
                "orca preconditions and git preservation gates satisfied")],
    )
