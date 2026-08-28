# Proposal: Extend OmniRoute `sh/*` Models to Remaining Supported Agent CLIs

## Why

The archived change `configure-omniroute-sh-models-across-agent-clis` (commits 41f8c1d, 6e6da66, eefc69e) registered the two approved OmniRoute models (`sh/gpt-5.6-sol` and `sh/Claude-Fable`) in pi, goose, and kimi, and confirmed omp and Kilo already carried `sh/*` routing. Four installed coding-agent CLIs with documented OmniRoute-compatible mechanisms still lack that registration: OpenCode, Droid, Grok, and Codex. This change extends the same clean-break `sh/*` routing to those four, registration-only, without changing any default model.

## What Changes

- Register the two live OmniRoute `sh/*` models in OpenCode, Droid, Grok, and Codex using each CLI's official provider mechanism.
- Use environment-backed `OMNIROUTE_API_KEY` indirection and preserve existing providers and defaults.
- Use Grok's proven Messages backend and Codex's required Responses provider configuration, with isolated real sentinel verification.

## Scope

This change SHALL:

- register `sh/gpt-5.6-sol` and `sh/Claude-Fable` in OpenCode, Droid, Grok, and Codex through each CLI's official provider mechanism;
- use the OmniRoute endpoint `http://localhost:20128/v1` and reference `OMNIROUTE_API_KEY` through environment indirection;
- preserve every existing provider and every default model selection in each mutated file;
- capture a mode-600 backup and SHA-256 hash for each target file before mutation;
- verify each changed CLI with one isolated real sentinel call and roll back independently on failure.

This change SHALL NOT:

- mutate the configured baselines: Kilo, Pi, OMP, Goose, Kimi;
- mutate prime-agent (owned by `add-omniroute-prime-agent-provider`);
- mutate cline (no env-indirection field found), Copilot, Cursor Agent, Auggie, AGY, Qoder (unsupported/unconfigured), or Claude Code (wrapper-owned);
- change any default model implicitly;
- add retired `dlg/*` routes or literal credentials to any configuration.

## Support matrix (2026-08-28, read-only inspection)

| CLI | Config surface | Current state | Planned registration | Default policy |
|---|---|---|---|---|
| OpenCode | ~/.config/opencode/opencode.json (mode 644) | providers cockpit,phanmemvip,shopapikey,zai; no omniroute | add `omniroute` provider (npm `@ai-sdk/openai`, baseURL `http://localhost:20128/v1`, apiKey `{env:OMNIROUTE_API_KEY}`) with both `sh/*` models | `model`/`small_model` unchanged |
| Droid | ~/.factory/settings.json (mode 600) | 3 customModels, all env-backed; none omniroute | add official BYOK `customModels` entries (baseUrl `http://localhost:20128/v1`, apiKey `${OMNIROUTE_API_KEY}`, provider `openai`) | session/mission defaults unchanged |
| Grok | ~/.grok/config.toml (mode 600) | providers cockpit,phanmemvip,shopapikey; default `cockpit-sol` (web/session/fork defaults also changed externally before apply) | add `model_providers.omniroute` (env_key `OMNIROUTE_API_KEY`) plus model aliases for both `sh/*` IDs | current defaults unchanged |
| Codex | ~/.codex/config.toml (mode 600) | top model `gpt-5.6-sol` via codex_local_access | add `model_providers.omniroute` (base_url `http://localhost:20128/v1`, wire_api `responses`, env_key `OMNIROUTE_API_KEY`) | top-level model unchanged |

Baselines (verify only): Kilo, Pi, OMP, Goose, Kimi.
Excluded: prime-agent, cline, Copilot, Cursor Agent, Auggie, AGY, Qoder, Claude Code.

## Capabilities

### Modified Capabilities

- `coding-cli-provider-registry`: adds `sh/gpt-5.6-sol` + `sh/Claude-Fable` registration requirements for the three registry consumers mutated here (opencode, grok, droid).
- `omniroute-agent-cli-routing`: adds a Codex registration requirement (Codex is outside the nine-consumer registry).

## Impact

- Four user-level configuration files change, one at a time, each with a mode-600 backup and atomic rollback path.
- `OMNIROUTE_API_KEY` remains the sole shared OmniRoute credential source; no literal credentials are introduced.
- Existing providers and defaults are preserved in every mutated file.
- Unrelated OpenSpec work in the store remains untouched.

## Known risks

- OmniRoute emits a malformed bare `response.in_progress` SSE heartbeat before the valid Responses event; strict Responses-dialect decoders can fail with `serialization error: missing field sequence_number`. Grok's OmniRoute provider was therefore switched to the proven `messages` backend, while Codex remains on `responses` and passed its final sentinels.
- Direct protocol testing also found intermittent/non-stream `chat` and `messages` upstream-empty-response failures; the approved CLI paths use streaming and passed the final real sentinels.
- OpenCode's active file is mode 644; this change backs it up at mode 600 but does not change active-file permissions (separate security follow-up).
- Goose's `config.yaml` selected model (`gpt-5.6-sol`) does not match its catalog name (`sh/gpt-5.6-sol`); dormant because `active_provider` is not custom_omniroute. Documented follow-up; not mutated here.

## Approval gate

The user directive "Follow openspec workflow configure omniroute sh models for other cli also" authorizes registration-only configuration of the remaining supported CLIs with no default-model changes, matching the approval recorded in the archived change's task 3.2. Apply proceeds only after strict validation of this package passes.
