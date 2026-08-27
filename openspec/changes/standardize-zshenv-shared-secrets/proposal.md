# Proposal: standardize-zshenv-shared-secrets

## Why

Provider API keys and shared tool credentials are currently scattered across five
dotenv files with no single source of truth. Coding-agent CLIs (Claude Code,
Codex, OpenCode, Goose, Pi, Prime Agent, Droid) each resolve credentials through
different mechanisms, and the same key is duplicated — and in four cases has
already **drifted** — across files:

| Key | Files | Status |
|---|---|---|
| `EXA_API_KEY` | zshenv.secrets ≠ hermes.env ≠ tdt.env | 3-way drift |
| `BRAVE_SEARCH_API_KEY` | zshenv.secrets = tdt.env ≠ hermes.env | drift |
| `TAVILY_API_KEY` | hermes.env ≠ tdt.env | drift |
| `OMNIROUTE_API_KEY` | zshenv.secrets ≠ tdt.env | drift |

Consistent duplicates (no drift yet): `HERMES_CUSTOM_SHOPAPIKEY_API_KEY`
(hermes=tdt), `HERMES_CUSTOM_COCKPIT_API_KEY` (hermes=adapter).

Additional defects found during research:

1. `~/.zshenv` is mode **644** (world-readable) while it sources credential
   material.
2. Claude Code `apiKeyHelper` scripts use `set -a; . "$env_file"`, exporting the
   **entire** `~/.hermes/.env` (Telegram/Slack/Discord/GitHub tokens included)
   into the claude process instead of the single key they need.
3. `~/.pi/agent/models.json` cockpit provider has `apiKey` set to the **URL**
   (`http://localhost:51006/v1`) instead of a credential.
4. Stale `cline_*` launcher functions in `~/.zshrc` reference a `cline` binary
   that is not installed.
5. The `~/.config/agent-llm/load-hermes-custom-credentials.zsh` loader hardcodes
   `$HOME/.hermes/.env` instead of honouring `$HERMES_HOME`.

## What Changes

This is a config/tooling-only consolidation. No application source changes, no
delta specs.

**Tiered single-source-of-truth model** (user-approved):

- **Shared tier → `~/.zshenv`** (mode 600): the 6 `HERMES_CUSTOM_*_API_KEY`
  provider keys plus shared tool keys consumed by shell CLIs or multiple tools
  (`BRAVE_SEARCH_API_KEY`, `EXA_API_KEY`, `TAVILY_API_KEY`, `OMNIROUTE_API_KEY`,
  `API_KEY_SECRET`, `COPILOT_PROVIDER_API_KEY`, `NPMJS_TOKEN`,
  `POSTMAN_API_KEY`, `FIRECRAWL_API_KEY`, `OPENROUTER_API_KEY`, `GITHUB_TOKEN`).
- **Service-private tier stays in place** (not moved): platform gateway tokens
  (`TELEGRAM_*`, `DISCORD_*`, `SLACK_*`, `FEISHU_*`, `MATRIX_*`, `WHATSAPP_*`,
  `BUZZ_*`, `BROWSERBASE_*`) remain in `~/.hermes/.env`; TDT service config
  (`JIRA_*`, `GITLAB_*`, `ATLASSIAN_*`, ports/flags) remains in `~/.tdt/.env`;
  `HERMES_WEBUI_*` remains in the webui `.env`.

**Drift resolution (user-approved: newer value wins):**

- `EXA_API_KEY`, `BRAVE_SEARCH_API_KEY`, `TAVILY_API_KEY` ← `~/.hermes/.env`
  (mtime 2026-08-25 21:32, newest)
- `OMNIROUTE_API_KEY` ← `~/.zshenv.secrets` (mtime 2026-08-25 14:13, newer than
  tdt.env 2026-08-08)

**Consumer rewiring** follows each CLI's official mechanism:

- Claude Code: `apiKeyHelper` scripts rewritten to env-first single-variable
  extraction (never `set -a` source).
- Codex: `env_key` in `config.toml` model providers; the existing custom
  providers were migrated from literal `experimental_bearer_token` values.
- OpenCode: `auth.json` literal keys → `{env:VAR}` config interpolation.
- Goose / Droid: keychain/env-native — no change.
- Pi: fix cockpit `apiKey` URL bug → env var reference.
- launchd services (Hermes gateway, TDT ai-review/webhook-receiver, adapter):
  `ProgramArguments` wrapped in `/bin/zsh -c 'source ~/.zshenv && exec …'` so
  the shared tier reaches non-shell launchd processes.

## Impact

- Affected files: `~/.zshenv`, `~/.zshrc`, `~/.hermes/.env`, `~/.tdt/.env`,
  `~/Developer/claude-code-provider-adapter/.env`, `~/.claude/helpers/*.sh`,
  `~/.pi/agent/models.json`, `~/.config/opencode/opencode.json`,
  `~/.config/agent-llm/load-hermes-custom-credentials.zsh` (retired),
  4 LaunchAgent plists.
- No secret value is changed except the four drift resolutions (newer wins).
- Value preservation is hash-verified before and after every move.
- Rollback: timestamped backups of every mutated file; revert = restore
  backups and reload plists.
