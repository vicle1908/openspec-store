# Delta: omniroute-agent-cli-routing

## ADDED Requirements

### Requirement: Closure evidence SHALL cite the canonical route model IDs

Every closure, sentinel, or evidence row produced for an OmniRoute routing change of this family SHALL cite the canonical route model IDs it verified: `sh/gpt-5.6-sol` for the OpenAI Responses route and `pm/Claude-Fable` for the Anthropic Messages route. Evidence rows that substitute any other model ID for these routes are defective; because archived artifacts SHALL NOT be edited after archive, the defect SHALL be corrected through a superseding register in a subsequent active change.

#### Scenario: SH rows cite the SH route model

- **WHEN** closure evidence records the canonical SH route
- **THEN** the row SHALL cite `POST http://localhost:20128/v1/responses` with model `sh/gpt-5.6-sol`
- **AND** an SH row citing a different model ID SHALL be recorded as defective in the superseding register of an active change

#### Scenario: PM rows cite the PM route model

- **WHEN** closure evidence records the canonical PM route
- **THEN** the row SHALL cite `POST http://localhost:20128/v1/messages` with model `pm/Claude-Fable`
- **AND** a PM row citing a non-PM model ID for the Anthropic Messages route SHALL be recorded as defective in the superseding register

#### Scenario: superseding register does not edit archived artifacts

- **WHEN** a defect is found in archived closure evidence
- **THEN** the correction SHALL live in a new active change's evidence register with a citation to the archived file and line
- **AND** the archived artifact SHALL remain byte-identical

### Requirement: The applied-surface register SHALL match the final on-disk state

A routing change's applied-surface register SHALL enumerate every configuration file it applied, with per-file backup reference and rollback command, and SHALL be reconciled against the final on-disk hashes and modes before closure. A file applied after the register's freeze SHALL be appended with its apply timestamp and backup reference; closure SHALL NOT proceed while any applied file is absent from the register.

#### Scenario: post-freeze apply is appended

- **WHEN** a configuration file is applied after the applied-surface register was written
- **THEN** the register SHALL be updated with that file's target path, apply timestamp, backup reference, and current hash/mode before closure
- **AND** closure SHALL NOT proceed while any applied file is absent from the register

#### Scenario: unmapped new-file labels are reconciled

- **WHEN** a closure manifest's new-file list contains a label that maps to no verified applied target
- **THEN** the label SHALL be reconciled to a verified target path or recorded as defective with the verified created files enumerated explicitly
- **AND** the closure SHALL NOT report the unmapped label as a verified creation

#### Scenario: register reconciles against frozen baselines

- **WHEN** the final applied-surface register is produced
- **THEN** each entry SHALL record the frozen pre-apply baseline hash and the final on-disk hash and mode, value-blind
- **AND** any file whose baseline is absent from the register SHALL block closure

### Requirement: Mode tightenings SHALL be named-approved before apply

Any file-mode change that tightens permissions (for example 0644→0600) SHALL be recorded as a named approval in the change's manifest BEFORE the file is applied, identifying target path, old mode, new mode, and approver. An apply-time tightening found without a prior named approval SHALL be surfaced as a ratification gate: the owner either records a retroactive ratification decision or the mode SHALL be reverted with a fresh backup. No further mode tightening SHALL occur while the gate is open.

#### Scenario: unapproved tightening becomes a ratification gate

- **WHEN** a post-apply review finds a mode tightening without a prior named approval
- **THEN** the owning change SHALL record a ratification decision (approve or revert) before closure
- **AND** the file's current mode and pre-apply mode SHALL be recorded value-blind in that decision

#### Scenario: pre-recorded named approval precedes apply

- **WHEN** a planned apply will tighten a file mode
- **THEN** the named approval SHALL exist in the change manifest before the apply executes
- **AND** the apply log SHALL reference the approval entry

### Requirement: Live verification through credential-carrying configs SHALL be rotation-gated

When a configuration file carries literal credentials that were exposed in any session transcript, no live route verification SHALL be executed through that file until the owner explicitly confirms the credentials were rotated upstream or authorizes proceeding without rotation. The gate, its release condition, and the release decision SHALL be recorded in the active change; verification evidence for such surfaces SHALL remain at config level until release, and the surface SHALL NOT be reported as fully verified while blocked.

#### Scenario: rotation gate blocks live sentinel

- **WHEN** a routing change's closure requires a live sentinel through a config carrying exposed literal credentials
- **THEN** the sentinel SHALL be blocked pending the recorded release decision
- **AND** config-level route-contract evidence SHALL be recorded instead
- **AND** the surface SHALL NOT be reported as fully verified while blocked

#### Scenario: release decision is recorded, not assumed

- **WHEN** the rotation gate is to be released
- **THEN** the active change SHALL record an explicit user confirmation (rotation done upstream) or written authorization to proceed without rotation, with a timestamp
- **AND** the released live verification SHALL be executed and recorded before the surface is reported as fully verified
