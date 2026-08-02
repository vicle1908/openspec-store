## Why

The `FeedbackStore` captures episodic run metadata (duration, cost, completion status) but lacks structured evaluation metrics. There are no latency percentiles, no accuracy scoring, no tool success rate tracking, and no regression detection across runs. As agents are deployed to production, teams need observability into quality trends, not just operational metrics. Industry consensus (LangSmith, Logfire, Braintrust, DeepEval) converges on structured metrics with comparison and regression capabilities.

## What Changes

- New `EvalRecord` Pydantic model extending `FeedbackEntry` with structured operational, quality, and behavioral metric fields
- New `agent_memory.eval_metrics` Postgres table with indexed columns for efficient querying
- New `EvalMetrics` class with `record()`, `query()`, `compare()`, and `regressions()` methods
- Auto-recording integration into `AgentRuntime.run()` to capture metrics on every agent run
- CLI command: `agent-core eval report --agent <name> --since 7d` for quick metric summaries

## Capabilities

### New Capabilities
- `structured-eval-metrics`: Structured evaluation records with operational (latency, cost, tokens), quality (success, accuracy), and behavioral (tool usage, retries) metrics, plus query, comparison, and regression detection APIs

### Modified Capabilities
<!-- No existing capabilities are modified — FeedbackStore is extended, not changed -->

## Impact

- **Code:** New `agent_core/evaluation/` module, `agent_core/_ai/agent.py` (auto-record), `agent_core/cli/app.py` (eval command)
- **Tests:** New `tests/evaluation/` directory
- **Dependencies:** None new (extends existing Postgres + Pydantic patterns)
- **Database:** One migration for `eval_metrics` table
- **Backward compatibility:** Fully backward compatible — new module, existing FeedbackStore unchanged
