# Why

Two issues were identified during the 2026-07-15 monitoring session:

1. **tee block-buffering**: the scheduler entrypoint's dual-sink redirect used bare `tee -a` which defaults to an 8 KB block buffer. Structlog heartbeat lines (~200 bytes each) did not reach `docker logs` or the host file until the buffer accumulated 8 KB — a ~40-line delay. `stdbuf -oL` forces line-buffering on tee so every line is flushed to both sinks immediately.

2. **No rotation**: `scheduler-entrypoint.log` grows unboundedly (5 MB observed). The `~/.tdt/scripts/rotate-logs.sh` script handles other service logs at 50 MB but had no entry for the scheduler log. Adding a startup-size-check + rename to the entrypoint itself is the correct place — it fires every container start regardless of when the rotate-logs LaunchAgent runs.

# What Changes

- `agent_core/deployments/scheduler/entrypoint.sh`:
  - `exec > >(tee -a ...)` → `exec > >(stdbuf -oL tee -a ...)` for line-buffering.
  - Before the redirect: if `scheduler-entrypoint.log` exceeds 50 MB, rename to `.1` before piping (the tee process has not started yet, so the rename is safe).
- `openspec/specs/scheduler-entrypoint` (MODIFIED): adds the line-buffering and startup-rotation requirements to the dual-sink stdout requirement.

# Impact

- Container: `docker logs` now shows every structlog line immediately (within one heartbeat interval, ~5 min or less). No change to log content.
- Host file: same content, but truncated to 50 MB max at each container start.
- Rotation: the old log (`.1`) is kept until the next startup rotation or manual cleanup. No deletion policy is added (handled separately by rotate-logs or manual cleanup).