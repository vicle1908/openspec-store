## MODIFIED Requirements

### Requirement: Evaluation dataset structure

The system SHALL provide pre-built evaluation datasets for core agent workflows. Evaluation records SHALL support nullable `trace_id` and `span_id` fields for linking to OTel traces. Pass-rate calculations SHALL be derived from boolean assertions and task-level success — not from numeric score thresholds.

#### Scenario: Dataset registry

- WHEN `agent_core.evaluation.datasets` is imported
- THEN it SHALL expose a registry mapping dataset names to Dataset instances
- AND each dataset SHALL have at least 3 cases with metadata

#### Scenario: CLI execution

- WHEN `agent-core eval run --dataset <name>` is executed
- THEN the named dataset SHALL be evaluated using the configured evaluators
- AND results SHALL be printed as JSON with per-case pass/fail
- AND pass/fail SHALL be derived from boolean assertions and task completion, not numeric score thresholds

#### Scenario: Dataset case schema

- WHEN a dataset case is defined
- THEN it SHALL include: id, input (dict), metadata (dict with expected values)
- AND metadata SHALL contain evaluators' expected outcomes for regression checking

## ADDED Requirements

### Requirement: Evaluation-to-trace linkage

`EvalRecord` SHALL include nullable `trace_id` and `span_id` fields. The database schema SHALL include corresponding nullable columns. These fields SHALL be populated from the `EvaluationReport` trace context when a trace is active during evaluation.

#### Scenario: Evaluation with active trace

- WHEN an evaluation runs while an OTel span is active
- THEN `EvalRecord.trace_id` SHALL be set to the `EvaluationReport.trace_id`
- AND `EvalRecord.span_id` SHALL be set to the `EvaluationReport.span_id`

#### Scenario: Evaluation without active trace

- WHEN an evaluation runs outside any OTel span context
- THEN `EvalRecord.trace_id` SHALL be `None`
- AND `EvalRecord.span_id` SHALL be `None`
- AND the evaluation SHALL still be recorded successfully

### Requirement: Evaluation pass/fail semantics

Pass-rate SHALL be derived from boolean assertions (`ReportCase.assertions`) and task-level failures (`ReportCase.evaluator_failures`). Numeric scores (`ReportCase.scores`) SHALL be aggregated separately as measurements with per-evaluator mean and stddev. When no assertions exist, pass rate SHALL be reported as `null` — not defaulted to a universal threshold.

#### Scenario: Boolean assertion pass rate

- WHEN an evaluation produces boolean assertions `{safety: True, accuracy: True}`
- THEN the pass rate SHALL be 1.0

#### Scenario: Mixed assertion and numeric results

- WHEN an evaluation produces `{assertions: {safety: True}, scores: {accuracy: 0.8}}`
- THEN the pass rate SHALL be 1.0 (from boolean assertion)
- AND the accuracy score SHALL be reported separately as a measurement

#### Scenario: No assertions, only numeric scores

- WHEN an evaluation produces only `{scores: {accuracy: 0.8}}`
- THEN the pass rate SHALL be `null`
- AND the accuracy score SHALL be reported as a measurement
