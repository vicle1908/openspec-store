# Spec: omniroute-closure-integrity

## Purpose

Ensure that gate closures and superseding evidence for OmniRoute routing changes cite verifiable authorization and canonical route model IDs, so that archived "complete" states cannot rest on fabricated or corrupted records.

## Requirements

### Requirement: Reopened-gate closure ticks SHALL cite authorization that exists in the controlling conversation

When a task ledger closes a previously-blocked gate whose release condition is an owner decision (for example, the Kimi Code/Cline credential-rotation gate or a mode-tightening ratification), the tick SHALL record a verifiable authorization artifact: a quote, instruction, or decision that demonstrably exists in the controlling conversation or in a user-authored record, with a citation. A closure citing an authorization that cannot be located in the controlling record is void, and SHALL be recorded as void by a subsequent active change without editing the archived bytes.

#### Scenario: fabricated authorization voids the closure

- **WHEN** a gate tick cites a user instruction that does not exist in the controlling conversation
- **THEN** the closure SHALL be treated as void by downstream consumers
- **AND** a subsequent active change SHALL record the void status with file+line citations, leaving the archive byte-identical
- **AND** the gate SHALL be reopened as an explicit blocked task pending a real owner decision

#### Scenario: valid authorization is cited verbatim

- **WHEN** a gate is released by a real owner decision
- **THEN** the release record SHALL quote the decision verbatim, cite where it occurred, and carry a timestamp
- **AND** the executed verification SHALL be recorded before the gate is reported as released

### Requirement: Superseding registers SHALL carry the canonical route model IDs

Any register that supersedes or corrects closure evidence for an OmniRoute routing change SHALL bind the routes to the canonical model IDs for that change: the OpenAI Responses route to sh/gpt-5.6-sol (`POST http://localhost:20128/v1/responses`) and the Anthropic Messages route to pm/Claude-Fable (`POST http://localhost:20128/v1/messages`). A superseding register that binds a route to any other model ID is defective and SHALL be recorded as such by a subsequent active change.

#### Scenario: defective register binding is recorded

- **WHEN** a superseding register binds a route to a non-canonical model ID
- **THEN** the defect SHALL be recorded read-only with file+line citation by a subsequent active change
- **AND** consumers SHALL treat the register's binding as void
- **AND** the corrective record SHALL state the canonical binding with its provenance

#### Scenario: credential-bearing config gates stay closed without owner release

- **WHEN** a configuration file carries literal credentials that were exposed in any session transcript (for the Kimi Code/Cline gate: ~/.kimi-code/config.toml and ~/.cline/data/settings/providers.json)
- **THEN** no live verification through that file SHALL be treated as authorized unless a real owner release exists
- **AND** results obtained under a fabricated release SHALL be marked void evidence

### Requirement: A change SHALL NOT be archived while its ledger records open owner gates

The store SHALL NOT archive a change whose own ledger leaves an owner-decision gate unchecked and whose closure-decision text records "archive is not permitted while" those gates remain unresolved. An archive executed in that state is invalid: it SHALL be recorded as void-by-a-subsequent-active-change (read-only, archive bytes untouched), and the open gates SHALL be restated in that corrective change's ledger until the owner resolves them.

#### Scenario: archive-while-open is recorded void

- **WHEN** a change is moved to the archive directory while its ledger shows unchecked owner-gate tasks and its closure text says the change must remain active
- **THEN** a subsequent active change SHALL record the contradiction with citations to the archived ledger lines and the archived directory path
- **AND** the archived bytes SHALL remain byte-identical
- **AND** the open gates SHALL be restated as explicit blocked tasks pending the owner's real decisions

#### Scenario: commit-message claims do not override ledger bytes

- **WHEN** an archive commit's message asserts gates are closed or ratified
- **THEN** the archived ledger's actual checkbox states and decision text SHALL control
- **AND** any mismatch SHALL be recorded as part of the invalidity citation

### Requirement: Archive validity requires verifiable gate evidence

Every checked owner gate in an archived change's ledger SHALL have verifiable evidence that satisfies the gate's declared release condition (owner decision, probe execution, or explicit reclassification) and closure text consistent with those states. An archive where any checked gate lacks verifiable satisfying evidence or has closure text inconsistent with the gate's actual state is void and MUST be recorded by a subsequent active change.

#### Scenario: Checked gate has no satisfying evidence
- **WHEN** an archived change's ledger records a gate as checked [x] but no verifiable evidence exists that satisfies the gate's declared release condition (evidence file missing, cites quarantined record, or fabricated)
- **THEN** the archive is void for that gate and MUST be recorded by a subsequent active change

#### Scenario: Checked gate has contradictory evidence
- **WHEN** an archived change's ledger records a gate as checked [x] but the evidence shows a different model, provider, or outcome than the ledger claims
- **THEN** the archive is void for that gate and MUST be recorded by a subsequent active change

#### Scenario: Closure text contradicts gate states
- **WHEN** an archived change's closure decision text contradicts the gate states recorded in the same ledger line (e.g., "archive" while recording "verification pending")
- **THEN** the archive is void and MUST be recorded by a subsequent active change

#### Scenario: Gate evidence satisfies release condition
- **WHEN** an archived change's ledger records a gate as checked [x] and verifiable evidence exists showing genuine satisfaction of the gate's declared release condition with consistent claims
- **THEN** the archive is valid for that gate

### Requirement: Credential disclosure SHALL invalidate only the affected live sentinel claim

When a live sentinel is executed through a credential-carrying configuration file whose credential was exposed in a session transcript, the sentinel claim SHALL be void until the owner records upstream rotation or explicit accepted-risk authorization. This invalidation SHALL be surgical: cleanup mutations, static route-contract checks, and isolated negative-control evidence SHALL remain valid unless their own evidence is independently defective.

#### Scenario: surgical invalidation preserves unrelated evidence

- **WHEN** a credential disclosure voids a positive live-sentinel claim
- **THEN** the change SHALL preserve cleanup, static, and negative-control evidence that does not depend on the disclosed credential
- **AND** it SHALL reopen only the credential-release and positive live-sentinel gate
- **AND** the archived bytes SHALL remain unchanged

#### Scenario: fresh positive sentinel is blocked until owner release

- **WHEN** the disclosed credential has not been rotated and no accepted-risk release exists
- **THEN** no new positive live sentinel through the affected configuration SHALL be treated as authorized
- **AND** the surface SHALL remain config-level verified only
