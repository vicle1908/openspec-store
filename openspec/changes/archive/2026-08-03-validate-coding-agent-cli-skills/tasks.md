## 1. Evidence Collection

- [x] 1.1 Record installed CLI versions and relevant help surfaces for Antigravity, Claude Code, and Codex.
- [x] 1.2 Audit current official Google, Anthropic, and OpenAI documentation for headless execution, permissions, sandboxing, sessions, subagents, plugins, hooks, MCP, and workspaces.
- [x] 1.3 Identify documentation/version skew and distinguish verified binary behavior from docs-only TUI behavior.

## 2. Skill Corrections

- [x] 2.1 Update the Antigravity skill and linked references/templates with validated model slugs, CWD/project semantics, output status handling, permissions, sandboxing, MCP, and subagents.
- [x] 2.2 Update the Claude Code skill with current print-mode permissions, tools, bare mode, sessions, native background agents, worktrees, hooks, MCP storage, and agent-team behavior.
- [x] 2.3 Update the Codex skill with non-PTY exec, explicit unattended approval plus sandbox policy, non-Git operation, JSONL/schema output, resume/review, plugins, hooks, MCP, subagents, and manual worktrees.

## 3. Live Verification

- [x] 3.1 Verify Antigravity model-slug and JSON execution, effective process CWD, absolute-path file write/readback, and unsupported `--cwd`/`doctor` claims.
- [x] 3.2 Verify Codex non-PTY JSONL execution, workspace-write file creation/readback, non-Git execution support, session/review help, plugins, MCP, and feature flags.
- [x] 3.3 Verify Claude Code installation health, auth status reporting, native background-agent listing, help surfaces, MCP syntax, and official documented behavior; record that model execution is blocked while unauthenticated.
- [x] 3.4 Reload all updated skills and scan for stale contradictory guidance.

## 4. OpenSpec Verification and Closure

- [x] 4.1 Write `verification.md` with exact commands, versions, outputs, and known limitations.
- [x] 4.2 Run `openspec validate --strict validate-coding-agent-cli-skills` and `openspec validate --strict --all` successfully.
- [x] 4.3 Run `openspec store doctor` and confirm the only uncommitted store changes belong to this change.
- [x] 4.4 Commit the shared OpenSpec store with a descriptive message.
