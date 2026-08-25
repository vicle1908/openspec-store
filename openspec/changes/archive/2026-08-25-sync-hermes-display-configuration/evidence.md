# Evidence: sync-hermes-display-configuration

## Version and environment

- Hermes Agent v0.20.5 (2026.8.19) · upstream 5ef1409f
- Install method: git
- Python: 3.11.15
- Config version: 38
- `hermes config check`: passes (no errors)
- Active profile: default (stealth/ox-alpha)
- Config path: `/Users/androidteam/.hermes/config.yaml`

## Documentation sources

| Source | URL / path | Accessed |
|---|---|---|
| Configuration page | https://hermes-agent.nousresearch.com/docs/user-guide/configuration | 2026-08-25 |
| Sessions page | https://hermes-agent.nousresearch.com/docs/user-guide/sessions | 2026-08-25 |
| FAQ | https://hermes-agent.nousresearch.com/docs/reference/faq | 2026-08-25 |
| Full docs aggregate | `llms-full.txt` (~3.96 MB) | 2026-08-25 |
| cli-config.yaml.example | `/Users/androidteam/.hermes/hermes-agent/cli-config.yaml.example` | 2026-08-25 |
| config_defaults.py (DEFAULT_CONFIG) | `/Users/androidteam/.hermes/hermes-agent/hermes_cli/config_defaults.py` | 2026-08-25 |
| display_config.py (_GLOBAL_DEFAULTS, _PLATFORM_DEFAULTS) | `/Users/androidteam/.hermes/hermes-agent/gateway/display_config.py` | 2026-08-25 |
| runtime_footer.py (_DEFAULT_FIELDS) | `/Users/androidteam/.hermes/hermes-agent/gateway/runtime_footer.py` | 2026-08-25 |
| agent/display.py (tool_preview, friendly_labels) | `/Users/androidteam/.hermes/hermes-agent/agent/display.py` | 2026-08-25 |

## Raw YAML vs resolved config

Every user-set raw YAML value was reflected identically in the resolved `hermes config get display` output. No value drift was detected. No profile overlay exists (`~/.hermes/profiles/` absent).

## Explicit vs inherited platform settings

| Platform | Explicit overrides (raw YAML) | Inherited from global |
|---|---|---|
| Telegram | tool_progress=verbose, grouping=separate, preview=0, show_reasoning=true, reasoning_style=code, streaming=true, interim=true, long_running=true, busy_ack=true, live_status=full | — |
| Discord | tool_progress=verbose, grouping=separate, preview=0, show_reasoning=true, streaming=true, interim=true, long_running=true, busy_ack=true, live_status=full | — |
| Slack | show_reasoning=true, tool_progress=verbose, grouping=separate, preview=0, streaming=true, interim=true, long_running=true, busy_ack=true, live_status=full | — |
| Feishu | streaming=true | tool_progress, grouping, preview, show_reasoning, interim, long_running, busy_ack, live_status (all from global block) |
| Matrix | streaming=true | Same as Feishu |
| WhatsApp | streaming=true | Same as Feishu |

## Source-only keys (not in official docs)

- `display.reasoning_full` — present in DEFAULT_CONFIG, resolves via `hermes config get display`, absent from official docs
- `display.tool_progress_grouping` — present in gateway/display_config.py _GLOBAL_DEFAULTS, resolves at runtime, absent from official config page (documented on Messaging Gateway page only)
- `display.live_status` — documented on Slack page, not on config page
- `display.busy_ack_detail` — documented only under Telegram platform defaults
- `display.long_running_notifications` — documented only under Telegram platform defaults

## Known documentation discrepancies

1. `cli-config.yaml.example` says `show_reasoning: false` and `streaming: true`; DEFAULT_CONFIG says `show_reasoning: true` and `streaming: false`. The example file is stale.
2. Config page lists `tool_progress` as `off|new|all|verbose`; Messaging Gateway page adds `log`.
3. `display.reasoning_full` is absent from all official documentation but resolves correctly from source.
4. `cleanup_progress`, `busy_ack_detail`, `long_running_notifications` are documented only in per-platform context; no global defaults stated.

## Verification commands

```bash
hermes --version
hermes profile list
hermes config path
hermes config get display
hermes config get streaming
hermes config check
cd ~/Developer/openspec-store && openspec validate sync-hermes-display-configuration --strict --store openspec-store
```

## Scope

- Config-only reconciliation — no Hermes source code modifications
- No live config mutation — the config is already at maximum direct-tool visibility
- OpenSpec spec + Hermes skill reference only
