## Redacted baseline — 2026-07-30

### Inspection boundary

The baseline used only read-only Hermes diagnostics and filesystem metadata.
Credential-file contents were not read. Evidence below intentionally omits API
key fragments, Telegram identifiers, message/log bodies, session identifiers,
and authentication material. No backup, configuration/profile mutation,
package execution, provider call, service change, or shared-system action was
performed.

### Runtime and profile identity

- Installed CLI: Hermes Agent `0.19.0` (`2026.7.20`), upstream revision
  `2d404942`, local build with one carried commit; Python `3.11.15`.
- Configuration: schema version `33`; `hermes config check` reported current
  schema and no required missing setting.
- Profiles: only the `default` profile exists. It is the interactive
  CLI/Desktop profile and currently also owns the Telegram gateway.
- Gateway: launchd-managed default-profile service is running and its service
  definition matches the installed Hermes build. The deep diagnostic emitted
  private recent-log content, so no log body is retained in this evidence.
- Telegram: configured with an explicit allowed-user setting. No identifier or
  token material is retained here.

### Capability inventory

- CLI and Telegram currently have the same built-in selection: 16 enabled
  configurable toolsets and 8 disabled entries. Enabled selections are `web`,
  `browser`, `terminal`, `file`, `code_execution`, `vision`, `image_gen`,
  `tts`, `skills`, `todo`, `memory`, `session_search`, `clarify`, `delegation`,
  `cronjob`, and `computer_use`.
- Disabled selections are `video`, `video_gen`, `x_search`, `stt`,
  `context_engine`, `homeassistant`, `spotify`, and `yuanbao`.
- `hermes doctor` reports browser, clarify, code execution, cron, delegation,
  file, memory, Project, session search, skills, terminal, todo, TTS, video,
  vision, and web as runtime-available. Kanban is runtime-gated. Several
  credential/system-dependent capabilities remain unavailable, including
  browser CDP, computer use, image/video generation, X search, Home Assistant,
  Spotify, and Yuanbao.
- The configured platform lists currently contain only composite entries
  (`hermes-cli` and `hermes-telegram`), not the explicit target inventory.
- Sixty skills are enabled: 46 bundled, 13 local, and one hub-installed.
- Built-in memory is enabled; no external memory provider is active.
- Cron has zero jobs and no recorded executions; the gateway ticker is active.

### MCP baseline

- One server, `mcp-router`, is enabled and reported as exposing all native
  tools. Its stdio transport is `npx -y @mcp_router/cli@latest connect`.
- No `tools.include` or `tools.exclude` key is set.
- Resource/prompt, sampling, elicitation, and parallel-call policy keys are not
  explicitly set and therefore still depend on runtime defaults.
- The revised change preserves this MCP Router setup exactly except for adding
  `supports_parallel_tool_calls=true`; no package pin/probe, reload, filter,
  protocol-feature reconfiguration, or MCP business operation is planned.

### Read-only MCP transport recheck — 2026-07-30

The installed CLI help and default-profile list were rechecked without invoking
the server:

- `hermes -p default mcp list` reports one enabled `mcp-router` server with
  transport `npx -y @mcp_router/cli@latest connect` and native tools `all`.
- `hermes -p default config get mcp_servers.mcp-router.command` returns `npx`.
- `hermes -p default config get mcp_servers.mcp-router.args` returns only
  `-y`, `@mcp_router/cli@latest`, and `connect`.
- The `tools`, `resources`, and `prompts` keys are not explicitly configured,
  so capability-advertised inventories remain unverified until the exact
  package/network probe is separately approved.

This is bounded transport/configuration evidence only. It does not claim a
freshly probed interface or prompt/resource/sampling/elicitation behavior. The
baseline task is complete; apply must fingerprint and preserve it, then add only
the parallel-call flag under configuration-mutation approval.

### Effective policy baseline

| Setting | Current redacted value | Target status |
|---|---|---|
| `timezone` | `GMT+7` | replace with IANA zone after config-mutation approval |
| `agent.service_tier` | `fast` | already target |
| `approvals.mode` | `smart` | change pending approval |
| `approvals.cron_mode` | `deny` | change pending approval |
| MCP reload confirmation | enabled | change pending approval |
| destructive slash confirmation | enabled | change pending approval |
| memory/skill write approval | disabled | already target |
| subagent auto-approval | disabled | change pending approval |
| private URL policy | enabled for security and browser | already target |
| unsafe browser evaluation | disabled | change pending approval |
| browser evaluate restriction | disabled | already target |
| website blocklist | disabled | already target |
| secret redaction | enabled | mandatory retained floor |
| allowlisted lazy installs | enabled | already target; no install authorized |
| compression | enabled | already target |
| loop warnings / hard stop | enabled / disabled | hard stop change pending approval |
| web-search/subagent caps | 50 / 50 under `loop_caps` | already target |
| deprecated async-child key | absent | already target |
| concurrency / depth / timeout / iterations | 3 / 1 / 600 / 50 | depth and timeout change pending approval |
| terminal backend / home mode / cwd | local / auto / TDT aggregator root | cwd change pending approval |
| model context override | absent | remain unset pending authoritative capacity evidence |

The empty deny, command-allowlist, and disabled-toolset values are presently
stored as empty lists. The target removes these keys so defaults, rather than
serialized policy remnants, produce the empty effective state.

### Permissions, storage, and warnings

- `config.yaml`, `.env`, and `auth.json` are mode `0600`.
- `state.db` is mode `0644`, which is broader than the required
  transcript-bearing-file policy. Permission correction is a separate local
  maintenance mutation and is not performed without exact approval.
- Hermes home is approximately 3.7 GB. The largest identified category is not
  inferred from file contents; recorded subdirectory sizes are sessions about
  3.5 MB, skills about 55 MB, logs about 3.6 MB, memories about 8 KB, and cron
  about 28 KB.
- No `backups/`, `checkpoints/`, or named `profiles/` directory currently
  exists at the default root.
- Doctor reported no active security advisory, no suspicious MCP stdio
  command, and two dependency-warning groups in build tooling. It also reported
  optional provider/integration prerequisites as unavailable; these are not
  treated as successful capabilities.

### Static safety-floor verification

The installed source confirms lazy installs are limited to the active Hermes
venv (or an append-only durable target), accept package-name/version specs only,
and are restricted to the code-owned `LAZY_DEPS` allowlist. No install was
triggered.

A six-assertion static probe passed without executing a command or opening a
URL: recursive root deletion and shutdown were hardline-blocked, unconfigured
`sudo -S` password guessing was blocked, the Hermes `.env` destination was
write-denied, and both the link-local metadata address and metadata hostname
were always blocked. This verifies the immutable exception floor independently
of model behavior.

An attempted `uv run --no-sync pytest` selected an incompatible project Python,
created an empty `.venv`, and failed before running tests because pytest was not
present. A second attempt bound the existing `venv` but also found pytest
unavailable. No package was installed. The generated `.venv` is preserved and
is not treated as evidence; removing it is a separate destructive cleanup.

## Approved operating policy

The intended policy is full technical capability for authorized CLI/Desktop and
Telegram sessions on the shared `default` profile, including every verified MCP
operation. That capability decision does not weaken Telegram admission,
secret redaction, immutable Hermes blocks, protected credential paths,
provider/service scopes, repository policy, or contemporaneous approval for
destructive, outward, credential, package, deployment, and shared-state actions.

## Apply checkpoints

Each row is an independent stop. Completion of a prior row does not authorize a
later row.

| Checkpoint | Action class | Required approval before execution |
|---|---|---|
| Credential rotation/rerouting | credential mutation | exact setting/provider and supported secret destination |
| Quick or full backup generation | local generated state | exact profile, backup type, label/output path, and integrity checks |
| Configuration mutation | global/profile configuration | exact keys and target profile |
| Package or network probe | package/network execution | exact pinned package, command, endpoint purpose, and bounds |
| Existing launchd gateway restart/rollback | service mutation | exact restart/restore sequence and success predicates for `ai.hermes.gateway` |
| Reversible local-write smoke | local mutation plus cleanup | exact disposable artifacts and cleanup method |
| Provider/private-network smoke | external/provider request | exact target, request class, budget/bounds, and evidence policy |
| MCP/shared-service mutation | outward/shared-state mutation | exact tool, business target, expected effect, cleanup, and verification |

Commit, push, publish, deploy, archive, update, package installation, credential
provisioning, profile creation, backup generation, and gateway mutation remain
unperformed.

## Recurring maintenance contract

All commands run from a non-repository operator directory and target `default`.
Read-only inspection does not authorize the paired mutation.

| Maintenance item | Reviewed command/boundary | Class and approval | Success predicate |
|---|---|---|---|
| Update availability | `hermes update --check` | read-only local; no separate approval | reports installed and available identity without changing source, venv, config, or service |
| Schema health | `hermes -p default config check` | read-only local | reports schema v33/current and no deprecated key |
| Schema migration | `hermes -p default config migrate` | configuration mutation; exact migration approval required | migration reports the intended version and a subsequent check is clean; no credential value retained |
| Quick recovery point | `hermes backup --quick --label <approved-label>` | local generated state; exact label approval required | manifest has no failed databases or oversized skips and captured databases pass integrity checks |
| Full recovery archive | `hermes -p default backup --output <approved-outside-path>` | local generated state; exact output approval required | “Backup complete,” no skipped-file warning, ZIP integrity and Hermes markers pass |
| Tool inventory drift | `hermes -p default tools list --platform <platform>` | read-only local | every expected name is enabled or has an attributed unavailable prerequisite; mutations are separately approved |
| MCP inventory drift | `hermes -p default mcp list` | read-only local | transport identity, enabled state, capability-aware inventory, and runtime naming match the baseline without package execution or reload |
| Credential rotation | supported default-profile `hermes secrets`/auth/setup flow | credential mutation; exact provider approval required | redacted presence and restrictive file modes verify; values never enter argv/evidence |
| Gateway validation | default-profile status and redacted platform health | read-only unless restart occurs | `ai.hermes.gateway`, default home, PID, sole token owner, Telegram, and cron are healthy |
| Rollback | restore prior default config/state and restart the same service | service mutation and potentially destructive restore; exact sequence/archive approval required | no new profile/service exists and the default gateway passes health and authorized round-trip |
| Prompt/schema overhead | `hermes -p default prompt-size --platform <platform> --json` plus `hermes insights` | read-only local/offline for prompt-size; insights is local analytics | fixed prompt/tool-schema budget and trends are recorded without private prompt bodies |
| Curator lifecycle | `hermes -p default curator status`, `run --dry-run`, and `rollback --list`; labeled backup only after approval | status/dry-run/list are read-only; mutations require separate approval | consolidation remains off and a verified restore path exists |

Recurring review also compares schema, tools, MCP names, credentials presence,
gateway health, backup integrity, permission modes, doctor warnings, and the
immutable safety-floor probe. It does not use `--all` gateway mutation, moving
package references, or named-profile ZIP import assumptions.

## Pre-mutation MCP fingerprint and prompt budget — 2026-07-30

The already redacted MCP baseline was normalized without reading credential
files or environment values. The canonical
`hermes.mcp-structure.v1` representation contains only the known command
basename, three non-secret arguments, `tools=all`, absent include/exclude and
resource/prompt/sampling/elicitation policy keys, and an absent parallel-call
flag. Its encoded size is `222` bytes and SHA-256 is
`e21e74cba61d3a6ddc749a0547385b4aa42bfe23b264456a877b49cf6a20c598`.
This is the comparison identity for task 4.5 after an approved configuration
mutation.

Read-only `config get` evidence confirmed:

- `mcp_servers.mcp-router.tools.include`: not set
- `mcp_servers.mcp-router.tools.exclude`: not set
- `mcp_servers.mcp-router.supports_parallel_tool_calls`: not set
- `agent.parallel_tool_call_guidance`: `true`
- `tools.tool_search.max_search_limit`: `30`

The installed configuration schema contains no profile-level MCP call quota or
operation-class serialization setting. Session history filters named
`max_tool_calls` are analytics filters, not a tool-dispatch policy. Tool
Search's current `30` value is a discovery result page bound and cannot cap
later descriptions or calls; changing it to the target value `20` remains a
separate configuration mutation.

Offline `prompt-size --json` was rerun for both current default-profile
surfaces and retained only counts, never prompt bodies, skill contents, memory
text, or user-profile text:

| Platform | System-prompt bytes | Skills-index bytes | Memory bytes | User-profile bytes | Tool count | Tool-schema bytes |
|---|---:|---:|---:|---:|---:|---:|
| CLI | 33,521 | 6,959 | 1,092 | 1,301 | 29 | 51,469 |
| Telegram | 30,147 | 6,959 | 1,092 | 1,301 | 29 | 51,469 |

These values are the pre-change prompt budget only. Task 4.9 remains open until
an approved configuration wave is active and the post-change fresh-session
budget is recorded against an unchanged MCP inventory.

The accepted concurrency risk is unchanged: independent MCP calls may race on
the same mutable resource, duplicate effects, conflict, or observe intermediate
state. Hermes must report each actual result and does not promise
serializability or silently retry business mutations.

## Representative workload and curator evidence — 2026-07-30

Read-only local analytics over the preceding seven days found 24 sessions,
2,391 messages, 1,595 recorded tool calls, 19,836,531 input tokens, 758,916
output tokens, 362,669,303 total reported tokens, and approximately 17 hours 22
minutes of active time. The recorded model was `gpt-5.6-sol`; platform totals
were 16 subagent, five desktop, and three Telegram sessions. Terminal, file
read/patch/search, and process operations dominated the observed tool mix.
No session identifiers, titles, prompts, message bodies, or provider response
content are retained here.

The current offline prompt-size comparison keeps the tool count and tool-schema
bytes identical between CLI and Telegram (29 tools; 51,469 bytes). The system
prompt differs by platform and the volatile section remains separately
attributed, so prompt totals are not treated as a stable cost forecast. No
Hermes or provider/proxy budget was added or changed; community cost reports
remain unmeasured risk signals.

Cron status confirms the existing gateway ticker is running, but there are no
active jobs and no durable execution attempts. This is recorded as zero local
cron workload, not as proof of agent-backed delivery. Task 6.11 remains open
for a separately approved disposable agent/no-agent job and cleanup.

The curator dry-run was deterministic and non-mutating: consolidation was off,
the LLM pass was skipped, 49 candidate skills were reported, and no transition
was applied. `curator rollback --list` found three existing pre-curator
snapshots, while `curator status` reported 49 managed skills, 12 unmanaged
skills, and zero archived skills. No backup, adoption, consolidation, archive,
or restore was performed; task 2.13 remains open for its separately approved
labeled manual backup.

## Default-profile doctor prerequisite ledger — 2026-07-30

`hermes -p default doctor` completed without `--fix`, package installation,
authentication, configuration mutation, profile creation, provider inference,
or service changes. The diagnostic reported no active security advisory, no
suspicious MCP stdio command, schema v33 with no deprecated configuration key,
and a consistent Hermes `0.19.0` Python environment. It also reported these
sanitized capability prerequisites:

| Capability | Doctor result |
|---|---|
| `browser-cdp` | base browser requirements plus an explicit `BROWSER_CDP_URL` or `browser.cdp_url` are absent |
| `computer_use` | the `cua-driver` executable does not resolve through the supported override, `PATH`, or known local install locations |
| `discord`, `discord_admin` | `DISCORD_BOT_TOKEN` is absent |
| `feishu_doc`, `feishu_drive` | the `lark_oapi` Python package is not importable |
| `hermes-yuanbao` | no Yuanbao gateway session or active Yuanbao adapter exists |
| `homeassistant` | `HASS_TOKEN` is absent; the URL alone does not enable the tools |
| `image_gen` | neither `FAL_KEY` plus importable `fal_client` nor an explicitly selected available image-provider plugin is present |
| `spotify` | the profile-scoped Spotify auth status is not logged in |
| `video_gen` | no discovered video-generation provider reports available |
| `x_search` | `XAI_API_KEY` is absent |
| OpenRouter connectivity | provider is not configured |
| Discord Python integration | optional `discord.py` package is not installed |
| optional OAuth identities | Nous Portal, OpenAI Codex, MiniMax, and xAI are not logged in |

The same run reported eight high build-tool advisories in the web workspace and
seven in the ui-tui workspace, with no critical or moderate advisory in either
workspace. No lockfile bump or remediation was attempted. The available
capabilities reported by doctor were browser, clarify, code execution, cron,
delegation, file, memory, Project, session search, skills, terminal, todo, TTS,
video, vision, web, and runtime-gated Kanban.

The concrete mappings above were derived from the installed `0.19.0` registry
`check_fn` implementations without importing optional integrations, reading
credential values, executing a provider, or invoking a setup hook. They explain
the generic doctor label but do not authorize installation, authentication, or
configuration. No guessed package, credential, alias, or setup command was used.

## Revised single-profile gateway decision (not executed)

Official architecture, installed source, and live evidence show that CLI and
Desktop instantiate local agent processes directly, while the existing default
gateway serves Telegram and gateway-owned cron. The live installation has one
`default` profile, one supervised `ai.hermes.gateway` service, and distinguishable
CLI and Telegram sessions in the shared state database. A named Telegram profile
and second gateway are therefore removed from this change.

After approved backups and default-profile validation, activation restarts the
existing service in place. Success requires the same launchd label, default
profile home, sole Telegram-token ownership, a supervised PID, Telegram and cron
health, and an authorized round-trip. Rollback restores prior default-profile
configuration/state as needed and restarts the same service. No profile creation,
credential copy, gateway install/uninstall, multiplexing, or token transfer is
planned or executed.

## Current read-only validation refresh — 2026-07-30

The installed Hermes identity is `0.19.0` (`2026.7.20`), upstream revision
`937222f4`, with one carried local commit. Context7's current official CLI
documentation was checked before invocation and agrees that `config check`,
`doctor`, `status --all`, profile/tool inventory, and gateway status are
read-only diagnostic surfaces when `--fix` and mutation subcommands are absent.

The following default-profile probes all exited zero. Raw stdout/stderr was not
retained in this evidence; only byte counts and SHA-256 identities are recorded:

| Probe | Stdout bytes | Stdout SHA-256 |
|---|---:|---|
| `config check` | 8,750 | `e59950ca9aff4cf4327b4693a6c6dc31479677cbaaf8b50711246a5b40e65acd` |
| `doctor` | 4,824 | `760bbffa291104ea3dce556ef40c7d10074fafc527fb4303a5a5fd34d3a9b3a4` |
| `status --all` | 3,452 | `20aa972280fd4998ec4481e7fc6bb49a6576a970913b1811102426efbe2147cd` |
| CLI tool inventory | 1,187 | `67328243e2694f3a02813edfc5d066bc0a7335df5ea769ce5301488a2843aed4` |
| Telegram tool inventory | 1,192 | `7f2c4bc1284afcb222d02b5a9240a4b5d61f157c56ba3fd912d0304bc7d9a27e` |
| gateway status | 249 | `fd6c0ee2053aca7cd8fe14347a988c9c19bd9b2da02831c90a7274640343bf52` |
| MCP list | 377 | `323ef9d5608deac07411cab8caf6fee73f5370f24a9f651bd87c4f3948981ec2` |
| memory status | 622 | `f504dd2cf0787dd7699c7039c48cf7c9953ad2ac9347f905381664af5cd1fc8f` |
| skills list | 6,567 | `091fa80515c31fdf7da5b0eda9c7b4682426b3a337c5b3752463c0b02dcc9166` |
| cron status/list/runs | 122 / 90 / 37 | `50915f94ae790cc40b6849fcb34ea8075971da8e14c4e588deff63c2a04d927d` / `fbc30fde8d66539906bf37dc9005f1cdc49d35e61a323c24d6cc5abf16e9c765` / `78e28a5254fee4228364d6406ef7e158a0cb474fb8a4f6865969ba69efb13669` |

`status --all` reports missing optional Codex, Qwen, and xAI OAuth identities;
these are unavailable prerequisites, not passing capabilities. No auth command,
provider call, package execution, MCP transport probe, or network smoke ran.
Configuration, environment, and auth files remain mode `0600`; Hermes home is
mode `0700`. Transcript-bearing `state.db` remains mode `0644`, so its required
permission correction remains a separately authorized local maintenance action.
Hermes home currently occupies approximately 3,910,715 KiB.

Offline prompt-size probes retained only aggregate counts. CLI currently reports
33,543 system-prompt bytes, 6,903 skills-index bytes, 1,092 memory bytes, 1,379
user-profile bytes, and 29 tools / 51,469 schema bytes. Telegram reports 30,225,
6,959, 1,092, 1,379, and the same 29 / 51,469 tool totals. These are still
pre-mutation measurements; task 4.9 remains open until approved configuration is
active and the post-change comparison is recorded.

`hermes profile list` shows only `default`, with its gateway running, and
`gateway.multiplex_profiles` is unset. Aggregate `state.db` metadata contains
five CLI, five Desktop, 17 subagent, four Telegram, and 11 TUI sessions. All
four Telegram sessions have durable routing metadata; the other surfaces have
none, proving source/chat separation without retaining session IDs, titles,
message bodies, user identifiers, or chat identifiers. This closes the
read-only inventory and shared-profile evidence tasks only; configuration,
backup, permissions, service restart, provider/network, and reversible-write
tasks remain independently gated.
