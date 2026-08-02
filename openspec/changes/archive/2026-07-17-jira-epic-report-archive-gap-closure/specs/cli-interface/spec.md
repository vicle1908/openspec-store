## ADDED Requirements

### Requirement: Verification evidence provenance

Automated CLI verification and manual live Jira smoke verification SHALL be recorded separately. A live smoke record MUST identify the verification date, requested epic scope, output formats, and outcome without storing credentials or sensitive Jira payloads.

#### Scenario: Dashboard live smoke succeeds

- **WHEN** an operator runs the documented dashboard smoke procedure against live Jira
- **THEN** the verification record identifies the epic scope and generated output formats
- **AND** it does not claim that the run is an automated integration test

#### Scenario: Empty dashboard input is tested

- **WHEN** the automated suite supplies an empty collected-item result
- **THEN** it verifies the documented CLI exit behavior and operator message
