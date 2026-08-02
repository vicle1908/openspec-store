# k8s-network-policies Specification (Delta)

## ADDED Requirements

### Requirement: Egress to PostgreSQL
The NetworkPolicy SHALL allow egress traffic to the PostgreSQL service on port 5432 for database access.

#### Scenario: Service connects to database
- **WHEN** a service needs to query PostgreSQL
- **THEN** the database connection is allowed via TCP port 5432

#### Scenario: Egress rule applies to all pods
- **WHEN** any pod in the namespace needs database access
- **THEN** the egress rule uses `podSelector: {}` to match all pods

### Requirement: Egress to Kafka
The NetworkPolicy SHALL allow egress traffic to the Kafka service on port 9092 for message streaming.

#### Scenario: Service produces to Kafka
- **WHEN** a service produces a message to Kafka
- **THEN** the connection is allowed via TCP port 9092

#### Scenario: Egress rule applies to all pods
- **WHEN** any pod in the namespace needs broker access
- **THEN** the egress rule uses `podSelector: {}` to match all pods

## MODIFIED Requirements

(None — existing requirements unchanged)

## REMOVED Requirements

(None)
