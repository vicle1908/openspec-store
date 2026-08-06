# k8s-deployment-base Specification

## ADDED Requirements

### Requirement: Base Deployment template with security context
The platform SHALL provide a Kustomize base Deployment template at `deploy/k8s/base/deployment.yaml` that includes a security context with `runAsNonRoot: true`, `runAsUser: 65532`, `fsGroup: 65532`, `allowPrivilegeEscalation: false`, `seccompProfile.type: RuntimeDefault`, and `capabilities.drop: [ALL]`.

#### Scenario: Deployment runs as non-root
- **WHEN** a Kubernetes cluster applies the base deployment template
- **THEN** the container runs with UID 65532 and the security context prevents privilege escalation

#### Scenario: Deployment uses seccomp default profile
- **WHEN** the container starts
- **THEN** seccomp uses the RuntimeDefault profile blocking risky syscalls

### Requirement: Liveness and readiness probes
The base Deployment template SHALL include both liveness and readiness HTTP probes targeting `/health/live` and `/health/ready` respectively on port 8080, with appropriate `initialDelaySeconds` and `periodSeconds`.

#### Scenario: Liveness probe fails triggers container restart
- **WHEN** the `/health/live` endpoint returns non-200 for 3 consecutive attempts
- **THEN** Kubernetes restarts the container

#### Scenario: Readiness probe gates traffic
- **WHEN** the `/health/ready` endpoint returns non-200
- **THEN** Kubernetes removes the pod from the Service endpoint slices

### Requirement: Resource requests and limits
The base Deployment template SHALL include resource requests and limits following the container-resource-standards capability, with requests at the minimum tier and limits at the maximum tier for the service role.

#### Scenario: Container receives guaranteed CPU allocation
- **WHEN** a node has CPU contention
- **THEN** the container receives at least its requested CPU allocation

#### Scenario: Container is throttled at limit
- **WHEN** the container exceeds its CPU limit
- **THEN** the container is throttled to the limit

### Requirement: Service template with port mapping
The platform SHALL provide a Kustomize base Service template at `deploy/k8s/base/service.yaml` exposing ports 8080 (HTTP) and 9090 (metrics) with appropriate port names.

#### Scenario: Service routes traffic to healthy pods
- **WHEN** traffic arrives at the Service
- **THEN** traffic is routed only to pods where the readiness probe succeeds

### Requirement: ServiceAccount template
The platform SHALL provide a ServiceAccount template with a corresponding Role granting read access to ConfigMaps and Secrets within the service's namespace.

#### Scenario: Service account has least-privilege permissions
- **WHEN** the service account attempts to access cluster-scoped resources
- **THEN** the access is denied by the Role binding

### Requirement: RollingUpdate strategy
The Deployment template SHALL use `RollingUpdate` strategy with `maxUnavailable: 25%` and `maxSurge: 25%` to enable zero-downtime deployments.

#### Scenario: Rolling update maintains availability
- **WHEN** a new version is deployed
- **THEN** at least 75% of desired replicas remain available during the rollout

### Requirement: Kustomize configuration
The base directory SHALL include a `kustomization.yaml` that references all base templates, sets common labels (`app.kubernetes.io/part-of: go-microservices-platform`), and configures namespace injection.

#### Scenario: Kustomize builds complete manifest
- **WHEN** `kustomize build deploy/k8s/base` is executed
- **THEN** a valid Kubernetes manifest is output with all resources

### Requirement: Environment-specific overlays
The platform SHALL provide overlay directories at `deploy/k8s/overlays/{local,staging,production}` that patch the base templates with environment-specific values.

#### Scenario: Production overlay increases replica count
- **WHEN** the production overlay is applied
- **THEN** the Deployment has at least 3 replicas

#### Scenario: Production overlay applies stricter resource limits
- **WHEN** the production overlay is applied
- **THEN** the resource limits match the production tier from container-resource-standards
