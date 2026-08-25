"""Read-only authority observations for workspace lifecycle cleanup.

Task 1.1 contract: observations for OpenSpec, Git, Orca, and runtime/index
ownership carry canonical path, repository/worktree identity, branch or
detached revision, activity, and an observation timestamp.

Adapters emit observations, not classifications (design Decision 1). The
correlator groups observations by canonical path and preserves conflicting
authority states rather than selecting the less restrictive state; the
classifier applies the most restrictive applicable outcome.

This module is read-only: it never queries live systems by itself and never
mutates anything. Live adapters produce observation dicts that match the
shape validated here.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Iterable, Mapping

AUTHORITIES = ("openspec", "git", "orca", "runtime", "index")

# Fact keys that mark an observation as live/owning activity.
_ACTIVITY_FACT_KEYS = (
    "live_terminal",
    "attached_pty",
    "host_activity",
    "isPinned",
    "active",
    "watcher_active",
)
_ACTIVE_AGENT_STATES = ("working", "interrupted")


class ObservationError(ValueError):
    """An observation is malformed."""


@dataclass(frozen=True)
class Observation:
    """One read-only authority observation."""

    authority: str
    canonical_path: str
    subject: str  # change name, branch, worktree/terminal id, owner id...
    observed_at: str  # ISO8601 UTC
    facts: Mapping[str, Any]

    @property
    def revision(self) -> str:
        return str(self.facts.get("revision") or "")

    @property
    def indicates_activity(self) -> bool:
        """True when the observation reports live ownership or activity."""
        if any(bool(self.facts.get(key)) for key in _ACTIVITY_FACT_KEYS):
            return True
        if self.facts.get("agent_state") in _ACTIVE_AGENT_STATES:
            return True
        if self.authority == "openspec" and int(self.facts.get("incomplete_tasks") or 0) > 0:
            return True
        if self.authority == "git" and bool(self.facts.get("dirty")) and not bool(
            self.facts.get("generated_only")
        ):
            return True
        return False

    @property
    def indicates_reclaimable_leaning(self) -> bool:
        """True when a Git observation alone would lean toward reclaimable."""
        if self.authority != "git":
            return False
        if self.facts.get("dirty") and not self.facts.get("generated_only"):
            return False
        return bool(
            self.facts.get("merged_into_target") or self.facts.get("ancestor_of_target")
        )


def parse_observed_at(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except (TypeError, ValueError) as exc:
        raise ObservationError(f"invalid observed_at timestamp: {value!r}") from exc
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def validate_observation(raw: Mapping[str, Any]) -> Observation:
    """Validate one raw observation dict against the task 1.1 contract."""
    if not isinstance(raw, Mapping):
        raise ObservationError("observation must be an object")
    authority = raw.get("authority")
    if authority not in AUTHORITIES:
        raise ObservationError(f"unknown authority: {authority!r}")
    canonical_path = str(raw.get("canonical_path") or "")
    if not canonical_path or not os.path.isabs(canonical_path):
        raise ObservationError(
            f"observation requires an absolute canonical path: {canonical_path!r}"
        )
    subject = str(raw.get("subject") or "")
    if not subject:
        raise ObservationError("observation requires a subject identity")
    observed_at = str(raw.get("observed_at") or "")
    parse_observed_at(observed_at)
    facts = raw.get("facts")
    if not isinstance(facts, Mapping):
        raise ObservationError("observation requires a facts object")
    return Observation(
        authority=str(authority),
        canonical_path=os.path.normpath(canonical_path),
        subject=subject,
        observed_at=observed_at,
        facts=facts,
    )


@dataclass
class PathRecord:
    """All authority observations correlated under one canonical path.

    Conflicting observations are preserved verbatim; nothing is merged away.
    """

    canonical_path: str
    observations: list  # Observation, insertion order

    def by_authority(self, authority: str) -> list:
        return [obs for obs in self.observations if obs.authority == authority]

    @property
    def authorities(self) -> set:
        return {obs.authority for obs in self.observations}

    def conflicting_pairs(self) -> list:
        """Pairs where one authority leans reclaimable while another is active.

        Example: Git reports a merged, clean worktree while Orca reports a
        live terminal on the same path. Both observations are preserved; the
        classifier must pick the most restrictive outcome.
        """
        pairs = []
        for left in self.observations:
            for right in self.observations:
                if left is right:
                    continue
                if left.indicates_reclaimable_leaning and right.indicates_activity:
                    pairs.append((left, right))
        return pairs


def correlate(observations: Iterable[Observation]) -> dict:
    """Group validated observations by canonical path, preserving conflicts."""
    records: dict[str, PathRecord] = {}
    for observation in observations:
        record = records.get(observation.canonical_path)
        if record is None:
            record = PathRecord(observation.canonical_path, [])
            records[observation.canonical_path] = record
        record.observations.append(observation)
    return records


def load_observations(raw_observations: Iterable[Mapping[str, Any]]) -> list:
    """Validate a batch of raw observation dicts."""
    return [validate_observation(raw) for raw in raw_observations]
