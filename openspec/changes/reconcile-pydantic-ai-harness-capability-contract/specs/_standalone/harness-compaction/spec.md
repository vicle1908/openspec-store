## REMOVED Requirements

### Requirement: Context compaction is configurable via harness_config

**Reason**: `harness_config` and `_build_harness_capabilities()` were removed; retaining this requirement makes the main contract normatively false.

**Migration**: Use typed public capability composition described by the current agent-core-capabilities and agent-compaction requirements.

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

Typed context compaction SHALL operate only on active conversation context, while caller-owned working, long-term, and step-persistence stores SHALL retain their own data and lifecycle semantics. Compaction SHALL not delete snapshots independently of the caller's configured store-retention policy; searchability is guaranteed only for snapshots retained by that policy.

#### Scenario: Compaction with persistent history

- **WHEN** an agent uses typed compaction together with step persistence
- **THEN** compaction SHALL not delete persisted snapshots
- **AND** a later history-search capability SHALL be able to use the retained caller-owned source

#### Scenario: Requested capability unavailable

- **WHEN** a caller explicitly requests a compaction capability that cannot be imported or constructed
- **THEN** construction SHALL fail before model or tool execution with the documented exact error category for that boundary: `ImportError` for an unavailable dependency, an upstream typed construction error for invalid capability arguments, or agent-core `ConfigError` for invalid public composition
- **AND** the runtime SHALL not silently continue without the requested behavior

#### Scenario: Caller configures bounded snapshot retention

- **WHEN** a caller configures a snapshot store that prunes older snapshots
- **THEN** compaction SHALL preserve the store's caller-owned retention semantics
- **AND** documentation and acceptance evidence SHALL not claim recovery of snapshots that the configured store has pruned
