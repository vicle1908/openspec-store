---
name: coding-agent-capability-verification
description: "Verify headless coding agents with real tool-use probes."
version: 0.4.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Coding-Agent, Verification, Headless, Permissions, Automation]
    related_skills: [claude-code, codex, antigravity, opencode, pi, kimi-code, goose]
---

# Coding-Agent Capability Verification

Use this skill when checking whether one or more coding-agent CLIs can actually perform authorized coding work. A model response, version string, or zero exit code proves connectivity only; it does not prove that file tools, shell tools, MCP, permissions, or the requested workspace are functional.

## When to Use

- A user asks to verify, recheck, or benchmark coding agents.
- A previous headless run returned empty output, a permission denial, a timeout, or a trust error.
- Agent configuration or provider credentials changed.
- You need evidence that an agent can read, write, and verify files before delegating a real task.

Do not use this skill as a substitute for repository-specific tests, code review, or implementation verification.

## Prerequisites

- The target CLI is installed and its version is known.
- The user has authorized the requested level of access.
- Use a disposable directory for capability probes.
- For coding tasks, use one Git worktree per concurrent writer and inspect the target repository's `AGENTS.md` before mutation.
- **Do not modify framework source files** (e.g. `~/.hermes/hermes-agent/`). Only edit user-owned files: AGENTS.md, skills/, config.yaml, memory. Framework changes are overwritten on updates.

## Access Model

Full access has two independent dimensions:

1. Permission approval: whether the agent is allowed to invoke a tool.
2. Execution sandbox: whether the agent can reach the intended filesystem, network, and workspace.

Set both deliberately. A permission bypass with a restricted sandbox can still fail to write. A full sandbox with approval prompts can still stall headless execution.

For authorized unrestricted work, use the agent-specific full-access invocation documented in `references/headless-probes.md`. Never infer that one CLI's flags apply to another.

## Procedure

1. Record the CLI version and help output relevant to print mode, permissions, sandboxing, tools, output format, and timeout.
   Treat the installed runtime output as authoritative; do not rely on a hard-coded patch version from this skill.
   Completion criterion: the exact installed version and accepted flags are captured without exposing credentials.

2. Inspect the effective configuration without printing secrets.
   Start from the exact user-supplied path. If it is absent, report that once and use targeted filename discovery; do not substitute a provider/model name for a directory or retry the same missing path indefinitely. Report only config presence, provider/model identity, permission/sandbox/tool policy, and credential presence booleans. If a config has a model but no explicit provider field, report the provider as unspecified rather than inferring it.
   Completion criterion: provider/model identity, permission mode, sandbox mode, tool policy, and config/auth presence are known without credential leakage.

3. Audit config against official docs.
   Compare the installed version against the latest available (`npm view <package> version` for npm-installed agents, `brew info <cask>` for Homebrew). Check credential file permissions (`ls -la` on auth/settings files containing tokens — they should be mode `0600`, not `0644`). Compare current config fields against the latest official documentation to identify missing recommended settings (e.g. `auto-mode-config.json` for Claude Code, `external_directory` rules for OpenCode, `doom_loop` protection).
   Completion criterion: version gap identified, credential permissions verified, config alignment with official docs assessed.

4. Run a connectivity probe with no model or provider override unless comparison is the purpose.
   Completion criterion: the process exits successfully and returns a bounded response.

5. Run a disposable write/read probe.
   Ask the agent to create exactly one marker file with a unique sentinel, then verify the file content externally with the host tool.
   Completion criterion: the marker exists at the requested path and contains the exact sentinel.

6. For a complex-task check, ask the agent to inspect a real repository read-only or modify an isolated worktree.
   Completion criterion: the report cites real paths, commands, and findings; for writes, the external diff and tests corroborate the report.

7. Classify failures precisely.
   - Connection/auth failure: no usable model response.
   - Permission failure: headless mode denied a needed tool.
   - Sandbox/workspace failure: tool ran but could not reach the target path.
   - Budget/timeout failure: progress started but the host or agent bound ended first.
   - Agent-quality failure: response completed but ignored the task or cited unverifiable artifacts.

8. Remove disposable probe files after evidence is collected.
   Completion criterion: no temporary marker artifacts remain.

## Skill Discovery Architecture

Each CLI agent discovers skills differently. Understanding this is critical for multi-agent workspaces.

### Native loading paths

| Agent | Reads skills from | How |
|-------|------------------|-----|
| **Claude Code** | `.claude/skills/*/SKILL.md` | Native — walks up from CWD |
| **Claude Code** | `.claude/commands/**/*.md` | Native — slash commands |
| **Codex** | `.fable-5/*/SKILL.md` | Native — walks up from CWD |
| **agy, OpenCode, Pi, Goose** | `.agents/skills/` | Via AGENTS.md parent traversal |

### Workspace layout (canonical)

```
.agents/skills/     ← ALL agents read here (84 dirs)
.claude/skills/     ← Claude Code native loading (openspec only)
.claude/commands/   ← Claude Code slash commands (/opsx:*)
.codex/skills/      ← Codex native loading (openspec + agent-specific)
```

### Pitfalls
- Claude Code `-p` mode doesn't auto-list skills but CAN access them via parent traversal
- Codex `codex exec` is non-interactive mode (not `codex "prompt"` which requires TTY)
- OpenCode default-model verification uses `opencode run "prompt"`; do not add a model/provider override unless comparison is the task.
- Goose first-run cold start ~55s; exit 0 does NOT guarantee success
- Pi runs last. The local MCP adapter now uses proxy mode (`directTools: false`); for bounded no-tool reviews use `--no-session --no-tools --no-extensions` so optional extensions cannot retain the process.

## CLI Selection Rules

- Claude Code: use `claude -p` with `--permission-mode bypassPermissions`, explicit `--tools`, generous `--max-turns`, and `--max-budget-usd` for complex tasks.
- Codex: use `codex exec` with `approval_policy="never"`, the user-authorized sandbox mode, `--output-last-message`, and `--skip-git-repo-check` only for umbrella directories that are not Git repositories.
- Antigravity (`agy`): place the prompt directly after `-p`; include `--dangerously-skip-permissions` for headless reads, writes, Bash, or MCP; use `--print-timeout` plus the host timeout.
- OpenCode: use `opencode run`, not `opencode exec`; verify the selected agent profile's permission block because named profiles may override global permissions. **Workaround for external directory restrictions:** OpenCode auto-rejects reads from `~/.hermes/skills/` (outside working directory). Copy review files into `~/Developer/` first, then pass local paths in the prompt. Clean up temp files after the review.
- Pi: use `pi -p --no-session --no-tools --no-extensions` for bounded no-tool reviews. For authorized coding use `--approve --tools read,write,edit,bash` and keep proxy-mode MCP unless a curated direct set is required.
- Kimi Code: use `kimi -p` (the executable is `kimi`; `kimi-code` is the skill name, while model IDs such as `fable-5` are not executable names) and rely on configured `default_permission_mode = "auto"`; current prompt mode rejects adding `--auto` or `--yolo`.
- Goose: use `goose run -t "..." --no-session -q --max-turns N`; no permission bypass flag exists. Use `--provider` and `--model` for provider overrides and `--output-format json` for evidence. Success requires exit code, structured status, exact expected response, nonzero usage when appropriate, absence of error text, and external artifact verification. `metadata.status` alone is insufficient. MCP Router v0.2.0 passed direct initialize/list (132 tools) and a real goose MCP call, but goose initialization is intermittent; use `--no-profile --with-builtin developer` when MCP is unnecessary. `--no-session` and `--name` are mutually exclusive. `goose doctor` is model-backed, not a quick health check.

## Evidence Rules

Treat agent self-reports as claims, not proof. Verify every claimed write externally. For repository tasks, inspect `git status`, `git diff --check`, changed files, and the repository's focused test command outside the agent. Keep model identity separate from provider/gateway backend identity when a proxy reports an internal model name.

A timeout is not a failure of the task and not evidence of completion. Inspect the worktree for valid partial work, then resume with a narrower prompt or increase the budget only when the transcript shows productive progress.

## Parallel Execution

Independent read-only probes can run in parallel. Concurrent writers must have separate worktrees or isolated directories. Keep one integration owner and never let two agents edit overlapping paths.

### Concurrency limits

- **Max 3 concurrent CLI agents** — dispatching 6+ parallel CLI processes (claude, agy, pi, opencode, goose) causes file descriptor exhaustion and hangs. Batch in groups of 3.
- **Pi is serial-heavy** — Pi's MCP adapter resolves 77+ tools which bloats context and causes timeouts. Run Pi last or in its own batch, not alongside other agents.
- **Recommended batch order:** `{Claude, agy, Goose}` → `{OpenCode, Codex, fable-5}` → `{Pi}` (serial, heavy MCP)
- **goose self-recovery** — goose detected a 300s tool timeout during delegation, retried the failed step automatically, and completed without intervention. This is a strength for unattended delegation.
- **goose MCP integration** — direct MCP transport and a real goose tool call pass, but some goose starts fail before initialization. Treat it as intermittent/degraded, pin the reviewed CLI version after approval, and preflight a real read-only MCP call before MCP-dependent work.

## Pitfalls

- A successful exact-output smoke test may still have no tools.
- A zero exit code may hide an empty result or a tool auto-denial.
- Headless agents can soft-deny file tools when permission flags are omitted.
- A CLI's default model may differ from a configured provider/model in a settings file; structured output or effective runtime diagnostics are stronger evidence.
- Keep product, Hermes skill, executable, provider, and model IDs distinct. For example, `fable-5` is the skill, `kimi` is the executable, and `fable-5` can be a model ID; never substitute one namespace for another.
- **Pi provider name mismatch:** Pi's `settings.json` (`defaultProvider`) and `models.json` (`providers`) must use the identical provider key. A stale key (e.g. `shoapikey` in `models.json` with `shopapikey` in `settings.json`) causes `Unknown provider` errors at runtime. Always verify both files agree after any config change: `pi --list-models` shows the effective registered providers.
- **Config default verification:** When verifying that an agent uses its configured defaults, omit `--provider` and `--model` overrides. Use structured output (Pi `--mode json`, agy `--output-format json`, OpenCode `--format json`) to extract the runtime model identity from metadata rather than trusting the agent's prose response.
- **Codex trust check at umbrella root:** Codex rejects execution inside non-Git directories (like `~/Developer`) with "Not inside a trusted directory". Use `--skip-git-repo-check` only for umbrella roots; use a real repo `workdir` for coding tasks.
- **Upgrading smoke tests to complex tasks:** A one-line OK probe proves connectivity but not capability. For architecture reviews or multi-file work, increase Claude to `--max-turns 40-90 --max-budget-usd 10`, agy to `--print-timeout 20m`, and Codex to generous timeouts. Host timeout and agent budget are independent controls.
- If a skill or reference lookup fails, inspect the catalog or source path once and stop; do not repeat the identical lookup in a loop. If agent references disagree about a default model or config path, report the conflict and use the installed CLI's effective diagnostics as the source of truth.
- A workspace umbrella may not be a Git repository even when all child directories are repositories.
- Reusing a probe directory can make a stale marker look like a successful write.
- Increasing timeout without increasing the agent's turn/token budget does not fix budget exhaustion.
- Goose startup and cost depend strongly on profile and model. Isolated provider probes took ~36–54s and 4.6K–7.8K tokens; full-profile docs/MCP runs were substantially more expensive. Use explicit host bounds and profile scope.
- **Goose exit code and `metadata.status` do NOT prove success.** Provider errors can return exit 0 plus `status: completed`. Require the exact expected response or artifact, nonzero usage where appropriate, no error text, and external verification.
- Goose MCP Router is healthy at the protocol boundary (v0.2.0, 132 tools) and worked in a real goose call, but initialization can fail intermittently. Preflight an actual read-only MCP call; use `--no-profile --with-builtin developer` when MCP is unnecessary.
- Goose JSON output returns a conversation envelope whose content order varies. Select assistant content items with `type == "text"`; do not assume `content[0]` is text. Always use `-q` for programmatic parsing.
- Goose `--no-session` and `--name` are mutually exclusive — passing both produces an error. Use `--name` without `--no-session` for named sessions, or `--no-session` without `--name` for disposable one-shots.
- Goose `goose doctor` is NOT a health check — it launches a full model-backed diagnostic session, consumes tokens, and can take minutes. Use `goose --version` + simple smoke test instead.
- Goose `goose serve` has `--dangerously-unauthenticated` flag — never use in production without authentication.
- Goose review exits 0 even with HIGH severity findings — inspect JSONL output, not just exit code.
- Goose skills count is context-dependent — varies by working directory due to `.agents/skills/` scanning.
- macOS does not ship `timeout` from coreutils. Install `coreutils` (`brew install coreutils`) and use `gtimeout` for process timeouts. Check with `command -v gtimeout || command -v timeout || echo NO_TIMEOUT_WRAPPER`.
- Do not modify framework source files (e.g. `~/.hermes/hermes-agent/tools/`). Only edit user-owned files: AGENTS.md, skills/, config.yaml. Framework changes are overwritten on updates and create maintenance burden.
- **AGENTS.md is the cross-agent propagation mechanism.** When rules need to reach all coding agents (Claude Code, Codex, agy, OpenCode, Pi, fable-5), add them to the workspace's `~/Developer/AGENTS.md`. Every agent auto-loads it on startup. This is how path-safety rules, project conventions, and workspace layout context reach delegated agents — not by modifying Hermes internals.
- Pi's `pi-mcp-adapter` can resolve 77+ direct MCP tools, which bloats the system prompt and causes timeouts. For bounded automation, use proxy mode (`--tools mcp`) or filter the MCP tool list in `mcp.json` to 5-20 tools.
- Credential file permissions matter. Settings files containing auth tokens (e.g. `~/.claude/settings.json`, `~/.codex/auth.json`) should be mode `0600`, not `0644`. Report permission issues as security findings.

## Verification

The skill succeeds when:

- the effective configuration is identified without credential leakage;
- credential file permissions are verified (mode `0600` for files containing tokens);
- version gap against latest official release is identified;
- connectivity succeeds;
- the disposable write/read probe succeeds externally;
- complex-task output cites real repository evidence;
- any failure is classified by cause rather than reported as a generic agent failure;
- temporary probe artifacts are removed.

See `references/headless-probes.md` for current command recipes, sentinel conventions, and evidence fields. See `references/goose-validated-features.md` for goose-specific config, providers, flags, and output schemas. See `references/multi-agent-review-patterns.md` for concurrency limits, batch ordering, and per-agent invocation patterns. See `references/read-only-config-inventory.md` for safe path discovery, non-secret field inventory, and credential-presence handling. See `references/official-docs-comparison.md` for per-agent config alignment with official documentation.
