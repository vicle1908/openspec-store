# k8s-pdb-template Specification

## ADDED Requirements

### Requirement: PodDisruptionBudget for each service
The platform SHALL provide a PodDisruptionBudget template at `deploy/k8s/base/pdb.yaml` ensuring at least 1 pod remains available during voluntary disruptions (node drain, cluster upgrade).

#### Scenario: Node drain preserves minimum availability
- **WHEN** a node is drained for maintenance
- **THEN** the PDB prevents eviction of the last remaining pod

#### Scenario: PDB allows voluntary disruptions above minimum
- **WHEN** 3 replicas exist and PDB minAvailable is 1
- **THEN** 2 pods can be evicted simultaneously

### Requirement: minAvailable configuration
The PDB template SHALL configure `minAvailable: 1` as the default, ensuring the service maintains availability during cluster operations.

#### Scenario: High-availability service uses higher minAvailable
- **WHEN** a service requires higher availability guarantees
- **THEN** the production overlay patches minAvailable to 2

### Requirement: Selector-based targeting
The PDB SHALL use a label selector matching the service's Deployment label (`app: <service-name>`).

#### Scenario: PDB applies to correct pods
- **WHEN** the PDB is created
- **THEN** it matches all pods with the service's app label

### Requirement: Integration with HPA
The PDB and HPA SHALL be configured to work together: PDB ensures minimum availability while HPA manages replica count.

#### Scenario: HPA respects PDB during scale-down
- **WHEN** HPA attempts to scale down below PDB minAvailable
- **THEN** HPA stops at minAvailable pods

### Requirement: Unhealthy pod eviction
The PDB SHALL NOT prevent eviction of pods that fail health checks or are in a terminating state.

#### Scenario: Failed pod is replaced
- **WHEN** a pod fails its liveness probe
- **THEN** the pod is evicted and replaced by the Deployment controller
