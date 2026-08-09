---
name: pi
description: "Delegate coding to Pi CLI (features, reviews, automation)."
version: 1.2.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Coding-Agent, Pi, Code-Review, Refactoring, Automation]
    related_skills: [claude-code, codex, antigravity, hermes-agent]
---

# Pi Coding Agent — Hermes Orchestration Guide

Delegate local coding, review, research, and automation to [Pi Coding Agent](https://pi.dev). This guide was validated against official Pi documentation and local Pi v0.84.1 on 2026-08-09.

## Overview

Pi is a minimal, extensible terminal coding harness. Core Pi supplies four model-callable tools—`read`, `write`, `edit`, and `bash`—plus interactive, print/text, JSON, RPC, and SDK modes. Optional extensions add capabilities rather than expanding the core by default.

Hermes should prefer non-interactive print mode for bounded delegation, use a dedicated Git worktree for writes, and independently verify files, diffs, and tests. Pi's final narrative is a self-report, not completion evidence.

## When to Use

Use this skill when delegating coding, repository review, debugging, refactoring, or bounded automation to the `pi` CLI.

Do not use it for:

- Direct Hermes subagent delegation; use Hermes `delegate_task` instead.
- Tasks needing user interaction during the run; use Pi's interactive TUI with a PTY.
- Overlapping writes in a checkout already owned by another agent.
- Work whose authority cannot safely include Pi's enabled tools and extensions.

## Readiness

```bash
command -v pi
pi --version
pi --help
pi list
pi --list-models
```

Local validated baseline:

- Binary: `/opt/homebrew/bin/pi`
- Version: `0.84.1`
- Core built-in tools: `read`, `write`, `edit`, `bash`
- Fresh-install default provider documented by help: `google`
- Effective local defaults may differ; inspect settings without printing credential material.

Install or update using a supported route:

```bash
curl -fsSL https://pi.dev/install.sh | sh
# or
npm install -g --ignore-scripts @earendil-works/pi-coding-agent
# update Pi and installed packages
pi update
```

Do not install or update unless the user asked for package mutation. For future skill maintenance, re-run local help because Pi and extensions evolve independently.

### Verified local provider setup

The current local Pi installation is `0.84.1` and uses the custom provider name `shopapikey` (exact spelling) with model `fable-5`. The name must match in both `~/.pi/agent/settings.json` (`defaultProvider`) and `~/.pi/agent/models.json` (`providers`); any mismatch causes provider-resolution errors. Verify provider/model registration without exposing credentials:

```bash
pi --list-models
pi -p --no-session --no-tools --provider shopapikey --model fable-5 \
  "Reply with exactly: PI_PROVIDER_OK"
```

The installed Pi configuration also exposes `cockpit` and `omniroute` providers. Keep provider-specific overrides explicit in evidence and do not print API keys.

## Authentication and provider readiness

Pi supports OAuth/subscription login for selected providers and API-key authentication for many providers. Interactive `/login` manages provider authentication. Environment variables include `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `KIMI_API_KEY`, `OPENROUTER_API_KEY`, and others listed by `pi --help`.

Never print credential values or pass a secret directly through `--api-key` in logged orchestration commands. A missing environment variable does not prove authentication is absent because Pi can persist OAuth or provider state. Prefer a bounded no-tools probe through the intended provider/model, then interpret the actual process result.

```bash
pi -p --no-session --no-tools \
  --provider <provider> --model <model> \
  "Answer this harmless readiness question in one sentence."
```

Do not override the user's effective provider/model without a task-specific reason. Record any explicit override in the task evidence.

## Preferred orchestration: print mode

Use `pi -p` for bounded non-interactive work. It does not require a PTY.
**Use full tool access** for authorized coding tasks: omit `--no-tools` and pass `--approve --tools read,write,edit,bash` (plus `mcp` when required). Pi does not provide a separate approval bypass; `--approve` trusts project-local resources, while the explicit tool list enables the coding primitives.

```python
terminal(
    command=(
        "pi -p --no-session --approve "
        "--tools read,write,edit,bash "
        "'Implement the requested change and run focused tests.'"
    ),
    workdir="/path/to/dedicated/worktree",
    background=True,
    notify_on_complete=True,
)
```

Key controls:

| Flag | Purpose |
|---|---|
| `-p`, `--print` | Process prompt and exit (non-interactive) |
| `--mode text\|json\|rpc` | Output mode; text is the default |
| `--no-session` | Avoid persisting an ephemeral one-shot run |
| `--provider <name>` | Provider name override |
| `--model <pattern>` | Model selection (supports `provider/id` and `:thinking` shorthand) |
| `--thinking off\|minimal\|low\|medium\|high\|xhigh\|max` | Reasoning level |
| `--tools <names>` | Comma-separated tool allowlist (core/extension tools only) |
| `--exclude-tools <names>` | Comma-separated tool denylist (core/extension tools only) |
| `--no-tools` | Disable all tools (built-in and extension) |
| `--approve` | Trust project-local Pi resources for this run |
| `--continue` | Continue previous session |
| `--session <path\|id>` | Use specific session file or partial UUID |

`--approve` is project-resource trust, not a general permission system or filesystem sandbox. Pi intentionally has no built-in permission popups. Scope authority through an isolated worktree/container, narrow tools, explicit working directory, and independent verification.

### Verified bounded no-tool review

The local `pi-mcp-adapter` previously used `directTools: true`, registering 77 direct MCP tools and keeping headless processes alive after valid output. The verified default is now proxy mode (`directTools: false` in `~/.pi/agent/mcp.json`). For bounded reviews that need no tools or extensions, use:

```bash
pi -p --no-session --no-tools --no-extensions "review prompt"
```

These are lifecycle/tool controls only; they preserve Pi's configured default provider and model. Native subprocess verification on 2026-08-09 produced exit 0, a valid smoke response, and a substantive `APPROVE_WITH_CONDITIONS` review in 25 seconds.

**MCP Router access**: Pi discovers MCP servers through the `pi-mcp-adapter` extension. When installed, all mcp-router tools are available automatically. Use `--tools mcp` to enable MCP proxy mode:

```python
terminal(
    command=(
        "pi -p --no-session --approve --tools read,write,edit,bash,mcp "
        "'Use all available tools including MCP to implement the change'"
    ),
    workdir="/path/to/project",
    background=True,
    notify_on_complete=True,
)
```

### JSON output

Use `--mode json` when machine-readable event streams are useful:

```bash
pi -p --mode json --no-session --tools read,bash \
  "Inspect the repository and report the failing tests. Do not edit files."
```

Treat JSON as an event stream whose exact fields may evolve. Validate the exit status and parse only fields needed by the workflow. Do not assume text embedded in a successful event proves repository changes or tests.

### Input files

Prefix file paths with `@` to include them in the initial message:

```bash
pi -p --no-session @proposal.md @design.md \
  "Review these documents for contradictions."
```

Use trusted local paths only. Images are supported as file arguments when the selected model accepts them.

## Tool scoping

Pi's core tools are broad primitives:

| Tool | Capability | Automation guidance |
|---|---|---|
| `read` | Read file contents | Safe baseline for review |
| `write` | Create or overwrite files | Enable only in an isolated write workspace |
| `edit` | Find/replace editing | Enable only for authorized mutations |
| `bash` | Execute shell commands | Broadest authority; constrain by workspace and prompt |
| `grep` | Read-only content search | Off by default; enable explicitly if needed |
| `find` | Read-only glob discovery | Off by default; enable explicitly if needed |
| `ls` | Read-only directory listing | Off by default; enable explicitly if needed |

Read-only review recipe:

```bash
pi -p --no-session --approve --tools read,write,edit,bash \
  "Review the current changes for correctness and missing tests; edit only if the task explicitly authorizes fixes."
```

Write-task recipe:

```bash
pi -p --no-session --approve --tools read,write,edit,bash \
  "Implement only the requested change. Run the focused test command. Do not commit or push."
```

## MCP tools via pi-mcp-adapter

Pi integrates MCP tools through the `pi-mcp-adapter` extension. When installed (check with `pi list`), MCP tools from configured servers are available to the model alongside Pi core tools.

Verified MCP tool behavior (v0.84.1):

| Aspect | Behavior |
|---|---|
| Availability | MCP tools are loaded by pi-mcp-adapter and visible to the model |
| `--tools` filtering | Direct MCP tools are filterable when they are registered as Pi tools; use the generated Pi tool names |
| `--exclude-tools` | Direct MCP tools can be denylisted the same way when registered directly |
| `--no-tools` | Disables all active Pi tools, including direct MCP tools, but proxy-mode MCP remains governed by whether the `mcp` tool itself is active |
| Tool naming | Direct MCP tools use adapter-generated names based on `toolPrefix`; with the default `server` prefix, server `mcp-router` + tool `brave_web_search` becomes `mcp_router_brave_web_search` |
| Configuration | MCP servers are configured in shared MCP files and Pi override files; adapter-specific behavior is commonly persisted in `~/.pi/agent/mcp.json` or `.pi/mcp.json` |

Use the right control surface for the MCP mode in play:

- **Direct tools:** filter with `--tools` / `--exclude-tools` using the generated Pi tool names.
- **Proxy mode:** filter through adapter config (`directTools`, `includeTools`, `excludeTools`, `disableProxyTool`, approvals) because all proxy access funnels through the single `mcp` tool.
- **Alternate config:** use `--mcp-config <path>` when you need a different MCP server/config set for one run.

```bash
# Direct MCP tool allowlist by generated Pi name
pi -p --no-session --tools mcp_router_brave_web_search \
  "Call mcp_router_brave_web_search with query 'Pi latest release notes'."

# Proxy-mode discovery through the single mcp tool
pi -p --no-session --tools mcp \
  "Use the mcp tool to search for a Brave web search tool, then call it."

# Combine direct MCP + core tools in one task
pi -p --no-session --tools mcp_router_list_repos,read \
  "Use mcp_router_list_repos to get repo stats, then use read to check a file."
```

For prompt efficiency, prefer the proxy or a curated direct subset. The adapter itself recommends targeted direct sets (roughly 5–20 tools) rather than exposing dozens of direct tools at once.

Extensions can register additional tools and flags. Check `pi --help` and `pi list` on the target installation before relying on extension capabilities.

## Sessions and continuations

```bash
pi --continue "Continue and run the remaining tests"
pi --resume
pi --session <path-or-partial-id> "Address the remaining failure"
pi --session-id <exact-project-session-id> "Continue this task"
pi --fork <path-or-partial-id> "Try the alternative approach"
pi --name "Refactor auth module"
```

- `--continue` continues the previous session.
- `--resume` opens session selection; it is interactive unless the invocation supplies a specific session through another flag.
- `--session` accepts a session path or partial UUID.
- `--session-id` uses an exact project session ID and creates it when missing.
- `--fork` branches an existing session into a new session.
- `--session-dir` changes session storage/lookup.
- `--no-session` is preferred for disposable automation.

Resume only when retained context materially helps. Re-supply invocation-specific model, tool, extension, and trust controls rather than assuming prior flags are restored.

## Context, skills, extensions, and packages

Pi discovers project context from `AGENTS.md` and `CLAUDE.md`. It supports `SYSTEM.md`, prompt templates, skills, themes, and TypeScript extensions.

Controls:

```bash
pi --no-context-files -p "Analyze only the supplied files"
pi --skill /path/to/skill -p "Apply the supplied workflow"
pi --extension /path/to/extension.ts -p "Use the explicit extension"
pi --prompt-template /path/to/prompts -p "Use the supplied template"
pi --no-skills --no-extensions --no-prompt-templates -p "Run with minimal discovery"
```

Project-local resources can change agent behavior. Use `--approve` only for a trusted repository after reading its instructions; use `--no-approve` or disable relevant discovery for untrusted input.

Package management:

```bash
pi list
pi install <source>
pi remove <source>
pi update <source>
pi config
```

Package operations mutate Pi settings and may execute network/package-manager activity. Perform them only when explicitly authorized. Use `-l` where supported to select local scope; consult `pi <command> --help` before mutation.

## Core omissions and optional extensions

Pi deliberately omits several features from core:

- **No built-in MCP:** use CLI tools documented by skills or an MCP extension/package (e.g. `pi-mcp-adapter`).
- **No built-in sub-agents:** use tmux/process orchestration or a sub-agent extension/package.
- **No built-in plan mode:** write plans to files or load a plan-mode extension.
- **No built-in permission popups:** isolate execution or install/build a confirmation extension.
- **No built-in to-do system:** use a tracked task file or an extension.
- **No built-in background Bash:** use Hermes background processes or tmux outside Pi.

Do not claim these features are unavailable when the current Pi installation has an extension providing them. Conversely, do not treat local extension flags as portable Pi core behavior.

## Interactive TUI

Interactive Pi requires a terminal/PTY. Tmux is optional and useful for durable monitoring.

```python
terminal(
    command="pi --approve",
    workdir="/path/to/dedicated/worktree",
    background=True,
    pty=True,
    notify_on_complete=True,
)
```

Important interactive controls documented by Pi:

| Control | Action |
|---|---|
| `/model` or `Ctrl+L` | Switch model |
| `Ctrl+P` | Cycle configured favorite models |
| `/tree` | Navigate tree-structured session history |
| `/export` | Export a session to HTML |
| `/share` | Share via session viewer / GitHub gist |
| `Enter` while working | Steer the current run (after current tool) |
| `Alt+Enter` | Queue a follow-up after current run finishes |
| `/reload` | Reload resources after config/extension changes |
| `/hotkeys` | Show all keyboard shortcuts |

Do not hard-code UI navigation sequences. Inspect the rendered TUI and current `/hotkeys` output.

## Worktrees and parallel execution

Pi has no core automatic worktree flag in local v0.84.1. Create worktrees before starting independent writers:

```bash
git worktree add -b fix/issue-78 ../worktrees/issue-78 origin/main
git worktree add -b fix/issue-99 ../worktrees/issue-99 origin/main
```

Run one Pi process per worktree. Never let two agents write overlapping paths. The parent remains the integration owner and verifies each diff before serial integration.

## Complexity-adaptive execution limits

Pi v0.84.1 has no native max-turn or budget flag. Give complex tasks a generous Hermes host timeout (20–30 minutes for large repository work), use milestone prompts, and monitor progress externally. Tool availability is controlled by the explicit tool list; do not confuse host timeout with a permission restriction.

| Complexity | Typical scope | Host timeout |
|---|---|---:|
| Small | Read-only review, diagnosis, one-file fix | 5-8 min |
| Medium | One subsystem with focused tests | 10-15 min |
| Large | One repository with related modules and full gates | 20-30 min |

Split cross-repository or multi-subsystem work into separate worktrees/invocations. A host timeout does not invalidate work already written. Inspect files and diff, preserve valid edits, and continue with a narrower prompt or explicit session resume. Extend time only when process output shows productive progress.

## Verification workflow

After Pi exits:

1. Confirm process exit status and preserve useful JSON/text output.
2. Run `git status --short` and ensure every changed path belongs to the authorized task.
3. Inspect `git diff --check` and the actual diff outside Pi.
4. Read critical changed files; do not rely on Pi's summary.
5. Run focused tests, then repository-required lint/type/full gates.
6. Confirm no commits, pushes, generated indexes, or unrelated environment changes occurred unless explicitly authorized.
7. Clean up disposable sessions/worktrees only after preserving required evidence.

Completion requires the artifact and external checks, not merely a successful Pi response.

## Common Pitfalls

1. **Treating `--approve` as a sandbox.** It trusts project-local resources; it does not constrain Bash or filesystem access. Use worktree/container isolation and narrow tools.
2. **Assuming extension flags are portable.** Flags below `Extension CLI Flags` in `pi --help` depend on installed packages. Check the current installation.
3. **Using `--no-builtin-tools` for a true no-tools run.** That can leave extension/custom tools enabled. Use `--no-tools` when zero callable tools are intended.
4. **Expecting `--resume` to be non-interactive by itself.** It selects a session interactively. Prefer `--session` or `--continue` for headless continuation.
5. **Expecting Pi to enforce a turn budget.** No core `--max-turns` exists in v0.84.1; use host bounds and narrow milestones.
6. **Trusting exit zero or final prose.** Verify files, diff, and tests independently.
7. **Running overlapping writers.** Assign one worktree per writer and keep one integration owner.
8. **Leaking credentials through diagnostics.** Never print settings or environment values indiscriminately; record only provider/model names and credential presence where needed.
9. **Assuming core MCP, sub-agents, or plan mode.** Those are extension-defined when present.
10. **Mutating Pi packages during a coding task.** Package install/update is a separate authorized operation.
11. **Assuming MCP names are the raw upstream names.** Direct MCP tools are adapter-generated Pi tool names such as `mcp_router_brave_web_search`, not bare upstream names like `brave_web_search`.
12. **Assuming proxy and direct MCP are filtered the same way.** Direct tools follow Pi tool filtering; proxy-mode access is governed by whether `mcp` is active plus adapter config.
13. **Exposing too many direct MCP tools.** `directTools: true` registered 77 tools and prevented bounded print-mode exit even after valid output. Prefer proxy mode (`directTools: false`) or a curated 5–20-tool subset. For no-tool reviews, also use `--no-extensions`.
14. **Treating project trust as a sandbox.** Trust only gates whether Pi loads project-local resources; it does not sandbox code, prompts, shell commands, or extensions.
15. **Keeping inline secrets in world-readable config files.** Pi config files often support environment indirection; use it and keep permissions tight.

## Verification Checklist

- [ ] `pi --version`, `pi --help`, and `pi list` checked on the target host.
- [ ] Target repository instructions and Git status inspected before writes.
- [ ] A dedicated worktree owns the write task.
- [ ] Print mode used without PTY for bounded automation.
- [ ] Provider/model overrides are explicit and justified.
- [ ] Tool allowlist matches the task's minimum required authority.
- [ ] When direct MCP tools are needed, their generated Pi names were verified (for example via `pi list`, `mcp({ search: ... })`, or cache/config inspection).
- [ ] Proxy vs direct MCP mode was chosen intentionally, and adapter config is appropriate for the task.
- [ ] Project-local resources are trusted only after inspection.
- [ ] Host timeout matches task complexity.
- [ ] Changed files and diff inspected outside Pi.
- [ ] Focused and repository-required tests run independently.
- [ ] Extension-dependent claims verified against current help/list output.
- [ ] No credentials, unrelated mutations, commits, or pushes were introduced.

## Official Sources

- [Pi Coding Agent](https://pi.dev/)
- [Pi documentation](https://pi.dev/docs/latest)
- [Pi source and coding-agent README](https://github.com/earendil-works/pi/tree/main/packages/coding-agent)
- [Programmatic usage](https://github.com/earendil-works/pi/tree/main/packages/coding-agent#programmatic-usage)
- [Extensions](https://github.com/earendil-works/pi/tree/main/packages/coding-agent#extensions)
- [Skills](https://github.com/earendil-works/pi/tree/main/packages/coding-agent#skills)
