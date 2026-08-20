## ADDED Requirements

### Requirement: Non-local manifests are complete and immutable

The platform SHALL render complete staging and production resources for all
eight services. Every workload image MUST use a verified immutable digest, and
each environment SHALL include valid configuration, workload identity,
resources, autoscaling, disruption budgets, network policy, and externally
sourced secrets.

#### Scenario: Environment render is deployable
- **WHEN** the staging or production overlay set is rendered and validated
- **THEN** exactly eight service applications contain complete schema-valid and reference-complete resources with immutable image digests

#### Scenario: Incomplete environment fails closed
- **WHEN** an image digest, secret prerequisite, reference, selector, resource, autoscaling, or disruption constraint is invalid
- **THEN** validation fails before reconciliation and identifies the affected service and environment

### Requirement: Release images are multi-architecture and evidenced

CI SHALL build, scan, attest, and publish every service for linux/amd64 and
linux/arm64. It MUST retain machine-readable evidence binding the service,
source revision, repository, required platforms, immutable digest, scan result,
and attestation result.

#### Scenario: Complete release image is publishable
- **WHEN** every required build, scan, attestation, and platform-index check succeeds
- **THEN** CI publishes the image and records its immutable multi-architecture digest

#### Scenario: Incomplete release blocks promotion
- **WHEN** any service, platform, scan, attestation, publish, or digest-evidence result is absent or failed
- **THEN** promotion remains unavailable

### Requirement: Supported architecture acceptance is retained

The platform MUST retain complete clean kind acceptance for both macOS arm64
and Linux amd64, including image identities, rendered manifests, rollouts,
Temporal readiness, cross-service smoke, telemetry, and diagnostics.

#### Scenario: Linux amd64 acceptance complements local arm64 evidence
- **WHEN** the release candidate runs in the Linux amd64 CI environment
- **THEN** the same required evidence classes as the macOS arm64 run pass and are retained for the exact source revision

### Requirement: Deployment validation is a required clean CI gate

CI SHALL require exhaustive deployment validation only after Compose,
Collector, Kustomize, reference, secret, ApplicationSet, and active OpenSpec
checks pass in a clean environment with supported resources.

#### Scenario: Release commit passes exhaustive validation
- **WHEN** a release candidate is evaluated in the supported clean CI environment
- **THEN** the retained manifest enumerates every required model, configuration, overlay, ApplicationSet, secret, and active-change check with no blocking failure

### Requirement: Git promotion and Argo CD convergence gate environments

Promotion SHALL update immutable digests through a reviewed Git change using a
least-privileged branch-protection-compatible identity. Staging MUST reconcile
to the expected revision and become Synced and Healthy with passing smoke and
telemetry before production approval.

#### Scenario: Staging promotion succeeds
- **WHEN** the reviewed promotion commit merges
- **THEN** all staging Applications reconcile to that revision and digest set, become Synced and Healthy, and pass smoke and telemetry verification

#### Scenario: Production uses the reviewed staging digest set
- **WHEN** staging evidence passes and an authorized operator approves production
- **THEN** production reconciles the same reviewed digests without an imperative service apply

### Requirement: Git-revert rollback is rehearsed and evidenced

The delivery system SHALL collect failure diagnostics before rollback and SHALL
use an operator-approved Git revert to restore the prior known-good digests.
The rehearsal MUST retain convergence status, smoke results, and recovery
timing.

#### Scenario: Staging rollback restores known-good state
- **WHEN** an operator approves reverting a failed staging promotion
- **THEN** Argo CD reconciles affected Applications to the previous digests, returns them to Synced and Healthy, and the retained smoke evidence passes
