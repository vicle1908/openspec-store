## REMOVED Requirements

### Requirement: Context compaction is configurable via harness_config

**Reason**: `harness_config` and `_build_harness_capabilities()` were removed; retaining this requirement makes the main contract normatively false.

**Migration**: Use typed public capability composition described by the current agent-runtime and agent-compaction requirements.

### Requirement: Optional compaction sub-features are configurable

**Reason**: The optional sub-feature dictionary projection is removed.

**Migration**: Supply supported sub-feature capabilities explicitly and test them through the public agent boundary.

### Requirement: Compaction composes with existing memory layers

**Reason**: This requirement is coupled to the obsolete `harness_config` setup and does not define the current caller-owned capability/store boundary.

**Migration**: Use the current typed composition and step-persistence requirements; preserve independent long-term memory behavior through existing memory contracts.

### Requirement: Compaction gracefully degrades when harness is unavailable

**Reason**: Production dependencies are now explicit and required at the composition boundary; silently skipping a requested capability would hide a deployment defect.

**Migration**: Fail typed construction when a requested capability cannot be imported or materialized.

### Requirement: Compaction parameters are configurable

**Reason**: The requirement describes fields on the removed dictionary interface.

**Migration**: Configure parameters on typed upstream capability instances.

### Requirement: Compaction config is documented in config.yaml.example

**Reason**: The configuration template described a removed interface.

**Migration**: Document typed capability construction and public `capabilities=[...]` composition instead.

## ADDED Requirements

### Requirement: Compaction layers remain independent from memory

Typed context compaction SHALL operate only on active conversation context, while caller-owned working, long-term, and step-persistence stores SHALL retain their own data and lifecycle semantics.

#### Scenario: Compaction with persistent history

- **WHEN** an agent uses typed compaction together with step persistence
- **THEN** compaction SHALL not delete persisted snapshots
- **AND** a later history-search capability SHALL be able to use the caller-owned source

#### Scenario: Requested capability unavailable

- **WHEN** a caller explicitly requests a compaction capability that cannot be imported or constructed
- **THEN** construction SHALL fail closed with a typed error
- **AND** the runtime SHALL not silently continue without the requested behavior
