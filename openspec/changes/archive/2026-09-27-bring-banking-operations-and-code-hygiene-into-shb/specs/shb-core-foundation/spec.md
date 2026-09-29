# shb-core-foundation Specification Delta

## Purpose
Specifies additions to `shb-core` for cryptographic payload signing, signature verification, and distributed idempotency key management.

## ADDED Requirements

### Requirement: Cryptographic Payload Signing and Verification
The `shb-core` package SHALL provide cryptographic security utilities under `shb_core.security.crypto` supporting HMAC-SHA256 and RSA-SHA256 request payload signing and verification for interbank API integrations and webhook security.

#### Scenario: Payload signing with HMAC-SHA256
- **WHEN** an application invokes `sign_payload(payload, secret_key)`
- **THEN** the utility canonicalizes the JSON payload and generates a hex-encoded HMAC-SHA256 digital signature

#### Scenario: Digital signature verification
- **WHEN** incoming request headers contain a digital signature
- **THEN** `verify_signature(payload, signature, secret_key)` validates the integrity of the payload in constant time, rejecting forged or tampered payloads

#### Scenario: Account and card PAN masking
- **WHEN** an account number or PAN string is passed to `mask_pan`
- **THEN** the utility masks middle digits, preserving only the first 4 and last 2 characters (e.g. `1029****56`)

### Requirement: Distributed Idempotency Key Management
The `shb-core` package SHALL provide a distributed idempotency manager under `shb_core.idempotency` to prevent duplicate transaction processing and double debits across distributed agent workers.

#### Scenario: Unique idempotency key reservation
- **WHEN** a payment or transfer operation is initiated with a valid idempotency key
- **THEN** the idempotency manager checks whether the key has been processed or locked
- **AND** permits execution if the key is new, caching the result with a configurable Time-To-Live (TTL)

#### Scenario: Duplicate request rejection
- **WHEN** an agent retries an operation using an already-processed or in-flight idempotency key
- **THEN** the idempotency manager returns the cached prior response or raises `DuplicateTransactionError`
