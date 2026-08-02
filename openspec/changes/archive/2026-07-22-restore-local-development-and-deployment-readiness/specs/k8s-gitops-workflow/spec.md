## ADDED Requirements

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

## REMOVED Requirements

### Requirement: CreateNamespace sync option

**Reason**: Service Applications must not create environment tenancy implicitly. Namespace lifecycle is a separately authorized platform prerequisite, and the constrained AppProject intentionally grants no Namespace resource ownership.

**Migration**: Pre-create `microservices-local`, `microservices-staging`, and `microservices` through the platform bootstrap process, validate their existence before enabling the corresponding ApplicationSet, and remove `CreateNamespace=true` from service Application sync options.

### Requirement: Image updater for automatic tag updates

**Reason**: Automatic mutable-tag updates cannot prove that deployed content matches the selected multi-architecture build, scan, attestation, and digest evidence, and they bypass the reviewed Git promotion path.

**Migration**: Publish immutable digests in the build workflow, update the selected environment Kustomize image digest through a promotion pull request, and let Argo CD reconcile the merged commit.
