"""Retention inventory consumer for workspace lifecycle cleanup.

Consumes the handoff defined by the ``workspace-artifact-retention-policy``
change (design Decision 9): an operational inventory document at
``~/Developer/.workspace-retention/retention-inventory.json``.

Semantics shared verbatim with the retention change:

- The lifecycle consumer reads ``entries``.
- ``PROTECTED`` classes and states are exclusion lists: a protected path is
  never a lifecycle candidate and is never deleted or relocated.
- ``RECLAIMABLE`` candidate artifacts are review-only proposals, never
  approved deletion targets.
- Entries with missing provenance or owner are downgraded to
  ``REVIEW_REQUIRED`` (numeric staleness bounds are owned by the retention
  producer's provenance freshness checks).
- A missing, malformed, or unapproved inventory fails closed: artifact
  reclaimability is blocked until an operator resolves the uncertainty.

This module is read-only. It never mutates the inventory or any retained
path, and it never exposes credential values or request/response bodies.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Optional

POLICY_NAME = "workspace-artifact-retention-policy"
DEFAULT_INVENTORY_PATH = (
    Path.home() / "Developer" / ".workspace-retention" / "retention-inventory.json"
)

POLICY_STATES = ("PROTECTED", "REVIEW_REQUIRED", "RECLAIMABLE", "RECLAIMED")

RETENTION_CLASSES = (
    "active index state",
    "generated index or cache",
    "tracked permanent fixture",
    "temporary or ephemeral test fixture",
    "runtime state or database",
    "retained evidence or report",
    "retained rollback or snapshot",
    "operator-owned preserved file",
)

PROTECTED_CLASSES = frozenset(
    {
        "active index state",
        "runtime state or database",
        "tracked permanent fixture",
        "retained evidence or report",
        "retained rollback or snapshot",
        "operator-owned preserved file",
    }
)

CANDIDATE_CLASSES = frozenset(
    {
        "generated index or cache",
        "temporary or ephemeral test fixture",
    }
)

# Field names that must never appear anywhere in a retention inventory.
_SECRET_FIELD_PATTERN = re.compile(
    r"(password|passwd|secret|token|api[_-]?key|credential|authorization|"
    r"private[_-]?key|request[_-]?body|response[_-]?body)",
    re.IGNORECASE,
)

_PROVENANCE_TYPES = ("repo_revision", "evidence_identity", "runtime_observation")


class RetentionError(ValueError):
    """A retention inventory is missing, malformed, or unapproved."""


@dataclass(frozen=True)
class RetentionEntry:
    """One reviewed retention inventory entry (handoff schema, Decision 9)."""

    path: str
    retention_class: str
    policy_state: str
    owner: str
    provenance: Mapping[str, Any]
    justification: str
    last_reference: str
    candidate: bool
    review: Mapping[str, Any]

    @property
    def protected(self) -> bool:
        """Protected class or PROTECTED state — both are exclusion lists."""
        return (
            self.retention_class in PROTECTED_CLASSES
            or self.policy_state == "PROTECTED"
        )

    def effective_state(self) -> str:
        """Policy state after fail-closed downgrades.

        Missing provenance or missing owner downgrades the entry to
        ``REVIEW_REQUIRED``; protection is never downgraded.
        """
        if self.protected:
            return "PROTECTED"
        if not _provenance_bound(self.provenance) or not self.owner:
            return "REVIEW_REQUIRED"
        return self.policy_state


def _provenance_bound(provenance: Mapping[str, Any]) -> bool:
    """True when provenance binds to a revision, evidence id, or observation."""
    ptype = provenance.get("type")
    if ptype not in _PROVENANCE_TYPES:
        return False
    if ptype == "repo_revision":
        return bool(provenance.get("revision"))
    if ptype == "evidence_identity":
        return bool(provenance.get("evidence"))
    return bool(provenance.get("observed_at"))


def _reject_secret_fields(node: Any, where: str = "$") -> None:
    if isinstance(node, Mapping):
        for key, value in node.items():
            if _SECRET_FIELD_PATTERN.search(str(key)):
                raise RetentionError(
                    f"credential-shaped field '{where}.{key}' is not permitted"
                )
            _reject_secret_fields(value, f"{where}.{key}")
    elif isinstance(node, list):
        for index, value in enumerate(node):
            _reject_secret_fields(value, f"{where}[{index}]")


@dataclass(frozen=True)
class RetentionInventory:
    """A validated retention inventory document."""

    policy: str
    policy_version: str
    policy_identity: str
    approval: Mapping[str, Any]
    generated_at: str
    entries: tuple  # RetentionEntry
    source_path: str

    def entry_for(self, canonical_path: str) -> Optional[RetentionEntry]:
        for entry in self.entries:
            if entry.path == canonical_path:
                return entry
        return None


def load_inventory(path: Optional[Path] = None) -> RetentionInventory:
    """Load and validate the retention inventory. Raises RetentionError."""
    source = Path(path) if path is not None else DEFAULT_INVENTORY_PATH
    if not source.is_file():
        raise RetentionError(f"retention inventory not found: {source}")
    try:
        document = json.loads(source.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RetentionError(f"retention inventory unreadable: {exc}") from exc
    if not isinstance(document, Mapping):
        raise RetentionError("retention inventory must be a JSON object")

    _reject_secret_fields(document)

    policy = document.get("policy")
    if policy != POLICY_NAME:
        raise RetentionError(
            f"retention inventory policy identity missing or unexpected: {policy!r}"
        )
    policy_version = document.get("policy_version")
    policy_identity = document.get("policy_identity")
    if not policy_version or not policy_identity:
        raise RetentionError("retention inventory is missing policy identity fields")

    approval = document.get("approval")
    if not isinstance(approval, Mapping) or approval.get("approved") is not True:
        raise RetentionError("retention inventory is not approved")

    generated_at = document.get("generated_at")
    if not generated_at:
        raise RetentionError("retention inventory is missing generated_at")

    raw_entries = document.get("entries")
    if not isinstance(raw_entries, list):
        raise RetentionError("retention inventory is missing entries list")

    entries = []
    for index, raw in enumerate(raw_entries):
        if not isinstance(raw, Mapping):
            raise RetentionError(f"entry {index} is not an object")
        entry_path = raw.get("path")
        if not entry_path:
            raise RetentionError(f"entry {index} is missing path identity")
        retention_class = raw.get("class")
        if retention_class not in RETENTION_CLASSES:
            raise RetentionError(
                f"entry {index} has unknown retention class: {retention_class!r}"
            )
        policy_state = raw.get("policy_state")
        if policy_state not in POLICY_STATES:
            raise RetentionError(
                f"entry {index} has unknown policy state: {policy_state!r}"
            )
        provenance = raw.get("provenance")
        if not isinstance(provenance, Mapping):
            raise RetentionError(f"entry {index} is missing provenance")
        entries.append(
            RetentionEntry(
                path=str(entry_path),
                retention_class=str(retention_class),
                policy_state=str(policy_state),
                owner=str(raw.get("owner") or ""),
                provenance=provenance,
                justification=str(raw.get("justification") or ""),
                last_reference=str(raw.get("last_reference") or ""),
                candidate=bool(raw.get("candidate", False)),
                review=raw.get("review") or {},
            )
        )

    return RetentionInventory(
        policy=str(policy),
        policy_version=str(policy_version),
        policy_identity=str(policy_identity),
        approval=approval,
        generated_at=str(generated_at),
        entries=tuple(entries),
        source_path=str(source),
    )


def load_or_unavailable(path: Optional[Path] = None) -> Optional[RetentionInventory]:
    """Load the inventory; return None when unavailable (fail-closed input)."""
    try:
        return load_inventory(path)
    except RetentionError:
        return None


# Gate outcomes for a lifecycle candidate path.
EXCLUDED_PROTECTED = "excluded_protected"
REVIEW_ONLY_CANDIDATE = "review_only_candidate"
REVIEW_REQUIRED = "review_required"
NOT_GOVERNED = "not_governed"
UNAVAILABLE = "unavailable"


@dataclass(frozen=True)
class GateDecision:
    outcome: str
    reason: str
    entry: Optional[RetentionEntry] = None


def gate(inventory: Optional[RetentionInventory], canonical_path: str) -> GateDecision:
    """Apply the retention exclusion/gating layer to one candidate path.

    - Missing/unapproved/malformed inventory -> UNAVAILABLE (fail closed).
    - Protected class or state -> EXCLUDED_PROTECTED (never a candidate).
    - RECLAIMABLE candidate entry -> REVIEW_ONLY_CANDIDATE (review-only
      proposal, never an approved deletion target).
    - REVIEW_REQUIRED (including downgraded) entries -> REVIEW_REQUIRED.
    - No entry for the path -> NOT_GOVERNED (lifecycle authorities decide).
    """
    if inventory is None:
        return GateDecision(
            UNAVAILABLE,
            "retention inventory unavailable; artifact reclaimability blocked",
        )
    entry = inventory.entry_for(canonical_path)
    if entry is None:
        return GateDecision(NOT_GOVERNED, "no retention entry for path")
    if entry.protected:
        return GateDecision(
            EXCLUDED_PROTECTED,
            f"retention_protected_class:{entry.retention_class} owner:{entry.owner or 'UNKNOWN'}",
            entry,
        )
    state = entry.effective_state()
    if state == "REVIEW_REQUIRED":
        return GateDecision(
            REVIEW_REQUIRED,
            f"retention_review_required class:{entry.retention_class}",
            entry,
        )
    if state == "RECLAIMABLE":
        if entry.candidate:
            return GateDecision(
                REVIEW_ONLY_CANDIDATE,
                f"retention_candidate_review_only class:{entry.retention_class}",
                entry,
            )
        return GateDecision(
            REVIEW_REQUIRED,
            f"retention_reclaimable_without_candidate_flag class:{entry.retention_class}",
            entry,
        )
    # RECLAIMED: an approved retirement already superseded the retention record.
    return GateDecision(
        NOT_GOVERNED,
        "retention_state_reclaimed; approved retirement already recorded",
        entry,
    )
