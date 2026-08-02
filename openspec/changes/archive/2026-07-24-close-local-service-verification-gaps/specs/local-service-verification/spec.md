## ADDED Requirements

### Requirement: Every service has a fail-closed local verification gate
Each service SHALL expose a default local verification target that runs static
checks, unit tests, race tests, compatibility checks, required fuzz regression,
and the configured coverage threshold. A missing tool, test suite, manifest, or
invalid numeric result MUST fail the target rather than print a skip or success.

#### Scenario: Required verification component is absent
- **WHEN** a service verification target references a missing validator, fuzz suite, manifest, or deployment file
- **THEN** the target exits non-zero and identifies the missing component

#### Scenario: Threshold override is not supplied
- **WHEN** a developer runs the default service or root verification target
- **THEN** the repository's real coverage threshold is enforced without a diagnostic override

### Requirement: Coverage measurement is numeric and reproducible
Every service SHALL generate a coverage profile from a successful test run,
extract exactly one numeric aggregate percentage, retain package-level detail,
and enforce at least 80% aggregate statement coverage. Test output or a failed
test command MUST NOT be interpreted as a passing percentage.

#### Scenario: Service is below threshold
- **WHEN** the numeric aggregate coverage is below 80%
- **THEN** verification exits non-zero and reports the service, measured percentage, and threshold

#### Scenario: Test run fails before coverage calculation
- **WHEN** any test fails while generating the coverage profile
- **THEN** verification reports the test failure and does not replace it with a synthetic passing coverage value

### Requirement: Default unit tests do not require live infrastructure
Tests that require another service, PostgreSQL, Redis, Kafka, Temporal, or
another live process SHALL use an explicit integration or end-to-end build tag
and SHALL run only after their declared prerequisites are ready.

#### Scenario: Default service tests run on a clean host
- **WHEN** a developer runs `go test ./...` without local service containers
- **THEN** unit and architecture tests complete without DNS, port, or credential failures

#### Scenario: Live contract smoke test runs without prerequisites
- **WHEN** a live-stack smoke test is selected but its declared dependency is unavailable
- **THEN** the tagged acceptance command fails with a transport diagnostic rather than contaminating the default unit gate

### Requirement: Required fuzz suites are executable
Inventory and shipping, plus any service whose default verification policy
declares a required fuzz suite, SHALL provide fuzz targets for the declared
untrusted HTTP, event, or contract parsing boundaries, committed seed corpora,
a deterministic regression mode, and a bounded short-fuzz mode. A service
Makefile MUST fail if it declares a required fuzz target whose implementation
is missing.

#### Scenario: Regression corpus executes
- **WHEN** inventory, shipping, or another service with a declared required fuzz suite runs its per-commit fuzz regression target
- **THEN** every committed seed executes without panic and invalid inputs return typed validation errors

#### Scenario: Fuzz implementation is missing
- **WHEN** a declared fuzz target has no runner or fuzz package
- **THEN** service verification exits non-zero and identifies the service

### Requirement: Generated contract verification distinguishes external failure
Contract-owning services SHALL use pinned Buf and generator versions, validate
source contracts, and compare deterministic generated output. Authentication,
quota, or network failure from a required remote plugin MUST be reported as an
external tooling failure and MUST NOT be treated as successful generation.

#### Scenario: Generated output is stale
- **WHEN** pinned generation succeeds and changes committed contract bindings
- **THEN** verification exits non-zero and reports the generated files that differ

#### Scenario: Remote plugin quota is exhausted
- **WHEN** the pinned generator cannot run because the remote registry rejects the request for quota or authentication
- **THEN** verification exits non-zero with the external failure category and does not claim contract incompatibility or success

### Requirement: Architecture checks are trimpath and order independent
Architecture tests SHALL locate their module without depending on absolute
runtime source paths and SHALL terminate under `go test -trimpath`. Tests that
inspect unordered collections MUST select records by stable identity rather
than iteration position.

#### Scenario: Trimpath architecture suite runs
- **WHEN** a service architecture suite runs with `-trimpath` and the race detector
- **THEN** module discovery terminates and all checks operate on the intended service root

#### Scenario: Shuffled unit suite runs
- **WHEN** service tests run with a deterministic shuffle seed
- **THEN** assertions remain stable and do not depend on map iteration or prior test order
