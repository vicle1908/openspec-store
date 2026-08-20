# Design: Agent Config Rationalization

## Architecture

This is a configuration-only change. No application code, no architecture decisions. The design is 4 key-value mutations in `~/.hermes/config.yaml`.

## Research Findings (Source-Backed)

### agent.api_max_retries

- **Source:** `vision_tools.py:513` — `for attempt in range(max_retries)` with exponential backoff via `httpx` transport
- **Scope:** Image download retries in `vision_tools.py`, video download retries in `vision_tools.py`, skills hub retries in `skills_hub.py`
- **NOT global:** This controls retries for specific tool operations, not general API calls
- **Idempotency:** Model inference retries are safe operationally — duplicate calls don't corrupt state, but they do count as separate billable tokens
- **Backoff:** Uses httpx retry with exponential backoff

### compression.idle_compact_after_seconds

- **Source:** `agent_init.py:2278-2283` — read at agent construction: `compression_idle_compact_after_seconds = max(0, int(_compression_cfg.get("idle_compact_after_seconds", 0)))`
- **Activation:** `turn_context.py:782-826` — fires at session resume when idle gap exceeds threshold
- **Boundary:** Takes effect on new sessions only; existing long-lived sessions retain the old value until gateway restart
- **Default:** 0 (disabled) — our baseline of 300 means it's already enabled

### tool_output.max_bytes

- **Source:** `tool_output_limits.py:23` — `max_bytes: 100000 # terminal output cap (chars)`
- **Mechanism:** `base.py:984` — head/tail window truncation: shows first ~half and last ~half of output
- **Scope:** Terminal/stream output only — not file reading
- **Behavior:** Truncation message shows `"[... truncated — showing last ~{max_bytes // 1024}KB ...]"`

### tool_output.max_lines

- **Source:** `tool_output_limits.py:24` — `max_lines: 5000 # read_file pagination + truncation cap`
- **Scope:** Affects BOTH terminal output AND `read_file` pagination limit
- **Impact:** Reducing from 5000 to 3000 means `read_file` with `limit=5000` will be capped at 3000 — pages through more but reads less per page
- **Trade-off:** 3000 lines is generous for 95% of operations; files >3000 lines require pagination

## Decisions

### agent.max_turns stays at 500
User explicitly retains this. The 4 proposed changes do NOT touch this setting.

### delegation.child_timeout_seconds stays at 0
Source research confirmed it's a wall-clock deadline (`_child_future.result(timeout=child_timeout)`), not an inactivity timeout. A cap would kill productive long-running subagents.

### tool_output.max_lines proposed at 3000 (not 2000)
The original recommendation was 2000, but source research shows this also caps `read_file` pagination. 3000 is safer — still a 40% reduction from 5000 while avoiding disruption to file-reading workflows.

### idle_compact_after_seconds: 300 → 900
Currently fires 5 minutes after session resume if idle. 15 minutes preserves context during natural breaks. Takes effect on new sessions only.

## Rollback

All 4 changes are individually reversible via `hermes config set`. A pre-mutation snapshot provides full rollback.
