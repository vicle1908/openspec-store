## Context

Kimi Code CLI is a terminal coding agent in the same broad category as Claude Code, Codex, and Antigravity. The local executable is `/opt/homebrew/bin/kimi`, version `0.31.1`. Its current command surface uses `kimi -p` for noninteractive prompts, `--output-format stream-json` for structured output, `--plan`, `--yolo`, `--auto`, session flags, custom skills/agents, MCP support, and `kimi acp` for Agent Client Protocol integrations.

The skill lives in the active Hermes profile outside the OpenSpec repository. The shared store records the scope, rationale, exact verification, and closure state.

## Decisions

### Use `kimi -p` as the primary delegation surface

`kimi -p` is the closest Kimi equivalent to Claude `-p`, Codex `exec`, and Antigravity `--print`. Hermes should run it with an explicit repository `workdir`, a bounded host-process timeout, and `stream-json` when machine-readable progress is needed.

### Do not copy flags between agent CLIs

Kimi's installed help does not expose Claude/Codex/Antigravity-specific controls such as `--max-turns`, `--max-budget-usd`, `--dangerously-skip-permissions`, or `--print-timeout`. The skill explicitly warns against assuming those flags.

### Preserve workspace isolation

Concurrent Kimi writers must use separate Git worktrees, consistent with the workspace policy. Hermes independently checks changed files, Git diff/status, and focused tests rather than trusting Kimi's final narrative.

### Keep MCP and ACP guidance separate

Kimi supports MCP as a client and exposes `kimi acp` for IDE/orchestrator integration. The skill documents both without changing persistent MCP configuration or copying credentials.

### Skip delta specs

No product requirement or runtime platform behavior changes. `.openspec.yaml` sets `skip_specs: true`.

## Verification Plan

1. Validate the OpenSpec change strictly and validate all store specs.
2. Confirm the skill file has valid frontmatter, expected sections, official sources, and no credential material.
3. Run `kimi --version`, `kimi --help`, `kimi acp --help`, and `kimi doctor config`.
4. Reload the skill and verify its saved content and metadata.
5. Run `openspec store doctor`, inspect the store diff, archive the completed change, and commit the store.
