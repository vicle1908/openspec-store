# Proposal

## Why

Oh My Pi (`omp` v18.14.1) on this workstation suffers from eight verified configuration and catalog defects across `~/.omp/agent/` (`models.yml`, `config.yml`, `mcp.json`, `lsp.json`, `agent.db`, and `~/.omp/profiles/`) and OpenSpec/Wiki documentation that silently strip reasoning-effort tiers from `omniroute/gemini-4-argon*`, inject unwanted `Memory context:` prefixes into prompts, starve the 2–3 Google AI Ultra (`g1-ultra-tier`) accounts with background workloads (causing 267 provider `503` errors and 162 skill-compression failures), poll a permanently 403-rejected OAuth credential 346 times, and leave historical spec clauses in conflict with live runtime state. Optimizing `~/.omp/agent/` to follow official OMP v18.14.1 schema semantics and modern resilience best practices eliminates Ultra-pool contention, restores native reasoning effort on `gemini-4-argon*`, hardens MCP/LSP/git-guard settings, and aligns OpenSpec, Wiki, and Notion documentation.

Specifically:
1. **Silent `thinking: null` Stripping on `omniroute/*gemini-4-argon*` (`~/.omp/agent/models.yml`)**: Even though `models.yml` declares `thinking: { mode: effort, efforts: [low, medium, high] }` on `gemini-4-argon`, `gemini-4-argon-high`, `gemini-4-argon-medium`, `gemini-4-argon-low`, and `nx/gemini-4-argon`, OMP's `custom-models.ts` (`useDefaults: true`) matches `gemini-4-argon` against the first bundled 1M-context reference row (`github-copilot/gemini-4-argon`), inheriting `compatConfig: { supportsReasoningEffort: false, supportsDeveloperRole: false }`. Because `omniroute` uses `api: openai-responses`, `resolveModelPolicy` sees `supportsReasoningEffort === false` and strips the `thinking` object to `null` in `omp models --json`.
2. **OmniRoute `Memory context:` Prefix Injection & Unused `equivalence:` Root Key (`~/.omp/agent/models.yml`)**: Neither `providers.omniroute` nor `providers.omniroute-anthropic` sets `headers: { "x-omniroute-no-memory": "true" }`, causing OmniRoute (`open-sse/handlers/chatCore.ts`) to prepend `Memory context:` into user prompts and bust prefix caches. Additionally, `models.yml` retains an ignored root-level `equivalence:` key (`omp://models.md` documents `providers` as the only consumed root key). *(Note: `promptCache` is intentionally omitted on `providers.omniroute` so OMP's background `cacheWarming` timer does not send 1-token replay requests against Ultra accounts every 4.5 minutes while idle.)*
3. **Ultra Account Pool Contention & Same-Model Prewalk Loop (`~/.omp/agent/config.yml`)**: `modelRoles.default` (`omniroute/gemini-4-argon`) and `modelRoles.smol` (`omniroute/gemini-4-argon:high`) both target the 2–3 Ultra `agy` accounts instead of routing fast/background work (`@smol`, Phase 2 local-memory consolidation, and `async.widgets`) to the 15-account `omniroute/gemini-3.8-flash-high` pool. Compounding this:
   - `prewalk.enabled: true` unconditionally arms prewalk on every new session (`into: "@smol"`), injecting planning nudges only to perform a same-model handoff (`gemini-4-argon` -> `gemini-4-argon:high`) and causing read-only prewalk continuation loops;
   - `title.generator` defaults to `"fork"` (forking the active `gemini-4-argon` session model and logging 6 `503` title errors);
   - `memory.backend: local` defaults to `memories.stage1Concurrency: 8` on `modelRoles.default` (bursting 8 concurrent extraction requests onto the Ultra pool at startup and logging `Memory phase1 stage1 job failed: 503`).
4. **Resilience, Rate-Limit Chain Walking & Fallback Coverage (`~/.omp/agent/config.yml`)**: `retry.rateLimitWalksChain` (added in v18.13.3) and `retry.usageAwareFallback` both default to `false`, causing turns with signed thinking to retry a rate-limited model up to `maxRetries: 10` before walking `retry.fallbackChains`; `retry.fallbackChains` lacks role entries for `advisor` (which resolves `roleHint: "advisor"` in `advisor.ts` and logged 138 debug failures / 3 halts during container restarts) and `smol`, as well as an `omniroute/*` wildcard chain.
5. **Compaction Sizing, Judge Suffix, Ollama Chat Pollution & Git Guard (`~/.omp/agent/config.yml`)**: `compaction.reserveTokens: 16384` and `keepRecentTokens: 20000` are undersized for 900k–1M context models and lack `compaction.modelThresholds` for 272k Cockpit models; `modelRoles.judge` carries a non-canonical `:high` suffix (`typesafe/jev-1.14.0:high` on a `kind: judge`, `reasoning: false` runner); `ollama` is not in `disabledProviders` (exposing local embedding model `ollama/nomic-embed-text:latest` as a chat model); and `bash.gitGuard` defaults to `false` in a multi-agent workspace.
6. **Rejected Antigravity OAuth Account & Stale Throwaway Profiles (`~/.omp/agent/agent.db`, `~/.omp/profiles/`)**: `agent.db:auth_credentials` row `id=4` (`email:vicgnome19091@gmail.com`) is permanently rejected with `HTTP 403 Forbidden` (332 usage-fetch warnings and 14 model-discovery warnings in `~/.omp/logs/`), while 15 other `google-antigravity` OAuth accounts are healthy. Furthermore, 3 stale throwaway smoke profiles (`~/.omp/profiles/omp-fresh-{cockpit,giaoduc,shopapikey}`) retain ~60 MB of old credential-bearing `agent.db` and `models.db` copies.
7. **MCP Schema/Timeout & Python 3.15 LSP Drift (`~/.omp/agent/mcp.json`, `~/.omp/agent/lsp.json`)**: `~/.omp/agent/mcp.json` omits `"$schema"`, `"type": "stdio"`, and `"timeout"` (defaulting to 30,000 ms, which truncates long MCP Router operations like GitNexus or Tavily deep research), and `~/.omp/agent/lsp.json` still sets `basedpyright.settings.python.version: "3.14"` instead of `"3.15"` after the workspace-wide CPython `3.15.1` migration.
8. **OpenSpec Spec Tension & Wiki/Notion Documentation Lag**: `openspec/specs/omp-provider-routing/spec.md` and `omp-fresh-shell-contract/spec.md` retain conflicting historical role assertions (`phanmemvip/gpt-5.6-sol:max` vs `google-antigravity/gemini-4-argon` vs `omniroute/gemini-4-argon`), un-suffixed fallback targets, `prewalk.auto: "suggest"`, `memories` top-level omission wording, and conflicting Cockpit `imageCountBudget: 20` vs text-only `input: [text]` scenarios, while `~/Developer/wiki/entities/omp.md` (Notion page `40ac4b21-deb4-8159-b891-cb85a17a2d73`) lacks the v18.14.1 runtime, role routing, and resilience architecture.

### Non-Goals

- Changing the primary default model (`modelRoles.default: omniroute/gemini-4-argon`), `modelRoles.plan` (`google-antigravity/gemini-4-argon:high`), or `modelRoles.judge` (`typesafe/jev-1.14.0`).
- Adding `promptCache` to `providers.omniroute` models (which would trigger OMP's background `cacheWarming` 1-token replay loop against scarce Ultra accounts) or adding `modelRoles.memory` (which `memory.backend: local` does not read).
- Modifying OmniRoute container combos, account pools, or tracked files in `/Users/androidteam/Omniroute`.
- Deleting or rotating any of the 15 healthy `google-antigravity` OAuth credentials, `typesafe`, `parallel`, `.env` API keys, or the `MCPR_TOKEN` value in `~/.omp/agent/mcp.json`.
- Modifying `/Users/androidteam/Developer/.claude/settings.json` (owned by Claude Code) or any Go, Python, or mobile application source code.

## What Changes

- **Restore `omniroute/*gemini-4-argon*` reasoning effort and opt out of OmniRoute prompt-memory injection in `~/.omp/agent/models.yml`**:
  - Add `headers: { "x-omniroute-no-memory": "true" }` to `providers.omniroute` and `providers.omniroute-anthropic`.
  - Add `compat: { supportsReasoningEffort: true, supportsDeveloperRole: true }` to `providers.omniroute` so `omp models --json` preserves `thinking: ["low", "medium", "high"]` on all 5 `gemini-4-argon*` models instead of inheriting `supportsReasoningEffort: false` from `github-copilot/gemini-4-argon`.
  - Remove the unused root-level `equivalence:` block from `~/.omp/agent/models.yml`.
- **Rebalance `@smol`, prewalk, title generation, compaction, and resilience in `~/.omp/agent/config.yml`**:
  - Route `modelRoles.smol` to `omniroute/gemini-3.8-flash-high:high` (routing fast subagents, `async.widgets`, and Phase 2 local-memory consolidation to the 15-account Flash pool) while keeping `modelRoles.default: omniroute/gemini-4-argon`, `modelRoles.plan: google-antigravity/gemini-4-argon:high`, and stripping the non-canonical `:high` suffix from `modelRoles.judge: typesafe/jev-1.14.0`.
  - Add `ollama` to `disabledProviders` (`[openrouter, lm-studio, llama.cpp, vscode, ollama]`) so local Ollama embedding models (`nomic-embed-text:latest`) are not discovered as chat models.
  - Set `prewalk: { enabled: false, auto: off, into: "@smol", autoTarget: "@smol" }` so prewalk only activates on explicit `--prewalk` / `/prewalk` rather than forcing an unconditional handoff on every session.
  - Set `title: { generator: tiny }` and `memories: { stage1Concurrency: 2 }` so session titles and startup local-memory extraction no longer burst requests against the 2–3 Ultra `gemini-4-argon` accounts.
  - Tune `compaction` (`reserveTokens: 65536`, `keepRecentTokens: 40000`, `modelThresholds: { "cockpit/*": 220000 }`) and enable `bash.gitGuard: true`.
  - Enable `retry.rateLimitWalksChain: true`, `retry.usageAwareFallback: true`, and `retry.usageReservePolicy: auto`, and add `retry.fallbackChains` entries for `advisor`, `smol`, and `omniroute/*` wildcard alongside existing exact-model chains.
- **Prune rejected Antigravity OAuth credential `id=4` and stale throwaway profiles**:
  - Remove the permanently 403-rejected `google-antigravity` credential row (`id=4`, `identity_key='email:vicgnome19091@gmail.com'`) and any associated `auth_credential_blocks` rows from `/Users/androidteam/.omp/agent/agent.db` inside a WAL-safe transaction after taking a `.backup` snapshot, leaving the 15 healthy `google-antigravity` OAuth accounts intact.
  - Delete the 3 leftover throwaway smoke profile directories `/Users/androidteam/.omp/profiles/omp-fresh-{cockpit,giaoduc,shopapikey}`.
- **Harden `~/.omp/agent/mcp.json` and align `~/.omp/agent/lsp.json` with Python 3.15**:
  - Add `"$schema"`, `"type": "stdio"`, and `"timeout": 300000` (5 minutes) to `/Users/androidteam/.omp/agent/mcp.json` (`mode 0600` and existing `env.MCPR_TOKEN` preserved untouched).
  - Update `servers.basedpyright.settings["python.version"]` from `"3.14"` to `"3.15"` in `/Users/androidteam/.omp/agent/lsp.json`.
- **Reconcile OpenSpec specs and sync Wiki + Notion Knowledge Hub**:
  - Reconcile `omp-provider-routing`, `omp-fresh-shell-contract`, and `lsp-user` specs so historical role-binding, fallback suffix, prewalk, `memories.stage1Concurrency`, and Cockpit `imageCountBudget` contradictions are superseded in place.
  - Update `/Users/androidteam/Developer/wiki/entities/omp.md` with the v18.14.1 runtime, role routing, and resilience architecture and sync to Notion (`40ac4b21-deb4-8159-b891-cb85a17a2d73`).

## Capabilities

### New Capabilities
*(None — all changes refine existing OMP routing, fresh-shell/credential, and user-LSP capabilities.)*

### Modified Capabilities
- `omp-provider-routing`: Add OmniRoute `x-omniroute-no-memory` headers, `compat` reasoning-effort preservation for `gemini-4-argon*`, removal of unused `equivalence` root key, `smol`/`judge` role refinements, `ollama` provider disablement, `prewalk`/`title`/`memories.stage1Concurrency`/`compaction`/`bash.gitGuard` runtime tuning, `retry.rateLimitWalksChain` + `usageAwareFallback` + `advisor`/`smol`/`omniroute/*` fallback chains, and in-place modification of conflicting historical role, fallback, prewalk, `memories`, and `imageCountBudget` requirements.
- `omp-fresh-shell-contract`: Require pruning of the rejected `google-antigravity` OAuth credential (`email:vicgnome19091@gmail.com`), cleanup of leftover throwaway `~/.omp/profiles/omp-fresh-*` directories, `mcp.json` (`0600`) explicit `$schema`, `type: "stdio"`, and `timeout: 300000` while preserving `env.MCPR_TOKEN`, and alignment of default-role supersession with `omniroute/gemini-4-argon`.
- `lsp-user`: Require `~/.omp/agent/lsp.json` to configure `basedpyright.settings.python.version: "3.15"` in alignment with the workspace Python 3.15.1 standard.

## Impact

- **Ownership Boundaries**:
  - **OMP User Agent Configuration (`/Users/androidteam/.omp/`)**: `/Users/androidteam/.omp/agent/models.yml`, `/Users/androidteam/.omp/agent/config.yml`, `/Users/androidteam/.omp/agent/mcp.json`, `/Users/androidteam/.omp/agent/lsp.json`, `/Users/androidteam/.omp/agent/agent.db`, and cleanup of `/Users/androidteam/.omp/profiles/omp-fresh-*`.
  - **Central OpenSpec Store (`/Users/androidteam/Developer/platform/openspec-store/`)**: Delta and synced specs under `openspec/specs/{omp-provider-routing,omp-fresh-shell-contract,lsp-user}/spec.md`.
  - **Workstation Knowledge (`/Users/androidteam/Developer/wiki/` & Notion)**: `/Users/androidteam/Developer/wiki/entities/omp.md` and Notion page `40ac4b21-deb4-8159-b891-cb85a17a2d73`.
