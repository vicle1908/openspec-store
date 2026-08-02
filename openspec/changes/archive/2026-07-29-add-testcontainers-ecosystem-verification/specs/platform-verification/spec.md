## ADDED Requirements

### Requirement: Repository container integration is orchestrated and retained

The repository SHALL provide a root orchestration target that runs every
required service container-integration suite and each required focused
ecosystem cohort in a deterministic order with bounded concurrency. The target
MUST retain per-service and aggregate manifests, verify their schemas and
identities, and exit non-zero for any failed, skipped, missing, stale,
cross-run, uncleaned, or non-native unapproved result.

#### Scenario: All container integration cohorts pass

- **WHEN** the root aggregate container verification target runs on a supported Docker host
- **THEN** every declared service integration suite and focused cohort completes with matching source and run evidence
- **AND** the aggregate manifest reports the exact commands, images, durations, outcomes, and cleanup states

#### Scenario: One service suite is absent

- **WHEN** the repository inventory declares a required integration suite whose command, build tag, fixture, or evidence is missing
- **THEN** root container verification exits non-zero and identifies the owning service and missing component

#### Scenario: Parallel execution exceeds its budget

- **WHEN** the configured resource or concurrency budget cannot safely run another cohort
- **THEN** orchestration queues or serializes the cohort within the declared timeout
- **AND** it does not attach to or reuse another run's resources

#### Scenario: Aggregate evidence references a failed cleanup

- **WHEN** a child manifest records failed or incomplete cleanup
- **THEN** aggregate validation fails even if the child's behavioral assertions passed

### Requirement: Container verification inventory and execution state are explicit

The root verification inventory SHALL record each suite or cohort's owner,
command, build tag, dependency set, expected evidence class, artifact path,
timeout, concurrency weight, and status as `present`, `external-only`, or
`not-configured`. Aggregate evidence MUST distinguish configured workflow
definitions from actually executed runs and MUST fail closed for required
entries that are missing, not configured, or only externally asserted.

#### Scenario: Required inventory entry has no executable command

- **WHEN** a required inventory entry has no runnable command, build tag, fixture, or evidence path
- **THEN** the aggregate target exits non-zero and identifies the incomplete entry
- **AND** no aggregate pass manifest is written

#### Scenario: Workflow is configured but not executed

- **WHEN** the repository contains the Docker-capable workflow definition but no matching hosted run artifact exists
- **THEN** local validation records the workflow as configured-but-unverified
- **AND** it does not convert that state into a passing hosted or release evidence class

### Requirement: Docker-capable CI executes container verification without implying cloud readiness

The repository SHALL declare a Docker-capable CI workflow for relevant
integration changes and manual execution. The workflow MUST use the pinned Go
toolchain, run the service integration and focused ecosystem targets, execute
their negative controls and evidence validators, and upload bounded evidence
on success or failure. The workflow definition and any local result MUST NOT be
represented as confirmed hosted execution, branch-protection enforcement, or
cloud readiness without separate retained external evidence.

#### Scenario: Relevant integration change triggers the workflow

- **WHEN** a change affects the harness, service adapters, migrations, selected Compose files, Shipping lifecycle, or evidence validators
- **THEN** the CI workflow runs the required container verification targets and publishes the per-revision artifact bundle

#### Scenario: Container verification fails in CI

- **WHEN** a required service or focused cohort fails
- **THEN** the workflow exits non-zero and uploads manifests, test output, container state, and redacted logs needed to diagnose the exact revision

#### Scenario: Workflow file exists without a hosted run

- **WHEN** reviewers can inspect the workflow definition but no matching hosted execution artifact is retained
- **THEN** the repository reports the workflow as configured but unverified
- **AND** it does not claim branch-protection, release, staging, or production readiness

#### Scenario: Default pull-request gate runs without live service fixtures

- **WHEN** the standard root pull-request verification target runs outside the container-integration workflow
- **THEN** it remains free from live infrastructure requirements
- **AND** container verification remains a separately named required check according to its declared cadence

### Requirement: Container verification scenarios are traceable

Every normative service-integration and focused-ecosystem scenario SHALL map to
a stable verification identifier, executable command or test name, required
environment, evidence class, and artifact path. A scenario MUST remain
incomplete when its verification is skipped, failing, unmapped, or supported
only by a different evidence class.

#### Scenario: Shipping focused scenario is implemented

- **WHEN** the Shipping ecosystem cohort is claimed complete
- **THEN** each dispatch, replay, conflict, concurrency, recovery, completion, cancellation, persistence, CDC, and Temporal scenario maps to passing focused evidence for the exact source revision

#### Scenario: Service integration scenario maps to full-stack smoke only

- **WHEN** a required service adapter scenario has no service-integration verification and maps only to a full-stack health or smoke result
- **THEN** traceability validation reports the adapter scenario incomplete

#### Scenario: Focused scenario maps to canonical full-stack evidence

- **WHEN** a focused cohort scenario is additionally exercised by the canonical full-stack gate
- **THEN** traceability records both evidence classes without treating either artifact as interchangeable
