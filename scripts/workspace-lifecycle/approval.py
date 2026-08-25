"""Operator approval gating for workspace lifecycle retirement.

Task 2.3 contract: operator approval is recorded against the exact plan
identity, and applying it requires a fresh pre-action observation. Stale or
mismatched approvals are rejected before any lifecycle mutation. Design
Decision A: approval is a documented review note tied to the manifest
identity; Decision 3: approved retirement references the exact plan identity
and stale plans cannot be applied.

This module records and validates approval documents and pre-action
observations. It never performs or authorizes direct deletion: a valid
approval only enables the ordered retirement transition recording owned by
task 3.3, which itself remains non-mutating in the first version.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import timedelta
from pathlib import Path
from typing import Mapping, Optional

import classify
import retention
from observations import PathRecord, parse_observed_at

DEFAULT_MAX_PRE_ACTION_AGE_MINUTES = 15
DEFAULT_MAX_PLAN_AGE_HOURS = 24
MAX_FUTURE_SKEW_MINUTES = 5

_SECRET_FIELD_PATTERN = re.compile(
    r"(password|passwd|secret|token|api[_-]?key|credential|authorization|"
    r"private[_-]?key|request[_-]?body|response[_-]?body)",
    re.IGNORECASE,
)


class ApprovalError(ValueError):
    """An approval record is malformed or carries secret fields."""


@dataclass(frozen=True)
class ApprovalRecord:
    """Operator intent bound to one exact plan identity."""

    plan_id: str
    plan_identity: str
    operator: str
    approval_note: str
    approved_at: str
    paths: tuple  # canonical paths approved for retirement review

    def to_document(self) -> dict:
        return {
            "record": "workspace-lifecycle-approval",
            "plan_id": self.plan_id,
            "plan_identity": self.plan_identity,
            "operator": self.operator,
            "approval_note": self.approval_note,
            "approved_at": self.approved_at,
            "paths": list(self.paths),
        }


@dataclass(frozen=True)
class Authorization:
    authorized: bool
    rejections: tuple
    approved_paths: tuple


def _reject_secret_fields(node, where: str = "$") -> None:
    if isinstance(node, Mapping):
        for key, value in node.items():
            if _SECRET_FIELD_PATTERN.search(str(key)):
                raise ApprovalError(
                    f"credential-shaped field '{where}.{key}' is not permitted"
                )
            _reject_secret_fields(value, f"{where}.{key}")
    elif isinstance(node, list):
        for index, value in enumerate(node):
            _reject_secret_fields(value, f"{where}[{index}]")


def make_approval(
    plan_id: str,
    plan_identity: str,
    operator: str,
    approval_note: str,
    approved_at: str,
    paths,
) -> ApprovalRecord:
    if not plan_id or not plan_identity:
        raise ApprovalError("approval requires exact plan id and plan identity")
    if not operator or not str(operator).strip():
        raise ApprovalError("approval requires an operator identity")
    if not approval_note or not str(approval_note).strip():
        raise ApprovalError("approval requires a documented review note")
    parse_observed_at(approved_at)
    path_tuple = tuple(str(p) for p in paths)
    if not path_tuple:
        raise ApprovalError("approval requires at least one approved path")
    record = ApprovalRecord(
        plan_id=str(plan_id),
        plan_identity=str(plan_identity),
        operator=str(operator),
        approval_note=str(approval_note),
        approved_at=str(approved_at),
        paths=path_tuple,
    )
    _reject_secret_fields(record.to_document())
    return record


def record_approval(record: ApprovalRecord, record_dir: Path) -> Path:
    """Persist the approval record in the scoped state directory (read-only
    toward everything else). Deterministic serialization."""
    record_dir = Path(record_dir)
    record_dir.mkdir(parents=True, exist_ok=True)
    path = record_dir / f"approval-{record.plan_id}.json"
    path.write_text(
        json.dumps(record.to_document(), sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    return path


def load_approval(path: Path) -> ApprovalRecord:
    document = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(document, Mapping) or document.get("record") != "workspace-lifecycle-approval":
        raise ApprovalError("not a workspace lifecycle approval record")
    _reject_secret_fields(document)
    for key in ("plan_id", "plan_identity", "operator", "approval_note",
                "approved_at", "paths"):
        if not document.get(key):
            raise ApprovalError(f"approval record missing {key}")
    return ApprovalRecord(
        plan_id=str(document["plan_id"]),
        plan_identity=str(document["plan_identity"]),
        operator=str(document["operator"]),
        approval_note=str(document["approval_note"]),
        approved_at=str(document["approved_at"]),
        paths=tuple(str(p) for p in document["paths"]),
    )


def validate_approval(
    approval: ApprovalRecord,
    manifest: Mapping,
    pre_action_records: Mapping[str, PathRecord],
    retention_inventory: Optional[retention.RetentionInventory] = None,
    now: Optional[str] = None,
    max_pre_action_age_minutes: int = DEFAULT_MAX_PRE_ACTION_AGE_MINUTES,
    max_plan_age_hours: int = DEFAULT_MAX_PLAN_AGE_HOURS,
) -> Authorization:
    """Validate approval against the exact plan and fresh observations.

    Every rejection is determined before any lifecycle mutation could be
    considered; authorization only enables transition recording (task 3.3).
    """
    if now is None:
        raise ApprovalError("validation requires an explicit observation time")
    now_dt = parse_observed_at(now)
    rejections = []

    if approval.plan_id != manifest.get("plan_id"):
        rejections.append("plan_id_mismatch")
    if approval.plan_identity != manifest.get("plan_identity"):
        rejections.append("plan_identity_mismatch")

    generated_raw = manifest.get("generated_at")
    generated_dt = parse_observed_at(str(generated_raw)) if generated_raw else None
    approved_dt = parse_observed_at(approval.approved_at)
    skew = timedelta(minutes=MAX_FUTURE_SKEW_MINUTES)
    if approved_dt > now_dt + skew:
        rejections.append("approval_in_future")
    if generated_dt is not None:
        if approved_dt < generated_dt:
            rejections.append("approval_predates_plan")
        if now_dt - generated_dt > timedelta(hours=max_plan_age_hours):
            rejections.append("stale_plan")

    entries_by_path = {
        entry.get("canonical_path"): entry for entry in manifest.get("entries") or []
    }
    pre_action_window = timedelta(minutes=max_pre_action_age_minutes)
    approved_paths = []

    for path in approval.paths:
        entry = entries_by_path.get(path)
        if entry is None:
            rejections.append(f"path_not_in_plan:{path}")
            continue
        if entry.get("classification") != "RECLAIMABLE":
            rejections.append(f"path_not_reclaimable:{path}")
            continue
        record = pre_action_records.get(path)
        if record is None or not record.observations:
            rejections.append(f"missing_pre_action_observation:{path}")
            continue
        fresh = True
        for obs in record.observations:
            observed_dt = parse_observed_at(obs.observed_at)
            if observed_dt > now_dt + skew or now_dt - observed_dt > pre_action_window:
                fresh = False
                break
        if not fresh:
            rejections.append(f"stale_pre_action_observation:{path}")
            continue
        result = classify.classify_path(record, retention_inventory)
        if result.classification != "RECLAIMABLE":
            rejections.append(
                f"pre_action_state_changed:{path}:{result.classification}"
            )
            continue
        approved_paths.append(path)

    return Authorization(
        authorized=not rejections,
        rejections=tuple(rejections),
        approved_paths=tuple(approved_paths),
    )
