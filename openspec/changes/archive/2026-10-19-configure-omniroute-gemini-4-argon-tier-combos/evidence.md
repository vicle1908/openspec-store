# Verification Evidence: `configure-omniroute-gemini-4-argon-tier-combos`

## 1. Pre-Flight Snapshot & Manual Model Removal (Tasks 1.1 & 1.2)

- **Pre-Mutation Snapshots**:
  - `/tmp/omniroute-combos-pre-argon-tiers.json` (`0600`, `13481` bytes, top-level keys `["active", "combos", "error"]` from `~/.local/bin/omniroute combo list --output json`).
  - `/tmp/omniroute-agy-models-pre-argon-tiers.json` (`0600`, `23693` bytes, captured prior to Task `1.2` at `created: 1792400202` from `GET /api/provider-models` and `~/.local/bin/omniroute models agy --output json`, containing the pre-mutation `source: "manual"` `gemini-4-argon` override under `agy` and all `39` `agy` catalog entries).
- **OmniRoute Tracked Files Cleanliness**:
  - `git -C /Users/androidteam/Omniroute status --short --untracked-files=no` → empty (`omniroute-tracked-files-clean`).
- **Manual `agy/gemini-4-argon` Custom Model Removal**:
  - Command: `~/.local/bin/omniroute models remove agy gemini-4-argon --yes`
  - Result: `action=remove | persistenceVerified=true | provider=agy | modelId=gemini-4-argon`.
  - Verified `GET http://127.0.0.1:20128/api/provider-models` has `0` entries for `gemini-4-argon` under `agy`.
  - Verified `GET http://127.0.0.1:20128/v1/models` advertises `gemini-4-argon`, `gemini-4-argon-high`, `gemini-4-argon-medium`, and `gemini-4-argon-low` with `owned_by: "combo"` and `custom: null`.

## 2. OmniRoute Combo Reconciliation & Tier Provisioning (Tasks 2.1 – 2.4)

### 2.1 Provisioned Combos (`GET /api/combos`)

| Combo Name | Combo ID | HTTP Action | Strategy | `context_cache_protection` | `candidatePool` | `resetAwareQuotaCacheTtlMs` | Step 1 (`338764b8-1cd7-4946-b789-ee5dad4c5073` / `vinhghtk1908@gmail.com`) | Step 2 (`0532bad4-2486-4286-8f06-510e9c678620` / `vinhvumobile@gmail.com`) |
|---|---|---|---|---|---|---:|---|---|
| `gemini-4-argon` | `f1cefc64-7662-4f0a-9234-84f70603cbe4` | `PATCH 200` | `auto` | `false` | `["agy"]` | `300000` | `agy/gemini-4-argon-high` | `agy/gemini-4-argon-high` |
| `gemini-4-argon-high` | `f7a7ff33-44bd-427a-957f-0774227e12ed` | `POST 201` | `auto` | `false` | `["agy"]` | `300000` | `agy/gemini-4-argon-high` | `agy/gemini-4-argon-high` |
| `gemini-4-argon-medium` | `4dc53616-dad7-4c51-8d09-067fec4d51d8` | `POST 201` | `auto` | `false` | `["agy"]` | `300000` | `agy/gemini-4-argon-medium` | `agy/gemini-4-argon-medium` |
| `gemini-4-argon-low` | `bafa3f44-dc5f-4bf3-8d0f-13a2fe078e5c` | `POST 201` | `auto` | `false` | `["agy"]` | `300000` | `agy/gemini-4-argon-low` | `agy/gemini-4-argon-low` |

### 2.2 Combo Target Health Checks (`POST /api/combos/test`)

| Combo Name | Resolved By | Step 1 (`338764b8` / `vinhghtk1908@gmail.com`) | Step 2 (`0532bad4` / `vinhvumobile@gmail.com`) |
|---|---|---|---|
| `gemini-4-argon` | `agy/gemini-4-argon-high` | `status: "ok"`, `13635ms`, `"pong"` | `status: "ok"`, `12919ms`, `"pong"` |
| `gemini-4-argon-high` | `agy/gemini-4-argon-high` | `status: "ok"`, `8696ms`, `"pong"` | `status: "ok"`, `22905ms`, `"pong"` |
| `gemini-4-argon-medium` | `agy/gemini-4-argon-medium` | `status: "ok"`, `55298ms`, `"pong"` | `status: "ok"`, `26320ms`, `"pong"` |
| `gemini-4-argon-low` | `agy/gemini-4-argon-low` | `status: "ok"`, `26322ms`, `"pong"` | `status: "ok"`, `13547ms`, `"pong"` |

### 2.3 Dual-Protocol & Tool-Calling Verification (`POST /v1/responses` & `POST /v1/chat/completions`)

| Combo | Protocol | HTTP Status | `X-OmniRoute-Combo-Trace` | `X-OmniRoute-Selected-Connection-Id` | `X-OmniRoute-Decision` | Upstream Model | Output |
|---|---|---:|---|---|---|---|---|
| `gemini-4-argon` | `POST /v1/chat/completions` | `200` | `combo-ff54080f-e158-4cab-8215-462fb68243e5` | `338764b8-1cd7-4946-b789-ee5dad4c5073` | `strategy=auto; provider=antigravity; latency_ms=4954` | `gemini-4-argon-high` | `"pong"` |
| `gemini-4-argon` | `POST /v1/responses` | `200` | `combo-e07c2c5c-28b3-4549-8b41-925bef0288b3` | `338764b8-1cd7-4946-b789-ee5dad4c5073` | `strategy=auto; provider=antigravity; latency_ms=12972` | `gemini-4-argon-high` | `"pong"` |
| `gemini-4-argon-high` | `POST /v1/chat/completions` | `200` | `combo-d55eb914-db5d-4b89-baab-77830a516277` | `338764b8-1cd7-4946-b789-ee5dad4c5073` | `strategy=auto; provider=antigravity; latency_ms=10287` | `gemini-4-argon-high` | `"pong"` |
| `gemini-4-argon-high` | `POST /v1/responses` | `200` | `combo-9f7c067f-e372-4965-be0e-c90d763987b6` | `338764b8-1cd7-4946-b789-ee5dad4c5073` | `strategy=auto; provider=antigravity; latency_ms=4240` | `gemini-4-argon-high` | `"pong"` |
| `gemini-4-argon-medium` | `POST /v1/chat/completions` | `200` | `combo-cbd1e3c1-d5c5-46b1-b426-7301ba1f6ba7` | `0532bad4-2486-4286-8f06-510e9c678620` | `strategy=auto; provider=antigravity; latency_ms=4149` | `gemini-4-argon-medium` | `"pong"` |
| `gemini-4-argon-medium` | `POST /v1/responses` | `200` | `combo-8a9d3d80-da58-405e-a6a6-077b1c6ae663` | `0532bad4-2486-4286-8f06-510e9c678620` | `strategy=auto; provider=antigravity; latency_ms=2487` | `gemini-4-argon-medium` | `"pong"` |
| `gemini-4-argon-low` | `POST /v1/chat/completions` | `200` | `combo-5492144e-d4e3-406d-905d-cba7e9a6b209` | `338764b8-1cd7-4946-b789-ee5dad4c5073` | `strategy=auto; provider=antigravity; latency_ms=8672` | `gemini-4-argon-low` | `"pong"` |
| `gemini-4-argon-low` | `POST /v1/responses` | `200` | `combo-ac681057-3bb0-43db-8555-760a386ca29e` | `338764b8-1cd7-4946-b789-ee5dad4c5073` | `strategy=auto; provider=antigravity; latency_ms=4558` | `gemini-4-argon-low` | `"pong"` |

- `POST /v1/responses` Tool-Calling (`gemini-4-argon-high`):
  - Turn 1 (`echo_tool`): `id=resp_chatcmpl-1792404454901-fedcd9b7`, `status=completed`, `output=[{"type":"function_call","name":"echo_tool","arguments":"{\"msg\":\"combo-ok\"}"}]`
  - Turn 2 (`function_call_output` continuation): `id=resp_chatcmpl-1792404458303-3d93cab9`, `status=completed`, `text="echo_tool was called with msg=\"combo-ok\" and returned: echoed: combo-ok."`

## 3. OMP Catalog & Fallback Chain Synchronization (Tasks 3.1 & 3.2)

### 3.1 Isolated Profile Smoke Gate (`~/.omp/profiles/argon-tiers-smoke/agent`, `retry: {fallbackChains: {}}`)

| Selector | Exit Code | Provider | Serving Model | Output | Duration (ms) | Reasoning Tokens | Fallbacks |
|---|---:|---|---|---|---:|---:|---:|
| `omniroute/gemini-4-argon` | `0` | `omniroute` | `gemini-4-argon` | `pong` | `5336` | `25` | `0` |
| `omniroute/gemini-4-argon-high` | `0` | `omniroute` | `gemini-4-argon-high` | `pong` | `5294` | `18` | `0` |
| `omniroute/gemini-4-argon-medium` | `0` | `omniroute` | `gemini-4-argon-medium` | `pong` | `28604` | `19` | `0` |
| `omniroute/gemini-4-argon-low` | `0` | `omniroute` | `gemini-4-argon-low` | `pong` | `7365` | `20` | `0` |

### 3.2 Live OMP Catalog & Clean-Shell Attribution Verification

- **Catalog (`omp models --json`)**:
  - Confirmed `omniroute/gemini-4-argon`, `omniroute/gemini-4-argon-high`, `omniroute/gemini-4-argon-medium`, and `omniroute/gemini-4-argon-low` are registered with `reasoning: true`, `contextWindow: 1000000`, `maxTokens: 128000`.
- **Live Clean-Shell Attribution Probes (`zsh -lc 'omp --no-prewalk --mode json --no-session --model "<selector>" -p "reply only: pong"'`)**:

| Selector | Exit Code | Provider | Serving Model | Output | Duration (ms) | Reasoning Tokens | Fallbacks |
|---|---:|---|---|---|---:|---:|---:|
| `omniroute/gemini-4-argon` | `0` | `omniroute` | `gemini-4-argon` | `pong` | `7342` | `23` | `0` |
| `omniroute/gemini-4-argon-high` | `0` | `omniroute` | `gemini-4-argon-high` | `pong` | `4997` | `21` | `0` |
| `omniroute/gemini-4-argon-medium` | `0` | `omniroute` | `gemini-4-argon-medium` | `pong` | `5566` | `20` | `0` |
| `omniroute/gemini-4-argon-low` | `0` | `omniroute` | `gemini-4-argon-low` | `pong` | `5194` | `20` | `0` |

- **Cleanup & Integrity**:
  - Removed throwaway profile `~/.omp/profiles/argon-tiers-smoke`.
  - Retained timestamped backups `~/.omp/agent/models.yml.bak.1792404489` and `~/.omp/agent/config.yml.bak.1792404489`.
  - Verified `~/.omp/agent/agent.db` MD5 unchanged.
