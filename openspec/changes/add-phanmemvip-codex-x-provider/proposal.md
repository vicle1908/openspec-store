# Proposal

## Why

The phanmemvip provider (`https://api.phanmemvip.shop/v1`) is already the gateway behind the shopapikey channel (Fable model) across Claude Code and the nine consumer CLIs, and its API key (`HERMES_CUSTOM_PHANMEMVIP_API_KEY`) is already exported in `~/.zshenv`. But the **Codex CLI** (`~/.codex/config.toml`) has no phanmemvip provider at all — it only knows `codex_local_access` (cockpit) and `omniroute` — so there is no way to point Codex at the phanmemvip `codex-x` model. We also want the Claude Code global default (home `~/.claude/settings.json`) to use `codex-x` on phanmemvip instead of the Fable channel. This change adds a phanmemvip provider + `codex-x` model to Codex and updates the Claude Code home default, using the verified-live `responses` wire and a swapable profile that mirrors the existing `omniroute.config.toml` launcher pattern.

## What Changes

- Add a `[model_providers.phanmemvip]` block to the Codex CLI config (`~/.codex/config.toml`) alongside the existing `codex_local_access` and `omniroute` providers, targeting `https://api.phanmemvip.shop/v1` with `wire_api = "responses"` and `env_key = HERMES_CUSTOM_PHANMEMVIP_API_KEY`.
- Add a new swapable profile `~/.codex/phanmemvip.config.toml` that selects `model = "codex-x"`, `model_provider = "phanmemvip"`, `model_reasoning_effort = "xhigh"` (following the `omniroute.config.toml` launcher pattern: the main `config.toml` keeps its full provider inventory and is swapped, not edited in place, to switch providers).
- Update the home `~/.claude/settings.json` global default model from `Claude-Fable[1m]` to `codex-x` (phanmemvip base URL retained, credential-free `apiKeyHelper` pattern retained).
- No model-catalog edit required: `codex-x` is already returned by `GET /v1/models` on the phanmemvip gateway, so Codex resolves it live; a `cockpit-model-catalog.json` entry is a fallback only if a real session fails to list it.

## Capabilities

### New Capabilities
- `codex-cli-provider-routing`: Owns the Codex CLI provider inventory (`[model_providers.*]` in `~/.codex/config.toml`) and the swapable profile-launcher pattern. Defines the phanmemvip provider (base URL `https://api.phanmemvip.shop/v1`, `wire_api = "responses"`, `env_key = HERMES_CUSTOM_PHANMEMVIP_API_KEY`), the `codex-x` model selection with `xhigh` effort, and the `phanmemvip.config.toml` profile that selects it (mirroring `omniroute.config.toml`).

### Modified Capabilities
- `claude-code-provider-profile-resolution`: The home `~/.claude/settings.json` global default model changes from `Claude-Fable[1m]` to `codex-x` on the phanmemvip base URL, keeping the credential-free `apiKeyHelper` pattern. (Project-level `.claude/settings.json` is explicitly out of scope.)

## Impact

- Files: `~/.codex/config.toml` (additive `[model_providers.phanmemvip]`), new `~/.codex/phanmemvip.config.toml`, `~/.claude/settings.json` (home, model value change only).
- Credentials: reuses the existing `HERMES_CUSTOM_PHANMEMVIP_API_KEY` (already in `~/.zshenv`); no new secret wiring; no secret persisted in any JSON.
- Behavior: bare `claude` (home) now defaults to phanmemvip/codex-x; Codex can be switched to phanmemvip/codex-x via the swapable profile. The other launchers (shopapikey, cockpit, omniroute) and the Claude Code launcher set are unchanged.
- Verification dependency: a live `codex-x` response on `https://api.phanmemvip.shop/v1` over the `responses` wire was already confirmed returning HTTP 200 during exploration.

## Non-Goals

- No phanmemvip **Claude Code** zsh launcher function is added (the `claude-code-provider-routing` launcher set of shopapikey/cockpit/omniroute is unchanged).
- The project-level `/Users/androidteam/Developer/.claude/settings.json` is intentionally **not** modified or created by this change.
- The `coding-cli-provider-registry` (nine consumer CLIs) is unchanged; Codex is outside that registry.
