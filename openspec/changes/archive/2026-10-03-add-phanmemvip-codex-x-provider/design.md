# Design

## Context

See proposal.md - Why.

Current state that shapes the approach:

- The Codex CLI config `~/.codex/config.toml` already coexists two providers selected by top-level `model`/`model_provider`: `codex_local_access` (cockpit local service, `http://localhost:51006/v1`, `wire_api = "responses"`) and `omniroute` (`http://localhost:20128/v1`, `wire_api = "responses"`). Both use `wire_api = "responses"`.
- `~/.codex/omniroute.config.toml` is the established **swapable profile** precedent: a standalone file applied by copying it over `config.toml`, leaving the main config's provider inventory and defaults unchanged. It selects `model = "sh/Claude-Fable.6-sol"` on the `omniroute` provider.
- The phanmemvip credential `HERMES_CUSTOM_PHANMEMVIP_API_KEY` is already exported in `~/.zshenv` and registered with `provider: "phanmemvip"`.
- The home `~/.claude/settings.json` currently provides the shopapikey (Fable) channel on `https://api.phanmemvip.shop` with a credential-free `apiKeyHelper`. The project-level `.claude/settings.json` is a separate, out-of-scope file.
- Exploration verified live against `https://api.phanmemvip.shop/v1`: `GET /v1/models` returns 200 with the key and lists `codex-x`; both `POST /v1/responses` and `POST /v1/chat/completions` return 200 for `codex-x`.

## Goals / Non-Goals

**Goals:**
- Make the phanmemvip provider selectable in Codex with the `codex-x` model at `xhigh` effort, using the existing omniroute swapable-profile pattern.
- Move the Claude Code home default to phanmemvip/codex-x.
- Zero new secret wiring and zero secret persistence.

**Non-Goals:**
- No new Claude Code zsh launcher function (launcher set unchanged).
- No change to the project-level `.claude/settings.json`.
- No change to `coding-cli-provider-registry` (Codex is outside the nine-CLI registry).

## Decisions

### Decision 1: `wire_api = "responses"`

Use `wire_api = "responses"` for the phanmemvip provider. Rationale: both existing Codex providers use `responses`, and the live probe returned HTTP 200 for `POST /v1/responses` with `model = "codex-x"`. Alternative considered: `wire_api = "chat"` — also returned 200, but `responses` matches the Codex-native convention already in use. The chat wire remains a fallback if a Responses-shaped request is rejected in a real session.

### Decision 2: Bare `codex-x`, no `[1m]` suffix

Use the bare model id `codex-x` in both the Codex profile and the Claude Code home settings. Rationale: `[1m]` is a Claude-Code context-window selector, and the `claude-code-provider-routing` spec explicitly states selector acceptance does not prove provider-side 1M capacity. codex-x is not a Claude model and its 1M capacity is unverified, so no `[1m]` is claimed. Alternative considered: `codex-x[1m]` — rejected pending 1M evidence.

### Decision 3: Swapable profile, not in-place default

Add `~/.codex/phanmemvip.config.toml` and leave the main `config.toml` inventory intact. Rationale: mirrors `omniroute.config.toml`, keeps the two existing providers' defaults untouched, and makes selection reversible by swapping the file. Alternative considered: make phanmemvip the permanent default in `config.toml` — deferred; the swapable profile follows the established launcher pattern requested by the operator. The additive `[model_providers.phanmemvip]` block is still added to the main `config.toml` so the provider is known when a profile references it, matching how `omniroute` already coexists there.

### Decision 4: Reuse the registered credential key

The provider uses `env_key = "HERMES_CUSTOM_PHANMEMVIP_API_KEY"` and no literal secret. Rationale: the key is already registered (`register-custom-provider-credentials`) and exported in `~/.zshenv`; no new wiring or JSON secret is needed.

### Decision 5: No forced model-catalog entry

No `cockpit-model-catalog.json` edit is made up front. Rationale: the gateway's `GET /v1/models` already lists `codex-x`, so Codex resolves it live. A catalog entry is a conditional fallback only if a real session cannot list it.

## Risks / Trade-offs

- [Responses wire rejected in a real session despite the probe] → Fall back to `wire_api = "chat"` (verified 200) and record the change.
- [`codex-x` not selectable without a catalog entry in some Codex build] → Add a `codex-x` entry to `cockpit-model-catalog.json` as the documented fallback.
- [Omitting `[1m]` under-serves 1M context if codex-x supports it] → Verify provider-side 1M capacity separately; add the suffix only with evidence.
- [Changing the Claude Code home default affects bare `claude` invocations] → Reversible by editing the home `settings.json` model values back to `Claude-Fable[1m]`.

## Migration Plan

1. Add the `[model_providers.phanmemvip]` block to `~/.codex/config.toml` (additive; keep existing blocks).
2. Create `~/.codex/phanmemvip.config.toml` with `model = "codex-x"`, `model_provider = "phanmemvip"`, `model_reasoning_effort = "xhigh"`, and the provider block.
3. Update the home `~/.claude/settings.json` model/alias values from `Claude-Fable[1m]` to `codex-x` (base URL, effort, and `apiKeyHelper` unchanged).
4. Verify: apply the profile, run a real Codex turn on phanmemvip/codex-x; confirm a bare `claude` session reports codex-x; confirm no secret appears in any JSON.

Rollback: restore the previous `~/.codex/config.toml` from its `.bak` and revert the home `settings.json` model values; no data migration is involved.

## Open Questions

- None blocking the specs, approach, or task breakdown. The `responses` vs `chat` and catalog questions are resolved by the conditional fallbacks above.
