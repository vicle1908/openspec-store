# agent-core-quality-gate Delta Specification

## ADDED Requirements

### Requirement: CI workflow includes secret scanning

Every agent-ecosystem repo SHALL have a `.github/workflows/ci.yml` that
includes gitleaks secret scanning with `fetch-depth: 0` and the pinned
gitleaks image version.

#### Scenario: CI workflow exists with gitleaks config
- **WHEN** `test_secret_scanning_policy.py` reads `.github/workflows/ci.yml`
- **THEN** the file SHALL contain `fetch-depth: 0`
- **AND** the file SHALL reference the pinned gitleaks image
- **AND** the test SHALL pass

### Requirement: Module test ratio baseline

Agent-core modules SHALL maintain a minimum test ratio of 0.50 (test LOC / src
LOC). Modules below this threshold SHALL have a tracked improvement plan.

#### Scenario: llm_gateway meets ratio target
- **WHEN** the llm_gateway module test ratio is measured
- **THEN** it SHALL be ≥ 0.50
- **AND** the ratio SHALL be recorded in SPEC_INDEX.md

#### Scenario: foundation meets ratio target
- **WHEN** the foundation module test ratio is measured
- **THEN** it SHALL be ≥ 0.50
- **AND** the ratio SHALL be recorded in SPEC_INDEX.md

#### Scenario: cli meets ratio target
- **WHEN** the cli module test ratio is measured
- **THEN** it SHALL be ≥ 0.50
- **AND** the ratio SHALL be recorded in SPEC_INDEX.md
