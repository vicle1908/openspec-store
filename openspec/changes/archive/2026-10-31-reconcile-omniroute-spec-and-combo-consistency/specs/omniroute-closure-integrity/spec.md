# Spec Delta: omniroute-closure-integrity

## MODIFIED Requirements

### Requirement: Reopened-gate closure ticks SHALL cite authorization that exists in the controlling conversation
When a task ledger closes a previously-blocked gate whose release condition is an owner decision (such as the Kimi Code/Cline credential-rotation gate or a mode-tightening ratification), the tick SHALL cite a verifiable authorization artifact (quote, instruction, or decision) in the controlling conversation or user-authored record. A closure citing an unlocatable authorization is void and SHALL be recorded as void by a subsequent active change without editing archived bytes.

#### Scenario: fabricated authorization voids the closure

- **WHEN** a gate tick cites a user instruction that does not exist in the controlling conversation
- **THEN** the closure SHALL be treated as void by downstream consumers
- **AND** a subsequent active change SHALL record the void status with file+line citations, leaving the archive byte-identical
- **AND** the gate SHALL be reopened as an explicit blocked task pending a real owner decision

#### Scenario: valid authorization is cited verbatim

- **WHEN** a gate is released by a real owner decision
- **THEN** the release record SHALL quote the decision verbatim, cite where it occurred, and carry a timestamp
- **AND** the executed verification SHALL be recorded before the gate is reported as released
