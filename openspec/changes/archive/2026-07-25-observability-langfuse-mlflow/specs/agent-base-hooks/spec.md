## MODIFIED Requirements

### Requirement: otel_metrics hook pack
The `otel_metrics` hook pack SHALL continue to record per-tool latency and count via OTel metrics instruments (existing behavior at `builtins.py:84-132`). No changes to this hook pack.

#### Scenario: Tool metrics recorded via OTel
- **WHEN** a tool invocation completes
- **THEN** an OTel metric `agent_core.tool.calls` is incremented and `agent_core.agent.run.duration` is recorded (existing behavior unchanged)

### Requirement: Hook double-fire awareness
Langfuse and MLflow hook packs SHALL be aware that `HookPoint.RUN` BEFORE/AFTER hooks fire twice per run: once from `BaseAgent.run()` directly (agent.py:234,337) and once from the `HookAdapter` bridging pydantic-ai (hooks.py). Tool and model hooks fire once (via HookAdapter only). Hook packs SHALL use a deduplication flag in the context dict to prevent double-recording of scores and metrics.

#### Scenario: Scores recorded once despite double-fire
- **WHEN** `HookPoint.RUN` AFTER hooks fire (twice per run)
- **THEN** Langfuse score recording happens only on the first fire (second fire is a no-op due to dedup flag `_langfuse_scores_recorded=True` in context)

### Requirement: cost_tracker hook pack
The `cost_tracker` hook pack SHALL continue to hook into `HookPoint.MODEL_REQUEST` (as it does today at `builtins.py:249`) to track per-call cost via the LLM gateway's `LLMUsage.cost_usd` field. Cost data SHALL be accumulated in `CostTrackerState` (existing) AND additionally logged to Langfuse (as trace cost) and MLflow (as metric `cost_usd`) when those backends are configured.

#### Scenario: Cost tracked to Langfuse
- **WHEN** an agent run makes LLM calls with total cost $0.05
- **THEN** the Langfuse trace shows cost $0.05 in the cost dashboard (recorded via `langfuse.trace(cost=...)` after run completes)

#### Scenario: Cost tracked to MLflow
- **WHEN** an agent run makes LLM calls with total cost $0.05
- **THEN** the MLflow run has metric `cost_usd=0.05` (logged via `mlflow.log_metric()` after run completes)

#### Scenario: Existing cost_tracker behavior preserved
- **WHEN** cost_tracker hook fires on `HookPoint.MODEL_REQUEST` AFTER
- **THEN** `CostTrackerState.total_cost_usd` is updated (existing behavior unchanged)

### Requirement: structured_audit hook pack
The `structured_audit` hook pack SHALL continue to write JSONL audit records for backward compatibility. Additionally, the same audit data SHALL be available as Langfuse trace attributes (since traces are inherently append-only and immutable).

#### Scenario: JSONL audit trail maintained
- **WHEN** an agent run completes
- **THEN** a JSONL record is written to the audit log file (existing behavior)

#### Scenario: Audit data in Langfuse trace
- **WHEN** an agent run completes and Langfuse is configured
- **THEN** the Langfuse trace contains the same audit fields (run_id, agent_name, tools_used, etc.) as trace attributes

### Requirement: approval_gate hook pack
The `approval_gate` hook pack SHALL continue to function unchanged. Approval requests SHALL be recorded as Langfuse trace events when Langfuse is configured.

#### Scenario: Approval gate functions
- **WHEN** an agent requests human approval
- **THEN** the approval gate pauses execution (existing behavior)

#### Scenario: Approval recorded in Langfuse
- **WHEN** an approval gate triggers and Langfuse is configured
- **THEN** a Langfuse trace event `approval_requested` is recorded with the approval details
