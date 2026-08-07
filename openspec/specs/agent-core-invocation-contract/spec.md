# agent-core-invocation-contract Specification

## Purpose
Establishes the typed `AgentRequest`/`AgentResult` invocation contract, a reference adapter demonstrating the consumer pattern, and a distributable wheel for agent-core.
## Requirements
### Requirement: A typed AgentRequest is the structured invocation input
The system SHALL provide an `AgentRequest` type that wraps the task and invocation parameters, and `BaseAgent.run` SHALL accept either a plain string or an `AgentRequest`.

#### Scenario: AgentRequest carries structured invocation fields
- **WHEN** an `AgentRequest` is constructed
- **THEN** it exposes `task`, optional `skill_profile`, a `context` dict, optional `correlation_id`, optional `timeout_seconds`, and optional `budget_usd`

#### Scenario: run accepts a plain string
- **WHEN** `BaseAgent.run("review this")` is called with a string
- **THEN** the call behaves as today and returns an `AgentResult`

#### Scenario: run accepts an AgentRequest
- **WHEN** `BaseAgent.run(AgentRequest(task="review this", skill_profile="reviewer"))` is called
- **THEN** the agent resolves skills through the request's `skill_profile` and returns an `AgentResult`

#### Scenario: Request profile overrides the agent default
- **WHEN** a `BaseAgent` constructed with `skill_profile="default"` is run with `AgentRequest(skill_profile="reviewer")`
- **THEN** the request's `reviewer` profile takes precedence for that invocation

### Requirement: AgentResult is the canonical invocation response
The system SHALL reuse the existing `AgentResult` as the response contract; no parallel response type is introduced.

#### Scenario: Result reports completion and reason
- **WHEN** an invocation returns
- **THEN** the `AgentResult` exposes `completed`, `output`, `reason`, `iterations`, and `duration_ms`

#### Scenario: Incomplete run carries a machine-readable reason
- **WHEN** a run is capped by iteration, timeout, or budget
- **THEN** `completed` is `False` and `reason` is one of the `RunReason` values (`max_iterations`, `agent_timeout`, `budget_exceeded`, `approval_needed`)

### Requirement: A reference adapter demonstrates the consumer pattern
The system SHALL ship one runnable reference adapter in `agent-core/examples/code_reviewer/` that maps a domain concept to an `AgentRequest`, invokes a configured `BaseAgent`, and derives a domain result from the `AgentResult`.

#### Scenario: Reference adapter builds and runs against mocks
- **WHEN** the reference adapter is invoked with a mock domain input and a mocked model
- **THEN** it constructs an `AgentRequest`, runs the agent, and returns a domain result without contacting any external service

#### Scenario: Reference adapter does not modify any running service
- **WHEN** the reference adapter ships
- **THEN** no file under `ai-review/` or `webhook-receiver/` is changed; the adapter is self-contained in `agent-core/examples/code_reviewer/`

### Requirement: agent-core is distributable to consumer repos
The system SHALL provide a documented distribution path so consumer repos can depend on agent-core, with a locally buildable wheel as the exit criterion.

#### Scenario: Wheel builds and installs into a clean environment
- **WHEN** `uv build` is run in agent-core
- **THEN** a wheel artifact is produced that installs into a fresh environment and exposes the `agent_core` package

#### Scenario: Distribution path is documented for both pilot and release
- **WHEN** a developer reads the distribution guidance
- **THEN** it documents the uv path/workspace dependency for monorepo pilots and the wheel→Nexus publish command for release consumers

