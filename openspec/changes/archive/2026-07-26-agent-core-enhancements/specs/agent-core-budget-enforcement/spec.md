## ADDED Requirements

### Requirement: BudgetTracker hook enforcement
BudgetTracker SHALL enforce USD cost ceilings via pydantic-ai model request hooks.

#### Scenario: Budget set and enforced
- **WHEN** `BaseAgent.run()` is called with `budget_usd=10.0`
- **THEN** `BudgetTracker.set_budget(run_id, 10.0)` SHALL be called
- **AND** before each LLM request, `BudgetTracker.pre_check(run_id)` SHALL be called
- **AND** after each LLM request, `BudgetTracker.check_and_record(run_id, estimated_cost)` SHALL be called
- **AND** `GatewayError(code="budget_exceeded")` SHALL be raised if budget is exceeded

#### Scenario: Budget ID flows through deps
- **WHEN** `BaseAgent.run()` constructs `AgentRuntimeDeps`
- **THEN** `deps.extra["budget_id"]` SHALL contain the budget ID (or None if no budget)
- **AND** the hook adapter SHALL flatten `deps.extra` into the hook context dict so hooks can access `budget_id`

#### Scenario: Cost estimation from tokens
- **WHEN** `after_model_request` hook fires
- **THEN** cost_usd SHALL be estimated from token counts using a pricing table (pydantic-ai does not provide cost_usd directly)
- **AND** the pricing table SHALL map model names to per-token costs (input/output)
- **AND** `BudgetTracker.check_and_record(budget_id, estimated_cost)` SHALL be called with the estimated cost

#### Scenario: No budget = no enforcement
- **WHEN** `budget_usd` is None
- **THEN** `budget_id` SHALL be None
- **AND** `pre_check()` and `check_and_record()` SHALL be no-ops

#### Scenario: GatewayError propagation
- **WHEN** budget is exceeded
- **THEN** `GatewayError(code="budget_exceeded")` SHALL propagate through the hook dispatch
- **AND** `AgentRuntime.run()` SHALL catch it and map to `RunReason.BUDGET_EXCEEDED`
