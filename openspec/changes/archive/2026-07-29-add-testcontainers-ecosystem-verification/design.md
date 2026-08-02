## Context

The repository has eight independent Go modules, a shared platform module, a
Go cross-service smoke module, and a canonical Docker Compose topology. Four
services currently import Testcontainers for Go `v0.43.0` and start PostgreSQL
directly from their integration tests. Their helpers are duplicated and use
different PostgreSQL versions: most use `postgres:17-alpine`, while the
Shipping repository test and the canonical `deploy/tools.env` pin use
`postgres:18.4-alpine`. The other service integration suites depend on
externally supplied DSNs or fixed localhost ports and may skip when the
environment is absent.

The root `services-verify` target invokes per-service `verify-pr`, which
deliberately excludes live integration tests. Root `verify-release` runs the
canonical Compose smoke path but does not invoke each service's
`test-integration` target. The active
`harden-shipping-dispatch-and-compose-evidence` change separately requires real
Shipping HTTP/Nexus concurrency, lease recovery, PostgreSQL counts, Kafka/CDC
delivery, Temporal terminal state, and exact run/project evidence.

Docker Compose remains the local topology authority. Its base and overlays
encode PostgreSQL logical replication, Kafka KRaft listeners, Debezium plugin
configuration, Temporal schema and namespace initializers, service migrations,
topic and connector initialization, health checks, LGTM, and evidence mounts.
Duplicating that full topology as generic Testcontainers definitions would
create a second configuration source and weaken the readiness contract.

Current official Testcontainers for Go documentation provides a Compose v2
module with an explicit stack identifier, multiple stack files, environment
injection, per-service wait strategies, service-container lookup, bounded
startup, and scoped down operations. It also provides user-defined networks,
network aliases, generic and module-specific containers, cleanup helpers, and
optional container reuse. The repository currently pins a compatible release;
implementation must repeat the official documentation and module-version
check before changing that pin.

The design must work on macOS Apple Silicon and Linux amd64, preserve unrelated
Docker projects and images, keep secrets out of evidence, and remain distinct
from hosted/cloud readiness owned by
`complete-cloud-deployment-and-cicd-readiness`.

## Goals / Non-Goals

**Goals:**

- Provide one test-only harness contract for image resolution, run identity,
  lifecycle, protocol readiness, logs, evidence, and cleanup.
- Make explicitly selected service integration tests self-provisioning and
  fail closed rather than silently skipping required dependencies.
- Add a focused multi-container cohort that reuses existing Compose files and
  proves real Shipping behavior across HTTP, Nexus, PostgreSQL, Kafka,
  Debezium, and Temporal.
- Retain exact, schema-versioned evidence for source, environment, resolved
  images, assertions, diagnostics, and cleanup.
- Preserve fast infrastructure-free default unit and architecture tests.
- Keep the focused Testcontainers result supplemental and retain the
  eight-service Compose manifest as the only canonical full-stack result.
- Provide deterministic local targets and a Docker-capable CI workflow
  definition without claiming that hosted execution has occurred.

**Non-Goals:**

- Replace the canonical Compose or kind lifecycle.
- Reimplement all service and infrastructure definitions as generic
  Testcontainers requests.
- Change REST, Protobuf, Kafka, Temporal, database, or provider contracts.
- Introduce production migrations, credentials, or real carrier calls.
- Treat container startup or a health endpoint as sufficient operational
  evidence.
- Enable reusable containers for release-significant evidence.
- Establish staging, production, Argo CD, or cloud readiness.

## Decisions

### 1. Verification remains a layered contract

The repository will distinguish four layers:

1. **Default verification**: static, unit, architecture, race, compatibility,
   fuzz regression, and coverage; no live service fixture or Testcontainers
   dependency. Existing short-lived tool containers remain separate,
   explicitly named checks.
2. **Service integration**: a disposable dependency fixture for one service
   module, exercising migrations and real adapters.
3. **Focused ecosystem**: a selected service cohort plus its real
   infrastructure boundaries and public operations.
4. **Canonical full stack**: the existing isolated eight-service Compose
   readiness gate.

The service and focused layers produce separate evidence classes and cannot be
promoted to canonical full-stack status. This is preferred over adding all
container work to `verify-pr`, which would make the default developer loop
slow and Docker-dependent, and over replacing Compose, which would duplicate
topology and initializer semantics.

### 2. One test-only module owns reusable Testcontainers infrastructure

A test-only Go module under `tests/ecosystem-verification` will own:

- repository-root and `deploy/tools.env` discovery;
- image and architecture resolution;
- Postgres and network fixtures;
- Compose-stack construction from existing files;
- run identity and artifact paths;
- protocol-level wait helpers;
- log and inspection capture;
- redaction and manifest writing;
- cleanup accounting.

The module will require both
`github.com/testcontainers/testcontainers-go v0.43.0` and
`github.com/testcontainers/testcontainers-go/modules/compose v0.43.0`.
The implementation must compile a minimal Compose fixture against Go 1.26.5
before migrating any service suite; `go list -m -json` and the official
Testcontainers documentation are the compatibility record, not an assumption
that the latest release is interchangeable with the repository pin.

Service integration tests may import its public fixture package through the
repository's existing local-module `require`/`replace` pattern. The harness
does not import service modules or service-private packages, preventing
dependency cycles and preserving Go `internal` boundaries. Focused acceptance
tests live in the same module and interact with services through public
boundaries.

This is preferred over copying helpers into all eight service modules. A
platform production package was rejected because it would make
Testcontainers part of the runtime module graph. A shell-only harness was
rejected because typed lifecycle, cleanup, concurrent assertions, and
machine-readable evidence are easier to enforce in Go.

### 3. Service fixtures use generic or module containers; ecosystem fixtures reuse Compose

Repository and adapter tests will start only the dependencies they own. A
PostgreSQL adapter test uses the repository-pinned PostgreSQL image, a unique
database or schema, canonical migrations, and a readiness strategy that proves
the final server accepts queries. Redis tests use the repository-pinned Redis
image or the existing cluster overlay when cluster behavior is the subject.
Kafka-only platform tests may use a focused broker fixture when they do not
depend on CDC or service roles.

The Shipping ecosystem cohort will use the Testcontainers Compose module with
the existing base, Shipping, Nexus, and required evidence overlays. It will set
a collision-resistant stack identifier, inject the exact run and evidence
environment, attach bounded waits to required roles, start with Compose wait
semantics, and inspect service containers through the Testcontainers API.
Because the rendered stack contains `shipping-service:local` and
`platform-otel-collector:local` build entries, the harness will preflight the
build contexts, build those images from the exact checkout, capture their image
IDs/digests and build commands, and reject a missing or unrelated local image.
It will not silently use a developer's pre-existing image as source-revision
evidence.

Individual generic definitions for PostgreSQL, Kafka, Debezium, Temporal, and
all Shipping roles were rejected for ecosystem verification because they
would copy listener, schema-init, connector, namespace, health, and volume
configuration already owned by Compose.

### 4. Runtime pins have one source and no silent substitution

The harness will resolve runtime image tags from `deploy/tools.env`. Missing
pins, malformed files, unavailable images, or unsupported host architecture
fail before the cohort starts. Evidence records the declared reference, local
image ID, resolved digest when available, platform, and any approved emulation
fallback. A fallback is never selected implicitly.

Test-only Go modules will use one verified Testcontainers for Go version and
the matching Compose module. The implementation will check the currently
pinned versions and current official documentation with Go module tooling
before any update; no dependency upgrade is required merely to create the
harness.

Hard-coded image fallbacks in service helpers will be removed. Diagnostic
overrides may be accepted only through explicit test variables and must be
recorded in evidence; they do not satisfy release-significant compatibility
evidence.

### 5. Readiness is protocol-level and bounded

Every container or Compose service has a startup context and a declared
strategy. Port-open or process-health checks are only the first layer:

- PostgreSQL must accept a query after canonical migration.
- Kafka must return metadata and complete a produce/consume probe.
- Debezium must report the expected connector and task state.
- Temporal must expose the expected namespace, endpoint, worker registration,
  and workflow execution.
- Service APIs must pass startup/readiness and a representative public
  operation.

Compose `Up(..., compose.Wait(true))` is not sufficient for one-shot
initializers. The harness must inspect every required initializer after startup
and fail if its exit status is non-zero, absent, or not reached before the
bounded deadline. Long-running services use explicit `WaitForService`
strategies; fixed sleeps are prohibited except as bounded polling intervals.

Any wait timeout fails the selected target and records container state and logs.

### 6. Lifecycle ownership and cleanup are explicit

Each invocation derives a run ID and a label-safe stack or network identity.
The harness proves the exact identity is absent before claiming ownership.
Service fixtures use unique networks, databases, volumes, and host port
mappings. The Compose cohort uses an explicit stack identifier and does not
attach to the default development project.

Cleanup first captures redacted diagnostics, then terminates only owned
containers and networks or downs only the owned Compose stack with orphans and
volumes removed. It never deletes shared images by default. The Compose
lifecycle always calls `Down` and then `Close`; the latter releases the
Testcontainers Docker client and Compose client even when the assertion fails.
The Reaper is enabled for ordinary disposable fixtures unless a documented CI
policy disables it, in which case the explicit ownership cleanup remains
mandatory. Cleanup status is part of the final result, and cleanup failure
makes the selected target fail.

Container reuse is disabled for CI, release, recovery, and evidence runs.
An explicit local diagnostic reuse mode may be added later, but its result
must be labeled non-authoritative and cannot feed an acceptance manifest.

### 7. Evidence has an independent focused schema

The harness writes
`artifacts/verification/local/testcontainers/<run-id>/manifest.json` using
`microservices.testcontainers-ecosystem/v1`. The manifest includes:

- source revision and dirty-state indicator;
- run ID, cohort, evidence class, start/end times, and host platform;
- exact Compose files or fixture definitions;
- declared and resolved image identities;
- required services, waits, commands, and assertion outcomes;
- public operation and dependency observations;
- referenced child artifacts with hashes;
- redacted failure diagnostics;
- ownership and cleanup outcome.

The allowed evidence classes are `service-integration` and
`focused-ecosystem`. Validators reject missing identity, stale or cross-run
artifacts, unexpected image substitutions, missing required checks, leaked
secret-shaped values, skipped required tests, and incomplete cleanup.

The existing Compose acceptance validator may reference the focused manifest
as supplemental evidence, but it must reject it as a replacement for
`canonical-full-stack`.

### 8. Shipping uses one domain assertion driver

The first ecosystem cohort will satisfy the active Shipping scenarios by
executing real dispatch, exact replay, conflicting input, concurrent HTTP and
Nexus duplicates, injected crash and lease-expiry recovery, completion,
cancellation, PostgreSQL inspection, Kafka consumption, Debezium connector
inspection, and Temporal terminal-state inspection.

The cohort will reuse or extract one canonical Shipping assertion driver
rather than maintain separate shell and Go interpretations. The driver accepts
explicit endpoints and run/project identity and emits a child manifest. The
Testcontainers harness owns environment lifecycle; the Shipping change owns
the domain assertions and accepted side-effect counts.

Neither the service Postgres fixture nor a health-only cohort may satisfy the
Shipping operational scenarios.

### 9. Explicit targets fail closed and CI remains scope-aware

The root will expose separate targets for one service integration suite, all
configured service integration suites, the focused ecosystem cohort, evidence
validation, negative controls, and their aggregate. The inventory explicitly
labels a suite `present`, `external-only`, or `not-configured`; the aggregate
fails when a required suite is absent or not configured rather than treating it
as a pass. Selecting a container target requires a reachable Docker API;
absence is a failure, not a skip. Individual service targets remain available
for iteration.

A Docker-capable CI workflow definition will run container-backed service
integration and focused cohorts on relevant changes and manual dispatch,
uploading evidence even on failure. Default `verify-pr` remains free of live
service fixtures, while existing Docker tool-container checks remain visible
in its evidence. Release wiring becomes blocking only after the new targets
pass their focused negative controls and an initial cross-platform soak.
Hosted workflow-run proof and branch-protection configuration remain tasks of
the cloud delivery change.

### 10. Security and observability treat Docker as a privileged boundary

The harness will start only repository-declared, pinned images and existing
Compose files. It will not accept arbitrary image names from untrusted test
input, mount unrelated host directories, or print credentials, DSNs, provider
payloads, or Docker authentication data. Docker socket access remains confined
to the host-side verification process and documented CI runner.

Structured logs include run ID, cohort, service, phase, duration, image
identity, and outcome. Logs and manifests use the repository's redaction
patterns, bounded size, and failure-first retention policy.

### 11. Execution contract and source-of-truth paths

The implementation will keep the following ownership boundaries explicit:

| Concern | Planned owner | Required evidence |
| --- | --- | --- |
| Reusable fixtures and Compose lifecycle | `tests/ecosystem-verification` | unit/lifecycle tests and child manifests |
| Versioned evidence schema | `verification/schemas/testcontainers-ecosystem-v1.schema.json` | schema validation and negative controls |
| Root orchestration and inventory | root `Makefile` plus `verification/testcontainers-ecosystem.yaml` | aggregate manifest and command matrix |
| Shipping domain assertions | existing Shipping verification driver or its extracted package | Shipping child manifest bound to run/project |
| Canonical full-stack readiness | `make local-operational-readiness` | `canonical-full-stack` manifest only |

The focused target will build local Compose images before invoking the
Testcontainers Compose stack, run the service and initializer checks, write
`artifacts/verification/local/testcontainers/<run-id>/manifest.json`, validate
that manifest, and perform scoped cleanup. A successful focused run is not a
successful canonical readiness run.

## Risks / Trade-offs

- **[Risk] Docker-backed gates increase latency and resource use.** →
  Share one dependency fixture within a service suite, use focused cohorts,
  bound concurrency, pre-pull pinned images in CI, and keep the default PR gate
  free of live service fixtures. Existing tool-container checks remain
  separately visible.
- **[Risk] Testcontainers Compose behavior diverges from direct `docker
  compose`.** → Use the same Compose files and environment, retain a
  same-revision comparison test, and keep direct Compose readiness
  authoritative.
- **[Risk] A port or health check passes before the dependency is usable.** →
  Require protocol-level probes and representative operations before marking a
  dependency ready.
- **[Risk] Cleanup removes unrelated work.** → Use unique identities, prove
  absence before ownership, remove only owned containers/networks/volumes, and
  never remove shared images by default.
- **[Risk] Parallel cohorts exhaust a developer workstation.** → Apply a
  bounded concurrency budget, unique networks and ports, and resource
  preflight; serialize the heavy Shipping cohort.
- **[Risk] Container reuse masks migration or recovery defects.** → Disable
  reuse for authoritative evidence and label any future local reuse mode
  diagnostic-only.
- **[Risk] Shared test helpers become a runtime dependency.** → Keep them in a
  test-only module imported only by tagged test code.
- **[Risk] Evidence exposes credentials or payloads.** → Record identities and
  counts rather than raw configuration or messages, run redaction validation,
  and retain bounded logs.
- **[Risk] A focused pass is interpreted as deployment readiness.** → Enforce
  evidence classes in schema validators and documentation; require the
  canonical Compose manifest for full local readiness and separate hosted
  proof for cloud readiness.

## Migration Plan

1. Inventory every integration suite, dependency, build tag, skip path, image
   source, migration runner, and current CI invocation; retain a baseline
   matrix.
2. Create the test-only harness module, image-pin loader, run identity,
   lifecycle helpers, evidence schema, redaction, validators, and negative
   controls.
3. Migrate the existing customer, inventory, payment, and Shipping PostgreSQL
   suites to the shared fixture and canonical PostgreSQL pin.
4. Convert order, notification, catalog, and reporting database/Redis suites
   from external or localhost assumptions to explicit fixtures, preserving
   service-owned migrations and cleanup.
5. Add the Testcontainers-managed Shipping Compose cohort and connect it to the
   canonical Shipping assertion driver and active-change evidence.
6. Add root targets, traceability mappings, documentation, and the
   Docker-capable CI workflow definition; run the service and focused cohorts
   on arm64 and amd64 where available.
7. After a stable soak and passing negative controls, make the aggregate
   container verification target part of the release-significant gate without
   changing canonical full-stack evidence classification.

Rollback removes the aggregate and focused target wiring, restores the prior
service-local integration helpers and module dependencies, and leaves the
existing Compose readiness commands intact. Because all fixtures are isolated
and disposable, rollback requires no application data migration or persistent
volume recovery.

## Resolved Execution Policy

- The retained macOS arm64 and Linux amd64 baselines set lightweight fixture
  concurrency to two, serialize the focused Shipping cohort, and use 15-minute
  service and 20-minute focused CI job timeouts.
- Relevant pull requests run both the service and focused workflow jobs;
  `workflow_dispatch` remains available for explicit reruns. The aggregate
  container target is release-significant through `verify-release`, while
  `verify-pr` remains free of live service fixtures.
- Branch-protection required-status enforcement remains an external repository
  configuration concern and is recorded as unverified until independently
  confirmed.
