# optimize-hermes-agent-config

Full automation, sub-agent orchestration, fable-5 (1M context) model selection,
Claude Code CLI, Codex CLI integration, and config optimization.

## Current Model Stack

| Slot | Provider | Model | Context |
|------|----------|-------|---------|
| Primary | shopapikey | fable-5 | 1M tokens |
| Fallback | shopapikey | fable-5 | 1M tokens |
| Compression | shopapikey | fable-5 | 1M tokens |
| Reasoning | — | xhigh (adaptive) | — |

## Key Settings

- Approvals: off (YOLO mode)
- Checkpoints: enabled (safety net)
- Delegation: depth=2, concurrency=5, 80 iterations
- Prompt caching: 1h TTL
- Idle compaction: 300s
- Timezone: Asia/Ho_Chi_Minh
- Context length: 1,000,000 tokens

## Docs-Compliance Status

All settings validated against official docs:
https://hermes-agent.nousresearch.com/docs/user-guide/configuration

5 type/format issues fixed:
- `tool_use_enforcement`: string → bool
- `reasoning_overrides`: JSON string → YAML dict
- `fallback_providers`: dict → list format
- `auxiliary.compression.timeout`: added 120s default
- `streaming.enabled`: removed legacy conflicting key

## Task Count

- Section 0: Model Selection (5 tasks)
- Section 1: Core Automation (6 tasks)
- Section 2: Delegation & Orchestration (5 tasks)
- Section 3: Reasoning & Enforcement (4 tasks)
- Section 4: Agent Budget & Iteration (3 tasks)
- Section 5: Context & Memory (5 tasks)
- Section 6: Web & Browser (4 tasks)
- Section 7: CLI Integrations (6 tasks)
- Section 8: Display & Visibility (2 tasks)
- Section 9: Resilience & Security (5 tasks)
- Section 10: Auxiliary Model Optimization (2 tasks)
- Section 11: Validation & Documentation (5 tasks)
- Section 12: Config Type Validation (6 tasks)
- **Total: 58 tasks, all complete**
