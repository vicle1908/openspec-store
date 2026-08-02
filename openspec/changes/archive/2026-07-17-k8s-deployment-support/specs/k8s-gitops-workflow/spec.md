# k8s-gitops-workflow Specification

## ADDED Requirements

### Requirement: ArgoCD ApplicationSet for all services
The platform SHALL provide an ArgoCD ApplicationSet at `deploy/argocd/applications.yaml` that generates Applications for all 8 microservices across staging and production environments using a matrix generator.

#### Scenario: ApplicationSet creates Applications for all services
- **WHEN** the ApplicationSet is applied to ArgoCD
- **THEN** Applications are created for order-service, notification-service, customer-service, catalog-service, reporting-service, payment-service, inventory-service, and shipping-service in both staging and production

#### Scenario: Application targets correct repository path
- **WHEN** an Application is created for order-service in production
- **THEN** the Application's source path points to `deploy/k8s/overlays/production`

### Requirement: Automated sync policy
The ApplicationSet SHALL configure automated sync with `prune: true` and `selfHeal: true` to ensure the cluster state matches Git state.

#### Scenario: ArgoCD syncs when Git changes
- **WHEN** a commit updates the image tag in the production overlay
- **THEN** ArgoCD automatically syncs the change within the sync window

#### Scenario: Self-heal corrects drift
- **WHEN** a manual change is made to a managed resource
- **THEN** ArgoCD reverts the change to match Git state

### Requirement: CreateNamespace sync option
The ApplicationSyncPolicy SHALL include `CreateNamespace: true` to automatically create namespaces when Applications are first deployed.

#### Scenario: Application creates namespace on first deploy
- **WHEN** an Application is deployed to a namespace that does not exist
- **THEN** the namespace is created before applying resources

### Requirement: Health assessment and retry
The ApplicationSyncPolicy SHALL configure retry with 5 attempts and exponential backoff (5s initial, 2x factor, 3m max) for failed syncs.

#### Scenario: Failed sync retries
- **WHEN** a sync fails due to transient error
- **THEN** ArgoCD retries up to 5 times with exponential backoff

#### Scenario: Health check blocks progression
- **WHEN** a resource fails its health check after sync
- **THEN** the Application is marked unhealthy and sync does not proceed

### Requirement: ArgoCD AppProject configuration
The platform SHALL provide an AppProject at `deploy/argocd/project.yaml` restricting source repos and destination namespaces.

#### Scenario: Application is restricted to allowed namespaces
- **WHEN** an Application attempts to create resources in a non-allowed namespace
- **THEN** the creation is denied by the AppProject

### Requirement: Image updater for automatic tag updates
The platform SHALL provide optional ArgoCD Image Updater configuration to automatically update image tags in Git when new images are pushed to the registry.

#### Scenario: Image updater commits new tag
- **WHEN** a new image version is pushed to the registry
- **THEN** ArgoCD Image Updater commits an updated kustomization.yaml with the new tag

### Requirement: Notification integration
The ArgoCD configuration SHALL integrate with the platform's notification system to send alerts on sync failures, health degradation, and successful deployments.

#### Scenario: Sync failure triggers notification
- **WHEN** a sync fails after all retries
- **THEN** a notification is sent to the on-call team via the configured channel
