## MODIFIED Requirements

### Requirement: Canonical full-stack Compose lifecycle

The platform SHALL expose one canonical root command that supplies the pinned
interpolation environment, combines the base data plane with all eight service
overlays, optionally includes tools and LGTM profiles, builds local service
images, and waits a bounded time for required services and one-shot
initializers to become healthy or exit zero. The command MUST use an isolated
project identity for evidence and MUST retain resolved Compose, image
platform, health, and one-shot exit state.

#### Scenario: Clean full-stack startup

- **WHEN** a developer runs the canonical full-stack command from a clean
  checkout with no project containers
- **THEN** Compose starts all required data-plane and eight-service roles with
  non-empty pinned image references and exits zero only after health and
  initializer gates pass

#### Scenario: Slow dependency converges

- **WHEN** Debezium requires its documented plugin-discovery budget
- **THEN** the lifecycle waits with progress and succeeds if the dependency
  converges before the budget expires

#### Scenario: One-shot initializer fails

- **WHEN** migration, topic, connector, or Nexus reconciliation exits
  non-zero
- **THEN** the lifecycle exits non-zero and retains the initializer logs and
  dependency diagnostics

#### Scenario: Full-stack rerun is idempotent

- **WHEN** the same project runs the canonical startup twice
- **THEN** the second run exits zero without duplicating topics, connectors,
  namespaces, migrations, or business side effects

## ADDED Requirements

### Requirement: Arm64 overlays preserve built image contracts

The arm64 Compose overlay SHALL set platform constraints without changing
repository-built service image names or removing image-layer assets required by
healthchecks. Static validation SHALL compare the resolved arm64 image identity
with the base image contract for every locally built service.

#### Scenario: OTel arm64 image retains its probe

- **WHEN** the arm64 model is rendered and started
- **THEN** the resolved OTel image is the repository-built image containing
  `/bin/wget` and its healthcheck returns `200`

#### Scenario: Overlay changes image identity

- **WHEN** an arm64 overlay replaces a custom image with an upstream image
- **THEN** Compose validation exits non-zero and identifies the service and
  conflicting image
