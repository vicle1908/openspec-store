## ADDED Requirements

### Requirement: Agent limits are configurable with unlimited defaults

`ConsumerRuntimeProfile` SHALL accept `None` for `max_iterations`, `timeout_seconds`, and `total_tokens_limit`, where `None` means unlimited. The default for all three fields SHALL be `None` (unlimited). `FlavorDefaults.budget_usd` SHALL also default to `None` (unlimited). When set to a non-`None` value, the agent SHALL enforce the configured cap. When `None`, the agent SHALL run without iteration, timeout, or token caps. Operators MAY set `budget_usd` via `~/.tdt/config.yaml` to impose a cost safety net; when unset, no cost cap applies.

#### Scenario: Default limits are unlimited

- **WHEN** `ConsumerRuntimeProfile()` is constructed without overrides
- **THEN** `max_iterations`, `timeout_seconds`, and `total_tokens_limit` SHALL all be `None`
- **AND** `FlavorDefaults.budget_usd` SHALL default to `None`
- **AND** the agent SHALL run without iteration, timeout, token, or cost caps

#### Scenario: Operator sets explicit limits via config

- **GIVEN** `~/.tdt/config.yaml` contains `agent.max_iterations: 50`, `agent.timeout_seconds: 600`, and `agent.budget_usd: 10.00`
- **WHEN** the agent profile is built from config
- **THEN** those values SHALL override the unlimited defaults
- **AND** the agent SHALL enforce the configured caps

#### Scenario: Budget_usd as optional cost safety net

- **GIVEN** `max_iterations`, `timeout_seconds`, and `total_tokens_limit` are all `None`
- **AND** `budget_usd` is set to a positive value in the config
- **WHEN** the agent's cumulative cost reaches the budget
- **THEN** the agent SHALL stop with `BUDGET_EXCEEDED`

#### Scenario: Unset budget means no cost cap

- **GIVEN** `~/.tdt/config.yaml` has no `agent.budget_usd` setting
- **WHEN** the agent profile is built
- **THEN** `budget_usd` SHALL be `None`
- **AND** the agent SHALL run without any cost cap
- **AND** the operator accepts responsibility for all LLM costs
