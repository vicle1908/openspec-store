# Proposal

## Why

While the shared OmniRoute gateway on `iosteam-mac-mini` exposes all four Gemini 4 combos (`gemini-4-neon`, `gemini-4-hydrogen`, `gemini-4-argon`, and pre-wired `gemini-4-carbon`) and peer workstation `macbook-pro-m5` has fully standardized its coding fleet and shell environment on `omniroute/gemini-4-neon` (`512K` context, `262K` max output), the host `Macmini` environment remains fragmented: its coding agents still default to `gemini-4-hydrogen` or legacy configurations, lack `gemini-4-neon` across client catalogs and switcher scripts, lack local `omp auth-gateway` (`:4000`) LaunchAgents for failover, and OmniRoute itself runs `gemini-4-neon` on an unweighted `priority` strategy without transport keepalive enabled. Standardizing `Macmini` coding agents on `gemini-4-neon` with local loopback endpoints, adding the local OMP Auth-Gateway backup tier, tuning OmniRoute's Neon combo to `quota-weighted`, and enabling `RESPONSES_TRANSPORT_KEEPALIVE_ENABLED` achieves uniform cross-workstation fleet parity while incorporating verified bug fixes discovered during the M5 rollout.

## What Changes

- **OmniRoute Gateway Strategy & Transport Hardening (`storage.sqlite`)**:
  - Tune `gemini-4-neon`, `gemini-4-neon-high`, `gemini-4-neon-medium`, and `gemini-4-neon-low` combos from `strategy: "priority"` to `strategy: "quota-weighted"` (`quotaWeightedFloorPercent: 5`, `quotaWeightedScoring: "leftover"`, `predictiveTtftMs: 0`), eliminating account exhaustion bottlenecks on single `step-1` pins.
  - Enable feature flag `RESPONSES_TRANSPORT_KEEPALIVE_ENABLED: true` in `key_value` (`namespace: "feature_flags"`) with OmniRoute cache reload/restart, eliminating synthetic snapshot disconnects (`stream closed before response.completed`) on long OpenAI Responses streams.
- **Local OMP Auth-Gateway & Broker Provisioning (`:4000` / `:8765`)**:
  - Provision macOS LaunchAgents `local.shb.omp.auth-broker.plist` (`127.0.0.1:8765`) and `local.shb.omp.auth-gateway.plist` (`127.0.0.1:4000`, `--no-auth`), giving `Macmini` the same local zero-latency `omp` failover tier as `macbook-pro-m5`.
- **Fleet Default Cutover to `omniroute/gemini-4-neon`** (**BREAKING** for interactive default sessions):
  - Standardize unoverridden interactive default sessions across OmniRoute-defaulting clients on `Macmini` to `omniroute/gemini-4-neon` at `high` effort:
    - OMP base profile (`~/.omp/agent/config.yml` `modelRoles.default: omniroute/gemini-4-neon`).
    - Kimi Code (`~/.kimi-code/config.toml` `default_model = "omniroute/gemini-4-neon"`).
    - Pi (`~/.pi/agent/settings.json` `defaultModel: "gemini-4-neon"`).
    - OpenCode (`~/.config/opencode/opencode.json` `model: "omniroute-responses/gemini-4-neon"`).
    - Goose (`~/.config/goose/config.yaml` `model: "gemini-4-neon"` and `GOOSE_MODEL=gemini-4-neon`).
    - Factory Droid (`~/.factory/settings.json` `sessionDefaultSettings.model: "custom:OmniRoute-Gemini-4-Neon-11"`).
    - Grok Build (`~/.grok/config.toml` `[models] default = "omniroute-gemini-4-neon"`).
    - Zed IDE (`~/.config/zed/settings.json` `agent.default_model.model: "gemini-4-neon"`).
    - Claude Code launcher (`omniroute()` in `~/.zshrc` launching `~/.claude/profiles/omniroute-pm.json` with default `gemini-4-neon`).
    - Kilo Code (`~/.config/kilo/kilo.jsonc` `model: "omniroute-responses/gemini-4-neon"`).
    - Cline (`~/.cline/data/settings/providers.json` `model: "gemini-4-neon"`).
    - SHB environment (`~/.shb/.env` `SHB_DEFAULT_MODEL=gemini-4-neon`).
- **512K Neon Compaction & Effort Ceiling Alignment**:
  - Enforce `512,000` context window and `<=400,000` compaction token limits for Neon across Goose (`GOOSE_CONTEXT_LIMIT=512000`, `GOOSE_AUTO_COMPACT_TOKEN_LIMIT=400000`, `providers.custom_omniroute.context_limit: 512000`), Factory Droid (`compactionTokenLimitPerModel: { "custom:OmniRoute-Gemini-4-Neon-11": 400000 }`), and OpenCode.
  - Constrain Gemini 4 effort parameters to wire-verified `low`, `medium`, `high` tiers across client menus (retaining OMP `slow: omniroute/gemini-4-argon:xhigh` strictly as a documented clamped compatibility selector).
- **Client Catalog Parity & Dual-Gateway Exposure**:
  - Expose all four OmniRoute Gemini 4 combos (`gemini-4-neon`, `gemini-4-hydrogen`, `gemini-4-argon`, and selectable-only `gemini-4-carbon`) in `omniroute` provider blocks across all clients.
  - Expose local `omp` (`http://127.0.0.1:4000/v1`) active Gemini 4 models (`omp/gemini-4-neon`, `omp/gemini-4-hydrogen`, `omp/gemini-4-argon`, `omp/gemini-3.8-flash`) as the secondary backup provider in client configurations (adding `custom_omp.json` for Goose).
  - Strictly forbid `gemini-4-carbon` from any default model, automated fallback chain, or local `omp` catalog.
- **Specialized Client Boundaries Preserved (Catalog-Only Updates)**:
  - Keep Codex CLI default on `gemini-4-hydrogen` (`~/.codex/config.toml` and `~/.codex/omniroute.config.toml`) while creating absolute `~/.codex/model-catalog.json` registering `gemini-4-{neon,hydrogen,argon,carbon}`.
  - Keep Hermes on `moa:default` while registering `gemini-4-neon` under `providers.omniroute.models` and `agent.reasoning_overrides` in `~/.hermes/config.yaml`.
  - Keep Claude Code global `apiKeyHelper` and `shopapikey` launchers intact on `Claude-Fable`.
  - Preserve `gemini-3.8-flash-high` (`9` active pins) as the dedicated auxiliary/fast tier and terminal safety net.
- **Shell Environment, Switchers, and Cross-Host Parity (`~/.zshenv`, `~/.zshrc`)**:
  - Add `switch-model-neon`, `switch-model-hydrogen`, `switch-model-argon`, `switch-model-carbon`, `switch-model-flash` and gateway switchers (`switch-gateway-omniroute`, `switch-gateway-omp`).
  - Add `omp-omniroute-*`, `pi-omniroute-*`, `grok-omniroute-*`, `kimi-omniroute-*`, `droid-omniroute-*`, `goose-omniroute-*`, `codex-omniroute-*`, and `claude-omniroute-*` shortcuts.
  - Keep all Macmini OmniRoute URLs bound to local `http://localhost:20128` / `http://127.0.0.1:20129` (avoiding Tailscale hairpinning).
  - Incorporate M5 review bug fixes: add `_sync_goose_limits` helper to update Goose context limits dynamically on switcher calls, and add `_claude_omp` helper ensuring local Claude Code sessions override `settings.json` `env` defaults and remap Haiku subagents to `gemini-3.8-flash` (avoiding HTTP 404 on `:4000`).
  - Update `scripts/setup-macbook-omniroute-client.sh` (both in `~/Developer/scripts` and `platform/openspec-store/scripts`) to include `gemini-4-neon*` in `required_combos` so `--check` passes cleanly across both nodes.

## Capabilities

### New Capabilities
- None. All requirements extend and reconcile existing registered capabilities in `openspec-store`.

### Modified Capabilities
- `omniroute-agent-cli-routing`: Update host coding-agent fleet on `iosteam-mac-mini` to expose `gemini-4-neon` as the primary default for OmniRoute-defaulting clients, register `gemini-4-neon*` in all client catalogs and setup scripts, enforce `512K` compaction limits, tune OmniRoute Neon combos to `quota-weighted`, and enable `RESPONSES_TRANSPORT_KEEPALIVE_ENABLED`.
- `omp-provider-routing`: Update OMP base profile to default to `omniroute/gemini-4-neon`, register `gemini-4-neon` and `gemini-4-carbon` in `models.yml`, configure `retry.fallbackChains["omniroute/gemini-4-neon"]` with fail-closed failover legs, and register local `omp/gemini-4-neon` backup models.
- `claude-code-provider-routing`: Update `omniroute()` launcher in `~/.zshrc` and profile `~/.claude/profiles/omniroute-pm.json` to default to `gemini-4-neon`, expose `gemini-4-{neon,hydrogen,argon,carbon}` in `modelPicker.options`, and add `_claude_omp` helper in `~/.zshrc` with Haiku/Opus/Sonnet remap protection.
- `pi-agent-harness-config`: Update Pi `~/.pi/agent/settings.json` and `models.json` to default to `gemini-4-neon` (`high`), expose `gemini-4-{neon,hydrogen,carbon}` under `omniroute-responses` and `gemini-4-{neon,hydrogen}` under `omp`, and align subagent role defaults.
- `grok-cli-provider-routing`: Update Grok `~/.grok/config.toml` default to `omniroute-gemini-4-neon`, register `gemini-4-neon` models under `omniroute` and `omp`, and restrict Gemini 4 reasoning efforts to `[high, medium, low]`.
- `hermes-moa-configuration`: Add `gemini-4-neon` to `providers.omniroute.models` and `agent.reasoning_overrides` in `~/.hermes/config.yaml` without altering the primary `moa:default` preset or direct provider fallback order.
- `omp-fresh-shell-contract`: Align `~/.zshenv` and `~/.zshrc` on `Macmini` to define non-clobbering `gemini-4-neon` defaults, shell model/gateway switcher functions, `_sync_goose_limits`, and provisioned LaunchAgents for `local.shb.omp.auth-broker` and `local.shb.omp.auth-gateway`.

## Impact

- **Host Workstation Files (`iosteam-mac-mini`)**:
  - `~/.omp/agent/{config.yml,models.yml}`
  - `~/.kimi-code/config.toml`
  - `~/.pi/agent/{settings.json,models.json}`
  - `~/.config/opencode/opencode.json`
  - `~/.config/goose/{config.yaml,custom_providers/custom_omniroute.json,custom_providers/custom_omp.json}`
  - `~/.factory/settings.json`
  - `~/.grok/config.toml`
  - `~/.config/zed/settings.json`
  - `~/.claude/profiles/omniroute-pm.json`
  - `~/.codex/{config.toml,omniroute.config.toml,model-catalog.json}`
  - `~/.hermes/config.yaml`
  - `~/.config/kilo/kilo.jsonc`
  - `~/.cline/data/settings/providers.json`
  - `~/.shb/.env`
  - `~/Library/LaunchAgents/{local.shb.omp.auth-broker.plist,local.shb.omp.auth-gateway.plist}`
  - `~/.zshenv` and `~/.zshrc`
- **OmniRoute Container (`omniroute` SQLite)**:
  - `storage.sqlite`: `combos` table (`gemini-4-neon*` strategy updated to `quota-weighted`), `key_value` table (`settings:RESPONSES_TRANSPORT_KEEPALIVE_ENABLED` set to `"true"`).
- **Workspace Tooling Scripts**:
  - `~/Developer/scripts/setup-macbook-omniroute-client.sh` and `platform/openspec-store/scripts/setup-macbook-omniroute-client.sh`.
- **Non-Goals**:
  - Mutating live remote configs on `macbook-pro-m5`.
  - Hairpinning `Macmini` client traffic through the Tailscale IP (`100.70.16.83` / MagicDNS domain) instead of local loopback (`localhost:20128` / `127.0.0.1:20129`).
  - Switching Hermes default from `moa:default` to single-model OmniRoute.
  - Switching Codex default CLI away from `gemini-4-hydrogen` or altering Codex cockpit profiles.
  - Enabling unverified Google AI Ultra accounts on `gemini-4-carbon*` before formal account qualification.
- **Affected Ownership Boundaries**:
  - `platform/openspec-store`: Change planning, delta specs, and synchronization scripts.
  - `~/.omp/`: OMP agent configuration, models catalog, and LaunchAgents.
  - Local workstation client runtimes: Kimi, Pi, OpenCode, Goose, Droid, Grok, Zed, Claude Code, Codex, Hermes, Kilo, Cline.
  - OmniRoute deployment (`/app/data/storage.sqlite`).
