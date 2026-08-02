## ADDED Requirements

### Requirement: Canonical event envelope
The platform SHALL define a Protobuf message `platform.events.v1.EventEnvelope` that every domain event uses as its wire format. The envelope SHALL carry the fields `event_id` (ULID), `event_type` (string), `event_version` (uint32), `aggregate_type` (string), `aggregate_id` (ULID), `aggregate_version` (uint64), `occurred_at` (google.protobuf.Timestamp), `producer` (string), `correlation_id` (string), `causation_id` (string), and `payload` (bytes — the marshalled typed event). The envelope is generated from `proto/platform/events/v1/event_envelope.proto` and SHALL NOT be hand-written.

#### Scenario: Envelope is generated from proto, not hand-written
- **WHEN** the contracts package is regenerated
- **THEN** the generated Go code matches the Buf-managed `platform/events/v1/event_envelope.proto` schema

#### Scenario: Envelope round-trips through marshal and unmarshal
- **WHEN** an envelope is marshalled to bytes and then unmarshalled
- **THEN** every field is preserved exactly, including `payload`

### Requirement: Generated Go types shared across services
The platform SHALL expose a Go package `github.com/victory1908/platform/contracts/platform/events/v1` that every service imports to construct and decode envelopes. The package SHALL expose typed constructors `NewEnvelope(eventID, eventType, ...)` and a decoder `DecodeEnvelope(bytes) (EventEnvelope, error)` that validates the required fields are non-empty and the payload bytes are non-empty.

#### Scenario: NewEnvelope requires all mandatory fields
- **WHEN** a caller constructs an envelope with an empty `event_id` or `event_type`
- **THEN** the constructor returns a validation error

#### Scenario: DecodeEnvelope rejects malformed bytes
- **WHEN** the decoder receives bytes that are not a valid `EventEnvelope`
- **THEN** it returns a typed error `ErrInvalidEnvelope` carrying the parse failure

#### Scenario: DecodeEnvelope rejects envelopes with missing required identifiers
- **WHEN** the decoder receives a valid `EventEnvelope` whose `event_id` or `aggregate_id` is empty
- **THEN** it returns a typed error `ErrInvalidEnvelope` listing the missing fields

### Requirement: Buf lint and breaking policy template
The platform SHALL publish a `buf.yaml` and `buf.gen.yaml` template that every service copies into its `proto/` directory. The template SHALL enable the Buf lint rules `DEFAULT`, `COMMENTS`, `FILE_LOWER_SNAKE_CASE`, `PACKAGE_DIRECTORY_MATCH`, `PACKAGE_VERSION_SUFFIX`, `RPC_REQUEST_STANDARD_NAME`, `RPC_RESPONSE_STANDARD_NAME`, `RPC_REQUEST_RESPONSE_UNIQUE`, `SERVICE_SUFFIX`, and `ENUM_VALUE_PREFIX`. The template SHALL enable the Buf breaking rules `FILE`, `PACKAGE`, `WIRE`, `WIRE_JSON`, and `EXTENSION_JSON`.

#### Scenario: Buf lint passes on every service's proto
- **WHEN** `make buf-lint` runs in any service module
- **THEN** the command exits 0 and reports zero lint findings

#### Scenario: Buf breaking detects a removed field
- **WHEN** a service removes a field from a `proto` file and runs `buf breaking --against proto-baseline/v0.X.0`
- **THEN** the command exits non-zero and reports the removed field

### Requirement: Compatibility policy enforcement
The platform SHALL enforce, via `make buf-breaking` in every service's CI, that the `proto/` directory has not introduced a breaking change against the pinned baseline. The first baseline is generated when the first service is archived; each subsequent service pins its baseline to the previous release. Field numbers SHALL NEVER be reused; removed fields SHALL be reserved in the proto file to prevent accidental reuse.

#### Scenario: Reserved field numbers block accidental reuse
- **WHEN** a proto file declares `reserved 5, 6, 7;` and a new field is added with tag number `6`
- **THEN** `buf breaking` reports the reuse as a violation

#### Scenario: First-release baseline is generated at archive time
- **WHEN** a service's first release is archived
- **THEN** the proto files are snapshotted to `proto-baseline/<version>/` for use by future breaking-change checks

### Requirement: Contract versioning convention
Every typed event SHALL be defined as `<domain>.events.v1.<EventName>` with a package suffix `.v1`, `.v2`, etc. for breaking changes. The contract version SHALL be carried in the envelope's `event_version` field. Breaking changes SHALL introduce a new event type and a new package version; the old event type SHALL continue to be published alongside for the migration window defined by the platform's compatibility policy.

#### Scenario: New event version lives in a new package
- **WHEN** an event needs a breaking change
- **THEN** the new event is defined in `proto/<domain>/events/v2/<event>.proto` and the v1 event continues to be published

### Requirement: Buf workspace v2 with root `buf.yaml`
When the platform grows beyond a single service (which is the Phase 2 state), the platform SHALL migrate to a Buf v2 workspace: a root `buf.yaml` at the repository root that declares one entry per service's `proto/` directory AND a shared `platform/proto/` directory for cross-service contracts. Internal-workspace dependencies (one service module depending on `platform/events/v1`) are resolved automatically — they MUST NOT be re-listed in the `deps:` block. The workspace forbids the legacy `buf.work.yaml` (v1); the root `buf.yaml` is the workspace file.

#### Scenario: Workspace lists every service's proto directory plus the shared platform proto
- **WHEN** `buf build` runs at the repository root
- **THEN** the build succeeds, traversing every service's `proto/` and the shared `platform/proto/`

#### Scenario: A service module that imports platform/events/v1 resolves without listing it in deps
- **WHEN** a service's `proto/order/v1/order.proto` imports `buf.build/victory1908/platform/events/v1`
- **THEN** the import resolves via the workspace (no `deps:` entry needed); `buf breaking --against .git#branch=main` succeeds

### Requirement: `buf.lock` committed for reproducibility
When BSR-pinned dependencies are introduced (e.g., `buf.build/bufbuild/protovalidate`), the platform SHALL commit `buf.lock` to the repo. The lock file records the commit hash and digest of every BSR dependency. CI SHALL fail the build if `buf.lock` is missing when any `deps:` entry exists. Locally, developers run `buf dep update` to refresh the lock.

#### Scenario: Buf dep update writes a lock file
- **WHEN** a developer adds `protovalidate` to `deps:` in `buf.yaml` and runs `buf dep update`
- **THEN** `buf.lock` is created with the pinned commit hash and digest

#### Scenario: CI rejects modifications to deps without a regenerated lock
- **WHEN** a PR modifies `deps:` in `buf.yaml` without regenerating `buf.lock`
- **THEN** the CI check `make buf-lint` fails with a clear error

### Requirement: protovalidate annotations on all input messages
The platform SHALL annotate every input message that crosses a service boundary (HTTP request bodies, Kafka producer payloads, Temporal activity inputs) with `buf/validate/validate.proto` annotations (`(buf.validate.field).required = true` for mandatory fields; `string.min_len`, `string.max_len`, `string.pattern` for constrained fields; `int64.gte`/`int64.lte` for bounded numerics; `google.protobuf.Timestamp` with `(buf.validate.field).within` for time-bounded windows). The annotation style replaces the deprecated `protoc-gen-validate` (`validate/validate.proto`); no new service may import the deprecated `validate/validate.proto`. Input messages SHALL be validated at the boundary via `(buf.validate.Validator)` reflection; the platform exposes a helper `ValidateProto(msg proto.Message) error` returning typed errors.

#### Scenario: protovalidate rejects a missing required field
- **WHEN** a request body arrives with a missing `customer_id`
- **THEN** the platform's `ValidateProto` returns a typed error `ErrValidationFailed` carrying field-level detail

#### Scenario: protovalidate rejects a malformed email
- **WHEN** a request body carries a `customer.email` whose value does not match the platform's email pattern
- **THEN** the platform returns `400 Bad Request` with a JSON error payload identifying the field path

### Requirement: Explicit `optional` on nullable scalars
The platform SHALL use `optional` on every proto3 scalar field that may be `null` (`optional string display_name = 1;`) instead of the older `google.protobuf.StringValue` wrapper (`google.protobuf.StringValue display_name = 1;`). This aligns with the proto3 → Editions migration: Editions default to explicit field presence, and `optional` is the forward-compat idiom. Message-typed fields already have explicit presence and SHALL NOT be marked `optional`. `repeated` and `map` fields SHALL NOT be marked `optional`.

#### Scenario: Optional scalar generates `*T` in Go and is distinguishable from unset
- **WHEN** `optional string external_ref = 10` is generated
- **THEN** the Go field is `ExternalRef *string`, distinguishable from `""` (zero value)

#### Scenario: Wrappers are rejected at lint time
- **WHEN** a service authors `google.protobuf.StringValue display_name = 1;` instead of `optional string display_name = 1;`
- **THEN** the platform's `buf.yaml` enables the `BASIC` rule `ENUM_NO_ALLOW_ALIAS` and `FIELD_NOT_REQUIRED`, and the deprecated form is flagged in code review (no automatic lint rule exists; the rejection lives in ADR-0006)

### Requirement: `buf.gen.yaml` uses the `remote:` plugin pattern
The platform SHALL configure `buf.gen.yaml` with `remote:` plugins, not `local:` plugins, so CI does not need to install `protoc` and per-language toolchains. The platform pins plugin versions by image tag (`buf.build/protocolbuffers/go:v1.36.10`, `buf.build/grpc/go:v1.5.3` if gRPC is adopted). The `managed:` mode MAY be enabled per service if the service prefers centralized `go_package` control; when `managed: true` is enabled, every per-file option (`go_package_prefix`, etc.) MUST be explicitly `disable:`-d for shared modules (`platform/proto/**`) so platform-generated paths are preserved.

#### Scenario: CI runs buf generate without protoc
- **WHEN** CI runs `make buf-generate`
- **THEN** the command uses the remote plugins via the Buf CLI and exits 0 without requiring local protoc binaries

#### Scenario: Pinning versions means reproducible builds
- **WHEN** two services run `buf generate` from different developer machines
- **THEN** both produce byte-identical generated Go code, because the plugin image is pinned in `buf.gen.yaml`

### Requirement: Buf BSR publication policy (deferred)
The platform SHALL NOT publish modules to the Buf BSR until (a) at least two services consume `platform/proto/**` from outside the workspace, AND (b) the platform has selected a commercial BSR tier (Teams or Pro) or self-hosted BSR. Until then, the platform uses `proto-baseline/<version>/` for breaking-change detection — the v0.1.0 baseline is already in `proto-baseline/v0.1.0/`. The community BSR tier is not adopted in Phase 2 because the platform's contract surface is internal.

#### Scenario: BSR publication is blocked by the absence of an ADR
- **WHEN** a developer adds `name: buf.build/<org>/<repo>` to a module's `buf.yaml`
- **THEN** the platform's CI rejects the change because no ADR has been authored; the developer is routed to open an ADR proposing BSR publication

### Requirement: Typed event registry for cross-service event consumers
The platform SHALL expose a typed event registry `platform/contracts/registry` that maps `event_type` strings to Go types. Every service populates the registry at startup with the typed events it generates AND the typed events it consumes (so the registry is bidirectional). Consumers use `registry.Decode(eventType string, payload []byte) (any, error)` to decode events with the correct type. The registry is the single source of truth for which event types are emitted / consumed across the platform; the platform's architecture test rejects a service that registers events under a non-canonical name (must match the proto file's fully qualified message name, e.g., `order.v1.OrderCreatedEvent`).

#### Scenario: Registry decodes payload using the registered typed event
- **WHEN** the consumer reads an `EventEnvelope` whose `event_type = "order.v1.OrderCreatedEvent"`
- **THEN** the registry decodes the `payload` into the registered `OrderCreatedEvent` Go type, returning a typed error if no type is registered for the event name

#### Scenario: Architecture test rejects unregistered event types
- **WHEN** the platform's architecture test runs and a service emits an event whose type is not in the registry
- **THEN** the test fails with a list of unregistered event names