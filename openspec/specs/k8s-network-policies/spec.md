# k8s-network-policies Specification

## Purpose

Define default-deny Kubernetes network isolation and the minimum explicitly allowed platform traffic.

## Requirements

> **Status**: IMPLEMENTED. NetworkPolicy manifests at deploy/k8s/base/ with default-deny, DNS, OTel, service-to-service, and data store egress rules.

### Requirement: Default deny all ingress and egress

> **Status**: IMPLEMENTED. Default deny NetworkPolicy exists at deploy/k8s/base/networkpolicy-default-deny.yaml.

The platform SHALL provide a NetworkPolicy at `deploy/k8s/base/networkpolicy-default-deny.yaml` that denies all ingress and egress traffic by default.

#### Scenario: New pod starts with no network access
- **WHEN** a pod is created in the namespace
- **THEN** all ingress and egress traffic is denied by default

### Requirement: Allow DNS resolution

> **Status**: IMPLEMENTED. DNS egress allowed to kube-system namespace on port 53.

The NetworkPolicy SHALL allow egress traffic to the kube-system namespace on UDP port 53 for DNS resolution.

#### Scenario: Pod resolves service name
- **WHEN** a pod needs to resolve a Kubernetes service
- **THEN** DNS queries are allowed to the cluster DNS service

### Requirement: Allow OTel Collector communication

> **Status**: IMPLEMENTED. OTel Collector egress allowed to observability namespace on ports 4317/4318.

The NetworkPolicy SHALL allow egress traffic to the observability namespace for OTel Collector endpoints (ports 4317, 4318).

#### Scenario: Service exports traces to OTel
- **WHEN** a service exports OpenTelemetry traces
- **THEN** traffic to the OTel Collector is allowed

### Requirement: Service-to-service communication

> **Status**: IMPLEMENTED. Namespace-internal ingress allowed for inter-service communication.

The NetworkPolicy SHALL allow ingress traffic from other services in the same namespace to enable inter-service communication.

#### Scenario: Order service calls customer service
- **WHEN** the order-service needs to call customer-service
- **THEN** the communication is allowed via namespace-internal policy

### Requirement: Ingress from ingress controller

> **Status**: IMPLEMENTED. Ingress from controller namespace allowed for external traffic.

The NetworkPolicy SHALL allow ingress traffic from the ingress controller namespace (nginx-ingress or Istio) for external traffic.

#### Scenario: External request reaches service
- **WHEN** a request arrives from outside the cluster
- **THEN** the ingress controller can forward traffic to the service

### Requirement: Egress to PostgreSQL

> **Status**: IMPLEMENTED. PostgreSQL egress allowed on port 5432 for database access.

The NetworkPolicy SHALL allow egress traffic to the PostgreSQL service on port 5432 for database access.

#### Scenario: Service connects to database
- **WHEN** a service needs to query PostgreSQL
- **THEN** the database connection is allowed

### Requirement: Egress to Kafka

> **Status**: IMPLEMENTED. Kafka egress allowed on port 9092 for message streaming.

The NetworkPolicy SHALL allow egress traffic to the Kafka service on port 9092 for message streaming.

#### Scenario: Service produces to Kafka
- **WHEN** a service produces a message to Kafka
- **THEN** the connection is allowed
