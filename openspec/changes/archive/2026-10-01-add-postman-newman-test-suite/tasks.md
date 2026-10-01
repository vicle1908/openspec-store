# Tasks: Add Postman and Newman Feature Integration and End-to-End Test Suite

## 1. Environment & Pre-Request Script Foundation (P0)

- [x] 1.1 Create `tests/postman/environments/go-microservices.local.postman_environment.json` parameterizing all 8 microservices with correct host port remappings (`payment_url: 8086`, `shipping_url: 8087`, `inventory_url: 8088`), Mailpit (`:8025`), Debezium (`:8085`), OTel (`:13133`), and Prometheus (`:9100`). Verification: validate JSON format with `jq . tests/postman/environments/go-microservices.local.postman_environment.json`.
- [x] 1.2 Create `tests/postman/environments/go-microservices.ci.postman_environment.json` using container-internal Docker bridge network hostnames and ports (`payment-api:8083`, `shipping-api:8085`, `inventory-api:8084`, `debezium:8083`). Verification: validate JSON format with `jq .`.
- [x] 1.3 Implement pure JavaScript Crockford Base32 ULID generator in `tests/postman/scripts/ulid-generator.js` and collection root pre-request scripts using Web Crypto `crypto.getRandomValues()` with math fallback, setting request-scoped `current_ulid`, `idempotency_key`, `correlation_id`, and `traceparent_header`. Verification: run node test script asserting output matches `^01[0-9A-HJKMNP-TV-Z]{24}$`.

## 2. Feature Integration Collection Implementation (P1)

- [x] 2.1 Author `01-Customer-Service` folder in `tests/postman/collections/go-microservices.feature-integration.postman_collection.json` covering health (`dependencies.database === "ok"`), create (extracting PascalCase `CustomerID`), get, list, patch with required trailing slash (`PATCH /{id}/`), verify-email, and GDPR export (`202 Accepted` with `Idempotency-Key`). Verification: newman run folder passes.
- [x] 2.2 Author `02-Catalog-Service` folder covering health, create product (asserting 201 with empty body), list & locate product ID, get details, price assignment (with RFC3339 timestamps and empty body assertion), quote generation, and price history. Verification: newman run folder passes.
- [x] 2.3 Author `03-Inventory-Service` folder covering health, stock setting (`PUT /levels/{sku}` with SKU path param and `contract_version: 1`), availability probe (mandatory `order_id` query param), direct reservation, and confirmation. Verification: newman run folder passes.
- [x] 2.4 Author `04-Payment-Service` folder covering health, payment intent creation (`POST /intents` with `contract_version: 1`), intent retrieval, capture, and refund (asserting non-empty timestamp string for status). Verification: newman run folder passes.
- [x] 2.5 Author `05-Shipping-Service` folder covering health, shipment dispatch (`POST /shipments` with `contract_version: 1`, `carrier: "stub"`, ISO country code `US`, and `line1` address schema), status lookup, and delivery completion. Verification: newman run folder passes.
- [x] 2.6 Author `06-Notification-Service` folder covering health, direct notification dispatch (`POST /notifications` with mandatory `Idempotency-Key` and `"payload": null`), asserting 200 OK, status lookup, and listing. Verification: newman run folder passes.
- [x] 2.7 Author `07-Order-Service` folder covering health, order submission with mandatory `Idempotency-Key` and 26-char ULID line items, single order query, and customer-filtered queries (`GET /?customer_id=...`). Verification: newman run folder passes.
- [x] 2.8 Author `08-Reporting-Service` folder covering health, orders report, and date-range revenue rollups. Verification: newman run folder passes.
- [x] 2.9 Author `09-Debezium-CDC` and `10-Telemetry-Infrastructure` folders covering all 7 connector statuses (`RUNNING`), Mailpit API messages (`GET /api/v1/messages`), OTel health (`Server available`), and Prometheus metrics (`http_requests_total`). Verification: newman run folder passes.

## 3. End-to-End Saga Workflow Collection Implementation (P1)

- [x] 3.1 Author `tests/postman/collections/go-microservices.e2e-saga.postman_collection.json` sequencing the complete lifecycle: preflight $\to$ customer registration $\to$ catalog creation & pricing $\to$ inventory stocking & availability $\to$ order placement. Verification: validate JSON format with `jq .`.
- [x] 3.2 Implement asynchronous Temporal saga polling in Step 08 using `postman.setNextRequest` loop with terminal failure detection (`failed`, `cancelled`, `rejected`), 20-attempt limit, and clean `pm.collectionVariables.unset("poll_count")`. Verification: newman execution verifies loop termination on `shipped` or `completed`.
- [x] 3.3 Add Step 09 and Step 10 verifying outbound SMTP delivery in Mailpit (`/api/v1/messages`) and projection ingestion in `reporting-service`. Verification: newman run passes with 100% assertions.

## 4. Headless Automation Runner & Makefile Targets (P2)

- [x] 4.1 Create executable `tests/postman/run-newman.sh` with preflight health probes, report directory initialization (`mkdir -p "$DIR/reports"`), binary resolution (`command -v newman` $\to$ `/opt/homebrew/bin/newman` $\to$ `npx -y newman`), and CLI options (`--timeout-request 10000`, `--timeout-script 5000`, `--delay-request 500`, `--bail folder,failure`). Verification: run `./tests/postman/run-newman.sh --help`.
- [x] 4.2 Add `newman-test`, `newman-e2e`, `newman-all`, and `newman-clean` targets to root `Makefile`, and align contract test host port fallbacks (`ORDER_PAYMENT_URL=http://localhost:8086`, `ORDER_INVENTORY_URL=http://localhost:8088`, `ORDER_SHIPPING_URL=http://localhost:8087`). Verification: `make -n newman-all` shows expected commands.
- [x] 4.3 Add `tests/postman/README.md` documenting Postman App import instructions, environment variables, and CLI invocation. Verification: file exists and links are valid.

## 5. Verification & OpenSpec Governance (P3)

- [x] 5.1 Run full `make newman-all` against live Docker Compose stack. Verification: exit code 0, 0 failed assertions in JUnit XML reports (`tests/postman/reports/feature-junit.xml` and `e2e-junit.xml`).
- [x] 5.2 Validate OpenSpec change `add-postman-newman-test-suite` with strict mode. Verification: `openspec validate add-postman-newman-test-suite --strict --store openspec-store` exits 0.
