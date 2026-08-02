## 1. Typed Configuration and Shared Kafka Options

- [x] 1.1 Extend Reporting typed configuration with canonical brokers, ordered topics, group, client/instance identity, session/heartbeat/rebalance timeouts, concurrent fetch count, bounded records per poll, and batch deadline; add validation tests for missing, legacy, duplicate, empty, and incompatible values.
- [x] 1.2 Remove the Reporting adapter group constant and hidden Kafka fallbacks so the validated runtime configuration is passed unchanged into client construction; add a regression test that fails if adapter defaults override configuration.
- [x] 1.3 Extract or extend a narrow platform Kafka option builder for consumer identity, topics, cooperative-sticky balancing, static membership, timeouts, fetch limits, disabled auto-commit, bounded rebalance ownership, and OTel hooks without changing ordinary consumer defaults.
- [x] 1.4 Add platform equivalence tests proving ordinary consumers retain `MaxConcurrentFetches(2)` while Reporting supplies eight and the exact current franz-go v1.21.5 options remain compatible with repository Kafka 4.3.1.
- [x] 1.5 Record the current official franz-go commit, rebalance, static-membership, and offset-ordering guidance in the owning design/reference documentation without adding or updating dependencies.

## 2. Durable Processing and Batch Commit Semantics

- [x] 2.1 Refactor Reporting polling to use bounded record batches and block rebalancing only while a non-empty owned batch is processed; validate batch size/deadline remain below rebalance timeout and release rebalance on every return, cancellation, and error path.
- [x] 2.2 Mark a successful record commit-eligible only after its projection mutation and completed processed receipt are durable; add crash-point tests before projection, after projection, after receipt, and before Kafka commit.
- [x] 2.3 Mark an unprocessable record commit-eligible only after its original bytes and diagnostics are durably quarantined; add tests proving projection-plus-quarantine failure leaves the offset unmarked.
- [x] 2.4 Commit marked offsets once per bounded batch in monotonic per-partition order, prohibit synchronous per-record commits, and add tests for multi-topic/multi-partition batches and offset+1 behavior.
- [x] 2.5 Handle full and partial batch-commit failures with categorized topic/partition telemetry, preserved receipts/projections, safe rebalance release, and idempotent redelivery tests.
- [x] 2.6 Add rebalance tests proving revoked/lost partitions are not committed after unsafe ownership loss and redelivered completed records short-circuit without projection regression.

## 3. Canonical Identity, Membership, and Readiness

- [x] 3.1 Set the sole group default to `reporting.projection.v1` and the sole topic set to the four admitted event topics; add validation proving `payments.events.v1` remains unsubscribed.
- [x] 3.2 Resolve stable instance identity from explicit Reporting configuration and deployed pod/container identity, require it for deployed orchestrators, permit deterministic test identities, and reject duplicate concurrent identities.
- [x] 3.3 Keep Reporting unready until static validation passes and live Kafka metadata confirms membership in `reporting.projection.v1`; add wrong-group, no-membership, and disconnected-broker readiness tests.
- [x] 3.4 Add redacted effective-client evidence containing group, sorted topics, client/instance identity, cooperative-sticky strategy, timeout settings, concurrent fetch count, auto-commit disabled, batch bounds, and commit mode.
- [x] 3.5 Add a three-member integration cohort proving partition sharing across all four topics, cooperative-sticky rolling restart behavior, unique identities, continued projection freshness, and no duplicate logical rows.

## 4. Controlled Consumer-Group Cutover

- [x] 4.1 Implement a dry-run cutover command/report that reads active legacy/canonical members, legacy committed offsets, per-topic/partition durable receipts, current source revision, and requested group identities without mutating Kafka or PostgreSQL.
- [x] 4.2 Compute each canonical start offset as the first offset not proven completed, select the earliest unproven offset when receipts are missing/pending/non-contiguous, and add fixtures for contiguous, gapped, empty, ahead, and ambiguous histories.
- [x] 4.3 Require explicit apply intent plus exact report/source/group identity, refuse active legacy or canonical members during mutation, initialize reviewed canonical offsets, and retain per-partition before/after evidence.
- [x] 4.4 Add empty local-state cutover coverage that records the selected new-group reset policy and proves no silent default-to-latest behavior.
- [x] 4.5 Add rollback support that first stops canonical members, restores exactly one selected legacy group at reviewed retained offsets, preserves projection/receipt state, and refuses simultaneous old/new execution.

## 5. Deployment Inputs and Drift Prevention

- [x] 5.1 Replace legacy Reporting group strings in service defaults, root Compose, local-fast/production-contract overlays when present, local kind, fixtures, dashboards, alerts, runbooks, and readiness expectations with `reporting.projection.v1`.
- [x] 5.2 Add an architecture validator that scans code, rendered deployment inputs, evidence fixtures, and dashboards for `reporting-projection`, `reporting-projection.v1`, missing instance identity, wrong topic set, or fetch concurrency below eight.
- [x] 5.3 Add the canonical Reporting group, topics, instance-identity class, client behavior, and later Kafka principal/ACL intent to the runtime-contract inventory consumed by `establish-production-contract-local-readiness`.
- [x] 5.4 Verify the change does not alter existing event schemas, the existing order/revenue projection tables, processed-receipt keys, public command APIs, Payments topic admission, platform ordinary-consumer defaults, or Kafka security implementation; verify the added Customer/Catalog/Notification projections are additive and read-only.

## 6. Owning-Operation Causal Acceptance

- [x] 6.1 Extend the cross-service acceptance state and evidence schema with source request/correlation/idempotency, aggregate/version, outbox event/type/version, Kafka topic/partition/offset, Reporting instance/group, processed receipt, projection identity, expected/observed field digest, and trace identity; reject missing or cross-run links.
- [x] 6.2 Add Customer, Catalog, Order, and Notification API operations that produce one representative event for each admitted topic without direct database or Kafka mutation; capture the exact source transaction/outbox and Kafka coordinates through service-scoped read-only evidence paths.
- [x] 6.3 Assert each selected event reaches a completed Reporting processed receipt and the correct projection, comparing all contract-relevant projected fields with the source operation's committed values rather than accepting row existence.
- [x] 6.4 Redeliver the exact captured events before and after a controlled rebalance and prove one logical receipt disposition, no duplicate rows, no field regression, and preserved event/coordinate/projection causality.
- [x] 6.5 Carry the same owned-event cohort through the three-member assignment and consumer-group cutover tests, proving member movement and reviewed offset initialization preserve field-correct projections and receipt linkage.
- [x] 6.6 Label direct Kafka injection as focused malformed-envelope, quarantine, denial, or redelivery-fixture evidence only; add validator tests proving it cannot satisfy canonical Reporting or local production-contract readiness.

## 7. Verification, Documentation, and Handoff

- [x] 7.1 Add unit tests for typed configuration, shared option construction, legacy-string rejection, static identity, commit eligibility, quarantine failure, batch ordering, cancellation, causal evidence validation, and redaction.
- [x] 7.2 Add container-backed Kafka/PostgreSQL integration tests for operation-led four-topic fan-in, exact receipt/projection linkage, three-member assignment, rolling rebalance, crash/redelivery, partial commit failure, controlled cutover, lag/freshness metrics, and idempotent field-correct projection results.
- [x] 7.3 Update Reporting and platform projection documentation to describe bounded synchronous batch commits accurately, distinguish them from prohibited synchronous per-record commits, document operation-led versus focused synthetic evidence, and document cutover/rollback diagnostics.
- [x] 7.4 Run `make -C platform verify`, `make -C services/reporting-service verify-pr`, the operation-led Reporting integration and cross-service smoke cohorts, `make verify-pr`, and `make check-coverage`; retain exact results. Do NOT run `make validate-deployment` — that gate belongs to the downstream `complete-cloud-deployment-and-cicd-readiness` change.
- [x] 7.5 Run `openspec validate --strict --all`, verify no active legacy Reporting group remains in the execution environment, and hand the canonical group and causal evidence contract to the downstream `standardize-service-runtime-security-contract` (Kafka ACL generation in Section 3) and `establish-production-contract-local-readiness` (operation acceptance in Section 9) changes.
