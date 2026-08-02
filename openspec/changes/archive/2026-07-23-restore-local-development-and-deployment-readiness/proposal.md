## Why

The platform had individually strong service, Compose, Kubernetes, and GitOps artifacts, but the documented local-development and local-deployment paths did not compose into a reproducible working system. Validation showed unresolved Compose interpolation, host/container DNS mismatches, incomplete Temporal and OpenTelemetry bootstrap, and undeployable local Kustomize output.

This change restores a trustworthy local developer and repository-validation
contract. Complete cloud delivery, live environment reconciliation, and CI/CD
promotion proof continue in
`complete-cloud-deployment-and-cicd-readiness`.

## What Changes

- Add one canonical, version-pinned Compose topology for the base data plane, all eight services, optional tooling, and optional LGTM observability.
- Run cross-service smoke tests inside the Compose network, wait on business-service readiness, and fail when required telemetry or service evidence is absent.
- Reconcile the contradictory customer GDPR export requirements around the deployed asynchronous `POST` plus durable `GET` contract, Temporal workflow ownership, idempotent replay, complete payload, and authorization.
- Complete Temporal bootstrap by creating required namespaces idempotently before workers start, and validate the pinned OpenTelemetry Collector configurations with the pinned Collector image.
- Separate stable Temporal task-queue names from SDK-valid Worker Deployment names; retain public queue/workflow contracts while replacing deployment identifiers that use the SDK-reserved `.` separator.
- Add a pinned, idempotent kind lifecycle for local Kubernetes development, including cluster creation, local image loading or registry use, deployment, readiness, smoke testing, diagnostics, and teardown.
- Replace generic Kubernetes placeholders with per-service environment
  directories, complete the local overlays, and add fail-closed rendering,
  schema, policy, and reference validation for every environment.
- Make non-local secrets originate from External Secrets or another external provider and prevent committed production credentials from entering rendered manifests.
- Correct Argo CD ApplicationSets so generators, paths, cluster parameters, repository references, and image overrides are valid; use Git as the single deployment source of truth.
- Make target namespaces explicit platform prerequisites instead of allowing service Applications to create cluster tenancy, and retire tag-based Argo Image Updater promotion in favor of reviewed immutable digests.
- Repair the CI service matrix, permissions, failure dependencies, and
  Git-owned promotion structure without claiming that multi-architecture
  publication or live environment promotion has run.
- Add deterministic validation for Compose models, Collector configs,
  Kustomize overlays, unresolved placeholders, schema/policy checks, secrets,
  ApplicationSets, and OpenSpec status evidence.
- Correct existing documentation and specification status claims that are not supported by executable evidence.
- **BREAKING**: remove the non-functional generic `local`, `staging`, and `production` Kubernetes overlays after their consumers move to per-service environment overlays.
- **BREAKING**: the deployment workflow will no longer imperatively apply manifests that Argo CD owns; promotion occurs through committed digest updates and Argo CD reconciliation.

## Capabilities

### New Capabilities

- `local-development-orchestration`: Defines the canonical Compose and kind developer lifecycles, prerequisites, readiness contract, diagnostics, cleanup, and retained validation evidence.

### Modified Capabilities

- `dedicated-workflow-orchestration`: Requires the full eight-service Compose topology and cross-service smoke runner to execute in a resolvable network context and assert all required services.
- `customer-gdpr-export`: Replaces the contradictory synchronous, non-Temporal export description with the deployed asynchronous Temporal request and durable lookup contract.
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
- **Delivery structure**: GitHub Actions permissions and matrix handling,
  promotion gates, Git ownership, Argo CD ApplicationSets/AppProject, and
  evidence retention. Live publishing, reconciliation, and rollback proof are
  explicitly outside this completed change.
- **Specifications and documentation**: operational-readiness and deployment-status claims become derived from named validation commands and retained artifacts rather than file presence or manually checked task boxes.
- **Service boundaries and contracts**: no Protobuf, event, or data-ownership contract changes. The customer GDPR REST specification is corrected to the already deployed asynchronous path because the existing main spec contradicts the dedicated Temporal requirements and executable smoke contract; other REST contracts remain unchanged.
- **Rollout**: validators landed first, followed by Compose/runtime bootstrap,
  local overlays, kind acceptance, and repository GitOps safeguards.
- **Rollback**: local rollback uses the retained prior Compose/Kustomize inputs
  without destructive data cleanup. Cloud Git-revert rehearsal belongs to the
  active cloud delivery change.
