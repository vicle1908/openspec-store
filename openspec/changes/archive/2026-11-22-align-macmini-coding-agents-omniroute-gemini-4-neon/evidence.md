# Verification Evidence: align-macmini-coding-agents-omniroute-gemini-4-neon

**Change Name:** `align-macmini-coding-agents-omniroute-gemini-4-neon`  
**Store:** `openspec-store` (`/Users/androidteam/Developer/platform/openspec-store`)  
**Execution Node:** `iosteam-mac-mini` (Darwin 27.0.0 arm64)  
**Timestamp:** `2026-11-22T05:45:00Z`

---

## 1. Safety Backup Verification

- **Backup Directory:** `~/.omniroute/backups/align-macmini-coding-agents-omniroute-gemini-4-neon/20261122T043316Z/` (mode `0700`)
- **Manifest File:** `SHA256SUMS` (mode `0600`) containing exact SHA-256 hashes of 20 pre-edit configuration files.

---

## 2. OmniRoute SQLite Gateway Verification

- **Database:** Docker volume `/app/data/storage.sqlite`
- **Combos Query:**
  ```sql
  SELECT name, data FROM combos WHERE name LIKE 'gemini-4-neon%';
  ```
  Verified: `gemini-4-neon`, `gemini-4-neon-high`, `gemini-4-neon-medium`, and `gemini-4-neon-low` all declare `strategy = "quota-weighted"` with `config.quotaWeightedFloorPercent = 5`, `config.quotaWeightedScoring = "leftover"`, and `config.predictiveTtftMs = 0`.
- **Feature Flag Query:**
  ```sql
  SELECT namespace, key, value FROM key_value WHERE namespace = 'feature_flags' AND key = 'RESPONSES_TRANSPORT_KEEPALIVE_ENABLED';
  ```
  Verified: returns `{"namespace":"feature_flags","key":"RESPONSES_TRANSPORT_KEEPALIVE_ENABLED","value":"true"}`.
- **Runtime Reload:** Docker container `omniroute` restarted, in-memory `WeakMap` cache reloaded, `/api/health` returns HTTP 200.

---

## 3. Local OMP Auth-Broker (`:8765`) & Auth-Gateway (`:4000`)

- **LaunchAgents:**
  - `~/Library/LaunchAgents/local.shb.omp.auth-broker.plist` (listening on `127.0.0.1:8765`, exit code 0)
  - `~/Library/LaunchAgents/local.shb.omp.auth-gateway.plist` (listening on `127.0.0.1:4000`, `--no-auth`, exit code 0)
- **Local Credentials:** Synced 20 active Google Antigravity OAuth credentials into `~/.omp/agent/agent.db` and migrated to broker.
- **Model Endpoint Probe:**
  ```bash
  curl -sS http://127.0.0.1:4000/v1/models
  ```
  Verified: HTTP 200 advertising all native Google Antigravity models.
- **Direct Inference Probe 1 (`google-antigravity/gemini-2.5-flash`):**
  - Prompt: `Reply with exact word PONG and nothing else.`
  - Result: **HTTP 200** $\rightarrow$ `PONG` (latency: 2.18s).
- **Direct Inference Probe 2 (`google-antigravity/claude-opus-4-6`):**
  - Prompt: `Reply with exact word PONG and nothing else.`
  - Result: **HTTP 200** $\rightarrow$ `PONG` (latency: 2.52s).

---

## 4. OMP Base Configuration & Fallback Chains

- `~/.omp/agent/models.yml`:
  - `providers.omniroute`: added `headers.x-omniroute-no-memory: "true"` and `gemini-4-neon` (`contextWindow: 512000`, `maxTokens: 262144`).
  - `providers.omp`: added `baseUrl: http://127.0.0.1:4000/v1`, `api: openai-responses`, registering `gemini-4-neon`, `gemini-4-hydrogen`, `gemini-4-argon`, and `gemini-3.8-flash`.
- `~/.omp/agent/config.yml`:
  - `modelRoles.default = omniroute/gemini-4-neon`
  - `retry.fallbackChains["omniroute/gemini-4-neon"]` routes through local `:4000` Neon $\rightarrow$ Hydrogen $\rightarrow$ Argon $\rightarrow$ Flash.
- **Diagnostic Verification:**
  ```bash
  omp models --kind all
  omp models --json
  ```
  Verified: 0 fallback chain warnings; all target selectors resolve.

---

## 5. Host Coding Agent Fleet Default Cutover (512K/400K Compaction Limits)

- **Kimi Code** (`~/.kimi-code/config.toml`): `default_model = "omniroute/gemini-4-neon"`; registered `omp` and `omniroute` neon models.
- **Pi** (`~/.pi/agent/{settings.json,models.json}`): `defaultModel = "gemini-4-neon"`; subagent overrides for `scout`, `researcher`, `worker` set to `omniroute-responses/gemini-4-neon` (`high`).
- **OpenCode** (`~/.config/opencode/opencode.json`): `model = "omniroute-responses/gemini-4-neon"`; registered provider `omp` (`:4000`).
- **Goose** (`~/.config/goose/{config.yaml,custom_providers/custom_omniroute.json,custom_providers/custom_omp.json}`): `model = gemini-4-neon`, `GOOSE_CONTEXT_LIMIT = 512000`, `GOOSE_PLANNER_CONTEXT_LIMIT = 512000`; created `custom_omp.json` (mode `0600`).
- **Factory Droid** (`~/.factory/settings.json`): `sessionDefaultSettings.model = "custom:OmniRoute-Gemini-4-Neon-11"`; `compactionTokenLimitPerModel = 400000`.
- **Grok** (`~/.grok/config.toml`): `default = "omniroute-gemini-4-neon"`; registered `[model_providers.omp]` and `[subagents.models]`.
- **Zed IDE** (`~/.config/zed/settings.json`): `agent.default_model.model = "gemini-4-neon"`; added provider `omp` (`:4000`).
- **Auxiliary**: `~/.config/kilo/kilo.jsonc` (`omniroute-responses/gemini-4-neon`), `~/.cline/data/settings/providers.json` (`gemini-4-neon`), `~/.shb/.env` (`SHB_DEFAULT_MODEL=gemini-4-neon`).

---

## 6. Claude Code Launcher, Codex Catalog & Hermes Alignment

- `~/.claude/profiles/omniroute-pm.json`: `model = "gemini-4-neon"`, `ANTHROPIC_MODEL = "gemini-4-neon"`, added to `modelPicker.options`.
- `~/.codex/model-catalog.json`: Provisioned absolute model catalog exposing `gemini-4-neon` (512K), `hydrogen` (1M), `argon` (1M), and `carbon` (1M); preserved `~/.codex/config.toml` default on `gemini-4-hydrogen`.
- `~/.hermes/config.yaml`: Added `gemini-4-neon` combos under `providers.omniroute.models` and `agent.reasoning_overrides`; preserved `moa:default` as primary preset.

---

## 7. Shell Environment, Switcher Helpers & Setup Script Parity

- `~/.zshenv`: Added `: "${GOOSE_MODEL:=gemini-4-neon}"`, `: "${GOOSE_CONTEXT_LIMIT:=512000}"`, and `: "${GOOSE_AUTO_COMPACT_TOKEN_LIMIT:=400000}"`.
- `~/.zshrc`: Updated `omniroute()` launcher; added `switch-model-neon`, `switch-model-hydrogen`, `switch-model-argon`, `switch-model-carbon`, `switch-model-flash`, `switch-gateway-omniroute`, `switch-gateway-omp`, `_sync_goose_limits`, `_claude_omp`, and CLI shortcuts (`omp-neon`, `pi-neon`, `grok-neon`, etc.).
- `setup-macbook-omniroute-client.sh`: Added all 5 `gemini-4-neon*` combos; verified `--check` passes with exit code 0; synced across `~/Developer/scripts/` and `platform/openspec-store/scripts/` (identical SHA-256: `b94a6bd8de0b...`).
- Syntax verification: `zsh -n ~/.zshenv ~/.zshrc` exit 0.

---

## 8. Live Real End-to-End Inference Calls

1. `POST http://localhost:20128/v1/chat/completions` with `gemini-3.8-flash-high`: **HTTP 200** $\rightarrow$ `PONG`.
2. `POST http://127.0.0.1:4000/v1/chat/completions` with `google-antigravity/gemini-2.5-flash`: **HTTP 200** $\rightarrow$ `PONG`.
3. `POST http://127.0.0.1:4000/v1/chat/completions` with `google-antigravity/claude-opus-4-6`: **HTTP 200** $\rightarrow$ `PONG`.
4. `omp --model omniroute/gemini-3.8-flash-high -p "Reply with exact word PONG and nothing else."`: **Success** $\rightarrow$ `PONG`.
5. `omp --model omp/gemini-3.8-flash -p "Reply with exact word PONG and nothing else."`: **Success** $\rightarrow$ `PONG` (walked fallback chain).
