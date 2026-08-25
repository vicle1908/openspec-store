## Context

The workspace has independent authorities for OpenSpec changes, Git repositories, Orca-managed worktrees, and runtime/index processes. Existing index-freshness contracts already define the approved repository inventory and generated Graphify/GitNexus ownership; this design consumes those signals and adds lifecycle retirement gates without changing index refresh behavior.

The observed topology is not transactional: Orca can retain terminals after Git reports a merged branch, OpenSpec can contain an untracked archive move, and a repository can have unpushed commits with no remote backup. The design therefore treats cleanup as a resumable, evidence-backed state machine rather than a filesystem sweep.

## Goals / Non-Goals

**Goals:**

- Normalize Git, Orca, OpenSpec, and runtime observations into stable path/worktree records.
- Make protection precedence deterministic and fail closed when an authority is unavailable.
- Produce a repeatable dry-run manifest that can be reviewed before any mutation.
- Separate classification from retirement so a stale result cannot directly trigger deletion.
- Make partial retirement recoverable and auditable across non-atomic ownership boundaries.

**Non-Goals:**

- Replacing Orca's workspace or terminal lifecycle.
- Replacing Git's branch/worktree implementation.
- Reimplementing OpenSpec archive or validation semantics.
- Refreshing or repairing Graphify/GitNexus indexes.
- Automatically deleting anything in the first version.

## Decisions

### 1. Use authority-specific adapters

Implement narrow read-only adapters for:

- OpenSpec: store selection, active changes, task completion, archive paths, and untracked change detection.
- Git: repository identity, worktree records, branch/detached revision, status, ancestry, remote reachability, and generated-only dirt classification.
- Orca: managed worktree identity, workspace status, host activity, terminals, PTYs, and agents.
- Runtime: bounded process/LaunchAgent/container/index-watcher ownership checks, returning `UNKNOWN` when unavailable.

Adapters emit observations, not classifications. This keeps authority facts separate from policy and avoids hiding conflicts.

### 2. Apply a strict classification precedence

Classification SHALL use the following order:

```text
PROTECTED
  active OpenSpec / untracked work / live Orca / active runtime / persistent state
      ↓
REVIEW_REQUIRED
  unknown owner / detached unique revision / squash ambiguity / unpushed history
      ↓
RECLAIMABLE
  preservation proven, no owner activity, no non-generated dirt
      ↓
RECLAIMED
  only after an approved lifecycle transition is recorded
```

A more restrictive observation always wins. `UNKNOWN` is not converted to `RECLAIMABLE`.

### 3. Separate plan and apply records

The dry-run manifest is immutable for the observation window and contains canonical path, repository/worktree identity, evidence timestamps, classification, blockers, and proposed owner action. An approved retirement record references the exact plan identity and requires a fresh pre-action observation; stale plans cannot be applied.

No credentials, request bodies, response bodies, or secret values enter either record.

### 4. Preserve lifecycle transaction boundaries

Retirement is a sequence of independently verifiable transitions:

1. Orca reports no live session, agent, terminal, PTY, or host activity.
2. Git worktree removal succeeds and the path is absent from Git's worktree registry.
3. Branch deletion is attempted only after the worktree transition is recorded.
4. OpenSpec paths are handled only by OpenSpec lifecycle commands and their own validation/commit process.

If a transition fails, the record remains `REVIEW_REQUIRED` with the completed and pending transitions; the workflow does not compensate by deleting the path directly.

### 5. Reuse existing workspace index ownership and consume the retention inventory

The approved repository inventory and `knowledge-status.sh --json` remain the source for Graphify/GitNexus freshness and operation status. Generated-only changes may be reported as generated noise only when the existing ownership metadata proves that classification; the cleanup workflow SHALL never invoke index mutation. The reviewed retention inventory from `workspace-artifact-retention-policy` is the artifact-protection source: protected retention classes SHALL be exclusions for lifecycle classification, and `RECLAIMABLE` candidate artifacts SHALL remain review-only proposals.

Retention handoff contract (shared verbatim with `workspace-artifact-retention-policy` design Decision 9): the required input is the operational inventory document at `~/Developer/.workspace-retention/retention-inventory.json` — top-level `policy` (fixed value `workspace-artifact-retention-policy`), `policy_version`, `policy_identity`, `approval` (`approved`, `digest`, `approved_at`, `approved_by`), `generated_at`, and `entries`. Each entry carries `path`, `class`, `policy_state`, `owner`, `provenance` (`type` is `repo_revision` | `evidence_identity` | `runtime_observation` with `revision`/`evidence`/`observed_at`), `justification`, `last_reference`, `candidate`, and `review`. The policy-state vocabulary is exactly `PROTECTED`, `REVIEW_REQUIRED`, `RECLAIMABLE`, `RECLAIMED`. The eight retention classes are exactly: active index state, generated index or cache, tracked permanent fixture, temporary or ephemeral test fixture, runtime state or database, retained evidence or report, retained rollback or snapshot, operator-owned preserved file; the six protected classes are all except the two candidate classes (generated index or cache, temporary or ephemeral test fixture). The lifecycle consumer reads `entries`, treats `PROTECTED` classes and states as exclusion lists, treats `RECLAIMABLE` candidate artifacts as review-only proposals, downgrades entries with missing provenance or owner to `REVIEW_REQUIRED`, and fails closed (blocks artifact reclaimability) when the inventory is missing, malformed, or unapproved.

### 6. Prefer explicit evidence over age heuristics

Age and naming patterns are candidate hints only. A `*-deploy-source-*` path can be reclaimable after ancestry and runtime checks, while a similarly old `*-repair-*` worktree can contain unique work. The manifest records the proof used for each result.

### 7. Implementation surface and owning repository

The `openspec-store` repository owns the implementation. Cross-repository workspace tooling already lives under `openspec-store/scripts/` (`knowledge-refresh/`, `sync-workspace-agent-skills.py`, `validate-archive-readiness.py`), and Decision B keeps cross-repository runtime state outside the store checkout.

- Implementation surface: `~/Developer/openspec-store/scripts/workspace-lifecycle/` — a versioned tool directory beside `scripts/knowledge-refresh/` with a `tests/` subdirectory containing `fixtures/` (mirroring `scripts/knowledge-refresh/tests/`). The inventory builder, authority adapters (OpenSpec, Git, Orca, runtime/index), manifest writer, and retirement transition recorder are implemented here. No adapter issues mutation commands.
- Runtime state: `~/Developer/.workspace-lifecycle/` — the workspace-state directory for dry-run manifests, approval records, and retirement transition records, following the `~/Developer/.workspace-retention/` and `~/Developer/.knowledge-refresh/` convention.
- Entry command: `python3 ~/Developer/openspec-store/scripts/workspace-lifecycle/workspace-lifecycle.py`. The default mode is the read-only dry-run scan, which writes only manifests under `~/Developer/.workspace-lifecycle/`.

Concrete read-only inputs:

- OpenSpec authority: `openspec` CLI pinned to the store (`openspec list --store openspec-store --json`, `openspec status --change <name> --store openspec-store --json`) plus `git -C ~/Developer/openspec-store status --porcelain` for untracked change and archive directories.
- Git authority: read-only `git -C <repo>` queries (`worktree list`, `status --porcelain`, `rev-parse`, `merge-base --is-ancestor`, `branch --contains`, `log`) against repositories listed in the reviewed inventory.
- Orca authority: read-only `orca` CLI queries for managed worktrees, workspace status, terminals, attached PTYs, pins, agents, and host activity.
- Index/freshness authority: `bash ~/Developer/scripts/knowledge-refresh/knowledge-status.sh --json`, which self-describes its inventory path and digest in its output. The reviewed repository inventory is versioned at `~/Developer/openspec-store/scripts/knowledge-refresh/knowledge-refresh-inventory.tsv`. The lifecycle tool reads these outputs and SHALL NOT invoke `refresh-knowledge-indexes.sh`, `graphify`, or `gitnexus`.
- Retention authority: `~/Developer/.workspace-retention/retention-inventory.json`, the required policy input produced by `workspace-artifact-retention-policy` (see Decision 5).

## Risks / Trade-offs

- Multiple adapters increase implementation surface, but a single Git-only view is demonstrably unsafe in this workspace.
- A strict `UNKNOWN → REVIEW_REQUIRED` rule produces false positives when Orca or runtime APIs are unavailable, but avoids irreversible data loss.
- Two-phase plan/apply requires a second observation and operator action, trading speed for stale-plan protection.
- Generated-only dirt classification depends on existing index ownership metadata; uncertain generated output remains review-required.
- Branch deletion after worktree removal can leave orphaned branches when the final step fails; the audit record makes retry explicit and safe.

## Open Questions (Resolved for Initial Design)

### A. Operator approval record

Initial behavior: approval is a human-signed local lifecycle command invocation or a documented review message associated with the manifest identity. No single authoritative approval database exists today, so the system records operator intent inline and refuses apply without an approval note attached to the exact plan id.

### B. Manifest storage

Initial behavior: store the workspace cleanup manifest and retirement record under a workspace-state directory rather than the OpenSpec store, because cleanup scope is cross-repo and not owned by any single spec change.

### C. Runtime adapter scope

Initial behavior: process, workspace, and watcher ownership are best-effort lookup adapters. Container and LaunchAgent coverage is optional and versioned. When a required adapter is unavailable or uncertain, the workflow SHALL record `UNKNOWN` and SHALL fail closed toward `REVIEW_REQUIRED`.

### D. Orca hierarchy and pinned state

Orca `isPinned=true`, a live child worktree, an unresolved orphaned terminal, or an agent in `working`/`interrupted` state is a protection signal. Child worktrees SHALL be retired before parents; Orca file-handle/workspace state SHALL be released before Git worktree removal. Paths under the Orca-managed root are not disposable merely because Git reports them merged.
