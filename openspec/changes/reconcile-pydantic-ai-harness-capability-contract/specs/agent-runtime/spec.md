## ADDED Requirements

### Requirement: Explicit optional harness capability composition

The public agent composition boundary SHALL treat pydantic-ai-harness capabilities as caller-owned optional behavior. When an optional harness capability is omitted, the runtime SHALL NOT silently inject it; mandatory platform instrumentation, tool preparation, hooks, and an explicitly classified fallback step store remain separate concerns.

#### Scenario: Optional capabilities omitted

- **WHEN** a caller constructs an agent without compaction, reminders, spend, planning, advisor, conversation-search, or ToolGuardrail capabilities
- **THEN** the runtime SHALL not add those optional capabilities implicitly
- **AND** the resulting behavior SHALL match the documented no-optional-capability contract

#### Scenario: Optional capabilities supplied

- **WHEN** a caller supplies typed harness capabilities through the public composition boundary
- **THEN** the runtime SHALL preserve each supplied capability's identity and relative order
- **AND** authority and tool visibility validation SHALL still apply before execution

#### Scenario: Unsupported declarative configuration

- **WHEN** a configuration document contains a capability setting that the public composition path cannot materialize
- **THEN** construction SHALL fail with a typed configuration error
- **AND** the runtime SHALL NOT silently ignore the setting

### Requirement: Harness dependency ownership is explicit

The workspace SHALL declare optional harness extras only in the repository that owns the corresponding production capability composition. Consumer repositories without a direct production use SHALL depend on the base compatibility package without inheriting unrelated optional extras.

#### Scenario: Capability owner retains an extra

- **WHEN** the capability-composition owner supports an optional harness module in production
- **THEN** its dependency declaration MAY retain the matching extra
- **AND** the lockfile and dependency baseline SHALL identify that ownership

#### Scenario: Consumer has no direct production use

- **WHEN** a consumer repository has no production import or supported test contract for an optional extra
- **THEN** the consumer dependency SHALL omit that extra
- **AND** a dependency-baseline test SHALL prevent accidental reintroduction
