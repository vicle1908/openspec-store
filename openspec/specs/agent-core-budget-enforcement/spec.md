## Purpose

REPLACED by pydantic-ai native `UsageLimits` for token/request budget enforcement. The custom `BudgetTracker` USD cost ceiling enforcement has been removed.

## Migration Summary

| Removed | Replacement |
|---|---|
| `BudgetTracker` | `pydantic_ai.UsageLimits` (token/request limits) |
| `GatewayError(code="budget_exceeded")` | `pydantic_ai.exceptions.UsageLimitExceeded` |
| USD cost estimation hook | Log-only cost estimation (no enforcement) |

## Requirements

### Requirement: Token-based budget enforcement

Budget enforcement SHALL use pydantic-ai's `UsageLimits` for token and request count limits.

#### Scenario: Request limit enforced

- **WHEN** `Agent.run()` is called with `usage_limits=UsageLimits(request_limit=100)`
- **THEN** pydantic-ai SHALL enforce the request limit natively
- **AND** `UsageLimitExceeded` SHALL be raised when exceeded

#### Scenario: No custom budget tracker

- **WHEN** the budget enforcement system is inspected
- **THEN** `BudgetTracker` class SHALL NOT exist
- **AND** `get_budget_tracker` function SHALL NOT exist

### Requirement: USD cost estimation retained

A simplified cost estimation hook MAY be retained for logging/observability purposes, but SHALL NOT enforce budget limits.

#### Scenario: Cost logged but not enforced

- **WHEN** an LLM request completes
- **THEN** the estimated USD cost MAY be logged for observability
- **AND** no `GatewayError` SHALL be raised based on USD cost
