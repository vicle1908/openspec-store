# Proposal: integrate-omp-three-provider-routing

## Why

omp (oh-my-pi) v17.2.15 is installed but configured with only one provider (`omniroute` via `localhost:20128`). We have three existing providers — shopapikey, giaoduc, cockpit — already wired for Claude Code and Hermes. Registering them in omp gives us access to `fable-5`, `Advance`, and `gpt-5.6-luna` without duplicating credential infrastructure.

## Provider Ground Truth (validated 2026-08-12)

| Provider | Base URL | Protocol | Model ID | Credential Env Var | Status |
|---|---|---|---|---|---|
| shopapikey | `https://api.phanmemvip.shop` | Anthropic Messages | `fable-5` | `HERMES_CUSTOM_SHOPAPIKEY_API_KEY` | HTTP 200 confirmed |
| giaoduc | `https://api.giaoduc.online` | Anthropic Messages | `Advance` | `HERMES_CUSTOM_GIAODUC_API_KEY` | HTTP 200 confirmed |
| cockpit | `http://localhost:8787` | Anthropic Messages (adapter) | `gpt-5.6-luna` | `HERMES_CUSTOM_COCKPIT_API_KEY` | HTTP 200 confirmed |
| omniroute | `http://localhost:20128/v1` | OpenAI Responses | `dlg/kimi-k2.6` etc. | (configured) | existing, keep |

**Protocol correction:** All three providers speak Anthropic Messages (`/v1/messages`). The earlier assumption that cockpit uses OpenAI Responses is stale — the adapter at `localhost:8787` confirmed Anthropic Messages on live test. Model IDs (`fable-5`, `Advance`, `gpt-5.6-luna`) are canonical upstream IDs confirmed by response metadata. The `[1m]` suffix accepted by upstream APIs is treated as a provider-specific alias; use canonical IDs in omp until isolated-profile testing proves bracket notation works.

## Non-Goals

- Modifying Claude Code, Hermes, or any other agent's provider routing.
- Changing credentials or their storage location.
- Overwriting the existing `omniroute` provider block.
- Verifying model capability metadata (contextWindow, maxTokens) beyond what the APIs publish.

## Scope

1. Add three provider blocks to `~/.omp/agent/models.yml`.
2. Preserve the existing model-role assignments in `~/.omp/agent/config.yml`; role reassignment is deferred to a separate change.
3. Preserve the existing `omniroute` provider as fallback.
4. Validate with an isolated omp profile before touching live config.
