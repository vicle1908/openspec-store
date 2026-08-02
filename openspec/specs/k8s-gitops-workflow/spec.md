# k8s-gitops-workflow Specification

## Purpose

Define Git-owned, Argo CD-reconciled deployment generation, health, update, and notification behavior for all platform services.
## Requirements

> **Status**: STATICALLY VERIFIED / LIVE UNVERIFIED. Application generation,
> repository/path values, cluster selection, AppProject policy, and deployment
> source ownership pass the retained local deployment validation manifest.
> Staging reconciliation, health, smoke, immutable published-image evidence,
> and production promotion remain active cloud work.
>
> **Acceptance evidence:** `make validate-deployment` plus staging reconciliation and environment smoke at the promoted revision. The validation manifest uses schema `microservices.deployment-validation/v1` and defaults to `artifacts/deployment-validation/<run-id>/manifest.json`; live Argo CD health and smoke evidence must be retained with it.

### Requirement: ArgoCD ApplicationSets for all services

> **Status**: STATICALLY VERIFIED. Local, staging, and production ApplicationSets generate the expected service Applications; live reconciliation and smoke evidence remains required.

The platform SHALL provide environment-specific ApplicationSets at `deploy/argocd/applications-{local,staging,production}.yaml` that generate Applications for all 8 microservices using matrix generators and the corresponding registered environment cluster.

#### Scenario: ApplicationSet creates Applications for all services
- **WHEN** the ApplicationSet is applied to ArgoCD
- **THEN** Applications are created for order-service, notification-service, customer-service, catalog-service, reporting-service, payment-service, inventory-service, and shipping-service in both staging and production

#### Scenario: Application targets correct repository path
- **WHEN** an Application is created for order-service in production
- **THEN** the Application's source path points to `deploy/k8s/overlays/production/order-service`

### Requirement: Automated sync policy

> **Status**: PARTIAL / UNVERIFIED. Sync-policy fields exist, but no retained reconciliation evidence proves them against valid generated Applications and selected environment clusters.

The ApplicationSet SHALL configure automated sync with `prune: true` and `selfHeal: true` to ensure the cluster state matches Git state.

#### Scenario: ArgoCD syncs when Git changes
- **WHEN** a commit updates the image tag in the production overlay
- **THEN** ArgoCD automatically syncs the change within the sync window

#### Scenario: Self-heal corrects drift
- **WHEN** a manual change is made to a managed resource
- **THEN** ArgoCD reverts the change to match Git state

### Requirement: Health assessment and retry

> **Status**: PARTIAL / UNVERIFIED. Retry fields are present; successful health-gated reconciliation evidence is pending.

The ApplicationSyncPolicy SHALL configure retry with 5 attempts and exponential backoff (5s initial, 2x factor, 3m max) for failed syncs.

#### Scenario: Failed sync retries
- **WHEN** a sync fails due to transient error
- **THEN** ArgoCD retries up to 5 times with exponential backoff

#### Scenario: Health check blocks progression
- **WHEN** a resource fails its health check after sync
- **THEN** the Application is marked unhealthy and sync does not proceed

### Requirement: ArgoCD AppProject configuration

> **Status**: STATICALLY VERIFIED. Repository, destination, namespace, and cluster-scoped prerequisite constraints pass the deployment validator; effective live-cluster authorization remains unverified.

The platform SHALL provide an AppProject at `deploy/argocd/project.yaml` restricting source repos and destination namespaces.

#### Scenario: Application is restricted to allowed namespaces
- **WHEN** an Application attempts to create resources in a non-allowed namespace
- **THEN** the creation is denied by the AppProject

### Requirement: Notification integration

> **Status**: DEFERRED. Notification integration not yet implemented.

The ArgoCD configuration SHALL integrate with the platform's notification system to send alerts on sync failures, health degradation, and successful deployments.

#### Scenario: Sync failure triggers notification
- **WHEN** a sync fails after all retries
- **THEN** a notification is sent to the on-call team via the configured channel

### Requirement: ApplicationSets generate valid environment applications

Argo CD ApplicationSets SHALL generate one Application per selected service and environment using valid Git directory and cluster generator parameters. Templates SHALL enable missing-key failure, use an actual repository URL, point `source.path` to the directory containing `kustomization.yaml`, and select clusters through explicit environment labels.

#### Scenario: Staging and production Applications are generated

- **WHEN** the ApplicationSets evaluate against registered staging and production cluster secrets
- **THEN** exactly one Application is generated for each of the eight services in each selected environment with a valid repository, revision, overlay directory, destination server, and namespace

#### Scenario: Missing generator value fails generation

- **WHEN** a template references an image, revision, cluster, or path value not supplied by its generators
- **THEN** ApplicationSet rendering fails with a missing-key error instead of creating an incomplete Application

#### Scenario: Local ApplicationSet targets real local overlays

- **WHEN** the local ApplicationSet evaluates for the registered kind cluster
- **THEN** it generates Applications only for existing per-service local overlay directories and uses the canonical repository URL

### Requirement: Git is the sole owner of Argo-managed deployment state

CI SHALL NOT imperatively apply or mutate application resources owned by Argo CD. Desired service images and configuration SHALL be committed to Git, and Argo CD SHALL reconcile that commit to the target cluster.

#### Scenario: Promotion changes Git before cluster state

- **WHEN** an approved service release is promoted
- **THEN** the environment overlay is updated in Git before Argo CD changes the cluster and the promotion evidence records the commit

#### Scenario: Competing imperative apply is rejected

- **WHEN** a deployment workflow attempts `kubectl apply` against an Argo-managed application overlay
- **THEN** workflow policy validation fails before cluster mutation

### Requirement: Service images are promoted by immutable digest

The build workflow SHALL publish each service for linux/amd64 and linux/arm64, capture its registry digest, and promote that digest into the target environment overlay through a reviewable Git change.

#### Scenario: Build outputs digest evidence

- **WHEN** a service image is built and pushed successfully
- **THEN** the workflow records the service name, source commit, image repository, platforms, and immutable digest in a machine-readable artifact

#### Scenario: Promotion uses exact built content

- **WHEN** the promotion change is rendered for staging or production
- **THEN** the service image digest equals the digest recorded by the selected build and no mutable tag determines deployed content

#### Scenario: Partial matrix failure prevents promotion

- **WHEN** any required service image fails to build, scan, attest, or publish
- **THEN** no environment promotion change is created for that release set

### Requirement: Argo CD health gates deployment completion

A deployment SHALL complete only after all promoted Applications report Synced and Healthy and the environment smoke test succeeds within bounded time.

#### Scenario: Healthy reconciliation completes deployment

- **WHEN** Argo CD reconciles the promoted Git commit and all required Applications become Synced and Healthy
- **THEN** the workflow runs the environment smoke test and records Argo CD revision and health evidence

#### Scenario: Unhealthy application blocks completion

- **WHEN** any required Application remains OutOfSync, Degraded, Missing, or Progressing beyond the timeout
- **THEN** deployment exits non-zero, captures Application and resource diagnostics, and does not report success

### Requirement: Git revert is the deployment rollback mechanism

The platform SHALL support rollback by reverting the environment configuration or digest promotion commit and allowing Argo CD to reconcile the last-known-good desired state.

#### Scenario: Failed release is reverted

- **WHEN** post-deployment verification fails and an operator approves rollback
- **THEN** the promotion commit is reverted, Argo CD returns all affected Applications to Synced and Healthy on the prior digests, and rollback evidence is retained
