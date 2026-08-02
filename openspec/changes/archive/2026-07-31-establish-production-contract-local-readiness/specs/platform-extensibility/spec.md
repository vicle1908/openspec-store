## MODIFIED Requirements

### Requirement: Local Compose is not production topology

The Docker Compose stack SHALL provide reproducible local development with
pinned images, health checks, internal/external listener separation, persistent
volumes where useful, and optional tools profiles. Its canonical readiness
profile SHALL preserve production application contracts for roles,
configuration validation, data ownership, authenticated dependency protocols,
workload authorization, observability, provider behavior, idempotency, failure,
and recovery. It SHALL explicitly record reduced replica, broker, replication,
failure-domain, resource, secret-provider, and certificate-provider topology and
MUST NOT be represented as production HA or cloud deployment evidence.

#### Scenario: Fresh production-contract startup
- **WHEN** a developer starts the canonical stack with empty volumes
- **THEN** secure identities, migrations, topics, publications, connectors, namespaces, and authorization policies initialize idempotently before dependent runtimes start

#### Scenario: Local topology reduction is reviewed
- **WHEN** the local stack uses one broker, one PostgreSQL server, one Temporal server, or one replica
- **THEN** the reduction is present in the runtime contract and retained evidence
- **AND** application security and behavioral contracts remain enforced

#### Scenario: Local evidence is described as production HA
- **WHEN** a consumer attempts to use local evidence as proof of multi-zone, autoscaling, managed-service, GitOps, or production rollback readiness
- **THEN** validation rejects the claim and identifies the required external evidence class

