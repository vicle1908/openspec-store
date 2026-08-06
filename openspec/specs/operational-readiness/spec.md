# operational-readiness Specification

## Purpose

This spec defines operational readiness requirements for the platform, covering infrastructure tooling, deployment safety, documentation, agent configuration, Kubernetes networking, ArgoCD deployment, Dockerfile standards, service verification, Kustomize configuration, and secrets management.
## Requirements

> **Status**: PARTIAL / UNVERIFIED. Source artifacts exist for several requirements, but current Compose, Kustomize, External Secrets, Argo CD, smoke, and telemetry paths have not passed clean-environment acceptance with retained evidence.
>
> **Status semantics and acceptance evidence:** Individual `IMPLEMENTED` annotations below describe source-level implementation only; they are not current deployment-readiness claims. Current readiness requires `make validate-deployment` and the relevant `make dev-smoke` or `make kind-smoke` acceptance to pass for the target commit. Retain the `go-microservices.deployment-validation/v1` manifest at `artifacts/deployment-validation/<run-id>/manifest.json` (or the configured artifact root) plus its referenced smoke and diagnostics artifacts.

### Requirement: Broker UI SHALL be available in tools overlay

> **Status**: IMPLEMENTED. Kafka UI exists in tools overlay with read-only access to Kafka.

The platform SHALL provide a broker UI service (kafka-ui or equivalent) in the tools docker-compose overlay so operators can inspect Kafka topics, consumer groups, messages, and broker configuration through a web interface. The tools overlay SHALL expose the broker UI on a configurable port (default 8080) and MUST NOT be included in the production or base overlays. The broker UI SHALL have read-only access to Kafka by default and MUST NOT be granted topic creation or deletion permissions without explicit operator override.

#### Scenario: Broker UI is accessible in tools overlay

- **WHEN** an operator runs `docker compose --profile tools up kafka-ui`
- **THEN** the broker UI is accessible at `http://localhost:8080` and can list all Kafka topics in the local development cluster

#### Scenario: Broker UI is not included in base overlay

- **WHEN** an operator runs `docker compose up` without the tools profile
- **THEN** no broker UI container is started and port 8080 is not bound

### Requirement: Rollback rehearsal SHALL be executable via make target

> **Status**: PARTIAL. Make target exists; rollback rehearsal script may be partial.

The platform SHALL provide a `rehearse-rollback` Make target in the root Makefile that executes the rollback rehearsal script (`scripts/rehearse-rollback.sh`). The rehearsal script MUST validate the rollback procedure for each service by simulating a deployment rollback against the target environment (staging by default) and confirming that the previous image tag is available, the health check passes after rollback, and the service returns to a ready state. The rehearsal script SHALL produce a structured report (exit 0 on success, non-zero on failure) and MUST NOT perform an actual rollback in production environments without an explicit `CONFIRM_PRODUCTION=1` flag.

#### Scenario: Rollback rehearsal succeeds against staging

- **WHEN** an operator runs `make rehearse-rollback SERVICE=order-service ENV=staging`
- **THEN** the script validates that the previous image tag exists, simulates the rollback, runs the health check, and exits 0 with a success report

#### Scenario: Rollback rehearsal blocks production without confirmation

- **WHEN** an operator runs `make rehearse-rollback SERVICE=order-service ENV=production` without `CONFIRM_PRODUCTION=1`
- **THEN** the script exits with code 1 and prints an error message indicating production rollback rehearsal requires explicit confirmation

### Requirement: Service runbooks SHALL exist for each service

> **Status**: PARTIAL. Root per-service runbooks remain incomplete; shared and service-local procedures are documented separately.

The platform SHALL maintain a discoverable operational runbook in the
repository's documented runbook locations for every deployable service:
order-service, payment-service, inventory-service, customer-service,
notification-service, shipping-service, catalog-service, and
reporting-service. Each service's operational documentation SHALL identify
service purpose and ownership, key dependencies, common failure modes and
remediation steps, escalation contacts, rollback procedure, scaling guidance,
and diagnostic commands. Runbooks MUST be reviewed and updated whenever the
service's deployment or dependency topology changes. Shared procedures such as
local CDC MAY be referenced rather than duplicated.

#### Scenario: Runbook exists for order-service

- **WHEN** an operator reads the canonical order-service operational runbook
- **THEN** the referenced file exists and contains sections for Dependencies, Failure Modes, Remediation, Rollback, Scaling, and Escalation

#### Scenario: Reporting service is included in the runbook inventory

- **WHEN** the runbook index is validated against the eight-service platform inventory
- **THEN** `reporting-service` appears with an explicit runbook status and ownership reference

#### Scenario: Shared local CDC procedure is referenced

- **WHEN** a service relies on the common local Debezium registration and recovery behavior
- **THEN** its documentation links to `docs/runbooks/local-cdc.md` without claiming that shared guidance is a service-specific runbook

### Requirement: Agent configs SHALL be wired for all supported agents

The platform SHALL provide properly configured agent configuration files for all supported AI coding agents (Claude via `.claude/settings.json`, Cursor via `.cursor/mcp.json`, Codex, KiloCode, Kiro, Factory, OpenCode, Zed, Kimi, Antigravity, and Hermes where installed). Each supported MCP client SHALL use MCP Router as the single client-facing gateway for GitNexus, Graphify, and AgentMemory. Client configuration MUST NOT additionally register those same knowledge servers directly unless a documented, time-bounded compatibility exception identifies the owner, reason, expiry, and rollback. Configurations MUST remain synchronized with the platform topology and MUST NOT contain hardcoded secrets or credentials.

The running MCP Router desktop app SHALL be the authoritative adapter and live
configuration owner. The app SHALL remain on latest stable `0.6.3` until a newer
stable release is reviewed, and stdio coding-agent bridges SHALL pin latest
stable `@mcp_router/cli@0.2.0`. Provider child definitions and token-access maps
MUST be previewed, applied, and restored through MCP Router's repository/service
layer; automation MUST NOT write the app SQLite database or shared token config
directly. Each supported coding-agent token SHALL receive only the reviewed
knowledge-child access needed by that client, while unrelated server access is
preserved exactly.

Repository-owned client transactions MAY inspect router SQLite/shared-config
shape for read-only evidence, but production apply and restore MUST return a
typed app-owned refusal for those targets and MUST NOT open a write connection,
issue SQL, or replace either file.

The transaction SHALL mutate only access booleans for existing approved tokens;
it MUST NOT create, rotate, delete, export, log, journal, or back up raw token
values. It SHALL address tokens by approved client alias and app-computed
one-way fingerprint, preserve unrelated true/false/absent access entries, and
reject unknown servers plus missing, duplicate, ambiguous, or expired tokens.
Rollback SHALL retain only access-map booleans, aliases, and one-way token
fingerprints. Raw token values MUST remain in place; fingerprint drift from
rotation/deletion/creation MUST block automated restore.

The app command channel MUST accept only canonical current-owner mode-0600
regular plan/result/approval paths and digest-bound generations. Preview MAY run
without approval; apply and restore MUST reject absent, stale, mismatched, or
replayed approval and MUST serialize execution under one app-owned lock. The
channel MUST NOT introduce a network admin endpoint or token-bearing arguments.
Apply/restore authorization MUST use an app-minted single-use challenge shown in
the trusted MCP Router BrowserWindow and a short-lived MACed capability issued
only after validated renderer-origin/webContents confirmation. The MAC key MUST
remain under `safeStorage`; expiry, consumption, replay, and restart recovery
MUST fail closed. External chat approval alone MUST NOT authenticate the app
command.

Before mutation the app MUST preflight every target and atomically publish a
redacted durable recovery journal. It MUST revalidate identities before every
publication/compensation step, quiesce affected running children, reject
concurrent server/token/workspace writers, define one commit point, compensate
in reverse order, verify compensation, refresh app caches/name maps, and restart
only children that were previously running. Secret-bearing backup payloads MUST
be encrypted with `safeStorage`; unavailable encryption blocks apply/restore.

#### Scenario: MCP Router app configuration is previewed

- **WHEN** the operator supplies a declarative coding-agent adapter plan
- **THEN** MCP Router validates app/database/shared-config identities, exact
  server definitions, pinned bridge/provider selectors, client aliases, and
  token-access deltas without mutation
- **AND** missing, duplicate, floating, secret-bearing, or third-state inputs
  fail closed with redacted evidence

#### Scenario: MCP Router app configuration is applied

- **WHEN** an approved plan is applied to the running app
- **THEN** server and token mutations execute through the app-owned services,
  preserve secret storage and unrelated rows/access, and publish exact post-state
- **AND** a later failure compensates prior changes or restores the protected
  app-owned backup before reporting failure

#### Scenario: MCP Router app configuration is restored

- **WHEN** acceptance fails and current state matches the approved post-state
- **THEN** the app-owned restore returns server definitions and token access to
  the exact approved pre-state without exposing token values

#### Scenario: Claude settings reference correct MCP servers

- **WHEN** a developer opens the project with Claude Code
- **THEN** Claude's effective MCP configuration points to the authorized MCP Router endpoint or bridge
- **AND** no duplicate direct GitNexus, Graphify, or AgentMemory MCP registration is active outside an approved compatibility exception

#### Scenario: Cursor MCP config includes all required tools

- **WHEN** a developer opens the project with Cursor
- **THEN** Cursor reaches all required platform-development tools through the authorized MCP Router connection
- **AND** the effective configuration contains no duplicate direct GitNexus, Graphify, or AgentMemory server

#### Scenario: Effective client topology is audited

- **WHEN** the operator runs the MCP topology diagnostic
- **THEN** it inventories every supported client configuration, MCP Router server, bridge process, and direct GitNexus, Graphify, and AgentMemory process family
- **AND** it distinguishes the expected one bridge per active client from duplicate child knowledge-server processes
- **AND** it emits only redacted paths, server names, process identities, counts, and health states

#### Scenario: Duplicate direct knowledge server is detected

- **WHEN** a supported client config or process tree contains a direct GitNexus, Graphify, or AgentMemory MCP server in addition to MCP Router
- **THEN** readiness fails and identifies the owning client and duplicate server class without printing credentials or command-line secret values
- **AND** no automatic deletion or process termination occurs during diagnosis

#### Scenario: Live client cutover is authorized

- **WHEN** reviewed source changes, backups, synthetic migration, restore rehearsal, and an exact redacted cutover plan have passed
- **THEN** an operator may issue execution approval bound to the plan digest, client inventory, configuration fingerprints, process owners, and maintenance window
- **AND** stale or changed inputs invalidate that approval before mutation

#### Scenario: Client cutover succeeds

- **WHEN** the approved live cutover removes duplicate direct registrations and restarts affected clients
- **THEN** each required client discovers GitNexus, Graphify, and AgentMemory through MCP Router
- **AND** no duplicate child knowledge-server process family remains after old client sessions exit
- **AND** client hooks, skills, unrelated MCP servers, credentials, sessions, and local indexes remain intact

#### Scenario: Client cutover fails

- **WHEN** any required client cannot discover or call its required router-exposed knowledge tools after cutover
- **THEN** maintenance remains active and the operator restores the exact backed-up client configuration for the affected scope
- **AND** the run records the failure and rollback outcome without exposing secrets

### Requirement: K8s NetworkPolicy SHALL allow database and messaging egress

> **Status**: IMPLEMENTED. NetworkPolicy allows egress to PostgreSQL, Kafka, and Redis endpoints.

The platform's Kubernetes NetworkPolicy manifests SHALL explicitly allow egress traffic from service pods to PostgreSQL (port 5432), Kafka (port 9092), and Redis (port 6379) endpoints. The NetworkPolicy SHALL use label selectors to target the appropriate pods and MUST NOT apply a default-deny egress rule without first defining the required allow rules for database and messaging traffic. All services that depend on PostgreSQL, Kafka, or Redis SHALL be covered by the egress policy.

#### Scenario: Order-service pod can reach PostgreSQL

- **WHEN** an order-service pod is scheduled in a namespace with the platform's NetworkPolicy applied
- **THEN** the pod can establish TCP connections to the PostgreSQL service on port 5432

#### Scenario: Inventory-service pod can reach Kafka

- **WHEN** an inventory-service pod is scheduled in a namespace with the platform's NetworkPolicy applied
- **THEN** the pod can establish TCP connections to the Kafka broker service on port 9092

#### Scenario: Default-deny does not block database egress

- **WHEN** a default-deny egress NetworkPolicy is applied to the namespace
- **THEN** pods with the platform's service labels can still reach PostgreSQL, Kafka, and Redis via the explicit allow rules

### Requirement: ArgoCD SHALL have retry, notifications, and image updater configured

> **Status**: PARTIAL. Retry configured; notifications and image updater may be partial.

The platform's ArgoCD Application manifests SHALL configure: (1) automatic retry with exponential backoff for failed sync operations (`retry.backoff.duration`, `retry.backoff.factor`, `retry.backoff.maxDuration`), (2) notification triggers for sync failures, health check failures, and resource degradation via ArgoCD Notifications, and (3) integration with ArgoCD Image Updater for automatic image updates when new tags are pushed to the container registry. The ArgoCD configuration SHALL include `resourceTrackingMethod: annotation` and MUST NOT use the deprecated `legacy` tracking method.

#### Scenario: ArgoCD retries failed sync with backoff

- **WHEN** an ArgoCD sync operation fails due to a transient error
- **THEN** ArgoCD retries the sync with exponential backoff starting at the configured base duration and capping at the configured max duration

#### Scenario: ArgoCD sends notification on sync failure

- **WHEN** an ArgoCD sync operation fails after exhausting retries
- **THEN** ArgoCD Notifications sends an alert to the configured notification channel (Slack, email, or webhook)

#### Scenario: Image Updater detects new tag and triggers sync

- **WHEN** a new image tag is pushed to the container registry for a service
- **THEN** ArgoCD Image Updater detects the new tag, updates the Application manifest, and triggers a sync operation

### Requirement: All Dockerfiles SHALL follow the canonical template

> **Status**: IMPLEMENTED. Dockerfiles follow multi-stage build template with distroless, non-root, healthcheck.

The platform's Dockerfiles SHALL follow the canonical multi-stage build template that includes: (1) a builder stage with pinned Go version, (2) a final stage with distroless or minimal base image, (3) a non-root user for the application process, (4) a `HEALTHCHECK` instruction that probes the service's health endpoint, (5) build-time PGO (Profile-Guided Optimization) support via build-arg injection of PGO profiles, and (6) proper signal handling via `tini` or `dumb-init`. Dockerfiles MUST NOT run as root in the final stage and MUST NOT include debug tools or shells in the production image.

#### Scenario: Payment-service Dockerfile includes HEALTHCHECK

- **WHEN** a developer builds the payment-service Docker image
- **THEN** the resulting image includes a HEALTHCHECK instruction that probes the `/healthz` endpoint every 30 seconds

#### Scenario: Dockerfile uses non-root user

- **WHEN** a container runs the payment-service image
- **THEN** the application process runs as a non-root user (UID > 0)

#### Scenario: Dockerfile supports PGO

- **WHEN** a developer builds with `--build-arg PGO_PROFILE_PATH=/path/to/profile.pb`
- **THEN** the Go compiler uses the PGO profile to optimize the resulting binary

### Requirement: services-verify SHALL include all services

> **Status**: PARTIAL. services-verify exists; coverage of all services may be partial.

The platform's `services-verify` Make target and associated verification scripts SHALL iterate over ALL services in the platform (order-service, payment-service, inventory-service, customer-service, notification-service, shipping-service, catalog-service) and not just the original subset. The verification SHALL include: build validation, lint check, unit test execution, and health check probe for each service. The list of services MUST be derived from the `services/` directory structure rather than a hardcoded list so new services are automatically included.

#### Scenario: Verification runs against payment-service

- **WHEN** an operator runs `make services-verify`
- **THEN** the verification script builds, lints, and tests payment-service in addition to order-service, customer-service, notification-service, and catalog-service

#### Scenario: New service is automatically included

- **WHEN** a developer adds a new service directory under `services/`
- **THEN** `make services-verify` includes the new service in the verification loop without manual configuration changes

### Requirement: Kustomize placeholders SHALL be resolved for all overlays

> **Status**: NOT IMPLEMENTED. Current generic environment overlays retain unresolved placeholders and incomplete references, and CI does not yet exhaustively discover and validate every per-service/environment render.

The platform's Kustomize base and overlay kustomization.yaml files SHALL NOT contain unresolved placeholders (e.g., `SERVICE_NAME`, `IMAGE_TAG`, `NAMESPACE`) in the rendered manifests. All placeholders MUST be resolved via kustomize patches, replacements, or variable substitutions in the overlay layer. The CI pipeline SHALL include a validation step that renders the kustomize output and verifies no unresolved placeholders remain.

#### Scenario: Base kustomization resolves SERVICE_NAME

- **WHEN** a developer runs `kustomize build k8s/base`
- **THEN** the rendered YAML does not contain any `SERVICE_NAME` placeholder and all references use the correct service identifier

#### Scenario: Overlay resolves all variables

- **WHEN** a developer runs `kustomize build k8s/overlays/production`
- **THEN** the rendered YAML contains resolved values for image tags, namespace, resource limits, and all other configurable fields

### Requirement: ArgoCD repoURL SHALL point to the actual repository

> **Status**: PARTIAL / UNVERIFIED. Current ApplicationSet sources use the canonical repository URL `https://github.com/victory1908/go-microservices`; clone, generation, and live reconciliation still require validation and retained evidence for the target revision.

The platform's ArgoCD Application manifests SHALL configure `spec.source.repoURL` to the actual Git repository URL that contains the Kubernetes manifests and Kustomize overlays. The repoURL SHALL be a valid, reachable Git HTTPS URL that ArgoCD can clone. The repoURL MUST NOT be a placeholder value, empty string, or localhost reference. The repoURL SHALL be consistent across all ArgoCD Application manifests for the platform's services.

#### Scenario: ArgoCD Application has valid repoURL

- **WHEN** an operator inspects an ArgoCD Application manifest for any service
- **THEN** the `spec.source.repoURL` field contains a valid HTTPS Git URL (not a placeholder)

#### Scenario: ArgoCD sync succeeds with real repoURL

- **WHEN** ArgoCD attempts to sync an Application with the configured repoURL
- **THEN** ArgoCD clones the repository successfully and renders the Kustomize overlays without error

#### Scenario: All services share the same repoURL

- **WHEN** an operator compares the repoURL across all ArgoCD Application manifests
- **THEN** all manifests reference the same Git repository URL

### Requirement: Test coverage thresholds

> **Status**: PARTIAL. Only order-service meets the 90/90/80 thresholds. The remaining 7 services fall below the target thresholds.

The platform SHALL enforce test coverage thresholds for every service: 90% unit test coverage, 90% integration test coverage, and 80% architecture test coverage. Coverage SHALL be measured by `go test -coverprofile` and enforced by CI.

#### Scenario: CI fails when unit test coverage is below 90%

- **WHEN** a service has unit test coverage below 90%
- **THEN** the CI pipeline fails the build and reports the service name and actual coverage percentage

#### Scenario: CI fails when integration test coverage is below 90%

- **WHEN** a service has integration test coverage below 90%
- **THEN** the CI pipeline fails the build and reports the service name and actual coverage percentage

#### Scenario: CI fails when architecture test coverage is below 80%

- **WHEN** a service has architecture test coverage below 80%
- **THEN** the CI pipeline fails the build and reports the service name and actual coverage percentage

### Requirement: Secrets SHALL use external secret management for non-local environments

> **Status**: NOT IMPLEMENTED. External-secret examples exist, but they are not included in every non-local service render and committed reusable credential literals remain; no retained secret/reference validation proves this requirement.

The platform SHALL NOT hardcode secrets, credentials, or sensitive configuration in docker-compose files, SQL scripts, or application source code for non-local environments. Secrets for staging and production environments SHALL be managed via an external secret management system (e.g., HashiCorp Vault, AWS Secrets Manager, or Kubernetes Secrets with external-secrets-operator). Local development MAY use placeholder values or a local vault instance but MUST NOT commit real credentials to version control.

#### Scenario: Staging environment uses external secrets

- **WHEN** the platform deploys to the staging environment
- **THEN** database credentials, API keys, and service tokens are fetched from the external secret management system at runtime, not from docker-compose or environment files in the repository

#### Scenario: Local development uses placeholder secrets

- **WHEN** a developer runs `docker compose up` locally
- **THEN** the environment uses placeholder values for secrets (e.g., `postgres_password=localdev`) and no real credentials are present in the repository

#### Scenario: CI validates no hardcoded secrets

- **WHEN** a pull request is submitted
- **THEN** the CI pipeline scans for hardcoded secrets in docker-compose files, SQL scripts, and environment files and fails the build if real credentials are detected

### Requirement: Deployment validation is executable and exhaustive

The platform SHALL provide one deployment-validation command that verifies the canonical Compose models, pinned Collector configurations, every Kustomize service/environment overlay, Kubernetes schemas and policies, workload reference integrity, ApplicationSet generation, tracked secrets, and OpenSpec change validity.

#### Scenario: Complete deployment configuration passes

- **WHEN** a developer or CI runs deployment validation on a conforming commit
- **THEN** every required check executes, the command exits zero, and a machine-readable result lists the validated files, commands, tool versions, and commit

#### Scenario: Any required check fails the gate

- **WHEN** a Compose model, Collector config, overlay, reference, ApplicationSet, secret rule, or OpenSpec validation fails
- **THEN** the command exits non-zero and identifies the failing check without reporting overall readiness

### Requirement: Readiness claims require retained evidence

An OpenSpec requirement, task, audit, or deployment report MUST NOT claim `IMPLEMENTED`, `COMPLETE`, `production-ready`, or equivalent current readiness unless its acceptance command passed for the referenced commit and its evidence location is recorded.

#### Scenario: Status is promoted with evidence

- **WHEN** all acceptance scenarios for a capability pass on the target commit
- **THEN** its status may be updated to implemented and includes or references the validation manifest that proves the result

#### Scenario: File presence alone cannot establish implementation

- **WHEN** an artifact exists but rendering, startup, health, or acceptance validation is absent or failing
- **THEN** the capability remains partial or not implemented regardless of manually checked task boxes

#### Scenario: Historical audit is not treated as current

- **WHEN** runtime pins or deployment artifacts change after a dated audit
- **THEN** current readiness requires a new validation manifest and the historical report remains labeled as a snapshot

### Requirement: Clean-environment acceptance prevents stale-state masking

Local and CI acceptance SHALL execute with a unique project or cluster identifier and SHALL prove that required readiness comes from resources created for the tested commit rather than pre-existing containers, volumes, images, or clusters.

#### Scenario: Clean acceptance identifies tested resources

- **WHEN** the acceptance job starts
- **THEN** it records its unique project or cluster identifier, source commit, image identifiers, and initial resource inventory before creating workloads

#### Scenario: Stale resource is detected

- **WHEN** a conflicting resource from another project, commit, or previous failed run would satisfy or obstruct an acceptance check
- **THEN** preflight exits non-zero or isolates the new run and records the stale resource in diagnostics

### Requirement: Non-local secrets are externally sourced

Staging and production rendered manifests SHALL contain ExternalSecret or equivalent external-provider references for sensitive values and MUST NOT contain committed database passwords, API credentials, private keys, or reusable production ACL passwords.

#### Scenario: Production secret reference is valid

- **WHEN** a production service overlay is rendered
- **THEN** each sensitive workload input resolves through a rendered external-secret resource and a validated cluster SecretStore prerequisite

#### Scenario: Committed production credential blocks validation

- **WHEN** tracked configuration or rendered non-local manifests contain a forbidden credential literal or private key
- **THEN** secret validation exits non-zero, identifies the file and category without printing the complete secret, and blocks promotion

### Requirement: Failure evidence is collected before cleanup

Every failed local, CI, staging, or production acceptance run SHALL collect bounded diagnostics before automatic cleanup or rollback.

#### Scenario: Compose failure evidence is retained

- **WHEN** Compose startup or smoke testing fails
- **THEN** service state, health, logs, resolved model metadata, and smoke evidence are collected before project teardown

#### Scenario: Kubernetes failure evidence is retained

- **WHEN** Kubernetes rollout, Argo CD reconciliation, or environment smoke testing fails
- **THEN** rendered manifests, events, workload descriptions, logs, image IDs, and Argo CD status are collected before cleanup or rollback

