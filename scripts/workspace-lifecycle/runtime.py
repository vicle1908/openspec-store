"""Bounded runtime ownership checks for workspace lifecycle cleanup.

Task 4.1 contract: bounded read-only ownership checks for processes,
LaunchAgents, containers, databases, rollback copies, and index watchers.
Each check is best-effort and bounded (design Decision C): when a check is
unavailable or uncertain, the observation is recorded as ``UNKNOWN``
(``available: false``) and classification fails closed toward
``REVIEW_REQUIRED``. An ``UNKNOWN`` runtime owner never converts to
``RECLAIMABLE``.

Secret values, credentials, and request/response bodies never enter
observations: probe detail is redacted with the shared manifest redaction
rules before the observation is emitted, keeping only non-secret owner,
endpoint, and classification metadata.

This module never mutates anything: probes are read-only lookups supplied
by the caller, and unavailable probes degrade to ``UNKNOWN`` instead of
failing the scan.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Mapping, Optional

from manifest import redact_facts

# Bounded runtime ownership surface (task 4.1, design Decision C).
RUNTIME_KINDS = (
    "process",
    "launchagent",
    "container",
    "database",
    "rollback_copy",
    "index_watcher",
)


@dataclass(frozen=True)
class RuntimeCheckOutcome:
    """Result of one bounded runtime probe.

    ``available`` is False when the check could not run or is uncertain;
    the observation then reports UNKNOWN and blocks reclaimability.
    ``active`` is True when a live owner references the path.
    """

    kind: str
    available: bool
    active: bool
    owner: str = ""
    detail: Mapping[str, Any] = field(default_factory=dict)


def unknown(kind: str) -> RuntimeCheckOutcome:
    """The fail-closed outcome for an unavailable or uncertain check."""
    return RuntimeCheckOutcome(kind=kind, available=False, active=False)


def run_check(
    kind: str, path: str, probe: Optional[Callable[[str], Any]]
) -> RuntimeCheckOutcome:
    """Run one bounded probe; any failure degrades to UNKNOWN.

    Missing probes, raised errors, ``None`` results, wrong types, and
    kind mismatches all fail closed to ``UNKNOWN`` so a broken adapter
    can never certify reclaimability.
    """
    if kind not in RUNTIME_KINDS:
        raise ValueError(f"unknown runtime check kind: {kind!r}")
    if probe is None:
        return unknown(kind)
    try:
        outcome = probe(path)
    except Exception:
        return unknown(kind)
    if not isinstance(outcome, RuntimeCheckOutcome) or outcome.kind != kind:
        return unknown(kind)
    return outcome


def runtime_observations(
    canonical_path: str,
    probes: Mapping[str, Callable[[str], Any]],
    observed_at: str,
) -> list:
    """Emit one redacted runtime observation per bounded check kind.

    ``probes`` maps a check kind to a read-only callable
    ``probe(path) -> RuntimeCheckOutcome | None``. Missing or failing
    probes produce UNKNOWN observations rather than skipping the check,
    so unavailable ownership evidence blocks reclaimability. Every
    observation carries the contract keys ``kind``, ``owner``, ``active``,
    and ``available``; probe detail is redacted before it is merged.
    """
    observations = []
    for kind in RUNTIME_KINDS:
        outcome = run_check(kind, canonical_path, probes.get(kind))
        facts = dict(redact_facts(dict(outcome.detail)))
        facts["kind"] = kind
        facts["owner"] = outcome.owner
        facts["active"] = bool(outcome.active)
        facts["available"] = bool(outcome.available)
        observations.append(
            {
                "authority": "runtime",
                "canonical_path": canonical_path,
                "subject": outcome.owner or f"{kind}-unknown",
                "observed_at": observed_at,
                "facts": facts,
            }
        )
    return observations
