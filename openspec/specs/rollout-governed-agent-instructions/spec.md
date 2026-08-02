# rollout-governed-agent-instructions Specification

## Purpose

Define clean-tree, ownership, host-bridge, validation-evidence, deferral, and
rollback gates for governed repository instruction rollout across TDT batches.

## Requirements

### Requirement: Governed batch rollout

Every repository rollout SHALL have an identified registry row, clean-tree evidence, ownership confirmation, pre-edit manifest, validation evidence, and rollback record.

#### Scenario: Target is not safe to edit

- **WHEN** a target has dirty policy files, ambiguous ownership, or broken worktree metadata
- **THEN** the batch SHALL remain deferred
- **AND** the plan SHALL record the exact blocker without mutating the target.

#### Scenario: Batch is validated

- **WHEN** all rows in a batch pass their repository-local checks
- **THEN** the batch manifest SHALL record the resulting paths, validation dates, and rollback references
- **AND** later batches SHALL not be marked complete from inferred or copied evidence.

#### Scenario: Batch evaluation contains deferred rows

- **WHEN** every row has current evidence but one or more targets fail the clean-tree, ownership, registry, or worktree-health gate
- **THEN** the governance change MAY complete after recording clean no-op rows and exact deferrals
- **AND** deferred rows SHALL NOT be labeled migrated or receive rollout-owned mutation

### Requirement: Host-native instruction bridges

Rollout SHALL preserve the canonical `AGENTS.md` source, reviewed `.agents` topology, and any host-native `CLAUDE.md` bridge without introducing untracked generated state or weakening local policy.

#### Scenario: Bridge or generated asset is absent

- **WHEN** a required bridge or generated asset cannot be verified
- **THEN** the repository SHALL remain incomplete until an implementation task supplies and validates it.
