# Hermes Balanced Low-Noise Display Configuration

## Purpose

This runbook defines the validated balanced low-noise display profile for the active Hermes `default` profile. The canonical requirements are in `openspec/specs/hermes-display-configuration/spec.md` after the associated OpenSpec change is archived.

Official reference: <https://hermes-agent.nousresearch.com/docs/user-guide/configuration#display-settings>

## Balanced Low-Noise Profile

The profile reduces display noise on CLI and messaging surfaces while preserving operational visibility.

### Changed Settings

| Setting | Value | Effect |
|---|---|---|
| `display.show_reasoning` | `false` | Stops streaming reasoning/thinking blocks. Model still thinks at full depth — only the visible blocks are suppressed. |
| `display.interim_assistant_messages` | `false` | Stops sending mid-turn assistant updates as separate chat messages. |
| `display.busy_steer_ack_enabled` | `false` | Simplified busy acknowledgement. |
| `display.turn_summary` | `false` | Removes CLI post-turn accounting footer (`⋯ 12.4s · edited 2 files`). |
| `display.tool_preview_length` | `60` | Truncates tool command previews to 60 characters. |
| `display.platforms.slack.show_reasoning` | `false` | Aligns Slack with the top-level reasoning suppression. |

### Preserved Visibility Settings

These remain enabled at their current values:

- `display.streaming: true` — real-time token delivery
- `display.tool_progress: all` — every tool call shown
- `display.show_cost: true` — token cost after each response
- `display.timestamps: true` — message ordering context
- `display.runtime_footer.enabled: true` — gateway metadata footer
- `display.background_process_notifications: all` — process awareness
- `display.long_running_notifications: true` — long-task alerts
- `compression.progress_notices: true` — context compression awareness

### Unsupported Key Exclusions

Two settings were removed because they are not recognized by the Hermes runtime:

- **`agent.verbose`** — only consumed by `batch_runner.py`, not the interactive agent runtime (`cli.py`, `gateway/run.py`, `tui_gateway/server.py`). Setting it to `false` has no effect; removing it is cleaner.
- **`display.busy_ack_detail`** — not a recognized key in Hermes v0.20.1. The correct key is `display.busy_steer_ack_enabled`.

## Validation

```bash
hermes config check
hermes config get display
```

Parse `~/.hermes/config.yaml` with `yaml.safe_load` and assert:

- `display.show_reasoning` is `false`
- `display.interim_assistant_messages` is `false`
- `display.busy_steer_ack_enabled` is `false`
- `display.turn_summary` is `false`
- `display.tool_preview_length` is `60`
- `display.platforms.slack.show_reasoning` is `false`
- `display.streaming` is `true`
- `display.tool_progress` is `all`
- `display.show_cost` is `true`
- `display.timestamps` is `true`
- `display.runtime_footer.enabled` is `true`
- `agent.verbose` is absent
- `display.busy_ack_detail` is absent

## Rollback

Before mutation, a local timestamped backup was kept:

```text
~/.hermes/backups/config-before-balanced-display-20260814-141713.yaml
SHA-256: 758e26008eb94f05682f932fa36074b0a571899b337aee63f05e5859fc76d28c
```

Do not commit the backup.

To roll back, restore this file atomically, rerun `hermes config check` and `hermes config get display`. No code changes are involved.
