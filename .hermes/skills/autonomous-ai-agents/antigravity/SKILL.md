---
name: antigravity
description: "Delegate coding to Google Antigravity CLI (agy)."
version: 1.2.2
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Coding-Agent, Google, Antigravity, Autonomous, Refactoring, Code-Review]
    related_skills: [claude-code, codex, opencode, hermes-agent]
---

# Antigravity CLI (`agy`) — Hermes Orchestration Guide

Delegate coding tasks to [Google Antigravity CLI](https://antigravity.google/docs/cli/overview). It supports noninteractive and interactive sessions, multi-file editing, commands, conversation history, structured output, subagents, MCP, plugins, skills, and native terminal sandboxing.

This guide was validated against official Google documentation and local `agy 1.1.11` on 2026-08-03. When docs and the installed binary disagree, use `agy --help` and `agy models` for the installed version.

### Verified local setup

The current local binary is `agy 1.1.11`. `agy models` currently lists `gemini-3.6-flash-high`, `gemini-3.6-flash-medium`, `gemini-3.6-flash-low`, `gemini-3.5-flash-*`, `gemini-3.1-pro-*`, `claude-sonnet-4-6`, `claude-opus-4-6-thinking`, and `gpt-oss-120b-medium`. A verified headless smoke test uses the configured default and returns `Gemini 3.6 Flash (High)`; do not invent a provider/model alias.

## Readiness

```bash
command -v agy
agy --version
agy --help
agy models
agy agent
agy plugin list
```

Installation:

```bash
brew install --cask antigravity-cli
# or
curl -fsSL https://antigravity.google/cli/install.sh | bash
```

The native installer uses `~/.local/bin/agy`; Homebrew currently links `agy` under its prefix. Authentication is interactive on first launch and subsequently uses the OS keyring. Settings live at `~/.gemini/antigravity-cli/settings.json`.

### Read-only configuration inventory

When auditing agent configuration, honor the exact path named by the user. For Antigravity, discover and read `~/.gemini/antigravity-cli/settings.json`; do not substitute a provider or model name for the configuration directory. If a path is absent, report it once and switch to targeted discovery instead of retrying the same missing path. Use `agy --version` for the installed version, then report only non-secret fields such as model, provider (if explicitly present), and settings presence. Treat account/auth files and inline credential fields as presence-only: never print their contents, values, emails, refresh tokens, or API keys. If the settings file has a model but no provider field, report the provider as unspecified rather than inferring one from the model name.

There is no `agy doctor` subcommand in v1.1.11. `agy doctor` is interpreted as an interactive prompt and fails without a TTY. Use version/help, a minimal print invocation, and the troubleshooting docs for diagnostics.

## Preferred orchestration: headless mode (print mode)

Use `-p` (or `--print` / `--prompt`) for bounded noninteractive work. It does not require a PTY.
**Always use `--dangerously-skip-permissions`** for unattended delegation — auto-approves all tool calls.

**CRITICAL**: The prompt goes DIRECTLY after `-p`, not as a separate argument.

```python
terminal(
    command=(
        "agy -p 'Implement the task and run tests.' "
        "--dangerously-skip-permissions "
        "--output-format json "
        "--print-timeout 20m"
    ),
    workdir="/path/to/project",
    background=True,
    notify_on_complete=True,
)
```

`--dangerously-skip-permissions` is required for headless file reads, writes, Bash, and MCP calls. Without it, headless mode soft-denies tools that would require approval and may return an empty response. Use a dedicated worktree or externally isolated workspace when granting this authority.
```

**Key flags (from official docs)**:
| Flag | Description |
|------|-------------|
| `-p`, `--print`, `--prompt` | Run a single prompt non-interactively |
| `--output-format` | `text` (default), `json`, or `stream-json` |
| `--json-schema` | Schema string or file path for structured output |
| `--model` | Model slug (see `agy models`) |

| `--agent` | Agent name (see `agy agents`) |
| `--continue`, `-c` | Continue the most recent conversation |
| `--conversation` | Resume a conversation by ID |
| `--dangerously-skip-permissions` | Auto-approve all tool permission requests |
| `--print-timeout` | Maximum time to wait (default `5m`) |
| `--sandbox` | Run with terminal sandbox restrictions |

**Output format**: JSON envelope contains `conversation_id`, `status`, `response`, `duration_seconds`, `num_turns`, `usage`.

**MCP Router access**: agy discovers MCP servers from the environment. All mcp-router tools are available automatically when the MCP server is running.

**Permissions**: By default, tools requiring approval are "soft-denied" in headless mode. Use `--dangerously-skip-permissions` to auto-approve all tool calls.

### Output formats

- `text`: final response
- `json`: one result object with `conversation_id`, `status`, `response`, `duration_seconds`, `num_turns`, and `usage`
- `stream-json`: JSON event stream, including an `init` event whose `cwd` proves the process workspace
- `--json-schema <schema-or-path>`: constrains structured output; for `stream-json`, applies to the final result

Validated result shape:

```json
{
  "conversation_id": "...",
  "status": "SUCCESS",
  "response": "...",
  "duration_seconds": 5.5,
  "num_turns": 1,
  "usage": {
    "input_tokens": 19973,
    "output_tokens": 7,
    "thinking_tokens": 0,
    "cache_read_tokens": 0,
    "total_tokens": 19980
  }
}
```

Check both process exit code and JSON `status`. A timed-out run can return JSON with `status: "ERROR"`, partial usage, and no final response.

When the final response is itself a deliverable, capture the complete JSON envelope to a file at invocation time and extract its `response` only after successful exit. Do not make `head` the only sink for long output. If stdout was not saved, recover from Antigravity's `transcript_full.jsonl` rather than the potentially truncated `transcript.jsonl`. See [references/output-capture-and-recovery.md](references/output-capture-and-recovery.md) for the validated capture and fallback workflow.

For strict read-only reviews where creating a temporary capture file is disallowed, use a tracked background process and recover a large one-line JSON envelope from the full process log if the wait display shows only its tail. See [references/read-only-review-orchestration.md](references/read-only-review-orchestration.md) for the frozen-ref, live-setting verification, and before/after status workflow.

## Workspace and project semantics

Antigravity has two related but distinct concepts:

- The OS process CWD. Hermes `workdir` and a shell `cd` both set this correctly; `stream-json` exposes it as `init.cwd`.
- The Antigravity project/conversation workspace. A resumed/default project can retain prior workspace state, and tool-generated artifacts can appear under `~/.gemini/antigravity-cli/scratch/` even when the process CWD is correct.

Therefore:

1. Always set the Hermes `workdir` for clarity and containment.
2. Use the process CWD as the primary workspace. Add `--new-project` only when you need a fresh logical Antigravity project/conversation container; it does not perform `cd` or create a filesystem workspace.
3. For additional roots, use repeatable `--add-dir <path>`.
4. For automation where placement matters, give the agent absolute target paths and verify the resulting file on disk.
5. Do not diagnose a scratch artifact as a failed `cd`. Inspect `stream-json` `init.cwd`, project/conversation state, and the actual file path first.

Validated file-write pattern (uses the configured default model):

**CRITICAL**: The prompt goes DIRECTLY after `-p`, not after other flags.

```python
terminal(
    command=(
        "agy -p 'Edit /absolute/project/src/example.py and run the focused tests.' "
        "--dangerously-skip-permissions "
        "--new-project --add-dir /absolute/project "
        "--print-timeout 20m --output-format json"
    ),
    workdir="/absolute/project",
    background=True,
    notify_on_complete=True,
)
```

The official best-practices page shows `--cwd`, but local v1.1.11 rejects it. Do not use `--cwd` unless the installed `agy --help` lists it.

## Models

By default, let `agy` use the model configured by the user. A normal smoke test should therefore omit both `--model` and model-specific tuning flags:

```bash
agy -p "Reply with OK"
```

Use `agy models` only when the task calls for an explicit model selection, a reproducible comparison, or diagnosis of a rejected configured model. It prints the exact accepted identifiers. Settings may display a human-readable default-model alias; when overriding the default, select a runtime-listed slug and record the override in verification evidence. Local v1.1.11 validated these slug forms directly:

```text
gemini-3.6-flash-high
gemini-3.6-flash-medium
gemini-3.6-flash-low
gemini-3.5-flash-high
gemini-3.5-flash-medium
gemini-3.5-flash-low
gemini-3.1-pro-high
gemini-3.1-pro-low
claude-sonnet-4-6
claude-opus-4-6-thinking
gpt-oss-120b-medium
```

Explicit override example, only when the task requires this model and the installed CLI reports it:

```bash
agy --model gemini-3.6-flash-low -p "Reply with OK"
```

Do not invent display names or rewrite `gemini` as another brand. Model availability is account/version dependent; query it at runtime before an explicit override. A rejected model-specific flag is a reason to remove that unnecessary override or consult current help, not to rename the agent or binary.

## Sessions and execution modes

- `--continue`, `-c`: continue the most recent conversation
- `--conversation <id>`: resume a conversation by ID. Live v1.1.11 verification showed that a conversation created with `--json-schema` can retain that schema and continue returning `structured_output` on resume even when the flag is not re-passed; inspect the resumed envelope rather than assuming schema state is cleared.
- `--prompt-interactive`, `-i`: send an initial prompt and continue interactively
- `--project <id>`: attach to an existing Antigravity project
- `--new-project`: create a project for this session
- `--mode accept-edits`: auto-approve file edits, subject to tool permission rules
- `--mode plan`: read/analyze first and propose a plan before editing
- default interactive mode: review edits
- `--disable-slash-commands`: disable slash command and skill expansion in print mode

Antigravity v1.1.11 has no `--max-turns` or dollar-budget cap. Bound unattended work with a specific prompt, `--print-timeout`, process timeout, permissions, and post-run verification.

## Permissions and sandbox

Official permission resource forms include:

- `read_file(path)` / `write_file(path)`
- `command(prefix-or-pattern)`
- `read_url(domain)` / `execute_url(domain)`
- `unsandboxed(prefix)`
- `mcp(server/tool)` or `mcp(*)`

Precedence is `deny` > `ask` > `allow`. Workspace reads/writes are auto-allowed by the default engine; commands, MCP, web actions, and non-workspace paths otherwise ask.

Settings example:

```json
{
  "toolPermission": "request-review",
  "artifactReviewPolicy": "asks-for-review",
  "enableTerminalSandbox": true,
  "allowNonWorkspaceAccess": false,
  "permissions": {
    "allow": ["command(git status)", "mcp(mcp-router/get_usage_stats)"],
    "deny": ["command(rm -rf)", "write_file(.git/)"]
  }
}
```

Valid global MCP wildcard syntax is `mcp(*)`, not `mcp*`.

- `--sandbox` enables native terminal restrictions.
- `--dangerously-skip-permissions` auto-approves tool permission requests; use only in an externally controlled workspace.
- `--mode accept-edits` controls artifact/file review, not all shell-command permissions.

Do not encode a specific interactive warning-dialog key sequence unless it is freshly observed on the installed version; dialog layout is version/state dependent.

## Interactive TUI

For a human-driven session, launch `agy` normally. For Hermes-managed multi-turn interaction, use a PTY or tmux so the TUI has a terminal and can be monitored. Tmux is useful, not an inherent Antigravity requirement.

```bash
tmux new-session -d -s agy-work -c /path/to/project -x 140 -y 40
tmux send-keys -t agy-work 'agy --new-project' Enter
tmux capture-pane -t agy-work -p -S -80
```

Useful official TUI commands include `/agents`, `/tasks`, `/resume`, `/rewind`, `/fork`, `/diff`, `/permissions`, `/mcp`, `/skills`, `/hooks`, `/config`, and `/exit`. Official pages currently conflict about `/fast` and planning command names; rely on the TUI's own `/help` and `Shift+Tab` behavior for the installed version.

## Subagents, plugins, skills, MCP, and hooks

- Async subagents and background tasks are available; inspect them with `/agents` and `/tasks`.
- Official current shortcut for the next waiting subagent is `Alt+J`; `Ctrl+K` fast-approves a pending subagent action.
- Workspace custom agents: `.agents/agents/`; global agents: `~/.gemini/config/agents/`.
- Workspace skills: `.agents/skills/`; skills become slash commands.
- Plugins may bundle skills, agents, rules, MCP servers, and hooks.
- `agy plugin` supports `list`, `import`, `install`, `uninstall`, `enable`, `disable`, `validate`, and `link` in v1.1.11.
- MCP is managed interactively with `/mcp` or through plugin/config files.

## Complexity-adaptive limits

Antigravity v1.1.11 has no max-turn flag. Set both `--print-timeout` and the longer Hermes host timeout according to scope:

| Complexity | Typical scope | `--print-timeout` | Host timeout |
|---|---|---:|---:|
| Small | Review, diagnosis, one-file fix | 5m | 8 min |
| Medium | One subsystem with focused tests | 10m | 15 min |
| Large | One repository with related modules and full verification | 20m | 25–30 min |

Split multi-repository and independent-gate work into separate worktrees/projects. Prefer one repository or one cohesive subsystem per print invocation. Continue by conversation ID only when the prior run produced useful progress. If the response claims completion but cites nonexistent paths, misses external failures, or ends with an unrelated MCP/index error, treat it as unverified and inspect the worktree directly.

Longer timeouts are appropriate for active test/build work, not repeated discovery. Monitor stream JSON or process output; stop and narrow the task when progress stalls or leaves the assigned scope.

## Pitfalls

1. **Do not assume an `--effort` flag exists.** Current `agy 1.1.11 --help` does not advertise `--effort`; select the exact reasoning variant from `agy models` (for example `gemini-3.6-flash-high`) instead. Recheck help after upgrades.

2. **`--cwd` is rejected in v1.1.11.** The official best-practices page shows `--cwd`, but the installed CLI rejects it. Use Hermes `workdir` parameter instead.

3. **`agy doctor` is NOT a diagnostic command.** It is interpreted as an interactive prompt and fails without a TTY. Use `agy --version`, `agy --help`, and a minimal `agy -p` invocation for health checks.

4. **No `--max-turns` or budget cap.** Bound unattended work with `--print-timeout` and Hermes host timeout, not a nonexistent flag.

5. **`--json-schema` state persists across resume.** A conversation created with `--json-schema` continues returning structured output on resume even when the flag is not re-passed. Inspect the resumed envelope rather than assuming schema state is cleared.

6. **`--print` / `--prompt` with flags in between breaks the prompt.** If you write `agy --print --dangerously-skip-permissions "prompt"`, the prompt is consumed as a flag value, NOT as the prompt text. The prompt MUST go directly after `-p`: `agy -p "prompt" --dangerously-skip-permissions`.

## Verification checklist

1. Capture `agy --version`, `agy --help`, and `agy models` when inventorying capabilities.
2. Use print mode without PTY for one-shot work.
3. Set Hermes `workdir` for the filesystem workspace; use `--new-project` only for fresh logical project/session state.
4. Preserve the configured default model unless the task requires an override; when overriding, choose an exact identifier from `agy models` and verify model-specific flags against current help.
5. Use JSON or stream JSON and check exit code plus `status`.
6. For writes, require absolute paths and read the files back outside Antigravity.
7. Inspect git diff and run focused tests before accepting coding work.
8. Remove disposable projects/artifacts after validation.

## Official sources

- [Overview](https://antigravity.google/docs/cli/overview)
- [Installation and auth](https://antigravity.google/docs/cli/install)
- [Using AGY CLI](https://antigravity.google/docs/cli/using)
- [CLI reference](https://antigravity.google/docs/cli/reference)
- [Projects](https://antigravity.google/docs/cli/projects)
- [Permissions](https://antigravity.google/docs/cli/permissions)
- [Sandbox](https://antigravity.google/docs/cli/sandbox)
- [Subagents](https://antigravity.google/docs/cli/subagents)
- [Plugins and skills](https://antigravity.google/docs/cli/plugins)
- [Best practices](https://antigravity.google/docs/cli/best-practices)
- [Troubleshooting](https://antigravity.google/docs/cli/troubleshooting)
