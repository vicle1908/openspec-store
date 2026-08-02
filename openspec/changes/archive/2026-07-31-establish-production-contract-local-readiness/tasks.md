## 1. Prerequisite and Runtime Contract

- [x] 1.1 **BLOCKED BY: `standardize-service-runtime-security-contract` task 9.4.** Verify every task and required acceptance artifact in `standardize-service-runtime-security-contract` is complete and passes its focused gates; stop this change if any service role still lacks production-contract support.
- [x] 1.2 Define the versioned runtime-contract schema and inventory for all eight services, shared dependencies, roles, images, commands, health contracts, configuration/secret classes, identities, dependency edges, data ownership, topics/groups, queues, provider mode, networks, container policies, resources, reductions, and evidence classes.
- [x] 1.3 Map every runtime-contract entry to owning OpenSpec requirements/scenarios and add validation that fails for untraced, duplicate, missing, or undeployed role records.
- [x] 1.4 Add positive and negative schema fixtures for a complete role, omitted role, extra role, insecure protocol, missing identity, undeclared reduction, and secret value accidentally placed in the inventory.

## 2. Compose and Kind Contract Normalization

- [x] 2.1 **REQUIRES: Section 1 complete.** Implement normalized parsing of the exact merged Compose model into runtime-contract roles, dependencies, secret references, networks, ports, healthchecks, security controls, and reductions; add fixture tests for each supported Compose pattern.
- [x] 2.2 Implement normalized parsing of rendered local kind resources into the same model, including Deployments, Jobs, ConfigMaps, Secret references, ServiceAccounts, Services, probes, security contexts, and NetworkPolicies; add fixture tests.
- [x] 2.3 Implement comparison and diagnostics that distinguish required invariant drift, renderer-specific topology, allowed reduction, deferred non-local drift, and secret leakage without comparing raw YAML.
- [x] 2.4 Add validator fixtures proving current insecure production overlays are reported as deferred downstream drift and cannot weaken or redefine the local contract.
- [x] 2.5 Wire runtime-contract validation into Compose validation, local kind validation, deployment validation, documentation traceability, and exact-revision evidence generation.

## 3. Run-Scoped PKI and Secret Bootstrap

- [x] 3.1 Implement a repository-owned Go bootstrap tool that creates a mode-0700 run directory and unique trust root, server/client certificates, PostgreSQL credentials, Kafka credentials, Redis ACL secrets, provider credentials, and other inventory-required inputs without adding an external runtime image.
- [x] 3.2 Encode canonical service/role identities and required peer identities in certificates and the non-secret bootstrap manifest; test validity windows, key usage, SAN/identity mapping, fingerprinting, and wrong-run rejection.
- [x] 3.3 Generate Compose secret declarations and local kind Secret inputs that mount individual files without interpolating values into YAML, environment values, or command arguments; add rendered-model secret-leak tests.
- [x] 3.4 Make bootstrap idempotent for one owned run/project, reject cross-project reuse, support credential/certificate replacement for fault cohorts, and test concurrent isolated runs.
- [x] 3.5 Implement scoped secret cleanup that always runs after diagnostics, removes only the owned run directory, records non-secret results, and fails readiness when cleanup is incomplete.

## 4. Mutually Exclusive Local Profiles and Commands

- [x] 4.1 Refactor the common Compose base and eight service overlays so image, role, command, health, and dependency structure remain common while plaintext credentials, host exposures, insecure transports, and stub selections move into explicit overrides.
- [x] 4.2 Add the production-contract override with secure-mode inputs, secret-file mounts, trust references, provider sandbox, hardened role settings, and no unresolved or reusable secret values; verify its merged model against the runtime contract.
- [x] 4.3 Add the local-fast override preserving supported developer convenience behavior, inject explicit insecure/non-evidentiary identity into every role, and add validation that local-fast artifacts cannot enter readiness.
- [x] 4.4 Add validation that rejects mixed production-contract/local-fast inputs, missing profile identity, insecure overrides in production-contract, and profile-specific services omitted from the merged model.
- [x] 4.5 Add `dev-fast-up`, `dev-fast-smoke`, `dev-fast-diagnostics`, and `dev-fast-down` targets with the same project ownership and cleanup safety as canonical targets; keep canonical aliases unchanged until final cutover.

## 5. Secure Dependency Topology and Initialization

- [x] 5.1 **REQUIRES: `standardize-service-runtime-security-contract` Section 2 (PostgreSQL) and Section 3 (Kafka) complete.** Configure production-contract PostgreSQL for verified TLS and role-specific secret files, then add idempotent owner/app/migrate/CDC initialization ordered before service migrations and connectors.
- [x] 5.2 Configure production-contract Kafka listeners for TLS/SASL, role-specific principals, and least-privilege ACL initialization ordered before topics, connectors, producers, and consumers; retain single-broker reduction evidence.
- [x] 5.3 Configure Debezium with its owned PostgreSQL CDC and Kafka identities, verified trust, restricted publications/topics, and redacted connector diagnostics; prove connector re-registration is idempotent.
- [x] 5.4 Configure Temporal/Nexus TLS, run-scoped identities, ClaimMapper, Authorizer, namespace, endpoint policy, and reconciliation ordering; prove the no-op Authorizer cannot start in production-contract.
- [x] 5.5 Configure Catalog/Notification Redis with run-scoped TLS, mutual client identity, per-service ACL files, disabled default user, restricted commands, and no host exposure; add allowed/denied command and key tests.
- [x] 5.6 Configure service-to-service HTTP and OTLP endpoints for mutual or required client TLS, correct trust identities, and redacted health/telemetry behavior; verify all eight roles resolve only secure endpoints.
- [x] 5.7 Add initializer dependency and failure tests proving an unsuccessful PKI, role, ACL, namespace, authorization, migration, topic, or connector job blocks every dependent role and retains safe diagnostics.

## 6. Network Segmentation, Container Hardening, and Images

- [x] 6.1 Add edge, service, data, messaging, workflow, observability, and provider-egress Compose networks and attach each role only according to runtime-contract dependency edges.
- [x] 6.2 Remove production-contract host publication for internal PostgreSQL, Kafka, Temporal, Redis, OTLP, provider, and internal service ports; add validator fixtures for every permitted loopback developer entry point.
- [x] 6.3 Apply non-root, read-only root filesystem, no-new-privileges, dropped capabilities, bounded tmpfs/volume, restart, logging, and resource controls to every production-contract application role.
- [x] 6.4 Inventory infrastructure-image writable paths and required exceptions, minimize each exception, and add a validator fixture that fails on an unowned capability, privilege, host mount, or writable-root exception.
- [x] 6.5 Add canonical role-aware image healthchecks to Inventory and Shipping, verify all eight service images use the intended binary and role command, and run image healthcheck regression tests.
- [x] 6.6 Run exact image-pin, Dockerfile, merged-model, linux/arm64 manifest, and approved-fallback checks for every production-contract image; do not add an image without current official compatibility review.

## 7. Networked Shipping Provider Sandbox

- [x] 7.1 Add a sandbox-server role to the canonical Shipping image exposing authenticated dispatch, lookup by provider idempotency key, cancellation, deterministic fault controls, and a protected effect-count endpoint.
- [x] 7.2 Implement or complete the Shipping external network adapter so production-contract dispatch, lookup/reconciliation, and cancellation pass through the ShippingProvider port with TLS, identity, credentials, timeouts, redaction, and stable idempotency.
- [x] 7.3 Add sandbox scenarios for success, rejection, delay before effect, delay after effect, connection loss after effect, duplicate request, lookup recovery, and cancellation; verify deterministic behavior and race safety.
- [x] 7.4 Add integration evidence proving successful network dispatch creates one shipment transition and outbox fact, and unknown-outcome recovery performs lookup without a duplicate provider effect.
- [x] 7.5 Reject in-process stub selection and incomplete provider credentials in production-contract while preserving the stub only in local-fast; add startup and evidence-class tests.

## 8. Local Kind Production-Contract Shape

- [x] 8.1 **REQUIRES: Sections 3 and 5 complete.** Feed the run-scoped secret/PKI inputs and production-contract security mode into local kind without changing staging or production overlays.
- [x] 8.2 Align local kind roles, Jobs, probes, security contexts, Secret mounts, Services, and NetworkPolicies with the runtime contract while retaining declared Kubernetes-specific topology.
- [x] 8.3 Extend `kind-up`, `kind-smoke`, diagnostics, and cleanup evidence with contract digest, security posture, declared reductions, and redaction validation; keep kind evidence distinct from Compose and cloud readiness.
- [x] 8.4 Run clean and repeated local kind acceptance on supported arm64 and verify normalized parity with the production-contract Compose model.

## 9. Actual-Operation Causal Acceptance

- [x] 9.1 **REQUIRES: Sections 5, 6, and 7 complete. Also REQUIRES: `reconcile-reporting-consumer-contract` task 7.5 (canonical Reporting group handoff).** Replace canonical direct-outbox CDC proof with owning-service API operations that atomically mutate each publishing domain and create its outbox fact; keep direct outbox insertion only as a separately labeled connector diagnostic and retain exact event ID, topic, partition, and offset evidence.
- [x] 9.2 Build the happy-path cohort through Customer, Catalog/Price, Inventory, and Order APIs; assert Payment captured, Inventory reserved then confirmed, Shipping dispatched once through the network sandbox, Order reached its expected terminal state, the exact notification was delivered, and Reporting projected correct fields.
- [x] 9.3 Build the compensation cohort with deterministic Shipping failure after Payment capture and Inventory reservation; assert Payment refund, Inventory release, compensated Order state, exact compensation outbox/Kafka facts, and zero Shipping logical effects.
- [x] 9.4 Build the idempotency cohort by repeating the API idempotency key, Workflow/Nexus operation identity, and selected event delivery; assert one aggregate transition, outbox fact, provider effect, notification, processed receipt, and projection result.
- [x] 9.5 Build the purposeful authorization cohort by executing the same domain commands with their allowed identities and with valid wrong identities; assert allowed durable outcomes and denial before mutation, outbox, retry/DLQ, Workflow effect, or provider call.
- [x] 9.6 Extend all thirteen Temporal execution cases beyond `COMPLETED` to assert each required durable aggregate state, outbox fact, compensation, or provider effect; require the Shipping dispatch case to use the network sandbox rather than `carrier: stub`.
- [x] 9.7 Bind notification evidence to the exact recipient plus order/event/correlation identity and expected template outcome, and bind Reporting evidence to exact projected fields plus its processed receipt and Kafka coordinates.
- [x] 9.8 Add a versioned per-operation causal ledger carrying run/project/source/contract, request/correlation/idempotency, domain aggregate, Workflow/run/activity, outbox event, Kafka coordinate, receipt/projection, provider effect, notification, trace, and before/after state identities; reject missing required links and cross-run joins.
- [x] 9.9 Query traces, metrics, and logs from each cohort's trace or correlation identity and assert the expected participating services and failure categories rather than accepting unrelated recent signals.

## 10. Security, Fault, Recovery, and Redaction Cohorts

- [x] 10.1 **REQUIRES: Sections 5 and 9 complete.** Add positive secure-operation evidence for PostgreSQL, Kafka, Debezium, Temporal/Nexus, internal HTTP, Redis, OTLP, and the provider sandbox using exact run/project/contract and causal-operation identity.
- [x] 10.2 Add negative identity/trust cohorts for each dependency class and assert protected operations are denied before mutation, readiness fails appropriately, and no business retry/DLQ or duplicate effect is created.
- [x] 10.3 Add PostgreSQL cross-schema/read/write/DDL and Kafka foreign-topic/group/admin denial cohorts with redacted authorization evidence; use service-scoped read-only diagnostic identities for state assertions and prohibit shared administrative credentials in the acceptance runner.
- [x] 10.4 Restart dependencies during in-flight purposeful HTTP, Kafka, Temporal, Reporting, and provider operations; assert reconnect bounds, preserved correlation/idempotency identities, and one logical effect in the causal ledger.
- [x] 10.5 Replace credentials or certificates during an in-flight operation and restart the affected role; prove old identity denial, new identity admission, restored readiness, and consistent domain/outbox/offset/Workflow/provider state.
- [x] 10.6 Add graceful-termination cohorts for representative API, Worker, orchestrator, and consumer roles while they own real work; assert unready-before-exit, bounded drain or safe abandonment, successful restart, and one logical effect.
- [x] 10.7 Retain Kafka redelivery, Temporal replay, Nexus authorization, Shipping unknown-outcome, same-project rerun, and concurrent-run isolation tests under the production-contract identity and bind each result to its operation ledger.
- [x] 10.8 Scan every rendered input, log, diagnostic, and evidence artifact for credential, token, private-key, and credential-bearing-DSN patterns; fail closed while reporting only artifact path and secret category.

## 11. Aggregate Evidence and Canonical Cutover

- [x] 11.1 **REQUIRES: All prior sections complete.** Version the local acceptance schema and validator for runtime-contract digest, security mode, identity fingerprints, declared reductions, parity, causal operation ledgers, security, fault/recovery, provider, redaction, and secret-cleanup results; add stale, cross-run, local-fast, missing-link, missing-class, and leaked-secret fixtures.
- [x] 11.2 Extend `local-operational-readiness` to order bootstrap, validation, startup, same-project rerun, happy-path, compensation, idempotency, authorization, fault/recovery, aggregate evidence, diagnostics, and scoped cleanup with bounded timeouts.
- [x] 11.3 Run two clean isolated production-contract Compose readiness executions plus one same-project idempotency rerun on supported arm64; retain exact image, contract, causal operation, security, fault, redaction, resource, and cleanup evidence.
- [x] 11.4 Measure startup time, peak memory, disk use, and architecture compatibility against the existing resource budget; document supported thresholds and keep optional tools out of the mandatory path unless required by evidence.
- [x] 11.5 Switch canonical `dev-up`, `dev-smoke`, `dev-diagnostics`, `dev-down`, and readiness targets to production-contract only after all aggregate evidence passes; verify local-fast remains explicitly named and non-evidentiary.
- [x] 11.6 Update root/deployment documentation, local runbooks, troubleshooting, security posture, evidence classes, causal-ledger interpretation, allowed reductions, cleanup, compatibility, and rollback guidance; record the deferred cloud change as downstream without implementing non-local resources.
- [x] 11.7 Run `make preflight`, `make verify-images`, `make compose-validate`, `make collector-validate`, `make kind-smoke`, `make local-operational-readiness`, `make validate-deployment`, `make verify-pr`, `make check-coverage`, and `openspec validate --strict --all`; retain exact results and skipped environment-dependent checks.
- [x] 11.8 Rehearse rollback of canonical target aliases to the explicit local-fast path, verify diagnostics and evidence labels remain honest, confirm no unrelated project or secret state is removed, and verify secure profile artifacts remain available for forward recovery.
