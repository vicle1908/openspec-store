## ADDED Requirements

### Requirement: GDPR Article 15 data export
The customer service SHALL expose `GET /api/v1/customers/{id}/export` that returns the customer's data in JSON form, including the customer profile, all addresses, the soft-delete timestamp (if any), the purge timestamp (if any), and any audit log entries. The endpoint SHALL require an `Idempotency-Key` header to dedupe retries; the response SHALL be a stable hash of the export's content so callers can detect re-execution.

#### Scenario: Export returns the customer's data
- **WHEN** an authenticated subject with access to customer `<id>` calls the export endpoint
- **THEN** the response is `200 OK` with the JSON payload containing the customer's profile, addresses, and audit entries

#### Scenario: Export is idempotent
- **WHEN** two export requests carry the same `Idempotency-Key`
- **THEN** the second response returns the same content hash as the first

#### Scenario: Export is not authorized for another tenant
- **WHEN** the calling subject does not own the customer
- **THEN** the response is `403 Forbidden`

### Requirement: GDPR Article 17 purge
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
Every purge SHALL produce an evidence record containing the customer's original ID (so the audit trail links pre- and post-purge), the SHA-256 hash of the row's last-known PII contents (so external auditors can verify the erasure happened), the operator subject who triggered it (or `system` for retention-driven purges), and the purge timestamp. The evidence record SHALL be retained for the audit-retention window (default 7 years).

#### Scenario: Evidence record is created
- **WHEN** a customer is purged
- **THEN** an evidence row exists in the `gdpr_purge_evidence` table with the SHA-256 hash and the purge timestamp

### Requirement: Audit log
The customer service SHALL record every state transition (create, update, soft-delete, restore, purge, address add/update/remove) in a `customer_audit_log` table. The audit log entry SHALL include the actor (subject ID or `system`), the action, the before/after diff, the timestamp, and the correlation ID. The audit log SHALL be append-only and SHALL NOT be modifiable by the public API.

#### Scenario: Audit entry is recorded on create
- **WHEN** a customer is created
- **THEN** an entry exists in `customer_audit_log` with action `create`, the actor, and the correlation ID

#### Scenario: Audit log is not modifiable via the API
- **WHEN** the API receives a request to modify an audit entry
- **THEN** the service returns `405 Method Not Allowed`

### Requirement: GDPR export and purge Temporal patterns
The export endpoint SHALL NOT use a Temporal workflow (it is a synchronous read). The purge workflow SHALL use Temporal's `ContinueAsNew` pattern when the retention timer exceeds the workflow history limit (default 50K events). The purge workflow SHALL be registered under `customer.purge.v1` with Worker Versioning v2 `DeploymentSeriesName=customer-purge.v1`. The cryptographic-erasure activity SHALL declare `StartToCloseTimeout=30s` and SHALL use `activity.RecordHeartbeat` for visibility. The immediate-purge activity SHALL be guarded by a separate role check (`PURGE_NOW`) so production deployments can disable it via configuration.

#### Scenario: Export endpoint is synchronous
- **WHEN** the API receives `GET /api/v1/customers/{id}/export`
- **THEN** the response is returned within 2 seconds; no Temporal workflow is started

#### Scenario: Retention timer uses ContinueAsNew
- **WHEN** the retention-timer activity's history approaches 50K events
- **THEN** the workflow calls `workflow.NewContinueAsNewError(ctx, CustomerPurgeWorkflow, ...)` and a new workflow execution takes over

#### Scenario: Immediate purge is role-guarded
- **WHEN** the service configuration sets `CUSTOMER_PURGE_NOW_ENABLED=false`
- **THEN** `DELETE /api/v1/customers/{id}/purge` returns `403 Forbidden` and the running purge workflow is left to its retention timer

#### Scenario: Cryptographic erasure activity declares timeouts
- **WHEN** the cryptographic-erasure activity is invoked
- **THEN** its `ActivityOptions` carry `StartToCloseTimeout=30s` and `ScheduleToCloseTimeout=5m`