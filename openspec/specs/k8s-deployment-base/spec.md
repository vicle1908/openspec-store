# k8s-deployment-base Specification

## Purpose

Define the reusable Kubernetes base and environment overlay contract for secure, reference-complete service workloads.
## Requirements

> **Status**: STATICALLY AND LOCALLY VERIFIED. All per-service overlays pass
> schema, policy, reference, image-policy, and isolated-cluster server-side
> dry-run validation in
> `artifacts/deployment-validation/20260723T115457Z-109bc7031b/manifest.json`
> (187 passed, 0 failed, 0 skipped). The manifest records a dirty worktree
> digest, so it establishes local validation of that source snapshot only; it
> is not staging or production deployment evidence.
>
> **Acceptance evidence:** `make validate-deployment`; schema `microservices.deployment-validation/v1`; default manifest `artifacts/deployment-validation/<run-id>/manifest.json`. A manifest containing a recorded skip for image checks or server-side dry-run cannot establish full Kubernetes readiness.

### Requirement: Base Deployment template with security context

> **Status**: STATICALLY VERIFIED. Rendered workloads passed security policy and server-side dry-run checks in the retained local validation manifest.

The platform SHALL provide a Kustomize base Deployment template at `deploy/k8s/base/deployment.yaml` that includes a security context with `runAsNonRoot: true`, `runAsUser: 65532`, `fsGroup: 65532`, `allowPrivilegeEscalation: false`, `seccompProfile.type: RuntimeDefault`, and `capabilities.drop: [ALL]`.

#### Scenario: Deployment runs as non-root
- **WHEN** a Kubernetes cluster applies the base deployment template
- **THEN** the container runs with UID 65532 and the security context prevents privilege escalation

#### Scenario: Deployment uses seccomp default profile
- **WHEN** the container starts
- **THEN** seccomp uses the RuntimeDefault profile blocking risky syscalls

### Requirement: Liveness and readiness probes

> **Status**: LOCALLY VERIFIED. Rendered probe configuration passed validation and the retained local kind acceptance exercised service readiness; live cloud behavior remains outside this evidence.

The base Deployment template SHALL include both liveness and readiness HTTP probes targeting `/health/live` and `/health/ready` respectively on port 8080, with appropriate `initialDelaySeconds` and `periodSeconds`.

#### Scenario: Liveness probe fails triggers container restart
- **WHEN** the `/health/live` endpoint returns non-200 for 3 consecutive attempts
- **THEN** Kubernetes restarts the container

#### Scenario: Readiness probe gates traffic
- **WHEN** the `/health/ready` endpoint returns non-200
- **THEN** Kubernetes removes the pod from the Service endpoint slices

### Requirement: Resource requests and limits

> **Status**: STATICALLY VERIFIED. Every environment render passed resource quantity, HPA, PDB, schema, and policy validation.

The base Deployment template SHALL include resource requests and limits following the container-resource-standards capability, with requests at the minimum tier and limits at the maximum tier for the service role.

#### Scenario: Container receives guaranteed CPU allocation
- **WHEN** a node has CPU contention
- **THEN** the container receives at least its requested CPU allocation

#### Scenario: Container is throttled at limit
- **WHEN** the container exceeds its CPU limit
- **THEN** the container is throttled to the limit

### Requirement: Service template with port mapping

> **Status**: STATICALLY VERIFIED. Selector, port, and workload-reference integrity passed exhaustive render validation.

The platform SHALL provide a Kustomize base Service template at `deploy/k8s/base/service.yaml` exposing ports 8080 (HTTP) and 9090 (metrics) with appropriate port names.

#### Scenario: Service routes traffic to healthy pods
- **WHEN** traffic arrives at the Service
- **THEN** traffic is routed only to pods where the readiness probe succeeds

### Requirement: ServiceAccount template

> **Status**: STATICALLY VERIFIED. Rendered ServiceAccount references passed exhaustive render and server-side dry-run validation; effective cloud-cluster authorization remains a live-deployment concern.

The platform SHALL provide a ServiceAccount template with a corresponding Role granting read access to ConfigMaps and Secrets within the service's namespace.

#### Scenario: Service account has least-privilege permissions
- **WHEN** the service account attempts to access cluster-scoped resources
- **THEN** the access is denied by the Role binding

### Requirement: RollingUpdate strategy

> **Status**: STATICALLY VERIFIED. RollingUpdate, replica, HPA, and PDB combinations passed policy and schema validation; live rollout availability remains unverified.

The Deployment template SHALL use `RollingUpdate` strategy with `maxUnavailable: 25%` and `maxSurge: 25%` to enable zero-downtime deployments.

#### Scenario: Rolling update maintains availability
- **WHEN** a new version is deployed
- **THEN** at least 75% of desired replicas remain available during the rollout

### Requirement: Kustomize configuration

> **Status**: STATICALLY VERIFIED. All local, staging, and production service overlays rendered successfully and passed reference-completeness checks.

The base directory SHALL include a `kustomization.yaml` that references all base templates, sets common labels (`app.kubernetes.io/part-of: microservices-platform`), and configures namespace injection.

#### Scenario: Kustomize builds complete manifest
- **WHEN** `kustomize build deploy/k8s/base` is executed
- **THEN** a valid Kubernetes manifest is output with all resources

### Requirement: Rendered workload references are complete

Every ServiceAccount, ConfigMap, Secret or ExternalSecret target, Service selector, HPA target, PDB selector, volume, and workload reference in rendered output SHALL resolve to an object in the same render or to an explicitly validated cluster prerequisite.

#### Scenario: Workload references resolve

- **WHEN** reference-integrity validation examines a rendered service overlay
- **THEN** every namespaced workload reference resolves to the expected rendered object and selectors match the intended Pods

#### Scenario: Dangling service account or configuration reference fails

- **WHEN** a Deployment references a ServiceAccount, ConfigMap, or Secret that is neither rendered nor declared as a cluster prerequisite
- **THEN** validation exits non-zero and reports the referring workload and missing object

### Requirement: Kubernetes schema and policy validation precedes apply

Rendered manifests SHALL pass pinned Kubernetes schema validation, platform policy checks, and server-side dry-run against a compatible disposable cluster before staging or production promotion.

#### Scenario: Valid manifests pass the deployment gate

- **WHEN** all rendered resources use supported API versions, valid quantities, valid selectors, and permitted security settings
- **THEN** schema validation, policy validation, and server-side dry-run all exit zero

#### Scenario: Invalid resource quantity blocks deployment

- **WHEN** a rendered workload contains an invalid CPU or memory quantity
- **THEN** validation exits non-zero before Argo CD promotion and records the resource and field

### Requirement: Environment image policy is explicit

Local overlays SHALL use uniquely tagged locally available images with a pull policy compatible with kind image loading or the documented local registry. Staging and production overlays SHALL reference immutable registry digests.

#### Scenario: kind uses the locally built image

- **WHEN** a local service image is loaded into the named kind cluster and its overlay is applied
- **THEN** the Pod starts from that unique image without attempting to resolve an unrelated mutable registry tag

#### Scenario: Non-local image is immutable

- **WHEN** a staging or production overlay is rendered
- **THEN** each service workload image contains an OCI digest and no mutable `latest` tag
