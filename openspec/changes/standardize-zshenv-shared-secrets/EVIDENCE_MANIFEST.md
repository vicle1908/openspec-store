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

## Follow-up reconciliation (same day, post-commit)

Re-check after the initial migration surfaced residual inconsistencies in the
adapter repository and one live routing bug:

- **Cockpit launcher port bug**: `cockpit()` in `~/.zshrc` pointed at
  `localhost:8787`, but 8787 is owned by hermes-webui (`server.py`, PID 671,
  health body shows `sessions/runs/accept_loop` — not the adapter). The
  adapter's host-mapped port is **8788** (since adapter commit `3f87da1`).
  Fixed to `http://localhost:8788`; profile JSON already had 8788.
- **Phantom `giaoduc()` launcher**: README documented a `giaoduc()` launcher
  that never existed (no profile JSON, no helper script, no function
  definition, no backup copy). Removed from README.
- **Stale `.env` documentation**: README, `install-launchagent.sh`, tracked
  plist, `.env.example`, and ignore-file exceptions still described the
  drained repo-local `.env` flow. All cleaned; `.env.example` deleted.
- **Tracked plist drift**: repo `config/*.plist` lacked the
  `launchd-env-wrapper.sh` first argument present in the installed
  LaunchAgent. Aligned; `plutil -lint` OK on both; normalized diff identical.
- **`start-adapter.sh` fail-fast ordering**: credential check moved before
  the 120s Docker wait.
- **README terminology regression** introduced and fixed during cleanup
  (protocol names restored via scripted replacement; 0 bad occurrences
  remain, assertions passed).

Adapter repo commit: `5708445 refactor: migrate credential flow to ~/.zshenv
shared tier` (8 files, +48/−44).

### Post-reconciliation verification

| Gate | Result | Evidence |
|---|---:|---|
| Adapter test suite | PASS | 55 passed in 0.35s (`uv run --extra dev pytest`) |
| Script syntax | PASS | `bash -n` on start-adapter.sh + install-launchagent.sh |
| Compose config (wrapper env) | PASS | `docker compose config --quiet` via launchd wrapper |
| Adapter health (8788) | PASS | HTTP 200 |
| ai-review / webhook health | PASS | HTTP 200 / 200 |
| Stale-ref sweep (adapter repo) | PASS | `git grep` for `.env.example`, `~/.hermes/.env`, loader, `zshenv.secrets`: no matches |
| `git diff --check` | PASS | clean |
| Shopapikey live sentinel | PASS | `SHOPAPIKEY_SENTINEL_OK` returned via fresh-shell `shopapikey --print` (benign `[1m]` selector warning, expected) |
| Cockpit live sentinel | BLOCKED | upstream `127.0.0.1:51006` has no listener (Cockpit Tools app process exists but is not serving); classification: upstream-down, not auth failure |

### Wrapper fail-closed correction (post-review)

The first fail-closed test (`env -u HOME ...`) was **invalid**: zsh
reconstructs `HOME` from the user account even when unset, so it did not
exercise the guard. Corrected test with an explicitly invalid home:

```bash
HOME="/tmp/agent-llm-nonexistent-home-$$" \
  ~/.config/agent-llm/launchd-env-wrapper.sh /bin/sh -c 'echo SHOULD_NOT_REACH'
# → "launchd-env-wrapper: missing readable .../.zshenv", exit 1
```

Result: `FAIL_CLOSED_VERIFIED` (exit 1, command never reached). The wrapper
was also hardened: a missing `HOME` now exits 1 instead of falling back to a
hardcoded path. Normal path re-verified after the edit:
`shop=36 cockpit=42 brave=74 mcpr=0`; modes `.zshenv`=600, wrapper=700.

README protocol terminology was byte-level re-verified after the scripted
fix: 0 occurrences of the mangled form; `Anthropic Messages (native)` and
`OpenAI Responses` present; title line intact.

### `hermes verify` limitation (recorded, not a pass)

`hermes verify --json` detects a FastAPI recipe whose bootstrap runs bare
`uv sync` (which **uninstalls** dev extras) and whose test phase runs bare
`pytest` (which resolves to Homebrew Python 3.11; the project requires
≥3.14). This produced a false collection failure (`respx` /
`claude_code_provider_adapter` missing). The verifier is therefore not a
valid gate for this repo until its recipe supports `--extra dev` and
`uv run`. Canonical verification command used instead:

```bash
cd ~/Developer/claude-code-provider-adapter
uv sync --extra dev
uv run --extra dev pytest   # → 55 passed
```

Dev environment was restored after each verifier run.

### Compose fail-closed hardening (post-review)

`docker-compose.yml` now uses explicit interpolation with a required-variable
guard instead of bare passthrough, so a manual `docker compose up` without
the shared credential fails at config time instead of starting with an empty
key:

```yaml
HERMES_CUSTOM_COCKPIT_API_KEY: "${HERMES_CUSTOM_COCKPIT_API_KEY:?HERMES_CUSTOM_COCKPIT_API_KEY is required (shared tier in ~/.zshenv)}"
```

Verified both paths:

| Path | Command | Result |
|---|---|---|
| Positive | wrapper env → `docker compose config --quiet` | PASS (`WRAPPER_PATH_OK`) |
| Negative | `zsh -dfc` (no rc files, `.zshenv` not sourced), var unset → `docker compose config --quiet` | exit 1, `required variable ... is missing a value` (`FAIL_CLOSED_VERIFIED`) |

Note: the first negative-path attempt used `zsh -c`, which re-sources
`~/.zshenv` and passed vacuously; `zsh -dfc` is the valid test. Container
recreated via wrapper after the change: healthy, cockpit key length 42,
adapter health 200.

### Final battery after wrapper edit (post-review)

| Gate | Result |
|---|---|
| Adapter tests | 55 passed in 0.28s |
| `zsh -n` (.zshenv, .zshrc, wrapper) | PASS |
| `bash -n` (start-adapter.sh, adapter-status.sh) | PASS |
| `plutil -lint` (repo + installed plist) | OK / OK, normalized diff identical |
| Compose config via wrapper | PASS |
| `git diff --check` | PASS |
| Health: adapter 8788 / ai-review 8090 / webhook 8080 | 200 / 200 / 200 |
| Cockpit upstream 51006 | still unreachable (sentinel remains BLOCKED) |

### Security note

During this session, literal credential values from `~/.zshenv` were
displayed once inside a patch-tool fuzzy-match error message. They were not
written to any file, committed, or delivered, but they passed through tool
output in this transcript. **Treat the affected shared-tier values as
compromised and rotate them at the provider side.** Recommended sequence:
rotate every exposed provider/tool credential at its provider; update only
`~/.zshenv` with the replacement values; recompute presence/length/hash
checks without printing values; confirm no duplicate values remain in
service `.env` files; re-run the provider sentinels after rotation. Never
include raw secret values in patch context or diagnostic output. Local file
permissions (600) are unaffected.

## OpenSpec planning evidence

- `openspec validate standardize-zshenv-shared-secrets --strict --store openspec-store`
  returned `Change 'standardize-zshenv-shared-secrets' is valid` before execution.
- Proposal, design, tasks, and this evidence manifest are stored in the shared
  `~/Developer/openspec-store` repository.
- Gateway reload and final live Claude sentinel remain explicit follow-up
  actions because they would interrupt the active Hermes control process.
