# OpenSpec Exploration Report: Postman & Newman API Integration and End-to-End Suite for go-microservices

**Date:** 2026-10-01  
**Author:** Antigravity / Hermes Agent  
**Context:** `~/Developer/platform/go-microservices` & `~/Developer/platform/openspec-store`  
**Target:** Feature Integration Testing & End-to-End Saga Flow Verification via Postman / Newman  

---

## 1. Executive Summary & Objective

The `go-microservices` monorepo currently contains 8 independently deployable microservices (`catalog`, `customer`, `inventory`, `notification`, `order`, `payment`, `reporting`, `shipping`), a shared platform module, and backing infrastructure (PostgreSQL 18.6, Kafka 4.3.1, Temporal 1.32.0, Redis 8.8.1, Debezium CDC 3.6.3, Mailpit 1.31.3, OpenTelemetry Collector 0.161.0, and Prometheus 3.15.0).

While unit tests (`go test ./...`) and compiled Go containerized smoke tests (`tests/cross-service-smoke`) exist, **no Postman collections, Newman automation runners, or standard machine-readable API integration test specifications currently exist** in the repository.

### Strategic Objective
Design, document, and plan a comprehensive Postman and Newman test suite that provides:
1. **Isolated Feature Integration Testing**: Dedicated test suites validating each microservice's external REST interface, checking HTTP status codes, headers (correlation IDs, request IDs, idempotency), JSON body contracts, error handling, and boundary validation.
2. **End-to-End (E2E) Business Flow Chaining**: A stateful checkout and fulfillment saga collection that exercises the multi-service business lifecycle: customer registration $\to$ product catalog creation & pricing $\to$ inventory stocking & reservation $\to$ order placement $\to$ Temporal saga fulfillment orchestration across payment capture, inventory confirmation, carrier dispatch, notification emission, and reporting projections.
3. **Headless CLI Automation**: Automated execution through Newman (`/opt/homebrew/bin/newman` v6.2.2) both on the local developer workstation and in CI, with machine-readable JUnit XML and JSON artifact emission.

---

## 2. Current State Assessment & Gap Analysis

| Dimension | Current State | Target State with Postman / Newman |
| :--- | :--- | :--- |
| **Existing Collections** | **Zero collections** (`find . -name "*postman*" -o -name "*newman*"` returns 0) | Two standardized Postman collections: `go-microservices.feature-integration.json` & `go-microservices.e2e-saga.json` |
| **Environment Config** | Hardcoded inside Go test fixtures or `.env` files | Standardized Postman Environment (`go-microservices.local.postman_environment.json`) parameterizing all service base URLs |
| **Protocol Validation** | Custom Go HTTP client code in `tests/cross-service-smoke` | Standard declarative HTTP assertions (`pm.test`, `pm.response.to.have.status`, JSON schema validation) |
| **Idempotency Verification** | Ad-hoc Go loops | Automated double-invocation assertions validating replay caches and fingerprint conflicts |
| **Developer Ergonomics** | Must rebuild and run Docker container to test single endpoint | Instant interactive debugging in Postman app + single-command CLI execution via `make newman-test` / `make newman-e2e` |
| **Telemetry & Outbox Hooks** | Checked implicitly | Explicit Newman assertions querying Debezium CDC connector states (`http://localhost:8085/connectors`), Mailpit messages (`http://localhost:8025/api/v1/messages`), and OTel health (`http://localhost:13133/`) |

---

## 3. Microservice API Surface & Endpoint Inventory

The 8 microservices expose distinct HTTP listening ports with specialized protocol requirements:

### 1. Customer Service (`http://127.0.0.1:8082`)
- `GET /health/ready`, `GET /health/live`
- `POST /api/v1/customers/` — Creates customer (`email`, `display_name`). Returns `CustomerID` (ULID) and version.
- `GET /api/v1/customers/{customerID}` — Fetches customer record with status.
- `GET /api/v1/customers?limit=10&cursor=...` — Cursor-paginated customer listing.
- `PATCH /api/v1/customers/{customerID}` — Updates display name or tax ID (`204 No Content`).
- `POST /api/v1/customers/{customerID}/verify-email` — Transitions email status (`204 No Content`).
- `POST /api/v1/customers/{customerID}/addresses` — Adds customer shipping address.
- `POST /api/v1/customers/{customerID}/gdpr/export` — Initiates GDPR export (`202 Accepted` or `200 OK`).

### 2. Catalog Service (`http://127.0.0.1:8083`)
- `GET /health/live`
- `POST /api/v1/catalog/products/` — Creates product (`sku`, `name`, `description`). Returns `201 Created`. Header `Idempotency-Key` supported.
- `GET /api/v1/catalog/products/?limit=100` — Lists products; returns array of `{product_id, sku}`.
- `GET /api/v1/catalog/products/{productID}` — Fetches single product details.
- `POST /api/v1/catalog/products/{productID}/prices` — Assigns active price (`amount_minor`, `currency`, `tax_class`, `effective_at`, `expires_at`).
- `GET /api/v1/catalog/products/{productID}/quote` — Computes active price quote.
- `GET /api/v1/catalog/products/{productID}/price-history` — Fetches audit log of price changes.

### 3. Inventory Service (`http://127.0.0.1:8088` -> container port `8084`)
- `GET /health/ready`, `GET /health/live`
- `PUT /api/v1/inventory/levels/{sku}` — Sets on-hand stock (`contract_version: 1`, `on_hand_quantity: int64`).
- `GET /api/v1/inventory/availability?order_id=...&sku=...` — Verifies SKU availability.
- `POST /api/v1/inventory/reservations` — Direct reservation (`contract_version: 1`, `order_id`, `lines: [...]`).
- `POST /api/v1/inventory/reservations/{reservationID}/confirm` — Commits reserved stock.
- `POST /api/v1/inventory/reservations/{reservationID}/release` — Releases reserved stock.

### 4. Payment Service (`http://127.0.0.1:8086` -> container port `8083`)
- `GET /health/ready`, `GET /health/live`
- `POST /api/v1/payments/intents` — Creates payment intent (`contract_version: 1`, `order_id`, `customer_id`, `amount_minor`, `currency`). Header `Idempotency-Key` required. Returns `payment_intent_id`, `status: "requires_capture"`.
- `GET /api/v1/payments/{intentID}` — Fetches intent status.
- `POST /api/v1/payments/{intentID}/capture` — Captures pre-authorized intent (`contract_version: 1`, `amount_minor`).
- `POST /api/v1/payments/{intentID}/refund` — Refunds payment (`contract_version: 1`, `amount_minor`, `reason`).

### 5. Shipping Service (`http://127.0.0.1:8087` -> container port `8085`)
- `GET /health/ready`, `GET /health/live`
- `POST /api/v1/shipments` — Dispatches shipment (`contract_version: 1`, `order_id`, `carrier: "stub"`, `address: {...}`). Requires 2-letter ISO country code (`US`). Header `Idempotency-Key` required.
- `GET /api/v1/shipments/{shipmentID}` — Queries shipment status and carrier tracking number.
- `POST /api/v1/shipments/{shipmentID}/complete` — Marks shipment as delivered.

### 6. Notification Service (`http://127.0.0.1:8081`)
- `GET /health/ready`, `GET /health/live`
- `POST /api/v1/notifications` — Dispatches notification (`recipient_id`, `channel: "email"`, `template_id: "order_confirmation"`, `template_version: 1`, `subject`, `payload: base64`). Header `Idempotency-Key` required. Returns `notification_id`, `status: "pending"`.
- `GET /api/v1/notifications/{notificationID}` — Fetches notification status.
- `GET /api/v1/notifications?limit=10` — Lists recent notifications.

### 7. Order Service (`http://127.0.0.1:8080` / `http://[::1]:8080`)
- `GET /health/ready`, `GET /health/live`
- `POST /api/v1/orders/` — Places new order. Requires Header `Idempotency-Key` and valid 26-character Crockford Base32 ULID for `line_item_id`. Initiates Temporal `order.fulfillment.v1` saga workflow.
- `GET /api/v1/orders/{orderID}` — Polls order status (`pending` $\to$ `processing` $\to$ `shipped`).
- `GET /api/v1/orders/?customer_id=...` — Lists customer orders.
- `POST /api/v1/orders/{orderID}/cancel` — Cancels an order.

### 8. Reporting Service (`http://127.0.0.1:8084`)
- `GET /health/ready`, `GET /health/live`
- `GET /api/v1/reports/orders?limit=10` — Read projection of orders.
- `GET /api/v1/reports/revenue?from=YYYY-MM-DD&to=YYYY-MM-DD` — Daily revenue rollups.

### 9. Infrastructure & Backing Services
- **Mailpit API (`http://127.0.0.1:8025/api/v1/messages`)**: Verifies real SMTP email delivery emitted by `notification-service`.
- **Debezium CDC Connectors (`http://127.0.0.1:8085/connectors`)**: Verifies 7 outbox replication tasks are in `RUNNING` state.
- **OpenTelemetry Collector (`http://127.0.0.1:13133/`)**: Confirms pipeline health.
- **Prometheus Metrics (`http://127.0.0.1:9100/metrics`)**: Confirms metric counters incrementing.

---

## 4. Test Suite Architecture & Design

### Collection Layout
All Postman assets will be maintained in a clean, versioned directory under the monorepo: `tests/postman/`.

```
tests/postman/
├── collections/
│   ├── go-microservices.feature-integration.postman_collection.json
│   └── go-microservices.e2e-saga.postman_collection.json
├── environments/
│   ├── go-microservices.local.postman_environment.json
│   └── go-microservices.ci.postman_environment.json
├── scripts/
│   └── ulid-generator.js
├── run-newman.sh
└── README.md
```

### Pre-Request Script Strategy (Dynamic Data Generation)
To ensure tests run hermetically without hardcoding static IDs that could collide across test runs:
- **ULID Generation**: Pure JavaScript implementation in Postman Pre-request Scripts generating 26-character valid Crockford Base32 ULIDs (`01` prefix + 24 characters).
- **Unique Identifiers**: Dynamically generated timestamps (`{{$timestamp}}`), correlation IDs (`corr-{{ulid}}`), idempotency keys (`idemp-{{ulid}}`), and customer emails (`test+{{ulid}}@victory1908.local`).
- **Environment Variable Chaining**: Responses extract and store variables for subsequent requests:
  - `pm.environment.set("customer_id", jsonData.CustomerID);`
  - `pm.environment.set("product_id", locatedProductID);`
  - `pm.environment.set("order_id", jsonData.order_id);`

### Asynchronous Saga Polling in Postman
To verify Temporal workflow progression from `pending` $\to$ `shipped` within Postman/Newman:
- Postman's `postman.setNextRequest("Poll Order Status")` looping pattern is employed with a bounded retry counter (`poll_attempt` $\le$ 20) and small wait periods, asserting eventual completion while failing closed on timeout.

---

## 5. Automation & CLI Runner Integration

Newman v6.2.2 is installed locally on the workstation (`/opt/homebrew/bin/newman`). The execution harness will be integrated into the monorepo's `Makefile`:

```makefile
# Makefile additions
.PHONY: newman-test newman-e2e newman-all

newman-test:
	./tests/postman/run-newman.sh feature

newman-e2e:
	./tests/postman/run-newman.sh e2e

newman-all: newman-test newman-e2e
```

The runner script will support:
- Automatic environment fallback (checking if services are running on `127.0.0.1` or `[::1]`).
- Comprehensive reporting formats: standard terminal CLI output, JUnit XML (`--reporters cli,junit`), and structured JSON evidence output for audit compliance.

---

## 6. OpenSpec Change Plan

This exploration transitions directly into OpenSpec change proposal:
**`add-postman-newman-test-suite`** in `~/Developer/platform/openspec-store`.

### Key Deliverables:
1. **Delta Specification (`specs/platform-verification/spec.md`)**: Adds normative requirements for Postman/Newman API integration verification and automated collection maintenance.
2. **Collection Implementation**:
   - `tests/postman/collections/go-microservices.feature-integration.postman_collection.json`
   - `tests/postman/collections/go-microservices.e2e-saga.postman_collection.json`
   - `tests/postman/environments/go-microservices.local.postman_environment.json`
3. **Execution Script & Build Targets**:
   - `tests/postman/run-newman.sh`
   - Targets in root `Makefile` (`newman-test`, `newman-e2e`, `newman-all`).
4. **Automated Verification**: Full execution of Newman against the live Docker Compose stack with zero failed assertions.
