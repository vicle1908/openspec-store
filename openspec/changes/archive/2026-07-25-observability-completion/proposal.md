## Why

The `observability-langfuse-mlflow` change was archived with 3 known gaps:
1. **Scorer framework not implemented** — `observability/scorers/` directory is empty
2. **Test files not created** — No unit or integration tests for the observability module
3. **Documentation missing** — No `docs/observability.md` or updated config examples

**Key discovery:** Pydantic Evals (`pydantic-evals`) is a mature evaluation framework from the Pydantic team that provides built-in evaluators mapping directly to 5 of our 7 required scorers. This means we can leverage existing, tested code instead of building from scratch.

## What Changes

- **Add `pydantic-evals>=2.18.0,<3` dependency** — provides Dataset, Case, EvaluationReport, and 10 built-in evaluators (EqualsExpected, Equals, Contains, IsInstance, MaxDuration, LLMJudge, GEval, HasMatchingSpan, ConfusionMatrixEvaluator, PrecisionRecallEvaluator)
- **Create thin scorer wrappers** — 2 custom scorers (RegressionScorer, CostScorer) + Langfuse/MLflow integration layer
- **Create evaluation runner** — using pydantic-evals Dataset for orchestration
- **Create test suite** — unit and integration tests for the observability module
- **Create documentation** — architecture, setup, configuration guide

## Capabilities

### New Capabilities

- `scorer-framework`: Evaluation scorers using pydantic-evals built-in evaluators + custom scorers, with Langfuse and MLflow integration
- `observability-tests`: Unit and integration test coverage for the observability module

### Modified Capabilities

None — this change fills gaps from the archived `observability-langfuse-mlflow` change.

## Impact

- **Code**: New files in `observability/scorers/`, `tests/observability/`, `docs/`
- **Dependencies**: Add `pydantic-evals>=1.0.0,<2` to pyproject.toml
- **Risk**: LOW — additive code, leverages battle-tested pydantic-evals framework
- **Lines of code**: ~150 new (down from ~500 with fully custom scorers)
