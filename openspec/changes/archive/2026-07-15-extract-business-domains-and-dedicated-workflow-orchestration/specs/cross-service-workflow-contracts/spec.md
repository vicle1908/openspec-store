# cross-service-workflow-contracts Specification

## Purpose
A shared `contracts/` package SHALL define the wire DTOs (request/response Go structs and the protobuf message types) for all cross-service HTTP calls between the order-service and the three extracted services (payment, inventory, shipping). Both the producer (extracted service) and the consumer (order-worker activity) SHALL import the same generated code so a contract change is a single PR. The contracts are managed by `buf` with the project's existing `buf.yaml` at the repo root; the generated Go code is committed to the repo to avoid build-time codegen requirements.

## ADDED Requirements

### Requirement: Each extracted service publishes its own contracts/ package

Each of the three new services (`payment-service`, `inventory-service`, `shipping-service`) SHALL publish a `contracts/<domain>/v1/` directory containing the **generated Go code** (e.g., `contracts/payment/v1/payment.pb.go`) produced by `buf generate` from the `.proto` source files. The `.proto` sources SHALL live in `proto/<domain>/v1/` (e.g., `proto/payment/v1/payment.proto`), matching the existing order-service convention (`services/order-service/proto/order/v1/commands.proto` and `services/order-service/proto/order/v1/order.proto` generate into `services/order-service/contracts/order/v1/`). Each `contracts/<domain>/v1/` directory SHALL also contain a `README.md` documenting the wire format, the protobuf package name, and the contract version.

The order-service's `go.mod` SHALL use a `replace` directive pointing to the local `services/<name>/contracts/` paths to import the generated Go code. The contract packages SHALL have no transitive dependencies beyond the standard library and `google.golang.org/protobuf`.

#### Scenario: payment-service publishes its contract package

- **WHEN** a developer runs `cd services/payment-service/proto/payment/v1 && cat payment.proto` and `cd services/payment-service/contracts/payment/v1 && cat README.md`
- **THEN** the proto defines `PaymentCaptureRequest`, `PaymentCaptureResponse`, `PaymentRefundRequest`, `PaymentRefundResponse` with `contract_version` as the first field
- **AND** the README documents the protobuf package name `github.com/victory1908/payment-service/contracts/payment/v1`
- **AND** the `payment.pb.go` file is committed to the repo

#### Scenario: order-service imports the payment contract

- **WHEN** the order-service builds with the `replace` directive `replace github.com/victory1908/payment-service/contracts => ../payment-service/contracts`
- **THEN** the order-service can `import "github.com/victory1908/payment-service/contracts/payment/v1"` and use the generated types
- **AND** the build succeeds without a `go generate` step

### Requirement: Contracts are versioned and contract_version is in every message

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

The `platform-contracts` spec (which already exists in `openspec/specs/platform-contracts/`) SHALL be extended (via a delta in this change) to require that every cross-service HTTP call uses a generated Go type from a `contracts/<domain>/v1/` package, and that every message includes the `contract_version` field. The architecture test in `platform/architecture/` SHALL verify that no `application/clients/` file in any service uses an inline struct for a cross-service DTO; all DTOs SHALL be imported from a `contracts/` package.

#### Scenario: order-service does not define inline cross-service DTOs

- **WHEN** the architecture test scans `services/order-service/internal/application/clients/`
- **THEN** the test fails if any file in that directory defines a `type CaptureRequest struct` or similar inline DTO that mirrors a `contracts/payment/v1/PaymentCaptureRequest` type
- **AND** the test passes if all DTOs are imported from `contracts/payment/v1`, `contracts/inventory/v1`, `contracts/shipping/v1`

### Requirement: buf.yaml is the canonical protobuf management tool

The repo-root `buf.yaml` file SHALL include all `services/<service>/proto/**/*.proto` files via the `build` configuration. The `buf generate` command SHALL be runnable from the repo root to regenerate all Go code. The generated `.pb.go` files SHALL be committed to the repo so that `go build` works without a codegen step. The CI pipeline SHALL run `buf lint` and `buf breaking --against '.git#branch=main'` to enforce contract stability.

#### Scenario: buf lint passes on all contracts

- **WHEN** `cd /Users/androidteam/Library/CloudStorage/GoogleDrive-victory1908@gmail.com/My Drive/project/go-microservices && buf lint` runs
- **THEN** the command exits 0 with no lint errors
- **AND** all new `services/<name>/proto/**/*.proto` files pass the lint check

#### Scenario: buf breaking detects a non-backward-compatible change

- **WHEN** a developer removes a field from `services/payment-service/proto/payment/v1/payment.proto` and runs `buf breaking --against '.git#branch=main'`
- **THEN** the command exits non-zero and reports `Field "3" on message "PaymentCaptureRequest" deleted`
- **AND** the CI pipeline blocks the merge

### Requirement: HTTP wire format is JSON

The cross-service HTTP endpoints SHALL accept and return `application/json`. The protobuf-generated Go types SHALL be marshalled to JSON via `protojson.Marshal` (not `encoding/json`'s default `Marshal`); this preserves protobuf field semantics (e.g., `oneof`, `int64` as string). The `Content-Type: application/json` header SHALL be set on every request; the response SHALL also be `application/json`.

#### Scenario: Payment capture endpoint returns JSON

- **WHEN** `POST /api/v1/payments/{intent_id}/capture` is called with `Content-Type: application/json`
- **THEN** the response has `Content-Type: application/json` and body `{"payment_capture_id":"...","status":"captured","captured_at":"2026-07-15T10:00:00Z","contract_version":1}`

#### Scenario: Order client marshals to JSON via protojson

- **WHEN** `payment.Client.Capture` builds the HTTP request
- **THEN** the request body is produced by `protojson.Marshal(&CaptureRequest{...})`
- **AND** the body is a JSON object with `contract_version` as the first field

### Requirement: HTTP timeout is per-peer and configurable

The per-peer HTTP timeout SHALL be read from `cfg.Peers.<Name>Timeout` (e.g., `cfg.Peers.PaymentTimeout`, default `5s`). The HTTP client SHALL apply the timeout to the underlying `http.Client` so a slow peer cannot stall the activity past the activity's `StartToCloseTimeout`. The platform's `clients.PeerConfig.Validate()` method SHALL return an error if the timeout is zero.

#### Scenario: Payment client enforces the per-peer timeout

- **WHEN** `payment.Client.Capture` is called with `cfg.Peers.PaymentTimeout = 2*time.Second` and the payment-service takes 5 seconds to respond
- **THEN** the HTTP client cancels the request after 2 seconds
- **AND** the client returns `clients.ErrPeerUnavailable` with cause `context deadline exceeded`
- **AND** the activity returns `NonRetryableApplicationError("peer_unavailable", ...)`
