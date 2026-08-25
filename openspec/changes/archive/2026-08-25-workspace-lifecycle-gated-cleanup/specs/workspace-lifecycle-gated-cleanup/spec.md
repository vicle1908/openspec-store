## Purpose

Provide a cross-system workspace lifecycle contract that identifies reclaimable Git/Orca/OpenSpec state without confusing merged history, generated output, inactive UI records, or completed agent work with permission to delete.

## ADDED Requirements

### Requirement: Reviewed workspace inventory

The cleanup workflow SHALL produce one inventory covering every configured repository and managed worktree in scope. Each observed path SHALL include its source authority, repository identity when applicable, branch or detached revision, OpenSpec relationship when applicable, ownership signals, observation time, and a classification of `PROTECTED`, `REVIEW_REQUIRED`, `RECLAIMABLE`, or `RECLAIMED`.

#### Scenario: Inventory correlates multiple authorities

- **WHEN** a path is present as a Git worktree and an Orca workspace
- **THEN** the inventory SHALL correlate both records by canonical path
- **AND** SHALL preserve conflicting Git and Orca states rather than selecting the less restrictive state
- **AND** SHALL classify the path using the most restrictive applicable outcome

#### Scenario: Unknown ownership

- **WHEN** a path cannot be mapped to a repository, OpenSpec change, Orca workspace, or known runtime owner
- **THEN** the path SHALL be classified `REVIEW_REQUIRED`
- **AND** the report SHALL identify the missing ownership evidence

#### Scenario: Retention inventory protects cleanup

- **WHEN** a reviewed retention inventory exists for an observed path
- **THEN** cleanup SHALL treat protected retention classes as exclusion lists and SHALL NOT delete or relocate a protected path
- **AND** cleanup SHALL treat `RECLAIMABLE` candidate artifacts as review-only proposals without deletion

### Requirement: Orca ownership hierarchy protection

An Orca-managed worktree SHALL remain `PROTECTED` when it is pinned, located under an Orca-managed root, has an active child worktree, has an orphaned but unresolved terminal, or has an agent whose state is `working` or `interrupted`.

#### Scenario: Pinned or parent worktree

- **WHEN** Orca reports `isPinned=true` or a live child worktree references the candidate as its parent
- **THEN** the candidate SHALL remain `PROTECTED`
- **AND** the report SHALL identify the pin or child dependency

#### Scenario: Orphaned terminal

- **WHEN** a terminal is disconnected or orphaned but its ownership and last activity cannot be conclusively retired
- **THEN** the worktree SHALL remain `REVIEW_REQUIRED`
- **AND** no filesystem removal SHALL be proposed

#### Scenario: Agent in working or interrupted state

- **WHEN** an Orca agent for the candidate worktree is in `working` or `interrupted` state
- **THEN** the candidate SHALL remain `PROTECTED`
- **AND** the report SHALL identify the agent and its state

### Requirement: Read-only dry-run default

The cleanup workflow SHALL default to a read-only dry-run. A dry-run SHALL not delete, move, prune, reset, checkout, push, stage, archive, or mutate a file, branch, worktree, OpenSpec change, process, container, database, or index.

#### Scenario: Dry-run discovers reclaimable state

- **WHEN** the workflow is run without an explicit approved retirement action
- **THEN** it SHALL emit a machine-readable manifest and human-readable summary
- **AND** SHALL report proposed actions without applying them
- **AND** SHALL return a non-mutating result even when reclaimable paths are present

### Requirement: Active work protection

A path SHALL remain `PROTECTED` when it is referenced by an incomplete OpenSpec change, an uncommitted archive move, non-generated untracked or modified content, an Orca workspace with host activity, a live terminal, an attached PTY, or an active agent.

#### Scenario: Git-merged worktree with active Orca session

- **WHEN** a worktree branch is merged into its target branch
- **AND** Orca reports host activity, an active workspace, a live terminal, an attached PTY, or an active agent for that worktree
- **THEN** the inventory SHALL classify the worktree as `PROTECTED`
- **AND** SHALL not recommend direct filesystem removal

#### Scenario: Active OpenSpec change

- **WHEN** a path belongs to an active OpenSpec change with incomplete tasks or an untracked change directory
- **THEN** the path SHALL be `PROTECTED`
- **AND** the report SHALL include the change name and incomplete or untracked condition

#### Scenario: Non-generated work is present

- **WHEN** a candidate contains uncommitted or untracked files that are not proven generated output
- **THEN** the path SHALL be `PROTECTED`
- **AND** the workflow SHALL not infer that the content is disposable from age, naming, or branch ancestry

### Requirement: Runtime and persistent-state protection

A path SHALL remain `PROTECTED` when a running process, LaunchAgent, container, index watcher, database, memory store, rollback copy, or other registered runtime owner references it. A missing or unavailable runtime check SHALL produce `REVIEW_REQUIRED`, not `RECLAIMABLE`.

#### Scenario: Active service path

- **WHEN** a workspace path is used by a running service or index watcher
- **THEN** the workflow SHALL classify it as `PROTECTED`
- **AND** SHALL identify the observed owner without exposing credentials or request bodies

#### Scenario: Runtime check unavailable

- **WHEN** runtime ownership cannot be checked
- **THEN** the workflow SHALL report the check as `UNKNOWN`
- **AND** SHALL block reclaimability until an operator resolves the uncertainty

### Requirement: Merge and preservation proof

A branch or detached worktree SHALL be `RECLAIMABLE` only when its content is proven preserved by the target history, an approved remote or backup, or an explicitly retained archival artifact. Squash-merged content SHALL require content-equivalence evidence rather than ancestry alone. Unpushed history without an approved preservation record SHALL block reclaimability.

#### Scenario: Clean ancestor deployment snapshot

- **WHEN** a detached deployment snapshot is clean and its revision is an ancestor of the target branch
- **AND** no OpenSpec, Orca, or runtime protection applies
- **THEN** the snapshot MAY be classified `RECLAIMABLE`
- **AND** the manifest SHALL record the ancestor proof

#### Scenario: Detached unique revision

- **WHEN** a detached worktree contains a revision not reachable from the target branch or an approved preservation location
- **THEN** it SHALL be `REVIEW_REQUIRED`
- **AND** no cleanup action SHALL be proposed as safe

#### Scenario: Unpushed repository history

- **WHEN** the target repository contains commits not present on its approved remote or backup
- **THEN** branch and worktree deletion SHALL remain blocked
- **AND** the report SHALL state that preservation approval is required

### Requirement: Ordered retirement ownership

An approved retirement SHALL follow ownership order: child Orca worktrees SHALL be retired before their parents, Orca workspace/file-handle state SHALL be released before Git removal, Git worktree metadata and checkout SHALL be retired second, and the branch reference SHALL be deleted last. OpenSpec changes and archives SHALL use OpenSpec lifecycle commands and SHALL not be removed through generic cleanup.

#### Scenario: Worktree removal ordering

- **WHEN** an operator approves a reclaimable Orca-managed worktree
- **THEN** the workflow SHALL require confirmation that Orca reports no active terminals, agents, host activity, attached PTYs, pins, or child worktrees before Git worktree removal
- **AND** SHALL require Orca file-handle/workspace release before Git removal
- **AND** SHALL require the Git worktree to be absent before branch deletion
- **AND** SHALL record each completed transition

#### Scenario: OpenSpec path encountered

- **WHEN** a candidate path is inside an OpenSpec change or archive
- **THEN** the workflow SHALL defer to OpenSpec status, validation, archive, and commit lifecycle rules
- **AND** SHALL not treat generic Git or filesystem cleanup as authorization

#### Scenario: Retirement transition fails

- **WHEN** an ordered retirement transition fails at any step
- **THEN** the record SHALL remain `REVIEW_REQUIRED` with completed and pending transitions recorded
- **AND** the workflow SHALL NOT compensate by deleting the path directly

### Requirement: Auditable cleanup manifest

Every approved or skipped retirement SHALL be recorded with the selected path, classification, evidence references, operator approval, action owner, before and after observations, and the reason for any refusal or skip. The manifest SHALL omit credential values and request or response bodies.

#### Scenario: Candidate is skipped

- **WHEN** a candidate fails any protection or preservation gate
- **THEN** the manifest SHALL retain the candidate with its blocking reason
- **AND** a later run SHALL be able to distinguish a newly observed candidate from a previously skipped one

#### Scenario: Manifest excludes secrets

- **WHEN** an observation contains credentials, tokens, or request/response bodies
- **THEN** the manifest SHALL omit those values
- **AND** SHALL retain only non-secret owner, endpoint, and classification metadata

#### Scenario: Repeated dry-run

- **WHEN** the same workspace is scanned without relevant state changes
- **THEN** the inventory SHALL produce stable classifications and stable path identities
- **AND** it SHALL not create duplicate cleanup actions or mutate the workspace
