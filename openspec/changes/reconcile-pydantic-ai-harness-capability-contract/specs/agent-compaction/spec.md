## REMOVED Requirements

### Requirement: Compaction strategy selection

**Reason**: The requirement describes the removed dictionary-based `AgentConfig.context_compaction` projection and conflicts with the typed public capability boundary.

**Migration**: Supply an explicit typed compaction capability through public agent composition and follow the added requirements below.

### Requirement: ClampOversizedMessages

**Reason**: The requirement is part of the removed unread configuration projection.

**Migration**: Configure any supported overflow/clamp capability explicitly through typed composition and verify it through the public agent path.

### Requirement: ClearToolResults

**Reason**: The requirement is part of the removed unread configuration projection.

**Migration**: Include `ClearToolResults` only inside an explicitly supplied compaction composition.

### Requirement: DeduplicateFileReads

**Reason**: The requirement is part of the removed unread configuration projection.

**Migration**: Include `DeduplicateFileReads` only inside an explicitly supplied compaction composition.

### Requirement: LimitWarner

**Reason**: The requirement describes a configuration path that is not materialized by the current public runtime.

**Migration**: Use the supported typed limit-warning capability explicitly or document it as unavailable; do not claim configuration support.

### Requirement: OverflowingToolOutput

**Reason**: The requirement describes a configuration path that is not materialized by the current public runtime.

**Migration**: Use the supported typed output-overflow capability explicitly or document it as unavailable; do not claim configuration support.

### Requirement: CacheStabilityMonitor

**Reason**: The requirement describes a configuration path that is not materialized by the current public runtime.

**Migration**: Use the supported typed cache-monitoring capability explicitly or document it as unavailable; do not claim configuration support.

## ADDED Requirements

### Requirement: Typed compaction is explicitly enabled

The agent runtime SHALL add context compaction only when the caller supplies a typed compaction capability, and SHALL preserve the configured strategy and target without silently replacing it.

#### Scenario: Compaction omitted

- **WHEN** an agent is constructed without a compaction capability
- **THEN** no compaction capability SHALL be installed
- **AND** the runtime SHALL not trim or summarize context because of an undocumented default

#### Scenario: Tiered compaction supplied

- **WHEN** a caller supplies a tiered compaction with a target and ordered strategies
- **THEN** the runtime SHALL preserve the target and strategy order
- **AND** the capability SHALL execute through the supported upstream capability API

### Requirement: Compaction behavior is publicly verifiable

Compaction acceptance SHALL execute through the public agent boundary and SHALL prove both the below-threshold and threshold-exceeded paths.

#### Scenario: Conversation remains below target

- **WHEN** a deterministic conversation remains below the configured target
- **THEN** no compaction receipt or synthetic summary SHALL be inserted

#### Scenario: Conversation exceeds target

- **WHEN** a deterministic conversation exceeds the configured target
- **THEN** compaction SHALL reduce the active context according to the supplied strategy
- **AND** protected facts and any configured receipt/evidence SHALL remain observable
