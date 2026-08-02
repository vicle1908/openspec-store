## ADDED Requirements

### Requirement: Deployment validation is executable and exhaustive

The platform SHALL provide one deployment-validation command that verifies the canonical Compose models, pinned Collector configurations, every Kustomize service/environment overlay, Kubernetes schemas and policies, workload reference integrity, ApplicationSet generation, tracked secrets, and OpenSpec change validity.

#### Scenario: Complete deployment configuration passes

- **WHEN** a developer or CI runs deployment validation on a conforming commit
- **THEN** every required check executes, the command exits zero, and a machine-readable result lists the validated files, commands, tool versions, and commit

#### Scenario: Any required check fails the gate

- **WHEN** a Compose model, Collector config, overlay, reference, ApplicationSet, secret rule, or OpenSpec validation fails
- **THEN** the command exits non-zero and identifies the failing check without reporting overall readiness

### Requirement: Readiness claims require retained evidence

An OpenSpec requirement, task, audit, or deployment report MUST NOT claim `IMPLEMENTED`, `COMPLETE`, `production-ready`, or equivalent current readiness unless its acceptance command passed for the referenced commit and its evidence location is recorded.

#### Scenario: Status is promoted with evidence

- **WHEN** all acceptance scenarios for a capability pass on the target commit
- **THEN** its status may be updated to implemented and includes or references the validation manifest that proves the result

#### Scenario: File presence alone cannot establish implementation

- **WHEN** an artifact exists but rendering, startup, health, or acceptance validation is absent or failing
- **THEN** the capability remains partial or not implemented regardless of manually checked task boxes

#### Scenario: Historical audit is not treated as current

- **WHEN** runtime pins or deployment artifacts change after a dated audit
- **THEN** current readiness requires a new validation manifest and the historical report remains labeled as a snapshot

### Requirement: Clean-environment acceptance prevents stale-state masking

Local and CI acceptance SHALL execute with a unique project or cluster identifier and SHALL prove that required readiness comes from resources created for the tested commit rather than pre-existing containers, volumes, images, or clusters.

#### Scenario: Clean acceptance identifies tested resources

- **WHEN** the acceptance job starts
- **THEN** it records its unique project or cluster identifier, source commit, image identifiers, and initial resource inventory before creating workloads

#### Scenario: Stale resource is detected

- **WHEN** a conflicting resource from another project, commit, or previous failed run would satisfy or obstruct an acceptance check
- **THEN** preflight exits non-zero or isolates the new run and records the stale resource in diagnostics

### Requirement: Non-local secrets are externally sourced

Staging and production rendered manifests SHALL contain ExternalSecret or equivalent external-provider references for sensitive values and MUST NOT contain committed database passwords, API credentials, private keys, or reusable production ACL passwords.

#### Scenario: Production secret reference is valid

- **WHEN** a production service overlay is rendered
- **THEN** each sensitive workload input resolves through a rendered external-secret resource and a validated cluster SecretStore prerequisite

#### Scenario: Committed production credential blocks validation

- **WHEN** tracked configuration or rendered non-local manifests contain a forbidden credential literal or private key
- **THEN** secret validation exits non-zero, identifies the file and category without printing the complete secret, and blocks promotion

### Requirement: Failure evidence is collected before cleanup

Every failed local, CI, staging, or production acceptance run SHALL collect bounded diagnostics before automatic cleanup or rollback.

#### Scenario: Compose failure evidence is retained

- **WHEN** Compose startup or smoke testing fails
- **THEN** service state, health, logs, resolved model metadata, and smoke evidence are collected before project teardown

#### Scenario: Kubernetes failure evidence is retained

- **WHEN** Kubernetes rollout, Argo CD reconciliation, or environment smoke testing fails
- **THEN** rendered manifests, events, workload descriptions, logs, image IDs, and Argo CD status are collected before cleanup or rollback
