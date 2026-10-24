# Tasks

## 1. Align Docker Compose Override & Runtime Entrypoint Normalization

- [x] 1.1 Update `/Users/androidteam/Omniroute/docker-compose.override.yml` to add `- OMNIROUTE_SQLITE_SLOW_MS=200` under `services.omniroute-base.environment` (relying on `docker-compose.yml` `x-common` for `stop_grace_period: 40s`) while keeping `git -C /Users/androidteam/Omniroute status --untracked-files=no` clean.
- [x] 1.2 Update `/Users/androidteam/Omniroute/scripts/container-entrypoint-compat.sh` (and comments in `/Users/androidteam/Omniroute/scripts/ensure-muse-wire-compat.sh`) to idempotently normalize `/app/.build/next/server/chunks/*.js` so `isGeminiTrailingModelTurnRejectingModel` matches `gemini-[34]*`, `MODEL_ACCESS_DENIED_PATTERNS` / `isModelScoped400` / `isProviderModelUnsupported400` exclude `\bmodel(?!\s+turn\b)` across `32946.js` and `55661.js`, and `lockModelIfPerModelQuota` routes `"agy"` to `lockExactModel`.

## 2. Apply Container Update, Unify Cache Config & Verify `gemini-4-argon` Resilience

- [x] 2.1 Recreate the `omniroute` container via `docker compose --profile base up -d --no-build` in `/Users/androidteam/Omniroute`, align `PATCH /api/settings/database` `.cache` (`semanticCacheMaxSize: 1000`, `semanticCacheTTL: 18000000`), verify `docker exec omniroute /app/container-entrypoint-compat.sh --patch-only` outputs `already_ok`, and verify `GET /api/resilience/model-cooldowns` and `GET /api/rate-limits` report zero `family:gemini` lockouts on `338764b8` and `0532bad4`.
- [x] 2.2 Send a multi-turn inference probe ending with an assistant turn (`role: "assistant"`) to `http://127.0.0.1:20128/v1/chat/completions` and `http://127.0.0.1:20128/v1/responses` with `model: "gemini-4-argon"` and `model: "gemini-4-argon-high"`, verifying HTTP 200 responses, zero `family:gemini` lockouts in `GET /api/resilience/model-cooldowns`, and healthy `~/.local/bin/omniroute health --json` output.
