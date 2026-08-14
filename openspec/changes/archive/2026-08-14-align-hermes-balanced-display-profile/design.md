# Design: Balanced Display Configuration

## Current State

All display settings were at their defaults or explicitly noisy values:

```yaml
display:
  show_reasoning: true          # streams thinking blocks (highest visual volume)
  interim_assistant_messages: true  # sends mid-turn updates as separate messages
  busy_ack_detail: true         # unsupported key, did not affect runtime
  turn_summary: true            # post-turn accounting footer
  tool_preview_length: 0        # no truncation on command previews
  tool_progress: all            # every tool call shown
  show_cost: true               # token cost after responses
  timestamps: true              # message ordering
  streaming: true               # real-time tokens
  runtime_footer:
    enabled: true               # gateway metadata
  platforms:
    slack:
      show_reasoning: true      # reasoning visible on Slack
```

Additionally, `agent.verbose: true` was set but not recognized by the Hermes config schema. No interactive CLI or gateway consumer was found. It was removed rather than retained as an ineffective custom key.

## Target State

```yaml
display:
  show_reasoning: false           # stop showing reasoning blocks (biggest noise win)
  interim_assistant_messages: false  # stop flooding chat with mid-turn updates
  busy_steer_ack_enabled: false   # simplified busy state
  turn_summary: false             # remove post-turn accounting line
  tool_preview_length: 60         # truncate command previews to 60 chars
  tool_progress: all              # keep tool visibility (useful)
  show_cost: true                 # keep cost visibility
  timestamps: true                # keep ordering
  streaming: true                 # keep real-time tokens
  runtime_footer:
    enabled: true                 # keep gateway metadata
  platforms:
    slack:
      show_reasoning: false       # align with top-level
```

## Official Doc Behavior Per Setting

| Setting | What it controls | Does it affect tokens/cost |
|---|---|---|
| `show_reasoning` | Renders model thinking/reasoning as visible blocks above each response | No — model still thinks; just hidden from UI |
| `interim_assistant_messages` | Gateway-only: sends completed mid-turn assistant updates as separate chat messages | No — display only |
| `busy_steer_ack_enabled` | Shows detailed acknowledgement when agent is processing | No — display only |
| `turn_summary` | CLI-only: prints one-line post-turn accounting footer | No — display only |
| `tool_preview_length` | Max chars for tool call previews (0 = unlimited, show full paths/commands) | No — display only |
| `platforms.slack.show_reasoning` | Per-platform override for reasoning visibility on Slack | No — display only |

## Design Decisions

1. **`show_reasoning: false`** is the single largest impact — reasoning blocks are hundreds of tokens of visible output per response. Setting this to false removes them without affecting model behavior.

2. **`tool_preview_length: 60`** instead of a hard 0 (unlimited) — keeps command previews visible but prevents extremely long commands from dominating the display. 60 chars is enough for most tools.

3. **`tool_progress: all`** preserved — tool call visibility is useful for understanding what the agent is doing. Users who want less can use `/verbose new` or set to `off`.

4. **`agent.verbose` removed** — Hermes v0.20.1 does not recognize this key in the interactive agent configuration schema. No interactive CLI or gateway consumer was identified. `batch_runner.py` has separate verbose handling, but that does not establish that global `agent.verbose` controls interactive sessions.

5. **`display.busy_ack_detail` removed** — the runtime does not recognize this key. The correct key is `display.busy_steer_ack_enabled`, which was already being set to false.

## Rollback Design

Single-file rollback: restore `~/.hermes/backups/config-before-balanced-display-20260814-141713.yaml` (SHA-256: `758e2600...`). Verify with `hermes config check` and `hermes config get display`. No code changes involved.
