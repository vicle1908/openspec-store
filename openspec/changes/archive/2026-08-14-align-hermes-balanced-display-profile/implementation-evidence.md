# Implementation Evidence: Align Hermes Balanced Display Profile

Evidence captured on 2026-08-14. No credential values exposed.

## Pre-Change Backup

- Backup path: `~/.hermes/backups/config-before-balanced-display-20260814-141713.yaml`
- Backup SHA-256: `758e26008eb94f05682f932fa36074b0a571899b337aee63f05e5859fc76d28c`
- Verified at creation time against live config.

## Config Mutation

Seven `hermes config set` calls applied. Two subsequent `hermes config unset` calls removed unsupported keys.

| Setting | Before | After | Status |
|---|---|---|---|
| `display.show_reasoning` | `true` | `false` | Supported, applied |
| `display.interim_assistant_messages` | `true` | `false` | Supported, applied |
| `display.busy_steer_ack_enabled` | `true` | `false` | Supported, applied (corrected from unsupported `busy_ack_detail`) |
| `display.turn_summary` | `true` | `false` | Supported, applied |
| `display.tool_preview_length` | `0` | `60` | Supported, applied |
| `display.platforms.slack.show_reasoning` | `true` | `false` | Supported, applied |
| `agent.verbose` | `true` | absent | Removed (unsupported key) |
| `display.busy_ack_detail` | `true` | absent | Removed (unsupported key) |

Post-mutation config SHA-256: `19f03775b7b6a61cfb45c111194a288171f8e74d94a5793bc052e4963817215f`

## Parsed-YAML Assertions (13/13 PASS)

All six target display settings at expected values. Both unsupported keys confirmed absent. All seven preserved visibility settings confirmed at their current values.

## Source-Path Verification

- `agent.verbose`: not recognized by the Hermes config schema. No interactive CLI or gateway consumer was found. `batch_runner.py` has its own verbose configuration usage, but the investigation does not conclusively establish that it consumes the global `agent.verbose` key. It was removed rather than retained as an ineffective custom key.
- `display.busy_ack_detail`: not present in any Hermes source file. `display.busy_steer_ack_enabled` is the supported key.
- `display.show_reasoning`: suppresses visible reasoning/thinking blocks. Does not change `agent.reasoning_effort` or token usage.

## CLI Verification

- `hermes config check`: PASS, schema v34.
- `hermes config get display`: shows all six target values.

## Rollback

Restore `~/.hermes/backups/config-before-balanced-display-20260814-141713.yaml` atomically. Rerun `hermes config check` and `hermes config get display`.
