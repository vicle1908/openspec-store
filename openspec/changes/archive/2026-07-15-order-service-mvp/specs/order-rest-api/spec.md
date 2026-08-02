## ADDED Requirements

### Requirement: HTTP API is versioned
Order endpoints SHALL be exposed under `/api/v1/orders` with stable JSON representations and machine-readable error codes.

#### Scenario: Domain validation failure
- **WHEN** a create request violates an Order invariant
- **THEN** the API returns HTTP 422 with a stable error code, request ID, and field details where applicable

### Requirement: Order commands and queries are mapped one-to-one to HTTP endpoints
The Order Service SHALL expose exactly four MVP endpoints under `/api/v1/orders`: `POST /api/v1/orders` to create, `GET /api/v1/orders/{id}` to fetch by ULID, `GET /api/v1/orders` to list with opaque cursor pagination, and `POST /api/v1/orders/{id}/cancel` to cancel. `PATCH`, `PUT`, and `DELETE` collection operations are out of scope for MVP; gRPC is deferred.

#### Scenario: Cancel an existing order
- **WHEN** a client posts a cancel request with a valid `Idempotency-Key` for an existing order that is not yet shipped
- **THEN** the API returns the cancelled Order view and the cancellation is recorded atomically with an outbox event

### Requirement: Error responses are translated through a stable adapter
Application-layer errors (`ValidationError`, `DomainError`, `NotFoundError`, `IdempotencyKeyError`, `FingerprintMismatchError`, `ConcurrencyConflictError`, invalid-cursor) SHALL be translated to a small set of stable HTTP error types in the HTTP adapter so transport code does not import application internals.

#### Scenario: Concurrency conflict maps to a stable HTTP 409
- **WHEN** the application returns `ConcurrencyConflictError{OrderID: "01J…"}` for an order whose version changed during processing
- **THEN** the HTTP adapter responds with HTTP 409 and a body of `{"code": "concurrency_conflict", "message": "optimistic concurrency conflict on order 01J…"}` so the retry contract is unchanged regardless of which service rejected the version.

### Requirement: Mutating requests are idempotent
Every mutating endpoint SHALL require an `Idempotency-Key` header and SHALL return the original response for an equivalent replay.

#### Scenario: Replayed create request
- **WHEN** a client retries a timed-out create request with the same key and body
- **THEN** it receives the original Order ID and status without creating another Order

### Requirement: List queries use cursor pagination
Order list endpoints SHALL use opaque cursor pagination with a deterministic sort and a bounded page size.

#### Scenario: Next page
- **WHEN** a client submits the returned next cursor
- **THEN** the API returns the following stable page without exposing database offsets

### Requirement: API boundary inputs are fuzz-tested
The HTTP adapter SHALL reject untrusted input (request bodies, opaque cursor strings, ULID identifiers) with stable, machine-readable errors. The decoder path for every public endpoint SHALL be exercised by a fuzz target whose regression corpus is checked in and re-run on every pull request so that a malformed payload cannot bypass validation or yield a non-round-trippable cursor.

#### Scenario: Non-canonical cursor is rejected
- **WHEN** a client submits a base64 cursor whose trailing bits decode to the same payload as a canonical cursor
- **THEN** the cursor decoder returns `invalid cursor` rather than accepting the lossy form, ensuring the server can always re-encode the cursor it accepted back to its original form

### Requirement: API propagates correlation context
The API SHALL establish request and correlation identifiers and SHALL propagate them to logs, outbox metadata, and workflow start options.

#### Scenario: Client omits correlation ID
- **WHEN** a request does not provide a valid correlation ID
- **THEN** the service generates one and returns it in the response
