# fuzz-testing Specification

## Purpose
The platform implements fuzz testing for HTTP handler input parsing across services to ensure robustness against malformed, unexpected, and adversarial input.

## Requirements

> **Status**: PARTIAL. Platform-level fuzz tests exist (HTTP, Kafka, Temporal
> validation). Inventory and shipping now have committed HTTP/event parser
> seeds, deterministic regression runners, bounded short-fuzz runners, and
> fail-closed local `verify-pr` integration. Remaining service breadth and
> hosted CI scheduling are deferred.

### Requirement: Fuzz test coverage

> **Status**: PARTIAL. Fuzz tests exist in platform/http/fuzz and platform/kafka/fuzz; service-level tests may be partial.

Each service SHALL have fuzz tests for its HTTP handler input parsing in `test/fuzz/http_test.go`. Fuzz tests SHALL verify that arbitrary input does not cause panics and that error responses are properly formatted.

#### Scenario: Fuzz test exists for customer-service
- **WHEN** the test suite is executed
- **THEN** `services/customer-service/test/fuzz/http_test.go` exists with `FuzzHTTPHandler` and `FuzzJSONValidation` functions

#### Scenario: Fuzz test exists for notification-service
- **WHEN** the test suite is executed
- **THEN** `services/notification-service/test/fuzz/http_test.go` exists with `FuzzHTTPHandler` and `FuzzJSONValidation` functions

#### Scenario: Fuzz test exists for catalog-service
- **WHEN** the test suite is executed
- **THEN** `services/catalog-service/test/fuzz/http_test.go` exists with `FuzzHTTPHandler` and `FuzzJSONValidation` functions

### Requirement: Seed corpus

> **Status**: PARTIAL. Seed corpus exists in platform fuzz tests; service-level corpus may be partial.

Each fuzz test SHALL include a seed corpus with valid JSON, empty objects, and invalid input to guide the fuzzer toward meaningful test cases.

#### Scenario: Customer-service seed corpus
- **WHEN** the customer-service fuzz test is executed
- **THEN** the seed corpus includes at minimum: valid customer JSON, empty JSON object, and invalid (non-JSON) input

#### Scenario: Notification-service seed corpus
- **WHEN** the notification-service fuzz test is executed
- **THEN** the seed corpus includes at minimum: valid notification JSON, empty JSON object, and invalid (non-JSON) input

#### Scenario: Catalog-service seed corpus
- **WHEN** the catalog-service fuzz test is executed
- **THEN** the seed corpus includes at minimum: valid product JSON, empty JSON object, and invalid (non-JSON) input

### Requirement: No panics on arbitrary input

> **Status**: IMPLEMENTED. Fuzz tests verify no panics on arbitrary input in platform packages.

Fuzz tests SHALL verify that arbitrary input never causes a panic in the JSON deserializer or input validator. The handler SHALL return a valid HTTP response (400, 422, or 201/202) for any input.

#### Scenario: Arbitrary bytes do not cause panic
- **WHEN** the fuzz test generates arbitrary bytes as input
- **THEN** the handler completes without panic and returns a valid HTTP status code

### Requirement: Error responses are properly formatted

> **Status**: IMPLEMENTED. Fuzz tests verify error responses are properly formatted with status codes.

Fuzz tests SHALL verify that error responses include a status code and are writable to the response writer. Invalid JSON SHALL return 400; missing required fields SHALL return 422.

#### Scenario: Invalid JSON returns 400
- **WHEN** the fuzz test provides non-JSON input
- **THEN** the handler returns 400 Bad Request

#### Scenario: Missing required fields returns 422
- **WHEN** the fuzz test provides valid JSON with empty required fields
- **THEN** the handler returns 422 Unprocessable Entity

### Requirement: Field length validation

> **Status**: IMPLEMENTED. Fuzz tests verify field length bounds are enforced.

Fuzz tests SHALL verify that parsed fields do not exceed maximum expected lengths. Fields exceeding bounds SHALL be rejected with 422 Unprocessable Entity.

#### Scenario: Name field length is bounded
- **WHEN** the fuzz test provides a name exceeding 1000 characters
- **THEN** the field length validation catches the violation

#### Scenario: Email field length is bounded
- **WHEN** the fuzz test provides an email exceeding 320 characters
- **THEN** the field length validation catches the violation

### Requirement: Local regression and bounded fuzz execution

> **Status**: PARTIAL. Inventory and shipping implement both modes and run
> deterministic regression corpora from `verify-pr`. The same convention is
> not yet complete for every service; hosted CI scheduling is out of scope for
> the local verification change.

Required service fuzz suites SHALL provide a deterministic regression command
that runs committed seeds and a separate bounded `go test -fuzz` command for
local development. A service that declares a required fuzz suite SHALL fail
`verify-pr` when its runner, target, or committed seeds are absent.

#### Scenario: Committed regression corpus runs locally
- **WHEN** inventory or shipping runs `make verify-pr`
- **THEN** its HTTP and event parser regression seeds execute deterministically and any panic or invalid acceptance fails the gate

#### Scenario: Bounded random fuzzing runs locally
- **WHEN** a developer runs the service's short-fuzz target
- **THEN** each declared fuzz target runs with a finite fuzz time and reports any panic found
