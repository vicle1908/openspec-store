# Tasks: Align Hermes Balanced Display Configuration

## 1. Ground Truth and Investigation

- [x] 1.1 Read live Hermes config and capture all display settings, agent.verbose, and provider/model state.
- [x] 1.2 Source-trace `agent.verbose` — not recognized by the Hermes config schema. No interactive CLI or gateway consumer was found. `batch_runner.py` has its own verbose configuration usage, but the investigation does not conclusively establish that it consumes the global `agent.verbose` key. It was removed rather than retained as an ineffective custom key.
- [x] 1.3 Source-trace `display.busy_ack_detail` — not a recognized key; the correct key is `display.busy_steer_ack_enabled`.
- [x] 1.4 Search active OpenSpec changes for overlapping display ownership. No active change claims display settings.
- [x] 1.5 Create isolated worktree and OpenSpec change.

## 2. Implementation

- [x] 2.1 Backup config before mutation (SHA-256: `758e26008eb94f05682f932fa36074b0a571899b337aee63f05e5859fc76d28c`).
- [x] 2.2 Set `display.show_reasoning` to `false`.
- [x] 2.3 Set `display.interim_assistant_messages` to `false`.
- [x] 2.4 Set `display.busy_steer_ack_enabled` to `false`.
- [x] 2.5 Set `display.turn_summary` to `false`.
- [x] 2.6 Set `display.tool_preview_length` to `60`.
- [x] 2.7 Set `display.platforms.slack.show_reasoning` to `false`.
- [x] 2.8 Remove unsupported `agent.verbose` key.
- [x] 2.9 Remove unsupported `display.busy_ack_detail` key.

## 3. Verification

- [x] 3.1 `hermes config check` — schema v34, no errors.
- [x] 3.2 `hermes config get display` — all six settings at target values.
- [x] 3.3 Parsed-YAML assertions: 6 target settings, 2 absent unsupported keys, preserved visibility settings. 13/13 PASS.
- [x] 3.4 Config SHA-256 after mutation: `19f03775b7b6a61cfb45c111194a288171f8e74d94a5793bc052e4963817215f`.

## 4. Documentation

- [x] 4.1 Write `proposal.md` with Why/What Changes/Capabilities, goals/non-goals, boundaries.
- [x] 4.2 Write `design.md` with target state, official doc behavior, rollback design.
- [x] 4.3 Write `tasks.md` with evidence lines.
- [x] 4.4 Write `specs/hermes-display-configuration/spec.md` delta spec (6 ADDED requirements).
- [x] 4.5 Write `implementation-evidence.md`.
- [x] 4.6 Write `docs/governance/hermes-display-configuration.md`.

## 5. Pre-archive Gates

- [x] 5.1 Run `openspec validate align-hermes-balanced-display-profile --strict` — valid.
- [x] 5.2 Run `openspec show --json --deltas-only` — 6 ADDED deltas confirmed.
- [x] 5.3 Run `openspec instructions apply --change align-hermes-balanced-display-profile --json` — remaining == 0.
- [x] 5.4 Run `git diff --check` on isolated worktree — clean.
- [x] 5.5 Stale-reference sweep: no maintained active target contradicts the balanced profile; historical before-values and normative unsupported-key exclusions are classified as intentional.
