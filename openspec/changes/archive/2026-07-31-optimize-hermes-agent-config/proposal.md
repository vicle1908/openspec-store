## Why

The current Hermes Agent configuration uses conservative defaults that limit
autonomous operation, cost efficiency, and resilience. A comprehensive audit
of the official configuration documentation reveals 20+ settings that should
be tuned for a production agent workflow:

**Automation gaps:** Approval prompts interrupt flows, checkpoints are
disabled (no safety net for YOLO mode), and idle compaction is off.

**Delegation gaps:** Flat-only spawning (depth=1), limited concurrency (3),
no cheaper sub-agent model, no per-model reasoning overrides, and loop caps
at defaults.

**Integration gaps:** Claude Code CLI (v2.1.212) and Codex CLI (v0.146.0)
are installed but not wired into delegation workflows. Web extraction has no
backend configured (search-only).

**Cost/resilience gaps:** Prompt caching at 5m tier (1h available), no
fallback model, auxiliary tasks all route through the expensive primary model,
no timezone set (affects cron/scheduling), and tool output limits are at
conservative defaults.

**Safety gaps:** No checkpoints to roll back destructive file operations,
no Tirith pre-exec scanning, and no PII redaction for messaging platforms.

## What Changes

### Core Automation (Section 1)
- Disable approval prompts (`approvals.mode: off`) for full automation.
- Enable checkpoints as a safety net for destructive file operations.
- Set timezone for accurate cron/scheduling.

### Delegation & Orchestration (Section 2)
- Expand to nested orchestration (`max_spawn_depth: 2`).
- Increase concurrency (`max_concurrent_children: 5`) and iterations (`80`).
- Configure a cheaper sub-agent model to reduce cost.
- Increase per-turn loop caps for web search and subagent spawning.

### Reasoning & Enforcement (Section 3)
- Set per-model reasoning overrides (high for Opus, medium for Sonnet).
- Enable tool-use enforcement globally for all models.
- Upgrade prompt caching to 1h TTL tier.

### Agent Budget & Iteration (Section 4)
- Increase `agent.max_turns` to 500 (from 150) for complex tasks.
- Set `api_max_retries` to 2 for faster fallback switching.

### Context & Memory (Section 5)
- Increase `context_file_max_chars` (20000 → 30000).
- Increase `memory_char_limit` (2200 → 3000) and `user_char_limit` (1375 → 2000).
- Increase `file_read_max_chars` (100000 → 150000) for large context models.
- Increase `tool_output` limits for richer terminal/read_file output.
- Enable idle compaction (`idle_compact_after_seconds: 300`).

### Web & Browser (Section 6)
- Configure web extract backend (tavily/firecrawl/exa).
- Enable browser session recording for debugging.

### CLI Integrations (Section 7)
- Document Claude Code CLI print-mode and interactive patterns.
- Document Codex CLI sandbox and exec patterns.

### Display & Visibility (Section 8)
- Enable `show_cost`, `timestamps`, `turn_summary`.

### Resilience & Security (Section 9)
- Configure fallback model for provider failover.
- Enable Tirith pre-exec security scanning.
- Enable PII redaction for messaging platforms.
- Relax tool loop guardrails for autonomous operation.

### Auxiliary Model Optimization (Section 10)
- Route compression to a cheaper auxiliary model.
- Configure auxiliary fallback chains.

## Goals

- Enable fully autonomous agent operation without approval interrupts.
- Unlock nested sub-agent orchestration with cost-efficient model routing.
- Maximize parallel sub-agent throughput for batch tasks.
- Make Claude Code and Codex CLI first-class delegation targets.
- Provide full web content extraction capability.
- Improve cost visibility, session observability, and resilience.
- Add safety nets (checkpoints) to compensate for YOLO mode.

## Non-Goals
## Model Selection
- **Selected model:** `fable-5` (1M context window) via `shopapikey` provider.
- Reasoning override: `xhigh` for fable-5 (adaptive thinking, 1M context).
- Fallback model also set to `fable-5` for unified model stack.

## Non-Goals
- Modifying MCP server configuration or adding new MCP servers.
- Modifying STT/TTS configuration.
- Changing session reset behavior.

## Affected Boundaries

- `~/.hermes/config.yaml` — primary configuration file.
- Claude Code CLI (`~/.claude/`) — settings for integration.
- Codex CLI (`~/.codex/`) — sandbox configuration.
- No service code, deployment, or infrastructure changes.

## Compatibility

- `approvals.mode: off` disables all safety checks for terminal commands.
  Compensated by enabling checkpoints and Tirith scanning.
- `max_spawn_depth: 2` enables nested orchestration. Cost scales multiplicatively.
- Prompt caching `1h` TTL requires Anthropic/OpenRouter provider support.

## Rollout

- Apply config changes incrementally via `hermes config set`.
- Verify each change with a fresh session (`/reset`).
- Test delegation with simple batches before nested orchestration.

## Rollback

- Revert individual settings via `hermes config set`.
- All changes are non-destructive config values.
