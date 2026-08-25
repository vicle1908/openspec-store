# Canonicalize Claude-Fable model name and phanmemvip Responses transport

## Why

The shopapikey endpoint's model list is `Claude-Opus, Claude-Sonnet,
Claude-Fable, default` — `fable-5` no longer exists as a canonical ID (it is
only a server-side alias that resolves to `Claude-Fable`). Ten main specs and
twelve consumer config files still name `fable-5`, so the spec surface lags
the provider reality (verification warning W1 on
`replace-giaoduc-with-phanmemvip`). Additionally, the user has directed that
phanmemvip SHALL be consumed exclusively via the OpenAI Responses API, and
two verification findings need closure: the cockpit Claude profile spec names
port 8787 while the live profile uses the docker-mapped 8788 (W2), and the
goose phanmemvip provider carries `engine: "anthropic"` inherited from the
giaoduc template instead of the OpenAI engine that routes `gpt-5.6-sol`
through the Responses format (suggestion S1).

## What Changes

- Rename the shopapikey wire model `fable-5` → `Claude-Fable` in every
  consumer config: Claude `settings.json` + `shopapikey.json` profile
  (preserving the `[1m]` suffix), OMP `models.yml`/`config.yml`, pi
  `models.json`, prime-agent `models.json`, grok `config.toml`, goose
  `custom_shopapikey.json` + `config.yaml`, `cline_shopapikey` in `~/.zshrc`,
  `~/.tdt/config.yaml` (`shopapikey-fable` model), and the Hermes
  `providers.shopapikey` block.
- Update the affected main specs to the canonical `Claude-Fable` name:
  `hermes-moa-configuration` (aggregators/references), `omp-provider-routing`,
  `claude-code-provider-routing`, `claude-code-provider-profile-resolution`,
  `provider-model-profile-resolution`, `cli-provider-profile-resolution`,
  `flavor-composition-sdk`, and `omp-fresh-shell-contract` (which also drops
  its stale `giaoduc/Advance` reference left by the prior migration).
- Codify the transport rule: phanmemvip SHALL be accessed only via the
  OpenAI Responses API (`/v1/responses`) in every consumer; no consumer SHALL
  route phanmemvip through Anthropic Messages.
- **goose**: set `engine: "openai"` in `custom_phanmemvip.json` (goose 1.45
  auto-routes `gpt-5*` models to the Responses format via
  `is_openai_responses_model()`; valid engines are openai/anthropic/ollama).
- **Claude cockpit profile spec**: align the cockpit profile scenario with
  the live docker-mapped adapter port `http://localhost:8788`.

Non-goals:

- No changes to cockpit, omniroute, or antigravity providers.
- No OmniRoute repair or `dlg/*` remapping.
- No phanmemvip Claude Code launcher (still deferred).
- `agent-config` (`fable-5o` — unrelated typo string) and `developer-memory`
  (pre-existing corrupted text) are NOT touched.

## Capabilities

### New Capabilities
- None.

### Modified Capabilities
- `hermes-moa-configuration`: aggregator and reference model names change
  `shopapikey:fable-5` → `shopapikey:Claude-Fable` in all presets.
- `omp-provider-routing`: canonical model IDs, role selectors, and smoke
  scenarios change to `Claude-Fable`; adds a phanmemvip Responses-only
  transport requirement.
- `claude-code-provider-routing`: shopapikey launcher pin and wire-model
  scenario change to `Claude-Fable[1m]` / `model=Claude-Fable`.
- `claude-code-provider-profile-resolution`: settings/profile env values
  change to `Claude-Fable[1m]`; cockpit profile base URL scenario aligns to
  port 8788.
- `provider-model-profile-resolution`: illustrative alias/wire-model examples
  change to `Claude-Fable`.
- `cli-provider-profile-resolution`: canonical profile example changes to
  `Claude-Fable`.
- `flavor-composition-sdk`: default model string changes to
  `openai-chat:Claude-Fable`.
- `omp-fresh-shell-contract`: model entries update to `Claude-Fable` and the
  stale `giaoduc/Advance` reference is removed.

## Impact

- **Config files (workstation)**: `~/.claude/settings.json`,
  `~/.claude/profiles/shopapikey.json`, `~/.omp/agent/{models,config}.yml`,
  `~/.pi/agent/models.json`, `~/.prime/agent/models.json`,
  `~/.grok/config.toml`, `~/.config/goose/custom_providers/{custom_phanmemvip,custom_shopapikey}.json`,
  `~/.config/goose/config.yaml`, `~/.zshrc`, `~/.tdt/config.yaml`,
  `~/.hermes/config.yaml`.
- **OpenSpec**: 8 main specs receive deltas.
- **Risk**: `fable-5` currently still resolves (server-side alias), so the
  rename is non-breaking; per-surface smoke tests with `Claude-Fable` are the
  acceptance gate before archive.
