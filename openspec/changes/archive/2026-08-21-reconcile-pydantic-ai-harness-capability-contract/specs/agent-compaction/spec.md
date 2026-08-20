## MODIFIED Requirements

### Requirement: Typed compaction is explicitly enabled

The agent runtime SHALL install its documented default tiered compaction
capability when the caller omits compaction, and SHALL preserve a caller's
typed compaction target and ordered strategies when supplied. An explicit
supported disablement SHALL remain effective and SHALL not be replaced by an
implicit second capability.

#### Scenario: Compaction omitted

- **WHEN** an agent is constructed without a compaction capability
- **THEN** the AgentRuntime default TieredCompaction SHALL be installed with its documented target
- **AND** the runtime SHALL not claim that omission means no compaction

#### Scenario: Tiered compaction supplied

- **WHEN** a caller supplies a tiered compaction with a target and ordered strategies
- **THEN** the runtime SHALL preserve the target and strategy order
- **AND** the capability SHALL execute through the supported upstream capability API

#### Scenario: Compaction explicitly disabled

- **WHEN** a caller supplies an explicit supported compaction disablement
- **THEN** no compaction capability SHALL be installed for that runtime
- **AND** the runtime SHALL preserve the caller's disablement

### Requirement: Compaction behavior is publicly verifiable

Compaction acceptance SHALL execute through the public agent boundary and SHALL
prove the below-threshold, threshold-exceeded, and explicit-override paths.
Deterministic evidence SHALL identify the capability configuration and SHALL
not be presented as live-provider acceptance.

#### Scenario: Conversation remains below target

- **WHEN** a deterministic conversation remains below the configured target
- **THEN** no compaction receipt or synthetic summary SHALL be inserted

#### Scenario: Conversation exceeds target

- **WHEN** a deterministic conversation exceeds the configured target
- **THEN** compaction SHALL reduce the active context according to the effective strategy
- **AND** protected facts and any configured receipt/evidence SHALL remain observable

#### Scenario: Explicit target overrides default

- **WHEN** a public caller supplies a typed target different from the AgentRuntime default
- **THEN** the below-target and exceeded-target outcomes SHALL be evaluated against the supplied target
- **AND** the evidence SHALL identify the override rather than attributing it to the default
