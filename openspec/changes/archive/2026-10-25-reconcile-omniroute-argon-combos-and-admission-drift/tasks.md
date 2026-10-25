# Tasks

## 1. Pre-Mutation Snapshots & Combo / Alias Reconciliation

- [x] 1.1 Capture pre-mutation rollback snapshots (`GET /api/combos`, `GET /api/settings/combo-defaults`, `GET /api/settings/feature-flags`, `GET /api/models/alias`, `PUT /api/db-backups`, and backups of `/Users/androidteam/Omniroute/.env`, `~/.codex/cockpit-model-catalog.json`, and `~/.codex/config.toml`).
- [x] 1.2 Update `gemini-4-argon` (`f1cefc64-7662-4f0a-9234-84f70603cbe4`), `gemini-4-argon-high` (`f7a7ff33-44bd-427a-957f-0774227e12ed`), `gemini-4-argon-medium` (`4dc53616-dad7-4c51-8d09-067fec4d51d8`), and `gemini-4-argon-low` (`bafa3f44-dc5f-4bf3-8d0f-13a2fe078e5c`) via `GET /api/combos/{id}` -> merge `config` -> `PUT /api/combos/{id}` to add explicit `"label"` values (`"vicgnome19094@gmail.com"`, `"vinhvumobile@gmail.com"`, `"vinhghtk1908@gmail.com"`) on all 3 Ultra account steps and `"targetTimeoutMs": 25000` in `config` while preserving `strategy: "auto"`, `context_cache_protection: false`, and existing `config` fields.
- [x] 1.3 Update `muse-spark-1.3` (`453c5dd3-f7f4-4c44-bd4b-6c3c1d0f4e5b`) and `PATCH /api/settings/combo-defaults` to include `"targetTimeoutMs": 25000`, set `context_length: 1000000` and `context_cache_protection: false` on `kimi-k3.1-pro` and `deepseek-v4.1-flash`, and remove the stale `gemini-4-argon` -> Nexus (`nx`) alias from `/api/models/alias`.

## 2. Heavyweight Chat Admission Concurrency & Composite-Combo Prune Protection

- [x] 2.1 Set `COMBO_AUTO_PRUNE_STALE_STEPS` to `"false"` via `PUT /api/settings/feature-flags` (`{"key": "COMBO_AUTO_PRUNE_STALE_STEPS", "value": "false"}`) and restore `claude-opus-5.5` (`4b2430da-0b3b-4b0e-9773-ec0f97adc252`, `context_length: 1000000`) with its 8 active `agy` steps ahead of `combo-ref: gemini-3.8-flash-high`.
- [x] 2.2 Update `/Users/androidteam/Omniroute/.env` to set `OMNIROUTE_CHAT_MAX_HEAVY_IN_FLIGHT=16` and `OMNIROUTE_CHAT_ADMISSION_QUEUE_MS=15000`, recreate `omniroute-base` (`docker compose --profile base up -d --no-build --pull never --no-deps --force-recreate omniroute-base`), and verify `GET /api/monitoring/health` reports `chatAdmission.countCapEnabled === true`, `chatAdmission.maxInflightBytes === 137363456`, and zero `503 chat_admission_busy` rejections across concurrent tool-bearing subagent probes on `gemini-4-argon*` and `gemini-3.8-flash-high`.

## 3. Codex Catalog Restoration, Canonical Spec Sync & Verification

- [x] 3.1 Restore `context_window: 1000000`, `max_context_window: 1000000`, `auto_compact_token_limit: 800000`, `prefer_websockets: false`, neutral `base_instructions`, and tier-matched `default_reasoning_level` (`high`, `medium`, `low`) on the 4 `gemini-4-argon*` entries in `~/.codex/cockpit-model-catalog.json`, and tighten `~/.codex/config.toml` permissions to `0600` (`stat -L -f "%04Lp"`).
- [x] 3.2 Update `wiki/entities/omniroute.md`, `wiki/concepts/omniroute-gemini-4-argon-fleet-routing.md`, and `openspec/changes/reconcile-omniroute-argon-combos-and-admission-drift/evidence.md` with full verification output, and validate with `openspec validate reconcile-omniroute-argon-combos-and-admission-drift --strict --json --store openspec-store`.
