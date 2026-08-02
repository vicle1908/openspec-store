# ops-health-omniroute-degradation-contract Specification

## Purpose

Distinguish between **soft-degraded** and **hard-degraded** health states for the `ai-review` service. Soft-degraded states (LLM proxy down, optional CLI missing, circuit-breaker open) keep the HTTP probe at 200 with `status=degraded` so that downstream observability can derive per-check alerts without flapping the service-level "down" alert.

## ADDED Requirements

### Requirement: Per-check classification into SOFT and HARD

`ai-review`'s `HealthChecker` MUST classify each check into a SOFT or HARD bucket. The classification determines whether a check failure flips the top-level HTTP status code.

#### Scenario: SOFT check returns error
- **WHEN** `check_omniroute_proxy()` returns `HealthResult(status="error", detail="HTTP 500")`
- **AND** the `omniroute_proxy` check is in the SOFT bucket
- **THEN** the aggregate `/health/full` response SHALL have `status=degraded` and HTTP status code 200
- **AND** the per-check map SHALL still contain the error detail so consumers can derive `omniroute_proxy_unavailable` alerts

#### Scenario: HARD check returns error
- **WHEN** the scheduler initialisation check returns `HealthResult(status="error", detail="...")`
- **AND** the `scheduler` check is in the HARD bucket
- **THEN** the aggregate `/health/full` response SHALL have HTTP status code 503
- **AND** the response body SHALL contain `status=error`

### Requirement: SOFT and HARD buckets are constants

The bucket assignment MUST be a code-level constant set, not a runtime decision. This keeps the contract auditable from a single source.

#### Scenario: SOFT_CHECKS is a frozenset
- **WHEN** an operator inspects `ai_review/utils/health.py`
- **THEN** `SOFT_CHECKS` SHALL be defined as `frozenset({"omniroute_proxy", "kimi_cli", "circuit_breaker", "sessions"})`
- **AND** `HARD_CHECKS` SHALL be defined as `frozenset({"scheduler", "postgres"})`

#### Scenario: A new check defaults to SOFT
- **WHEN** a developer adds a new `check_<name>()` method to `HealthChecker`
- **AND** they do not add the check name to either bucket
- **THEN** the check is treated as SOFT (no HTTP 503 on its failure)
- **AND** the developer SHOULD add the check name to the appropriate bucket explicitly

### Requirement: Aggregate status is deterministic

Given a check map, the aggregate `status` and HTTP 503 flag SHALL be a pure function of the check statuses and bucket membership.

#### Scenario: All checks OK
- **WHEN** every check returns `status="ok"` or `status="warning"`
- **THEN** the aggregate is `status="ok"`, HTTP 200

#### Scenario: Only SOFT errors
- **WHEN** only SOFT-bucket checks return `status="error"`
- **THEN** the aggregate is `status="degraded"`, HTTP 200

#### Scenario: Any HARD error
- **WHEN** at least one HARD-bucket check returns `status="error"`
- **THEN** the aggregate is `status="error"`, HTTP 503

#### Scenario: Both SOFT and HARD errors
- **WHEN** SOFT-bucket checks AND HARD-bucket checks both return `status="error"`
- **THEN** the aggregate is `status="error"`, HTTP 503 (HARD dominates)

### Requirement: Per-check detail is preserved at all times

The HTTP response body SHALL include the full per-check map with details for both SOFT and HARD failures. Consumers must be able to read the underlying error even when the HTTP status code is 200.

#### Scenario: HTTP 200 with degraded status still includes error detail
- **WHEN** `omniroute_proxy: {status: error, detail: HTTP 500}` is the only failing check
- **THEN** the response body SHALL contain `"status": "degraded"`
- **AND** the response body SHALL contain `"checks": {"omniroute_proxy": {"status": "error", "detail": "HTTP 500"}, ...}`
- **AND** the HTTP status code SHALL be 200