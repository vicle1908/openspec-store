# Proposal: Add Postman and Newman Feature Integration and End-to-End Test Suite

## Why

The `go-microservices` repository contains 8 independently deployable microservices (`catalog`, `customer`, `inventory`, `notification`, `order`, `payment`, `reporting`, `shipping`), a shared platform module, and backing infrastructure (PostgreSQL 18.6, Kafka 4.3.1, Temporal 1.32.0, Redis 8.8.1, Debezium CDC 3.6.3, Mailpit 1.31.3, OTel Collector 0.161.0, and Prometheus 3.15.0).

While unit test coverage and containerized Go smoke tests (`tests/cross-service-smoke`) exist:
1. **Zero Postman / Newman Assets**: No machine-readable Postman collections, environments, or Newman automation scripts exist in the repository.
2. **Developer Ergonomics & API Exploration**: Developers and QA engineers currently lack a standardized, interactive API collection to exercise endpoints directly without writing custom Go code or manual `curl` commands.
3. **Headless Multi-Service Integration Gate**: There is no non-Go, standards-based HTTP test runner capable of executing both isolated feature-level contract tests and multi-service business sagas in local development and external CI environments.
4. **Idempotency & Boundary Verification**: Testing of idempotency key replay, header enforcement (correlation IDs, valid ULID formats), and asynchronous workflow progression (Temporal saga execution, Mailpit SMTP delivery, Debezium outbox replication) is not accessible via standard HTTP testing tools.

## What Changes

We propose introducing a comprehensive Postman and Newman test suite under `tests/postman/` in `go-microservices`:
1. **Feature Integration Collection (`go-microservices.feature-integration.postman_collection.json`)**:
   - Covers isolated endpoints across all 8 microservices:
     - `customer-service`: Health, customer creation, retrieval, listing, display name update, email verification, address addition, and GDPR export.
     - `catalog-service`: Health, product creation, listing, details lookup, price assignment, quote generation, and price history audit.
     - `inventory-service`: Health, stock level assignment (`PUT /api/v1/inventory/levels/{sku}`), availability check, reservation, and confirmation.
     - `payment-service`: Health, payment intent creation (`POST /api/v1/payments/intents`), intent lookup, capture, and refund.
     - `shipping-service`: Health, shipment dispatch (`POST /api/v1/shipments`), status/tracking lookup, and delivery completion.
     - `notification-service`: Health, direct notification creation, status lookup, and listing.
     - `order-service`: Health, order creation, order lookup, and filtered customer order queries.
     - `reporting-service`: Health, orders report, and date-range revenue rollups.
     - Infrastructure & Telemetry: Debezium connector statuses, Mailpit API messages, OTel health check, and Prometheus metrics.
   - Includes positive assertions, negative tests (missing headers, invalid JSON, unknown fields), and idempotency replay assertions.
2. **End-to-End Saga Workflow Collection (`go-microservices.e2e-saga.postman_collection.json`)**:
   - Executes the complete checkout and fulfillment lifecycle sequentially:
     - Customer creation $\to$ Catalog product creation & pricing $\to$ Inventory stocking $\to$ Order placement $\to$ Asynchronous Temporal saga fulfillment polling (advancing to `shipped`) $\to$ Outbound SMTP delivery verification in Mailpit $\to$ Debezium CDC outbox verification $\to$ Reporting projection check.
3. **Postman Environment (`go-microservices.local.postman_environment.json`)**:
   - Parameterizes base URLs for all 8 microservices, Mailpit, Debezium, OTel, and Prometheus.
4. **Dynamic Pre-request Scripting (ULID & Correlation Generators)**:
   - Employs pure JavaScript Crockford Base32 ULID generation (`01` + 24 chars) to prevent static data collisions across runs.
5. **Headless Newman Runner & Makefile Targets**:
   - Adds `tests/postman/run-newman.sh` with automatic fallback to `/opt/homebrew/bin/newman` or `npx -y newman`.
   - Adds `make newman-test`, `make newman-e2e`, and `make newman-all` targets to root `Makefile`.

## Capabilities

### Modified Capabilities
- `platform-verification`: Adds normative requirements for Postman/Newman automated API integration and end-to-end verification suites, schema validation, and Makefile orchestration.

## Non-Goals

- Replacing existing Go unit tests or the Go-based containerized smoke runner (`tests/cross-service-smoke`).
- Modifying production microservice Go code or changing existing REST API routes or schemas.
- Modifying Kubernetes or cloud deployment manifests.

## Impact

- **Affected Repository**: `~/Developer/platform/go-microservices`
- **New Directory**: `tests/postman/`
- **Dependencies**: Uses existing workstation `newman` CLI (`/opt/homebrew/bin/newman`) or `npx newman` with zero additional language toolchains required.
- **CI / Local Ergonomics**: Instant one-command execution via `make newman-all` with terminal and JUnit XML reporting.
