# Design

## Context
OMP interacts with OmniRoute through the OpenAI Responses protocol (`/v1/responses`) configured in `~/.omp/agent/models.yml`. OmniRoute manages multiple upstream providers, including Google Antigravity (`agy`), Codex, and the newly added Nexus provider (`nx` at `https://api.nexusmmo.store/v1`). Currently, OMP's execution roles in `~/.omp/agent/config.yml` rely heavily on `omniroute/gemini-3.8-flash-high`. Live investigation confirmed that `nx/deepseek-v4.1-flash` and `nx/deepseek-v4-pro` are operational and responsive, while `nx/Gemini 4 Argon` encounters intermittent upstream relay parameter validation errors (HTTP 400 in-stream). See `proposal.md` for the broader motivation.

## Goals / Non-Goals

**Goals:**
- Register `nx/deepseek-v4.1-flash`, `nx/deepseek-v4-pro`, and `nx/Gemini 4 Argon` in `~/.omp/agent/models.yml` with catalog-verified context and reasoning attributes.
- Reassign the fast `commit` role to `omniroute/nx/deepseek-v4.1-flash` in `~/.omp/agent/config.yml`.
- Establish explicit fallback chains in `retry.fallbackChains` for all newly registered OmniRoute Nexus selectors.
- Verify configuration end-to-end using an isolated OMP profile with zero fallback masquerade prior to live rollout.

**Non-Goals:**
- Mutating the OmniRoute Docker SQLite database (`combos` table); routing will be managed directly in OMP.
- Assigning `nx/Gemini 4 Argon` to automated execution roles (`default`, `task`, `plan`) while upstream relay validation remains unstable.
- Modifying non-OmniRoute provider blocks (`shopapikey`, `phanmemvip`, `cockpit`, `omniroute-anthropic`, `omniroute-chat`) or their authentication references.

## Decisions

### 1. Direct OMP Model Configuration over OmniRoute Combos
- **Decision:** Declare individual models under `providers.omniroute.models` (`omniroute/nx/deepseek-v4.1-flash`) rather than creating a virtual combo in OmniRoute's SQLite database.
- **Rationale:** Direct configuration requires zero mutation of the running container's SQLite database volume, preserves exact model attribution in OMP logs, and allows OMP's native `retry.fallbackChains` to govern failover deterministically.
- **OmniRoute Skills Alignment:** While OmniRoute's official `omni-combos-routing` skill provides `POST /api/combos` with 14 routing strategies (such as `priority` and `auto`), keeping routing client-side in OMP isolates configuration changes from container persistence. If multi-provider pooling for DeepSeek 4.1 (Nexus + Ollama Cloud) is requested later, `omni-combos-routing` defines the standard interface for creating that combo without schema divergence. Live model verification leverages the `omni-models` skill contract (`/api/v1/models` and `omniroute models nx --json`).
### 2. Conservative Role Allocation
- **Decision:** Bind `modelRoles.commit` to `omniroute/nx/deepseek-v4.1-flash`. Retain `omniroute/gemini-3.8-flash-high` as primary for `default`, `task`, `plan`, `slow`, `advisor`, `tiny`, `smol`, and `vision`.
- **Rationale:** DeepSeek V4.1 Flash provides high-speed reasoning MoE completions ideal for concise, analytical commit message generation (~6s turnaround). Primary reasoning and background memory workloads remain on the stable, high-quota Gemini 3.8 Flash pool.

### 3. Fail-Closed Fallback Chains
- **Decision:** Map every `omniroute/nx/*` selector to:
  1. `omniroute/gemini-3.8-flash-high`
  2. `google-antigravity/gemini-3.8-flash:high`
- **Rationale:** Ensures that if the Nexus upstream API experiences rate limits or network degradation, OMP seamlessly falls back to local and direct Antigravity routes without stalling agent turns.

### 4. Isolated Smoke Gate Verification
- **Decision:** Build a throwaway profile (`~/.omp/profiles/smoke-nx-gate/agent`) with empty fallback chains (`retry: {fallbackChains: {}}`) to smoke-test `nx/deepseek-v4.1-flash`.
- **Rationale:** Empty fallback chains guarantee that any successful response is strictly self-served by the Nexus model, preventing fallback masquerade from falsely passing verification gates.

### 5. Verification Patterns from OmniRoute Skills
- **Model Catalog Probing (`omni-models` / `cli-models`):** Authoritative model catalog validation is conducted via `bun ~/Omniroute/bin/omniroute.mjs models nx --json` and `GET /api/v1/models`, ensuring exact ID matching (`nx/deepseek-v4.1-flash`, `nx/Gemini 4 Argon`) and context window bounds prior to writing OMP configuration.
- **Routing Simulation (`omni-combos-routing`):** Dry-run routing validation via `POST /api/routing/simulate` evaluates model resolution and target fallback paths without triggering upstream token spend.
- **Inference & Observability (`omni-inference` / `omni-usage-logs`):** Verifies that streaming responses emit valid SSE tokens and that reasoning tokens are cleanly captured in usage metadata without tripping token limits.

## Risks / Trade-offs

- **Upstream Nexus API Availability:** Nexus is a third-party relay; network variance or rate limits could cause transient errors. *Mitigation:* Explicit fallback chains automatically route failed calls to Gemini 3.8 Flash.
- **DeepSeek Reasoning Token Budget:** DeepSeek V4.1 Flash generates internal chain-of-thought tokens that consume part of the completion budget. Setting a token limit $< 100$ causes premature truncation (upstream 502). *Mitigation:* `commit` tasks and standard agent prompts use sufficient output token bounds ($\ge 2048$ tokens).
- **Gemini 4 Argon Upstream Relay Issues:** Upstream relay parameter validation triggers HTTP 400 when standard client payloads are submitted. *Mitigation:* Argon 4 is added to the catalog for manual experimentation only and excluded from automated execution roles until stabilized.
