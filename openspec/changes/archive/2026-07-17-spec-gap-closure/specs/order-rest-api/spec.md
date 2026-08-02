# order-rest-api Delta Specification

## Purpose

This delta updates the main `order-rest-api` spec to reflect the actual implementation status discovered during the spec-gap-closure audit. One requirement has modified status annotation.

## MODIFIED Requirements

### Requirement: API boundary inputs are fuzz-tested [DEFERRED]

> **Status**: DEFERRED. Fuzz targets exist in `services/order-service/test/fuzz/` for HTTP requests, IDs, and protobuf, and cursor/validation fuzz tests exist (`internal/adapters/http/cursor_fuzz_test.go`, `internal/adapters/temporal/validation_fuzz_test.go`, `FuzzDecodeCreateOrderRequest`). However, the spec requires that the decoder path for every public endpoint be exercised by a fuzz target whose regression corpus is checked in and re-run on every pull request. The current fuzz targets do not cover all four public endpoints (`POST /api/v1/orders`, `GET /api/v1/orders/{id}`, `GET /api/v1/orders`, `POST /api/v1/orders/{id}/cancel`), the regression corpus is not consistently checked in, and the fuzz tests are not wired into the PR CI gate (`make verify-pr`).

The HTTP adapter SHALL reject untrusted input (request bodies, opaque cursor strings, ULID identifiers) with stable, machine-readable errors. The decoder path for every public endpoint SHALL be exercised by a fuzz target whose regression corpus is checked in and re-run on every pull request so that a malformed payload cannot bypass validation or yield a non-round-trippable cursor.

#### Scenario: Non-canonical cursor is rejected

- **WHEN** a client submits a base64 cursor whose trailing bits decode to the same payload as a canonical cursor
- **THEN** the cursor decoder returns `invalid cursor` rather than accepting the lossy form, ensuring the server can always re-encode the cursor it accepted back to its original form

#### Scenario: Fuzz targets cover all public endpoints

- **WHEN** `make verify-pr` runs for the order service
- **THEN** a fuzz target exists for each of the four public endpoints (`POST /api/v1/orders`, `GET /api/v1/orders/{id}`, `GET /api/v1/orders`, `POST /api/v1/orders/{id}/cancel`)
- **AND** each fuzz target's regression corpus is checked into `services/order-service/test/fuzz/<endpoint>/corpus/`
- **AND** the fuzz targets run as part of `make verify-pr` (not only as a nightly cron)

#### Scenario: Fuzz target detects validation bypass

- **WHEN** a fuzz-generated payload bypasses input validation and reaches the application layer with invalid data
- **THEN** the fuzz target reports a finding and the regression corpus is updated to prevent the bypass from recurring
