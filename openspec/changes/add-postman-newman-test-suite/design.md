# Design: Postman and Newman Test Suite for Feature Integration and End-to-End Saga Flows

## 1. Architecture Overview

The testing framework introduces a standards-based, declarative HTTP testing layer for `go-microservices` using Postman Collection Format v2.1.0 executed headlessly via Newman v6.

```
~/Developer/platform/go-microservices/tests/postman/
├── collections/
│   ├── go-microservices.feature-integration.postman_collection.json
│   └── go-microservices.e2e-saga.postman_collection.json
├── environments/
│   ├── go-microservices.local.postman_environment.json
│   └── go-microservices.ci.postman_environment.json
├── run-newman.sh
└── README.md
```

### Key Principles
1. **Zero Hardcoded IDs & Hermetic State**: All entities (customers, products, line items, orders, idempotency keys, correlation IDs) are generated at runtime using pure JavaScript pre-request scripts.
2. **Schema & Assertion Rigor**: Every request verifies status codes, mandatory response headers, and JSON structure with `pm.expect()` assertions.
3. **Dual-Tier Test Design**:
   - **Tier 1 (Feature Integration)**: Tests isolated endpoints for each microservice, verifying positive mutations, retrieval, updates, validation rejections (400 Bad Request / 422 Unprocessable Entity), and idempotency replays.
   - **Tier 2 (End-to-End Saga)**: Sequences a complete business checkout and fulfillment flow, verifying the state transitions of the distributed transaction across multiple services.
4. **Resilient Asynchronous Polling**: For asynchronous transitions (such as Temporal sagas processing orders to `shipped`), Postman's `postman.setNextRequest` loop mechanism polls the target status with exponential backoff and a hard retry limit.

---

## 2. Directory Layout & Collection Specifications

### 2.1 Feature Integration Collection (`go-microservices.feature-integration.postman_collection.json`)
Organized into 10 folders matching the service boundaries:
1. **01-Customer-Service**:
   - `01 - Health Ready`: `GET {{customer_url}}/health/ready` (asserts `status == "ready"`, `database == "ok"`).
   - `02 - Create Customer`: `POST {{customer_url}}/api/v1/customers/` (asserts 201, extracts `CustomerID`).
   - `03 - Get Customer`: `GET {{customer_url}}/api/v1/customers/{{customer_id}}` (asserts 200, matches email).
   - `04 - List Customers`: `GET {{customer_url}}/api/v1/customers?limit=5` (asserts array structure).
   - `05 - Update Customer`: `PATCH {{customer_url}}/api/v1/customers/{{customer_id}}` (asserts 204).
   - `06 - Verify Email`: `POST {{customer_url}}/api/v1/customers/{{customer_id}}/verify-email` (asserts 204).
   - `07 - Request GDPR Export`: `POST {{customer_url}}/api/v1/customers/{{customer_id}}/gdpr/export` (asserts 200/202).
   - `08 - Negative: Invalid Body`: `POST {{customer_url}}/api/v1/customers/` with empty body (asserts 400).
2. **02-Catalog-Service**:
   - `01 - Health Live`: `GET {{catalog_url}}/health/live` (asserts 200).
   - `02 - Create Product`: `POST {{catalog_url}}/api/v1/catalog/products/` (asserts 201, header `Idempotency-Key`).
   - `03 - List Products & Locate ID`: `GET {{catalog_url}}/api/v1/catalog/products/?limit=100` (extracts `product_id`).
   - `04 - Get Product Details`: `GET {{catalog_url}}/api/v1/catalog/products/{{product_id}}` (asserts 200).
   - `05 - Assign Price`: `POST {{catalog_url}}/api/v1/catalog/products/{{product_id}}/prices` (asserts 201).
   - `06 - Price Quote`: `GET {{catalog_url}}/api/v1/catalog/products/{{product_id}}/quote` (asserts 200, matching minor unit).
   - `07 - Price History`: `GET {{catalog_url}}/api/v1/catalog/products/{{product_id}}/price-history` (asserts array length $\ge 1$).
3. **03-Inventory-Service**:
   - `01 - Health Ready`: `GET {{inventory_url}}/health/ready` (asserts 200).
   - `02 - Set Inventory Level`: `PUT {{inventory_url}}/api/v1/inventory/levels/{{product_id}}` (contract version 1, on-hand 75).
   - `03 - Check Availability`: `GET {{inventory_url}}/api/v1/inventory/availability?order_id=...&sku=...` (asserts `available == true`).
   - `04 - Reserve Inventory`: `POST {{inventory_url}}/api/v1/inventory/reservations` (asserts 200/201, extracts `reservation_id`).
   - `05 - Confirm Reservation`: `POST {{inventory_url}}/api/v1/inventory/reservations/{{reservation_id}}/confirm` (asserts `status == "confirmed"`).
4. **04-Payment-Service**:
   - `01 - Health Ready`: `GET {{payment_url}}/health/ready` (asserts 200).
   - `02 - Create Payment Intent`: `POST {{payment_url}}/api/v1/payments/intents` (asserts 201, status `requires_capture`).
   - `03 - Get Payment Intent`: `GET {{payment_url}}/api/v1/payments/{{payment_intent_id}}` (asserts 200).
   - `04 - Capture Payment`: `POST {{payment_url}}/api/v1/payments/{{payment_intent_id}}/capture` (asserts `status == "captured"`).
   - `05 - Refund Payment`: `POST {{payment_url}}/api/v1/payments/{{payment_intent_id}}/refund` (asserts 200).
5. **05-Shipping-Service**:
   - `01 - Health Ready`: `GET {{shipping_url}}/health/ready` (asserts 200).
   - `02 - Dispatch Shipment`: `POST {{shipping_url}}/api/v1/shipments` (asserts 201, carrier `stub`, tracking number, extracts `shipment_id`).
   - `03 - Get Shipment`: `GET {{shipping_url}}/api/v1/shipments/{{shipment_id}}` (asserts `status == "dispatched"`).
   - `04 - Complete Shipment`: `POST {{shipping_url}}/api/v1/shipments/{{shipment_id}}/complete` (asserts `status == "delivered"`).
6. **06-Notification-Service**:
   - `01 - Health Ready`: `GET {{notification_url}}/health/ready` (asserts 200).
   - `02 - Dispatch Notification`: `POST {{notification_url}}/api/v1/notifications` (asserts 200, extracts `notification_id`).
   - `03 - Get Notification`: `GET {{notification_url}}/api/v1/notifications/{{notification_id}}` (asserts 200).
   - `04 - List Notifications`: `GET {{notification_url}}/api/v1/notifications?limit=5` (asserts array).
7. **07-Order-Service**:
   - `01 - Health Ready`: `GET {{order_url}}/health/ready` (asserts 200).
   - `02 - Create Order`: `POST {{order_url}}/api/v1/orders/` (header `Idempotency-Key`, 26-char valid ULID line item ID, asserts 201).
   - `03 - Get Order`: `GET {{order_url}}/api/v1/orders/{{order_id}}` (asserts 200, initial status).
   - `04 - List Orders`: `GET {{order_url}}/api/v1/orders/?customer_id={{customer_id}}` (asserts 200, orders matched).
8. **08-Reporting-Service**:
   - `01 - Health Ready`: `GET {{reporting_url}}/health/ready` (asserts 200).
   - `02 - Orders Report`: `GET {{reporting_url}}/api/v1/reports/orders?limit=10` (asserts 200).
   - `03 - Revenue Report`: `GET {{reporting_url}}/api/v1/reports/revenue?from=2026-01-01&to=2026-12-31` (asserts 200).
9. **09-Debezium-CDC**:
   - `01 - List Connectors`: `GET {{debezium_url}}/connectors` (asserts 7 connectors present).
   - `02 - Verify Connector Health`: Verifies catalog, customer, inventory, notification, order, payment, shipping connectors in `RUNNING` state.
10. **10-Telemetry-Infrastructure**:
    - `01 - OTel Health`: `GET {{otel_url}}/` (asserts 200, status `Server available`).
    - `02 - Prometheus Metrics`: `GET {{prometheus_url}}/metrics` (asserts 200, `http_requests_total` metric series present).
    - `03 - Mailpit Inbound Message Inspection`: `GET {{mailpit_url}}/api/v1/messages` (asserts 200).

---

### 2.2 End-to-End Saga Collection (`go-microservices.e2e-saga.postman_collection.json`)
Executes the ordered workflow across services:
1. `Step 01 - Health Preflight`: Verifies all 8 services and 4 infrastructure components are healthy.
2. `Step 02 - Create Customer`: Registers customer `e2e_cust_{{$timestamp}}@victory1908.local`.
3. `Step 03 - Create Catalog Item`: Adds unique SKU and description.
4. `Step 04 - Price Catalog Item`: Assigns USD price (2999 minor units) effective immediately.
5. `Step 05 - Seed Stock`: Injects 100 units on-hand into `inventory-service`.
6. `Step 06 - Check Availability`: Confirms available stock before order placement.
7. `Step 07 - Submit Order`: Issues `POST /api/v1/orders/` with valid ULID line item and idempotency key.
8. `Step 08 - Poll Saga Fulfillment`: Uses `postman.setNextRequest("Step 08 - Poll Saga Fulfillment")` to poll `GET /api/v1/orders/{{order_id}}` until status is `shipped` or `completed` (max 20 retries).
9. `Step 09 - Verify Outbound Email`: Queries Mailpit (`/api/v1/messages`) to verify delivery of confirmation email.
10. `Step 10 - Verify Reporting Projection`: Queries `reporting-service` to ensure order appeared in projections.

---

## 3. Dynamic Data & ULID Scripting

### Pure JavaScript ULID Generator (Pre-request Script)
In `tests/postman/scripts/ulid-generator.js` and embedded in collection root pre-request scripts:
```javascript
function generateULID() {
    const ENCODING = "0123456789ABCDEFGHJKMNPQRSTVWXYZ";
    let now = Date.now();
    let timeStr = "";
    for (let i = 9; i >= 0; i--) {
        timeStr = ENCODING[now % 32] + timeStr;
        now = Math.floor(now / 32);
    }
    let randStr = "";
    for (let i = 0; i < 16; i++) {
        randStr += ENCODING[Math.floor(Math.random() * 32)];
    }
    return timeStr + randStr;
}
pm.environment.set("current_ulid", generateULID());
```

---

## 4. Newman Runner & Makefile Orchestration

### Runner Script (`tests/postman/run-newman.sh`)
```bash
#!/usr/bin/env bash
set -euo pipefail

SUITE="${1:-all}"
NEWMAN_BIN="${NEWMAN_BIN:-/opt/homebrew/bin/newman}"
if ! command -v "$NEWMAN_BIN" &> /dev/null; then
    NEWMAN_BIN="npx -y newman"
fi

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="$DIR/environments/go-microservices.local.postman_environment.json"

case "$SUITE" in
    feature)
        $NEWMAN_BIN run "$DIR/collections/go-microservices.feature-integration.postman_collection.json" \
            -e "$ENV_FILE" \
            --reporters cli,junit \
            --reporter-junit-export "$DIR/reports/feature-junit.xml"
        ;;
    e2e)
        $NEWMAN_BIN run "$DIR/collections/go-microservices.e2e-saga.postman_collection.json" \
            -e "$ENV_FILE" \
            --reporters cli,junit \
            --reporter-junit-export "$DIR/reports/e2e-junit.xml"
        ;;
    all)
        "$0" feature
        "$0" e2e
        ;;
    *)
        echo "Unknown suite: $SUITE (use: feature, e2e, all)" >&2
        exit 1
        ;;
esac
```

### Makefile Integration
```makefile
.PHONY: newman-test newman-e2e newman-all

newman-test:
	./tests/postman/run-newman.sh feature

newman-e2e:
	./tests/postman/run-newman.sh e2e

newman-all: newman-test newman-e2e
```
