# Design

## Context

See `proposal.md - Why` for the eight verified configuration, catalog, credential, and documentation defects in the live Oh My Pi (`omp` v18.14.1) setup at `/Users/androidteam/.omp/`.

Current workstation invariants and constraints:
- **Authoritative Binary**: `/opt/homebrew/bin/omp` (`can1357/tap/omp`, `18.14.1`).
- **Live Lock & SQLite WAL**: `/Users/androidteam/.omp/agent/config.yml.lock` is a shared `flock(2)` lockfile across active OMP processes and MUST NEVER be moved or deleted. `/Users/androidteam/.omp/agent/agent.db` and `models.db` run in SQLite `WAL` mode (`mode 0600` on `agent.db`, `config.yml`, `models.yml`, `.env`, `mcp.json`).
- **OmniRoute Gateway Pool Topology (`http://127.0.0.1:20128`)**: `omniroute/gemini-4-argon*` routes exclusively to the 2–3 Google AI Ultra (`g1-ultra-tier`) `agy` accounts, whereas `omniroute/gemini-3.8-flash-high` pools 12–15 `agy` accounts.
- **Credential Cascade**: Because OMP's `$env` cascade does not read `~/.zshenv` in non-login (`zsh -fc`) or GUI-spawned sessions, `~/.omp/agent/.env` (`mode 0600`) holds the 5 active provider keys (`TYPESAFE_API_KEY`, `OMNIROUTE_API_KEY`, `HERMES_CUSTOM_{COCKPIT,SHOPAPIKEY,PHANMEMVIP}_API_KEY`), and `~/.omp/agent/mcp.json` (`mode 0600`) retains its `env.MCPR_TOKEN` value directly so non-login MCP connections do not expand `${MCPR_TOKEN}` to an empty string.

## Goals / Non-Goals

**Goals:**
- Preserve native `thinking` effort tiers (`["low", "medium", "high"]`) on all `omniroute/*gemini-4-argon*` models in `omp models --json` and eliminate OmniRoute's `Memory context:` prompt prefix injection.
- Isolate `omniroute/gemini-4-argon` (Ultra pool) for primary interactive reasoning while routing `@smol` (including Phase 2 local memory consolidation and `async.widgets`), `title.generator`, and bounded `memories.stage1Concurrency` to prevent 503 pool starvation.
- Enable v18.13.3–v18.14.1 resilience and safety controls (`retry.rateLimitWalksChain`, `retry.usageAwareFallback`, `bash.gitGuard`, `compaction` tuning, `advisor`/`smol`/`omniroute/*` fallback chains).
- Prune the permanently 403-rejected `google-antigravity` OAuth credential (`id=4`, `email:vicgnome19091@gmail.com`) and 3 stale `~/.omp/profiles/omp-fresh-*` directories using WAL-safe transactions and isolated-profile smoke gates.

**Non-Goals:**
- Modifying any source code in `/opt/homebrew/Cellar/omp/` or `/Users/androidteam/Omniroute/`.
- Adding `promptCache` to `providers.omniroute` models (which arms OMP's `w0e` background cache warmer and sends 1-token full-context replay requests every 4.5 minutes while idle, burning Ultra quota) or adding `modelRoles.memory` (which `memory.backend: local` ignores in `aJ`).
- Changing `modelRoles.default` (`omniroute/gemini-4-argon`), `modelRoles.plan` (`google-antigravity/gemini-4-argon:high`), or `modelRoles.judge` (`typesafe/jev-1.14.0`).

## Decisions

### 1. Explicit `compat` Override and `x-omniroute-no-memory` Header on `providers.omniroute` in `models.yml`
- **Decision**: Add `compat: { supportsReasoningEffort: true, supportsDeveloperRole: true }` and `headers: { "x-omniroute-no-memory": "true" }` to `providers.omniroute` (and `headers: { "x-omniroute-no-memory": "true" }` to `providers.omniroute-anthropic`), omit `promptCache`, and remove the unused root `equivalence:` block.
- **Rationale**: In OMP `packages/coding-agent/src/config/custom-models.ts` (`mPe`), custom models built with `useDefaults: true` inherit `compatConfig` from the first matching bundled reference row (`github-copilot/gemini-4-argon`, which sets `supportsReasoningEffort: false, supportsDeveloperRole: false`). Under `api: openai-responses`, `resolveModelPolicy` (`dU`) checks `supportsReasoningEffort === false` and strips the `thinking` object to `undefined` (`null` in `omp models --json`), silently discarding `models.yml`'s `thinking: { mode: effort, efforts: [low, medium, high] }`. Setting `compat: { supportsReasoningEffort: true, supportsDeveloperRole: true }` at the `providers.omniroute` level overrides the inherited `github-copilot` compat flags for all OmniRoute models. Meanwhile, `x-omniroute-no-memory: "true"` instructs OmniRoute's `isNoMemoryRequested` check (`open-sse/handlers/chatCore.ts:1135`) to skip gateway memory/skill injection.
- **Alternatives Considered**:
  - *Adding `promptCache: { short: 300, long: 3600 }` to `omniroute` models*: Rejected after binary inspection (`class w0e`, offset `157978969`) proved that `promptCache` triggers a background 1-token full-history replay timer every 4.5 minutes under `providers.cacheWarming: "idle"`, wasting scarce Google AI Ultra quota.

### 2. Role Rebalancing & Background Concurrency Isolation in `config.yml`
- **Decision**:
  - Set `modelRoles.smol: omniroute/gemini-3.8-flash-high:high` while keeping `modelRoles.default: omniroute/gemini-4-argon` and `modelRoles.plan: google-antigravity/gemini-4-argon:high` (and omitting `modelRoles.memory`).
  - Strip `:high` from `modelRoles.judge: typesafe/jev-1.14.0` and add `ollama` to `disabledProviders: [openrouter, lm-studio, llama.cpp, vscode, ollama]`.
  - Set `prewalk: { enabled: false, auto: off, into: "@smol", autoTarget: "@smol" }`, `title: { generator: tiny }`, and `memories: { stage1Concurrency: 2 }`.
- **Rationale**: In OMP's local memory pipeline (`_I` & `aJ`, offset `154822912`), Phase 1 uses `fallbackRole: "default"` and Phase 2 uses `fallbackRole: "smol"` (`modelRoles.memory` is only read by `mnemopi`). Routing `smol` to the 15-account `gemini-3.8-flash-high` pool shifts `@smol` subagents, `async.widgets` (`modelRoles.widget` defaults to `@smol`), and Phase 2 memory consolidation off the 2–3 Ultra accounts. Setting `title.generator: "tiny"` stops `title-generator` from forking the primary `gemini-4-argon` session model, and reducing `memories.stage1Concurrency` from `8` to `2` prevents startup Phase 1 extraction from saturating the Ultra pool. Disabling default `prewalk` prevents unconditional same-session handoffs and read-only prewalk continuation loops while preserving on-demand `--prewalk` and `/prewalk` support.

### 3. Resilience, Compaction & Git Guard Settings in `config.yml`
- **Decision**:
  - Set `retry.rateLimitWalksChain: true`, `retry.usageAwareFallback: true`, and `retry.usageReservePolicy: auto`.
  - Add `retry.fallbackChains.advisor`, `retry.fallbackChains.smol`, and `retry.fallbackChains['omniroute/*']` (`[google-antigravity/gemini-4-argon:high, omniroute/gemini-3.8-flash-high:high, google-antigravity/gemini-3.8-flash:high]`).
  - Set `compaction.reserveTokens: 65536`, `compaction.keepRecentTokens: 40000`, `compaction.modelThresholds: { "cockpit/*": 220000 }`, and `bash.gitGuard: true`.
- **Rationale**: `retry.rateLimitWalksChain: true` (introduced in OMP v18.13.3) allows turns carrying signed thinking blocks to walk `fallbackChains` immediately on HTTP 429 rather than burning 10 retries on a throttled endpoint. In `advisor.ts` (offset `159638535`), `retryFallbackChainKeys` passes `roleHint: "advisor"`, which resolves `retry.fallbackChains.advisor` before halting after 3 failed backlogs. `compaction.modelThresholds['cockpit/*']: 220000` triggers OMP's client-side compaction before Cockpit's 244,800-token (90% of 272k) server threshold. `bash.gitGuard: true` protects shared workspace checkouts against destructive git commands while snapshotting discarded worktree state to `refs/omp/discarded`.

### 4. WAL-Safe `agent.db` Credential Pruning & Isolated-Profile Smoke Gate Transaction Boundary
- **Decision**:
  - Before any live mutation, create timestamped `mode 0600` backups of `config.yml`, `models.yml`, `mcp.json`, `lsp.json`, and `agent.db` (via `sqlite3 "file:$HOME/.omp/agent/agent.db?mode=ro" ".backup '<backup-path>'"`).
  - Stage candidate `models.yml`, `config.yml`, `.env`, `agent.db`, and `models.db` in an isolated throwaway profile `/Users/androidteam/.omp/profiles/omp-v18-14-smoke/agent` (`mode 0700` dir, `0600` files) and verify:
    1. `omp --profile omp-v18-14-smoke models --json` reports `thinking: ["low", "medium", "high"]` on all 5 `omniroute/*gemini-4-argon*` models and `0` models under `ollama` or `openrouter`;
    2. Uncached `omp find` judge probes pass in both `zsh -lic` and stripped `zsh -fc` (`stats.requests > 0`, `stats.failed == 0`);
    3. Direct attributed `--no-prewalk --mode json --no-session` smoke probes with empty fallback chains succeed for `omniroute/gemini-4-argon`, `omniroute/gemini-3.8-flash-high`, and `google-antigravity/gemini-4-argon:high`.
  - Apply live `agent.db` pruning inside a single `PRAGMA busy_timeout=5000; BEGIN IMMEDIATE; ... COMMIT;` transaction deleting only `auth_credential_blocks` and `auth_credentials` where `provider='google-antigravity' AND identity_key='email:vicgnome19091@gmail.com'`.
  - Atomically replace `models.yml`, `config.yml`, `mcp.json` (adding `"$schema"`, `"type": "stdio"`, `"timeout": 300000` while preserving `env.MCPR_TOKEN`), and `lsp.json` via same-directory temporary files (`os.replace`, preserving `0600` on `models.yml`/`config.yml`/`mcp.json` and `0644` on `lsp.json`, never touching `config.yml.lock`), and remove the throwaway smoke profile plus the 3 stale `omp-fresh-*` profiles.

## Risks / Trade-offs

- **[Risk] Concurrent OMP sessions writing `config.yml` or `agent.db` during apply** → **Mitigation**: Verify MD5 hashes before replacement, never touch `config.yml.lock`, use same-directory atomic `os.replace`, and execute `agent.db` deletion inside `PRAGMA busy_timeout=5000; BEGIN IMMEDIATE;` after a read-only `.backup`.
- **[Risk] Removing the wrong `google-antigravity` OAuth row** → **Mitigation**: Scope the `DELETE` strictly by `provider = 'google-antigravity' AND identity_key = 'email:vicgnome19091@gmail.com'` and assert before/after counts (`16 -> 15` active rows).

## Migration Plan

1. Take timestamped backups under `/Users/androidteam/.omp/agent/backups/` (`mode 0700` dir, `0600` files).
2. Run isolated-profile validation in `/Users/androidteam/.omp/profiles/omp-v18-14-smoke/agent` (`zsh -lic` and `zsh -fc`).
3. Apply atomic updates to `/Users/androidteam/.omp/agent/{models.yml,config.yml,mcp.json,lsp.json}` and WAL-safe `DELETE` on `/Users/androidteam/.omp/agent/agent.db`.
4. Remove `/Users/androidteam/.omp/profiles/omp-v18-14-smoke` and `/Users/androidteam/.omp/profiles/omp-fresh-{cockpit,giaoduc,shopapikey}`.
5. Verify live catalog, role resolution, judge probe, and zero 403 warnings in fresh session logs; on any failure, restore backups atomically and verify MD5 parity.
