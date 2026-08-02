## Context

The `observability-langfuse-mlflow` change created LangfuseClient and MLflowClient wrappers but left the scorer framework empty. Research reveals that **pydantic-evals** (part of the Pydantic ecosystem) provides built-in evaluators that cover 5 of our 7 required scorers.

Existing code patterns:
- `LangfuseClient` at `observability/langfuse_client.py` — no-op fallback, score_trace() method
- `MLflowClient` at `observability/mlflow_client.py` — no-op fallback, start_run/log_params/log_metrics
- Hook packs in `agent_base/hooks/builtins.py` — langfuse_hooks(), mlflow_hooks()
- pydantic-evals provides: Dataset, Case, EvaluationReport, 8+ built-in evaluators

## Goals / Non-Goals

**Goals:**
- Leverage pydantic-evals for 5 of 7 evaluators (Latency, ToolUsage, Correctness, Relevance, PlanAdherence)
- Create 2 custom evaluators (CostScorer, RegressionScorer) that pydantic-evals doesn't provide
- Integrate evaluation results with Langfuse (via OTel traces) and MLflow (via experiment logging)
- Create comprehensive test coverage (90%+ target)
- Document the scorer framework and observability setup

**Non-Goals:**
- Modify existing LangfuseClient or MLflowClient
- Change hook pack behavior
- Add new Docker services
- Modify existing tests

## Decisions

### D1: Use pydantic-evals as evaluation engine

**Decision:** Use pydantic-evals v2.18.0 (`Dataset`, `Case`, `Evaluator`, `EvaluationReport`) as the core evaluation framework.

**pydantic-evals 2.18.0 features:**
- Python 3.10-3.14 support
- 10 built-in evaluators (case-level + report-level)
- Custom evaluators via `@dataclass class MyEvaluator(Evaluator)` with `evaluate(ctx: EvaluatorContext)` method
- `EvaluatorContext` provides: name, inputs, metadata, expected_output, output, duration, metrics, attributes, span_tree
- Logfire/OTel integration for visualization
- Dataset serialization (YAML/JSON)
- Async evaluation with concurrency control

**Built-in evaluators mapping (13 case-level + 4 report-level):**
| Our Requirement | pydantic-evals Equivalent |
|-----------------|--------------------------|
| LatencyScorer | `MaxDuration(seconds=...)` |
| ToolUsageScorer | `ToolCorrectness(tools=[...])` + `HasMatchingSpan` |
| CorrectnessJudge | `EqualsExpected()` or `LLMJudge(rubric="correct...")` |
| RelevanceJudge | `LLMJudge(rubric="relevant...", include_input=True)` |
| PlanAdherenceJudge | `TrajectoryMatch(expected=[...])` + `HasMatchingSpan` |
| Tool budget | `MaxToolCalls(max_calls=N)` (bonus — no custom needed) |
| Model request budget | `MaxModelRequests(max_requests=N)` (bonus) |
| Argument validation | `ArgumentCorrectness(tool, args)` (bonus) |
| CostScorer | Custom (no equivalent) |
| RegressionScorer | Custom (no equivalent) |

**Rationale:** pydantic-evals is maintained by the Pydantic team, well-tested, has Logfire integration (works with Langfuse via OTLP), and provides Dataset/Case management, EvaluationReport, and span-based evaluation out of the box.

### D2: Custom evaluators for CostScorer and RegressionScorer

**Decision:** Implement `CostScorer` and `RegressionScorer` as custom pydantic-evals `Evaluator` subclasses.

**Rationale:** These are agent-core specific (cost-per-token efficiency, baseline comparison) and have no pydantic-evals equivalent.

### D3: Langfuse integration via OTel traces

**Decision:** pydantic-evals traces are sent to Langfuse via OTel (already configured in agent-core). No additional Langfuse SDK calls needed for evaluation visualization.

**Rationale:** pydantic-evals natively integrates with Logfire/OTel, and Langfuse ingests OTLP traces. Zero additional code for visualization.

### D4: MLflow integration via experiment logging

**Decision:** After running pydantic-evals evaluations, log summary metrics to MLflow via the existing MLflowClient.

**Rationale:** MLflow provides experiment comparison UI that pydantic-evals doesn't. Logging eval results as MLflow metrics enables cross-run comparison.

### D5: Tests use mocks, not real services

**Decision:** Unit tests mock Langfuse and MLflow clients. Integration tests use pydantic-evals Dataset with mock task functions.

**Rationale:** Tests should be fast and deterministic. Real service integration is verified by Docker Compose (already working).

## Risks / Trade-offs

- [Risk] pydantic-evals dependency adds weight → Acceptable, it's a focused library from the Pydantic team
- [Risk] LLM-as-Judge tests need mock LLM responses → Use deterministic mock responses in tests
- [Risk] Regression scorer needs baseline data → Use mock historical data in tests
- [Trade-off] Only 2 custom evaluators needed (vs 7 with fully custom approach)
