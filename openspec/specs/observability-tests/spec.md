# Observability Tests

**Capability:** observability-tests
**Status:** Implemented (agent-core observability module)
**Date:** 2026-07-25

## Purpose

Unit and integration test coverage for the agent-core observability module, including LangfuseClient, MLflowClient, scorers, and evaluation runner.

## Requirements

### Requirement: LangfuseClient unit tests
The system SHALL have unit tests for `LangfuseClient` covering: initialization with config, no-op fallback when unconfigured, score_trace() method, and context manager behavior.

#### Scenario: Client initializes with config
- **WHEN** `LangfuseClient.create({"host": "http://localhost:3000", "public_key": "pk", "secret_key": "sk"})` is called
- **THEN** a client instance is returned (or no-op if SDK not installed)

#### Scenario: No-op fallback
- **WHEN** `LangfuseClient.create({})` is called with empty config
- **THEN** a no-op client is returned that silently discards operations

### Requirement: MLflowClient unit tests
The system SHALL have unit tests for `MLflowClient` covering: initialization, no-op fallback, start_run(), log_params(), log_metrics(), log_tags().

#### Scenario: Client initializes with URI
- **WHEN** `MLflowClient.create("http://localhost:5000")` is called
- **THEN** a client instance is returned (or no-op if SDK not installed)

### Requirement: Scorer unit tests
The system SHALL have unit tests for CostScorer and RegressionScorer covering: evaluate() return type, threshold behavior, edge cases.

#### Scenario: CostScorer thresholds
- **WHEN** `CostScorer().evaluate()` is called with cost_usd/tokens_total combinations
- **THEN** scores are 1.0 (excellent), 0.8 (good), 0.5 (acceptable), 0.2 (expensive), 0.0 (zero tokens)

#### Scenario: RegressionScorer detection
- **WHEN** `RegressionScorer(baseline_latency_ms=5000).evaluate()` is called with latency_ms=3000 and success=True
- **THEN** result is `{"passed": True, "rationale": "within baseline"}`

### Requirement: Integration test
The system SHALL have an integration test that runs the full evaluation pipeline using pydantic-evals Dataset: create Dataset with cases and evaluators → run evaluate_sync() → verify EvaluationReport returned with correct case count.

#### Scenario: End-to-end evaluation
- **WHEN** `run_evaluation(dataset=my_dataset, task_function=my_agent, targets=[])` is called
- **THEN** pydantic-evals Dataset evaluation runs and EvaluationReport is returned

#### Scenario: MLflow logging
- **WHEN** `run_evaluation(dataset=my_dataset, task_function=my_agent, targets=["mlflow"])` is called with mocked MLflow
- **THEN** `_log_to_mlflow()` is called with the report
