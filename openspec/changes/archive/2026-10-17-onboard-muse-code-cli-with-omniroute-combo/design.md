# Design

## Context

See `proposal.md` for motivation and scope boundaries.

Meta Muse Code (`muse`, distributed via Homebrew cask `muse-code` at `v1.4.10-R6427.1`) is a compiled native Rust `arm64` terminal coding agent (`/opt/homebrew/Caskroom/muse-code/<version>/muse-aarch64-macos` symlinked to `/opt/homebrew/bin/muse`). It communicates over the **OpenAI Responses API** (`POST <base_url>/responses` with SSE streaming) and queries a proprietary discovery endpoint (`GET <base_url>/muse-code/models`).

Local OmniRoute (`v3.8.51` running on `http://127.0.0.1:20128`) already implements:
1. `GET /v1/muse-code/models` (`src/app/api/v1/muse-code/models/route.ts`, mapped via `next.config.mjs` `/v1/:path*` rewrite and `CLIENT_API` bearer policy), advertising 13 Meta models including `muse-spark-1.3` (`limit: 1048576`, `reasoning: true`, `tool_call: true`).
2. `POST /v1/responses` (`src/app/api/v1/responses/route.ts`), which delegates to `handleChatImplementation` (`src/sse/handlers/chat.ts`) and automatically flattens Muse's `"type": "namespace"` tool groups (`{"type": "namespace", "name": "muse", "tools": [...]}`) into collision-safe `"muse__<leaf>"` function names (`open-sse/translator/request/openai-responses/namespaceFlatten.ts`) and restores `{"namespace": "muse", "name": "<leaf>"}` on streamed `function_call` output items (`open-sse/translator/response/openai-responses/functionCallIdentity.ts`).

Key technical constraints verified during codebase and documentation inspection:
- **Combo Precedence Over Unconfigured Static Provider (`#8530` / `#6940`)**: In `src/sse/handlers/chat.ts:993-1020`, `getComboForModel(resolvedModelStr)` executes strictly before static provider lookup (`handleSingleModelChat` at line 1354). Creating a combo named `muse-spark-1.3` via `POST /api/combos` returns HTTP `201` with a non-blocking `warning.code = "COMBO_NAME_SHADOWS_MODEL"` (`src/app/api/combos/route.ts:122-127`) and intercepts bare `"model": "muse-spark-1.3"` requests cleanly.
- **Muse CLI $\ge$ 1.0.1 Front-Door Bearer Withholding**: Passing `--base-url` on the CLI without pinning `endpoint_transport` in `~/.config/muse/settings.json` strips the `Authorization: Bearer` header (`"Meta bearer withheld: base_url is off the sanctioned front door"`). Furthermore, `"schema_version": 1` is mandatory in `settings.json` (`malformed settings file` if omitted), and the built-in default model in Muse 1.4.x is `"muse-spark-1.2"` unless `"model": "muse-spark-1.3"` is explicitly set.
- **`mcpServers` / `mcp_servers` Serialization**: Muse Code 1.4.10 accepts `mcp_servers` as an input alias and canonicalizes user settings on disk to `mcpServers` with `"transport": "stdio"` and `"mode": "optional"`.
- **macOS Keychain & File Credential Store**: Running `muse auth set --provider meta --api-key-stdin` stores the key in macOS Keychain (`svce="ai.meta.dev.credentials"`, writing `{"schema_version": 2, "providers": {"meta": {"storage": "keychain"}}}` in `~/.config/muse/auth.json`) or in `~/.config/muse/auth.json` (`schema_version: 1`) when `TBH_CREDENTIAL_BACKEND=file` is set.
- **Binary Name (`muse`) vs Cask Token (`muse-code`) in Toolchain Governance**: Cask `muse-code` installs `/opt/homebrew/bin/muse` (there is no `muse-code` executable on `PATH`). Like `cursor-agent` (cask `cursor-cli`), `inventory-workstation-toolchain.py` (`tools_to_evaluate`, `tools_to_check`, and `elif name in ("droid", "cursor-agent", "buzz", "muse"):` at line 826), `config/workstation-toolchain-manifest.json`, and `reconcile-agent-cli-coverage.py` must evaluate the executable identifier `"muse"` with `updater_dispatch="none"`, `supported_verb=None`, `delegating_to="brew"`, `status="uncovered_declared"`.

## Goals / Non-Goals

**Goals:**
- Provision Meta Muse Code (`muse`) via official Homebrew cask `muse-code` (`/opt/homebrew/bin/muse`) with single-owner PATH resolution.
- Create OmniRoute combo `muse-spark-1.3` routing to the 15-account `gemini-3.8-flash-high` Antigravity pool (`combo-ref`) with `agy/gemini-3.8-flash-medium` fallback.
- Configure `~/.config/muse/settings.json` and `~/.config/muse/auth.json` (mode `0600`) with sanctioned `endpoint_transport` bearer pinning, `mcp_servers.mcp-router` stdio integration, and workstation skills.
- Register `muse` / `muse-code` across `toolchain_updater_registry.py`, `inventory-workstation-toolchain.py`, `config/workstation-toolchain-manifest.json`, `reconcile-agent-cli-coverage.py`, `test-version-authority-governance.py`, and `workstation_update.py`.
- Verify live headless `muse exec --disable-approval --no-session-log` prompt and tool-call execution against `http://127.0.0.1:20128/v1/responses`.

**Non-Goals:**
- Configuring or authenticating a direct Meta account (`auth.meta.com` RFC 8628 device OAuth or `META_API_KEY` for `mc/*` / `msw/*`) in OmniRoute (deferred to a separate change).
- Altering existing model routing or provider files for other coding CLIs (`omp`, `claude`, `kimi`, `goose`, `pi`, `codex`).

## Decisions

1. **OmniRoute Combo Interception Named `muse-spark-1.3` (`POST /api/combos`)**:
   - *Decision*: Register an OmniRoute combo with exact name `muse-spark-1.3` (`strategy: "priority"`, `context_length: 1000000`, `context_cache_protection: true`):
     ```json
     {
       "name": "muse-spark-1.3",
       "description": "Muse Spark 1.3 routed via Gemini 3.8 Flash High Antigravity pool",
       "strategy": "priority",
       "context_length": 1000000,
       "context_cache_protection": true,
       "models": [
         {
           "kind": "combo-ref",
           "comboName": "gemini-3.8-flash-high"
         },
         {
           "kind": "model",
           "model": "agy/gemini-3.8-flash-medium",
           "providerId": "agy"
         }
       ]
     }
     ```
   - *Rationale*: In `"flatten"` mode (default `nestedComboMode`), `resolveNestedComboTargets` (`src/lib/combos/comboStructure.ts:304-329`) recursively expands `combo-ref` `gemini-3.8-flash-high` into its 15 connection-pinned `agy` legs followed by `agy/gemini-3.8-flash-medium`. When a Meta account is later added in a separate change, `mc/muse-spark-1.3` can be prepended to this combo without modifying `~/.config/muse/settings.json`.
   - *Alternatives Considered*:
     - `oc/muse-spark-1.3-contributor-free`: Rejected (`HTTP 410 model_shutdown`).
     - `agy/claude-sonnet-4-6-high` / `gh/gpt-5.6-sol-high`: Rejected (`HTTP 400` unsupported model IDs).

2. **Sanctioned `endpoint_transport` & Dual-Compatible MCP Configuration in `~/.config/muse/settings.json`**:
   - *Decision*: Seed `~/.config/muse/auth.json` (mode `0600`) using `TBH_CREDENTIAL_BACKEND=file` and write `~/.config/muse/settings.json` (mode `0600` inside `~/.config/muse` mode `0700`):
     ```json
     {
       "schema_version": 1,
       "model": "muse-spark-1.3",
       "provider": "meta",
       "endpoint_transport": {
         "base_url": "http://127.0.0.1:20128/v1",
         "auth": "bearer"
       },
       "run": {
         "subagent_delegation_mode": "auto"
       },
       "mcpServers": {
         "mcp-router": {
           "transport": "stdio",
           "command": "npx",
           "args": ["-y", "@mcp_router/cli@latest", "connect"],
           "env": {
             "MCPR_TOKEN": "<workstation-mcpr-token>"
           },
           "mode": "optional"
         }
       }
     }
     ```
   - *Rationale*: Uses the canonical `mcp_servers` (`transport: "stdio"`, `enabled: true`, `mode: "optional"`) schema required by `muse exec` and TUI sessions while satisfying Muse Code 1.0.1+ front-door bearer checks.

3. **Homebrew Cask Ownership (`cask "muse-code"`), Manifest Parity, & Process-Lock Guard**:
   - *Decision*:
     - In `toolchain_updater_registry.py`: Register `("muse", "brew-cask")` and `("muse-code", "brew-cask")` with `source_type="brew-cask"`, `supported_verb=None`, `updater_dispatch="none"`, `delegating_to="brew"`, `status="uncovered_declared"` (matching `droid`, `cursor-agent`, and `buzz`).
     - In `inventory-workstation-toolchain.py`: Add `"muse"` to `tools_to_evaluate`, `documented_channels_map` (`"muse": ["brew-cask: muse-code"]`), `elif name in ("droid", "cursor-agent", "buzz", "muse"):` (line 826), `tools_to_check`, `preferred_sources` (`"muse": ("cask muse-code", True)`), and `name_collisions`.
     - In `config/workstation-toolchain-manifest.json`: Add `"muse"` to `profiles.ai-agents` and `tools.muse` (`authoritative_owner: "brew-cask"`, `package_name: "muse-code"`, `dispatch_classification: "none"`, `supported_verb: "brew upgrade --cask muse-code"`) so `reconcile_with_manifest()` reports `0` unknowns.
     - In `reconcile-agent-cli-coverage.py` (and both copies of `workstation-daily-update.sh` if `AGENT_CLI_KNOWN_UNCOVERED` is updated): Add `"muse"` to `known_agents` and `--include-uncovered`.
     - In `shb/shb-schedule/src/shb_schedule/workflows/workstation_update.py`: In `step_homebrew_update()`, check `pgrep -x` against `("muse-code", "muse", "muse-aarch64-macos")` before upgrading `muse-code`.

## Transaction Boundaries

- **OmniRoute SQLite State (`/app/data` on Docker volume `omniroute-data`)**: Mutated exclusively via OmniRoute's authenticated REST API (`POST /api/combos` to create, and `PUT /api/combos/<combo-id>` or `DELETE /api/combos/<combo-id>` using the returned UUID `id`), never via host bind-mount SQLite edits.
- **User Workstation Config (`~/.config/muse/`)**: Isolated to `~/.config/muse/{settings.json,auth.json,skills/}` with pre-mutation backup if any prior files exist.
- **Governance Repositories (`platform/openspec-store` and `shb/shb-schedule`)**: Tracked in separate Git repositories; if `workstation-daily-update.sh` is touched, both `/Users/androidteam/Developer/scripts/workstation-daily-update.sh` and `platform/openspec-store/scripts/workstation-daily-update.sh` must stay byte-identical per `config/script-provenance-manifest.tsv`.

## Risks / Trade-offs

- **Risk**: OmniRoute v3.8.51 emits `data: {"type":"response.in_progress","sequence_number":1,"response":{"id":null,"status":"in_progress"}}` after 1,000 ms on `POST /v1/responses`, and Muse 1.4.10 probes `GET /muse-code/models` at the origin root.
  - *Mitigation*: Normalized `/muse-code` $\rightarrow$ `/v1/muse-code` in `scripts/dev/peer-stamp.mjs` (`/app/peer-stamp.mjs`) and `response: { id: "resp_keepalive", object: "response", status: "in_progress", output: [], error: null }` in `open-sse/utils/sseHeartbeat.ts` (`/app/.build/next/server/chunks/20286.js`), and added an idempotent `Gate 4b` post-recreate guard in `~/Omniroute/scripts/update.sh` so container recreates preserve both normalizations automatically.
- **Risk**: Cask name collision between `muse-code` (Meta Muse Code CLI) and `muse` (disabled `muse.ai` desktop app).
  - *Mitigation*: Recorded explicitly in `inventory-workstation-toolchain.py` `name_collisions`, `config/workstation-toolchain-manifest.json`, and unit tests in `test-version-authority-governance.py`.
