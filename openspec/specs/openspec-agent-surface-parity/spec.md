# openspec-agent-surface-parity Specification

## Purpose

Define how TDT-maintained OpenSpec agent workflows remain version-aligned,
invocation-consistent, and safe for apply, sync, and archive operations across
the workspace.

## Requirements

### Requirement: TDT skills use one reviewed OpenSpec release contract

All OpenSpec workflow `SKILL.md` files across active `platform/openspec-store` adapter trees (`.agents/skills`, `.claude/skills`, `.factory/skills`, `.junie/skills`, `.kilocode/skills`, `.kiro/skills`, `.pi/skills`, `.qoder/skills`) SHALL derive from the same installed official OpenSpec CLI release (`1.17.0` or newer) and SHALL record matching `metadata.generatedBy` provenance.

#### Scenario: Complete skill set is refreshed
- **WHEN** the OpenSpec agent surface in `platform/openspec-store` is prepared for activation
- **THEN** all 12 canonical OpenSpec skills across all 8 active adapter trees (96 `SKILL.md` files) SHALL match the installed `1.17.0+` workflow contracts and report identical `metadata.generatedBy`
- **AND** no host-visible OpenSpec skill SHALL remain at `1.12.0` or advertise deprecated `/opsx:*` command-shim invocations

#### Scenario: Mixed version is found
- **WHEN** any OpenSpec `SKILL.md` in `platform/openspec-store` reports a stale `metadata.generatedBy` version or retains an incompatible workflow section
- **THEN** parity verification SHALL fail and agent-driven apply, sync, single archive, and bulk archive MUST remain gated until reconciled
### Requirement: Local overlays are explicit and non-controlling

TDT-specific safety overlays SHALL be separately identified and MUST NOT replace
or weaken CLI state, resolved paths, built-in workflow steps, artifact rules,
explicit user choices, cancellation, or failure-stop behavior.

#### Scenario: Compatible safety overlay is retained
- **WHEN** a local Git, GitNexus, secret, or repository-scope guardrail is compatible with the official workflow
- **THEN** it MAY be retained with provenance in the parity evidence
- **AND** its effect SHALL remain additive

#### Scenario: Overlay conflicts with release behavior
- **WHEN** a local instruction conflicts with a controlling 1.7 workflow input or safety stop
- **THEN** the conflicting overlay MUST be removed or escalated
- **AND** the official release behavior SHALL remain unchanged

### Requirement: Runtime inputs remain separate from workflow authority

Apply and archive workflows SHALL consume current project context and applicable
operation guidance while keeping them separate from built-in instructions, CLI
state, completion evidence, artifact rules, resolved paths, and user choices.

#### Scenario: Apply inputs are available
- **WHEN** `instructions apply` returns project context or operation guidance
- **THEN** the workflow SHALL consider applicable entries
- **AND** it MUST NOT use them as proof of task completion or permission to bypass CLI-controlled state

#### Scenario: Archive input lookup fails
- **WHEN** optional archive context/guidance lookup is unsupported or invalid
- **THEN** archive SHALL continue with no runtime input as defined by the release workflow
- **AND** the failure MUST NOT be confused with a required specs-instruction lookup failure

### Requirement: Spec sync is store-aware, scoped, and fail-closed

Agent-driven sync SHALL use `artifactPaths.specs.existingOutputPaths`, SHALL
write main specs beneath the CLI-reported `planningHome.root`, SHALL honor an
explicit caller subset, and SHALL obtain one valid specs-instruction snapshot
before writing.

#### Scenario: Caller narrows delta paths
- **WHEN** archive or the user supplies a subset of declared delta paths
- **THEN** sync SHALL process only that subset
- **AND** it MUST NOT widen selection to other deltas

#### Scenario: Required instruction lookup fails
- **WHEN** `instructions specs` exits non-zero or returns invalid artifact-instruction JSON
- **THEN** sync MUST stop before every main-spec write
- **AND** the active change SHALL remain unmoved

#### Scenario: New capability is synchronized
- **WHEN** a selected delta introduces a capability with a Purpose section
- **THEN** the new main spec SHALL preserve that Purpose and merge requirements into main-spec structure
- **AND** it MUST NOT retain delta operation headers

### Requirement: Single archive verifies sync before moving

Single-change archive SHALL run requested sync inline, wait for completion, and
verify every declared delta capability before moving `changeRoot` or reporting
specs as synced.

#### Scenario: Included deltas match
- **WHEN** inline sync completes for ADDED, MODIFIED, REMOVED, or RENAMED requirements
- **THEN** archive SHALL verify the corresponding main-spec semantics
- **AND** it SHALL preserve unrelated scenarios before moving the change

#### Scenario: Sync or verification fails
- **WHEN** inline sync fails or any delta remains mismatched
- **THEN** archive MUST stop before moving `changeRoot`
- **AND** it MUST NOT report successful synchronization

#### Scenario: User cancels
- **WHEN** the user selects Cancel during the sync/archive decision
- **THEN** archive MUST perform no main-spec write and no change move

### Requirement: Bulk archive preserves per-delta decisions

Bulk archive SHALL carry included and excluded delta decisions through execution,
SHALL sync and verify only included deltas inline, and SHALL report every excluded
delta as `sync skipped` with its reason.

#### Scenario: Conflict delta is excluded
- **WHEN** implementation evidence excludes one delta from a conflicting capability
- **THEN** bulk archive MUST omit that delta from sync and verification
- **AND** it SHALL retain and report the exclusion reason without treating the whole change as skipped

#### Scenario: Batch prerequisite fails
- **WHEN** any required specs-instruction snapshot fails before the batch's first write or move
- **THEN** the entire batch MUST stop atomically

#### Scenario: Change verification fails
- **WHEN** an included delta remains mismatched after sync
- **THEN** that change MUST remain active
- **AND** bulk summary SHALL report failure rather than archive or successful sync

#### Scenario: Batch is cancelled
- **WHEN** the user cancels consolidated confirmation
- **THEN** bulk archive MUST perform no write and move no selected change

### Requirement: Legacy command wrappers retire after replacement proof

All 96 generated `/opsx:*` and `opsx-*` command, workflow, and prompt wrappers in `platform/openspec-store` and their 24 managed symlinks under `~/Developer/.claude/commands/opsx/` and `~/.claude/commands/opsx/` SHALL be retired once all 12 corresponding `1.17.0+` `openspec-*` skills are generated, valid, and discoverable via `.agents/skills` and `.claude/skills`.

#### Scenario: Replacements pass
- **WHEN** all 12 `openspec-*` skills report `metadata.generatedBy` `1.17.0` (or newer) and pass `sync-workspace-agent-skills.py` verification
- **THEN** `openspec update` under `"delivery": "skills"` SHALL remove all 96 unmodified generated command, workflow, and prompt files in `platform/openspec-store`
- **AND** `sync-workspace-agent-skills.py` SHALL prune the 24 managed command symlinks in `~/Developer/.claude/commands/opsx/` and `~/.claude/commands/opsx/` (`claude_commands=0`)

#### Scenario: Replacement is missing
- **WHEN** any of the 12 canonical `openspec-*` replacement skills is absent or invalid in `.agents/skills` or `.claude/skills`
- **THEN** command wrapper retirement MUST stop and `sync-workspace-agent-skills.py --check` SHALL exit non-zero

### Requirement: Cross-surface activation is deterministic

Activation SHALL require generator-version parity across `platform/openspec-store/.agents/skills/openspec-*` and `platform/openspec-store/.claude/skills/openspec-*`, zero orphaned manual split files inside generated skill directories, and a clean `sync-workspace-agent-skills.py --check` exit (`0`).

#### Scenario: Parity and indexes pass
- **WHEN** all 12 OpenSpec skills pass `1.17.0+` generator parity, orphaned `openspec-onboard/references/onboarding-walkthrough.md` files are removed, legacy `/opsx:*` wrappers are retired, and `sync-workspace-agent-skills.py --check` exits `0`
- **THEN** the runtime migration SHALL mark skills-only agent-driven apply, sync, single archive, and bulk archive active across Codex, Claude Code, OMP, Hermes, Pi, and OpenCode

#### Scenario: Separately owned index remains stale
- **WHEN** workflow content is regenerated in `platform/openspec-store` but workspace/user symlinks or `.skill-snapshots/current/` report drift
- **THEN** `sync-workspace-agent-skills.py --check` SHALL exit non-zero
- **AND** activation MUST wait until `sync-workspace-agent-skills.py` reconciles links and snapshot checks pass

### Requirement: Emptied OpenSpec command directories are pruned while non-OpenSpec and tool-skill directories stay intact
`platform/openspec-store` SHALL remove emptied OpenSpec command directories left after skills-only reconciliation while preserving active non-OpenSpec tool runtimes and tracked tool symlink trees.

#### Scenario: Emptied command directories are pruned cleanly
- **WHEN** `platform/openspec-store` is reconciled to OpenSpec `1.17.0+` skills-only delivery
- **THEN** emptied command directories (`.claude/commands/opsx`, `.agents/workflows`, `.factory/commands`, `.junie/commands`, `.kilocode/workflows`, `.kiro/prompts`, `.pi/prompts`, `.qoder/commands/opsx`) SHALL be absent
- **AND** directories containing active non-OpenSpec tool assets or tracked symlinks (`.opencode/`, `.agent/skills`, `.goose/skills`, `.zencoder/skills`) SHALL remain intact and unmodified
