## Why

The platform has individually strong service, Compose, Kubernetes, and GitOps artifacts, but the documented local-development and deployment paths do not compose into a reproducible working system. Current validation shows unresolved Compose interpolation, host/container DNS mismatches, incomplete Temporal and OpenTelemetry bootstrap, undeployable Kustomize output, and a delivery workflow that neither builds its service matrix correctly nor promotes immutable images.

This change restores a trustworthy developer and deployment contract: every supported path must start from a clean machine or cluster, converge to healthy services, execute a real cross-service smoke test, and retain evidence that justifies OpenSpec implementation status.

## What Changes

- Add one canonical, version-pinned Compose topology for the base data plane, all eight services, optional tooling, and optional LGTM observability.
- Run cross-service smoke tests inside the Compose network, wait on business-service readiness, and fail when required telemetry or service evidence is absent.
- Complete Temporal bootstrap by creating required namespaces idempotently before workers start, and validate the pinned OpenTelemetry Collector configurations with the pinned Collector image.
- Separate stable Temporal task-queue names from SDK-valid Worker Deployment names; retain public queue/workflow contracts while replacing deployment identifiers that use the SDK-reserved `.` separator.
- Add a pinned, idempotent kind lifecycle for local Kubernetes development, including cluster creation, local image loading or registry use, deployment, readiness, smoke testing, diagnostics, and teardown.
- Replace generic Kubernetes placeholders with deployable per-service local, staging, and production overlays; resolve service accounts, ConfigMaps, Secrets, roles, images, resource quantities, and workload references.
- Make non-local secrets originate from External Secrets or another external provider and prevent committed production credentials from entering rendered manifests.
- Correct Argo CD ApplicationSets so generators, paths, cluster parameters, repository references, and image overrides are valid; use Git as the single deployment source of truth.
- Make target namespaces explicit platform prerequisites instead of allowing service Applications to create cluster tenancy, and retire tag-based Argo Image Updater promotion in favor of reviewed immutable digests.
- Build and publish each service image correctly in CI, capture immutable digests, update Git-managed Kustomize state, wait for Argo CD health, and run post-deployment smoke tests.
- Add deterministic CI gates for Compose models, Collector configs, all Kustomize overlays, unresolved placeholders, schema/policy validation, secret scanning, and OpenSpec status evidence.
- Correct existing documentation and specification status claims that are not supported by executable evidence.
- **BREAKING**: remove the non-functional generic `local`, `staging`, and `production` Kubernetes overlays after their consumers move to per-service environment overlays.
- **BREAKING**: the deployment workflow will no longer imperatively apply manifests that Argo CD owns; promotion occurs through committed digest updates and Argo CD reconciliation.

## Capabilities

### New Capabilities

- `local-development-orchestration`: Defines the canonical Compose and kind developer lifecycles, prerequisites, readiness contract, diagnostics, cleanup, and retained validation evidence.

### Modified Capabilities

- `dedicated-workflow-orchestration`: Requires the full eight-service Compose topology and cross-service smoke runner to execute in a resolvable network context and assert all required services.
- `per-service-temporal-registration`: Requires idempotent namespace bootstrap and worker convergence before Temporal-dependent services are considered ready.
- `platform-temporal-versioning`: Requires SDK-valid deployment identities independent from stable task-queue names and an explicit default versioning behavior for every versioned worker.
- `platform-observability`: Requires pinned Collector configurations to validate and start, and makes required telemetry assertions fail closed.
- `k8s-deployment-base`: Replaces placeholder templates with complete per-service environment overlays whose rendered resources and references are deployable.
- `k8s-gitops-workflow`: Corrects ApplicationSet generation and requires digest-based Git promotion with Argo CD as the deployment owner.
- `operational-readiness`: Adds executable deployment validation, external-secret enforcement, evidence-backed status rules, and clean-environment readiness gates.

## Impact

- **Developer workflow**: root Make targets, Docker Compose overlays, smoke-test execution, pinned prerequisites, and local diagnostics/cleanup.
- **Runtime bootstrap**: Temporal schema and namespace initialization, worker startup ordering, OpenTelemetry Collector configuration, and one-shot topic initialization.
- **Kubernetes**: Kustomize base and environment overlays for eight services, workload identities and references, image and resource configuration, External Secrets, NetworkPolicies, HPA/PDB resources, and kind support.
- **Delivery**: GitHub Actions build/publish permissions and matrix handling, digest capture, Git promotion, Argo CD ApplicationSets/AppProject, health waits, rollback, and evidence retention.
- **Specifications and documentation**: operational-readiness and deployment-status claims become derived from named validation commands and retained artifacts rather than file presence or manually checked task boxes.
- **Service boundaries and contracts**: no REST, Protobuf, event, or data-ownership contract changes. The change only makes existing eight-service boundaries deployable and verifiable.
- **Rollout**: land validators first, repair Compose/runtime bootstrap, then Kubernetes overlays, then GitOps promotion; keep the existing manual deployment workflow disabled until the replacement passes staging rehearsal.
- **Rollback**: revert the Git digest promotion for deployed services; retain the last-known-good Compose/Kustomize evidence bundle and cluster diagnostics. Database and event-schema rollback remain outside this change.
