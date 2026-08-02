# customer-gdpr-export Specification

## Purpose

Implements GDPR export (right to portability) and cryptographic erasure (right to be forgotten) via Temporal workflows with a configurable 30-day retention period and audit logging.
## Requirements
### Requirement: GDPR Article 15 data export

The customer service SHALL expose `POST /api/v1/customers/{id}/gdpr/export` to request an asynchronous export. The request MUST carry an `Idempotency-Key` header and SHALL return `202 Accepted` with the durable export identifier and current status. The service SHALL expose `GET /api/v1/customers/{id}/gdpr/export?idempotency_key=<key>` as a read-only lookup that returns the durable export representation when available.

A completed representation SHALL contain `export_id`, `customer_id`, `idempotency_key`, `sha256_hash`, `payload`, `status`, `created_at`, and `completed_at`. The payload SHALL include the customer profile, all addresses, the soft-delete timestamp when present, the purge timestamp when present, and the customer's audit-log entries. The content hash MUST be calculated from the stored payload.

A repeated POST for the same customer and idempotency key MUST return the existing export state, preserve the export ID, content hash, and payload, and MUST NOT start another workflow. An authenticated subject MUST have access to the requested customer; unauthorized cross-tenant access SHALL return `403 Forbidden`.

#### Scenario: Export request completes through durable lookup

- **WHEN** an authorized subject requests an export with a new idempotency key and polls the lookup
- **THEN** the POST returns `202 Accepted`, the lookup eventually returns `200 OK` with status `completed`, and the representation contains the complete payload and a non-empty SHA-256 hash

#### Scenario: Export returns the customer's data

- **WHEN** an authorized subject requests an export and reads its completed durable representation
- **THEN** the payload contains the customer's profile, addresses, deletion and purge timestamps when present, and audit entries

#### Scenario: Export replay is idempotent

- **WHEN** the same customer export is requested twice with the same idempotency key
- **THEN** the second request returns the existing export ID and status, no duplicate workflow is started, and subsequent lookup returns the same hash and payload

#### Scenario: Export is idempotent

- **WHEN** two POST requests use the same customer and `Idempotency-Key`
- **THEN** both requests resolve to the same export identity, content hash, and payload

#### Scenario: Export lookup is read-only

- **WHEN** a caller reads an export by customer and idempotency key
- **THEN** the service returns the existing durable state without starting or signaling a Temporal workflow

#### Scenario: Export is not authorized for another tenant

- **WHEN** the authenticated subject does not own the requested customer
- **THEN** the request and lookup return `403 Forbidden` without exposing export state

### Requirement: GDPR Article 17 purge

> **Status**: PARTIAL. Soft-delete exists; Temporal purge workflow may be partial.

The customer service SHALL expose `DELETE /api/v1/customers/{id}` that soft-deletes the customer immediately and enqueues a Temporal workflow `CustomerPurgeWorkflow`. The workflow SHALL wait for the retention window (default 30 days), then perform cryptographic erasure: the customer row is rewritten with all PII columns set to NULL, all addresses are deleted, the row's `purged_at` is set, and a `CustomerPurged` event is emitted. The workflow SHALL be cancellable via `DELETE /api/v1/customers/{id}/purge` which cancels the workflow and immediately purges.

#### Scenario: Soft delete enqueues the purge workflow
- **WHEN** `DELETE /api/v1/customers/{id}` is called
- **THEN** the customer transitions to `soft_deleted` and a `CustomerPurgeWorkflow` is started

#### Scenario: Retention timer triggers the purge
- **WHEN** the retention window elapses
- **THEN** the purge workflow performs cryptographic erasure and emits `CustomerPurged`

#### Scenario: Immediate purge skips the retention window
- **WHEN** `DELETE /api/v1/customers/{id}/purge` is called
- **THEN** the running purge workflow is cancelled and a new one runs immediately

### Requirement: Cryptographic erasure evidence

> **Status**: PARTIAL. Evidence record schema exists; SHA-256 hashing may be partial.

Every purge SHALL produce an evidence record containing the customer's original ID (so the audit trail links pre- and post-purge), the SHA-256 hash of the row's last-known PII contents (so external auditors can verify the erasure happened), the operator subject who triggered it (or `system` for retention-driven purges), and the purge timestamp. The evidence record SHALL be retained for the audit-retention window (default 7 years).

#### Scenario: Evidence record is created
- **WHEN** a customer is purged
- **THEN** an evidence row exists in the `gdpr_purge_evidence` table with the SHA-256 hash and the purge timestamp

### Requirement: Audit log

> **Status**: PARTIAL. Audit log table exists; state transition recording may be partial.

The customer service SHALL record every state transition (create, update, soft-delete, restore, purge, address add/update/remove) in a `customer_audit_log` table. The audit log entry SHALL include the actor (subject ID or `system`), the action, the before/after diff, the timestamp, and the correlation ID. The audit log SHALL be append-only and SHALL NOT be modifiable by the public API.

#### Scenario: Audit entry is recorded on create
- **WHEN** a customer is created
- **THEN** an entry exists in `customer_audit_log` with action `create`, the actor, and the correlation ID

#### Scenario: Audit log is not modifiable via the API
- **WHEN** the API receives a request to modify an audit entry
- **THEN** the service returns `405 Method Not Allowed`

### Requirement: GDPR export and purge Temporal patterns

The export request SHALL start `CustomerGDPRExportWorkflow` using workflow type and task queue `customer.gdpr.v1`, a deterministic identity derived from the customer and idempotency key, and retry-safe workflow-start policies. Export collection and persistence SHALL execute as activities, and the durable lookup SHALL NOT start workflow execution.

The purge workflow SHALL use Temporal's `ContinueAsNew` pattern when the retention timer approaches the workflow history limit. The purge workflow SHALL remain registered under `customer.purge.v1` with Worker Deployment name `customer-workflows-v1`. The cryptographic-erasure activity SHALL declare `StartToCloseTimeout=30s` and SHALL use `activity.RecordHeartbeat` for visibility. The immediate-purge activity SHALL be guarded by a separate role check so production deployments can disable it via configuration.

#### Scenario: Export request starts the dedicated workflow

- **WHEN** the API accepts a new customer export request
- **THEN** one `CustomerGDPRExportWorkflow` execution starts on `customer.gdpr.v1` and persists a completed export for durable lookup

#### Scenario: Export endpoint is synchronous

- **WHEN** a caller uses the durable GET lookup for an existing export
- **THEN** the lookup returns the current stored representation without starting or signaling a Temporal workflow

#### Scenario: Export replay reuses workflow and durable state

- **WHEN** a duplicate request uses the same customer and idempotency key
- **THEN** workflow-start policy and durable lookup return the existing execution state without a second externally visible export effect

#### Scenario: Retention timer uses ContinueAsNew

- **WHEN** the purge workflow history approaches the configured limit
- **THEN** the workflow calls `workflow.NewContinueAsNewError` and a new execution continues the retention timer

#### Scenario: Immediate purge is role-guarded

- **WHEN** immediate purge is disabled by configuration
- **THEN** the immediate-purge endpoint returns `403 Forbidden` and the retention workflow remains active

#### Scenario: Cryptographic erasure activity declares timeouts

- **WHEN** the cryptographic-erasure activity is invoked
- **THEN** its activity options carry `StartToCloseTimeout=30s` and `ScheduleToCloseTimeout=5m`

