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
| mcp-router | BLOCKED | MCP stdio transport exited repeatedly; health script reported Healthy. Native terminal fallback was used; no migration work was blocked. (Earlier state; recovered — see "MCP Router transport follow-up" below.) |

## Launchd activation note

The Hermes gateway plist was edited and validated but was **not reloaded from
this session**, because this agent runs inside the active Hermes gateway and
reloading it would terminate the current control process. A fresh wrapper-started
Hermes Python process was tested after draining `~/.hermes/.env`: all 16 shared
keys were present, while `MCPR_TOKEN` was loaded from the private Hermes dotenv.
Restart the gateway from a shell **outside** the active gateway once the
current session is no longer needed:

```bash
hermes gateway restart
```

Manual fallback only if the CLI restart is unavailable:
`launchctl unload ~/Library/LaunchAgents/ai.hermes.gateway.plist` followed by
`launchctl load ~/Library/LaunchAgents/ai.hermes.gateway.plist`.

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
| Cockpit live sentinel | BLOCKED | upstream `127.0.0.1:51006` has no listener (Cockpit Tools app process exists but is not serving); classification: upstream-down, not auth failure (Earlier state; superseded — cockpit sentinel PASS after 2026-08-27 upstream recovery; see "Corrected clean-room verification" below.) |

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
| Cockpit | not run | upstream 51006 has no listener | BLOCKED — upstream down (earlier state; superseded — see "Corrected clean-room verification" below: cockpit sentinel PASS after 2026-08-27 upstream recovery) |

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
| Cockpit upstream 51006 | still unreachable (sentinel remains BLOCKED) (Earlier state; superseded — 51006 OPEN and clean-room sentinel PASS after 2026-08-27 upstream recovery.) |

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
| cockpit live sentinel | PASS (after upstream recovery) | Earlier state: CLI timed out at 150s, TCP 51006 REFUSED, HTTP 000. After user-reported cockpit restart: TCP 127.0.0.1:51006 OPEN, HTTP root 404 (transport available; root 404 is not an API health failure), clean-room sentinel `COCKPIT_LIVE_OK`, exit 0 |
| Giaoduc live sentinel | NOT APPLICABLE — provider retired | No live request made after retirement |
| Gateway wrapper activation | PENDING USER ACTION | Running gateway pid 4966 started 2026-08-25 17:49:53, predating the plist edit (2026-08-27 12:57:27) and wrapper edit (2026-08-27 15:58:58); plist `ProgramArguments[0]` is correctly the wrapper; external `hermes gateway restart` still required. Retraction: the earlier claim "gateway environment contains 0 shared-tier variable names" relied on `ps -wwE`, which is unreliable for cross-process env introspection on macOS; the current gateway environment was not reliably introspected. Clean-room shells and the wrapper dry run are the authoritative source tests. |

### Corrected clean-room verification (2026-08-27)

Two verifier artifacts in the earlier batteries are corrected here:

1. **Regex bug:** the initial shared-tier regex omitted `GITHUB_TOKEN` and
   `API_KEY_SECRET` and included `MCPR_TOKEN`, producing a coincidental
   16-match count that was not the canonical roster.
2. **Inherited contamination:** the long-lived acting session contained
   inherited legacy environment variables (including
   `HERMES_CUSTOM_GIAODUC_API_KEY` and `MCPR_TOKEN`), so non-clean-room
   `zsh` runs reflected session inheritance, not active configuration
   sources. Process ancestry was not directly proven; the clean-room
   results below are the authoritative source tests.

Authoritative results (all via `env -i HOME TERM` clean-room shells,
names only, never values):

| Check | Result |
|---|---|
| Clean-room 4-mode matrix (`-c`, `-ic`, `-lc`, `-ilc`) | 16/16 canonical shared-tier names; 0 Giaoduc; 0 `MCPR_TOKEN` leak in every mode |
| Non-empty value check (names only, never values) | 16/16 non-empty in all 4 clean-room modes (`-c`, `-ic`, `-lc`, `-ilc`); 16/16 non-empty in wrapper dry run |
| Wrapper dry run (`launchd-env-wrapper.sh /usr/bin/env`) | exit 0; 16/16 shared-tier names; 0 Giaoduc; 0 `MCPR_TOKEN` |
| `launchctl getenv HERMES_CUSTOM_GIAODUC_API_KEY` | absent (no launchd global injection) |
| Clean-room shopapikey sentinel | `SHOPAPIKEY_LIVE_OK`, exit 0 |
| Clean-room cockpit sentinel | `COCKPIT_LIVE_OK`, exit 0 |
| Giaoduc sweep, live config surfaces | 0 refs in `~/.zshenv`, `~/.zshrc`, `~/.codex`, `~/.pi`, `~/.claude*`, `~/.tdt/.env`, `~/.hermes/.env`, `~/.hermes/config.yaml`, OpenCode dirs, adapter repo, wrapper, loader |
| Giaoduc refs in `~/.config/agent-llm/backups/` | 6 refs, all confined to documented historical backups (codex-config.toml ×4, pre-migration-hashes.txt ×1, zshenv ×1) — security-retention issue, not active configuration |

This section supersedes earlier environment-count rows recorded from
contaminated or regex-incomplete batteries.

`MCPR_TOKEN` remains service-private by design (design.md D1): it is
supplied via mcp-router's own config `env:` block, not the shared tier.

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
- Gateway reload was executed 2026-08-28 (see below) after confirming the
  executing session was NOT a descendant of the gateway process. The final
  live Claude sentinel is exercised by ordinary session traffic through the
  now-keyed gateway.


## Gateway wrapper activation (2026-08-28)

### Incident

The 2026-08-28 08:44 gateway restart (pid 4966 → 14388) did NOT activate the
wrapper: launchd re-spawned from its **cached pre-wrapper job definition**
(`launchctl print` showed `program = …/venv/bin/python`, not the wrapper).
The gateway process carried zero shared-tier keys, and because task 5.1 had
drained the provider keys from `~/.hermes/.env`, every provider 401'd:
38 `401`/`AuthenticationError`/`no resolvable api_key` events between 08:44
and 08:57 (`shopapikey`, `phanmemvip`, `cockpit`, `moa` all affected).

### Fix

Executed from a session verified NOT to descend from the gateway process:

```bash
launchctl bootout gui/$(id -u)/ai.hermes.gateway
# first bootstrap raced async teardown → "Bootstrap failed: 5: Input/output error"
# retried after the job fully left the domain:
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/ai.hermes.gateway.plist
```

### Verification

| Gate | Result | Evidence |
|---|---:|---|
| launchd definition | PASS | `launchctl print` → `program = /Users/androidteam/.config/agent-llm/launchd-env-wrapper.sh` |
| New gateway process | PASS | pid 42908, started 2026-08-28 08:58:09 |
| Shared tier in process env | PASS | all 5 `HERMES_CUSTOM_*` keys + `BRAVE_SEARCH_API_KEY`, `EXA_API_KEY`, `TAVILY_API_KEY`, `OMNIROUTE_API_KEY` present (names verified via `ps Eww`; values never printed) |
| Auth errors after restart | PASS | 0 `401`/`AuthenticationError` events post-08:58 (vs 38 in the broken window) |
| Wrapper dry-run | PASS | wrapper + `/usr/bin/env` exports 5 `HERMES_CUSTOM_*` keys |
| Pre-existing failures unchanged | N/A | Matrix/WhatsApp connect failures occur daily since ≥ 2026-08-21 (~250–290/day) — predate the migration; `MATRIX_ACCESS_TOKEN` untouched in private tier |

### Latent hazard found during verification

`hermes gateway status` reports "Service definition is stale relative to the
current Hermes install — Run: hermes gateway start". Root cause:
`generate_launchd_plist()` in `hermes_cli/gateway.py` regenerates the plist
WITHOUT `launchd-env-wrapper.sh` (verified by generating in memory — no
wrapper reference), and `refresh_launchd_plist_if_needed()` overwrites the
installed plist on `hermes gateway start`/restart. Following the CLI's own
advice would silently revert the D5 bridge and reproduce this incident.
Mitigation rules and recovery procedure: design.md D5 hazard section.
Proposed follow-up: wrapper-aware generator patch (decision pending).

### Independent post-restart verification (2026-08-28, this session)

Re-verified independently after the user-reported restart, without relying on
the activation session's own claims:

| Gate | Result | Evidence |
|---|---:|---|
| Gateway process | PASS | pid 42908, started Fri Aug 28 08:58:09 2026 — after plist edit (08-27 12:57) and wrapper edit (08-27 15:58) |
| launchd loaded definition | PASS | `launchctl print` → `program = …/launchd-env-wrapper.sh` |
| Gateway env (BSD `ps Eww`, names only) | PASS | 16/16 canonical shared-tier names present; 0 Giaoduc; `MCPR_TOKEN` absent (private tier) |
| Native MCP bridge | PASS | `mcp__mcp_router__list_directory` on adapter repo returned real listing through the keyed gateway — the decisive 6.4b runtime proof |
| Clean-room 4-mode matrix | PASS | 16/16 non-empty, 0 Giaoduc, 0 MCPR leak in `-c`/`-ic`/`-lc`/`-ilc` |
| Wrapper dry run | PASS | exit 0, 16/16 non-empty, 0 Giaoduc, 0 MCPR |
| Syntax + plist | PASS | `.zshenv`, `.zshrc`, wrapper `zsh -n` clean; plist lint OK; `ProgramArguments[0]` = wrapper |
| Giaoduc sweep, live surfaces | PASS | 0 refs across all live config surfaces (documented historical backups excluded) |
| Post-restart sentinels | PASS | clean-room `SHOPAPIKEY_LIVE_OK` and `COCKPIT_LIVE_OK`, both exit 0; cockpit 51006 TCP OPEN |
| Auth errors post-08:58 | PASS | 0 genuine events. One grep hit at 09:12:53 was a false positive: a hardline-block warning whose text contains the literal string `401` inside a grep pattern, not an auth failure |

Task ledger: all tasks checked (6.4a, 6.4b, R1–R4 complete). Migration is
fully activated at runtime; the only open item is the documented D5 follow-up
decision (wrapper-aware `generate_launchd_plist()` patch), which is a
hardening decision, not a migration gap.

## Wrapper-aware generator patch (2026-08-28, task R5)

### Change

`~/.hermes/hermes-agent/hermes_cli/gateway.py` (upstream checkout, local
uncommitted change):

- New `_configured_launchd_env_wrapper()` resolver: reads
  `gateway.launchd_env_wrapper` via `load_config_readonly()`, validates it
  is an executable file, fails open to `None` on any error (unset,
  non-string, missing, non-executable, config unloadable).
- `generate_launchd_plist()` prepends the resolved wrapper to
  ProgramArguments before the `stderr_timestamp` command. Mirrors the
  `runtime.nofile_soft_limit` / SoftResourceLimits idiom.
- Config knob added to `~/.hermes/config.yaml` (outside the git checkout):
  `gateway.launchd_env_wrapper: /Users/androidteam/.config/agent-llm/launchd-env-wrapper.sh`.
- 6 new tests in `tests/hermes_cli/test_gateway_service.py`
  (`TestLaunchdEnvWrapper`): prepend when configured, omit when unset,
  resolver absent-key / non-executable / executable / config-unloadable.

### Verification

| Gate | Result | Evidence |
|---|---:|---|
| New test class | PASS | 6/6 passed |
| Full gateway service suite | PASS | 109 passed, 1 skipped |
| Gateway status suite | PASS | 72 passed, 2 skipped |
| Lint | PASS | ruff 0.15.10 (repo-pinned) clean on both changed files |
| Generated plist | PASS | ProgramArguments[0] = wrapper; 13 args; `plistlib` parses |
| Config merge | PASS | `gateway.launchd_env_wrapper` present; existing gateway keys preserved (deep merge) |
| End-to-end refresh | PASS | `refresh_launchd_plist_if_needed()` rewrote plist to current format WITH wrapper; detached reload helper restarted gateway (pid 42908 → 6023) |
| New process env | PASS | all 5 `HERMES_CUSTOM_*` keys + shared tool keys present (names via `ps Eww`; values never printed) |
| Auth errors post-refresh | PASS | 0 `401`/`AuthenticationError` events |
| `hermes gateway status` | PASS | "✓ Service definition matches the current Hermes install" (stale warning gone) |

### Update-survival strategy

The patch is a local uncommitted change in the upstream checkout.
`hermes update` uses `updates.non_interactive_local_changes: stash`
(default): it stashes local changes, pulls, and restores them — the patch
normally survives. On a stash-restore conflict, re-apply:

```bash
cd ~/.hermes/hermes-agent
git apply ~/.config/agent-llm/backups/20260827-zshenv-shared-secrets/hermes-launchd-env-wrapper.patch
```

The config knob in `~/.hermes/config.yaml` is outside the git checkout and
survives updates unconditionally. Patch backup (153 lines, 2 files,
+118/−6) stored alongside the migration backups.

## Research-CLI centralization (2026-08-28, task R6)

### Data bugs found by live verification

Live CLI round-trips (bx, tvly, exa, gh + direct API probes) exposed two
shared-tier values that hash-preservation alone could not catch:

| Key | Defect | Evidence |
|---|---|---|
| `BRAVE_SEARCH_API_KEY` | Value was a **URL** (74 chars, contains `://`), not a key | Brave API returned 422 `SUBSCRIPTION_TOKEN_INVALID`; pre-migration manifest shows the 74-char value came from hermes.env (the "newer wins" winner) |
| `TAVILY_API_KEY` | Key **exhausted** at provider | Tavily API returned HTTP 432 (quota) |

The valid keys survived elsewhere: the 31-char `BSAH…` Brave key in the
`tdt.env`/`zshenv.secrets` backups and bx's keystore (all three
hash-identical, sha256[:12] `9d1699cf9385`, HTTP 200 verified); the 41-char
Tavily key in tvly's config file (sha256[:12] `109118dc4a56`, HTTP 200
verified).

### Fix

1. Replaced both values in `~/.zshenv` from the valid sources (value-blind
   Python edit; mode 600 preserved; `zsh -n` clean).
2. Centralized the research CLIs on the shared tier:
   - **bx**: removed `api_key` from
     `~/Library/Application Support/brave-search/config.json`. Empirically
     proven first: with an empty config, bx falls back to the
     `BRAVE_SEARCH_API_KEY` env var (a bogus env key reached the API).
   - **tvly**: `tvly logout` removed `~/.tavily/config.json`. tvly prefers
     `TAVILY_API_KEY` env over its config file (proven: a bogus env key
     shadowed the valid config key).

### Verification

| Gate | Result | Evidence |
|---|---:|---|
| `.zshenv` values | PASS | BRAVE len 31 sha `9d1699cf9385`; TAVILY len 41 sha `109118dc4a56`; mode 600; syntax clean |
| bx keystore cleared | PASS | `bx config show-key` → "no API key configured" |
| tvly config cleared | PASS | `~/.tavily/config.json` removed by `tvly logout` |
| bx live via env | PASS | fresh-shell `bx web` returned real Brave results |
| tvly live via env | PASS | fresh-shell `tvly search` returned real Tavily results |
| exa / gh (already env) | PASS | live results / `gh auth status` logged in |
| Pre-fix backups | PASS | `~/.config/agent-llm/backups/20260827-zshenv-shared-secrets/pre-research-cli-centralization/` (zshenv, bx-config.json, tvly-config.json) |

### Shared-tier status after R6

All 16 shared-tier keys now hold live-validated values where a probe exists:
Brave, Tavily, Exa, GitHub validated live; provider keys validated via CLI
round-trips (codex/opencode/pi/hermes PONG, phanmemvip/cockpit HTTP 200).
OmniRoute/Firecrawl/OpenRouter/Copilot/NPMJS/Postman/API_KEY_SECRET have no
cheap live probe and remain hash-preserved.

### R6 follow-up: service env alignment + multi-agent sweep (2026-08-28)

After R6 corrected the `.zshenv` values, the running launchd services still
held the stale Brave/Tavily (all started before the ~10:05 fix and had
sourced the old `.zshenv`).

| Service | Consumes Brave/Tavily? | Action |
|---|---|---|
| `ai.hermes.gateway` | Yes — web toolset falls back to Tavily/Brave behind firecrawl | Restarted via `launchctl kickstart -k` (wrapper re-sources corrected `.zshenv`); new pid 28617 now holds BRAVE len 31 (not a URL) + TAVILY len 41; all 5 `HERMES_CUSTOM_*` present; 0 auth 401s |
| `com.tdt.ai-review` / `com.tdt.webhook-receiver` | No (grep of both repos: zero references) | Left running — stale env is inert |

Multi-agent sweep (other coding agents unaffected by R6, all live-verified):

| Agent | Key mechanism | Live result |
|---|---|---|
| goose | macOS keychain (`api_key_env` hints; providers `configured: true`) | ✅ PONG via cockpit |
| codex / opencode / pi / hermes | env (shared tier) | ✅ PONG each (verified pre-R6; keys unchanged by R6) |
| Claude-Fable CLI | `apiKeyHelper` env-first scripts | ✅ single-line tokens |
| mcp-router (Brave/Tavily MCP) | own valid keys (`auth_mode: keyed`) | ✅ both return results |

Firecrawl (gateway's primary web backend) validated live: HTTP 200. No coding
agent reads the cleared bx/tvly keystores; no agent config references
`BRAVE_SEARCH_API_KEY`/`TAVILY_API_KEY` directly except via the shared tier.
