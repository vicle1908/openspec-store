# openspec-agent-surface-parity Specification

## Purpose

Define how TDT-maintained OpenSpec agent workflows remain version-aligned,
invocation-consistent, and safe for apply, sync, and archive operations across
the workspace.

## Requirements

### Requirement: TDT skills use one reviewed OpenSpec release contract

All TDT-maintained `.agents/skills/openspec-*` workflows SHALL derive from the
same exact official OpenSpec release and SHALL record matching provenance.

#### Scenario: Complete skill set is refreshed
- **WHEN** the OpenSpec agent surface is prepared for activation
- **THEN** all 12 declared TDT OpenSpec skills SHALL match the reviewed 1.7.0 workflow contracts
- **AND** no host-visible OpenSpec skill may remain at 1.6.0 or use stale `/opsx:*` invocation

#### Scenario: Mixed version is found
- **WHEN** any OpenSpec skill reports another version or retains an incompatible workflow section
- **THEN** agent-driven apply, sync, single archive, and bulk archive MUST remain disabled

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

The `/opsx` sync and update wrappers SHALL be removed only after corresponding
1.7 `.agents` and `.codex` skills are present, valid, and discoverable by their
`$openspec-*` names.

#### Scenario: Replacements pass
- **WHEN** `$openspec-sync-specs` and `$openspec-update-change` pass version, invocation, and content checks on both surfaces
- **THEN** the two legacy wrappers MAY be removed
- **AND** their pre-removal names and hashes SHALL remain in rollback evidence

#### Scenario: Replacement is missing
- **WHEN** either replacement skill is absent or invalid
- **THEN** wrapper removal MUST stop
- **AND** activation SHALL remain disabled

### Requirement: Cross-surface activation is deterministic

Activation SHALL require semantic parity between TDT `.agents` and generated
`.codex` OpenSpec 1.7 workflows plus a successful handoff to the shared skill-index
owner.

#### Scenario: Parity and indexes pass
- **WHEN** all 12 skills pass release comparison, archive fixtures pass, legacy wrappers are retired, and indexes are current
- **THEN** the runtime migration MAY enable agent-driven apply, sync, single archive, and bulk archive

#### Scenario: Separately owned index remains stale
- **WHEN** workflow content is correct but skill-index validation reports stale generated artifacts
- **THEN** this change SHALL preserve index ownership boundaries
- **AND** activation MUST wait for `align-jti-skill-runtime-contract` to refresh and validate them
