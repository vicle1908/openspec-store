## Context

PostgreSQL is authoritative and service transactions already write their
domain changes and outbox rows atomically. Order has an idempotent Debezium
registration path in Compose and local kind. Payment, inventory, shipping,
notification, customer, and catalog have some combination of migrations,
publications, slots, topic provisioning, connector claims, or placeholder
infrastructure roles, but no complete retained registration-and-delivery path.

The design must preserve service-owned schemas, current event topics and
at-least-once delivery. It must work on macOS arm64 through the already pinned
Debezium image and must not imply cloud readiness.

## Goals / Non-Goals

**Goals:**

- Give every CDC-owning service one canonical connector config aligned with its
  outbox table, publication, slot, topic, and database credentials.
- Register connectors idempotently after Postgres, Kafka, Debezium, migrations,
  and topic provisioning are ready.
- Fail local bootstrap and readiness when a required connector is absent,
  failed, or materially misconfigured.
- Retain machine-readable evidence for connector state and representative
  outbox-to-Kafka delivery.
- Share validation and registration behavior without coupling service domain
  packages.

**Non-Goals:**

- Staging or production connector rollout, cloud secret management, GitOps
  reconciliation, image publishing, or CI/CD promotion.
- Changing event schemas, topic names, database ownership, or delivery from
  at-least-once to exactly-once.
- Deleting existing replication slots, publications, outbox rows, or topics.

## Decisions

1. Use one connector per service-owned outbox. This preserves independent
   failure domains, offsets, publication ownership, and topic routing. A shared
   multi-table connector was rejected because it couples service rollout and
   credentials.

2. Mirror the proven order registration pattern through a shared, parameterized
   registration helper invoked by service-specific infrastructure-init
   workloads. Registration performs bounded Debezium readiness retries, reads
   the current connector config, creates when absent, and updates only when the
   canonical configuration differs. Blind delete-and-recreate was rejected
   because it can disturb offsets and increases duplicate-delivery risk.

3. Keep canonical connector JSON beside each owning service and mount it
   read-only into Compose/local-kind registration workloads. Static validation
   checks the config against the owning migration and topic declaration.

4. Require `pgoutput`, `publication.autocreate.mode=disabled`, explicit
   publication and slot names, an exact outbox table include list, Outbox Event
   Router topic replacement, heartbeats, JSON-compatible value conversion, and
   idempotent Kafka producer overrides. Database credentials remain environment
   inputs and are not committed in connector JSON.

5. Treat connector `RUNNING` state as necessary but not sufficient. Local
   acceptance inserts a uniquely identified representative outbox event through
   the owning service transaction path when available, consumes the routed
   Kafka record, and retains connector status plus delivery diagnostics.

6. Use service-scoped readiness checks for required connector state without
   importing infrastructure into domain/application packages. Infrastructure
   roles and deployment health gates own this responsibility.

## Risks / Trade-offs

- [Connector update changes offset-sensitive fields] → Reject incompatible
  changes with diagnostics and require an explicit migration rather than
  silently deleting the connector.
- [At-least-once replay produces duplicates] → Preserve stable event IDs and
  require downstream idempotency; acceptance checks identity, not message count.
- [Replication slot conflicts with stale local state] → Diagnose connector,
  publication, and slot ownership; never auto-drop durable database objects.
- [Six extra connectors increase local resource use] → Retain explicit resource
  limits and validate arm64 support using the existing pinned Debezium image.
- [Startup ordering creates long waits] → Bound retries, expose the final REST
  error/status, and fail closed instead of marking services ready.

## Migration Plan

1. Add and statically validate connector configs service by service.
2. Add idempotent registration to Compose, then prove connector convergence.
3. Add equivalent local-kind ConfigMaps/workloads and readiness ordering.
4. Add representative delivery acceptance and retain evidence.
5. Update current spec statuses and service runbooks only for services whose
   evidence passes.

Rollback removes new registration workloads and config mounts. It does not
delete connectors automatically; operators may pause them if needed, while
publications, slots, topics, and outbox data remain intact for recovery.

## Resolved Questions

- Notification routes by its migration-defined `event_type` field to the
  implemented `notifications.events.v1` topic. This proves the local connector
  path without overstating the still-unimplemented normative
  `notifications.dispatch.v1` application transaction.
- Customer and catalog retain thin service entry points that call the shared
  CDC helper, preserving role-specific startup diagnostics while sharing
  PostgreSQL prerequisite and connector convergence behavior.
