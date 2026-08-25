"""Machine-readable cleanup manifest for workspace lifecycle cleanup.

Task 2.1 contract: the dry-run manifest carries path identity, authority
observations, classification, blockers, evidence timestamps, proposed owner
action, and secret-redaction rules. Design Decision 3: the manifest is
immutable for the observation window; no credentials, request bodies,
response bodies, or secret values enter the record.

Validation rejects:

- missing identity (plan id, canonical path, observation subject),
- stale evidence (observations older than the evidence window relative to
  the manifest generation time, or missing timestamps),
- credential-shaped fields anywhere in the document.

Redaction strips secret-shaped keys from observation facts while retaining
non-secret owner, endpoint, and classification metadata.

This module is read-only: it builds and validates manifest documents in memory
and never mutates workspace state.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Iterable, Mapping, Optional

import retention
from observations import AUTHORITIES, Observation, parse_observed_at

MANIFEST_NAME = "workspace-lifecycle-cleanup-manifest"
SCHEMA_VERSION = "0.1.0"
CLASSIFICATIONS = ("PROTECTED", "REVIEW_REQUIRED", "RECLAIMABLE", "RECLAIMED")

DEFAULT_MAX_EVIDENCE_AGE_HOURS = 24
MAX_FUTURE_SKEW_MINUTES = 5

_SECRET_FIELD_PATTERN = re.compile(
    r"(password|passwd|secret|token|api[_-]?key|credential|authorization|"
    r"private[_-]?key|request[_-]?body|response[_-]?body)",
    re.IGNORECASE,
)

# Proposed owner actions never include deletion; retirement stays a separate
# approved lifecycle operation (design Decision 4).
_ACTION_REVIEW = "review"
_ACTION_PROPOSE_RETIREMENT_REVIEW = "propose_retirement_review"
_ACTION_NONE = "none"
_ACTION_RECORDED = "recorded_retirement_transition"


class ManifestError(ValueError):
    """A cleanup manifest is malformed, stale, or carries secret fields."""


def redact_facts(facts: Mapping[str, Any]) -> dict:
    """Strip secret-shaped keys; keep owner/endpoint/classification metadata."""
    redacted = {}
    for key, value in facts.items():
        if _SECRET_FIELD_PATTERN.search(str(key)):
            continue
        if isinstance(value, Mapping):
            redacted[key] = redact_facts(value)
        else:
            redacted[key] = value
    return redacted


def redact_observation(observation: Observation) -> dict:
    return {
        "authority": observation.authority,
        "subject": observation.subject,
        "observed_at": observation.observed_at,
        "facts": redact_facts(observation.facts),
    }


def _reject_secret_fields(node: Any, where: str = "$") -> None:
    if isinstance(node, Mapping):
        for key, value in node.items():
            if _SECRET_FIELD_PATTERN.search(str(key)):
                raise ManifestError(
                    f"credential-shaped field '{where}.{key}' is not permitted"
                )
            _reject_secret_fields(value, f"{where}.{key}")
    elif isinstance(node, list):
        for index, value in enumerate(node):
            _reject_secret_fields(value, f"{where}[{index}]")


def propose_owner_action(classification: str, observations: Iterable[Observation]) -> dict:
    """Name the owning authority and the proposed (non-deletion) action."""
    authorities = {obs.authority for obs in observations}
    if classification == "PROTECTED":
        return {"owner": "operator", "action": _ACTION_NONE,
                "note": "protected; no cleanup action proposed"}
    if classification == "REVIEW_REQUIRED":
        return {"owner": "operator", "action": _ACTION_REVIEW,
                "note": "operator review required before any lifecycle action"}
    if classification == "RECLAIMED":
        return {"owner": "lifecycle-recorder", "action": _ACTION_RECORDED,
                "note": "approved transition already recorded"}
    # RECLAIMABLE: propose retirement review to the owning lifecycle tool.
    if "orca" in authorities:
        owner = "orca"
    elif "openspec" in authorities:
        owner = "openspec"
    elif "git" in authorities:
        owner = "git"
    else:
        owner = "operator"
    return {"owner": owner, "action": _ACTION_PROPOSE_RETIREMENT_REVIEW,
            "note": "review-only proposal; deletion requires approved action"}


def _path_identity(observations: Iterable[Observation]) -> dict:
    identity = {
        "repo_identity": None,
        "worktree_id": None,
        "branch": None,
        "revision": None,
        "detached": None,
    }
    for obs in observations:
        if obs.authority == "git":
            for key in ("repo_identity", "worktree_id", "branch", "revision", "detached"):
                if identity[key] is None and key in obs.facts:
                    identity[key] = obs.facts[key]
    return identity


def build_entry(
    canonical_path: str,
    observations: Iterable[Observation],
    classification: str,
    blockers: Iterable[str],
    evidence: Iterable[str],
    generated_at: str,
) -> dict:
    """Build one redacted manifest entry."""
    if classification not in CLASSIFICATIONS:
        raise ManifestError(f"unknown classification: {classification!r}")
    if not canonical_path or not os.path.isabs(canonical_path):
        raise ManifestError(
            f"manifest entry requires absolute canonical path: {canonical_path!r}"
        )
    observation_list = [redact_observation(obs) for obs in observations]
    timestamps = [obs["observed_at"] for obs in observation_list]
    return {
        "canonical_path": canonical_path,
        "identity": _path_identity(list(observations)),
        "observations": observation_list,
        "classification": classification,
        "blockers": list(blockers),
        "evidence": list(evidence),
        "evidence_timestamps": {
            "generated_at": generated_at,
            "oldest_observation": min(timestamps) if timestamps else None,
            "newest_observation": max(timestamps) if timestamps else None,
        },
        "proposed_owner_action": propose_owner_action(classification, observations),
        "previously_skipped": False,
    }


def build_manifest(
    plan_id: str,
    entries: Iterable[Mapping[str, Any]],
    generated_at: str,
    retention_inventory: Optional[retention.RetentionInventory] = None,
    workspace_root: str = "~/Developer",
) -> dict:
    """Assemble the dry-run manifest document (in memory, read-only)."""
    if not plan_id:
        raise ManifestError("manifest requires a plan id")
    parse_observed_at(generated_at)
    entry_list = list(entries)
    manifest = {
        "manifest": MANIFEST_NAME,
        "schema_version": SCHEMA_VERSION,
        "plan_id": plan_id,
        "plan_identity": plan_identity(entry_list),
        "generated_at": generated_at,
        "workspace_root": workspace_root,
        "mode": "dry-run",
        "retention_policy": (
            {
                "available": True,
                "policy": retention_inventory.policy,
                "policy_identity": retention_inventory.policy_identity,
                "source_path": retention_inventory.source_path,
            }
            if retention_inventory is not None
            else {"available": False}
        ),
        "entries": entry_list,
    }
    validate_manifest(manifest)
    return manifest


def plan_identity(entries: Iterable[Mapping[str, Any]]) -> str:
    """Stable digest over the decision-relevant entry content.

    Excludes generated_at so repeated scans of unchanged state produce the
    same plan identity (task 2.2 stable repeated-scan behavior).
    """
    normalized = []
    for entry in entries:
        normalized.append(
            {
                "canonical_path": entry.get("canonical_path"),
                "classification": entry.get("classification"),
                "blockers": sorted(entry.get("blockers") or []),
                "evidence": sorted(entry.get("evidence") or []),
                "observations": [
                    {
                        "authority": obs.get("authority"),
                        "subject": obs.get("subject"),
                        "observed_at": obs.get("observed_at"),
                    }
                    for obs in (entry.get("observations") or [])
                ],
            }
        )
    normalized.sort(key=lambda item: str(item.get("canonical_path")))
    payload = json.dumps(normalized, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def validate_manifest(
    manifest: Mapping[str, Any],
    max_evidence_age_hours: int = DEFAULT_MAX_EVIDENCE_AGE_HOURS,
) -> None:
    """Validate a manifest document. Raises ManifestError."""
    if not isinstance(manifest, Mapping):
        raise ManifestError("manifest must be an object")
    if manifest.get("manifest") != MANIFEST_NAME:
        raise ManifestError("missing or unexpected manifest identity")
    for key in ("schema_version", "plan_id", "plan_identity", "generated_at", "entries"):
        if not manifest.get(key) if key != "entries" else manifest.get(key) is None:
            raise ManifestError(f"manifest is missing {key}")

    _reject_secret_fields(manifest)

    generated_at = parse_observed_at(str(manifest["generated_at"]))
    max_age = timedelta(hours=max_evidence_age_hours)
    skew = timedelta(minutes=MAX_FUTURE_SKEW_MINUTES)

    entries = manifest["entries"]
    if not isinstance(entries, list):
        raise ManifestError("manifest entries must be a list")

    for index, entry in enumerate(entries):
        if not isinstance(entry, Mapping):
            raise ManifestError(f"entry {index} is not an object")
        path = entry.get("canonical_path")
        if not path or not os.path.isabs(str(path)):
            raise ManifestError(f"entry {index} is missing path identity")
        if not isinstance(entry.get("identity"), Mapping):
            raise ManifestError(f"entry {index} is missing identity object")
        classification = entry.get("classification")
        if classification not in CLASSIFICATIONS:
            raise ManifestError(
                f"entry {index} has unknown classification: {classification!r}"
            )
        action = entry.get("proposed_owner_action")
        if not isinstance(action, Mapping) or not action.get("owner") or not action.get("action"):
            raise ManifestError(f"entry {index} is missing proposed owner action")
        observations = entry.get("observations")
        if not isinstance(observations, list):
            raise ManifestError(f"entry {index} is missing observations list")
        for obs_index, obs in enumerate(observations):
            if not isinstance(obs, Mapping):
                raise ManifestError(f"entry {index} observation {obs_index} invalid")
            if obs.get("authority") not in AUTHORITIES:
                raise ManifestError(
                    f"entry {index} observation {obs_index} has unknown authority"
                )
            if not obs.get("subject"):
                raise ManifestError(
                    f"entry {index} observation {obs_index} is missing subject identity"
                )
            observed_raw = obs.get("observed_at")
            if not observed_raw:
                raise ManifestError(
                    f"entry {index} observation {obs_index} is missing evidence timestamp"
                )
            observed_at = parse_observed_at(str(observed_raw))
            if observed_at > generated_at + skew:
                raise ManifestError(
                    f"entry {index} observation {obs_index} timestamp is in the future"
                )
            if generated_at - observed_at > max_age:
                raise ManifestError(
                    f"entry {index} observation {obs_index} evidence is stale "
                    f"(older than {max_evidence_age_hours}h)"
                )


def mark_previously_skipped(manifest: Mapping[str, Any], prior: Mapping[str, Any]) -> dict:
    """Distinguish newly observed candidates from previously skipped ones.

    A path skipped in a prior manifest (classified PROTECTED or
    REVIEW_REQUIRED) keeps that history in the new manifest.
    """
    prior_states = {}
    for entry in prior.get("entries") or []:
        if isinstance(entry, Mapping) and entry.get("canonical_path"):
            prior_states[entry["canonical_path"]] = entry.get("classification")
    updated = json.loads(json.dumps(manifest))
    for entry in updated["entries"]:
        previous = prior_states.get(entry.get("canonical_path"))
        if previous in ("PROTECTED", "REVIEW_REQUIRED"):
            entry["previously_skipped"] = True
    return updated
