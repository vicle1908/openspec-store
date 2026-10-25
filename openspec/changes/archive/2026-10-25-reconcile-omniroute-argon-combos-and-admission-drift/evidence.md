# Verification Evidence: reconcile-omniroute-argon-combos-and-admission-drift

## 1. Pre-Mutation Snapshots (Task 1.1)

Captured pre-mutation artifacts into `/tmp/omniroute-drift-snapshots/`:
- `combos.json` (`GET /api/combos`)
- `combo-defaults.json` (`GET /api/settings/combo-defaults`)
- `feature-flags.json` (`GET /api/settings/feature-flags`)
- `models-alias.json` (`GET /api/models/alias`)
- `cockpit-model-catalog.json.bak` (`~/.codex/cockpit-model-catalog.json`)
- `.env.pre-drift.bak` (`/Users/androidteam/Omniroute/.env`)
- Manual SQLite database snapshot via `PUT /api/db-backups`.

## 2. Gemini 4 Argon Combos Step Labels & Target Timeout (Task 1.2)

Updated all 4 `gemini-4-argon*` combos via `PUT /api/combos/{id}`:
- **`gemini-4-argon`** (`f1cefc64-7662-4f0a-9234-84f70603cbe4`):
  - `targetTimeoutMs`: `25000`
  - Step `[0]`: `62af823b-f3d7-4e6b-87a9-98069167d4f6` (`label: "vicgnome19094@gmail.com"`, `weight: 0`)
  - Step `[1]`: `0532bad4-2486-4286-8f06-510e9c678620` (`label: "vinhvumobile@gmail.com"`, `weight: 0`)
  - Step `[2]`: `338764b8-1cd7-4946-b789-ee5dad4c5073` (`label: "vinhghtk1908@gmail.com"`, `weight: 0`)
- **`gemini-4-argon-high`** (`f7a7ff33-44bd-427a-957f-0774227e12ed`):
  - `targetTimeoutMs`: `25000`, 3 steps with matching Ultra account labels.
- **`gemini-4-argon-medium`** (`4dc53616-dad7-4c51-8d09-067fec4d51d8`):
  - `targetTimeoutMs`: `25000`, 3 steps with matching Ultra account labels.
- **`gemini-4-argon-low`** (`bafa3f44-dc5f-4bf3-8d0f-13a2fe078e5c`):
  - `targetTimeoutMs`: `25000`, 3 steps with matching Ultra account labels.

## 3. Peripheral Combos & Defaults Alignment (Task 1.3)

- **`muse-spark-1.3`** (`453c5dd3-f7f4-4c44-bd4b-6c3c1d0f4e5b`): Added `targetTimeoutMs: 25000` to `config` while preserving `strategy: "priority"`, `nestedComboMode: "execute"`, and `context_cache_protection: false`.
- **`PATCH /api/settings/combo-defaults`**: Updated with `targetTimeoutMs: 25000`, `zeroLatencyOptimizationsEnabled: true`, `predictiveTtftMs: 25000`, `hedging: false`, `fallbackCompressionMode: "off"`.
- **`kimi-k3.1-pro` & `deepseek-v4.1-flash`**: Set `context_length: 1000000`, `context_cache_protection: false`, and `targetTimeoutMs: 25000`.
- **Stale Alias Removal**: Verified `GET /api/models/alias` no longer maps `gemini-4-argon` to Nexus `nx`.

## 4. Heavyweight Chat Admission Concurrency & Composite-Combo Prune Protection (Tasks 2.1 & 2.2)

- **Feature Flag**: Persisted `COMBO_AUTO_PRUNE_STALE_STEPS: "false"` in SQLite `feature_flags` via `PUT /api/settings/feature-flags` (`{"key": "COMBO_AUTO_PRUNE_STALE_STEPS", "value": "false"}`).
- **`claude-opus-5.5` Restored**: Restored all 8 active `agy` Opus accounts ahead of `combo-ref: gemini-3.8-flash-high` (`modelsCount: 9`, `nestedComboMode: "flatten"`, `targetTimeoutMs: 25000`, `context_length: 1000000`).
- **Heavyweight Admission Scaled**:
  - Set `OMNIROUTE_CHAT_MAX_HEAVY_IN_FLIGHT=16` and `OMNIROUTE_CHAT_ADMISSION_QUEUE_MS=15000` in `/Users/androidteam/Omniroute/.env`.
  - Recreated `omniroute-base` container.
  - Probed `GET /api/monitoring/health`:
    ```json
    {
      "activeHeavy": 3,
      "activeHealthyHeadroom": 0,
      "waiting": 0,
      "queuedBytes": 0,
      "shedTotal": 0,
      "maxInflightBytes": 137363456,
      "budgetSource": "v8_heap",
      "pressureSeverity": "normal"
    }
    ```
    Admitted 3 concurrent heavy requests without shedding (previously capped at 1).

## 5. Codex Catalog & Permissions Verification (Task 3.1)

- In `~/.codex/cockpit-model-catalog.json`, all 4 `gemini-4-argon*` entries verified with:
  - `context_window`: `1000000`
  - `max_context_window`: `1000000`
  - `auto_compact_token_limit`: `800000`
  - `prefer_websockets`: `false`
  - `default_reasoning_level`: `"high"` (`gemini-4-argon`, `gemini-4-argon-high`), `"medium"` (`gemini-4-argon-medium`), `"low"` (`gemini-4-argon-low`)
  - `base_instructions`: `null`
- Verified permissions: `stat -L -f '%04Lp' ~/.codex/config.toml` outputs `0600`.

## 6. Live Dual-Protocol Inference Verification

- Request to `gemini-4-argon-high` on `/v1/chat/completions`:
  ```json
  {"model":"gemini-4-argon-high","content":"PONG","usage":{"prompt_tokens":864,"completion_tokens":32,"total_tokens":896,"completion_tokens_details":{"reasoning_tokens":26}}}
  ```
  Status: `200 OK`, latency: `2.4s`, successful token reasoning output.
