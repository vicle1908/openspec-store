# cli-provider-profile-resolution Delta Specification

## MODIFIED Requirements

### Requirement: Consumer implementation claims require canonical API evidence

Every installed CLI consumer that claims canonical provider integration MUST provide verifiable evidence that its implementation matches the canonical API contract. Claims without evidence SHALL be treated as unverified.

#### Scenario: Consumer claims require evidence

- **WHEN** a consumer claims canonical API integration
- **THEN** the claim MUST include verifiable evidence (test results, API response captures, or schema validation proofs)
- **AND** claims without evidence SHALL be rejected

### Requirement: Identity-bound live CLI acceptance evidence

Live CLI acceptance evidence MUST be bound to the exact CLI identity (version, configuration, runtime environment) at the time of execution. Evidence from a different identity SHALL NOT be used to validate the current identity.

#### Scenario: Evidence is identity-bound

- **WHEN** live CLI acceptance evidence is captured
- **THEN** the evidence MUST include the exact CLI identity (version, config hash, runtime env)
- **AND** evidence from a different identity SHALL be rejected

### Requirement: Automated artifact and dependency drift validation

Artifact and dependency drift MUST be automatically validated before each release. Drift detection MUST cover source files, dependencies, configurations, and generated artifacts.

#### Scenario: Drift detection runs automatically

- **WHEN** a release is prepared
- **THEN** automated drift detection MUST run against all tracked artifacts
- **AND** drift findings MUST be classified and resolved before release
