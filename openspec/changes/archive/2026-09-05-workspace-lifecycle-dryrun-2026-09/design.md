## Context

The `workspace-lifecycle-gated-cleanup` change (archived 2026-08-25) built `openspec-store/scripts/workspace-lifecycle/`: a read-only dry-run tool that consumes authority observations, correlates them per canonical path, applies the approved retention inventory (`~/Developer/.workspace-retention/retention-inventory.json`) as an exclusion layer, and classifies every path as PROTECTED / REVIEW_REQUIRED / RECLAIMABLE. Its acceptance run used fixture observations only. Post-`ecosystem-cleanup` research found real candidates the tool was built to judge: orphaned orca checkouts under `~/orca/workspaces/agent-core/`, root-level junk, empty dirs, the `review-hermes-cron` evidence worktree, and `tdt/` runtime copies.

## Goals / Non-Goals

**Goals:**
- Exercise the lifecycle tool on real workspace state for the first time
- Produce a durable, evidence-backed classification manifest covering the discovered candidates
- Respect the retention inventory exactly: PROTECTED entries are exclusions; unknown paths stay REVIEW_REQUIRED
- Make `.claude/` untracked noise disappear from 16 repos via gitignore

**Non-Goals:**
- No deletion of any classified path (dry-run only — spec Decision 4 requires a separate approved retirement)
- No retention-inventory amendment in this change (amendments need their own review; we only record what an amendment would need)
- No `tdt/` service migration (live `com.tdt.ai-review` LaunchAgent — runtime owner's change)
- No change to the lifecycle tooling itself unless a real-data bug blocks the run

## Decisions

### 1. Observation collection by hand-built JSON, not a new adapter

**Decision:** Write the observation JSON file per the task-1.1 contract (authority, canonical_path, subject, observed_at, facts) by scripting read-only queries: `git worktree list` per repo, `launchctl list` + `ps` for runtime, file listing for orca roots, `openspec list` for changes.

**Rationale:** The tool validates observation shape but ships no live collectors (adapters were fixture-driven). Building permanent adapters is tooling work beyond this change's scope; a one-shot observation file gets real data through the existing validation.

**Alternative considered:** Extend the tool with live adapters — deferred; this change proves the pipeline, a follow-up can productionize collection.

### 2. Scope observations to the research-derived candidate set

**Decision:** Observe exactly: (a) the 6 orphaned orca checkout dirs + 2 empty orca dirs, (b) root-level untracked files from research (omniroute review bundles ×6, git bundle, shell-artifact files, stale plan/context files), (c) empty workspace dirs, (d) `review-hermes-cron` worktree + branch, (e) `tdt/` tree with its live-service facts, (f) `~/.tdt/deployments` sibling for comparison.

**Rationale:** The retention inventory already protects the 14 known state paths; the manifest's value is classifying the *unclassified* residue. Whole-home scanning is out of scope and duplicates what the tool would do with a complete observation set later.

### 3. `.claude/` gitignore as a separate task group, not lifecycle classification

**Decision:** Handle the 16 repos' gitignore normalization as direct repo commits inside this change, since `.claude/` is per-session agent config explicitly documented as harmless — not a lifecycle-governed path.

**Rationale:** The retention policy governs artifacts; `.claude/` noise is repo hygiene. Conflating them would bloat the manifest with 16 trivially-fine entries.

### 4. Evidence lives in the change directory

**Decision:** The generated manifest, summary, and the observation file are copied into `openspec/changes/workspace-lifecycle-dryrun-2026-09/evidence/` at run time, then committed with the store.

**Rationale:** The `.workspace-lifecycle/` output dir is runtime state; the change archive is the durable record (mirrors `remediate-cleanup-archive-gaps`'s evidence pattern).

## Risks / Trade-offs

- **[Risk] Observation set misses a path, manifest under-classifies** → Mitigation: candidate list is derived from completed research; a final re-scan task verifies no new unclassified residue appeared.
- **[Risk] Tool rejects real observations (fixture-shape assumptions)** → Mitigation: validate against `observations.py` contract first; if a blocker bug surfaces, record it as evidence and stop — do not patch the tool in this change.
- **[Risk] gitignore commits dirty graphify hooks** → Mitigation: commit only `.gitignore` per repo, verify status clean after each.
