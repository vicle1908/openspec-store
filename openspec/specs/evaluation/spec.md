## Purpose

This specification defines requirements for Evaluation.

## Requirements

### Requirement: Workflow Quality Evaluation

The harness SHALL evaluate workflow quality using agent-core's pydantic-evals integration.

#### Scenario: Evaluation dataset
- **WHEN** evaluating the harness
- **THEN** the harness SHALL define evaluation cases with:
  - `Case`: Input ticket + expected output artifact
  - `Evaluator`: Quality criteria (duration, tool correctness, cost)
  - `Dataset`: Collection of cases for batch evaluation

#### Scenario: Built-in evaluators
- **WHEN** running evaluations
- **THEN** the harness SHALL use these evaluators:
  - `MaxDuration(seconds=300)` — workflow must complete within 5 minutes
  - `ToolCorrectness(tools=["gitnexus_query", "graphify_path"])` — correct tools used
  - `CostScorer()` — cost efficiency score
  - `RegressionScorer()` — regression against baseline
  - `LLMJudge(rubric="Artifact is complete and accurate")` — quality judgment

#### Scenario: Custom evaluators
- **WHEN** domain-specific evaluation is needed
- **THEN** the harness SHALL implement custom evaluators:
  - `ArtifactCompleteness` — checks all required fields are present
  - `SourceRefVerification` — checks all source_refs are verified
  - `TraceChainIntegrity` — checks trace chain is complete
  - `GateApprovalRate` — checks approval/rejection ratio

### Requirement: Stage Quality Metrics

The harness SHALL track quality metrics per stage.

#### Scenario: Per-stage metrics
- **WHEN** a stage completes
- **THEN** the harness SHALL record:
  - `duration_ms` — execution time
  - `tool_calls` — number of tool invocations
  - `validation_tier` — highest tier applied
  - `validation_result` — pass/fail/flagged
  - `artifact_size` — artifact field count
  - `source_refs_count` — number of references

#### Scenario: Aggregated metrics
- **WHEN** a workflow completes
- **THEN** the harness SHALL aggregate:
  - `total_duration_ms` — sum of all stage durations
  - `total_tool_calls` — sum of all tool invocations
  - `validation_failures` — count of failed validations
  - `gate_approvals` — count of gate approvals
  - `gate_rejections` — count of gate rejections
  - `backtrack_count` — count of backtrack events

### Requirement: Evaluation Reporting

The harness SHALL generate evaluation reports for analysis.

#### Scenario: Langfuse scoring
- **WHEN** a workflow completes
- **THEN** the harness SHALL score the trace via `LangfuseClient.score_trace()`
- **THEN** scores SHALL include:
  - `cost_efficiency` — from CostScorer
  - `regression` — from RegressionScorer
  - `quality` — from LLMJudge (if configured)

#### Scenario: MLflow experiment logging
- **WHEN** a workflow completes
- **THEN** the harness SHALL log to MLflow:
  - `params`: ticket_id, stage_count, gate_count
  - `metrics`: total_duration, total_cost, validation_failures
  - `artifacts`: verification_report.md

#### Scenario: Evaluation dataset export
- **WHEN** exporting evaluation data
- **THEN** the harness SHALL export:
  - `Dataset` format for pydantic-evals
  - `CSV` format for spreadsheet analysis
  - `JSON` format for programmatic access

### Requirement: Regression Detection

The harness SHALL detect quality regressions across runs.

#### Scenario: Baseline comparison
- **WHEN** a workflow completes
- **THEN** the harness SHALL compare against baseline:
  - Duration regression: >20% slower than baseline
  - Cost regression: >20% more expensive than baseline
  - Quality regression: LLMJudge score < baseline score

#### Scenario: Regression alerting
- **WHEN** a regression is detected
- **THEN** the harness SHALL:
  - Log warning with regression details
  - Flag in verification report
  - (Future) Send alert to monitoring system

### Requirement: Evaluation Configuration

The harness SHALL configure evaluation via ConsumerConfig.

#### Scenario: Evaluation config fields
- **WHEN** HarnessConfig is instantiated
- **THEN** it SHALL include:
  - `evaluation_enabled: bool` — enable/disable evaluation (default: true)
  - `evaluation_dataset_path: str | None` — custom dataset path
  - `evaluation_targets: list[str]` — scoring targets (langfuse, mlflow)
  - `evaluation_timeout_seconds: int` — max evaluation time (default: 60)
  - `regression_threshold: float` — regression threshold (default: 0.2)
