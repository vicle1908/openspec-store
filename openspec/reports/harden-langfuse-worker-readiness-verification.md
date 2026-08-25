# harden-langfuse-worker-readiness verification

Date: 2026-08-25
Store: `openspec-store`
Schema: `spec-driven`
Implementation source: `/Users/androidteam/Developer/tdt-observability`
Reviewed HEAD: `f67d945b7bfe54af1471e96291033982a77deb2f`
Implementation commit: `23f47b46dec45d5c359ccac6c134575dca026bb7`
Evidence commit: `f67d945b7bfe54af1471e96291033982a77deb2f`

## Summary

| Dimension | Status |
|---|---|
| Completeness | **BLOCKED** — 10/11 tasks complete after this report commit; task 3.4 remains incomplete |
| Correctness | **BLOCKED** — 11/13 scenarios supported; two compatibility-pass scenarios fail on recurring worker socket timeouts |
| Coherence | **PASS with blocker retained** — implementation follows the queue-aware/fail-closed design and correctly refuses to reinterpret liveness as compatibility success |

Final assessment: **not ready for archive**.

## Evidence mapping

### Langfuse worker readiness is queue-aware

- `deploy/docker-compose.langfuse.yaml` makes web and worker depend on healthy Redis.
- The worker healthcheck uses the image-supported bounded endpoint
  `/api/ready?failIfQueueConsumptionStuck=true` on port 3030.
- Focused Compose tests cover Langfuse/full profiles, finite budgets, dependency conditions, and exact false BullMQ bypass value.
- Fresh runtime readiness was HTTP 200 with status `ok`, queue consumption enabled, 32 registered workers, and `stuck=false` for every minute of the 699-second window.
- Worker, Redis, and gateway restart counts remained zero.

### Redis 8 and ClickHouse 26 compatibility

- `_check_langfuse_bullmq_skip` rejects file and ambient non-false overrides before Docker mutation; focused tests cover both paths.
- Redis remained `redis:8.10.1-alpine`, healthy, and restart-free.
- ClickHouse retained exactly one matching event in both `default.events_core` and `default.events_full` for trace `2b19f3b56803f23b20e8a0fb703a297c`.
- **Failure:** worker logs accumulated 616 matches for recurring `Queue job ... errored: Error: Socket timeout. Expecting data, but didn't receive any in 30000ms.` during the fresh 699-second window. Web matches remained zero.

### Backend credentials and Collector configuration

- Langfuse/full Collector configs use `/api/public/otel/v1/traces` with
  `x-langfuse-ingestion-version: "4"` and Basic-auth environment providers.
- Both configs validate under `otel/opentelemetry-collector-contrib:0.159.0`.
- Focused tests assert the exact endpoint/header and no legacy fallback.
- The fresh trace reached Langfuse exactly once, Tempo returned HTTP 200, MLflow contained one matching span, gateway readiness returned HTTP 200, and Collector counters retained accepted/sent spans for Langfuse, LGTM, and MLflow.

### Latest dependency cohort behavioral acceptance

- Running/health-only acceptance is correctly rejected by the new artifacts.
- Functional event delivery and strict queue readiness pass.
- **Failure:** the cohort requirement forbids Redis/ClickHouse/BullMQ/socket-timeout compatibility errors in the bounded window; the recurring worker errors violate this normative condition even though event delivery succeeds.

## Verification commands

- `openspec validate harden-langfuse-worker-readiness --strict --store openspec-store`: pass.
- `openspec doctor --store openspec-store`: pass.
- Focused pytest: 340 passed.
- Focused Ruff: pass.
- Four daemon-free profile renders: pass.
- Pinned Langfuse/full Collector validation: pass.
- `git diff --check`: pass.
- Targeted mypy: four pre-existing diagnostics at lines 424, 1129, 1543, and 1629; none is in the new helper/test paths.
- Graphify: refreshed by the implementation owner; generated output remains unstaged.
- GitNexus: implementation owner retained the staged review; apply-time MCP comparison disconnected and no fresh pass is claimed.

## Issues

### CRITICAL

1. **Task 3.4 is incomplete.** The ten-minute clean compatibility window failed with 616 worker socket-timeout error matches.
   - Recommendation: keep the change active and archive blocked. Determine whether the selected Redis 8.10.1/Langfuse 4.16.0 cohort can be corrected without undocumented timeout variables. A Redis downgrade, Langfuse upgrade, or requirement relaxation is a material dependency/specification decision and requires explicit user direction plus artifact updates.

2. **Two compatibility-pass scenarios fail.** `Redis 8 compatibility passes` and `Langfuse latest-image cohort passes` both require a bounded no-error result.
   - Recommendation: do not mark task 3.4 complete and do not reinterpret HTTP 200/readiness/event receipt as proof that the no-error requirement passed.

### WARNING

1. Redis resource/health timing remains unmeasured (`48M` reservation, `512M` limit, no explicit Redis `maxmemory`, and timeout longer than interval). This was explicitly excluded from the implementation until a representative workload provides defensible values.
2. Targeted mypy remains non-clean at pre-existing unrelated locations.

### SUGGESTION

Retain the minute-by-minute runtime evidence under a durable value-free report after the dependency decision is resolved; `/tmp/harden-langfuse-runtime-10m-evidence.md` is currently ephemeral.

## Archive disposition

Archive readiness is **blocked**. The active change must remain in
`openspec/changes/harden-langfuse-worker-readiness` with task 3.4 unchecked.
No spec sync or archive command is authorized from the current evidence.
