# Design

## Context

See `proposal.md` for motivation. OMP (`v18.12.2`, installed at `/opt/homebrew/bin/omp` via Homebrew tap `can1357/tap/omp`) loads configuration and credentials through four distinct layers:
1. **Settings (`~/.omp/agent/config.yml`)**: Global role bindings (`modelRoles`), fallback chains (`retry.fallbackChains`), provider filters (`disabledProviders`), and subsystem flags (`isolation`, `prewalk`, `advisor`, `providers.tinyModelDevice`, `externalThinking`). Concurrent OMP processes coordinate writes to `config.yml` using `flock(2)` on `~/.omp/agent/config.yml.lock`.
2. **Custom Catalog (`~/.omp/agent/models.yml`)**: Static custom provider definitions (`omniroute`, `shopapikey`, `phanmemvip`, `cockpit`, `omniroute-anthropic`, `omniroute-chat`). Starting in OMP `v18.12.0`, explicit `contextWindow` and `maxTokens` in `models.yml` override built-in catalog rules.
3. **Credential Cascade (`packages/ai/src/stream.ts` & `packages/utils/src/env.ts`)**: Resolves API keys in order: CLI `--api-key` $\to$ `models.yml` `apiKey` $\to$ stored OAuth $\to$ stored `agent.db:auth_credentials` (`/login`, `source: "login"`) $\to$ `$env` (`Bun.env` $\to$ `<project>/.env` $\to$ `~/.omp/agent/.env` $\to$ `~/.omp/.env` $\to$ `~/.env`). Crucially:
   - `$env` **never reads `~/.zshenv`**, so OMP processes launched by GUI apps (Orca, Herdr) or non-rc shells (`zsh -fc`) that lack `~/.zshenv` variables in `Bun.env` see `typesafe/jev-1.14.0` as unauthenticated unless `TYPESAFE_API_KEY` is present in `~/.omp/agent/.env` or `agent.db:auth_credentials`.
   - Furthermore, for custom providers in `models.yml`, OMP's `resolveConfigValue(d)` (`CS(d)`) looks up `process.env[d]` and **falls back to the literal string `d`** (`return p || d;`) when `d` is unset or empty in `Bun.env` and `.env` files. Because `~/.omp/agent/.env` currently has mode `0644` and only 4 empty keys, any GUI/daemon-launched OMP process that lacks `~/.zshenv` in `Bun.env` sends literal `"OMNIROUTE_API_KEY"` or `"HERMES_CUSTOM_COCKPIT_API_KEY"` as its `Authorization: Bearer` token (`HTTP 401`).
   - When `--profile <name>` is passed on the CLI, OMP's root CLI dispatcher (`dirs.ts`) sets `agentDir = ~/.omp/profiles/<name>/agent` *before* `env.ts` loads `.env` files, so isolated profile tests read `~/.omp/profiles/<name>/agent/.env` and `~/.omp/profiles/<name>/agent/agent.db` without touching live `~/.omp/agent/`.
4. **Workstation Toolchain Governance (`/Users/androidteam/Developer/platform/openspec-store`)**: Enforces single-owner binary authority across `config/workstation-toolchain-manifest.json` (validated against `config/workstation-manifest.schema.json`), `config/Brewfile`, `scripts/toolchain_updater_registry.py`, `scripts/inventory-workstation-toolchain.py`, `scripts/reconcile-agent-cli-coverage.py`, and `scripts/workstation-daily-update.sh`.

## Goals / Non-Goals

**Goals:**
- Guarantee deterministic, sub-second `typesafe/jev-1.14.0` resolution for OMP's `judge` role (`find`, `prewalk.auto`, `ttsr.judge`, `eval` `judge()`) and valid custom-gateway credentials across both login shells (`zsh -lic`) and non-rc/GUI processes (`zsh -fc`) without `HTTP 402` or literal-env-name `HTTP 401` failures.
- Stage and verify all `.env`, `agent.db`, `models.yml`, and `config.yml` changes inside an isolated profile (`~/.omp/profiles/omp-v18-12-opt/agent`) before mutating live `~/.omp/agent/` state.
- Register `omp` (`brew-formula`, `can1357/tap/omp`) with full JSON Schema compliance, dynamic Cellar source verification, and shadow-path scanning across all workstation toolchain inventory, agent CLI coverage scripts, and governance unit tests.

**Non-Goals:**
- Mutating active chat/advisor role targets (`default`, `smol`, `tiny`, `vision`, `slow`, `plan`, `commit`, `task`, `advisor: cockpit/gpt-6.1-sol:xhigh`).
- Changing OmniRoute container combos or SHB Python `shb_core.jev` modules.

## Decisions

### 1. Belt-and-Suspenders Credential Persistence (`~/.omp/agent/.env` + `agent.db`) and OpenRouter `402` Elimination
- **Decision**:
  1. Explicitly bind `modelRoles.judge: typesafe/jev-1.14.0` and `retry.fallbackChains.judge: [typesafe/jev-latest, typesafe/jev-preview]` in `~/.omp/agent/config.yml`.
  2. Add `disabledProviders: [openrouter, lm-studio, llama.cpp, vscode]` in `~/.omp/agent/config.yml`.
  3. Populate all 5 active keys from `~/.zshenv` into `~/.omp/agent/.env` (`chmod 0600`):
     - `TYPESAFE_API_KEY` (`len=107`)
     - `OMNIROUTE_API_KEY` (`len=35`)
     - `HERMES_CUSTOM_COCKPIT_API_KEY` (`len=42`)
     - `HERMES_CUSTOM_SHOPAPIKEY_API_KEY` (`len=36`)
     - `HERMES_CUSTOM_PHANMEMVIP_API_KEY` (`len=36`)
     while removing the retired empty `HERMES_CUSTOM_GIAODUC_API_KEY=` and `HERMES_CUSTOM_OMNIROUTE_API_KEY=` lines and commenting out the unfunded `OPENROUTER_API_KEY` export on line 26 of `~/.zshenv`.
  4. In `agent.db`, execute an immediate transaction (`PRAGMA busy_timeout=5000; BEGIN IMMEDIATE;`) that deletes existing `openrouter` and `typesafe` rows from `auth_credential_blocks` first (matching `credential_id` subquery and `provider_key GLOB`, since `auth_credential_blocks` has columns `(credential_id, provider_key, block_scope, blocked_until_ms, updated_at)` and no `provider` column), then deletes from `auth_credentials` (which has no `UNIQUE(provider)` constraint), and inserts a single `typesafe` row:
     ```sql
     PRAGMA busy_timeout=5000;
     BEGIN IMMEDIATE;
     DELETE FROM auth_credential_blocks
      WHERE credential_id IN (SELECT id FROM auth_credentials WHERE provider IN ('openrouter', 'typesafe'))
         OR provider_key GLOB 'openrouter:*'
         OR provider_key GLOB 'typesafe:*';
     DELETE FROM auth_credentials WHERE provider IN ('openrouter', 'typesafe');
     INSERT INTO auth_credentials (provider, credential_type, data, disabled_cause, identity_key)
     VALUES ('typesafe', 'api_key', json_object('key', :typesafe_key, 'source', 'login'), NULL, NULL);
     COMMIT;
     ```
- **Rationale**: Setting `"source": "login"` in `auth_credentials.data` places `typesafe` at the top of OMP's stored API-key cascade, while populating all 5 active keys in `~/.omp/agent/.env` (`0600`) ensures `resolveConfigValue` in `models.yml` never falls back to literal variable names when OMP is launched by GUI apps or `zsh -fc` (`NO_RCS`).

### 2. OMP `v18.12.2` Runtime Settings, Wildcard Fallback Chains & Context Import Fix
- **Decision**:
  - Set `isolation.backend: apfs` (replacing `rcopy`) so isolated `task` subagents use macOS APFS `clonefile(2)` copy-on-write via `pi-natives`.
  - Set `externalThinking: false` (replacing `true`) so Gemini 4 Argon, Gemini 3.8 Flash, and Cockpit GPT-6.1-Sol use native reasoning tokens rather than the deprecated XML scratchpad wrapper.
  - Set `providers.tinyModelDevice: mlx` to enable Apple Silicon 4-bit MLX local inference acceleration.
  - Replace `cockpit/gpt-6-astra` in `retry.fallbackChains` with wildcard `cockpit/*: [google-antigravity/gemini-4-argon:high, omniroute/gemini-3.8-flash-high, google-antigravity/gemini-3.8-flash:high]` to cover `modelRoles.advisor: cockpit/gpt-6.1-sol:xhigh` and all Cockpit models without repeating identical YAML blocks, and replace unauthenticated `google/*` and `google-vertex/*` wildcard hops in `retry.fallbackChains['google-antigravity/*']` with `google-antigravity/gemini-3.8-flash:high` (`['omniroute/gemini-3.8-flash-high', 'google-antigravity/gemini-3.8-flash:high']`).
  - Remove superseded top-level keys `memories`, `renderMermaid`, `calc`, and `bashInterceptor.redirects`, and set `tui: { renderMermaid: true }`.
  - Change `/Users/androidteam/Developer/.claude/CLAUDE.md:L153` from `@AGENTS.md` to `@../AGENTS.md` because OMP resolves `@` imports relative to `.claude/` (`at-imports.ts`) and `.claude/CLAUDE.md` (priority `80`) shadows `/Users/androidteam/Developer/AGENTS.md` (priority `10`) at depth `0` unless imported via `@../AGENTS.md`.

### 3. `models.yml` Catalog Pruning, `v18.12.0` Context Window Alignment, and Stage-First Transaction Boundary
- **Decision**:
  - Remove all 14 retired `sh/*` entries (including duplicate `sh/codex-x`) from `providers.omniroute.models` (leaving the 11 active live models) and remove the retired `omniroute-chat` (`sh/codex-x`) provider block.
  - Set `contextWindow: 128000` on `nx/deepseek-v4.1-flash` and `contextWindow: 200000` on `omniroute-anthropic` (`pm/Claude-Fable`, `pm/Claude-Opus`, `pm/Claude-Sonnet`) to match live OmniRoute `/v1/models`.
  - Add `reasoning: true`, `thinking: { mode: effort, efforts: [low, medium, high, xhigh], defaultLevel: high }`, `supportsTools: true`, and `imageCountBudget: 20` to all 5 `providers.cockpit.models` entries (`gpt-6-astra`, `gpt-6.1-sol`, `gpt-5.6-luna`, `gpt-5.6-sol`, `gpt-5.6-terra`).
- **Transaction & Rollback Boundary**:
  1. Leave `~/.omp/agent/config.yml.lock` untouched (preserving active `flock(2)` coordination across running OMP sessions) and move the 16 legacy `.bak*`/`*.pre-*`/`backups-*` items in `~/.omp/agent/` into `~/.omp/agent/backups-archive/` (`mode 0700`).
  2. Use `sqlite3 "file:$HOME/.omp/agent/agent.db?mode=ro" ".backup '<dest>'"` (never plain `cp`, which misses the `3.9 MB` `agent.db-wal` or `CREATE TABLE AS SELECT`, which drops `PRIMARY KEY` constraints) both to create the baseline backup of `agent.db` and to seed `~/.omp/profiles/omp-v18-12-opt/agent/agent.db`.
  3. Stage `.env`, `agent.db` credential changes, `models.yml`, and `config.yml` inside `~/.omp/profiles/omp-v18-12-opt/agent` first and run uncached `omp find` smoke gates in both `zsh -lic` (`OMP_JUDGMENT_CACHE_DB=/tmp/omp-judge-lic.db`) and `env -u ... zsh -fc` (`OMP_JUDGMENT_CACHE_DB=/tmp/omp-judge-fc.db`) before mutating live `~/.omp/agent/` files.

### 4. Declarative Toolchain Governance & Shadow-Path Hardening for `/opt/homebrew/bin/omp`
- **Decision**:
  - Add `"omp"` to `profiles.ai-agents` and `tools.omp` in `config/workstation-toolchain-manifest.json` with all 6 JSON Schema required fields plus peer `brew-formula` metadata:
    ```json
    "omp": {
      "authoritative_owner": "brew-formula",
      "active_path_pattern": "{{HOMEBREW_PREFIX}}/bin/omp",
      "update_authority": "brew",
      "release_channel": "stable",
      "dispatch_classification": "none",
      "verification_smoke_command": "omp --version",
      "writer_binary": "brew",
      "supported_verb": "brew upgrade can1357/tap/omp",
      "delegating_to": null,
      "package_name": "can1357/tap/omp",
      "known_shadow_paths": [
        "{{HOME}}/.bun/bin/omp",
        "{{HOME}}/.npm-global/bin/omp"
      ],
      "category": "ai-agent",
      "notes": "Oh My Pi coding agent CLI managed via Homebrew tap formula can1357/tap/omp."
    }
    ```
  - Add `tap "can1357/tap"` and `brew "can1357/tap/omp"` to `config/Brewfile` and document `omp` in `docs/mac-development-setup.md`.
  - Add `("omp", "brew-formula")` (`status="uncovered_declared"`, `updater_dispatch="none"`, `delegating_to="brew"`, `supported_verb=None`) to `SUPPORTED_UPDATER_REGISTRY` in `scripts/toolchain_updater_registry.py`.
  - In `scripts/inventory-workstation-toolchain.py`:
    - Add `"omp"` to `tools_to_evaluate`, `documented_channels_map` (`"omp": ["brew-formula: can1357/tap/omp", "npm: @oh-my-pi/pi-coding-agent"]`), `tools_to_check` (alongside missing `"qwen"`), and `preferred_sources` (`"omp": ("formula can1357/tap/omp", True)`).
    - In `evaluate_authority_and_drift()`, verify `dyn_root, src = derive_install_root_and_source(resolved_path)` and `decl = get_supported_updater(name, src)` for `omp` so `drift_status = "clean"` is set only when `src == "brew-formula"` and `decl is not None` (reporting `target_misalignment` or `unknown` if a shadow binary or cleared registry is encountered).
    - In `inventory_tools()`, map `elif tool_name == "omp": pkg_keys.append("@oh-my-pi/pi-coding-agent")` and inspect `known_shadow_paths` (`~/.bun/bin/omp`, `~/.npm-global/bin/omp`) so any shadow binary is appended to `copies`.
  - In `scripts/reconcile-agent-cli-coverage.py`, add `"omp"` to `known_agents` and `--include-uncovered`, and update `evaluate_update_path()` (`L166-167`) so `source_type == "package_manager"` verifies `decl is not None and decl.status == "uncovered_declared"` and includes `delegating_to={decl.delegating_to}` in the returned detail string.
  - Append `omp` to `AGENT_CLI_KNOWN_UNCOVERED` in both `scripts/workstation-daily-update.sh` and `/Users/androidteam/Developer/scripts/workstation-daily-update.sh` (preserving SHA-256 parity), and add unit test assertions in `scripts/test-version-authority-governance.py` and `tests/test_portable_workstation_slice_a.py`.

## Risks / Trade-offs

- **SQLite `agent.db` WAL & Lock Safety**: Running OMP sessions hold open connections to `agent.db` (`3.9 MB` `agent.db-wal`) and `config.yml.lock`. Mitigation: never move `config.yml.lock`, use `sqlite3 ".backup"` for WAL-consistent copies, and run the `auth_credential_blocks` + `auth_credentials` mutation inside a single `BEGIN IMMEDIATE` transaction with `PRAGMA busy_timeout=5000;` only after isolated-profile smoke gates pass.
- **`omp find` Judgment Cache Masking**: OMP caches `find` judgments in `judgment-cache.db`. Mitigation: pass distinct temporary `OMP_JUDGMENT_CACHE_DB` paths for the `zsh -lic` and `zsh -fc` smoke probes and assert `.stats.requests > 0`.
- **`workstation-daily-update.sh` Mirror Parity**: Updating `platform/openspec-store/scripts/workstation-daily-update.sh` without syncing `/Users/androidteam/Developer/scripts/workstation-daily-update.sh` breaks `test_workstation_daily_update_mirror_parity_and_bash_fail_closed`. Mitigation: copy and verify `shasum -a 256` equality across both paths as an explicit task gate.
