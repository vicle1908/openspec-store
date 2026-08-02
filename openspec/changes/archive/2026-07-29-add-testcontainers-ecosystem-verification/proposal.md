## Why

The repository has container-backed PostgreSQL tests in only four service
modules, with duplicated helpers, inconsistent PostgreSQL versions, and
integration suites that are not executed by the root pull-request or release
targets. The platform needs a fail-closed, evidence-backed Testcontainers layer
that makes service integration and focused cross-component behavior
reproducible without creating a second full-stack readiness authority.

## What Changes

- Introduce a reusable Testcontainers ecosystem-verification contract for
  disposable service dependencies and focused multi-container cohorts.
- Standardize container-backed integration tests across all services that own
  PostgreSQL or Redis adapters, using repository-owned image pins, canonical
  migrations, bounded protocol-level readiness, isolated identities, and
  guaranteed cleanup.
- Add a host-side focused ecosystem harness that can run existing Compose
  overlays through Testcontainers, beginning with the Shipping HTTP, Nexus,
  PostgreSQL, Kafka, Debezium, and Temporal lifecycle already required by the
  active Shipping hardening change.
- Retain schema-versioned evidence for source revision, run identity, selected
  topology, resolved images, checks, diagnostics, and cleanup; classify the
  result as focused evidence that cannot satisfy canonical full-stack
  readiness.
- Add deterministic local targets and a Docker-capable CI workflow definition
  for service integration and focused ecosystem cohorts. Hosted workflow
  execution evidence remains owned by the active cloud delivery change.
- Preserve `make local-operational-readiness` and its eight-service Compose
  manifest as the only canonical local full-stack readiness authority.
- Keep default unit, architecture, coverage, and compatibility gates free from
  live service fixtures. Existing tool-container uses (for example Buf
  validation) remain explicit and are not Testcontainers evidence.
- **Goals:** eliminate silent integration skips, align container dependencies
  with the canonical runtime pins, exercise real boundary behavior, retain
  reproducible evidence, and shorten diagnosis through cohort-scoped logs.
- **Non-goals:** replace Docker Compose or kind, duplicate all eight services as
  generic container definitions, claim cloud or production readiness, test real
  carrier credentials, change public APIs or events, or require Docker for
  default unit tests.

## Capabilities

### New Capabilities

- `testcontainers-ecosystem-verification`: Defines deterministic disposable
  dependency fixtures, focused multi-container cohorts, evidence identity,
  cleanup, image compatibility, and execution-cadence requirements.

### Modified Capabilities

- `local-service-verification`: Requires explicitly selected service
  integration gates to provision their declared container dependencies,
  execute without silent skips, and retain diagnostics.
- `local-compose-operational-readiness`: Classifies Testcontainers ecosystem
  results as focused supplemental evidence and preserves the canonical
  eight-service Compose gate as full-stack authority.
- `platform-verification`: Adds repository-level orchestration and retained
  evidence for container-backed service integration and focused ecosystem
  cohorts while keeping hosted and cloud proof distinct.

## Impact

- **Affected code and systems:** service integration suites and test helpers,
  a new host-side test module under `tests/`, root Make targets, selected
  Compose overlays, evidence schemas and validators, documentation, and a
  Docker-capable CI workflow definition.
- **Service boundaries:** tests interact only through public HTTP, Nexus,
  Kafka, Temporal, PostgreSQL, Redis, and migration boundaries. The harness
  does not import service-private domain types or write another service's
  schema except through explicit verification inspection.
- **Contracts and data ownership:** public REST, Protobuf, Kafka event,
  Temporal workflow, database ownership, and delivery guarantees do not
  change. Test data is isolated and disposable; no production migration is
  introduced.
- **Dependencies:** the existing Testcontainers for Go dependency and its
  Compose submodule are aligned across the owning test modules using the
  currently verified compatible `v0.43.0` release. Runtime images continue to
  come from `deploy/tools.env` and must support `linux/arm64` and `linux/amd64`,
  or record an approved fallback. Compose-built local images must be built from
  the exact checkout and their image identity retained in evidence.
- **Compatibility:** default `go test ./...` and `make verify-pr` remain usable
  without live service infrastructure or Testcontainers fixtures. Some existing
  compatibility checks use short-lived Docker tool containers. Docker is
  required for the new integration and ecosystem targets, and an explicitly
  selected target fails closed when its provider is unavailable.
- **Rollout:** first standardize PostgreSQL fixtures, then add the focused
  Shipping cohort and evidence validator, then expand service coverage and wire
  local/CI orchestration. The canonical Compose gate remains unchanged until
  supplemental evidence is proven stable.
- **Rollback:** remove the focused targets and workflow wiring, revert test-only
  module dependencies and helpers, and retain the existing Compose readiness
  path. Rollback does not mutate persistent application data or require a
  schema downgrade.
