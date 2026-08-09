---
name: codex
description: "Delegate coding to OpenAI Codex CLI (features, PRs)."
version: 2.1.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Coding-Agent, Codex, OpenAI, Code-Review, Refactoring, Automation]
    related_skills: [claude-code, antigravity, hermes-agent]
---

# OpenAI Codex CLI — Hermes Orchestration Guide

Delegate local coding, review, research, and automation to [OpenAI Codex CLI](https://developers.openai.com/codex/cli). This guide was validated against official OpenAI documentation and local `codex-cli 0.147.0` on 2026-08-08.

### Verified local setup

The current host uses the custom Responses provider `codex_local_access` with model `gpt-5.6-sol` at a local Cockpit endpoint. `codex login status` reports an authenticated API-key session, and `codex doctor` reports the provider/configuration as healthy. Never print the API key or copy it into prompts, logs, or command arguments.

The workspace umbrella `~/Developer` is not itself a Git repository. For commands launched at that umbrella root, include `--skip-git-repo-check`; for a real repository or worktree, prefer its own `workdir` and normal Git trust checks.

## Readiness

```bash
command -v codex
codex --version
codex login status
codex doctor
codex --help
codex exec --help
codex review --help
codex features list
```

Codex supports ChatGPT login, API key/access-token auth, custom Responses API providers, and local OSS providers. A missing `OPENAI_API_KEY` does not prove auth is absent; use `codex login status`. Also inspect `model_provider` and `model` from config without exposing provider credentials: this host currently uses a custom provider/model, so provider-backed verification here is not evidence about the default OpenAI endpoint.

Install/update with one supported route:

```bash
curl -fsSL https://chatgpt.com/codex/install.sh | sh
# or
npm install -g @openai/codex
# or
brew install --cask codex
```

## Preferred orchestration: `codex exec`

`codex exec` is noninteractive and does not require a PTY. Use it for one-shot tasks, CI, scripts, reviews, and Hermes background work.
**Always use full permissions** — `approval_policy="never"` for unattended delegation. The current host is configured for `danger-full-access`; use `--sandbox danger-full-access` when the user explicitly authorizes unrestricted filesystem/network access and the target workspace is controlled. Use `--skip-git-repo-check` for the umbrella `~/Developer` root.

```python
terminal(
    command=(
        "codex exec -c 'approval_policy=\"never\"' --sandbox danger-full-access "
        "--output-last-message /tmp/codex-final.txt "
        "'Implement the requested change and run focused tests.' < /dev/null"
    ),
    workdir="/path/to/repo",
    background=True,
    notify_on_complete=True,
)
```

A PTY is only needed for the interactive TUI/pickers, not `codex exec`.

**MCP Router access**: Codex discovers MCP servers from the environment. All mcp-router tools are available automatically when the MCP server is running. Use `--add-dir` for additional workspace roots if needed.

## Full Permission Default (MANDATORY for Hermes orchestration)

For authorized unrestricted coding tasks, invoke Codex with:

```bash
codex exec -c 'approval_policy="never"' --sandbox danger-full-access \
  --output-last-message /tmp/codex-final.txt "task prompt"
```

Use `--skip-git-repo-check` only when the working root is an umbrella directory such as `~/Developer`; use a repository/worktree `workdir` otherwise. `--dangerously-bypass-approvals-and-sandbox` is not needed when `--sandbox danger-full-access` plus `approval_policy="never"` is sufficient.

Flags breakdown:
- `-c 'approval_policy="never"'` — auto-approve all tool calls (no interactive prompts)
- `--sandbox danger-full-access` — unrestricted filesystem/network execution
- `--output-last-message <file>` — capture final response for Hermes to read

**NEVER use** `--full-auto` (does not exist) or `--dangerously-bypass-approvals-and-sandbox` (too permissive for normal use).

### Automation output

- Default: formatted progress plus final response
- `--json`: JSONL events such as `thread.started`, `turn.started`, `item.completed`, and `turn.completed`
- `--output-schema <file>`: require the final response to match a JSON Schema. Pass it on each turn where structured output is required; a later `codex exec resume` can continue the thread by ID without automatically implying a new schema requirement.
- `--output-last-message <file>`, `-o`: write the final natural-language response to a file
- `--ephemeral`: do not persist session files
- `--ignore-user-config`: skip `$CODEX_HOME/config.toml` while retaining auth
- `--ignore-rules`: skip user/project execpolicy rule files

For CI, combine JSONL progress with a final-message file:

```bash
codex exec --json -o /tmp/final.txt "Run tests and diagnose failures"
```

## Git and workspace semantics

Codex normally expects `exec` to run in a trusted Git repository, but this is not an absolute requirement:

```bash
codex exec --skip-git-repo-check "Analyze this directory"
```

Prefer a Git repo for coding work because diffs and checkpoints improve safety. Use:

- `-C, --cd <dir>` to set Codex's working root
- `--add-dir <dir>` to grant another writable root
- Hermes `workdir` to scope the host process
- manual Git worktrees for parallel write tasks

Codex has no top-level automatic `--worktree` flag in local v0.147.0. Create worktrees yourself before launching independent writers.

## Sandboxing and approvals

Sandbox modes:

- `read-only`: read/analysis only
- `workspace-write`: write within the workspace and configured writable roots
- `danger-full-access`: no Codex filesystem sandbox

Approval policies for the interactive CLI:

- `untrusted`
- `on-request`
- `never`

`codex exec` defaults to a read-only sandbox. For authorized unrestricted editing, use `danger-full-access` and approval policy `never`:

```bash
codex exec -c 'approval_policy="never"' --sandbox danger-full-access "task"
```

This prevents impossible interactive approval prompts. `danger-full-access` intentionally removes Codex filesystem/network sandboxing; use it only because the user authorized unrestricted agents and the target workspace is controlled.

In a Hermes service context, if Codex's native sandbox fails because host namespaces/seatbelt restrictions conflict, first inspect the actual error. If the user authorized implementation and the workspace itself is safely isolated, `--sandbox danger-full-access` may be used with explicit `workdir`, clean Git status, narrow prompts, diff review, and tests. Do not generalize a Linux bubblewrap failure to macOS or every host.

## Models, profiles, web, and local providers

- `-m, --model <model>` selects a model.
- `-c key=value` overrides any config key for one invocation.
- `-p, --profile <name>` layers `$CODEX_HOME/<name>.config.toml` over base config.
- `--strict-config` rejects unknown config keys.
- `--search` enables live web search; interactive Codex otherwise uses cached search where available.
- `--oss --local-provider ollama|lmstudio` selects a local OSS provider.
- Reasoning effort and other model behavior are configured through `-c`/profiles according to the current config reference.

User config lives at `~/.codex/config.toml`; trusted projects may add `.codex/config.toml` with documented restrictions.

## Sessions

Interactive sessions:

```bash
codex resume --last
codex resume <session-id> "Continue the task"
codex fork --last
codex archive <session-id-or-name>
codex unarchive <session-id-or-name>
codex delete <session-id-or-name>
```

Noninteractive sessions can also resume:

```bash
codex exec resume --last "Continue and run tests"
codex exec resume <session-id> "Address the remaining failure"
```

`codex resume --last` is scoped to the current directory unless `--all` is used. `--include-non-interactive` includes exec sessions in the interactive resume search.

## Code review

Codex has a dedicated non-mutating review surface:

```bash
codex review --uncommitted
codex review --base origin/main
codex review --commit <sha> --title "change title"
codex exec review --base origin/main
```

Choose exactly one review target. `--uncommitted`, `--base`, `--commit`, and a custom review prompt conflict as documented by the current CLI.

For remote PR review, check out the PR into a disposable clone/worktree, then use `codex review --base <base>`.

## Skills, plugins, hooks, MCP, and subagents

Current Codex is extensible:

- Skills follow the open Agent Skills format (`SKILL.md`) and are browsable with `/skills`.
- `codex plugin` manages plugins and marketplaces; `codex plugin list --json` is automation-friendly.
- Treat `codex mcp list --json` as secret-bearing: current v0.147.0 can include inline MCP `env` values. Parse and redact environment values before logging, storing, or reporting inventory; never paste raw output into evidence.
- Plugins can bundle tools, skills, MCP servers, and other assets.
- Lifecycle hooks are stable in local v0.147.0 and configurable through `hooks.json` or `config.toml`; inspect with `/hooks`.
- `codex mcp` manages stdio and streamable HTTP MCP servers. OAuth is supported for compatible HTTP servers.
- `codex mcp-server` exposes Codex itself as a stdio MCP server.
- Multi-agent is stable in local v0.147.0. The TUI uses `/agent` or `/subagents` to inspect and switch agent threads.

MCP examples:

```bash
codex mcp add context7 -- npx -y @upstash/context7-mcp
codex mcp add remote-docs --url https://example.com/mcp
# `list --json` may contain inline env secrets; redact before display/storage.
codex mcp list --json | jq 'map(.transport.env = (if .transport.env then (.transport.env | with_entries(.value = "<redacted>")) else null end))'
codex mcp login remote-docs
```

## Interactive TUI

Run `codex` for a conversational TUI. It requires a real terminal/PTY; tmux is optional but useful for Hermes-managed multi-turn sessions.

```python
terminal(
    `codex --sandbox danger-full-access`
    workdir="/path/to/repo",
    background=True,
    pty=True,
    notify_on_complete=True,
)
```

Useful controls include `/permissions`, `/model`, `/diff`, `/review`, `/compact`, `/resume`, `/fork`, `/skills`, `/plugins`, `/mcp`, `/hooks`, `/agent`, and `/subagents`. `Tab` queues a follow-up while Codex is working; `Enter` steers the current turn.

## Parallel work with manual worktrees

Never run overlapping writers in one checkout. Create one worktree per independent task:

```bash
git worktree add -b fix/issue-78 ../worktrees/issue-78 origin/main
git worktree add -b fix/issue-99 ../worktrees/issue-99 origin/main
```

Then launch separate `codex exec --sandbox danger-full-access` processes with each worktree as `workdir`. Monitor them with Hermes background process tools, verify each diff/tests, and integrate serially.

## Complexity-adaptive execution limits

Codex `exec` has no portable max-turn flag in the installed CLI, so bound it with task shape, host timeout, and progress monitoring:

| Complexity | Typical scope | Host timeout |
|---|---|---:|
| Small | Review, diagnosis, one-file fix | 5–8 min |
| Medium | One subsystem with focused tests | 10–15 min |
| Large | One repository with related modules and full gates | 20–30 min |

Split cross-repository or multi-subsystem work into separate worktrees/invocations. Use `codex exec resume <thread-id>` for a narrow continuation when the prior run produced useful context. Do not let a completed coding task drift into unrelated environment repair or index regeneration: if tests/diff show the assigned artifact is ready, stop the process and verify externally. Extend a timeout only when JSONL/progress output shows productive work rather than repeated discovery.

A host timeout does not invalidate already-written work. Inspect and preserve valid edits, then resume or finish manually under one-writer ownership. Never interpret a long-running process as evidence of correctness.

## Verification checklist

1. Record `codex --version`, `codex login status`, and relevant `--help` output.
2. Inspect `git status` and repository instructions before write tasks.
3. Prefer `codex exec` without PTY for automation.
4. Use `danger-full-access` only for authorized controlled workspaces; preserve one-writer worktree ownership.
5. Use `--json`/`-o` when machine-readable progress or a stable final artifact is needed.
6. Read changed files and inspect `git diff` outside Codex.
7. Run focused tests and required repository gates.
8. For parallel writers, use separate worktrees.

## Official sources

- [Codex CLI](https://developers.openai.com/codex/cli)
- [CLI reference](https://developers.openai.com/codex/cli/reference)
- [Noninteractive mode](https://developers.openai.com/codex/noninteractive)
- [Configuration reference](https://developers.openai.com/codex/config-reference)
- [Approvals and security](https://developers.openai.com/codex/agent-approvals-security)
- [Skills](https://developers.openai.com/codex/skills)
- [MCP](https://developers.openai.com/codex/mcp)
