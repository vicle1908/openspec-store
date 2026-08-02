## ADDED Requirements

### Requirement: Per-service environment overlays render deployable resources

The platform SHALL provide local, staging, and production Kustomize overlays for each of the eight services. Every rendered workload SHALL contain resolved image, role, port, resource, identity, configuration, and secret values and MUST contain no placeholder token.

#### Scenario: Every overlay renders without placeholders

- **WHEN** CI renders every directory matching `deploy/k8s/overlays/{local,staging,production}/*-service`
- **THEN** each render exits zero and contains no `SERVICE_NAME`, `IMAGE_PLACEHOLDER`, `ROLE_PLACEHOLDER`, version placeholder, or resource placeholder

#### Scenario: Generic placeholder overlays are rejected

- **WHEN** an overlay relies on an unresolved generic service name or resource quantity
- **THEN** deployment validation exits non-zero and identifies the file and field before cluster application

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

### Requirement: Environment resource sets are complete

Each service overlay SHALL define workload resources and replicas appropriate to the service role and environment, and SHALL include HPA and PDB resources only where their replica semantics are valid.

#### Scenario: Production availability resources agree

- **WHEN** a production service overlay renders with an HPA and PDB
- **THEN** Deployment replicas, HPA minimum replicas, and PDB availability permit a rolling update without an impossible scheduling or eviction condition

#### Scenario: One-replica local service avoids impossible disruption policy

- **WHEN** a local overlay renders a single replica
- **THEN** its disruption policy is absent or configured so routine local maintenance is not permanently blocked

## REMOVED Requirements

### Requirement: Environment-specific overlays

**Reason**: A single `SERVICE_NAME`-based local, staging, or production overlay cannot resolve the distinct images, roles, ports, resources, identities, and secrets of eight independently deployable services and currently renders invalid resources.

**Migration**: Replace consumers of `deploy/k8s/overlays/{local,staging,production}` with the corresponding per-service directories under each environment and aggregate them through ApplicationSets or explicit Kustomize resources.
