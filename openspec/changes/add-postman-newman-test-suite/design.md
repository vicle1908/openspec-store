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
1. **Variable Hygiene & Scope Isolation**:
   - `pm.environment`: Strictly read-only static configuration (service base URLs, port mappings). Never mutated during test runs.
   - `pm.collectionVariables`: Inter-request workflow state (`customer_id`, `product_id`, `order_id`, `poll_count`). Cleaned up via `.unset()` upon workflow completion.
   - `pm.variables`: Request-scoped ephemeral tokens (`current_ulid`, `idempotency_key`, `correlation_id`, `traceparent_header`). Never leaked across iterations.
2. **Schema & Assertion Rigor**:
   - Response validation uses exact HTTP status assertions (e.g. 201 for resource creation, 202 for async acceptance, 204 for empty mutations, 400/422 for boundary errors).
   - JSON responses validated with Postman's built-in `Ajv` schema validator against strict contract schemas.
3. **Dual-Tier Test Design**:
   - **Tier 1 (Feature Integration)**: Tests isolated endpoints for each microservice, verifying positive mutations, retrieval, updates, validation rejections (400 Bad Request / 422 Unprocessable Entity), and idempotency replays.
   - **Tier 2 (End-to-End Saga)**: Sequences a complete business checkout and fulfillment flow, verifying the state transitions of the distributed transaction across multiple services.
4. **Resilient Asynchronous Polling**: For asynchronous transitions (such as Temporal sagas processing orders to `shipped`), Postman's `postman.setNextRequest` loop mechanism polls the target status with exponential backoff and a hard retry limit.

---

## 2. Port Mappings & Environment Matrix

The host ports are mapped to avoid collisions with internal container ports:

| Service | Container Port | Host Port | Postman Env Variable | Environment Notes |
| :--- | :--- | :--- | :--- | :--- |
| **order-service** | `8080` | `8080` | `order_url` | Accessible on `http://127.0.0.1:8080` / `http://[::1]:8080` |
| **notification-service** | `8081` | `8081` | `notification_url` | Metrics on `:9091` |
| **customer-service** | `8082` | `8082` | `customer_url` | 1:1 host binding |
| **catalog-service** | `8083` | `8083` | `catalog_url` | 1:1 host binding |
| **reporting-service** | `8084` | `8084` | `reporting_url` | 1:1 host binding |
| **debezium** | `8083` | `8085` | `debezium_url` | Remapped to `8085` to avoid catalog conflict |
| **payment-service** | `8083` | `8086` | `payment_url` | Remapped to `8086` to avoid catalog/debezium conflict |
| **shipping-service** | `8085` | `8087` | `shipping_url` | Remapped to `8087` to avoid debezium conflict |
| **inventory-service** | `8084` | `8088` | `inventory_url` | Remapped to `8088` to avoid reporting conflict |
| **mailpit** | `8025` / `1025` | `8025` / `1025` | `mailpit_url` | API on `:8025`, SMTP on `:1025` |
| **otel-collector** | `13133` | `13133` | `otel_url` | Health probe on `:13133` |
| **prometheus** | `9090` | `9100` | `prometheus_url` | Metrics query on `:9100` |

---

## 3. Microservice Protocol Specifications & Nuances

### 1. Customer Service (`http://127.0.0.1:8082`)
- `GET /health/ready`: Asserts `pm.response.json().dependencies.database === "ok"`.
- `POST /api/v1/customers/`: Creates customer (`email`, `display_name`). Serializes PascalCase `{"CustomerID": "...", "Version": 1}`. Extract `CustomerID` into `pm.collectionVariables`.
- `GET /api/v1/customers/{{customer_id}}`: Serializes snake_case `{"customer_id": "...", "status": "active"}`.
- `PATCH /api/v1/customers/{{customer_id}}/`: **Trailing slash required** due to Chi router registration. Asserts `204 No Content`.
- `POST /api/v1/customers/{{customer_id}}/verify-email`: Asserts `204 No Content`.
- `POST /api/v1/customers/{{customer_id}}/gdpr/export`: Header `Idempotency-Key` required. Asserts `202 Accepted` (`export_id`, `status: "pending"`).

### 2. Catalog Service (`http://127.0.0.1:8083`)
- `GET /health/live`: Asserts `200 OK` (`{"status": "live"}`).
- `POST /api/v1/catalog/products/`: Header `Idempotency-Key` optional. Returns `201 Created` with an **empty body** (0 bytes). Do not parse JSON.
- `GET /api/v1/catalog/products/?limit=100`: Locate product ID from array of `{product_id, sku}`.
- `POST /api/v1/catalog/products/{{product_id}}/prices`: Requires RFC3339 timestamps for `effective_at` and `expires_at`. Returns `201 Created` with empty body.
- `GET /api/v1/catalog/products/{{product_id}}/quote`: Asserts `200 OK` with `amount_minor` and `currency`.
- `GET /api/v1/catalog/products/{{product_id}}/price-history?limit=5`: Asserts array of prices.

### 3. Inventory Service (`http://127.0.0.1:8088`)
- `GET /health/ready`: Asserts `200 OK`.
- `PUT /api/v1/inventory/levels/{{sku}}`: Path parameter is **SKU**, not product ID. Payload requires `"contract_version": 1` and `"on_hand_quantity": 75`. `DisallowUnknownFields()` active. Asserts `200 OK`.
- `GET /api/v1/inventory/availability?order_id=...&sku=...`: **`order_id` query parameter is strictly mandatory** (missing returns 400). Asserts `available: true`.
- `POST /api/v1/inventory/reservations`: Requires `"contract_version": 1`, `order_id`, and `lines: [...]`. Asserts `201 Created`, extracts `reservation_id`.
- `POST /api/v1/inventory/reservations/{{reservation_id}}/confirm`: Asserts `200 OK`, `status: "confirmed"`.

### 4. Payment Service (`http://127.0.0.1:8086`)
- `GET /health/ready`: Asserts `200 OK`.
- `POST /api/v1/payments/intents`: Requires `"contract_version": 1`, `order_id`, `customer_id`, `amount_minor`, `currency`. Header `Idempotency-Key` supported. Asserts `201 Created`, `status: "requires_capture"`.
- `POST /api/v1/payments/{{payment_intent_id}}/capture`: Header `Idempotency-Key` supported. Asserts `200 OK`, `status: "captured"`.
- `POST /api/v1/payments/{{payment_intent_id}}/refund`: Requires `"contract_version": 1`, `amount_minor`, `reason`. Note: refund `status` is serialized as an RFC3339 timestamp. Asserts `200 OK`.

### 5. Shipping Service (`http://127.0.0.1:8087`)
- `GET /health/ready`: Asserts `200 OK`.
- `POST /api/v1/shipments`: Requires `"contract_version": 1`, `order_id`, `carrier: "stub"`, header `Idempotency-Key`, and address object with `{name, line1, line2, city, state, postal_code, country}` (2-letter ISO code like `US`). `DisallowUnknownFields()` active (do not send `street`). Asserts `201 Created`, extracts `shipment_id`.
- `GET /api/v1/shipments/{{shipment_id}}`: Asserts `200 OK`, `status: "dispatched"`.
- `POST /api/v1/shipments/{{shipment_id}}/complete`: Asserts `200 OK`, `status: "delivered"`.

### 6. Notification Service (`http://127.0.0.1:8081`)
- `GET /health/ready`: Asserts `200 OK`.
- `POST /api/v1/notifications`: **Header `Idempotency-Key` is strictly mandatory** (missing returns 400). Payload field `payload` is `[]byte` in Go: must be `null` or valid Base64 string. Asserts **`200 OK`** (not 201), extracts `notification_id`.
- `GET /api/v1/notifications/{{notification_id}}`: Asserts `200 OK`.
- `GET /api/v1/notifications?limit=5`: Asserts `200 OK`.

### 7. Order Service (`http://[::1]:8080`)
- `GET /health/ready`: Asserts `200 OK`.
- `POST /api/v1/orders/`: **Header `Idempotency-Key` is strictly mandatory**. Line item `line_item_id` and order ID require **valid 26-character Crockford Base32 ULIDs**. Address requires `{street, city, state, postal_code, country}`. Asserts `201 Created`, extracts `order_id`.
- `GET /api/v1/orders/{{order_id}}`: Asserts `200 OK`.
- `GET /api/v1/orders/?customer_id={{customer_id}}`: Returns `{"orders": [...], "next_cursor": "..."}`. Asserts `200 OK`.

### 8. Reporting Service (`http://127.0.0.1:8084`)
- `GET /health/ready`: Asserts `200 OK`.
- `GET /api/v1/reports/orders?limit=10`: Asserts `200 OK`.
- `GET /api/v1/reports/revenue?from=2026-01-01&to=2026-12-31`: Asserts `200 OK`.

### 9. Infrastructure & Backing Services
- **Mailpit API (`http://127.0.0.1:8025/api/v1/messages`)**: Verifies real SMTP message delivery from `notification-service`.
- **Debezium CDC Connectors (`http://127.0.0.1:8085/connectors`)**: Verifies all 7 connectors and tasks in `RUNNING` status.
- **OpenTelemetry Collector (`http://127.0.0.1:13133/`)**: Asserts `Server available`.
- **Prometheus Metrics (`http://127.0.0.1:9100/metrics`)**: Asserts metrics active.

---

## 4. Dynamic Data & ULID Scripting

### Pure JavaScript ULID Generator (Pre-request Script)
In `tests/postman/scripts/ulid-generator.js` and collection root pre-request scripts:
```javascript
function generateULID() {
    const ENCODING = "0123456789ABCDEFGHJKMNPQRSTVWXYZ";
    let now = Date.now();
    let timeChars = new Array(10);
    for (let i = 9; i >= 0; i--) {
        timeChars[i] = ENCODING[now % 32];
        now = Math.floor(now / 32);
    }
    let randChars = new Array(16);
    let randomBytes = new Uint8Array(16);
    if (typeof crypto !== "undefined" && crypto.getRandomValues) {
        crypto.getRandomValues(randomBytes);
    } else {
        for (let i = 0; i < 16; i++) randomBytes[i] = Math.floor(Math.random() * 256);
    }
    for (let i = 0; i < 16; i++) {
        randChars[i] = ENCODING[randomBytes[i] % 32];
    }
    return timeChars.join("") + randChars.join("");
}

const currentUlid = generateULID();
pm.variables.set("current_ulid", currentUlid);
pm.variables.set("idempotency_key", "idemp-" + currentUlid);
pm.variables.set("correlation_id", "corr-" + currentUlid);

// W3C traceparent context: version(00)-traceid(32hex)-spanid(16hex)-traceflags(01)
const traceId = Array.from({ length: 32 }, () => Math.floor(Math.random() * 16).toString(16)).join("");
const spanId = Array.from({ length: 16 }, () => Math.floor(Math.random() * 16).toString(16)).join("");
pm.variables.set("traceparent_header", `00-${traceId}-${spanId}-01`);
```

---

## 5. End-to-End Saga Collection Structure & Polling Logic

The collection `tests/postman/collections/go-microservices.e2e-saga.postman_collection.json` executes 10 sequential steps:
1. `Step 01 - Health Preflight`: Probes all 8 services and 4 backing components.
2. `Step 02 - Create Customer`: Registers customer `e2e_cust_{{current_ulid}}@victory1908.local`.
3. `Step 03 - Create Catalog Item`: Adds unique SKU and product metadata.
4. `Step 04 - Price Catalog Item`: Assigns USD price ($29.99 minor units) effective immediately.
5. `Step 05 - Seed Stock`: Sets 100 units on-hand in `inventory-service` using SKU.
6. `Step 06 - Check Availability`: Verifies availability with `order_id` and `sku`.
7. `Step 07 - Submit Order`: Submits order with ULID line items and idempotency key.
8. `Step 08 - Poll Saga Fulfillment`: Asynchronous polling loop asserting transition from `pending` $\to$ `shipped` or `completed`.
9. `Step 09 - Verify Outbound Email`: Queries Mailpit (`/api/v1/messages`) to verify delivery.
10. `Step 10 - Verify Reporting Projection`: Confirms ingestion into `reporting-service`.

### Hardened Saga Polling Test Script (Step 08):
```javascript
const MAX_POLL_RETRIES = 20;
const POLL_REQUEST_NAME = "Step 08 - Poll Saga Fulfillment";
const NEXT_STEP_NAME = "Step 09 - Verify Outbound Email";

const responseJson = pm.response.json();
const status = responseJson.status;
let pollCount = Number(pm.collectionVariables.get("poll_count") || 0);

if (["failed", "cancelled", "rejected"].includes(status)) {
    pm.collectionVariables.unset("poll_count");
    postman.setNextRequest(null);
    pm.expect.fail(`Saga failed with terminal status: ${status}`);
}

if (status === "shipped" || status === "completed") {
    pm.test("Order reached fulfillment status", () => {
        pm.expect(status).to.be.oneOf(["shipped", "completed"]);
    });
    pm.collectionVariables.unset("poll_count");
    postman.setNextRequest(NEXT_STEP_NAME);
} else {
    if (pollCount >= MAX_POLL_RETRIES) {
        pm.collectionVariables.unset("poll_count");
        postman.setNextRequest(null);
        pm.expect.fail(`Polling timed out after ${MAX_POLL_RETRIES} attempts. Current status: ${status}`);
    } else {
        pm.collectionVariables.set("poll_count", pollCount + 1);
        postman.setNextRequest(POLL_REQUEST_NAME);
    }
}
```

---

## 6. Newman Runner & Makefile Orchestration

### Runner Script (`tests/postman/run-newman.sh`)
```bash
#!/usr/bin/env bash
set -euo pipefail

SUITE="${1:-all}"
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="${NEWMAN_ENV_FILE:-$DIR/environments/go-microservices.local.postman_environment.json}"
mkdir -p "$DIR/reports"

# Resolve Newman binary
if command -v newman &> /dev/null; then
    NEWMAN_CMD=(newman)
elif [ -x "/opt/homebrew/bin/newman" ]; then
    NEWMAN_CMD=(/opt/homebrew/bin/newman)
else
    NEWMAN_CMD=(npx -y newman)
fi

# Preflight check unless skipped
if [[ "${SKIP_PREFLIGHT:-0}" != "1" && "$SUITE" != "--help" && "$SUITE" != "-h" ]]; then
    echo "=== Running Preflight Health Checks ==="
    for port in 8080 8081 8082 8083 8084 8086 8087 8088; do
        if ! curl -s -f "http://127.0.0.1:$port/health/ready" > /dev/null 2>&1 && \
           ! curl -s -f "http://127.0.0.1:$port/health/live" > /dev/null 2>&1 && \
           ! curl -s -f "http://[::1]:$port/health/ready" > /dev/null 2>&1; then
            echo "ERROR: Target microservice on port $port is not healthy. Run 'make dev-up' first or set SKIP_PREFLIGHT=1." >&2
            exit 1
        fi
    done
    echo "✓ All microservice health probes passed"
fi

COMMON_ARGS=(
    -e "$ENV_FILE"
    --reporters cli,junit
    --timeout-request 10000
    --timeout-script 5000
    --delay-request 500
)

run_feature() {
    "${NEWMAN_CMD[@]}" run "$DIR/collections/go-microservices.feature-integration.postman_collection.json" \
        "${COMMON_ARGS[@]}" \
        --reporter-junit-export "$DIR/reports/feature-junit.xml"
}

run_e2e() {
    "${NEWMAN_CMD[@]}" run "$DIR/collections/go-microservices.e2e-saga.postman_collection.json" \
        "${COMMON_ARGS[@]}" \
        --bail folder,failure \
        --reporter-junit-export "$DIR/reports/e2e-junit.xml"
}

case "$SUITE" in
    feature)
        run_feature
        ;;
    e2e)
        run_e2e
        ;;
    all)
        run_feature
        run_e2e
        ;;
    -h|--help)
        echo "Usage: $0 [feature|e2e|all]"
        exit 0
        ;;
    *)
        echo "Unknown suite: $SUITE (use: feature, e2e, all)" >&2
        exit 1
        ;;
esac
```

### Makefile Integration
Add targets to `~/Developer/platform/go-microservices/Makefile`:
```makefile
.PHONY: newman-test newman-e2e newman-all newman-clean

newman-test:
	./tests/postman/run-newman.sh feature

newman-e2e:
	./tests/postman/run-newman.sh e2e

newman-all:
	./tests/postman/run-newman.sh all

newman-clean:
	rm -rf tests/postman/reports
```
Also patch the host contract test port fallback variables on lines 637, 650, and 663 (`ORDER_PAYMENT_URL=http://localhost:8086`, `ORDER_INVENTORY_URL=http://localhost:8088`, `ORDER_SHIPPING_URL=http://localhost:8087`).
