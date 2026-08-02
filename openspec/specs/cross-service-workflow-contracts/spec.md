# cross-service-workflow-contracts Specification

## Purpose
This spec defines the cross-service wire-format policy for the
`extract-business-domains-and-dedicated-workflow-orchestration` change.
Each of the three extracted services (`payment-service`, `inventory-service`,
`shipping-service`) publishes a hand-maintained Go contract package under
`services/<name>/contracts/<domain>/v1/` that mirrors the eventual
`buf generate` output. The order-service holds a parallel mirror under
`services/order-service/contracts/<domain>/v1/` so the order-worker can
type-check its outbound HTTP calls without importing the peer service's
Go module (cross-service Go imports are forbidden by
`platform-extensibility`). When the operator runs `buf generate`, the
hand-maintained mirrors SHALL be replaced by the generated files, and the
order-service SHALL switch to the generated mirrors via a `replace`
directive in `go.mod`.

## Requirements
### Requirement: Each extracted service publishes its own contracts/ package

> **Status**: IMPLEMENTED. All three services have contracts directories with hand-maintained Go types.

Each of the three new services (`payment-service`, `inventory-service`, `shipping-service`) SHALL publish a `contracts/<domain>/v1/` directory containing the **hand-maintained Go types** (`<domain>.pb.go`) that mirror the `.proto` source files. The `.proto` sources SHALL live in `proto/<domain>/v1/` (e.g., `services/payment-service/proto/payment/v1/payment.proto`), matching the existing order-service convention (`services/order-service/proto/order/v1/`). Each `contracts/<domain>/v1/` directory SHALL also contain a `REGENERATE.md` describing the `buf generate` command that will replace the hand-maintained stub with the generated binding.

The order-service SHALL hold a parallel `contracts/<domain>/v1/` mirror under `services/order-service/contracts/<domain>/v1/` so the order-worker can compile its outbound HTTP client without crossing service boundaries. The hand-maintained order-service mirrors SHALL be type-compatible with the corresponding new-service stubs (same struct names, same field types, same JSON field names).

#### Scenario: payment-service publishes its contract package

- **WHEN** a developer runs `cd services/payment-service/contracts/payment/v1 && cat payment.go`
- **THEN** the file defines `PaymentCaptureRequest`, `PaymentCaptureResponse`, `PaymentRefundRequest`, `PaymentRefundResponse` with `ContractVersion` as the first field
- **AND** a `REGENERATE.md` documents the `buf generate` command and the expected output

#### Scenario: order-service mirrors the payment contract

- **WHEN** the order-service builds
- **THEN** `services/order-service/contracts/payment/v1/payment.go` exists with the same type names as `services/payment-service/contracts/payment/v1/payment.go`
- **AND** the order-service's `internal/application/clients/payment_client.go` imports `github.com/victory1908/services/order-service/contracts/payment/v1`

### Requirement: Contracts are versioned and contract_version is in every message

> **Status**: IMPLEMENTED. ContractVersion field exists as first field in all contract types.

Each request/response message SHALL include a `contract_version` field of type `int32` with a tag of `1` (the first field, before any business fields). The `contract_version` for the initial release SHALL be `1`. A contract change that is backward-compatible (e.g., adding a new field) SHALL bump the minor version (`1` → `2`); a contract change that is not backward-compatible (e.g., removing a field, changing a field type) SHALL bump the major version (`1` → `2` for breaking changes tracked separately, with a `contract_major_version` field added at the protocol level).

The HTTP endpoints SHALL validate the `contract_version` header on every request and SHALL return `409 Conflict` with body `{ "error": "contract_version_mismatch", "expected": 1, "received": 2 }` if the version is greater than the service's registered version.

#### Scenario: Payment capture rejects an unknown contract version

- **WHEN** `POST /api/v1/payments/{intent_id}/capture` is called with header `X-Contract-Version: 99`
- **THEN** the endpoint returns `409 Conflict` with body `{ "error": "contract_version_mismatch", "expected": 1, "received": 99 }`
- **AND** the endpoint does NOT perform the capture

#### Scenario: Contract version is in the first field of the protobuf message

- **WHEN** `buf generate` runs against `services/payment-service/proto/payment/v1/payment.proto`
- **THEN** the generated `PaymentCaptureRequest` struct has `ContractVersion int32` as the first field
- **AND** the protobuf tag is `protobuf:"varint,1,opt,name=contract_version,proto3"`

### Requirement: The platform-contracts spec defines the cross-service message types

> **Status**: PARTIAL. Platform-contracts spec exists; architecture test enforcement may be partial.

The `platform-contracts` spec (which already exists in `openspec/specs/platform-contracts/`) SHALL be extended (via a delta in this change) to require that every cross-service HTTP call uses a generated Go type from a `contracts/<domain>/v1/` package, and that every message includes the `contract_version` field. The architecture test in `platform/architecture/` SHALL verify that no `application/clients/` file in any service uses an inline struct for a cross-service DTO; all DTOs SHALL be imported from a `contracts/` package.

#### Scenario: order-service does not define inline cross-service DTOs

- **WHEN** the architecture test scans `services/order-service/internal/application/clients/`
- **THEN** the test fails if any file in that directory defines a `type CaptureRequest struct` or similar inline DTO that mirrors a `contracts/payment/v1/PaymentCaptureRequest` type
- **AND** the test passes if all DTOs are imported from `contracts/payment/v1`, `contracts/inventory/v1`, `contracts/shipping/v1`

### Requirement: buf.yaml is the canonical protobuf management tool

> **Status**: IMPLEMENTED. buf.yaml exists at repo root; buf generate, buf lint configured.

The repo-root `buf.yaml` file SHALL include all `services/<service>/proto/**/*.proto` files via the `build` configuration. The `buf generate` command SHALL be runnable from the repo root to regenerate all Go code. The generated `.pb.go` files SHALL be committed to the repo so that `go build` works without a codegen step. The CI pipeline SHALL run `buf lint` and `buf breaking --against '.git#branch=main'` to enforce contract stability.

#### Scenario: buf lint passes on all contracts

- **WHEN** `cd /Users/androidteam/Library/CloudStorage/GoogleDrive-victory1908@gmail.com/My Drive/project/microservices && buf lint` runs
- **THEN** the command exits 0 with no lint errors
- **AND** all new `services/<name>/proto/**/*.proto` files pass the lint check

#### Scenario: buf breaking detects a non-backward-compatible change

- **WHEN** a developer removes a field from `services/payment-service/proto/payment/v1/payment.proto` and runs `buf breaking --against '.git#branch=main'`
- **THEN** the command exits non-zero and reports `Field "3" on message "PaymentCaptureRequest" deleted`
- **AND** the CI pipeline blocks the merge

### Requirement: HTTP wire format is JSON

> **Status**: IMPLEMENTED. All cross-service HTTP endpoints use JSON; protojson.Marshal used for serialization.

The cross-service HTTP endpoints SHALL accept and return `application/json`. The protobuf-generated Go types SHALL be marshalled to JSON via `protojson.Marshal` (not `encoding/json`'s default `Marshal`); this preserves protobuf field semantics (e.g., `oneof`, `int64` as string). The `Content-Type: application/json` header SHALL be set on every request; the response SHALL also be `application/json`.

#### Scenario: Payment capture endpoint returns JSON

- **WHEN** `POST /api/v1/payments/{intent_id}/capture` is called with `Content-Type: application/json`
- **THEN** the response has `Content-Type: application/json` and body `{"payment_capture_id":"...","status":"captured","captured_at":"2026-07-15T10:00:00Z","contract_version":1}`

#### Scenario: Order client marshals to JSON via protojson

- **WHEN** `payment.Client.Capture` builds the HTTP request
- **THEN** the request body is produced by `protojson.Marshal(&CaptureRequest{...})`
- **AND** the body is a JSON object with `contract_version` as the first field

### Requirement: HTTP timeout is per-peer and configurable

> **Status**: IMPLEMENTED. Per-peer timeout configuration exists in clients package with configurable defaults.

The per-peer HTTP timeout SHALL be read from `cfg.Peers.<Name>Timeout` (e.g., `cfg.Peers.PaymentTimeout`, default `5s`). The HTTP client SHALL apply the timeout to the underlying `http.Client` so a slow peer cannot stall the activity past the activity's `StartToCloseTimeout`. The platform's `clients.PeerConfig.Validate()` method SHALL return an error if the timeout is zero.

#### Scenario: Payment client enforces the per-peer timeout

- **WHEN** `payment.Client.Capture` is called with `cfg.Peers.PaymentTimeout = 2*time.Second` and the payment-service takes 5 seconds to respond
- **THEN** the HTTP client cancels the request after 2 seconds
- **AND** the client returns `clients.ErrPeerUnavailable` with cause `context deadline exceeded`
- **AND** the activity returns `NonRetryableApplicationError("peer_unavailable", ...)`

