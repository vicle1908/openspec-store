## 1. Platform foundation scaffolding

- [x] 1.1 Create `platform/go.mod` pinned to Go 1.26.5 with module path `github.com/victory1908/platform`
- [x] 1.2 Create `platform/observability/`, `platform/contracts/`, `platform/kafka/`, `platform/health/`, `platform/runtime/` package skeletons with package-level doc comments
- [x] 1.3 Add `platform/Makefile` with targets `platform-verify`, `platform-test`, `platform-lint`, `platform-vet` mirroring the order-service Makefile pattern
- [x] 1.4 Add `platform/docs/README.md` describing the public `pkg/` surface and the `internal/` boundary
- [x] 1.5 Add `platform/.github/workflows/platform-ci.yml` (or equivalent CI job) that runs `make platform-verify` on every PR
- [x] 1.6 Run `docker manifest inspect` for `linux/arm64` against every pinned infrastructure image and capture results in `platform/verification/images.yaml`

## 2. Platform observability module

- [x] 2.1 Implement `platform/observability/logger.go` providing `New(ctx, service, version, env) *zap.Logger` with ISO-8601 timestamps, JSON output in non-dev, and the OTel-aware field injection described in `platform-observability` Requirement 1
- [x] 2.2 Implement `platform/observability/propagation.go` providing extract/inject helpers for `traceparent`, `X-Correlation-Id`, `X-Request-Id`, `X-Causation-Id` across HTTP and Kafka boundaries
- [x] 2.3 Implement `platform/observability/metrics.go` providing a Prometheus registry builder with the `<scope>_` prefix rule and the `/metrics` HTTP handler
- [x] 2.4 Implement `platform/observability/tracer.go` configuring the OTel tracer provider with OTLP gRPC exporter and `ParentBased(AlwaysOn)` sampling
- [x] 2.5 Implement `platform/observability/redact.go` (port the existing order-service list and add a final-pass redactor in the OTel Collector config)
- [x] 2.6 Implement `platform/observability/middleware.go` providing the chi-router HTTP middleware that creates a server span and records request metrics
- [x] 2.7 Implement `platform/observability/logging_test.go`, `propagation_test.go`, `metrics_test.go`, `tracer_test.go` (with an OTel test collector), `middleware_test.go`, `redact_test.go`
- [x] 2.8 Add fuzz tests `platform/observability/fuzz/redact_fuzz_test.go` and `platform/observability/fuzz/logging_fuzz_test.go`

## 3. Platform contracts module

- [x] 3.1 Create `platform/proto/platform/events/v1/event_envelope.proto` with all envelope fields from `platform-contracts` Requirement 1
- [x] 3.2 Create `platform/proto/buf.yaml`, `platform/proto/buf.gen.yaml` with the lint and breaking rules from `platform-contracts` Requirement 3
- [x] 3.3 Generate the Go types into `platform/contracts/platform/events/v1/`
- [x] 3.4 Implement `platform/contracts/event_envelope.go` with `NewEnvelope` and `DecodeEnvelope` constructors
- [x] 3.5 Implement `platform/contracts/event_envelope_test.go` covering round-trip, invalid bytes, missing required fields
- [x] 3.6 Add fuzz test `platform/contracts/fuzz/decode_envelope_fuzz_test.go`
- [x] 3.7 Publish the `platform/contracts` package as `github.com/victory1908/platform/contracts/platform/events/v1`
- [x] 3.8 Author root `buf.yaml` workspace that lists `services/order-service/proto/`, `services/notification-service/proto/`, `services/customer-service/proto/`, `services/catalog-service/proto/`, `services/reporting-service/proto/`, and `platform/proto/`
- [x] 3.9 Run `buf dep update` to generate `buf.lock` and commit it; reject `buf.lock` drift in CI
- [x] 3.10 Add `buf.build/bufbuild/protovalidate` to `deps:` in `buf.yaml`; mark all input messages with `(buf.validate.field).required` for mandatory fields
- [x] 3.11 Implement `platform/contracts/validate.go` exposing `ValidateProto(msg proto.Message) error`
- [x] 3.12 Migrate every service's `proto/<domain>/v1/*.proto` to use `optional` on nullable scalars instead of `google.protobuf.*Value` wrappers
- [x] 3.13 Implement `platform/contracts/registry` with `Register(eventType string, factory func() any)` and `Decode(eventType string, payload []byte) (any, error)`
- [x] 3.14 Add architecture test `services/<service>/test/architecture/event_registry_complete_test.go` asserting every emitted event type is in the registry


## 4. Platform Kafka harness

- [x] 4.1 Implement `platform/kafka/consumer.go` providing the typed consumer with the receipt table behavior from `platform-kafka-harness` Requirement 1
- [x] 4.2 Implement `platform/kafka/receipt.go` with the durable receipt store, including the unique-violation-as-success semantics
- [x] 4.3 Implement `platform/kafka/processor.go` defining the `ProcessRecord` interface
- [x] 4.4 Implement `platform/kafka/quarantine.go` with the original-bytes-preserved quarantine table
- [x] 4.5 Implement `platform/kafka/replay.go` with the `replay-quarantine` CLI subcommand
- [x] 4.6 Implement `platform/kafka/crash_recovery.go` with the `pending → reconcile` logic from Requirement 6
- [x] 4.7 Implement unit tests `platform/kafka/{consumer,receipt,quarantine,replay,crash_recovery}_test.go`
- [x] 4.8 Implement integration test `platform/kafka/integration_test.go` against a real Kafka broker (Compose `kafka` service)

## 5. Platform health module

- [x] 5.1 Implement `platform/health/probe.go` with `/health/live`, `/health/ready`, `/health/startup` HTTP handlers
- [x] 5.2 Implement `platform/health/checks.go` with the `Check` interface and parallel execution with timeout
- [x] 5.3 Implement `platform/health/role.go` providing the `healthcheck` subcommand
- [x] 5.4 Implement unit tests covering all three probes, the parallel timeout, and the role subcommand
- [x] 5.5 Implement integration test against a real Postgres and Kafka in Compose

## 6. Platform runtime module

- [x] 6.1 Implement `platform/runtime/roles.go` with the `Run(ctx, role)` dispatch and the documented role set
- [x] 6.2 Implement `platform/runtime/fx.go` exposing `WithObservability()`, `WithHealth()`, `WithKafkaHarness()`, `WithRuntime()` Fx options
- [x] 6.3 Implement `platform/runtime/shutdown.go` with the SIGTERM/SIGINT handler and the 30-second shutdown budget
- [x] 6.4 Implement `platform/runtime/config.go` with the typed `Load[ConfigType]` helper
- [x] 6.5 Implement unit tests for each helper and integration test for the bootstrap order (Compose-driven)
- [x] 6.6 Implement `platform/runtime.NewApp(role)` that constructs a per-role `fx.New(...)` and calls `fx.ValidateApp(opts...)` before `app.Run()`
- [x] 6.7 Implement `platform/runtime/role_modules.go` exposing `RuntimeRoleModule(role, appModule)` per `platform-runtime` Requirement 12
- [x] 6.8 Migrate existing `order-service/internal/runtime/{api.go, worker.go, orchestrator.go}` to use `RuntimeRoleModule`
- [x] 6.9 Add `platform/runtime/test/fxtest_helpers.go` with `RequireStartWithin(t, timeout)` and `RequireStopWithin(t, timeout)`
- [x] 6.10 Add domain-Fx-isolation architecture test template at `platform/test/architecture/domain_no_fx_dependency_test.go`; copy it into each service
- [x] 6.11 Migrate every Temporal worker to `fx.StartStopHook` (NOT `fx.Hook` with blocking `Run()`); verify no `worker.Run` inside `OnStart` via grep in CI


## 6a. Platform cache module (capability-gated)

- [x] 6a.1 Implement `platform/cache/cache.go` exposing the `Cache` interface (`Get`, `Set`, `SetNX`, `Del`, `Incr`) and the `TTL` type with the five canonical bands (`TTLShort=5s`, `TTLMedium=60s`, `TTLLong=10m`, `TTLDay=24h`, `TTLWeek=7d`)
- [x] 6a.2 Implement `platform/cache/errors.go` with `ErrCacheMiss`, `ErrCacheOutage`, `ErrCacheCorruption`, `ErrCacheConfiguration`
- [x] 6a.3 Implement `platform/cache/keyspace.go` with the `Key(prefix, parts...)` helper that enforces the `<service>:<purpose>:<scope>:<id>` regex
- [x] 6a.4 Implement `platform/cache/observability.go` with the metrics described in `platform-cache` Requirement 7
- [x] 6a.5 Confirm the platform module imports NO cache vendor SDK (`go list -m all | grep -E 'redis|valkey|bigcache|ristretto|freecache'` returns empty)
- [x] 6a.6 Author `platform/docs/adr/0001-capability-gated-cache.md` codifying the admission policy (mirror of `order-service/docs/adr/0004-optional-infrastructure.md`)
- [x] 6a.7 Implement unit tests for the interface, the keyspace helper, the errors, and the observability surface
- [x] 6a.8 Add fuzz tests `platform/cache/fuzz/keyspace_fuzz_test.go` and `platform/cache/fuzz/ttl_fuzz_test.go`

## 6b. Platform Temporal versioning module

- [x] 6b.1 Implement `platform/temporal/versioning.go` exposing `runtime.DeploymentVersion()` that returns the worker's build ID derived from the git SHA at build time
- [x] 6b.2 Implement `platform/temporal/options.go` with `NewValidatedActivityOptions(...)` that requires `StartToCloseTimeout`, `ScheduleToCloseTimeout`, `ScheduleToStartTimeout` (optional), and `HeartbeatTimeout` (when long-running)
- [x] 6b.3 Implement `platform/temporal/errors.go` with the typed wrappers `NewNonRetryableApplicationError`, `NewRetryableApplicationError`, `NewCompensationApplicationError` (delegating to `go.temporal.io/sdk/temporal` but enforcing policy)
- [x] 6b.4 Implement `platform/temporal/saga.go` with the `NewSaga(activities, compensations)` helper that enforces inverse-order compensation
- [x] 6b.5 Implement `platform/temporal/operation_id.go` with `OperationIDFor(workflowID, operation)` for stable activity identifiers
- [x] 6b.6 Implement `platform/temporal/schedule.go` with `NewSchedule(spec, action)` wrapping Temporal's Schedule API
- [x] 6b.7 Implement `platform/temporal/telemetry.go` returning the OTel interceptor chain (`go.temporal.io/sdk/contrib/opentelemetry v0.7.0`)
- [x] 6b.8 Implement `platform/temporal/contract_version.go` with `validateVersionedOperation` and the typed error `ErrContractVersionMismatch`
- [x] 6b.9 Implement `platform/temporal/audit/` as the `workflowaudit` static-analysis tool that walks workflow source trees and rejects `time.Now`, `time.Since`, `math/rand`, `crypto/rand`, `os.Getenv`, `context.Background`, goroutines, channels
- [x] 6b.10 Implement `platform/temporal/cli/terminate.go` for `temporal-workflow terminate --workflow-id=<id>`
- [x] 6b.11 Implement unit tests for every helper; integration tests against a real Temporal dev server (Compose)
- [x] 6b.12 Author `platform/docs/adr/0002-worker-versioning-v2.md` capturing the deployment-series contract

## 6c. Platform hexagonal enforcement (architecture tests)

- [x] 6c.1 Implement `platform/architecture/` package exposing the `WalkImports(pkg, layer) error` helper that uses `golang.org/x/tools/go/packages` to inspect every import in a package
- [x] 6c.2 Implement the canonical test suite:
  - `TestDomainDoesNotImportAdapters`
  - `TestApplicationDoesNotImportAdapters`
  - `TestAdaptersDoNotImportEachOther`
  - `TestPortsDoNotImportAdapters`
  - `TestSoleWriterRule`
  - `TestPortsAreInterfaces`
  - `TestAdapterImplementsExactlyOnePort`
  - `TestDomainInvariantsAreEnforced`
  - `TestBuildTagIsolation`
- [x] 6c.3 Implement per-capability test suites:
  - `TestCacheKeyspaceDeclaration` (only when the service admits a cache)
  - `TestCacheAdapterImplementsCacheInterface` (only when the service admits a cache)
  - `TestWorkerVersioningIsConfigured` (only when the service uses Temporal)
  - `TestDeterministicWorkflowCode` (only when the service uses Temporal)
  - `TestKafkaConsumerUsesCooperativeStickyBalancer` (only when the service uses Kafka)
- [x] 6c.4 Implement the meta-test `architecture_test_test.go` that verifies each architecture test detects a planted violation
- [x] 6c.5 Document the architecture test API in `platform/architecture/README.md` so every service can wire its own `test/architecture/main_test.go`
- [x] 6c.6 Implement unit tests for the architecture package itself

## 6d. Kafka harness enhancements

- [x] 6d.1 Implement `platform/kafka/retry_consumer.go` reading from `<topic>.retry.NNNN` topics, sleeping for the configured delay, then re-publishing to the source topic with `retry-attempt` header incremented
- [x] 6d.2 Implement `platform/kafka/dlq_publisher.go` routing terminal failures to `<topic>.dlq` with `dlq-reason` and `dlq-diagnostics` headers
- [x] 6d.3 Implement `platform/kafka/inbox.go` providing the `processed_events` table helper for inbox-style dedupe (PK on `(consumer_group, event_id)`)
- [x] 6d.4 Implement `platform/kafka/burrow.go` exposing the `kafka_consumergroup_lag` metric in Burrow-compatible format
- [x] 6d.5 Update `platform/kafka/consumer.go` to use franz-go `v1.21.5` with `kgo.CooperativeStickyBalancer()`, `kgo.InstanceID()`, `kgo.SessionTimeout(45s)`, `kgo.HeartbeatInterval(3s)`, `kgo.MaxConcurrentFetches(2)`, `kgo.FetchMinBytes(1MB)`, `kgo.MaxPartitionFetchBytes(1MB)`
- [x] 6d.6 Implement `platform/kafka/producer.go` with idempotent producer settings (`enable.idempotence=true`, `compression.type=lz4`, `linger.ms=10`, `batch.size=131072`, `acks=all`, `max.in.flight.requests.per.connection=5`, `delivery.timeout.ms=120000`)
- [x] 6d.7 Implement `platform/kafka/propagation.go` extracting/injecting `traceparent`, `X-Correlation-Id`, `X-Request-Id`, `X-Causation-Id` across Kafka boundaries

## 6e. Debezium connector improvements

- [x] 6e.1 Update `order-service/deploy/debezium-connector.json` to add `heartbeat.interval.ms=10000` and `heartbeat.topics.prefix=order-debezium-heartbeat`
- [x] 6e.2 Migrate `order-service/internal/adapters/postgres/migrations/` to add `ALTER TABLE outbox REPLICA IDENTITY DEFAULT` (INSERT-only outbox halves WAL volume)
- [x] 6e.3 Update Debezium producer settings (`producer.override.*`) per `precise-changes.md` Section 6
- [x] 6e.4 Author `services/order-service/docs/adr/0004-debezium-connector-tuning.md` documenting the heartbeat and REPLICA IDENTITY choices

## 6f. Platform Go runtime (1.26 conventions)

- [x] 6f.1 Every service's `go.mod` pins `go 1.26.5` exactly; the `verify-go-version` Makefile target fails the build if not
- [x] 6f.2 Each service's `Dockerfile` and `Deployment` manifest sets `GOMEMLIMIT` to 80% of the container memory limit
- [x] 6f.3 Each service commits a `default.pgo` file captured from a staging peak-load run; the build runs `go build -pgo=./default.pgo -o /app/service`
- [x] 6f.4 Every service uses the `tool` directive in `go.mod` to pin `staticcheck`, `govulncheck@v1.6.0`, `golangci-lint`, `mockgen`, `oapi-codegen`, `stringer`, `buf`; the legacy `tools.go` is deleted; CI rejects `tools.go` via `verify-no-tools-go`
- [x] 6f.5 Every `httputil.ReverseProxy` uses `Rewrite:` (not `Director:`); migration can run via `go fix -diff ./...` preview PRs
- [x] 6f.6 Integration, load, and fuzz tests write per-test artifacts via `t.ArtifactDir()` under `go test -count=1 -race -artifacts`
- [x] 6f.7 Performance benchmarks migrate to `for b.Loop()`
- [x] 6f.8 Author `docs/adr/0005-go-1.26-runtime.md` documenting `tlssecpmlkem`, `asynctimerchan`, the implicit `greenteagc=1`, and the planned Go 1.27 migration
- [x] 6f.9 Staging canary deployment sets `GOEXPERIMENT=goroutineleakprofile`; the `/debug/pprof/goroutineleak` endpoint is scraped by Prometheus
- [x] 6f.10 Run `go fix -diff ./...` once per quarter as a preview PR

## 7. Migrate order-service observability to platform module

- [x] 7.1 Replace `order-service/internal/observability/` with imports of `github.com/victory1908/platform/observability`
- [x] 7.2 Add OTel SDK wiring in `order-service/cmd/order-service/api/main.go`, exposing `/metrics` on a separate port
- [x] 7.3 Propagate trace context across all HTTP and Kafka boundaries in `order-service`
- [x] 7.4 Update `order-service/docker-compose.yaml` to set `OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4317`
- [x] 7.5 Verify `make verify-pr` succeeds for the order-service against the new platform module
- [x] 7.6 Run `make test-e2e` and confirm the order-service's traces appear in Tempo, metrics in Mimir, logs in Loki

## 8. OTel Collector and LGTM overlay

- [x] 8.1 Create `deploy/docker-compose.lgtm.yaml` overlay with the `grafana/otel-lgtm:v0.11.0` image
- [x] 8.2 Create `deploy/otel-collector-config.yaml` with OTLP receivers (gRPC + HTTP), batch processor, memory_limiter, tail_sampling, and exporters (logging for dev, Tempo/Mimir/Loki for prod)
- [x] 8.3 Create `deploy/otel-collector` Dockerfile and entrypoint that loads `otel-collector-config.yaml`
- [x] 8.4 Add `deploy/otel-collector-config.prod.yaml` with the prod-only Tempo/Mimir/Loki exporters and authentication settings
- [x] 8.5 Add a Grafana dashboard JSON `deploy/grafana/order-service-overview.json` and a Loki datasource `deploy/grafana/datasources.yaml`
- [x] 8.6 Document the overlay pattern in `deploy/README.md`

## 9. Notification service scaffolding

- [x] 9.1 Create `services/notification-service/go.mod` pinned to Go 1.26.5 with module path `github.com/victory1908/services/notification-service`
- [x] 9.2 Create the role directory layout: `cmd/notification-service/{api,worker,orchestrator,migrate,infrastructure_init,healthcheck}/`
- [x] 9.3 Add `services/notification-service/Makefile` derived from `Makefile.platform` with `NOTIFICATION_` scope prefix
- [x] 9.4 Add `services/notification-service/docs/README.md` and `services/notification-service/docs/local-vs-production.md`
- [x] 9.5 Add `services/notification-service/verification/{traceability.yaml,coverage-policy.yaml,reference-environment.yaml,tools.env}`
- [x] 9.6 Pin every infrastructure image and verify `linux/arm64` manifest

## 10. Notification domain and persistence

- [x] 10.1 Define `proto/notification/events/v1/notification.proto` with `NotificationCreated`, `NotificationDispatched`, `NotificationDelivered`, `NotificationFailed`, `NotificationCancelled` events
- [x] 10.2 Generate Go types via Buf
- [x] 10.3 Implement `internal/domain/notification/` with the `Notification` aggregate, status transitions, and template versioning per `notification-aggregate` specs
- [x] 10.4 Implement unit tests for the aggregate (success, invalid transitions, version conflict)
- [x] 10.5 Implement `internal/adapters/postgres/migrations/` with the `notifications` table, the outbox table, the durable receipt table, and the quarantine table
- [x] 10.6 Implement `internal/adapters/postgres/repository.go` with the repository port and the optimistic concurrency control
- [x] 10.7 Implement `internal/ports/` with `NotificationRepository`, `UnitOfWork`, `Clock`, `IDGenerator`
- [x] 10.8 Implement integration test against a real Postgres (Compose `postgres` service)

## 11. Notification application layer

- [x] 11.1 Implement `internal/application/commands/create_notification.go` with idempotency-key handling
- [x] 11.2 Implement `internal/application/queries/get_notification.go` and `list_notifications.go`
- [x] 11.3 Implement `internal/application/orchestration/dispatch_notification_workflow.go` (Temporal workflow)
- [x] 11.4 Implement `internal/application/orchestration/dispatch_notification_activity.go` (Temporal activity)
- [x] 11.5 Implement the SMTP provider adapter behind the `NotificationProvider` interface
- [x] 11.6 Implement the outbox-driven dispatch consumer using `platform/kafka`
- [x] 11.7 Implement unit tests for commands, queries, workflow, activity, provider adapter
- [x] 11.8 Implement integration test for the dispatch workflow against real Temporal, Postgres, Kafka, SMTP catcher (mailhog)

## 12. Notification HTTP and Kafka boundary

- [x] 12.1 Implement `internal/adapters/http/` with the chi router, OTel middleware, idempotency-key middleware, error mapping
- [x] 12.2 Implement `POST /api/v1/notifications`, `GET /api/v1/notifications/{id}`, `GET /api/v1/notifications?cursor=...`
- [x] 12.3 Implement `internal/adapters/kafka/` consuming `orders.events.v1` and `payments.events.v1` (when it exists) via `platform/kafka`
- [x] 12.4 Implement `internal/adapters/temporal/` worker registration with the `notification` task queue
- [x] 12.5 Implement integration tests for HTTP and Kafka boundary paths

## 13. Notification verification and documentation

- [x] 13.1 Implement `test/architecture/` mirroring `platform/architecture/`: `TestDomainDoesNotImportAdapters`, `TestApplicationDoesNotImportAdapters`, `TestAdaptersDoNotImportEachOther`, `TestPortsDoNotImportAdapters`, `TestSoleWriterRule` (notification service owns `notification` schema), `TestPortsAreInterfaces`, `TestAdapterImplementsExactlyOnePort`, `TestDomainInvariantsAreEnforced` (notification aggregate transitions are typed), `TestBuildTagIsolation`
- [x] 13.2 Implement `test/architecture/TestDeterministicWorkflowCode` invoking `workflowaudit` against every workflow file
- [x] 13.3 Implement `test/architecture/TestWorkerVersioningIsConfigured` asserting the worker's `WorkerDeploymentOptions` are non-empty
- [x] 13.4 Implement `test/integration/` end-to-end: emit `OrderShipped` from order-service, observe notification email in mailhog
- [x] 13.5 Implement `test/compatibility/` covering the documented scenarios in `notification-aggregate` and `notification-dispatcher` specs (status transitions, template versioning, idempotency, retry, DLQ)
- [x] 13.6 Implement `test/faults/` covering SMTP outage (5s deadline), retry exhaustion, quarantine, malformed envelope decode, idempotency-key collision, dedupe under redelivery, retry topic overflow, DLQ publication, consumer crash mid-transaction
- [x] 13.7 Implement `test/performance/` with a 1k-notification/s dispatch load test against mailhog (p99 latency, mailhog catch-rate, retry rate, DLQ rate)
- [x] 13.8 Implement `test/replay/<workflow>_replay_test.go` for the dispatch workflow against recorded history
- [x] 13.9 Implement `test/fuzz/` for the aggregate (status transitions, idempotency key collisions, template version mismatches)
- [x] 13.10 Add fuzz tests `test/fuzz/cache_key_fuzz_test.go` if the cache is admitted
- [x] 13.11 Implement `test/kafka/` covering retry-topic chain: processor returns RetryableError → record routed to `.retry.1000` → RetryConsumer picks it up after 1s → re-publishes to source topic → processor runs again
- [x] 13.12 Implement `test/observability/` confirming OTel spans propagate from the HTTP handler through Kafka headers and back into the dispatch workflow's span
- [x] 13.13 Author `docs/runbooks/notification-dispatch.md` with troubleshooting steps
- [x] 13.14 Author `docs/sequences/notification-lifecycle.md` with the canonical sequence diagram
- [x] 13.15 Author `docs/cache-keyspace.md` if the cache is admitted
- [x] 13.16 Verify `make verify-pr`, `make verify-release`, and `make verify-traceability` succeed for notification-service

## 18a. Customer service additional verification

- [x] 18a.1 Implement `test/architecture/` mirroring platform; add `TestSoleWriterRule` (customer owns `customer` schema) and `TestDeterministicWorkflowCode` (purge workflow is deterministic)
- [x] 18a.2 Implement `test/replay/customer_purge_replay_test.go` against recorded purge workflow history
- [x] 18a.3 Implement `test/faults/` covering: GDPR export under Postgres slow-query, retention timer fire at boundary, immediate-purge race with retention-timer, cryptographic-erasure failure recovery, audit-log corruption detection
- [x] 18a.4 Implement `test/compatibility/` covering GDPR export, retention timer, purge, ContinueAsNew on long histories, Schedule API for retention review
- [x] 18a.5 Implement `test/performance/` with 10k-customer GDPR export load test (p95 export time, p95 purge time)
- [x] 18a.6 Implement `test/observability/` confirming trace context propagates from the export HTTP request through the purge workflow
- [x] 18a.7 Author `docs/runbooks/customer-gdpr.md`, `docs/sequences/customer-lifecycle.md`, `docs/sequences/customer-purge.md`

## 23a. Catalog service additional verification

- [x] 23a.1 Implement `test/architecture/` mirroring platform; add `TestSoleWriterRule` (catalog owns `catalog` schema), `TestCacheKeyspaceDeclaration` (if cache admitted), `TestCacheAdapterImplementsCacheInterface` (if cache admitted), `TestCacheInvalidationOnPriceChange` (price change → SCAN match → DEL within 100ms)
- [x] 23a.2 Implement `test/faults/` covering: price-quote cache outage (fallback to Postgres), price change during in-flight quote, cache corruption (cache-aside returns ErrCacheCorruption, falls back), price-window edge cases, attribute-schema evolution, category-cycle detection
- [x] 23a.3 Implement `test/compatibility/` covering all `catalog-product` and `catalog-pricing-snapshot` scenarios
- [x] 23a.4 Implement `test/performance/` with 10k-quote/s load test (p99 quote latency, cache hit rate, Postgres fallback latency)
- [x] 23a.5 Implement `test/observability/` confirming OTel spans propagate from the Order service through the catalog HTTP client into the quote handler
- [x] 23a.6 Author `docs/runbooks/catalog-pricing.md`, `docs/sequences/catalog-lifecycle.md`, `docs/cache-keyspace.md`

## 30a. Reporting service additional verification

- [x] 30a.1 Implement `test/architecture/` mirroring platform; add `TestConsumerOnlyArchitecture` (rejects producer SDK imports), `TestSoleWriterRule` (reporting owns `reporting` schema), `TestDeterministicWorkflowCode` (rollup workflow deterministic)
- [x] 30a.2 Implement `test/faults/` covering: consumer crash mid-projection (offset vs row state), late-arriving event replay, out-of-order events per aggregate, projection drift detection, replay idempotency, Schedule API missed firing recovery
- [x] 30a.3 Implement `test/compatibility/` covering `reporting-projection` scenarios + late-event replay + replay idempotency + Schedule API
- [x] 30a.4 Implement `test/performance/` with 10k-events/s load test across all topics (consumer lag, freshness p95, projection table size, query latency p95)
- [x] 30a.5 Implement `test/observability/` confirming Burrow classifies the consumer correctly under load
- [x] 30a.6 Author `docs/runbooks/reporting-projection.md`, `docs/sequences/reporting-projection.md`

## 14. Customer service scaffolding

- [x] 14.1 Create `services/customer-service/go.mod` pinned to Go 1.26.5
- [x] 14.2 Create the role directory layout for `customer-service`
- [x] 14.3 Add `Makefile`, `docs/README.md`, `docs/local-vs-production.md`, `verification/` config
- [x] 14.4 Pin every infrastructure image and verify `linux/arm64` manifest
- [x] 14.5 Author `docs/ownership.md` row confirming customer-service owns the `customer` schema and `customers.events.v1`

## 15. Customer domain and persistence

- [x] 15.1 Define `proto/customer/events/v1/customer.proto` with all events listed in `customer-profile` Requirement 7
- [x] 15.2 Generate Go types via Buf
- [x] 15.3 Implement `internal/domain/customer/` with `Customer` and `Address` aggregates
- [x] 15.4 Implement unit tests for the aggregates (create, update, soft-delete, restore, purge transitions)
- [x] 15.5 Implement migrations for `customers`, `addresses`, `customer_audit_log`, `gdpr_purge_evidence`, the outbox table, the durable receipt table
- [x] 15.6 Implement the repository with optimistic concurrency
- [x] 15.7 Implement integration tests for the persistence layer

## 16. Customer application layer

- [x] 16.1 Implement commands: `create_customer`, `update_customer`, `soft_delete_customer`, `restore_customer`, `add_address`, `update_address`, `remove_address`
- [x] 16.2 Implement queries: `get_customer`, `list_customers`, `get_addresses`
- [x] 16.3 Implement the `CustomerPurgeWorkflow` and `CustomerPurgeActivity` per `customer-gdpr-export` Requirement 2
- [x] 16.4 Implement the audit log writer and the cryptographic erasure routine
- [x] 16.5 Implement the unit-of-work orchestration with outbox writes
- [x] 16.6 Implement unit tests for commands, queries, workflow, activity
- [x] 16.7 Implement integration test for the purge workflow against real Temporal and Postgres

## 17. Customer HTTP and Kafka boundary

- [x] 17.1 Implement the chi router with the documented endpoints in `customer-profile` Requirement 5
- [x] 17.2 Implement idempotency-key middleware
- [x] 17.3 Implement error mapping (404, 409, 400, 422)
- [x] 17.4 Implement the `GET /api/v1/customers/{id}/reference` endpoint for the Order Service
- [x] 17.5 Implement the GDPR export and immediate-purge endpoints per `customer-gdpr-export`
- [x] 17.6 Implement the Kafka producer for `customers.events.v1`
- [x] 17.7 Implement the Kafka consumer for external `CustomerRegistered` events (if any)
- [x] 17.8 Implement integration tests for HTTP and Kafka boundaries

## 18. Customer verification and documentation

- [x] 18.1 Implement `test/architecture/` with the standard set
- [x] 18.2 Implement `test/integration/` end-to-end: create customer, GDPR export, retention-driven purge
- [x] 18.3 Implement `test/compatibility/` covering all documented scenarios in customer specs
- [x] 18.4 Implement `test/faults/` covering concurrency conflicts, soft-delete race, retention timer edge cases
- [x] 18.5 Author `docs/runbooks/customer-gdpr.md` with the export and purge runbook
- [x] 18.6 Author `docs/sequences/customer-lifecycle.md`
- [x] 18.7 Verify `make verify-pr` and `make verify-release` succeed for customer-service

## 19. Catalog service scaffolding

- [x] 19.1 Create `services/catalog-service/go.mod` pinned to Go 1.26.5
- [x] 19.2 Create the role directory layout for `catalog-service`
- [x] 19.3 Add `Makefile`, `docs/README.md`, `docs/local-vs-production.md`, `verification/` config
- [x] 19.4 Pin every infrastructure image and verify `linux/arm64` manifest
- [x] 19.5 Author `docs/ownership.md` row confirming catalog-service owns the `catalog` schema and `catalog.events.v1`

## 20. Catalog domain and persistence

- [x] 20.1 Define `proto/catalog/events/v1/catalog.proto` with `ProductCreated`, `ProductUpdated`, `ProductActivated`, `ProductArchived`, `ProductVariantAdded/Updated/Removed`, `PriceAssigned`, `PriceChanged`
- [x] 20.2 Generate Go types via Buf
- [x] 20.3 Implement `internal/domain/catalog/` with `Product`, `ProductVariant`, `Category`, `Price` aggregates
- [x] 20.4 Implement unit tests for the aggregates (status transitions, variant lifecycle, category cycle detection)
- [x] 20.5 Implement migrations for `products`, `product_variants`, `categories`, `prices`, the outbox, the durable receipt
- [x] 20.6 Implement the repository with optimistic concurrency
- [x] 20.7 Implement integration tests for the persistence layer

## 21. Catalog application layer

- [x] 21.1 Implement commands: `create_product`, `update_product`, `activate_product`, `archive_product`, `add_variant`, `update_variant`, `remove_variant`, `assign_price`, `change_price`, `create_category`, `update_category`, `soft_delete_category`
- [x] 21.2 Implement queries: `get_product`, `list_products`, `get_category`, `list_categories`, `get_price_history`
- [x] 21.3 Implement the price quote service in `internal/application/pricing/quote.go` with the 5-second cache
- [x] 21.4 Implement the discount window evaluator with priority resolution
- [x] 21.5 Implement unit-of-work orchestration with outbox writes
- [x] 21.6 Implement unit tests for commands, queries, pricing, discount evaluation
- [x] 21.7 Implement integration test for the price quote path

## 22. Catalog HTTP and Kafka boundary

- [x] 22.1 Implement the chi router with the documented endpoints in `catalog-product` Requirement 3 and `catalog-pricing-snapshot` Requirement 2
- [x] 22.2 Implement idempotency-key middleware and cursor-based pagination
- [x] 22.3 Implement error mapping including the `422 no_price_for_product` case
- [x] 22.4 Implement the `GET /api/v1/products/{id}/quote` endpoint with the snapshot ID generation
- [x] 22.5 Implement the Kafka producer for `catalog.events.v1`
- [x] 22.6 Implement integration tests for HTTP and Kafka boundaries

## 23. Catalog verification and documentation

- [x] 23.1 Implement `test/architecture/` with the standard set plus the cross-service check that order-service cannot write to `catalog.prices`
- [x] 23.2 Implement `test/integration/` end-to-end: create product, assign price, quote, change price, confirm snapshot still resolves
- [x] 23.3 Implement `test/compatibility/` covering all documented scenarios
- [x] 23.4 Implement `test/performance/` with a 10k-quote/s load test
- [x] 23.5 Author `docs/runbooks/catalog-pricing.md` with discount-window and snapshot-retention runbooks
- [x] 23.6 Author `docs/sequences/catalog-lifecycle.md`
- [x] 23.7 Verify `make verify-pr` and `make verify-release` succeed for catalog-service

## 24. Wire Order Service to Customer and Catalog

- [x] 24.1 Update `order-service/internal/application/commands/create_order.go` to call `GET /customer-service/api/v1/customers/{id}/reference` before persisting the order
- [x] 24.2 Update the create-order flow to call `GET /catalog-service/api/v1/products/{id}/quote` for each line item and store the `price_snapshot_id`
- [x] 24.3 Add the OTel HTTP middleware wrapper on outbound calls so trace context propagates
- [x] 24.4 Surface typed errors `ErrPriceQuoteUnavailable` and `ErrCustomerReferenceUnavailable` to the API caller
- [x] 24.5 Update `order-service/verification/traceability.yaml` with the cross-service verification IDs (PV-100..PV-110 series)
- [x] 24.6 Update `order-service/docker-compose.yaml` to set `ORDER_CUSTOMER_SERVICE_URL` and `ORDER_CATALOG_SERVICE_URL` and add `depends_on`
- [x] 24.7 Verify `make verify-pr` and the cross-service e2e test succeed

## 25. Reporting service scaffolding

- [x] 25.1 Create `services/reporting-service/go.mod` pinned to Go 1.26.5
- [x] 25.2 Create the role directory layout for `reporting-service`
- [x] 25.3 Add `Makefile`, `docs/README.md`, `docs/local-vs-production.md`, `verification/` config
- [x] 25.4 Pin every infrastructure image and verify `linux/arm64` manifest
- [x] 25.5 Author `docs/ownership.md` row confirming reporting-service owns the `reporting` schema and is consumer-only

## 26. Reporting projection store

- [x] 26.1 Define `proto/reporting/events/v1/reporting.proto` with the projection row events (optional — reporting does not emit domain events but emits internal projection events)
- [x] 26.2 Implement migrations for `report_orders`, `report_customers`, `report_products`, `report_daily_revenue`, `report_facts`, plus the consumer offset tracking tables
- [x] 26.3 Implement the `report_daily_revenue` aggregation view or materialized refresh
- [x] 26.4 Implement the projection writer with idempotent application of events
- [x] 26.5 Implement the late-arriving-event reconciler
- [x] 26.6 Implement integration tests against real Postgres and Kafka

## 27. Reporting consumer

- [x] 27.1 Implement `internal/adapters/kafka/consumer.go` consuming every `*.events.v1` topic via `platform/kafka`
- [x] 27.2 Implement per-topic handlers that update the appropriate projection table
- [x] 27.3 Implement the consumer offset tracking using `last_event_offset`
- [x] 27.4 Implement the freshness metric `report_freshness_seconds{topic,partition}`
- [x] 27.5 Implement unit tests for each projection handler
- [x] 27.6 Implement integration tests for the full consumer path

## 28. Reporting query API

- [x] 28.1 Implement the chi router with the documented endpoints in `reporting-projection` Requirement 3
- [x] 28.2 Implement cursor-based pagination and the `404 not_yet_projected` error
- [x] 28.3 Implement the query handlers with bounded query timeouts
- [x] 28.4 Implement unit tests for each query
- [x] 28.5 Implement integration tests for the query API

## 29. Reporting replay and observability

- [x] 29.1 Implement the `reporting replay --topic=... --from-offset=... --to-offset=...` CLI command per `reporting-projection` Requirement 5
- [x] 29.2 Implement the replay progress metric `reporting_replay_events_total{topic}`
- [x] 29.3 Implement the consumer-lag and event-consumption-rate metrics
- [x] 29.4 Implement the structured log per consumer error per Requirement 6
- [x] 29.5 Verify replay is idempotent by running it twice and comparing projection rows

## 30. Reporting verification and documentation

- [x] 30.1 Implement `test/architecture/` enforcing consumer-only and no-producer-SDK-imports
- [x] 30.2 Implement `test/integration/` end-to-end: order creation in order-service produces a `report_orders` row within 5 seconds
- [x] 30.3 Implement `test/compatibility/` covering all documented scenarios
- [x] 30.4 Implement `test/faults/` covering consumer crash and offset recovery, late-arriving events
- [x] 30.5 Author `docs/runbooks/reporting-projection.md`
- [x] 30.6 Author `docs/sequences/reporting-projection.md`
- [x] 30.7 Verify `make verify-pr` and `make verify-release` succeed for reporting-service

## 31. Cross-service Compose integration

- [x] 31.1 Update `deploy/docker-compose.yaml` to declare every new service's `*-migrate`, `*-infrastructure-init`, `*-api`, `*-worker`, `*-orchestrator`, `*-healthcheck` containers
- [x] 31.2 Add `deploy/docker-compose.lgtm.yaml` overlay that brings up the OTel Collector and the LGTM stack
- [x] 31.3 Wire the cross-service `depends_on` graph so `notification-api` and `customer-api` start only after `order-api` is healthy
- [x] 31.4 Add the per-service Kafka topics, Debezium connectors, and Temporal task queues
- [x] 31.5 Add the `mailhog` SMTP catcher for local dev
- [x] 31.6 Run the full Compose stack and confirm every service passes its `healthcheck` role

## 32. End-to-end cross-service verification

- [x] 32.1 Author the e2e test driver `scripts/e2e-cross-service.sh` that runs the order → customer → catalog → notification → reporting flow
- [x] 32.2 Verify the customer row appears in reporting within 5 seconds of creation (PV-110 freshness SLO)
- [x] 32.3 Verify the catalog price change triggers a reporting `report_products` update AND invalidates the price-quote cache within 100 ms (PV-108)
- [x] 32.4 Verify the order creation triggers a notification email in mailhog (PV-105)
- [x] 32.5 Verify the order's price_snapshot_id resolves against catalog within the snapshot-retention window (PV-102)
- [x] 32.6 Verify Order Service captures the customer reference snapshot before persisting the order (PV-100)
- [x] 32.7 Verify Order Service aborts when customer reference is unavailable (PV-101)
- [x] 32.8 Verify Order Service aborts when price quote is unavailable (PV-103)
- [x] 32.9 Verify trace context propagates from the HTTP request through cross-service calls into Kafka headers into the consumer's processing span (PV-104)
- [x] 32.10 Verify GDPR export returns the customer's data within 2 seconds (PV-106)
- [x] 32.11 Verify the customer purge workflow respects the retention timer (PV-107)
- [x] 32.12 Verify every service's OTel data lands in LGTM with the correct `service.name` resource attribute
- [x] 32.13 Verify the cross-service architecture tests pass (no peer-service internal imports, sole-writer rules enforced)
- [x] 32.14 Verify Burrow classifies every consumer group as `OK` under steady-state load
- [x] 32.15 Verify the release-cadence CI (from `phase-1-follow-ups`) passes against the Phase 2 image set

## 33. Documentation and ADRs

- [x] 33.1 Author `platform/docs/adr/0001-shared-platform-module.md` capturing the platform-boundary decision
- [x] 33.2 Author `platform/docs/adr/0002-otel-collector.md` capturing the observability-pipeline decision
- [x] 33.3 Author `platform/docs/adr/0003-buf-workspace.md` capturing the Protobuf contracts decision
- [x] 33.4 Author `docs/architecture.md` with the canonical cross-service architecture diagram and rationale
- [x] 33.5 Update `order-service/docs/ownership.md` to reflect the new peer services
- [x] 33.6 Update `order-service/docs/extraction.md` with lessons learned from Phase 2 extraction
- [x] 33.7 Update `service-template/checklist.md` with the new platform prerequisites
- [x] 33.8 Author each service's `docs/README.md`, `docs/adr/`, `docs/runbooks/`, `docs/sequences/`

## 34. Release verification

- [x] 34.1 Confirm the Phase 1 follow-ups change (`phase-1-follow-ups`) is merged first and the release-cadence CI is green
- [x] 34.2 Pin all image versions in `verification/tools.env` after `make verify-images` confirms `linux/arm64`
- [x] 34.3 Generate the Buf breaking baseline for each service at archive time
- [x] 34.4 Run `make verify-release` against the full Phase 2 image set
- [x] 34.5 Run the rollback rehearsal against the pinned Phase 1 image and the new schema
- [x] 34.6 Confirm every service's `/health/ready` is green and every service's OTel data is in LGTM during the rehearsal
- [x] 34.7 Confirm the architecture tests pass for every service against the platform module's pinned version
- [x] 34.8 Confirm `make archive` produces the changelog entries and the proto baselines for each service

## 35. Hidden technical debt from order-service code review (Phase 2a cross-cutting)

- [x] 35.1 Confirm the existing `internal/adapters/temporal/activities.go` does NOT contain hardcoded stubs for payment/inventory/shipping — replace any stub activity with a structured `log.Warn` + `ErrExtractionPending` so the platform stops pretending domain operations exist (per precise-changes.md §12.1)
- [x] 35.2 Replace the hand-rolled `decodeEnvelope` helper in `internal/adapters/kafka/` with `platform/contracts.DecodeEnvelope(...)` and add unit tests for `ErrInvalidEnvelope` (per precise-changes.md §12.2)
- [x] 35.3 Replace the per-event-type `switch` in the order-service consumer with `platform/contracts/registry.Decode(eventType, payload)` (per precise-changes.md §12.3)
- [x] 35.4 Add `Order.customer_snapshot.version` field and an `ErrCustomerReferenceStale` check in the create-order flow (per precise-changes.md §12.4)
- [x] 35.5 Introduce `ports.IDGenerator` interface and route ALL ULID generation through it; remove direct `oklog/ulid/v2` imports outside `infrastructure/id` (per precise-changes.md §12.5)
- [x] 35.6 Add `config.ValidateForRole(role)` and call it before constructing any resource in `internal/runtime/<role>.go` (per precise-changes.md §12.6)
- [x] 35.7 Add `verify-fx-graphs` Makefile target that runs `fx.ValidateApp` against every role's Fx app before `test-unit` (per precise-changes.md §12.7)
- [x] 35.8 Add `CREATE INDEX CONCURRENTLY idx_outbox_event_id ON outbox (event_id)` as a new migration; verify the index is used by `EXPLAIN ANALYZE` (per precise-changes.md §12.8)

## 36. Ready-for-Execution checklist (gates before applying)

- [x] 36.1 `openspec validate phase-2-platform-services --type change` reports valid
- [x] 36.2 `openspec validate --strict --type spec` runs against every capability spec; no warnings
- [x] 36.3 Every scenario has a `verification ID` in `verification/traceability.yaml`
- [x] 36.4 `precise-changes.md` paths match the actual order-service layout (Section 0 of that file enumerates the layout)
- [x] 36.5 `tests/platform/` directory exists with a smoke test importing every `platform/*` package
- [x] 36.6 `tools/templates/` directory contains the canonical `Makefile`, `Dockerfile`, and Compose overlay
- [x] 36.7 `docs/adr/0005-go-1.26-runtime.md` exists and documents every GODEBUG setting
- [x] 36.8 A dry-run of `openspec apply --change phase-2-platform-services --step platform-module-only` against an empty workspace completes without surfacing "unknown file" errors
- [x] 36.9 The user has approved the roll-out sequence (recommended: 1a Phase 1 follow-ups first → 2c Phase 2a platform-only first)

## 37. Verified dependency updates (2026-07-15 pass)

These tasks were identified during a re-validation pass against `proxy.golang.org` and the upstream release pages. Each item is a pre-condition for the corresponding spec section.

- [x] 37.1 Replace `v1.44.1` OTel core pins with `v1.44.0` (the only tagged stable; `v1.44.1` is a `pkg.go.dev` pseudo-version, not a real tag) — affects `proposal.md` Dependencies section and every service's `go.mod`
- [x] 37.2 Replace `v0.69.0` `exporters/prometheus` pin with `v0.66.0` (the module is on the **core** (not contrib) version line)
- [x] 37.3 Move `otelslog` import to `go.opentelemetry.io/contrib/bridges/otelslog v0.19.0` (the `instrumentation/log/slog/otelslog` path does not exist in contrib)
- [x] 37.4 Replace `instrumentation/database/sql/otelsql` with `github.com/XSAM/otelsql v0.42.0` (moved out of contrib years ago)
- [x] 37.5 Replace `instrumentation/github.com/jackc/pgx/v5` with `github.com/exaring/otelpgx v0.11.1` (the recommended native pgx tracer)
- [x] 37.6 Pin Temporal SDK at `v1.46.0` and Temporal Server at `v1.31.2`
- [x] 37.7 Pin the Temporal-OTel bridge to the Apr 30 pseudo-version (`v0.7.1-0.20260430232007-8b9d2c2589cd`) until Temporal cuts a stable `v0.7.1`/`v0.8.0`; track the issue/PR on `temporalio/sdk-go`
- [x] 37.8 Pin `kadm` at `v1.18.0` for the `infrastructure init` role
- [x] 37.9 Remove `PauseFetchTopics` / `ResumeFetchTopics` from the design narrative (not franz-go APIs); use `kgo.AutoCommitMarks() + cl.PollFetches(ctx)` throttling
- [x] 37.10 Rename `workflowaudit` → `workflowcheck` everywhere in `design.md` and `specs/platform-temporal-versioning/spec.md`; add the allowlist file at `platform/workflows/.workflowcheck.yaml`; add the tool to the `tool` directive in `go.mod`
- [x] 37.11 Update `Worker Versioning v2` wording from "Server 1.30+" to "Server 1.31+" (GA in 1.31.0); switch the type name to `worker.DeploymentOptions`
- [x] 37.12 Remove the `temporal-proxy` reference from the proposal (not a real Temporal product); use the OTel-Collector path
- [x] 37.13 Bump `oliver006/redis_exporter` from `v1.62.0` to `v1.86.0` (array-feature support for Redis 8.8)
- [x] 37.14 Bump `buf` from `v1.49.0` to `v1.71.0`; pin `protovalidate` at `v1.2.2`
- [x] 37.15 Bump `go-redis` to `v9.21.0` and `valkey-glide` to `v2.5.0` (when the catalog service admits a cache)
- [x] 37.16 Bump `pgx/v5` to `v5.10.0`; verify the `MaxConnLifetime` enforce-on-Acquire fix is in (PR #2561)
- [x] 37.17 Pin `oklog/ulid/v2` at `v2.1.1`; use the new `Make(time.Time, *rand.Reader)` and `Timestamp()` helpers
- [x] 37.18 Pin `golang.org/x/crypto` at `v0.54.0`; set `bcrypt.DefaultCost = 12` in the platform's config
- [x] 37.19 **Switch `mailhog` → `mailpit`** (`axllent/mailpit:v1.30`); author `order-service/docs/adr/0006-mailhog-to-mailpit.md` documenting the switch
- [x] 37.20 Pin `golangci-lint v2.12.2` (v2 line is GA; v1 is EOL); use the `.golangci.yml` v2 schema
- [x] 37.21 Correct `govulncheck` pin from the hallucinated `v1.6.0` to the real `v1.1.4`
- [x] 37.22 Pin `oapi-codegen` at `v2.7.2` (security-critical; v2.7.0–v2.7.1 had code-injection CVEs)
- [x] 37.23 Fix the four phantom Fx APIs in `specs/platform-runtime/spec.md`: `fx.ValidateApp` → `app.Err()`; `fxtest.WithRequireStartTimeout` / `WithRequireStopTimeout` → `fxtest.WithTestLogger` + `fxtest.EnforceTimeout`; add a new requirement using `fx.StartTimeout` / `fx.StopTimeout` (the real API replacing `fx.WithTimeout`)
- [x] 37.24 Audit Grafana dashboards and Tempo queries for the new `otelhttp v0.69.0` server span name format (`<method> <route>` or `<method>`) and the `_OTHER` method label
- [x] 37.25 Bump `grafana/grafana:12.0.0` → `grafana/grafana:13.1.0` and `prom/prometheus:v3.5.0` → `prom/prometheus:v3.13.1` (or LTS `v3.5.5`) in `deploy/docker-compose.lgtm.yaml`
- [x] 37.26 Migrate the OTel Collector config to handle the cluster-name snake_case rename wave (`kafkametrics` → `kafka_metrics`, `loadbalancingexporter` → `loadbalancing_exporter`, `k8sattributes` → `k8s_attributes`) introduced between `v0.149` and `v0.156`
- [x] 37.27 Enable `OTEL_GO_X_SELF_OBSERVABILITY=true` in staging (or canary) to surface SDK self-metrics; promote to production once stable
- [x] 37.28 Verify the `tp.Shutdown(ctx)` error path is logged in every service (the `BatchSpanProcessor.Shutdown` error was historically swallowed; v1.44.0 now propagates via `errors.Join`)
- [x] 37.29 Plan the mockgen → mockery/moq migration as a Phase 3+ follow-up (mockgen is archived; mockery v3 is a drop-in)
- [x] 37.30 Run `make verify-images` for `linux/arm64` against every updated image pin; record the digest in `verification/tools.env`
