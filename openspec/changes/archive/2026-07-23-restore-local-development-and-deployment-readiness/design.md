## Context

The repository contains eight Go services, a shared platform module, PostgreSQL, Kafka, Debezium, Temporal, Redis, OpenTelemetry, layered Docker Compose files, Kustomize overlays, Argo CD ApplicationSets, and GitHub Actions workflows. The artifacts currently validate in isolation more often than they validate as a system: root Compose targets omit the interpolation environment and service overlays, smoke tests use container DNS from a host process, Temporal schemas start without an application namespace, the pinned Collector rejects its configuration, Kustomize emits unresolved placeholders and dangling references, and CI does not promote built image digests into Git-managed deployment state.

The operational contract must work on macOS arm64 and Linux amd64. Docker Compose remains the fastest local integration topology; kind provides production-shape Kubernetes validation. Existing domain, Protobuf, outbox, Kafka, and Temporal routing contracts remain unchanged. The customer GDPR REST specification is an explicit exception: its synchronous non-Temporal text conflicts with the already-defined `customer.gdpr.v1` workflow and the deployed asynchronous API, so this change reconciles the specification with that observable contract. Official behavior used by this design includes Docker Compose interpolation, health-gated dependencies and `up --wait`; Temporal namespace registration for self-hosted services; the current OpenTelemetry Collector internal-telemetry schema; Kustomize overlays and image transforms; kind image loading/local registry workflows; Argo CD Git/cluster generators; and GHCR's `packages: write` permission.

Stakeholders are service developers, platform maintainers, CI operators, and release operators. A successful implementation gives each group the same named commands and the same retained evidence instead of separate undocumented procedures.

## Goals / Non-Goals

**Goals:**

- Make a clean Compose checkout converge to the complete eight-service platform through one documented command.
- Make smoke tests resolve service names correctly and fail on missing services, workers, telemetry, or evidence.
- Make Temporal, OpenTelemetry, topic provisioning, and migrations deterministic and idempotent.
- Produce valid, reference-complete Kubernetes manifests for every service in local, staging, and production.
- Provide an idempotent kind lifecycle with arm64-compatible images and bounded readiness waits.
- Make Git the single source of deployment state and promote immutable image digests through Argo CD.
- Convert OpenSpec implementation status into an evidence-backed assertion enforced by CI.
- Preserve service ownership, database transaction boundaries, at-least-once event delivery, idempotency, and public contract versions while reconciling the contradictory customer GDPR export route description.

**Non-Goals:**

- Change REST endpoints other than the customer GDPR specification correction, Protobuf schemas, Kafka event versions, aggregate ownership, or database schemas.
- Replace Docker Compose, Kustomize, Argo CD, Temporal, Kafka, PostgreSQL, or OpenTelemetry with different platforms.
- Design production cluster provisioning, multi-region failover, service mesh adoption, or progressive-delivery controllers.
- Add Helm merely as an alternative packaging layer.
- Guarantee production data rollback; this change only provides application/configuration rollback through Git.

## Decisions

### 1. One canonical Compose model with explicit interpolation

The root Makefile will define `COMPOSE_ENV`, `COMPOSE_BASE`, `COMPOSE_APPS`, `COMPOSE_LGTM`, `COMPOSE_TOOLS`, and `COMPOSE_FULL` once. Every root Compose command will pass `--env-file deploy/tools.env`; required variables will use `${VAR:?message}` or validated defaults so unresolved image tags fail during `docker compose config` rather than during startup.

`make dev-up` will render the full model, build service images, and run `docker compose up --wait --wait-timeout <bounded duration>`. Optional tools and LGTM components remain profiles/overlays. `make dev-down` will target the same project and file set; destructive volume removal will require a separate explicit command.

This follows Docker's documented interpolation and health-gated startup behavior. A generated mega-file was rejected because it duplicates the layered source of truth. Continuing with ad hoc long commands was rejected because it already caused drift between README, Makefile, and CI.

### 2. Smoke tests execute as a Compose workload

The cross-service smoke runner will be built or mounted into a one-shot `smoke` service on `platform-network`. It will use container DNS and depend on every required API/worker readiness condition. Evidence is written to a bind-mounted repository artifact directory. Host execution may remain as an explicit alternate mode only when all endpoint variables are supplied with published localhost ports.

The smoke contract covers all eight services, their required long-running roles, Mailpit, and the expected telemetry backend. Missing traces for required services fail the run. Running the current test unchanged on the host was rejected because Compose DNS names are intentionally network-scoped.

### 3. Runtime initialization is modeled as explicit one-shot dependencies

Temporal initialization is split into schema initialization, server readiness, and namespace initialization. An idempotent namespace initializer runs `temporal operator namespace describe` followed by `create` only when absent. All Temporal workers depend on its successful completion and expose readiness only after registration.

Task queues and registered workflow names remain stable public routing contracts. Worker Deployment names are separate deployment identities and use dash-delimited names without `.`, which the current Go SDK reserves as its deployment-version separator. Each versioned worker also sets an explicit default versioning behavior so workflow registration cannot fail after polling starts.

Topic and connector initialization scripts will be executable, idempotent, and modeled with `service_completed_successfully`. A second invocation must exit zero without deleting data or duplicating resources.

The Collector configuration will use the schema supported by the pinned image. CI runs the image's `validate` subcommand for every Collector config. Runtime health checks use the enabled health extension or a documented metrics endpoint. Relying on a container being `running` was rejected because it did not detect invalid configuration or absent Temporal namespaces.

### 4. Per-service, per-environment Kustomize overlays replace generic placeholders

The target tree is `deploy/k8s/overlays/{local,staging,production}/{service}/`. Every overlay renders a complete service workload with resolved image, role, ports, resources, service account, ConfigMap, Secret/ExternalSecret, probes, HPA/PDB applicability, and NetworkPolicy. The base must itself be syntactically and schema valid; it will use stable generic resource names that Kustomize can transform, not free-form placeholder tokens.

CI verifies:

1. `kubectl kustomize` succeeds for every overlay.
2. No forbidden placeholder token remains.
3. Kubernetes schema/policy validation succeeds with pinned tooling.
4. Every workload reference resolves to a rendered object or documented cluster prerequisite.
5. A disposable kind cluster accepts the local overlays and reaches readiness.

For local kind, images use unique non-`latest` tags and `IfNotPresent`, then are loaded with `kind load docker-image` or pushed to the documented local registry. Staging and production use registry digests. A single generic production overlay was rejected because it cannot express eight different binaries, roles, ports, resources, and secrets safely.

### 5. External secrets are part of the rendered non-local graph

Staging and production overlays include ExternalSecret resources that reference an installed ClusterSecretStore. Database URLs, API credentials, and Redis ACL secrets are not committed as production literals. Local overlays generate documented non-sensitive development credentials.

CI scans tracked configuration and rendered non-local manifests for forbidden credential patterns. The external-secrets CRDs and SecretStore are explicit cluster prerequisites validated before Argo CD sync. Keeping an unused ExternalSecret template beside literal production credentials was rejected because it provides no runtime protection.

### 6. Argo CD owns deployment; CI owns build and promotion

ApplicationSets enable Go templates with `missingkey=error`. Git directory generators point to overlay directories, cluster generators select explicitly labeled staging or production clusters, and `values` is a string map. `source.path` references the directory containing `kustomization.yaml`. Staging and production are distinct enough to permit different sync and approval policies.

Environment namespaces are platform prerequisites and are not created by service Applications. The AppProject permits only the exact repository, registered target clusters, namespaces, and namespaced workload kinds; CRDs, namespaces, ClusterSecretStores, and cluster registration remain separately controlled bootstrap resources.

Build jobs use a real GitHub Actions matrix, authenticate to `ghcr.io`, receive `packages: write`, build both supported architectures, and record each pushed digest. A promotion job updates the environment Kustomize `images` digest fields on a promotion branch and opens or updates a pull request. After merge, Argo CD reconciles the commit; CI waits for the Applications to become Synced and Healthy and then executes a post-deployment smoke test. Imperative `kubectl apply` is limited to disposable validation clusters and bootstrap resources that Argo CD does not own.

Mutable `latest` promotion was rejected because tags can move. Having both CI and Argo CD apply the same resources was rejected because it creates competing field managers and an ambiguous rollback source.

Argo CD Image Updater tag promotion was rejected for this workflow because it bypasses the required build-evidence selection and reviewable digest change. The repository's CI promotion pull request is the sole automated writer of environment image digests.

### 7. Evidence gates specification status

A deployment validation command produces a machine-readable manifest containing commit SHA, tool versions, rendered overlay list, image digests, commands, timestamps, and pass/fail results. CI retains the manifest plus Compose logs, Kubernetes events, pod descriptions, Argo CD status, and smoke reports.

An OpenSpec requirement or task may be marked implemented/complete only when its named acceptance command passes and its evidence location is recorded. Historical reports remain dated snapshots and cannot describe current readiness without a fresh validation manifest. File existence alone is not implementation evidence.

### 8. The GDPR export contract is asynchronous and idempotent

The customer export request uses `POST /api/v1/customers/{id}/gdpr/export` with a required `Idempotency-Key` and returns `202 Accepted`. The caller polls `GET /api/v1/customers/{id}/gdpr/export?idempotency_key=<key>` until durable state is completed. A repeated POST for the same customer and key returns the existing export state and does not start another workflow. The export workflow and task queue remain `customer.gdpr.v1`; the GET lookup never starts workflow execution.

The completed representation includes the export ID, owning customer ID, idempotency key, SHA-256 content hash, payload, status, and timestamps. The payload retains the Article 15 profile, address, deletion timestamp, purge timestamp, and audit-entry requirements. Authorization remains fail-closed for a subject that does not own the customer; local smoke may use the explicitly documented development authentication mode but cannot establish production authorization readiness.

Keeping the synchronous `GET /customers/{id}/export` description was rejected because it directly contradicts the dedicated Temporal specifications, service traceability, current API, and executable acceptance path. Treating the current incomplete payload or disabled authorization as sufficient was also rejected; those scenarios remain open until focused and live evidence passes.

## Risks / Trade-offs

- **Full local topology consumes substantial CPU and memory** → Keep per-service and infrastructure-only targets, document minimum resources, and retain profiles for optional tooling/observability.
- **kind increases local tooling and startup time** → Keep Compose as the default inner loop; use kind for deployment-shape validation and provide pinned bootstrap commands.
- **External Secrets complicates disposable clusters** → Use generated local Secrets only in the local overlays and validate External Secrets in staging/production with installed CRDs.
- **Digest promotion adds a Git round trip** → Automate the promotion pull request and expose the exact build-to-deploy commit relationship in evidence.
- **ApplicationSet generator changes can affect many Applications** → Validate generated Applications in a disposable Argo CD environment or schema test before applying, select clusters by environment label, and roll out staging before production.
- **Strict validators initially fail many existing manifests/spec statuses** → Land the gates in report-only mode only within the repair branch, fix all failures, then make them required before merge.
- **Mixed old Compose projects can mask clean-start failures** → Use a deterministic project name, preflight orphan detection, and a clean-environment CI job; never count pre-existing containers as acceptance evidence.
- **Arm64 support can lag for third-party tools** → Verify manifests for both architectures before pin updates and document emulation only as a time-bounded exception with owner and removal date.

## Migration Plan

1. Add the validation script and CI report without changing runtime ownership; capture a failing baseline.
2. Fix Compose interpolation, canonical file sets, script permissions, OTel validation, Temporal namespace initialization, and in-network smoke execution. Prove a clean full-stack start twice to establish idempotency.
3. Build per-service local overlays and the pinned kind lifecycle. Validate all eight services and smoke tests in kind.
4. Build staging and production overlays, external-secret references, schema/policy gates, and reference-integrity checks. Remove generic placeholder overlays after all consumers migrate.
5. Correct ApplicationSets and AppProject constraints. Rehearse staging sync, health wait, smoke test, and Git revert rollback.
6. Repair GHCR matrix builds and digest evidence, then enable promotion pull requests. Disable the imperative deployment jobs before enabling Argo CD promotion.
7. Update operational documents and OpenSpec statuses only after the corresponding retained evidence passes.

Rollback is a Git revert of the environment digest/configuration commit followed by Argo CD reconciliation. During migration, the old deployment workflow remains disabled rather than serving as an automatic fallback. Compose rollback uses the prior known-good file set and image pins without deleting persistent volumes unless the operator explicitly selects destructive cleanup.

## Open Questions

- Which repository-scoped credential will push promotion branches under branch protection: the built-in `GITHUB_TOKEN` with explicit permissions or an installation token from an existing GitHub App? Implementation must choose the least-privileged option supported by the repository settings and document the required configuration.
- Which staging and production cluster-secret labels are authoritative for ApplicationSet selection? The implementation must define and validate them before enabling automated sync.

## Completion Boundary

This archived change proves the repository and local-runtime portions of the
design: canonical Compose, macOS arm64 kind, local image loading, ordered
Kubernetes convergence, GDPR ownership, Temporal routing, telemetry, validation
mechanics, per-service overlay structure, ExternalSecret references, and GitOps
ownership rules. Live Linux amd64 CI acceptance, complete staging/production
resources, published multi-architecture release images, promotion credentials,
required CI enforcement, environment reconciliation, production approval, and
rollback rehearsal continue in
`complete-cloud-deployment-and-cicd-readiness`.
