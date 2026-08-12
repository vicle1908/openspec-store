# Design: use-native-cockpit-and-reassign-omp-model-roles

## Cockpit native routing

Hermes config defines Cockpit as:

- `base_url: http://localhost:51006/v1`
- `api_mode: codex_responses`
- `key_env: HERMES_CUSTOM_COCKPIT_API_KEY`
- default model: `gpt-5.6-luna`

Empirical omp testing established:

- `api: openai-responses` → `pong`, exit 0
- `api: openai-codex-responses` → `endpoint not supported`, exit 1
- Native `/v1/responses` → `pong` (confirmed)
- Native `/v1/chat/completions` → `pong` (confirmed)
- Native `/v1/models` returns empty list — models must be declared statically

Cockpit Tools.app (`/Applications/Cockpit Tools.app`) owns the process on
port 51006 via `cockpit-cliproxy`. The Docker adapter on host port 8788
(container port 8787) is a separate Claude Messages compatibility adapter
used by Claude Code and is not contacted by omp after this change.

## Port ownership

| Consumer | Host port | Transport | Owner |
|---|---|---|---|
| omp (after change) | 51006 | openai-responses | This change |
| Claude Code (adapter) | 8788 | anthropic-messages | setup-hermes-webui-tailscale-access |
| Hermes WebUI | 8787 (reused) | N/A | setup-hermes-webui-tailscale-access |

Docker Compose maps `127.0.0.1:8788:8787` — container port stays 8787.
This change must not revert the adapter port mapping, Claude profiles,
Docker Compose, or Hermes WebUI work.

## models.yml: cockpit block replacement

Current cockpit block:
```yaml
cockpit:
  baseUrl: http://localhost:8788
  apiKey: HERMES_CUSTOM_COCKPIT_API_KEY
  api: anthropic-messages
  auth: apiKey
  models:
    - id: gpt-5.6-luna
      name: gpt-5.6-luna (cockpit)
      input: [text]
```

Proposed cockpit block:
```yaml
cockpit:
  baseUrl: http://localhost:51006/v1
  apiKey: HERMES_CUSTOM_COCKPIT_API_KEY
  api: openai-responses
  auth: apiKey
  models:
    - id: gpt-5.6-luna
      name: gpt-5.6-luna (cockpit native)
      input: [text]
```

No other provider block changes. Shopapikey and giaoduc retain
`api: anthropic-messages`. OmniRoute retains its full block and
`equivalence` section.

## config.yml: role reassignment

Current roles (all OmniRoute, `dlg` route fails):
```yaml
modelRoles:
  default: omniroute/dlg/kimi-k2.6:high
  smol: omniroute/dlg/kimi-k2.6
  slow: omniroute/dlg/kimi-k2.6
  plan: omniroute/dlg/deepseek-v4-pro
  commit: omniroute/dlg/deepseek-v4-flash
```

Proposed roles:
```yaml
modelRoles:
  default: cockpit/gpt-5.6-luna:high
  smol: shopapikey/fable-5
  slow: cockpit/gpt-5.6-luna:max
  plan: cockpit/gpt-5.6-luna:max
  commit: shopapikey/fable-5
  task: giaoduc/Advance
```

Role selection rationale:

- `default: cockpit/gpt-5.6-luna:high` — Proven thinking level via omp,
  native transport, no adapter dependency. `:high` validated in isolated profile.
- `smol: shopapikey/fable-5` — Lightweight for title generation and
  classification. No thinking-level suffix.
- `slow: cockpit/gpt-5.6-luna:max` — Deepest reasoning for architectural
  decisions. `:max` validated in isolated profile.
- `plan: cockpit/gpt-5.6-luna:max` — Planning benefits from deep reasoning.
  `:max` validated.
- `commit: shopapikey/fable-5` — Lightweight for commit messages.
- `task: giaoduc/Advance` — Uses third provider for subagent work.

No automatic fallback has been demonstrated. If cockpit is unavailable,
`default`, `slow`, and `plan` roles fail until cockpit returns or the
user switches via `/model`.

## Per-file atomic replacement with coordinated rollback

Files are updated sequentially, not atomically as a pair:

1. Backup `models.yml` → replace cockpit block → verify parse
2. Backup `config.yml` → replace `modelRoles` → verify parse

If step 2 fails, step 1 is restored immediately. If any live verification
fails after both files are written, both are restored.

## Scope boundaries

This change modifies exactly two files:

- `~/.omp/agent/models.yml` — cockpit provider block only
- `~/.omp/agent/config.yml` — `modelRoles` section only

Explicitly unchanged:

- Hermes config (`~/.hermes/config.yaml`)
- Claude Code profiles (`~/.claude/profiles/*`)
- Shell launchers (`~/.zshrc`)
- Cockpit Tools.app configuration
- Docker Compose (`~/Developer/claude-code-provider-adapter/docker-compose.yml`)
- The adapter container and its host port 8788 mapping
- adapter-status.sh, start-adapter.sh, launchd plist
- agent-core, tdt-core, or any Python agent configuration
- OmniRoute provider definition in `models.yml`
- The `equivalence` section in `models.yml`
- All provider credentials (environment-variable references only)
