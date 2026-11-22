# Design

## Context

See `proposal.md` for background and problem statement. This design governs the technical approach for bringing `iosteam-mac-mini` (the host workstation) into uniform configuration parity with `macbook-pro-m5` while maintaining local host operational constraints:

1. **OmniRoute Architecture on Host**:
   - OmniRoute `v3.8.54` runs locally inside Docker Compose (`~/Omniroute`, container `omniroute`) binding port `20128` (Next.js dashboard + `/v1`) and port `20129` (API bridge).
   - All `Macmini` client connections target `http://localhost:20128` or `http://127.0.0.1:20129` over loopback; traffic does not hairpin through Tailscale IP `100.70.16.83`.
   - `storage.sqlite` in named Docker volume `omniroute_omniroute-data` (`/app/data/storage.sqlite`) manages combo definitions and settings.
2. **Current Divergence from M5**:
   - `Macmini` clients still point default configurations to `gemini-4-hydrogen` (1M) or legacy routes, lacking `gemini-4-neon` across client pickers and shell helpers.
   - `Macmini` lacks the local OMP Auth-Gateway (`http://127.0.0.1:4000`) and broker (`:8765`), which on M5 provide a zero-latency fallback tier directly to Google Antigravity.
   - `gemini-4-neon` on OmniRoute currently uses `strategy: "priority"` (always hitting `desujedud378@gmail.com` first until 429), whereas `gemini-4-hydrogen` and `gemini-4-argon` use `strategy: "quota-weighted"`.
   - Feature flag `RESPONSES_TRANSPORT_KEEPALIVE_ENABLED` is missing from `storage.sqlite` `key_value` (`namespace = 'feature_flags'`, defaulting to `false`), causing long Responses streams to disconnect.

## Goals / Non-Goals

**Goals:**
- Tune OmniRoute `gemini-4-neon*` combos to `strategy: "quota-weighted"` and enable `RESPONSES_TRANSPORT_KEEPALIVE_ENABLED: true`.
- Provision and activate `local.shb.omp.auth-broker` (`:8765`) and `local.shb.omp.auth-gateway` (`:4000`) LaunchAgents on `Macmini`.
- Standardize OmniRoute-defaulting clients (OMP base profile, Kimi, Pi, OpenCode, Goose, Factory Droid, Grok, Zed, Claude Code `omniroute` launcher, Kilo, Cline, SHB env) on `gemini-4-neon` (`high` effort, `512K` context).
- Enforce `512K` context and `<=400K` auto-compaction limits for Neon on Goose, Factory Droid, and OpenCode.
- Expose all four Gemini 4 combos (`neon`, `hydrogen`, `argon`, selectable-only `carbon`) under `omniroute` and active models (`neon`, `hydrogen`, `argon`, `flash`) under local `omp`.
- Preserve specialized client boundaries: Codex CLI default remains `gemini-4-hydrogen` (`~/.codex/config.toml` / `omniroute.config.toml`), Hermes remains `moa:default`, and Claude Code global remains `shopapikey`.
- Align shell switchers, `_sync_goose_limits`, and `_claude_omp` subagent overrides in `~/.zshenv` and `~/.zshrc`.
- Protect all writes with timestamped mode-`0600` backups and SHA-256 manifests.

**Non-Goals:**
- Enabling unverified Google AI Ultra accounts on `gemini-4-carbon*`.
- Reconfiguring `macbook-pro-m5` or altering remote Tailscale endpoints.
- Switching Hermes default to a single provider model.
- Hairpinning `Macmini` local client requests through Tailscale network interfaces.

## Decisions

### Decision 1: Gateway SQLite Tuning via Better-SQLite3 Script
- **Choice**: Execute a targeted Node.js script inside the `omniroute` container to update `combos` and `key_value` in `/app/data/storage.sqlite`.
- **Transaction Boundary**:
  ```sql
  BEGIN IMMEDIATE;
  -- 1. Update gemini-4-neon combos to quota-weighted
  -- (data JSON: strategy='quota-weighted', config.quotaWeightedFloorPercent=5, config.quotaWeightedScoring='leftover', config.predictiveTtftMs=0)
  -- 2. Upsert RESPONSES_TRANSPORT_KEEPALIVE_ENABLED into key_value (feature_flags)
  INSERT INTO key_value (namespace, key, value)
  VALUES ('feature_flags', 'RESPONSES_TRANSPORT_KEEPALIVE_ENABLED', 'true')
  ON CONFLICT(namespace, key) DO UPDATE SET value = 'true';
  COMMIT;
  ```
- **Rationale**: In OmniRoute `40967.js` (`244714`), `isFeatureFlagEnabled()` reads `key_value` with `namespace = 'feature_flags'` and caches values per DB instance in a process-local `WeakMap`. Because an external SQLite script bypasses the in-process invalidator, Task 1.2 restarts the `omniroute` container (or applies the flag through OmniRoute's feature-flag API) after the transaction so the running server reloads the `WeakMap` cache.
- **Alternative Rejected**: Writing `namespace = 'settings'` or updating SQLite without flushing the runtime cache, which leaves `RESPONSES_TRANSPORT_KEEPALIVE_ENABLED` evaluated as `false` in memory.

### Decision 2: Provision Local OMP Auth-Broker and Gateway LaunchAgents
- **Choice**: Create two user LaunchAgent plists under `~/Library/LaunchAgents/`:
  - `local.shb.omp.auth-broker.plist`: runs `/opt/homebrew/bin/omp auth-broker serve --bind=127.0.0.1:8765`, working directory `/Users/androidteam/.omp`, standard output/error `/Users/androidteam/.omp/logs/auth-broker.log`.
  - `local.shb.omp.auth-gateway.plist`: runs `/opt/homebrew/bin/omp auth-gateway serve --bind=127.0.0.1:4000 --no-auth`, `OMP_AUTH_BROKER_URL=http://127.0.0.1:8765`, standard output/error `/Users/androidteam/.omp/logs/auth-gateway.log`.
- **Rationale**: `omp auth-gateway` allows local tools and fallback chains to access native Google Antigravity OAuth accounts (stored in `~/.omp/agent/agent.db`) via standard OpenAI Responses protocol on `http://127.0.0.1:4000/v1` without incurring OmniRoute overhead or rate-limit contention.
- **Alternative Rejected**: Running ad-hoc background screen or nohup processes. Rejected because LaunchAgents automatically recover after reboot or process crashes.

### Decision 3: Local Loopback Endpoint Preservation on Macmini
- **Choice**: All `Macmini` client configurations target `http://localhost:20128` (or `http://127.0.0.1:20129` for API bridge).
- **Rationale**: Routing local requests to `https://iosteam-mac-mini.tailc6b508.ts.net` incurs WireGuard encryption overhead, DNS resolution latency, and fails if the Tailscale daemon is temporarily paused. Loopback is zero-overhead and always available.

### Decision 4: 512K Compaction and Model Guardrails on Fleet
- **Choice**:
  - `omniroute/gemini-4-neon` context limit declared as `512,000` tokens across all client catalogs (`models.yml`, `models.json`, `opencode.json`, `config.yaml`, `custom_omniroute.json`, `settings.json`, `config.toml`).
  - Auto-compaction limits set to `<= 400,000` tokens (Goose `GOOSE_AUTO_COMPACT_TOKEN_LIMIT=400000`, Factory Droid `compactionTokenLimitPerModel: {"custom:OmniRoute-Gemini-4-Neon-11": 400000}`).
  - `gemini-4-carbon` exposed as selectable-only (`isActive: false` on OmniRoute); forbidden from all default models and fallback chains.
  - `gemini-3.8-flash-high` retained as auxiliary tier and terminal fallback leg.

### Decision 5: Shell Helper Convergence with Bug Remediation
- **Choice**:
  - Add `switch-model-neon`, `switch-model-hydrogen`, `switch-model-argon`, `switch-model-carbon`, `switch-model-flash` and `switch-gateway-omniroute`, `switch-gateway-omp` to `~/.zshrc`.
  - Include helper `_sync_goose_limits` in `~/.zshrc` to adjust `GOOSE_CONTEXT_LIMIT` and `GOOSE_AUTO_COMPACT_TOKEN_LIMIT` dynamically.
  - Include helper `_claude_omp` in `~/.zshrc` to pass `--settings` with `modelOverrides` remapping `claude-*-haiku*` to `gemini-3.8-flash` while explicitly overriding `ANTHROPIC_BASE_URL`, `ANTHROPIC_API_KEY`/`ANTHROPIC_AUTH_TOKEN`, `ANTHROPIC_DEFAULT_{HAIKU,OPUS,SONNET}_MODEL`, and `CLAUDE_CODE_SUBAGENT_MODEL` from `~/.claude/settings.json` on `:4000` launches.
  - Reconcile and update `scripts/setup-macbook-omniroute-client.sh` (both `~/Developer/scripts/` and `platform/openspec-store/scripts/`) to include `gemini-4-neon*` in `required_combos`.

## Risks / Trade-offs

- **Neon 512K Context Ceiling**: Prompts exceeding 512,000 tokens will be rejected by OmniRoute Neon. *Mitigation*: Compaction thresholds capped at 400K, and 1M models (`hydrogen`, `argon`) remain immediately selectable via `switch-model-hydrogen` or client pickers.
- **Shared Argon Quota Family**: Neon, Hydrogen, and Argon share weekly `family: "argon"` quota on OmniRoute. *Mitigation*: Fast/auxiliary tasks (OMP scout/commit/tiny/memory, Grok subagents, Claude haiku) remain pinned to `gemini-3.8-flash-high` (independent 9-pin pool).
- **Local `:4000` Fallback Model Availability**: If Google Antigravity temporarily fails on a specific model over `:4000`, OMP fallback chains continue down to `omniroute/gemini-3.8-flash-high:high` and `google-antigravity/gemini-3.8-flash:high`.
