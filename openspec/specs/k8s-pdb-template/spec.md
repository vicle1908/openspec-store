# k8s-pdb-template Specification

## Purpose

Define voluntary-disruption availability guarantees that remain compatible with replica and autoscaling settings.

## Requirements

> **Status**: IMPLEMENTED. PDB template at deploy/k8s/base/pdb.yaml with minAvailable: 1 and HPA integration.

### Requirement: PodDisruptionBudget for each service

> **Status**: IMPLEMENTED. PDB template exists at deploy/k8s/base/pdb.yaml with minAvailable: 1.

The platform SHALL provide a PodDisruptionBudget template at `deploy/k8s/base/pdb.yaml` ensuring at least 1 pod remains available during voluntary disruptions (node drain, cluster upgrade).

#### Scenario: Node drain preserves minimum availability
- **WHEN** a node is drained for maintenance
- **THEN** the PDB prevents eviction of the last remaining pod

#### Scenario: PDB allows voluntary disruptions above minimum
- **WHEN** 3 replicas exist and PDB minAvailable is 1
- **THEN** 2 pods can be evicted simultaneously

### Requirement: minAvailable configuration

> **Status**: IMPLEMENTED. PDB template configured with minAvailable: 1 as default.

The PDB template SHALL configure `minAvailable: 1` as the default, ensuring the service maintains availability during cluster operations.

#### Scenario: High-availability service uses higher minAvailable
- **WHEN** a service requires higher availability guarantees
- **THEN** the production overlay patches minAvailable to 2

### Requirement: Selector-based targeting

> **Status**: IMPLEMENTED. PDB uses label selector matching service Deployment label.

The PDB SHALL use a label selector matching the service's Deployment label (`app: <service-name>`).

#### Scenario: PDB applies to correct pods
- **WHEN** the PDB is created
- **THEN** it matches all pods with the service's app label

### Requirement: Integration with HPA

> **Status**: IMPLEMENTED. PDB and HPA configured to work together with proper coordination.

The PDB and HPA SHALL be configured to work together: PDB ensures minimum availability while HPA manages replica count.

#### Scenario: HPA respects PDB during scale-down
- **WHEN** HPA attempts to scale down below PDB minAvailable
- **THEN** HPA stops at minAvailable pods

### Requirement: Unhealthy pod eviction

> **Status**: IMPLEMENTED. PDB allows eviction of unhealthy pods failing health checks.

The PDB SHALL NOT prevent eviction of pods that fail health checks or are in a terminating state.

#### Scenario: Failed pod is replaced
- **WHEN** a pod fails its liveness probe
- **THEN** the pod is evicted and replaced by the Deployment controller
