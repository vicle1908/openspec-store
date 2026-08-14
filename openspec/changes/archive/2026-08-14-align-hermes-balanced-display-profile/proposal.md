## Why

The live Hermes profile explicitly configured several high-volume display surfaces that produce excessive output on CLI and messaging platforms: `show_reasoning`, `interim_assistant_messages`, `turn_summary`, and `tool_preview_length: 0` (unlimited). Two additional settings were set but had no effect: `agent.verbose: true` (not recognized by the Hermes config schema, no interactive CLI or gateway consumer found) and `display.busy_ack_detail: true` (unsupported key — correct key is `display.busy_steer_ack_enabled`).

## What Changes

Six supported display settings are changed to their balanced low-noise values:

| Setting | Before | After |
|---|---|---|
| `display.show_reasoning` | `true` | `false` |
| `display.interim_assistant_messages` | `true` | `false` |
| `display.busy_steer_ack_enabled` | `true` | `false` |
| `display.turn_summary` | `true` | `false` |
| `display.tool_preview_length` | `0` | `60` |
| `display.platforms.slack.show_reasoning` | `true` | `false` |

Two unsupported keys are removed:
- `agent.verbose is not recognized by the Hermes config schema, and no interactive CLI/gateway consumer was found; batch runner has its own verbose setting
- `display.busy_ack_detail` — not a recognized key; replaced by `display.busy_steer_ack_enabled`

## Capabilities

### New Capabilities

- `hermes-display-configuration`: Define the supported balanced low-noise display profile, preserved visibility settings, unsupported-key exclusions, validation, and rollback.

## Goals

- Reduce display noise on CLI and messaging surfaces.
- Remove unsupported config keys that do not affect runtime behavior.
- Document the balanced profile in governance runbook and canonical spec.
- Preserve all operational visibility settings.

## Non-Goals

- No change to model reasoning depth, API cost, or token usage.
- No change to `agent.max_turns`, delegation, compression, or provider configuration.
- No live Slack smoke test (structural evidence only).

## Affected Boundaries

- Live profile: `~/.hermes/config.yaml`, display section only.
- Canonical store: new spec `hermes-display-configuration`.
- Maintained runbook: new `docs/governance/hermes-display-configuration.md`.
- No Hermes source code or provider changes.

## Rollback

Restore `~/.hermes/backups/config-before-balanced-display-20260814-141713.yaml` (SHA-256: `758e2600...`). Verify with `hermes config check` and `hermes config get display`. No code changes to revert.
