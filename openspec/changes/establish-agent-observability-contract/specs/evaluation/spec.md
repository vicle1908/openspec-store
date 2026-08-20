## ADDED Requirements

### Requirement: Evaluation records carry trace linkage

`EvalRecord` SHALL include nullable `trace_id` and `span_id` fields. When an active OTel span exists during evaluation, these fields SHALL be populated. When no active span exists, they SHALL be `None`.

#### Scenario: Evaluation with active trace

- **WHEN** an evaluation runs inside an active OTel span
- **THEN** `EvalRecord.trace_id` SHALL be set to the active trace ID
- **AND** `EvalRecord.span_id` SHALL be set to the root span ID
- **AND** the database schema SHALL include `trace_id` and `span_id` columns

#### Scenario: Evaluation without active trace

- **WHEN** an evaluation runs outside any OTel span context
- **THEN** `EvalRecord.trace_id` SHALL be `None`
- **AND** `EvalRecord.span_id` SHALL be `None`
- **AND** the evaluation SHALL still be recorded successfully

### Requirement: Numeric score aggregation semantics

Evaluation pass-rate calculations SHALL correctly aggregate numeric scores using threshold comparison, not identity comparison with `True`. A score passes when its value meets or exceeds the evaluator threshold.

#### Scenario: Numeric scores aggregated correctly

- **WHEN** an evaluation produces scores `{accuracy: 0.8, cost: 1.0}` with threshold 0.5
- **THEN** the pass-rate SHALL reflect that both scores pass
- **AND** the aggregation SHALL use threshold comparison, not `result.value is True`

#### Scenario: Mixed score types

- **WHEN** an evaluation produces scores `{safety: True, accuracy: 0.3}` with threshold 0.5
- **THEN** the pass-rate SHALL be 0.5 (one pass, one fail)

### Requirement: Evaluation dataset provenance

Evaluation datasets SHALL record the evaluator name and version (when available) alongside each case result. This enables reproducing a specific evaluation run.

#### Scenario: Dataset case includes provenance

- **WHEN** an evaluation case is recorded
- **THEN** the record SHALL include `evaluator_name` and `evaluator_version` (when available)
- **AND** these fields SHALL be queryable for audit purposes
