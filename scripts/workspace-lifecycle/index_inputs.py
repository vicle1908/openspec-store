"""Read-only workspace/index inventory inputs for lifecycle cleanup.

Task 1.3 contract: consume the approved repository inventory
(``knowledge-refresh-inventory.tsv``) and ``knowledge-status.sh --json``
output as read-only inputs. This module only parses provided documents; it
SHALL NOT invoke ``refresh-knowledge-indexes.sh``, ``graphify``, or
``gitnexus``, and it never mutates indexes, repositories, or files.

Skip vocabulary follows the existing ``workspace-index-freshness`` contracts:
``skipped_dirty``, ``skipped_merge_state``, ``watcher_active``,
``detached_head``, ``ephemeral_worktree``, ``stale_worktree``,
``skipped_uninitialized``, ``non_default_branch``, ``provider_disabled``.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Optional

from observations import Observation

STALE_WORKTREE_AGE_DAYS = 30
EPHEMERAL_WORKTREE_MARKER = ".claude/worktrees/"

PROVIDER_TOOLS = ("GitNexus", "Graphify")
ROW_TOOLS = ("GitNexus", "Graphify", "Dirty", "Worktree")
FRESHNESS_RULES = ("commit_equality", "missing_recorded_revision")


class IndexInputError(ValueError):
    """A workspace/index inventory input is malformed."""


@dataclass(frozen=True)
class InventoryEntry:
    """One approved repository inventory row (TSV)."""

    canonical_root: str
    default_branch: str
    gitnexus_enabled: bool
    graphify_enabled: bool

    @property
    def repo_name(self) -> str:
        return os.path.basename(self.canonical_root.rstrip("/"))

    def provider_enabled(self, provider: str) -> bool:
        if provider == "gitnexus":
            return self.gitnexus_enabled
        if provider == "graphify":
            return self.graphify_enabled
        raise IndexInputError(f"unknown provider: {provider!r}")


def load_reviewed_inventory(path: Path) -> tuple:
    """Parse the approved repository inventory TSV (read-only)."""
    source = Path(path)
    if not source.is_file():
        raise IndexInputError(f"reviewed inventory not found: {source}")
    entries = []
    for line_number, raw_line in enumerate(
        source.read_text(encoding="utf-8").splitlines(), start=1
    ):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        fields = raw_line.split("\t")
        if len(fields) != 4:
            raise IndexInputError(
                f"inventory line {line_number}: expected 4 tab-separated fields"
            )
        root, default_branch, gitnexus, graphify = (f.strip() for f in fields)
        if not os.path.isabs(root):
            raise IndexInputError(
                f"inventory line {line_number}: canonical root must be absolute: {root!r}"
            )
        if not default_branch:
            raise IndexInputError(
                f"inventory line {line_number}: missing default branch"
            )
        for flag in (gitnexus, graphify):
            if flag not in ("yes", "no"):
                raise IndexInputError(
                    f"inventory line {line_number}: enablement must be yes/no, got {flag!r}"
                )
        entries.append(
            InventoryEntry(
                canonical_root=root,
                default_branch=default_branch,
                gitnexus_enabled=gitnexus == "yes",
                graphify_enabled=graphify == "yes",
            )
        )
    if not entries:
        raise IndexInputError("reviewed inventory contains no entries")
    return tuple(entries)


@dataclass(frozen=True)
class StatusRow:
    """One row of knowledge-status.sh --json output."""

    repo: str
    tool: str
    status: str
    facts: Mapping[str, Any]


@dataclass(frozen=True)
class KnowledgeStatus:
    """Validated machine-readable knowledge index status."""

    generated: str
    inventory: str
    inventory_digest: str
    provider_versions: Mapping[str, Any]
    staleness_threshold_days: int
    rows: tuple  # StatusRow

    def provider_rows(self, repo: str) -> list:
        return [
            row
            for row in self.rows
            if row.repo == repo and row.tool in PROVIDER_TOOLS
        ]

    def is_dirty(self, repo: str) -> bool:
        return any(row.repo == repo and row.tool == "Dirty" for row in self.rows)

    def dirty_files(self, repo: str) -> int:
        for row in self.rows:
            if row.repo == repo and row.tool == "Dirty":
                return int(row.facts.get("dirtyFiles") or 0)
        return 0

    def watcher_active(self, repo: str) -> bool:
        return any(
            row.repo == repo and row.tool == "Graphify" and row.status == "WATCHER"
            for row in self.rows
        )

    def worktrees(self, repo: str) -> list:
        return [
            (str(row.facts.get("worktree")), str(row.facts.get("worktreeBranch")))
            for row in self.rows
            if row.repo == repo and row.tool == "Worktree"
        ]


def parse_knowledge_status(document: Mapping[str, Any]) -> KnowledgeStatus:
    """Validate ``knowledge-status.sh --json`` output (read-only)."""
    if isinstance(document, (str, bytes)):
        try:
            document = json.loads(document)
        except json.JSONDecodeError as exc:
            raise IndexInputError(f"knowledge status is not valid JSON: {exc}") from exc
    if not isinstance(document, Mapping):
        raise IndexInputError("knowledge status must be a JSON object")

    required = ("generated", "inventory", "inventoryDigest", "providerVersions",
                "stalenessThresholdDays", "repos")
    for key in required:
        if key not in document:
            raise IndexInputError(f"knowledge status missing field: {key}")

    rows_raw = document["repos"]
    if not isinstance(rows_raw, list):
        raise IndexInputError("knowledge status repos must be a list")

    rows = []
    for index, raw in enumerate(rows_raw):
        if not isinstance(raw, Mapping):
            raise IndexInputError(f"knowledge status row {index} is not an object")
        repo = raw.get("repo")
        tool = raw.get("tool")
        status = raw.get("status")
        if not repo or tool not in ROW_TOOLS or not status:
            raise IndexInputError(
                f"knowledge status row {index} missing repo/tool/status"
            )
        if tool in PROVIDER_TOOLS:
            rule = raw.get("freshnessRule")
            if rule not in FRESHNESS_RULES:
                raise IndexInputError(
                    f"knowledge status row {index} has invalid freshnessRule: {rule!r}"
                )
        if tool == "Dirty" and not isinstance(raw.get("dirtyFiles"), int):
            raise IndexInputError(
                f"knowledge status row {index} Dirty row needs integer dirtyFiles"
            )
        if tool == "Worktree" and not raw.get("worktree"):
            raise IndexInputError(
                f"knowledge status row {index} Worktree row needs worktree path"
            )
        rows.append(StatusRow(repo=str(repo), tool=str(tool), status=str(status), facts=raw))

    return KnowledgeStatus(
        generated=str(document["generated"]),
        inventory=str(document["inventory"]),
        inventory_digest=str(document["inventoryDigest"]),
        provider_versions=document["providerVersions"],
        staleness_threshold_days=int(document["stalenessThresholdDays"]),
        rows=tuple(rows),
    )


@dataclass(frozen=True)
class IndexTarget:
    """A candidate index-operation target (repo checkout or worktree)."""

    path: str
    provider: str  # "gitnexus" | "graphify"
    branch: str = ""
    detached: bool = False
    branch_age_days: int = 0
    has_index_state: bool = True
    in_merge_state: bool = False


@dataclass(frozen=True)
class TargetDecision:
    eligible: bool
    skip_reason: Optional[str]


def classify_index_target(
    entry: InventoryEntry,
    status: KnowledgeStatus,
    target: IndexTarget,
    context: str = "nightly",
) -> TargetDecision:
    """Decide eligibility of an index target under existing contracts.

    Read-only mirror of the workspace-index-freshness skip rules; it never
    performs the operation itself. ``context`` is ``nightly`` (scheduled
    refresh) or ``dispatch`` (local post-merge dispatch, default branch only).
    """
    if context not in ("nightly", "dispatch"):
        raise IndexInputError(f"unknown context: {context!r}")
    repo = entry.repo_name

    if not entry.provider_enabled(target.provider):
        return TargetDecision(False, "provider_disabled")
    if target.in_merge_state:
        return TargetDecision(False, "skipped_merge_state")
    if status.is_dirty(repo):
        return TargetDecision(False, "skipped_dirty")
    if target.detached:
        return TargetDecision(False, "detached_head")
    if EPHEMERAL_WORKTREE_MARKER in target.path:
        return TargetDecision(False, "ephemeral_worktree")
    if target.branch_age_days > STALE_WORKTREE_AGE_DAYS:
        return TargetDecision(False, "stale_worktree")
    if (
        context == "dispatch"
        and target.branch
        and target.branch != entry.default_branch
    ):
        return TargetDecision(False, "non_default_branch")
    if target.provider == "graphify" and status.watcher_active(repo):
        return TargetDecision(False, "watcher_active")
    if not target.has_index_state:
        return TargetDecision(False, "skipped_uninitialized")
    return TargetDecision(True, None)


def build_index_observations(
    inventory: Iterable[InventoryEntry], status: KnowledgeStatus
) -> list:
    """Convert status rows into read-only index-authority observations."""
    observations = []
    for entry in inventory:
        for row in status.provider_rows(entry.repo_name):
            observations.append(
                Observation(
                    authority="index",
                    canonical_path=entry.canonical_root,
                    subject=row.tool.lower(),
                    observed_at=status.generated,
                    facts={
                        "provider": row.tool.lower(),
                        "freshness": str(row.facts.get("freshness") or row.status),
                        "freshness_rule": str(row.facts.get("freshnessRule") or ""),
                        "watcher_active": row.status == "WATCHER",
                        "indexed_sha": str(row.facts.get("indexedSha") or ""),
                        "head_sha": str(row.facts.get("headSha") or ""),
                        "dirty": status.is_dirty(entry.repo_name),
                        "dirty_files": status.dirty_files(entry.repo_name),
                    },
                )
            )
    return observations
