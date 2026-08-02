## ADDED Requirements

### Requirement: Normative scenarios have automated evidence
Every normative scenario in this change SHALL map to at least one stable verification ID in a machine-readable traceability manifest. Each entry SHALL identify the owning capability, test tier, executable command or test name, required environment, and evidence artifact. A scenario SHALL NOT be considered implemented when its mapped verification is missing, skipped without an approved exception, or failing.

#### Scenario: Implementation task is completed
- **WHEN** a task claims to implement a normative requirement
- **THEN** its mapped verification IDs pass and their evidence is linked from the task or CI run

### Requirement: Pull requests pass deterministic fast gates
Every pull request SHALL pass formatting, generated-code cleanliness, dependency and architecture checks, Buf lint and breaking checks, migration parsing, unit tests, race-enabled tests for concurrent packages, and required integration tests. CI SHALL use the pinned Go toolchain, SHALL disable result caching for release-significant test runs, and SHALL publish machine-readable test and coverage output.

#### Scenario: Pull request changes command concurrency
- **WHEN** a pull request changes command handling, repository concurrency, consumer receipt handling, or worker lifecycle code
- **THEN** the relevant race-enabled and integration suites run and block merge on failure

### Requirement: Critical behavior is verified by properties and faults
The verification suite SHALL include table-driven invariant tests and fuzz targets for untrusted parsers and boundary validation. It SHALL inject the defined crash windows between database commit, CDC publication, workflow start, receipt transition, and Kafka offset commit. Every injected failure SHALL converge after restart without losing a committed Order event or repeating a committed business effect.

#### Scenario: Orchestrator crashes after workflow start
- **WHEN** the orchestrator starts the deterministic workflow and terminates before marking the receipt `started` or committing the Kafka offset
- **THEN** redelivery reconciles the existing workflow, marks the receipt `started`, commits the offset, and does not create a second workflow execution

### Requirement: Contracts, migrations, and workflows remain compatible
CI SHALL run Buf breaking checks against the configured main-branch baseline, migrate a fresh PostgreSQL database to head, upgrade a database fixture from the immediately previous release, and replay retained Temporal histories against the candidate worker. Compatibility fixtures SHALL be version controlled and updated only with an explicit compatibility review.

#### Scenario: Candidate worker changes workflow code
- **WHEN** a candidate modifies workflow control flow, activity invocation, signal or update handling, or workflow data types
- **THEN** every retained compatible history replays without nondeterminism before release

### Requirement: The local topology is reproducible
The smoke suite SHALL render Compose configuration, start the pinned stack from empty volumes, wait for health rather than fixed sleeps, verify idempotent infrastructure initialization, execute the Order creation-to-workflow path, restart with retained volumes, and tear down cleanly. Required images SHALL be checked for the target architectures before a pin is accepted.

#### Scenario: Clean checkout on arm64
- **WHEN** the smoke suite runs from a clean checkout with empty volumes on a supported arm64 host
- **THEN** all required services become healthy without emulation or manual setup and the end-to-end probe completes

### Requirement: Security verification blocks known reachable risk
Pull requests and release candidates SHALL run `govulncheck` for reachable Go vulnerabilities, scan repository and built-image dependencies and configuration with the pinned scanner, detect committed secrets, and produce an SBOM for the release image. A release SHALL contain no unapproved reachable High or Critical vulnerability; every exception SHALL identify an owner, rationale, compensating control, and expiry date.

#### Scenario: Reachable High vulnerability is detected
- **WHEN** a scanner reports a reachable High vulnerability in the candidate application
- **THEN** the release gate fails unless a non-expired, reviewed exception is recorded

### Requirement: Performance and recovery have measurable release gates
A release candidate SHALL pass version-controlled k6 smoke and reference-load scenarios on a declared environment. The MVP reference gate SHALL sustain 25 successful create-order requests per second for five minutes with HTTP error rate below 1%, create-order latency p95 below 500 ms and p99 below 1 s, and committed-order-to-workflow-start latency p95 below 10 s with no lost events. Recovery tests SHALL verify eventual drain after broker, connector, orchestrator, worker, and database interruptions. These local reference thresholds SHALL NOT be represented as production SLOs.

#### Scenario: Reference load exceeds an asynchronous latency threshold
- **WHEN** committed-order-to-workflow-start p95 is 10 seconds or greater, an event is lost, or any k6 threshold fails
- **THEN** the release gate fails and retains request, outbox, connector, consumer, and workflow diagnostics

### Requirement: Verification evidence is reproducible and retained
Each CI verification run SHALL record commit SHA, dirty-state indicator, tool and image versions or digests, architecture, random or shuffle seed, commands, start and end times, and pass/fail status. Release evidence SHALL include JUnit or Go JSON results, coverage, Buf reports, migration results, replay results, security reports and SBOM, Compose service state and logs on failure, and k6 summaries. Pull-request evidence SHALL be retained for at least 30 days and release evidence for at least one year.

#### Scenario: Verification failure is investigated
- **WHEN** a required gate fails
- **THEN** an engineer can identify the exact source revision, environment, command, seed, failed verification ID, and relevant diagnostics without rerunning the job

### Requirement: Phase completion is evidence gated
A phase SHALL be complete only when all tasks are checked, every in-scope normative scenario is mapped and passing, required gates have evidence, no required test is silently skipped, and all temporary exceptions have an owner and expiry. Manual exploratory checks MAY supplement but SHALL NOT replace required automated evidence.

#### Scenario: MVP release candidate is proposed
- **WHEN** the team proposes the MVP as ready for release
- **THEN** the traceability manifest has no unmapped or failing in-scope scenario and the PR, compatibility, smoke, security, recovery, and reference-load gates all pass
