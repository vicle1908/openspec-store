---
name: kimi-code
description: "Delegate coding and research to Kimi Code CLI."
version: 1.1.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Coding-Agent, Kimi, Moonshot, Code-Review, Refactoring, Automation]
    related_skills: [claude-code, codex, antigravity, hermes-agent]
---

# Kimi Code CLI — Hermes Orchestration Guide

Delegate coding, review, research, and terminal automation to Moonshot AI's Kimi Code CLI (`kimi`). It is a full terminal coding agent: it can inspect and edit code, run shell commands, search files, use web/MCP capabilities, load Skills, select agent profiles, and dispatch focused subagents.

This guide was validated against the installed `kimi 0.34.0` on 2026-08-08. When documentation and the installed binary disagree, use `kimi --help` and `kimi doctor config`.

The verified local configuration now follows the current guide: default model `gd-Advance`, `default_permission_mode = "auto"`, `loop_control.max_attempts_per_step = 5`, and `[mcp].tool_timeout_ms = 100000`. The credential-bearing config is protected as mode `0600`; never print its values.

## Canonical identity

Keep these names distinct and exact:

| Surface | Canonical name |
|---|---|
| Product | Kimi Code CLI |
| Hermes skill | `kimi-code` |
| Executable | `kimi` |
| Homebrew formula | `kimi-code` |
| Upstream repository | `MoonshotAI/kimi-code` |

Do not rename the skill or executable after a provider/model served through Kimi. Provider and model names are runtime configuration, not the product or binary name.

## Readiness

Verify the installed binary before delegating:

```bash
command -v kimi
kimi --version
kimi --help
kimi acp --help
kimi doctor config
```

`kimi doctor config` passes with no deprecation warnings after the documented 0.32 loop-control migration. Keep the current `max_attempts_per_step` and `tool_timeout_ms` names; do not reintroduce the removed aliases.

Install using the upstream install guide, or the Homebrew formula on supported systems:

```bash
brew install kimi-code
```

The supported project is Kimi Code CLI at `MoonshotAI/kimi-code`. Treat the older `MoonshotAI/kimi-cli` repository as legacy and use the current Kimi Code documentation when behavior differs.

Authentication is normally completed interactively with `/login`, or with the device-code command:

```bash
kimi login
```

Never print, copy, or pass authentication tokens as command-line arguments. A successful `kimi --version` proves installation only, not authentication.

## Preferred orchestration: print mode

Use `kimi -p` for bounded noninteractive work. It does not need a PTY and is the closest equivalent to `claude -p`, `codex exec`, and `agy --print`. The configured `default_permission_mode = "auto"` supplies full autonomous tool access for prompt mode.

Current `kimi 0.34.0` rejects explicit `--auto` and `--yolo` when combined with `-p/--prompt`; rely on the configured default for headless execution. Use `--auto` or `--yolo` only for interactive sessions when selecting a different persistent mode.
Omit `--model` by default so new sessions use the user's configured `default_model`; override it only when the task requires a specific model or a reproducible comparison:

```python
terminal(
    command=(
        "kimi -p 'Inspect the current repository, implement the requested change, "
        "and run focused tests.' --output-format stream-json"
    ),
    workdir="/absolute/path/to/repository",
    background=True,
    notify_on_complete=True,
)
```

Plain text is suitable for human handoff:

```bash
kimi -p "Review the current changes for correctness, security, and missing tests"
```

Use `--output-format stream-json` for automation. Parse stdout defensively: the installed CLI may emit an initial plain working-directory line before the JSONL events. Ignore/document that preamble, parse subsequent JSON objects independently, verify the process exit code, and preserve the final assistant result separately from progress/tool events.

Kimi prompt mode handles regular tool calls under the configured `auto` permission policy. Do not add `--auto` or `--yolo` to `-p`; current `kimi 0.34.0` rejects those combinations. Use `--auto` or `--yolo` only in interactive mode.

**MCP Router access**: kimi discovers MCP servers from the environment. All mcp-router tools are available automatically when the MCP server is running. Use `--skills-dir` to load additional skills:

```bash
kimi --skills-dir ~/.hermes/skills -p "Review this plan using all available tools"
```

## Interactive sessions

Kimi's TUI requires a real terminal/PTY:

```python
terminal(
    command="kimi --plan",
    workdir="/absolute/path/to/repository",
    background=True,
    pty=True,
    notify_on_complete=True,
)
```

Useful modes and session controls:

```bash
kimi --plan                 # explore and plan before edits
kimi --yolo                 # auto-approve regular tool calls
kimi --auto                 # fully autonomous mode
kimi --continue             # continue the latest session for this directory
kimi --session <id>         # resume a specific session
```

Use `--auto` only for trusted workspaces. `--yolo` skips regular approvals but is not identical to fully autonomous mode.

## Workspace and isolation

Set Hermes `workdir` to the target repository. For concurrent write tasks, create one Git worktree per task before starting Kimi; never run overlapping writers in one checkout:

```bash
git worktree add -b feature/task ../worktrees/task origin/main
```

Kimi supports repeatable `--add-dir` for additional workspace roots. Verify the resulting diff and tests outside Kimi before accepting its report. Kimi does not replace the workspace's worktree ownership rules.

## Sessions and agents

Kimi supports reusable Skills and custom agent profiles:

```bash
kimi --skills-dir /path/to/team-skills -p "Use the project workflow and review this change"
kimi --agent reviewer -p "Review the current diff and report only actionable findings"
kimi --agent-file /path/to/agent.md -p "Analyze this repository"
```

The official Kimi Code CLI includes built-in focused subagents such as `coder`, `explore`, and `plan`. Use them for independent read-only exploration or clearly partitioned work. Do not assume a particular subagent CLI flag; inspect the current agent documentation or use the interactive agent controls for the installed version.

## MCP and IDE integration

Kimi Code CLI supports MCP and can be driven from ACP-compatible IDEs/orchestrators through:

```bash
kimi acp
```

MCP configuration is managed through Kimi's documented MCP configuration flow (currently exposed through the CLI/TUI's `/mcp-config` workflow and configuration files). Inspect the installed documentation before changing persistent MCP configuration. Do not copy credentials from MCP Router or other clients into shell history.

For Zed or JetBrains ACP configuration, use the absolute path from `command -v kimi` when GUI-launched processes may have a different PATH:

```json
{
  "command": "/opt/homebrew/bin/kimi",
  "args": ["acp"],
  "env": {}
}
```

## Comparison with other delegation skills

| Workflow need | Kimi Code CLI | Claude Code | Codex | Antigravity |
|---|---|---|---|---|
| One-shot automation | `kimi -p` | `claude -p` | `codex exec` | `agy --print` |
| Structured output | `--output-format stream-json` | JSON/stream-json | `--json` | JSON/stream-json |
| Interactive TUI | `kimi` | `claude` | `codex` | `agy` |
| Plan mode | `--plan` | permission/plan modes | interactive/config | `--mode plan` |
| Autonomous mode | `--auto` | permission modes | approval policy/config | skip-permissions/mode |
| Sessions | `--continue`, `--session` | `--continue`, `--resume` | `resume` | `--continue`, conversation |
| Skills | `--skills-dir` and discovered Skills | Skills/plugins | Agent Skills/plugins | `.agents/skills`/plugins |
| IDE protocol | `kimi acp` | varies by integration | varies by integration | varies by integration |
| MCP | supported | supported | supported | supported |

Kimi is therefore suitable as a peer coding-agent backend for Hermes. The adapter should use `kimi -p` rather than assuming Claude/Codex/Antigravity-specific flags such as `--max-turns`, `--max-budget-usd`, `--dangerously-skip-permissions`, or `--print-timeout`.

## Complexity-adaptive execution limits

Kimi prompt mode exposes no portable max-turn or model-budget flag. Use task decomposition and the Hermes host timeout:

| Complexity | Typical scope | Host timeout |
|---|---|---:|
| Small | Read-only review, one-file change | 5–8 min |
| Medium | One subsystem and focused verification | 10–15 min |
| Large | One repository with several related modules | 20–30 min |

Do not assign several repositories or independent coverage/quality gates in one prompt. Split by repository or subsystem and use `--session <id>` / `--continue` only when the prior session is making useful progress. Stream JSON for long jobs so progress can be distinguished from a stall. If Kimi remains in planning/discovery without producing evidence or edits, terminate the bounded run and retry with a narrower prompt; adding more wall-clock time alone is not a remedy.

After a timeout or interruption, inspect the worktree before retrying. Preserve valid partial work, keep one-writer ownership, and verify outside Kimi.

## Verification checklist

- [ ] `command -v kimi` resolves the intended binary.
- [ ] `kimi --version` and `kimi --help` were checked in the current environment.
- [ ] Authentication was verified through Kimi's login/config flow without exposing credentials.
- [ ] The Hermes process uses the intended repository as `workdir`.
- [ ] Noninteractive runs use `kimi -p` with a bounded host-process timeout.
- [ ] Structured runs validate exit status and parse `stream-json` defensively.
- [ ] Concurrent writers use separate Git worktrees.
- [ ] Changed files, `git diff`, and focused tests were independently verified.

## Official sources

- [Homebrew formula: kimi-code](https://formulae.brew.sh/formula/kimi-code)
- [Kimi Code CLI repository](https://github.com/MoonshotAI/kimi-code)
- [Kimi CLI repository and migration notice](https://github.com/MoonshotAI/kimi-cli)
- [Command reference](https://moonshotai.github.io/kimi-code/en/reference/kimi-command)
- [IDE/ACP integration](https://moonshotai.github.io/kimi-code/en/guides/ides)
- [Kimi Code](https://www.kimi.com/code)
