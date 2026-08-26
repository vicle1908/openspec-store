# Migrate kimi and grok to phanmemvip (full migration)

## Why

Two consumer CLIs remain outside the phanmemvip migration: **kimi** (all four
custom models point at OmniRoute `dlg/*` IDs that no longer exist in the
catalog — OmniRoute recovered to healthy but its catalog changed; the
moonshot-ai fallback account is suspended for insufficient balance) and
**grok** (its shopapikey provider uses the Anthropic Messages backend, which
fails with `missing field signature` because phanmemvip's Messages responses
omit thinking signature fields — while phanmemvip serves `Claude-Fable` via
the Responses API successfully, verified live). This change completes the
migration for both surfaces.

## What Changes

- **kimi** (`~/.kimi-code/config.toml`): add a `phanmemvip` provider
  (`type = "openai_responses"`, `base_url = https://api.phanmemvip.shop/v1`,
  key `HERMES_CUSTOM_PHANMEMVIP_API_KEY`) with models `gpt-5.6-sol` and
  `Claude-Fable` (both 1M context, thinking-capable); set
  `default_model = "phanmemvip-sol"`; remove the four broken OmniRoute
  `dlg/*` model entries (`kimi-k2-6`, `gpt-5-5`, `deepseek-v4-pro`,
  `deepseek-v4-flash`) whose IDs no longer exist in the OmniRoute catalog.
  The `moonshot-ai` provider and `kimi-k2-thinking` model are preserved
  (account suspended — external blocker; config remains valid for when the
  account is restored).
- **grok** (`~/.grok/config.toml`): switch the shopapikey provider from
  `api_backend = "messages"` to `api_backend = "responses"` and remove the
  Anthropic-only `extra_headers` block, so `shopapikey-claude-fable` routes
  `Claude-Fable` through the Responses API (verified working) instead of the
  broken Messages path.
- **Spec**: extend `coding-cli-provider-registry` from seven to nine consumer
  CLIs (adding kimi and grok) with phanmemvip-via-Responses requirements.

Non-goals:

- No OmniRoute catalog remapping beyond removing dead `dlg/*` IDs from kimi.
- No moonshot-ai account remediation (billing issue, external).
- No changes to the other seven already-migrated CLIs.

## Capabilities

### New Capabilities
- None.

### Modified Capabilities
- `coding-cli-provider-registry`: the consumer CLI set expands from seven to
  nine (adds kimi, grok); phanmemvip-via-Responses and giaoduc-absence
  requirements gain kimi/grok scenarios; the Claude-Fable naming requirement
  gains a grok scenario.

## Impact

- **Config files**: `~/.kimi-code/config.toml`, `~/.grok/config.toml`.
- **OpenSpec**: 1 modified capability.
- **Risk**: kimi's literal `api_key` pattern is its existing convention (no
  env-var support for custom providers); backups precede all edits; per-CLI
  smoke tests gate archive.
- **External blockers recorded**: moonshot-ai account suspended (429
  insufficient balance); OmniRoute `aug/*` upstream requires `auggie` CLI
  login (502); OmniRoute github upstream in credential cooldown.
