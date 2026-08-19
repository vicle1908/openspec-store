## ADDED Requirements

### Requirement: Evaluation dataset structure
The system SHALL provide pre-built evaluation datasets for core agent workflows.

#### Scenario: Dataset registry
- WHEN `agent_core.evaluation.datasets` is imported
- THEN it SHALL expose a registry mapping dataset names to Dataset instances
- AND each dataset SHALL have at least 3 cases with metadata

#### Scenario: CLI execution
- WHEN `agent-core eval run --dataset <name>` is executed
- THEN the named dataset SHALL be evaluated using the configured evaluators
- AND results SHALL be printed as JSON with per-case pass/fail

#### Scenario: Dataset case schema
- WHEN a dataset case is defined
- THEN it SHALL include: id, input (BaseModel), metadata (dict with expected values)
- AND metadata SHALL contain evaluators' expected outcomes for regression checking
