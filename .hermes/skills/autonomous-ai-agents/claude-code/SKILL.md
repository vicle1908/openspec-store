---
name: claude-code
description: "Delegate coding to Claude Code CLI (features, PRs)."
version: 3.1.1
author: Hermes Agent + Teknium
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Coding-Agent, Claude, Anthropic, Code-Review, Refactoring, Automation]
    related_skills: [codex, antigravity, hermes-agent, opencode]
---

# Claude Code — Hermes Orchestration Guide

Delegate coding, review, research, and background work to [Claude Code](https://code.claude.com/docs/en/cli-reference). The host has two validated Claude binaries: `/opt/homebrew/bin/claude` (2.1.220) and `/Users/androidteam/.local/bin/claude` (2.1.225). PATH differs between the normal terminal and MCP-supervised processes, so pin the intended absolute binary when comparing runs; never infer that `claude` resolves to the same version everywhere.

### Verified local setup

The current local settings grant `Bash(*)`, wildcard mcp-router/plugin/agentmemory rules, the configured `opus[1m]` model, and experimental agent teams. The global permission default is now `bypassPermissions`; explicit invocation flags remain recommended for auditable automation. Never expose the configured endpoint or authentication token in diagnostics.

## Readiness

```bash
command -v claude
claude --version
claude auth status --text
claude doctor
claude --help
claude agents --json
```

Install/update:

```bash
npm install -g @anthropic-ai/claude-code
claude update
```

Authentication:

```bash
claude auth login
claude auth login --console
claude auth login --sso
claude auth status
```

Do not infer authentication from the current process environment alone. `claude auth status` exits `0` when authenticated and `1` otherwise.

In service/gateway contexts on macOS, a token exported by the user's login-shell setup may be absent from the direct subprocess environment. Check presence without printing values, then run both status and Claude through the same login-shell context when appropriate:

```bash
zsh -lic '[[ -n "$ANTHROPIC_AUTH_TOKEN" ]] && echo token-present || echo token-absent'
zsh -lic 'claude auth status'
zsh -lic 'claude -p "Reply with OK" --tools "" --max-turns 1 --output-format json'
```

Never print, copy, persist, or pass the token as a command-line value. A token-loaded invocation can report `authMethod: "oauth_token"` even when direct `claude auth status` reports logged out.

Authentication environment precedence matters:

- Values already exported by the invoking process/login shell can override `env` values in `~/.claude/settings.json`.
- When settings contain the intended token and endpoint but `zsh -lic` exports an older `ANTHROPIC_BASE_URL`, prefer direct `claude ...` invocation so Claude loads the settings-owned environment.
- Compare endpoint presence/host safely; never print token values or silently unset/bypass an endpoint without confirming the intended provider/billing route.
- A successful minimal no-tools probe does not guarantee tool-enabled coding requests will be accepted by an intermittent gateway. Retry boundedly, then report a pre-token API connectivity failure when usage is zero and `terminal_reason: "api_error"`.

The configured provider/model may classify forced exact-output health prompts as prompt injection even under `--safe-mode`; do not attribute that behavior to plugins without evidence. Treat a completed API result as connectivity evidence and use a genuine bounded coding task plus external tests for capability verification.

## Preferred orchestration: print mode

Use `claude -p` for bounded noninteractive work. It does not require a PTY.
**Use full permissions** for authorized coding tasks — `bypassPermissions` disables permission prompts. Set a generous task budget and timeout for complex work; use an isolated worktree when multiple writers are active.

For complex coding/review tasks, use `--max-turns 40–90` and `--max-budget-usd` appropriate to the task. Do not use the previous `--max-turns 8` smoke-test budget for architecture reviews or multi-file implementation.

```python
terminal(
    command=(
        "claude -p 'Implement the requested change and run focused tests.' "
        "--permission-mode bypassPermissions --tools 'Read,Edit,Write,Bash' "
        "--max-turns 12 --output-format json"
    ),
    workdir="/path/to/trusted/project",
    background=True,
    notify_on_complete=True,
)
```

**MCP Router access**: Claude Code automatically discovers MCP servers from the environment. To explicitly include mcp-router tools:
```python
terminal(
    command=(
        "claude -p 'Use mcp-router tools as needed for the task.' "
        "--permission-mode bypassPermissions --tools 'Read,Edit,Write,Bash' "
        "--max-turns 12 --output-format json"
    ),
    workdir="/path/to/trusted/project",
    background=True,
    notify_on_complete=True,
)
```

Print mode disables workspace trust verification. Use `bypassPermissions` for unattended delegation — it skips all approval prompts while retaining safety circuit breakers.

### Output and streaming

- `--output-format text|json|stream-json`
- `--input-format text|stream-json`
- `--json-schema <schema>` requests structured data in `structured_output`, but support is provider/model dependent. Verify the field exists and validate it before relying on it. The locally configured first-party-compatible endpoint with model `opus[1m]` ignored the schema in repeated safe-mode and legitimate code-analysis probes, returning ordinary prose without `structured_output`.
- Token streaming: `--output-format stream-json --verbose --include-partial-messages`
- Bidirectional streaming: use stream JSON for input and output; `--replay-user-messages` requires both
- `--forward-subagent-text`: forward subagent text/thinking in stream JSON
- `--include-hook-events`: include lifecycle events in stream JSON
- `--prompt-suggestions`: emit a predicted next prompt
- `--no-session-persistence`: do not save a print-mode session

Validate process exit code and the result object. Exact JSON fields evolve; parse only documented fields needed by the workflow.

### Cost and turn bounds

- `--max-turns <n>`: print-only turn limit
- `--max-budget-usd <amount>`: print-only aggregate API budget; subagent spend counts
- `--fallback-model <model>`: print-only overload fallback
- Per-subagent limits can use `maxTurns`

There is no turn limit by default.

## Tool availability versus permission

These flags are not interchangeable:

- `--tools "Read,Edit,Bash"`: restricts which built-in tools Claude sees.
- `--allowedTools`: permission allow rules; matching tools/calls execute without prompting but other tools may remain visible.
- `--disallowedTools`: deny rules. A bare tool name removes it from context; a scoped rule denies matching calls.
- `--tools` does not restrict MCP tools. Deny them with `--disallowedTools "mcp__*"` or suppress MCP configuration.

Current permission modes include `default`/`manual`, `acceptEdits`, `plan`, `auto`, `dontAsk`, and `bypassPermissions` where supported by the installed version.

`--dangerously-skip-permissions` is equivalent to bypass mode but is not an absolute removal of every safety mechanism: explicit ask rules, some connector/MCP interactions, managed policy, and deletion circuit breakers may still intervene. Reserve it for externally isolated execution.

Permissions decide whether an action may run. Claude Code's Bash sandbox is a separate filesystem/network isolation layer configured through `/sandbox` and `sandbox.*` settings.

## Bare mode

```bash
claude --bare -p "Analyze the supplied context" --permission-mode bypassPermissions --tools "Read,Bash" --max-turns 5
```

`--bare` skips automatic discovery of hooks, LSP, plugins, MCP servers, skills, auto-memory, CLAUDE.md, background prefetches, and keychain/OAuth credentials. It still provides built-in Bash and file tools. Explicitly supplied settings, prompts, agents, plugins, MCP configs, skills by explicit invocation, and added directories can still load.

Supply `ANTHROPIC_API_KEY`, `apiKeyHelper` through settings, or configured third-party provider credentials. Anthropic recommends bare mode for automation and documents that it may become the default for `-p` in a future release.

## Sessions

```bash
claude --continue
claude --continue -p "Continue and run tests"
claude --resume <session-id-or-name>
claude --resume <id> -p "Continue the task"
claude --resume <id> --fork-session
claude --session-id <uuid>
```

- `--continue` is scoped to the current directory.
- `--resume` accepts an ID/name; no value opens the interactive picker.
- Session lookup includes the project and its Git worktrees.
- Print sessions remain resumable by ID even when absent from the picker.
- `--fork-session` works with resume or continue.
- Invocation-only settings such as MCP config, plugins, added directories, and fallback model are not necessarily restored on resume; pass them again.

## Native background agents

Claude Code can manage independent background sessions without hand-built tmux:

```bash
claude --background "Investigate the flaky tests"
claude agents --json
claude agents --json --all
claude attach <session-id>
claude logs <session-id>
claude stop <session-id>
claude respawn <session-id>
claude rm <session-id>
```

`--background` cannot be combined with `-p`. `claude agents` opens interactive Agent View; `claude agents --json` is the noninteractive listing interface and does not list static subagent definition files.

## Interactive TUI

Interactive Claude requires a terminal/PTY, not tmux specifically. Tmux is optional and useful for durable monitoring. Agent View also requires an interactive terminal.

```python
terminal(
    command="claude --permission-mode acceptEdits",
    workdir="/path/to/project",
    background=True,
    pty=True,
    notify_on_complete=True,
)
```

First-time trust or permission dialogs vary by version and policy. Inspect the currently rendered choices; do not hard-code arrow-key sequences.

## Worktrees

Claude can create isolated worktrees:

```bash
claude --worktree feature-auth
claude --worktree feature-auth --tmux
claude --worktree '#123'
```

- Worktrees live under `.claude/worktrees/<name>` on a `worktree-<name>` branch.
- The default base is the remote default branch; configure `worktree.baseRef: "head"` when local HEAD is intended.
- `--tmux` requires `--worktree`; `--tmux=classic` selects traditional tmux.
- Print-mode worktrees are not automatically cleaned up.
- Subagents can request `isolation: worktree`.
- Agent-team teammates do not automatically receive separate worktrees; partition write ownership explicitly.

## Subagents and agent teams

Custom subagents can be defined in `.claude/agents/`, `~/.claude/agents/`, or via `--agents` JSON and selected with `--agent`.

Current fields include `tools`, `disallowedTools`, `permissionMode`, `maxTurns`, `mcpServers`, `hooks`, `skills`, `memory`, `background`, `effort`, `isolation`, and `initialPrompt`. Subagents generally run in the background and can spawn nested subagents subject to current depth limits.

Agent teams are a separate experimental capability, disabled by default. Enable with `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`. They provide separate sessions, a shared task list, direct messaging, and lead coordination, but consume more tokens than subagents.

`--teammate-mode` supports `in-process`, `auto`, `tmux`, and `iterm2` on current compatible versions. Treat undocumented/version-only flags as unstable even if local help exposes them.

## Skills, commands, and project instructions

Claude loads `CLAUDE.md`, `.claude/rules/*.md`, skills, plugins, and commands according to its current settings hierarchy.

Skills and custom commands can be invoked in print mode; they are not restricted to interactive TUI usage. Use `--disable-slash-commands` to disable them. Prefer skills for reusable workflows and CLAUDE.md/rules for persistent project conventions.

## Hooks

Hooks receive structured JSON on stdin. Do not rely on invented `$CLAUDE_TOOL_INPUT` or `$CLAUDE_FILE_PATHS` environment variables. Parse the documented event payload.

Example command hook:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "python3 .claude/hooks/check_bash.py"
          }
        ]
      }
    ]
  }
}
```

The hook program reads JSON from stdin and returns the documented JSON/exit status. Matchers use canonical tool names or documented regex-style matching, not permission expressions such as `Write(*.py)`.

Current events include `Setup`, `SessionStart`, `UserPromptSubmit`, `UserPromptExpansion`, `PreToolUse`, `PermissionRequest`, `PermissionDenied`, `PostToolUse`, `PostToolUseFailure`, `PostToolBatch`, `SubagentStart`, `SubagentStop`, `TaskCreated`, `TaskCompleted`, `Stop`, `StopFailure`, `TeammateIdle`, `PreCompact`, `PostCompact`, `SessionEnd`, `Notification`, `ConfigChange`, `InstructionsLoaded`, `CwdChanged`, `FileChanged`, `DirectoryAdded`, `WorktreeCreate`, `WorktreeRemove`, `Elicitation`, `ElicitationResult`, and `MessageDisplay` on current documented versions.

Handlers can include command, HTTP, prompt, agent, and asynchronous forms. Check the [current hooks reference](https://code.claude.com/docs/en/hooks) before implementing policy-critical automation.

## MCP

Stdio:

```bash
claude mcp add my-server -- npx my-mcp-server
```

HTTP:

```bash
claude mcp add --transport http sentry https://mcp.sentry.dev/mcp
```

Authentication and inspection:

```bash
claude mcp list
claude mcp login <name>
claude mcp logout <name>
```

Scopes and storage:

| Scope | Flag | Storage |
|---|---|---|
| Local, default | `--scope local` | Project entry inside `~/.claude.json` |
| User | `--scope user` | Top-level `mcpServers` in `~/.claude.json` |
| Project | `--scope project` | `.mcp.json` at project root |

For print automation, use `--mcp-config <json-or-file>` and optionally `--strict-mcp-config`. Strict mode ignores other user/project MCP configuration but does not override managed policy.

## Review and Git workflows

For quick bounded review:

```bash
claude -p "Review the current changes for correctness, security, and missing tests." \
  --permission-mode bypassPermissions --tools "Read,Edit,Write,Bash" --max-turns 40 --max-budget-usd 10
```

Claude can resume sessions linked to PRs with `--from-pr`. Worktree isolation is preferred for concurrent writers. Regardless of Claude's report, inspect changed files, Git diff, and test output outside Claude before declaring success.

## Complexity-adaptive limits

Do not use one fixed turn/timeout budget for every task. Classify the work before launch:

| Complexity | Typical scope | `--max-turns` | Host timeout |
|---|---|---:|---:|
| Small | Read-only review, one-file fix, focused diagnosis | 8–15 | 5–8 min |
| Medium | One subsystem, tests plus implementation, bounded refactor | 25–45 | 10–15 min |
| Large | One repository, several related modules and full verification | 60–90 | 20–30 min |

Use `--max-budget-usd` as an additional generous budget for large tasks. A turn limit or budget is a runtime guard, not a tool restriction; keep it high enough to finish the assigned scope.

For work spanning multiple subsystems, repositories, or independent acceptance gates, split it into milestone invocations instead of setting an unlimited turn count. A good sequence is: baseline/plan, one subsystem per implementation turn, then independent verification. Resume the same session with `--resume <id>` when context helps; otherwise start a fresh bounded session to avoid accumulated drift.

A turn-limit exit is partial work, not failure and not completion. Inspect the worktree, preserve valid edits, run external checks, then resume with a narrow remaining-task prompt. Increase the next budget only when the transcript shows productive progress. Stop or redirect when the agent repeatedly explores unrelated tooling, rewrites generated indexes, or attempts nonessential environment repair after the assigned code is complete.

Always keep a host timeout above the expected model budget; `--max-turns` and the host timeout are independent. For large Claude jobs, prefer 20–30 minutes over the previous 10-minute ceiling.

## Verification checklist

1. Record `claude --version`, `claude auth status`, and `claude doctor`.
2. Inspect repository instructions and Git status before writes.
3. Use `-p` without PTY for bounded automation.
4. Distinguish tool visibility (`--tools`) from permission rules (`--allowedTools`/`--disallowedTools`).
5. Bound print work with turns, budget, timeout, and explicit permissions.
6. Prefer native background agents or isolated worktrees for parallel work.
7. Read files, inspect diff, and run tests independently.
8. Clean up background sessions and worktrees.

## Official sources

- [CLI reference](https://code.claude.com/docs/en/cli-reference)
- [Programmatic usage](https://code.claude.com/docs/en/headless)
- [Sessions](https://code.claude.com/docs/en/sessions)
- [Worktrees](https://code.claude.com/docs/en/worktrees)
- [Parallel agents](https://code.claude.com/docs/en/agents)
- [Subagents](https://code.claude.com/docs/en/sub-agents)
- [Agent teams](https://code.claude.com/docs/en/agent-teams)
- [Hooks](https://code.claude.com/docs/en/hooks)
- [Permissions](https://code.claude.com/docs/en/permissions)
- [Sandboxing](https://code.claude.com/docs/en/sandboxing)
- [MCP quickstart](https://code.claude.com/docs/en/mcp-quickstart)
- [Terminal configuration](https://code.claude.com/docs/en/terminal-config)
