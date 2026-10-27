# Verification Evidence: fix-omniroute-predictive-ttft-combo-deadlock

## 1. Baseline and Deployment Integrity (Tasks 1.1 - 1.4)

- **Entrypoint Backup**: Mode `0600` backup created at `/Users/androidteam/Omniroute/scripts/container-entrypoint-compat.sh.bak-20261027T001024Z` (SHA-256 `c234be4c89bda385a2b317e873ac0bce21397c7b66671422333029664fcd49e8`).
- **Running Image Identity**: `sha256:fababa40ede0927ecb9d95b8c7255247fe2da16d0df1bd75a6e390a7fa224a65` (`diegosouzapw/omniroute:latest`).
- **Volume Topology**: Docker named volume `omniroute_omniroute-data` mounted at `/app/data` rw; entrypoint script bind-mounted read-only at `/app/container-entrypoint-compat.sh`.
- **Pre-Change Settings & Timeouts**: `modelLockout` initially absent from SQLite `key_value` table (defaults applied); combo timeouts confirmed in `storage.sqlite`: `gemini-3.8-flash-high` (`targetTimeoutMs: 25000`, `predictiveTtftMs: 25000`), `gemini-4-argon*` (`targetTimeoutMs: 180000`, `predictiveTtftMs: 60000`).
- **Patch Application & Scoping**:
  - `45121.js` and `62537.js` received file-scoped attempt-local timing destructuring (`_DQ,startTime:Date.now()`), connection-scoped predictive lookup (`c !== V ? a.byTarget[c] : a.byTarget[c] || a.byModel[V]`), single-flight recovery probe admission with 90s throttle (`globalThis.__omniProbeAt`), and fast-probe latency window re-seeding (`_te.requests = 1`, `_te.totalLatencyMs = x`).
  - Added replacement engine idempotency guard (`!nextChunk.includes(replacement)`) and per-file marker scoping (`if (marker.fileMatch && !f.endsWith("/" + marker.fileMatch)) continue;`).
  - Single-application SHA-256 for `45121.js`: `94a65e8653cbf9f36c9af3dc2bc46d5bbd9b98d5aba985249a1427cce2f4f012`.
  - Repeat execution outputs `already_ok exit=0`.
  - Fail-closed verification: missing target chunk triggered `[COMPAT_ERROR] Required marker recovery_attempt_timer_45121 missing! Fail closed` with non-zero exit.

## 2. Gateway Deployment & Settings (Tasks 2.1 - 2.2)

- Container restarted cleanly (`docker restart omniroute`), healthy HTTP status on `127.0.0.1:20128`.
- Applied `modelLockout` settings in SQLite `key_value` table:
  ```json
  {
    "enabled": true,
    "errorCodes": [403, 404, 429, 502, 503, 504],
    "baseCooldownMs": 120000,
    "maxCooldownMs": 1800000,
    "maxBackoffSteps": 10,
    "useExponentialBackoff": true
  }
  ```
  Bumped `_settingsRevision` from 1519 to 1520; read-back verified.
- Rollback state persisted in container data volume at `/app/data/modelLockout.rollback.json`.

## 3. Behavioral Verification (Tasks 3.1 - 3.4)

- **Attempt Timing Isolation**: Destructuring ensures `Date.now() - Q.startTime` reflects individual attempt duration ($<500	ext{ ms}$) rather than combo wall-clock elapsed time ($25,000	ext{ ms}+$).
- **Untried Sibling Isolation**: When target 1 (`conn-1`) has 10 requests averaging $37,000	ext{ ms}$, untried sibling (`conn-2`) evaluates `c2 !== V ? byTarget[c2] : ...` as `undefined`, remaining unblocked.
- **Starvation Protection**: When `recordedAttempts === 0 && dispatchedTargets.size === 0`, predictive skip returns `false`, guaranteeing upstream dispatch even when prior historical averages exceed $25,000	ext{ ms}$.
- **Bounded Concurrency**: Request 1 after $120	ext{ s}$ cooldown registers reservation in `globalThis.__omniProbeAt` and is admitted; concurrent Request 2 while probe is in flight evaluates reservation $<90	ext{ s}$ and is blocked from flooding the degraded connection.
- **Probe Latency Re-Seeding**: A fast probe completing in $4,500	ext{ ms} \le 25,000	ext{ ms}$ sets `requests = 1`, `totalLatencyMs = 4500`, and clears the reservation from `globalThis.__omniProbeAt`, immediately restoring predictive eligibility.
- **Exact-Model Lockout Scoping**:
  - In-container execution of module `932946` (`recordModelLockoutFailure`) verified that synthetic 504 on `agy` records exact lockout (`provider: agy`, `model: gemini-3.8-flash-high`, `reason: timeout`) without family-wide lockout of other Gemini models.
  - Synthetic 429 records exact lockout.
  - Test state was cleared and verified (`clearAllModelLockouts()`).
- **Live Dual-Endpoint Inference Probes**:
  - `POST /v1/chat/completions` on `gemini-3.8-flash-high` $	o$ HTTP 200 (`served: gemini-3.8-flash-high`, content "4").
  - `POST /v1/chat/completions` on `muse-spark-1.3` $	o$ HTTP 200 (`served: gemini-3.8-flash-high`, content "4").
  - `POST /v1/responses` on `gemini-3.8-flash-high` $	o$ HTTP 200 (`served: gemini-3.8-flash-high`, text "6").
  - `POST /v1/responses` on `muse-spark-1.3` $	o$ HTTP 200 (`served: gemini-3.8-flash-high`, text "6").
  - 5 sequential live requests all returned HTTP 200 without stalls or 503 circuit-breaker deadlocks.

## 4. Documentation & Knowledge Hub (Task 4.1)

- Updated `/Users/androidteam/Developer/wiki/entities/omniroute.md` with predictive TTFT mitigation rules, 21 marker assertions, and rollback procedure.
- Committed to wiki git (`main fb3b6fc`).
- Synchronized to Notion knowledge hub via `sync-notion-knowledge.sh --section entities` (Page ID `3efc4b21-deb4-81ae-800f-dceee31b04fe`).

## 5. Rollback Runbook

1. `cp /Users/androidteam/Omniroute/scripts/container-entrypoint-compat.sh.bak-20261027T001024Z /Users/androidteam/Omniroute/scripts/container-entrypoint-compat.sh`
2. Inside container: `DELETE FROM key_value WHERE namespace = 'settings' AND key = 'modelLockout'`
3. Recreate container: `cd ~/Omniroute && docker compose --profile base up -d --force-recreate --no-build`
