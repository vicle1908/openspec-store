# Tasks: Add Postman and Newman Feature Integration and End-to-End Test Suite

## 1. Environment & Pre-Request Script Foundation (P0)

- [ ] 1.1 Create `tests/postman/environments/go-microservices.local.postman_environment.json` parameterizing all 8 microservices, Mailpit, Debezium, OTel, and Prometheus. Verification: validate JSON format with `jq . tests/postman/environments/go-microservices.local.postman_environment.json`.
- [ ] 1.2 Implement pure JavaScript Crockford Base32 ULID generator in `tests/postman/scripts/ulid-generator.js` and as pre-request scripts. Verification: run node test script asserting output matches `^01[0-9A-HJKMNP-TV-Z]{24}$`.

## 2. Feature Integration Collection Implementation (P1)

- [ ] 2.1 Author `01-Customer-Service` folder in `tests/postman/collections/go-microservices.feature-integration.postman_collection.json` covering health, create, get, list, patch, verify-email, and GDPR export. Verification: newman run folder passes.
- [ ] 2.2 Author `02-Catalog-Service` folder covering health, create product, list, get details, price assignment, quote generation, and price history. Verification: newman run folder passes.
- [ ] 2.3 Author `03-Inventory-Service` folder covering health, stock setting (`PUT /levels/{sku}`), availability probe, direct reservation, and confirmation. Verification: newman run folder passes.
- [ ] 2.4 Author `04-Payment-Service` folder covering health, payment intent creation, intent retrieval, capture, and refund. Verification: newman run folder passes.
- [ ] 2.5 Author `05-Shipping-Service` folder covering health, shipment dispatch (`carrier: "stub"`, ISO country code `US`), status lookup, and delivery completion. Verification: newman run folder passes.
- [ ] 2.6 Author `06-Notification-Service` folder covering health, direct notification dispatch, status lookup, and listing. Verification: newman run folder passes.
- [ ] 2.7 Author `07-Order-Service` folder covering health, order submission with idempotency key and ULID line items, single order query, and customer-filtered queries. Verification: newman run folder passes.
- [ ] 2.8 Author `08-Reporting-Service` folder covering health, orders report, and date-range revenue rollups. Verification: newman run folder passes.
- [ ] 2.9 Author `09-Debezium-CDC` and `10-Telemetry-Infrastructure` folders covering all 7 connector statuses, Mailpit API messages, OTel health, and Prometheus metrics. Verification: newman run folder passes.

## 3. End-to-End Saga Workflow Collection Implementation (P1)

- [ ] 3.1 Author `tests/postman/collections/go-microservices.e2e-saga.postman_collection.json` sequencing the complete lifecycle: preflight $\to$ customer registration $\to$ catalog creation & pricing $\to$ inventory stocking & availability $\to$ order placement. Verification: validate JSON format with `jq .`.
- [ ] 3.2 Implement asynchronous Temporal saga polling in Step 08 using `postman.setNextRequest` loop with exponential backoff until order status is `shipped` or `completed`. Verification: newman execution verifies loop termination on `shipped`.
- [ ] 3.3 Add Step 09 and Step 10 verifying outbound SMTP delivery in Mailpit and projection ingestion in `reporting-service`. Verification: newman run passes with 100% assertions.

## 4. Headless Automation Runner & Makefile Targets (P2)

- [ ] 4.1 Create executable `tests/postman/run-newman.sh` supporting `feature`, `e2e`, and `all` suites with automatic fallback to `/opt/homebrew/bin/newman` or `npx -y newman`, generating terminal and JUnit XML reports. Verification: run `./tests/postman/run-newman.sh --help`.
- [ ] 4.2 Add `newman-test`, `newman-e2e`, and `newman-all` targets to root `Makefile`. Verification: `make -n newman-all` shows expected commands.
- [ ] 4.3 Add `tests/postman/README.md` documenting Postman App import instructions, environment variables, and CLI invocation. Verification: file exists and links are valid.

## 5. Verification & OpenSpec Governance (P3)

- [ ] 5.1 Run full `make newman-all` against live Docker Compose stack. Verification: exit code 0, 0 failed assertions in JUnit XML report.
- [ ] 5.2 Validate OpenSpec change `add-postman-newman-test-suite` with strict mode. Verification: `openspec validate add-postman-newman-test-suite --strict --store openspec-store` exits 0.
