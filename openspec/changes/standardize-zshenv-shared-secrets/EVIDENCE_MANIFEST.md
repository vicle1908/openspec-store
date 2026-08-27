# Evidence Manifest: standardize-zshenv-shared-secrets

Date: 2026-08-27
Scope: macOS user shell, coding-agent CLI configuration, launchd wrappers.

## Safety and baseline

- Timestamped backup directory: `~/.config/agent-llm/backups/20260827-zshenv-shared-secrets/`
- Backup count: 17 files before migration; Codex `config.toml` backed up before its later migration.
- `~/.zshenv` permissions changed from 644 to 600 **before** writing credential values.
- Pre-migration canonical hashes are stored in:
  `~/.config/agent-llm/backups/20260827-zshenv-shared-secrets/pre-migration-hashes.txt`
- No credential values are included in this evidence artifact.

## Canonical shared tier

`~/.zshenv` now contains 17 exported shared-tier variables, including:

- 6 provider keys: Phanmemvip, Shopapikey, Cockpit, Antigravity,
  Localhost-51006, and Giaoduc.
- Shared tool keys: Brave, Exa, Tavily, OmniRoute, Firecrawl, OpenRouter,
  GitHub, API_KEY_SECRET, Copilot provider, NPMJS, and Postman.

`MCPR_TOKEN` is deliberately excluded from the shared tier. Hash comparison
showed different values for Hermes, OpenCode, Pi, and Qoder; it is
client/service-specific and remains owned by each client configuration.

## Verification results

| Gate | Result | Evidence |
|---|---:|---|
| `.zshenv` mode | PASS | mode 600 |
| `.zshenv` syntax | PASS | `zsh -n ~/.zshenv` |
| Shared key presence | PASS | 17/17 keys present |
| Shared key preservation | PASS | 17/17 post-write hashes equal canonical pre-migration hashes |
| Shell visibility | PASS | `zsh -c`, `zsh -ic`, `zsh -lc`, `zsh -ilc`: 4/4, each 17 set / 0 missing |
| `.zshenv` startup | PASS | prior measured clean-shell cost 0.01–0.02s; loader remains silent |
| Legacy `~/.zshenv.secrets` | PASS | deleted after migration; `.zshrc` source block removed |
| Legacy credential loader | PASS | source line removed; loader replaced with deprecation stub |
| Claude helpers | PASS | env-first and restricted fallback each return one line; no executable `set -a` |
| Pi providers | PASS | cockpit URL bug fixed; 4 providers use `${ENV_VAR}` templates; Pi resolver source verified |
| OpenCode | PASS | 3 shared providers use `{env:VAR}`; `shopapikey` and `cockpit` literal auth entries removed; provider models list resolves |
| Codex | PASS | custom providers use `env_key`; literal `experimental_bearer_token` entries removed; `codex --help` exit 0 |
| TDT dotenv duplicates | PASS | no shared-tier names remain in `~/.tdt/.env` |
| TDT services | PASS | both LaunchAgents reloaded; ai-review health 200, webhook health 200 |
| Adapter dotenv duplicate | PASS | repo `.env` deleted after container verification |
| Adapter container | PASS | key length 42 inside container; health 200; zero startup error lines |
| LaunchAgent plist structure | PASS | all 4 plists parse; wrapper is first ProgramArgument |
| Launchd wrapper | PASS | syntax clean; clean process test loaded shared keys; missing HOME/.zshenv fails closed |
| CCE config | PASS | mode hardened to 600; CCE remains a private literal-token exception because its CLI accepts literal TOKEN only |
| mcp-router | BLOCKED | MCP stdio transport exited repeatedly; health script reported Healthy. Native terminal fallback was used; no migration work was blocked. |

## Launchd activation note

The Hermes gateway plist was edited and validated but was **not reloaded from
this session**, because this agent runs inside the active Hermes gateway and
reloading it would terminate the current control process. A fresh wrapper-started
Hermes Python process was tested after draining `~/.hermes/.env`: all 17 shared
keys were present, while `MCPR_TOKEN` was loaded from the private Hermes dotenv.
Reload the gateway LaunchAgent once the current session is no longer needed:

```bash
launchctl unload ~/Library/LaunchAgents/ai.hermes.gateway.plist
launchctl load ~/Library/LaunchAgents/ai.hermes.gateway.plist
```

## Official setup references consulted

- Claude Code environment variables/authentication:
  https://code.claude.com/docs/en/env-vars
  https://code.claude.com/docs/en/authentication
  https://code.claude.com/docs/en/llm-gateway-connect
- OpenCode providers/config variables:
  https://opencode.ai/docs/providers/
  https://opencode.ai/docs/config/
- Goose provider configuration:
  https://block-goose.mintlify.app/
  https://goose-docs.ai/docs/guides/environment-variables/
- Factory Droid settings:
  https://docs.factory.ai/droid-cli/settings
- Hermes provider environment conventions:
  https://hermes-agent.nousresearch.com/docs/integrations/providers

Codex and Pi behavior was additionally verified against the installed binaries
and local source: Codex CLI 0.149.1 exposes `env_key` in its model-provider
schema; Pi 0.84.3 resolves configured `apiKey` values through
`resolveConfigValueOrThrow`, including `${ENV_VAR}` templates.

## OpenSpec planning evidence

- `openspec validate standardize-zshenv-shared-secrets --strict --store openspec-store`
  returned `Change 'standardize-zshenv-shared-secrets' is valid` before execution.
- Proposal, design, tasks, and this evidence manifest are stored in the shared
  `~/Developer/openspec-store` repository.
- Gateway reload and final live Claude sentinel remain explicit follow-up
  actions because they would interrupt the active Hermes control process.
