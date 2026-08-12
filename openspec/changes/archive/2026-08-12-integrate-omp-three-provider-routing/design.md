# Design: integrate-omp-three-provider-routing

## Architecture

omp resolves credentials per-provider through a layered chain:
CLI flag → `agent.db` stored key → OAuth → env var → `models.yml` `apiKey:` field.

We use the `models.yml` layer, referencing `HERMES_CUSTOM_*` env vars that already
exist in `~/.zshrc`. No new credential storage is introduced.

## Security Decision (2026-08-12)

The three `HERMES_CUSTOM_*_API_KEY` values were exposed in terminal output during
the research phase of this change. The user explicitly declined credential rotation:

> "Update changes, no need rotate. Just keep current keys. Prepare for execution"

This decision is recorded in the change artifacts. The existing credentials are
retained as-is. The rule that plaintext credential values must never be copied into
OpenSpec artifacts or `models.yml` (only env-var names) remains in force.

## Validated Provider Matrix

| Provider | Base URL | Wire Protocol | Model ID (canonical) | Credential Var | HTTP Verified |
|---|---|---|---|---|---|
| shopapikey | `https://api.phanmemvip.shop` | `anthropic-messages` | `fable-5` | `HERMES_CUSTOM_SHOPAPIKEY_API_KEY` | 200 |
| giaoduc | `https://api.giaoduc.online` | `anthropic-messages` | `Advance` | `HERMES_CUSTOM_GIAODUC_API_KEY` | 200 |
| cockpit | `http://localhost:8787` | `anthropic-messages` | `gpt-5.6-luna` | `HERMES_CUSTOM_COCKPIT_API_KEY` | 200 |
| omniroute | `http://localhost:20128/v1` | `openai-responses` | `dlg/*` | existing value preserved verbatim | existing |

**Protocol (validated 2026-08-12):** All three providers speak Anthropic Messages
(`/v1/messages`). The cockpit adapter at `localhost:8787` confirmed HTTP 200 on
`/v1/messages` and 404 on `/v1/responses` and `/v1/chat/completions`.

**Model IDs (smoke-tested):** Canonical selectors `shopapikey/fable-5`,
`giaoduc/Advance`, and `cockpit/gpt-5.6-luna` all returned successful responses
in isolated-profile testing. The `[1m]` suffixed variants accepted by upstream
APIs are out of scope for this rollout unless the user specifically requests them.

**Base URL convention:** omp uses `baseUrl` as-is (does not append `/v1`). The
Anthropic Messages protocol appends `/messages` internally.

**Metadata:** `reasoning`, `contextWindow`, `maxTokens`, and `cost` are intentionally
omitted. The minimal configuration that passed isolated testing contains only:
`baseUrl`, `apiKey`, `api`, `auth`, and `models[]` with `id`, `name`, `input`.

## Proposed models.yml Additions

The existing `omniroute` block is preserved verbatim (including its credential
configuration and `equivalence` section). Three new provider blocks are added
as siblings under `providers:`:

```yaml
providers:
  # === EXISTING (preserved) ===
  omniroute:
    baseUrl: http://localhost:20128/v1
    apiKey: <existing value preserved verbatim>
    api: openai-responses
    models:
      # ... (unchanged, 3 models)

  # === NEW: Three providers ===
  shopapikey:
    baseUrl: https://api.phanmemvip.shop
    apiKey: HERMES_CUSTOM_SHOPAPIKEY_API_KEY
    api: anthropic-messages
    auth: apiKey
    models:
      - id: fable-5
        name: fable-5 (shopapikey)
        input: [text]

  giaoduc:
    baseUrl: https://api.giaoduc.online
    apiKey: HERMES_CUSTOM_GIAODUC_API_KEY
    api: anthropic-messages
    auth: apiKey
    models:
      - id: Advance
        name: Advance (giaoduc)
        input: [text]

  cockpit:
    baseUrl: http://localhost:8787
    apiKey: HERMES_CUSTOM_COCKPIT_API_KEY
    api: anthropic-messages
    auth: apiKey
    models:
      - id: gpt-5.6-luna
        name: gpt-5.6-luna (cockpit)
        input: [text]
```

## Role Assignments

**NOT part of this change.** The existing `omniroute` roles are kept intact.
Role reassignment is separate work that requires its own approval.

## What Does NOT Change

- Claude Code provider routing (`~/.claude/profiles/*`, `~/.zshrc` launchers).
- Hermes provider routing (MoA config, `config.yaml`).
- Agent-core, tdt-core, or any Python agent LLM configuration.
- OmniRoute deployment or its models.
- Credential storage location (stays in `~/.zshrc` exports).
- `config.yml` modelRoles (all omniroute assignments preserved).
