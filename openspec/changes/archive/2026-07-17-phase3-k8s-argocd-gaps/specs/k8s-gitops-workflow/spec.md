# k8s-gitops-workflow Specification (Delta)

## ADDED Requirements

### Requirement: Sync retry with exponential backoff
The ApplicationSet syncPolicy SHALL configure retry with a limit of 5 attempts and exponential backoff (5s initial duration, factor of 2, 3m max duration).

#### Scenario: Failed sync retries automatically
- **WHEN** a sync operation fails due to a transient error
- **THEN** ArgoCD retries up to 5 times with exponential backoff starting at 5s

#### Scenario: Retry exhausts without success
- **WHEN** all 5 retry attempts are exhausted
- **THEN** the Application is marked as OutOfSync and a notification is triggered

### Requirement: Image updater for automatic tag updates
The platform SHALL provide optional ArgoCD Image Updater configuration to automatically update image tags in Git when new images are pushed to the registry.

#### Scenario: Image updater commits new tag
- **WHEN** a new image version is pushed to the registry
- **THEN** ArgoCD Image Updater commits an updated kustomization.yaml with the new tag

### Requirement: Notification integration
The ArgoCD configuration SHALL integrate with the platform notification system to send alerts on sync failures, health degradation, and successful deployments.

#### Scenario: Sync failure triggers notification
- **WHEN** a sync fails after all retries are exhausted
- **THEN** a notification is sent to the on-call team via the configured channel

#### Scenario: Deployment success notification
- **WHEN** a sync completes successfully for a production service
- **THEN** a success notification is sent to the team channel

## MODIFIED Requirements

(None — existing requirements unchanged)

## REMOVED Requirements

(None)
