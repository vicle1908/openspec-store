## 1. Dependencies & Setup

- [x] 1.1 Add `pydantic-evals>=2.18.0,<3` to `pyproject.toml` dependencies. Run `uv sync` and verify import. pydantic-evals 2.18.0 supports Python 3.10-3.14.
- [x] 1.2 Verify pydantic-evals built-in evaluators work: `MaxDuration`, `HasMatchingSpan`, `ToolCorrectness`, `EqualsExpected`, `Contains`, `LLMJudge`, `TrajectoryMatch`.

## 2. Custom Evaluators

- [x] 2.1 Create `src/agent_core/observability/scorers/__init__.py` with public exports: `CostScorer`, `RegressionScorer`, `run_evaluation`. Re-export pydantic-evals built-in evaluators for convenience.
- [x] 2.2 Create `cost.py` with `CostScorer(Evaluator)`: custom evaluator for cost-per-token efficiency. Accepts `cost_usd` and `tokens_total` from trace metadata. Returns numeric score (0-1).
- [x] 2.3 Create `regression.py` with `RegressionScorer(Evaluator)`: custom evaluator comparing current metrics against baseline. Detects latency >20% or success_rate <-10% regressions. Returns boolean with rationale.

## 3. Evaluation Runner

- [x] 3.1 Create `runner.py` with `run_evaluation(dataset, task_function, targets)` function. Run pydantic-evals Dataset evaluation. Log summary metrics to MLflow via MLflowClient when "mlflow" in targets. Return EvaluationReport.

## 4. Unit Tests

- [x] 4.1 Create `tests/observability/__init__.py` and `tests/observability/test_langfuse_client.py`: test initialization, no-op fallback, score_trace, context manager. Mock Langfuse SDK.
- [x] 4.2 Create `tests/observability/test_mlflow_client.py`: test initialization, no-op fallback, start_run, log_params, log_metrics. Mock MLflow SDK.
- [x] 4.3 Create `tests/observability/scorers/__init__.py` and `test_cost_scorer.py`: test CostScorer with various cost/token combinations. Test edge cases (zero tokens, negative cost).
- [x] 4.4 Create `tests/observability/scorers/test_regression_scorer.py`: test RegressionScorer with mock baseline data. Test regression detection and no-regression scenarios.
- [x] 4.5 Create `tests/observability/test_runner.py`: test run_evaluation with pydantic-evals Dataset and mock task function. Verify EvaluationReport returned and MLflow metrics logged.

## 5. Documentation

- [x] 5.1 Create `docs/observability.md`: architecture overview, Docker Compose setup, pydantic-evals integration, scorer framework usage, configuration reference, troubleshooting.
- [x] 5.2 Update `config.yaml.example` with langfuse/mlflow/collector settings.
