# operational-readiness Delta Spec

> **Change**: ecosystem-alignment
> **Base**: openspec/specs/operational-readiness/spec.md
> **Date**: 2026-07-18

## Purpose

This delta updates the operational-readiness spec to add ArgoCD repoURL configuration and document test coverage threshold gaps across non-order services.

---

## ADDED Requirements

### Requirement: ArgoCD repoURL SHALL point to the actual repository

> **Status**: NOT IMPLEMENTED. ArgoCD Application manifests currently use a placeholder repository URL (`https://github.com/org/go-microservices`). GitOps sync will fail until this is resolved.

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

---

## MODIFIED Requirements

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
