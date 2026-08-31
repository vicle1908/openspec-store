# Delta: omniroute-closure-integrity

## Purpose

Ensure that gate closures and superseding evidence for OmniRoute routing changes cite verifiable authorization and canonical route model IDs, so that archived "complete" states cannot rest on fabricated or corrupted records.

## ADDED Requirements

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
