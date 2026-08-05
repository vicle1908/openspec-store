# Design: Docker Compose Stack Stability

## Current Topologies

The repository has two valid classes of Compose operation:

- **Full/local stack:** base plus application overlays and optional LGTM/tools
  overlays. The base stack owns `otel-collector` and exposes it as the internal
  hostname `otel-collector`.
- **Focused acceptance stack:** the shipping Testcontainers pilot uses only
  `docker-compose.yaml`, `docker-compose.shipping-service.yaml`, and
  `docker-compose.nexus-local.yaml`. It intentionally does not include the
  LGTM overlay and must remain independently runnable.

A service overlay cannot require an optional service that is absent from a valid
focused topology. Compose validates dependency references before startup, so a
`depends_on.otel-collector` edge causes the focused pilot to fail with
`no such service: otel-collector`.

## Changes

### Redis host isolation

Remove the catalog overlay's host mapping for Redis. Services use the internal
network address `redis:6379`; host access is not part of the application
contract. This prevents collisions when the canonical E2E project and another
local Compose project coexist.

### OTel startup behavior

Do not add a hard collector dependency to service overlays. The platform
observability bootstrap retains OTLP exporter retry/backoff behavior, and the
full stack's collector is independently health-checked. Focused stacks remain
valid without the optional collector. The validation contract explicitly checks
that no service overlay introduces an undeclared dependency.

### Temporal initializer behavior

Keep `temporal-admin-tools` as a one-shot service with `restart: "no"` and
retain `service_completed_successfully` for consumers. Its completion is
validated as an initializer result; it is not expected to remain running.

### Validation and evidence

`deploy/scripts/validate-compose.sh` SHALL validate the rendered models and
assert the Redis and initializer invariants. CI evidence SHALL include:

- `make compose-validate`;
- `make collector-validate`;
- shipping-focused Testcontainers execution;
- full LGTM smoke execution;
- PR required checks via `gh pr checks`.

GHCR diagnostic evidence remains operational documentation: the effective
build-job permission is `packages: write`, authentication succeeds, and a
selective 403 may still occur from package-level visibility/association or
registry propagation.

### Latest-only local Kubernetes toolchain

`deploy/kind/tool-versions.env` is the authoritative local validation contract.
The repository SHALL pin current upstream releases rather than require operators
to downgrade to superseded binaries. The 2026-08-05 baseline is kind v0.32.0,
kubectl/Kubernetes v1.36.3, kubeconform v0.8.0, External Secrets v2.8.0, and
kindest/node v1.36.1 with the digest published by kind v0.32.0. The node patch
level differs from kubectl only because v1.36.1 is the newest node artifact
published by the latest kind release.

The repository installer SHALL verify upstream checksums, and the External
Secrets CRD bundle SHALL be pinned by immutable commit plus repository-recorded
SHA-256. Preflight SHALL fail on version drift and pass when invoked with the
repo-installed tool directory first in `PATH`.

### Deterministic focused Shipping concurrency

The focused Shipping pilot requires two concurrent calls to prove exactly one
provider side effect, retained replay, conflict behavior, and an explicit
`operation_in_progress` response. A zero-delay stub may complete before the
second caller observes the in-progress state, yielding two `201` responses and
making the evidence timing-dependent. The focused cohort SHALL set a bounded
one-second stub dispatch delay. Unit tests SHALL constrain the delay to 500 ms
through 5 seconds so it exposes concurrency without materially extending the
cohort.

The External Secrets CRD checksum is immutable integrity data, not a credential.
When the generic-api-key detector flags a changed checksum, the repository MAY
add only the exact commit/file/rule/line fingerprint to `.gitleaksignore`, with
owner, review date, expiry, and false-positive classification in the waiver
manifest. Broad path or rule suppression is prohibited.
