## ADDED Requirements

### Requirement: Public runtime-option forwarding

The public runtime composition boundary SHALL forward supported runtime options
from `BaseAgent` and `build_agent` to `AgentRuntime` and the upstream run API
without private-agent reconstruction. Omitted options SHALL receive documented
runtime defaults, while explicitly supplied typed options SHALL take precedence
and retain their identity and configuration.

#### Scenario: Omitted options receive runtime defaults

- **WHEN** a consumer constructs a public agent without optional runtime capabilities
- **THEN** AgentRuntime SHALL apply only the documented defaults for that option
- **AND** the public construction path SHALL not require compatibility-only keywords

#### Scenario: Explicit option overrides a default

- **WHEN** a consumer supplies a typed runtime capability or supported run option
- **THEN** the public construction and run path SHALL forward that exact option
- **AND** the supplied configuration SHALL override the corresponding default

#### Scenario: Unsupported private mutation is unavailable

- **WHEN** a consumer uses the public runtime-option path
- **THEN** the runtime SHALL use supported agent and run APIs
- **AND** it SHALL not inspect or reconstruct private upstream agent state

