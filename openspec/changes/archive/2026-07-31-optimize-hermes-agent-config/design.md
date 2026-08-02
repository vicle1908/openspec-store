## Context

The Hermes Agent runs on this Mac as the primary AI assistant, connected to
WhatsApp, Telegram, and Discord. It manages a microservices project with 8 Go
services, OpenSpec-driven development, MCP tool integration, and multi-session
memory. The agent currently operates with conservative defaults across 10+
configuration areas that require manual tuning.

Two custom providers are configured (shopapikey with Claude/Fable models, cockpit
with GPT models). The primary model is `fable-5` (1M context window) via the
shopapikey provider, with `xhigh` reasoning override for adaptive thinking.
Fallback model is also `fable-5`. Claude Code v2.1.212 and Codex CLI v0.146.0
are installed but not integrated. The MCP router provides 137 deferred tools.
Context compression is well-tuned at 50% threshold / 20% target.

This change addresses agent operational configuration only — no microservice
code, deployment, or infrastructure changes.

## Goals / Non-Goals

**Goals:**

- Enable fully autonomous operation with safety nets.
- Unlock nested sub-agent orchestration with cost-efficient routing.
- Integrate Claude Code and Codex CLI as first-class delegation targets.
- Add web extraction, timezone, caching, and resilience configurations.
- Optimize auxiliary model routing for cost efficiency.

**Non-Goals:**
- MCP server changes.
- Platform toolset changes.
- Compression threshold changes.

## Configuration Changes

### Section 1: Core Automation

**Approvals — Full Automation:**
```yaml
approvals:
  mode: off              # was smart
```
All shell commands execute without prompting. Secret redaction stays ON.

**Checkpoints — Safety Net for YOLO:**
```yaml
checkpoints:
  enabled: true          # was false
  max_snapshots: 20      # default OK
```
Automatic filesystem snapshots before destructive file operations. Critical
safety net when approvals are off — allows `hermes checkpoints rollback`.

**Timezone:**
```yaml
timezone: "Asia/Ho_Chi_Minh"   # was empty (server-local)
```
Ensures accurate cron scheduling, log timestamps, and system prompt time
injection.

### Section 2: Delegation & Orchestration

```yaml
delegation:
  max_iterations: 80            # was 50
  max_concurrent_children: 5    # was 3
  max_spawn_depth: 2            # was 1 (flat)
  orchestrator_enabled: true    # already true
  max_summary_chars: 30000      # was 24000 — richer child summaries
```

**Cost warning:** depth=2, concurrency=5 → max 25 concurrent leaf agents.

**Loop Caps (per-turn runaway protection):**
```yaml
tool_loop_guardrails:
  loop_caps:
    max_web_searches: 100       # was 50
    max_subagents: 20           # was 50 — tighter for cost control
```

### Section 3: Reasoning & Enforcement

**Per-Model Reasoning Overrides:**
```yaml
agent:
  reasoning_effort: "xhigh"    # high reasoning for primary fable-5 model
  reasoning_overrides:
    "fable-5": "xhigh"         # 1M context adaptive thinking model
```
Fable-5 with 1M context supports adaptive thinking. `xhigh` gives thorough
reasoning on complex tasks. Spelling-tolerant matching.

**Tool-Use Enforcement:**
```yaml
agent:
  tool_use_enforcement: true    # was auto
```
Forces tool-use guidance for ALL models. The `auto` mode excludes Claude
(assumes it's reliable), but explicit enforcement is safer for autonomous
operation where describing actions instead of performing them is costly.

**Prompt Caching — 1h TTL:**
```yaml
prompt_caching:
  cache_ttl: "1h"       # was "5m"
```
Anthropic supports `5m` and `1h` tiers. The 1h tier means system prompt,
skill blocks, and early context are cached across sessions for a full hour.
First send pays full rate; subsequent sends within the hour pull from cache
at discounted rate. Significant cost savings.

### Section 4: Agent Budget & Iteration

```yaml
agent:
  max_turns: 500               # was 150 — docs default is 500
  api_max_retries: 2           # was 3 — faster fallback switching
```

`max_turns: 500` matches the documented default and gives complex tasks
room to complete. `api_max_retries: 2` means faster handoff to fallback
provider on transient errors (3 total attempts before fallback).

### Section 5: Context & Memory

```yaml
model:
  context_length: 1000000        # NEW — 1M tokens for fable-5
context_file_max_chars: 30000   # was 20000 (default)
file_read_max_chars: 150000     # was 100000 — large context model
tool_output:
  max_bytes: 100000             # was 50000 — richer terminal output
  max_lines: 3000               # was 2000
  max_line_length: 3000         # was 2000
memory:
  memory_char_limit: 3000       # was 2200
  user_char_limit: 2000         # was 1375
compression:
  idle_compact_after_seconds: 300  # was 0 (disabled) — auto-compact after 5min idle
```

Larger limits for models with 200K+ context windows. Idle compaction
automatically compresses long idle conversations.

### Section 6: Web & Browser

```yaml
web:
  backend: brave-free           # search (unchanged)
  extract_backend: tavily       # NEW — requires TAVILY_API_KEY
browser:
  dialog_policy: auto_dismiss   # was must_respond — smoother automation
  record_sessions: false        # keep off unless debugging
```

Web extract enables `web_extract` tool for full page content. Browser
`auto_dismiss` prevents dialog prompts from blocking autonomous browsing.

### Section 7: CLI Integrations

**Claude Code CLI** (v2.1.212 at `/opt/homebrew/bin/claude`):
- Print mode: `claude -p "task" --dangerously-skip-permissions --max-turns 10`
- Interactive: tmux-based PTY orchestration
- Key flags: `-p`, `--output-format json`, `--allowedTools`, `--bare`
- Settings: `~/.claude/settings.json` (global)

**Codex CLI** (v0.146.0 at `/opt/homebrew/bin/codex`):
- Auto-build: `codex exec --sandbox workspace-write "task"`
- Full-access: `codex exec --sandbox danger-full-access "task"`
- Constraint: must run inside git repo, use `pty=true`
- From gateway: prefer `danger-full-access` (bubblewrap often fails)

### Section 8: Display & Visibility

```yaml
display:
  show_cost: true               # was false — track $ spending
  timestamps: true              # was false — see when each turn happened
  turn_summary: true            # post-turn accounting footer
```

### Section 9: Resilience & Security

**Fallback Model:**
```yaml
fallback_providers:
  provider: shopapikey
  model: fable-5
```
Automatic failover when primary is unavailable. Unified on fable-5 for consistency.

**Tirith Pre-Exec Scanning:**
```yaml
security:
  redact_secrets: true           # already ON
  tirith_enabled: true           # was commented out
  tirith_timeout: 5
  tirith_fail_open: true         # allow exec if tirith unavailable
```
Scans terminal commands before execution for dangerous operations.
Compensates for `approvals.mode: off`.

**PII Redaction:**
```yaml
privacy:
  redact_pii: true               # was false
```
Hashes user IDs and phone numbers from LLM context on WhatsApp/Signal/Telegram.

**Tool Loop Guardrails:**
```yaml
tool_loop_guardrails:
  warnings_enabled: true
  hard_stop_enabled: false       # keep off for interactive use
  warn_after:
    same_tool_failure: 5         # was 3
    idempotent_no_progress: 3    # was 2
```

### Section 10: Auxiliary Model Optimization

```yaml
auxiliary:
  compression:
    provider: "shopapikey"       # was auto (uses primary model)
    model: "fable-5"             # 1M context model for compression
    timeout: 120
```
Routes context compression to the same fable-5 model (1M context) for
consistency. All other auxiliary tasks remain on `auto` (primary model).

## Verification

1. Apply each section via `hermes config set` commands.
2. Start a fresh session (`/reset`) after each section.
3. Section 1: Execute `rm /tmp/_openspec-verify-$$` without prompt.
4. Section 2: Run flat and nested delegation tests.
5. Section 3: Verify reasoning overrides appear in status.
6. Section 4: Confirm max_turns=500 in iteration budget display.
7. Section 5: Read a large file, verify no truncation at 100K.
8. Section 6: Call `web_extract(urls=["https://example.com"])`.
9. Section 7: Run `claude -p "echo test" --output-format json`.
10. Section 8: Check CLI shows cost and timestamps.
11. Section 9: Verify fallback by checking config.
12. Section 10: Trigger compression, verify fable-5 model used.
13. Run `openspec validate --strict --all` for spec regression check.

## Docs-Compliance Fixes (Section 12)

Five config type/format issues found during cross-reference validation against
official Hermes docs (https://hermes-agent.nousresearch.com/docs/user-guide/configuration):

1. **`tool_use_enforcement: 'true'`** → `true` (bool). `hermes config set`
   stored string `'true'`; docs specify bool type.
2. **`reasoning_overrides`** → YAML dict. `hermes config set` stored JSON
   string; docs explicitly say "edit YAML directly" for this key.
3. **`fallback_providers`** → list format. Docs show list of provider/model
   entries; `hermes config set` stored legacy single-entry dict.
4. **`auxiliary.compression.timeout`** → added `120`. Docs default is 120s;
   was missing from config.
5. **`streaming.enabled: false`** → removed. Legacy key conflicted with
   current `display.streaming: true`. `display.streaming` is the documented
   key for CLI token streaming.

### Lesson: `hermes config set` type limitations

`hermes config set` stores all values as YAML scalars. Complex types (dicts,
lists, booleans) may be stored as quoted strings instead of native types.
After setting complex config values, verify type correctness by checking
the raw YAML with `grep` or Python. Key affected settings:
- `reasoning_overrides` (dict) — must be YAML dict, not JSON string
- `fallback_providers` (list) — must be YAML list, not single dict
- Boolean values — `hermes config set` may quote them as strings
