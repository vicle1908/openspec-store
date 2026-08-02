## ADDED Requirements

### Requirement: Effective risk threshold transparency

Resource-overload and timeline-risk rules SHALL obtain their effective thresholds and weights from one documented configuration source. Default and project-override values MUST be covered by tests, and diagnostic configuration output SHALL expose the effective non-secret values used for a run.

#### Scenario: Default overload rule is evaluated

- **WHEN** no project override is configured
- **THEN** the analyzer uses the documented default overload threshold and weight
- **AND** a boundary test verifies the first workload count that triggers the risk

#### Scenario: Project risk threshold is overridden

- **WHEN** a project config overrides a supported risk threshold
- **THEN** the analyzer uses that value for the matching project
- **AND** configuration inspection reports the effective value
