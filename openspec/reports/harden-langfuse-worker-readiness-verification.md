# harden-langfuse-worker-readiness verification

Date: 2026-08-25
Store: `openspec-store`
Schema: `spec-driven`
Implementation repository: `/Users/androidteam/Developer/tdt-observability`
Implementation commit: `3516db0dc2652f0d8d1465bc5b83e7cfecad7585`
Durable evidence commit: `272a6d5cbe480c0755f444ab90ef25323a55c130`
Current documentation/knowledge head: `474b25bd3cb9fee1f4a8786db9d3db0acbe69901`
Independent exact-commit review: `PASS / MERGE` (the ephemeral review source was summarized into this ledger before post-archive cleanup)

## Summary

| Dimension | Status |
|---|---|
| Completeness | **PASS for implementation/runtime** — tasks 1.1–3.5 complete; pre-archive tasks 4.1–4.2 close after final validation and owned-scope reconciliation |
| Correctness | **PASS** — 5/5 delta requirements and 21/21 scenarios map to source, tests, durable documentation, and current runtime evidence |
| Coherence | **PASS** — proposal, design, deltas, implementation, Docker Desktop deployment, incident exception, and retained-stack evidence agree |

Final assessment: **archived and verified at the accepted runtime checkpoint**.
There are no critical implementation, test, documentation, or runtime issues.
The later operator resource pause described below changes current process state,
not the accepted behavior or archive result.

## Evidence index

### Source and configuration

- **S1 — fixed paired policy and startup ordering:** `deploy/docker-compose.langfuse.yaml` pins Langfuse web/worker `4.16.0`, Redis `8.10.1-alpine`, ClickHouse `26.7.5.10-alpine`, contains `REDIS_SOCKET_TIMEOUT_MS: "0"` on both application services, preserves `LANGFUSE_BULLMQ_SKIP_REDIS_VERSION_CHECK` as the fail-closed false input, retains healthy-Redis dependencies, and uses the strict worker endpoint.
- **S2 — external composite:** `src/tdt_observability/deployment/stack.py:929-1375` selects exactly one running worker by Compose labels, validates a strict container ID, performs one combined in-worker Node probe, resolves `ioredis` through `/app/worker/package.json`, concurrently checks the service-DNS worker endpoint and authenticated Redis PING using existing in-container environment, reads Redis/worker container health separately, and requires exactly three consecutive full passes within a hard 120-second evidence budget.
- **S3 — value-free evidence and failure dominance:** `src/tdt_observability/deployment/stack.py` plus the deployment evidence schema reject malformed or secret-bearing composite fragments, retain component status without command output or environment assignments, enforce atomic cumulative transitions, and let a failed external composite dominate a live pass.
- **S4 — local resource policy:** `deploy/docker-compose.yaml` limits LGTM to 1.0 CPU; `deploy/docker-compose.langfuse.yaml` limits ClickHouse to 1.5 CPUs and uses bounded local HTTP `/ping` health (`wget -T 5`, Docker timeout 15 seconds).
- **S5 — exact v4 route:** the selected Langfuse Collector configurations retain `/api/public/otel/v1/traces` and `x-langfuse-ingestion-version: "4"` without a legacy route.

### Tests and static verification

- **T1 — merged-main focused gate:** 442 deployment, Compose-model, gateway, and evidence-contract tests passed; Ruff passed; daemon-free profile renders and schema/contract checks passed; `git diff --check` passed. Earlier full-repository proof at the evidence-writer stage was 603 passed.
- **T2 — Compose policy tests:** `tests/test_compose_models.py` covers heavy-service CPU limits, bounded ClickHouse HTTP health, strict worker health, healthy Redis ordering, exact false BullMQ gate, fixed paired socket-timeout literals, and absence of an override lane.
- **T3 — composite behavior tests:** `tests/deployment/test_coordinator_evidence_contract.py` covers a full finite-budget composite, endpoint HTTP 200 failing to mask Redis-path loss, timeout classification, one value-free in-worker Redis probe, failure propagation, three-pass transitions, external evidence validation, and failure dominance.
- **T4 — credential/routing tests:** focused preflight tests reject missing, placeholder, mismatched, and ambient/file BullMQ-bypass inputs without exposing values; both selected Collector configurations validate under `otel/opentelemetry-collector-contrib:0.159.0`; route/header tests reject legacy fallback.
- **T5 — independent review:** the final exact-commit review returned `PASS / MERGE`; its findings are summarized in this ledger and its temporary source was removed after archive. The preceding attack rereview passed 121 targeted tests and 223 coordinator contract tests.
- **T6 — typing boundary:** changed-line strict mypy produced no diagnostics. Module-wide mypy still reports only pre-existing diagnostics in `stack.py` and `evidence.py`; this change does not claim unrelated type cleanup.

### Durable documentation

- **D1 — operator contract:** `README.md:222-256` records the exact v4 route, strict worker endpoint, false BullMQ bypass, fixed non-overridable socket policy, four-input composite, three-pass rule, value-free evidence, and two-service primary recreation scope.
- **D2 — final acceptance:** `deploy/evidence/final-full-deployment-acceptance.md:402-487`, committed as `272a6d5cbe480c0755f444ab90ef25323a55c130`, records exact source/image identities, tests, paired literals, composite inputs and budgets, primary recreation scope, resource diagnosis, the value-free security exception, disposable and retained fault/recovery, exact trace fan-out, two clean windows, restart counts, and final retained identities.
- **D3 — planning coherence:** the proposal and design distinguish the ordinary web/worker correction and Redis fault proof from the later ClickHouse credential-incident response. They require in-place credential rotation first and permit a fresh affected-backend reset only under explicit no-old-data authority.

### Accepted runtime evidence (historical checkpoint)

- **R1 — final composite:** strict endpoint HTTP 200, `enabled=true`, `registeredWorkerCount=32`, `stuck=false`, authenticated same-worker Redis PING, healthy Redis/worker container states, and three consecutive passes. Representative elapsed times were 20.531199 seconds, 17.902537 seconds, and 57.105312 seconds while the fresh backend settled.
- **R2 — primary correction scope:** the implementation correction recreated only `langfuse-web` and `langfuse-worker`. Redis, gateway, PostgreSQL, ClickHouse, MinIO, networks, credentials, and volumes were not recreated for that correction.
- **R3 — disposable fault proof:** a collision-free project used the pinned worker and Redis 8.10.1, recorded 71 passing attempts and four fault-window failures on one long-lived ioredis client, recovered on the same client, omitted socket timeout, exited zero, had zero restarts, created no named volume, and was removed with `docker compose down` without `-v`.
- **R4 — retained fault/recovery:** only retained `langfuse-redis` stopped for 64 seconds. The external composite failed because the authenticated worker-network Redis probe failed while the worker stayed running. The same Redis container `f2609d5470f2` and volume `tdt-local-full_langfuse-redis-8-10-data` returned through normal Compose lifecycle; Redis health returned in one second and three composite passes returned in 13 seconds, within the 120-second bound, with zero application restarts. The post-recovery v4 ingestion/fan-out trace supplied representative queue work.
- **R5 — exact event fan-out:** trace `a44fd3f4ee7f4dcb59173bb2cb18f430` produced exactly one row in `default.events_core`, exactly one row in `default.events_full`, one Tempo receipt, and MLflow trace `tr-a44fd3f4ee7f4dcb59173bb2cb18f430`. Collector HTTP accepted spans increased 1→2; independent Langfuse, LGTM, and MLflow sent-span counters each increased 4→5; receiver failed/refused counters remained zero.
- **R6 — final clean cohort:** the first 20/20-sample, 600-second clean window passed. After credential rotation and fresh ClickHouse initialization, a second final 20/20-sample, 600-second window also passed with web, worker, Redis, ClickHouse, and LGTM continuously running/healthy, restart counts zero, and relevant Redis-version, Redis-command, BullMQ, socket-timeout, lock-renewal, stalled-job, and reconnect lines zero.
- **R7 — ClickHouse incident response:** a local diagnostic exposed the then-current ClickHouse application credential. No value is retained. The application user could not alter itself, so explicit greenfield/no-old-data authority was used to replace only ClickHouse and its versioned volume with a fresh unprinted credential, recreate web/worker against it, rerun all 46 migrations, verify `events_core` and `events_full`, and rerun composite, fan-out, restart, and final clean-window gates. Every other stateful volume was preserved.
- **R8 — retained deployment at acceptance:** the final `tdt-local-full`, `tdt-local-full-agent-core`, and `tdt-local-full-tdt-scheduler` projects were left running at the accepted checkpoint. Final recorded identities were web `673a675f65d5`, worker `e95473b326f0`, Redis `f2609d5470f2`, ClickHouse `afcd577b1cc4`, LGTM `d4e7cf33f2c0`, gateway `bfe1b1bfc689`, and MLflow `5404f1c2f4d5`; every recorded restart count was zero. Omniroute was not touched.

### Current operator state after archive

- **O1 — intentional resource pause:** on 2026-08-25 the operator authorized shutdown of the three stable TDT projects after implementation, archive, documentation, and cleanup completed. Diagnostics immediately before shutdown showed all 15 TDT containers running, every configured healthcheck healthy, and restart counts zero.
- **O2 — ownership-scoped teardown:** scheduler, observability/backends, and agent-core were brought down in reverse dependency order with exact Docker-recorded Compose inputs, `down --remove-orphans`, and no `-v`. No `tdt-local-full*` container or network remains.
- **O3 — state retained:** all eight named TDT volumes, pinned images, the protected operator environment, and Omniroute remain preserved. No image, volume, credential file, build cache, or foreign resource was removed.
- **O4 — interpretation:** R1–R8 remain authoritative evidence for their dated accepted cohort. O1–O3 supersede only claims that those processes are currently running. A later restart requires a fresh current-state verification; retained volumes and cached images alone are not readiness evidence.

## Requirement and scenario mapping

### `tdt-compose-operational-readiness`

#### Requirement: Latest Langfuse dependency deviations pass behavioral acceptance

| Scenario | Source | Tests | Docs | Runtime | Verdict |
|---|---|---|---|---|---|
| Langfuse latest-image cohort passes | S1, S2, S4 | T1-T3 | D1, D2 | R1, R5, R6 | PASS |
| Fixed timeout policy is paired and non-overridable by planning inputs | S1 | T1, T2, T4 | D1, D2 | R1, R6 | PASS |
| Redis interruption recovery is bounded | S2, S3 | T1, T3 | D1-D3 | R3-R5 | PASS |
| Deviation evidence is health-only | S2, S3 | T3 | D1, D2 | R1, R5; health alone was not used | PASS |
| Local resource pressure would starve readiness timers | S4 | T1, T2 | D2 | R1, R6 | PASS |
| Worker liveness or queue readiness fails | S2, S3 | T3 | D1, D2 | R4 demonstrated non-ready while worker stayed live | PASS |

#### Requirement: Langfuse OTLP fan-out remains exact and independently evidenced

| Scenario | Source | Tests | Docs | Runtime | Verdict |
|---|---|---|---|---|---|
| Exact event and fan-out evidence passes | S5 | T1, T4 | D1, D2 | R5 | PASS |
| Event or fan-out evidence is incomplete | S3, S5 | T3, T4 | D1, D2 | R5 independently satisfied every required signal | PASS |

### `tdt-observability-docker-deployment`

#### Requirement: Langfuse worker readiness is queue-aware and externally composite

| Scenario | Source | Tests | Docs | Runtime | Verdict |
|---|---|---|---|---|---|
| Worker queue and composite readiness pass | S1-S3 | T1-T3 | D1, D2 | R1, R6 | PASS |
| Worker queue consumption is stuck | S2, S3 | T3 | D1 | R1 proved enabled workers and `stuck=false`; fail-closed negative paths are tested | PASS |
| Redis is only started | S1-S3 | T2, T3 | D1 | R1 required Docker health and authenticated PING, not running-only state | PASS |
| Worker remains live during a Redis interruption | S2, S3 | T3 | D2 | R4 | PASS |
| Composite recovery requires consecutive passes | S2, S3 | T3 | D1, D2 | R4, R5 | PASS |

#### Requirement: Redis 8 and ClickHouse 26 compatibility is proven with Langfuse

| Scenario | Source | Tests | Docs | Runtime | Verdict |
|---|---|---|---|---|---|
| Redis 8 compatibility passes | S1-S3 | T1-T3 | D1, D2 | R1, R3-R6 | PASS |
| BullMQ version gate is evaluated explicitly | S1, S3 | T2, T4 | D1, D2 | R1, R6 | PASS |
| ClickHouse 26 compatibility passes | S1, S4, S5 | T1, T2, T4 | D2, D3 | R5-R7 | PASS |
| Compatibility deviation fails | S2, S3 | T3 | D1-D3 | R4 proved failure dominance; final cohort later passed | PASS |

#### Requirement: Backend credentials and Collector configuration fail closed

| Scenario | Source | Tests | Docs | Runtime | Verdict |
|---|---|---|---|---|---|
| Langfuse OTLP authentication succeeds | S5 | T1, T4 | D1, D2 | R5 | PASS |
| Required backend credential is missing | S3 | T4 | D1 | Fail-closed preflight is tested; final protected inputs were present without value capture | PASS |
| A backend credential is exposed during diagnostics | D3 operational policy | T1 evidence/redaction contracts | D2, D3 | R7 | PASS |
| Collector config uses unsupported syntax | S5 | T4 | D1, D2 | R5 and gateway readiness passed under the pinned Collector | PASS |

## OpenSpec workflow gates

- Selected strict validation: **PASS** — 1/1 change valid, zero issues.
- Archive-readiness validator: **PASS** — 13/13 tasks, 2 delta specs, all required artifacts, zero errors or warnings.
- Delta/main comparison and sync: **PASS** — all 5 selected requirement blocks match the two main specs; strict specs-wide validation passed 376/376.
- Supported archive: **PASS** — archived as `openspec/changes/archive/2026-08-25-harden-langfuse-worker-readiness`; OpenSpec confirmed both specs were already in sync.
- Archive/spec/report store commit: **PASS** — committed as `890912f667045f2b31f583d85eba0aa99760ea92`; this post-archive update only finalizes the report's cleanup ledger.

These are ordered lifecycle operations, not implementation gaps. Tasks 4.1 and 4.2 are complete after final validation and the exact pre-archive ownership review; sync, archive, and the store commit now finalize the lifecycle.

## Warnings and accepted exceptions

1. **GitNexus unavailable/stale:** exact implementation commits, direct diffs, focused and full test results, runtime evidence, and independent exact-commit review are authoritative. The current pre-commit retry first encountered duplicate registered repo names; the prescribed absolute-path call then ended with the MCP connection closing. No fresh GitNexus success is claimed.
2. **Security reset exception:** no volume was removed during the ordinary timeout correction or either Redis fault proof. One ClickHouse volume was intentionally reset only for credential-incident response under explicit no-old-data authority; this is not generalized into a claim that every volume was preserved.
3. **Pre-existing mypy diagnostics:** module-wide diagnostics outside changed lines remain in `stack.py` and `evidence.py`; changed-line strict mypy was clean.
4. **Initial Docker resource starvation:** early runtime delays were diagnosed as contention from unbounded LGTM and ClickHouse work on the 8-vCPU Docker Desktop baseline. The final 1.0/1.5 CPU limits, bounded ClickHouse healthcheck, final composite, and two clean windows close this change's readiness risk without making a general production-sizing claim.
5. **Knowledge tooling:** canonical Graphify output was refreshed, de-duplicated, and committed at `1094a9ed06a2597350ab33d325cc9677cc37f88d`. GitNexus remains stale because incremental analysis hit duplicate embedding primary key `Function:src/tdt_observability/cli.py:main:0`; its bounded FTS repair succeeded, but no fresh GitNexus pass is claimed.

## Archive disposition

Implementation, documentation, accepted runtime verification, selected strict validation, archive readiness, spec synchronization, and supported archive are **PASS**. The archived change is retained at `openspec/changes/archive/2026-08-25-harden-langfuse-worker-readiness`. Its behavioral conclusions remain valid after the separately authorized operator pause because teardown followed the normative volume-preserving ownership boundary. Current runtime readiness is intentionally not claimed while the TDT projects are stopped; a later restart requires fresh verification. Omniroute, unrelated changes/worktrees, credentials, images, and all TDT volumes remain outside retirement scope.
