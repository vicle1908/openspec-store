# Replace giaoduc with phanmemvip (Codex Responses API)

## Why

The giaoduc provider (`api.giaoduc.online`, Anthropic Messages, model `Advance`)
returned `401 invalid_api_key` in OMP on 2026-08-25 and is being retired from the
workspace. Its replacement is the `phanmemvip` provider
(`https://api.phanmemvip.shop/v1`), which speaks the Codex Responses API
(`POST /v1/responses`, verified live: `gpt-5.6-sol` returned "pong") and is
already first-class in the Hermes config v39 (fallback chain #2, MoA references).
All consumer configs still route to giaoduc and must migrate to
`phanmemvip/gpt-5.6-sol` over the Responses API.

## What Changes

- **BREAKING**: Remove giaoduc as a routed provider from every consumer config;
  replace its role bindings with `phanmemvip/gpt-5.6-sol` (Codex Responses API,
  key `HERMES_CUSTOM_PHANMEMVIP_API_KEY`, 1M context).
- **Hermes** (`~/.hermes/config.yaml`): remove the `giaoduc` provider block;
  replace `giaoduc:Advance` references in MoA presets (`default`, `deep`,
  `fast`) with `phanmemvip:gpt-5.6-sol` at a **1:1 effort mapping**
  (`@high` → `@high`); the `deep` preset's giaoduc aggregator becomes
  `phanmemvip:gpt-5.6-sol` at `max` (1:1 with the prior `@max`).
- **OMP** (`~/.omp/agent/config.yml` + `models.yml`): **add** a `phanmemvip`
  provider block to `models.yml` (`api: openai-responses`,
  `baseUrl: https://api.phanmemvip.shop/v1`,
  `apiKey: HERMES_CUSTOM_PHANMEMVIP_API_KEY`, model `gpt-5.6-sol`, 1M context);
  **remove** the giaoduc block. Rebind `task` role from `giaoduc/Advance:xhigh`
  to `phanmemvip/gpt-5.6-sol:xhigh`; replace giaoduc entries in
  `retry.fallbackChains` with phanmemvip. Supersedes the in-progress
  `omp-model-role-fallback-tuning` change, whose premise (restore the giaoduc
  task role) is invalidated by this direction.
- **pi** (`~/.pi/agent/settings.json` + `models.json`): `defaultProvider`
  giaoduc → phanmemvip, `defaultModel` Advance → gpt-5.6-sol; add phanmemvip
  provider block (`api: openai-responses`); remove giaoduc block.
- **prime-agent** (`~/.prime/agent/models.json`): add phanmemvip provider block
  (`openai-responses`); remove giaoduc block.
- **grok** (`~/.grok/config.toml`): `default` model `giaoduc-advance` →
  `phanmemvip-sol`; add `[model_providers.phanmemvip]`
  (`api_backend = "responses"`, `env_key = HERMES_CUSTOM_PHANMEMVIP_API_KEY`,
  `base_url = https://api.phanmemvip.shop/v1`); add `[model.phanmemvip-sol]`;
  remove giaoduc provider and model entries.
- **goose** (`~/.config/goose/`): add `custom_phanmemvip.json`
  (`engine: openai`, `api_key_env: HERMES_CUSTOM_PHANMEMVIP_API_KEY` — sourced
  from the shared `~/.zshenv` credential loader, model `gpt-5.6-sol`); remove
  `custom_giaoduc.json`; update `config.yaml` providers map accordingly.
- **zshrc** (`~/.zshrc`): remove the `giaoduc()` Claude launcher and the
  `cline_giaoduc()` launcher. **No phanmemvip Claude launcher is added in this
  change** — shopapikey/Claude-Fable remains the only Anthropic-side Claude
  route for now; a phanmemvip Claude launcher (adapter-backed) is deferred to a
  later change.
- **claude** (`~/.claude/`): remove `profiles/giaoduc.json` and
  `helpers/giaoduc-key.sh`. No phanmemvip profile/helper added (deferred).
- **tdt-core** (repo): register `HERMES_CUSTOM_PHANMEMVIP_API_KEY` in
  `environment-key-registry.json` (`secret: true`, `provider: phanmemvip`);
  deregister `HERMES_CUSTOM_GIAODUC_API_KEY`.
- **Credential hygiene**: remove `HERMES_CUSTOM_GIAODUC_API_KEY` from
  `~/.hermes/.env` after all consumers are migrated and verified.

Non-goals:

- No changes to shopapikey, cockpit, antigravity, or omniroute providers.
- No `fable-5` → `Claude-Fable` rename rollout (separate follow-up change).
- No OmniRoute repair or `dlg/*` model remapping (separate follow-up).
- No phanmemvip Claude Code launcher or claude-code-provider-adapter changes
  (deferred; shopapikey/Claude-Fable stays the Anthropic-side route).
- kimi config is untouched (it has no giaoduc references).

## Capabilities

### New Capabilities
- None.

### Modified Capabilities
- `hermes-moa-configuration`: MoA preset references and the deep/default-2
  aggregator change from `giaoduc:Advance` to `phanmemvip:gpt-5.6-sol` at a
  1:1 effort mapping; direct fallback chain swaps giaoduc for phanmemvip;
  context-window ownership validation set swaps giaoduc for phanmemvip.
- `omp-provider-routing`: provider blocks (giaoduc removed, phanmemvip added
  with `openai-responses`), `task` role rebinding, wire-protocol and canonical
  model ID requirements, fallback-chain membership; the prior change-scoped
  "no external system modification" constraint is removed because this change
  intentionally spans Hermes, Claude, goose, grok, pi, prime-agent, and
  tdt-core surfaces.
- `claude-code-provider-profile-resolution`: giaoduc profile/helper scenarios
  removed (no phanmemvip profile added in this change); the profile set
  becomes shopapikey + cockpit.
- `claude-code-provider-routing`: giaoduc launcher removed from the launcher
  set (no phanmemvip launcher added in this change); the launcher set becomes
  shopapikey + cockpit.
- `register-custom-provider-credentials`: registry gains
  `HERMES_CUSTOM_PHANMEMVIP_API_KEY` bound to `phanmemvip` and loses the
  giaoduc entry (still three custom keys: shopapikey, phanmemvip, cockpit).
- `provider-model-profile-resolution`: illustrative example scenarios that used
  giaoduc as the canonical bound-provider / fallback-alias example are updated
  to phanmemvip so the master schema spec stays consistent with the retired
  provider.

Not modified (giaoduc appears only in non-normative text, no requirement
changes): `agent-core-model-resolution` references giaoduc solely in its
Purpose line; its resolution requirements are provider-agnostic. The agent-core
runtime config migration (if any giaoduc binding exists) is tracked in
tasks.md, not as a spec delta.

## Impact

- **Config files (workstation)**: `~/.hermes/config.yaml`,
  `~/.omp/agent/{config,models}.yml`, `~/.pi/agent/{settings,models}.json`,
  `~/.prime/agent/models.json`, `~/.grok/config.toml`,
  `~/.config/goose/{config.yaml,custom_providers/}`, `~/.zshrc`,
  `~/.claude/{profiles,helpers}/`, `~/.hermes/.env`.
- **Repos**: `tdt-core` (credential registry).
- **OpenSpec**: supersedes active change `omp-model-role-fallback-tuning`
  (abandon); 6 main specs receive deltas.
- **Risk**: any consumer still referencing giaoduc after credential removal
  fails closed with 401; the isolated-profile smoke-test gate (borrowed from
  the superseded change) must pass for every phanmemvip selector before live
  application and before the giaoduc key is removed from `~/.hermes/.env`.

## Decisions (locked)

1. **OMP**: add phanmemvip provider block AND remove giaoduc block (full swap).
   Supersedes/abandons `omp-model-role-fallback-tuning`.
2. **Claude Code**: keep only shopapikey/Claude-Fable for now. Remove the
   giaoduc launcher/profile/helper; do NOT add a phanmemvip Claude launcher in
   this change (deferred). No adapter changes.
3. **MoA**: 1:1 effort mapping (`giaoduc:Advance@high` →
   `phanmemvip:gpt-5.6-sol@high`; deep aggregator `@max` → `@max`).
4. **goose**: `api_key_env: HERMES_CUSTOM_PHANMEMVIP_API_KEY`, sourced from the
   shared `~/.zshenv` credential loader.
