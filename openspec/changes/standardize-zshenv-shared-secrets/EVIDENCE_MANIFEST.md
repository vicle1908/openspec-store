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

`~/.zshenv` now contains 16 exported shared-tier variables, including:

- 5 provider keys: Phanmemvip, Shopapikey, Cockpit, Antigravity, and
  Localhost-51006.
- Shared tool keys: Brave, Exa, Tavily, OmniRoute, Firecrawl, OpenRouter,
  GitHub, API_KEY_SECRET, Copilot provider, NPMJS, and Postman.

Giaoduc was part of the original migration snapshot but was retired on
2026-08-27 because it is no longer used. The original 17-key migration
verification remains below as historical evidence; current-state checks use
16 keys.

`MCPR_TOKEN` is deliberately excluded from the shared tier. Hash comparison
showed different values for Hermes, OpenCode, Pi, and Qoder; it is
client/service-specific and remains owned by each client configuration.

## Post-migration retirement verification (2026-08-27)

Giaoduc is no longer used and has been removed from active configuration. This
is a fresh current-state check; historical backups and the historical evidence
section below are intentionally excluded from the active sweep.

| Gate | Result | Evidence |
|---|---:|---|
| Active `~/.zshenv` | PASS | 0 Giaoduc references; 16 exported shared keys; mode 600; `zsh -n` clean |
| Active `~/.zshrc` | PASS | 0 Giaoduc references; launcher functions are only `shopapikey`, `cockpit`, `claude_reset`; `zsh -n` clean |
| Shell visibility | PASS | `zsh -c`, `zsh -ic`, `zsh -lc`, `zsh -ilc`: 4/4, each 16 set / 0 missing; Giaoduc absent |
| Active Codex config | PASS | `~/.codex`; 0 Giaoduc references; only `codex_local_access`; default unchanged |
| Other active consumers | PASS | Pi, OpenCode, Claude profiles/helpers, TDT/Hermes dotenv, LaunchAgents, adapter repo: 0 Giaoduc references |
| CLI availability | PASS | Claude, OpenCode, Pi, Codex `--help` / version commands exit 0 |
| Runtime liveness | PASS | Adapter 8788 health 200; ai-review 8090 health 200; webhook 8080 health 200 |
| Historical references | INTENTIONAL | Migration backup and OpenSpec historical evidence retain Giaoduc for audit; no active consumer uses it |
| Giaoduc live sentinel | NOT APPLICABLE | Provider retired; no live request made after removal |

## Initial migration verification snapshot (before Giaoduc retirement)

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
Hermes Python process was tested after draining `~/.hermes/.env`: all 16 shared
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

### Real CLI verification battery (post-review)

Strict pass criteria: exit=0 AND sentinel present in the FINAL response AND no
reconnect/auth errors. All sentinels ran with `MCPR_TOKEN` removed from the
environment; outputs captured to mode-600 temp files, deleted after counting;
only counts/lengths reported (never values).

| CLI | Command | Result | Classification |
|---|---|---|---|
| Claude Code shopapikey | fresh-shell `shopapikey --print` sentinel | exit=0, sentinel returned | FUNCTIONAL — degraded (gateway `unrecognized_model` warning) |
| OpenCode | `opencode run --model shopapikey/Claude-Fable` | exit=0, sentinel, no errors | PASS |
| Pi | `pi -p --no-session --no-tools --no-extensions --provider shopapikey --model Claude-Fable` | exit=0, sentinel, no errors | PASS |
| Codex (giaoduc, historical) | `codex exec --strict-config -c model_provider="giaoduc" -m Advance` | exit=1, 5 reconnects, empty final response | HISTORICAL — retired, not an active provider |
| Cockpit | not run | upstream 51006 has no listener | BLOCKED — upstream down |

Environment gates re-verified in the same battery: 16/16 shared keys present
in all 4 zsh modes; both Claude helpers correct on env-path and fallback
(lengths 36/42, single line).

### Shopapikey warning diagnosis (degraded pass)

- The `unrecognized_model` warning appears with BOTH the `fable[1m]`
  selector AND explicit `--model Claude-Fable` (comparison run: both exit=0,
  both return the sentinel, both warn).
- Provider catalog (GET /v1/models with the valid key) lists exactly:
  `codex`, `Claude-Sonnet`, `Claude-Fable`, `default` — the model ID
  is catalog-valid.
- Conclusion: gateway-side cosmetic warning on SDK sub-queries
  (`query_source: sdk`), pre-existing (profile dated 2026-08-25, untouched
  by this migration). No profile changes made — provider documentation does
  not confirm expected behavior for the warning.

### Historical pre-retirement evidence — Giaoduc

Giaoduc was removed from the shared tier and Codex configuration on 2026-08-27
because it is no longer used. The following evidence is retained for audit
purposes only. Do not re-test or re-enable this provider.

### Codex + Giaoduc root cause (historical)

- `env_key` migration itself is verified: `~/.codex`,
  0 literal `experimental_bearer_token` entries remain, `env_key` present
  for both custom providers, and `--strict-config` accepted the config.
- Direct endpoint probes with the migrated key:
  - `POST https://api.giaoduc.online/v1/responses` → **404** (endpoint does
    not exist), yet the Codex provider block uses `wire_api = "responses"`.
  - `POST /v1/chat/completions` and `/v1/messages` → **401 "Invalid API
    key"** with both `Authorization: Bearer` and `x-api-key` styles.
- Control test: `GET /v1/models` returns 200 even with a **bogus** key —
  that earlier 200 was NOT authentication evidence.
- No alternate giaoduc credential exists anywhere (`~/.tdt/.env`,
  `~/.hermes/.env`, Prime Agent config paths all checked — none).
- Conclusion: the Codex-era giaoduc key is invalid for inference and/or
  giaoduc does not expose a Responses endpoint. `wire_api` was NOT blindly
  switched to `chat` — auth fails on every inference endpoint regardless.
  Codex+giaoduc is not a working provider without fresh credentials or an
  adapter; recorded as blocked, pre-existing.

### Cockpit sentinel preconditions (still unmet)

51006 has no listener; the Cockpit Tools app process exists but the API
service is not serving. Sentinel deferred until `51006 /v1/models` returns
a real response. Adapter health on 8788 proves adapter liveness only, not
upstream readiness.

### Credential rotation (user action, blocking further live testing)

Per the security note above, the shared-tier values exposed via the
patch-tool error must be rotated at the provider side before further live
CLI testing. Replacement values go only into `~/.zshenv` locally; never
into chat, command arguments, or tool context. After rotation, re-run
presence/length/hash checks and the sentinel battery.

Pitfall recorded from this battery: the direct HTTP probes expanded the key
into curl's argv (`curl -H "Authorization: Bearer $VAR"`), which is visible
via `ps` while the request runs. Future probes must use a mode-600 curl
config file (`curl --config`) or client-side env authentication instead of
command-line expansion.

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

### MCP Router transport follow-up (2026-08-27)

The MCP Router blocker was re-investigated at the transport boundary using the
MCP integration debugging workflow and official Router documentation:

- Official contract: `npx -y @mcp_router/cli connect` with `MCPR_TOKEN`.
- Hermes configuration shape verified without printing values: command `npx`,
  args `[-y, @mcp_router/cli@latest, connect]`, env key `MCPR_TOKEN` present.
- Desktop/backend health script: `Healthy`.
- Correct host test: `hermes mcp test mcp-router` → connected in 8021ms,
  137 tools discovered.
- Direct official Python SDK probe, with corrected installed-SDK field names
  (`server_info` and `is_error`), passed: `initialize`, `tools/list`,
  `list_directory` (`is_error=False`), and `read_file` (`is_error=False`).
  Probe exit 0; temporary probe removed.
- Native `mcp__mcp_router__list_directory` in this existing Hermes session
  still fails because its immutable startup snapshot retains stale watchdog
  bridges. This is a session lifecycle issue, not Router/backend failure.
- Required resolution: reload the Hermes gateway from an independent shell and
  start a fresh session before relying on native `mcp__mcp_router__*` tools.
  Gateway restart was not attempted from inside this active gateway.
- The Cua independent-shell fallback was unavailable because embedded Cua
  startup timed out; no GUI action was taken.

### Skill probe recipe correction (2026-08-27)

The installed MCP Python SDK uses snake_case attributes. The
`mcp-integration-debugging` skill probe recipe was corrected accordingly:
`serverInfo` → `server_info`, `isError` → `is_error`, `inputSchema` →
`input_schema`, `structuredContent` → `structured_content`. Intentional
camelCase references were preserved: wire-format prose (JSON-RPC/SSE) and
error-message examples in `stale-session-sdk-fallback.md`.

- Both shipped probe scripts pass `py_compile`.
- `references/mcp-router-stdio-probe.py` executed live against mcp-router:
  `Server: MCP Router v0.2.0`, 137 tools, `list_directory` call
  `is_error=False`, exit 0.
- `scripts/mcp-router-stdio-probe.py --server mcp-router` executed live in
  discovery mode: 137 tools listed, exit 0.
- Provenance: `~/.hermes/skills/` is not git-tracked; these fixes are
  live-on-disk, not repository-committed.

### Live provider sentinels and gateway wrapper activation (2026-08-27)

| Gate | Result | Evidence |
|---|---:|---|
| shopapikey live sentinel | PASS | `zsh -ic 'shopapikey --print …'` returned `SHOPAPIKEY_LIVE_OK`, exit 0 |
| cockpit live sentinel | BLOCKED — upstream down | CLI timed out at 150s; independent probe: TCP 127.0.0.1:51006 REFUSED, HTTP 000 |
| Giaoduc live sentinel | NOT APPLICABLE — provider retired | No live request made after retirement |
| Gateway wrapper activation | PENDING USER ACTION | Running gateway pid 4966 started 2026-08-25 17:49:53, predating the plist edit (2026-08-27 12:57:27) and wrapper edit (2026-08-27 15:58:58); gateway environment contains 0 shared-tier variable names; plist `ProgramArguments[0]` is correctly the wrapper; external `hermes gateway restart` still required |

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
