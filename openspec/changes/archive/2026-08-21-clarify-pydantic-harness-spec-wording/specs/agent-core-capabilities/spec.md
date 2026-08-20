## MODIFIED Requirements

### Requirement: TieredCompaction in AgentRuntime

AgentRuntime SHALL compose a default `TieredCompaction` capability with a
120,000-token target when the caller omits compaction. A caller-supplied typed
compaction capability SHALL override that default while preserving its target
and ordered strategies. The supported explicit disablement SHALL be
`compaction_enabled=false`. Any retained internal convenience keyword SHALL
remain compatibility-only, undocumented, and unreachable through `BaseAgent`
or `build_agent`.

#### Scenario: Default compaction

- **WHEN** AgentRuntime is constructed without a compaction capability
- **THEN** TieredCompaction SHALL be present with the documented 120,000-token target
- **AND** the runtime SHALL apply the default through the public typed capability boundary

#### Scenario: Explicit compaction override

- **WHEN** a caller supplies TieredCompaction with target_tokens=50,000 and ordered strategies
- **THEN** TieredCompaction SHALL use 50,000 as the target token count
- **AND** the runtime SHALL preserve the supplied strategy order
- **AND** public-boundary behavior tests SHALL prove the below-target and exceeded-target paths

#### Scenario: Custom target

- **WHEN** a caller supplies TieredCompaction with target_tokens=50,000
- **THEN** TieredCompaction SHALL use 50,000 as the target token count
- **AND** the runtime SHALL preserve the supplied strategy order
- **AND** public-boundary behavior tests SHALL prove the below-target and exceeded-target paths

#### Scenario: Explicit compaction disablement is not implicit

- **WHEN** a caller supplies `compaction_enabled=false` through the supported public runtime boundary
- **THEN** the runtime SHALL honor that disablement
- **AND** it SHALL not silently replace the caller's choice with a second capability

### Requirement: One harness capability configuration boundary

The workspace SHALL expose one public harness-capability configuration boundary:
typed objects and supported runtime options supplied through `BaseAgent` or
`build_agent`. Internal compatibility keywords MAY remain temporarily for
migration or focused tests, but they SHALL not be projected from `AgentConfig`,
AgentSpec compatibility metadata, or public consumer constructors, and SHALL
not be confused with the supported public options listed in this contract.

#### Scenario: Public typed boundary

- **WHEN** a consumer supplies a typed harness capability through `BaseAgent` or `build_agent`
- **THEN** the capability SHALL be passed through with its identity and configuration preserved
- **AND** no parallel dictionary or convenience-key projection SHALL be required

#### Scenario: Compatibility-only internal keyword

- **WHEN** an internal test or migration shim uses a retained AgentRuntime convenience keyword
- **THEN** the keyword SHALL remain outside public consumer construction and documentation
- **AND** public capability acceptance SHALL not rely on that keyword

### Requirement: Public runtime options are distinct from private legacy aliases

The public agent-core capability contract SHALL accept supported runtime options
through `BaseAgent` and `build_agent`, including caller-supplied capabilities and
authority policy, `target_tokens`, `spend_limit_per_run_usd`,
`spend_limit_per_day_usd`, `enable_planning`, `advisor_model`,
`advisor_max_uses`, and `compaction_enabled`. Private legacy aliases and
configuration-only keys MAY be retained for migration or internal compatibility,
but SHALL not be documented as public consumer construction inputs, projected by
public consumers, or used to reconstruct private upstream agent state.

#### Scenario: Supported public runtime options are forwarded

- **WHEN** a consumer supplies a supported typed capability or named runtime option through `BaseAgent` or `build_agent`
- **THEN** agent-core SHALL forward the supplied identity and value through the supported runtime boundary
- **AND** an explicit caller value SHALL take precedence over the corresponding default

#### Scenario: Private legacy alias is not public API

- **WHEN** a consumer constructs an agent through the public SDK
- **THEN** private legacy aliases and configuration-only keys SHALL not be required or advertised
- **AND** the public path SHALL not project those aliases into a second capability configuration

#### Scenario: Unsupported private mutation is rejected by contract

- **WHEN** a caller attempts to rely on a private alias to mutate upstream agent state
- **THEN** the public capability contract SHALL provide no such guarantee
- **AND** evidence SHALL identify the supported public option used instead
