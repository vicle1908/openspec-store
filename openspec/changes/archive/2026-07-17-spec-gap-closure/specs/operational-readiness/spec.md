# operational-readiness Specification

## ADDED Requirements

### Requirement: Broker UI SHALL be available in tools overlay

The platform SHALL provide a broker UI service (kafka-ui or equivalent) in the tools docker-compose overlay so operators can inspect Kafka topics, consumer groups, messages, and broker configuration through a web interface. The tools overlay SHALL expose the broker UI on a configurable port (default 8080) and MUST NOT be included in the production or base overlays. The broker UI SHALL have read-only access to Kafka by default and MUST NOT be granted topic creation or deletion permissions without explicit operator override.

#### Scenario: Broker UI is accessible in tools overlay

- **WHEN** an operator runs `docker compose --profile tools up kafka-ui`
- **THEN** the broker UI is accessible at `http://localhost:8080` and can list all Kafka topics in the local development cluster

#### Scenario: Broker UI is not included in base overlay

- **WHEN** an operator runs `docker compose up` without the tools profile
- **THEN** no broker UI container is started and port 8080 is not bound

### Requirement: Rollback rehearsal SHALL be executable via make target

The platform SHALL provide a `rehearse-rollback` Make target in the root Makefile that executes the rollback rehearsal script (`scripts/rehearse-rollback.sh`). The rehearsal script MUST validate the rollback procedure for each service by simulating a deployment rollback against the target environment (staging by default) and confirming that the previous image tag is available, the health check passes after rollback, and the service returns to a ready state. The rehearsal script SHALL produce a structured report (exit 0 on success, non-zero on failure) and MUST NOT perform an actual rollback in production environments without an explicit `CONFIRM_PRODUCTION=1` flag.

#### Scenario: Rollback rehearsal succeeds against staging

- **WHEN** an operator runs `make rehearse-rollback SERVICE=order-service ENV=staging`
- **THEN** the script validates that the previous image tag exists, simulates the rollback, runs the health check, and exits 0 with a success report

#### Scenario: Rollback rehearsal blocks production without confirmation

- **WHEN** an operator runs `make rehearse-rollback SERVICE=order-service ENV=production` without `CONFIRM_PRODUCTION=1`
- **THEN** the script exits with code 1 and prints an error message indicating production rollback rehearsal requires explicit confirmation

### Requirement: Service runbooks SHALL exist for each service

The platform SHALL maintain a runbook in `docs/runbooks/` for every service in the platform (order-service, payment-service, inventory-service, customer-service, notification-service, shipping-service, catalog-service). Each runbook SHALL document: service purpose and ownership, key dependencies (databases, message brokers, external APIs), common failure modes and remediation steps, escalation contacts, rollback procedure, scaling guidance, and diagnostic commands. Runbooks MUST be reviewed and updated whenever a service's deployment or dependency topology changes.

#### Scenario: Runbook exists for order-service

- **WHEN** an operator reads `docs/runbooks/order-service.md`
- **THEN** the file exists and contains sections for Dependencies, Failure Modes, Remediation, Rollback, Scaling, and Escalation

#### Scenario: Runbook is referenced from service README

- **WHEN** a developer reads `services/order-service/README.md`
- **THEN** the README includes a link to `docs/runbooks/order-service.md`

### Requirement: Agent configs SHALL be wired for all supported agents

The platform SHALL provide properly configured agent configuration files for all supported AI coding agents (Claude via `.claude/settings.json`, Cursor via `.cursor/mcp.json`, Codex, KiloCode, Kiro, Factory, and OpenCode). Each configuration file SHALL reference the correct MCP server endpoints, tool permissions, and project-specific context. Configuration files MUST be kept in sync with the platform's service topology and MUST NOT contain hardcoded secrets or credentials.

#### Scenario: Claude settings reference correct MCP servers

- **WHEN** a developer opens the project with Claude Code
- **THEN** `.claude/settings.json` contains MCP server configurations pointing to the correct endpoints for the platform's services

#### Scenario: Cursor MCP config includes all required tools

- **WHEN** a developer opens the project with Cursor
- **THEN** `.cursor/mcp.json` lists all MCP tool servers required for platform development with valid connection strings

### Requirement: K8s NetworkPolicy SHALL allow database and messaging egress

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

The platform's `services-verify` Make target and associated verification scripts SHALL iterate over ALL services in the platform (order-service, payment-service, inventory-service, customer-service, notification-service, shipping-service, catalog-service) and not just the original subset. The verification SHALL include: build validation, lint check, unit test execution, and health check probe for each service. The list of services MUST be derived from the `services/` directory structure rather than a hardcoded list so new services are automatically included.

#### Scenario: Verification runs against payment-service

- **WHEN** an operator runs `make services-verify`
- **THEN** the verification script builds, lints, and tests payment-service in addition to order-service, customer-service, notification-service, and catalog-service

#### Scenario: New service is automatically included

- **WHEN** a developer adds a new service directory under `services/`
- **THEN** `make services-verify` includes the new service in the verification loop without manual configuration changes

### Requirement: Kustomize placeholders SHALL be resolved for all overlays

The platform's Kustomize base and overlay kustomization.yaml files SHALL NOT contain unresolved placeholders (e.g., `SERVICE_NAME`, `IMAGE_TAG`, `NAMESPACE`) in the rendered manifests. All placeholders MUST be resolved via kustomize patches, replacements, or variable substitutions in the overlay layer. The CI pipeline SHALL include a validation step that renders the kustomize output and verifies no unresolved placeholders remain.

#### Scenario: Base kustomization resolves SERVICE_NAME

- **WHEN** a developer runs `kustomize build k8s/base`
- **THEN** the rendered YAML does not contain any `SERVICE_NAME` placeholder and all references use the correct service identifier

#### Scenario: Overlay resolves all variables

- **WHEN** a developer runs `kustomize build k8s/overlays/production`
- **THEN** the rendered YAML contains resolved values for image tags, namespace, resource limits, and all other configurable fields

### Requirement: Secrets SHALL use external secret management for non-local environments

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
