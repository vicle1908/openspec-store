# Verification Evidence

Date: 2026-08-03

## Environment

- Antigravity CLI: `1.1.10`
- Claude Code: `2.1.212`
- Codex CLI: `0.146.0`
- Hermes skill surfaces:
  - `~/.hermes/skills/autonomous-ai-agents/antigravity/SKILL.md` v1.1.0
  - `~/.hermes/skills/autonomous-ai-agents/claude-code/SKILL.md` v3.0.0
  - `~/.hermes/skills/autonomous-ai-agents/codex/SKILL.md` v2.0.0

## Antigravity

Command:

```bash
agy --version
agy models
agy --model gemini-3.6-flash-low --effort low \
  --print-timeout 30s --output-format json \
  --print 'Reply with exactly AGY_VERIFY_OK'
```

Observed:

- Version: `1.1.10`
- `agy models` returned documented slug identifiers, including `gemini-3.6-flash-low`, `claude-sonnet-4-6`, and `gpt-oss-120b-medium`.
- Process exited `0`.
- JSON status: `SUCCESS`.
- Response: `AGY_VERIFY_OK`.
- Conversation ID: `b0e677ab-f2a1-4a64-9ccd-95ad9c6571fa`.

Earlier bounded probes in the same audit also established:

- Shell CWD is inherited and visible in stream JSON `init.cwd`.
- `--new-project` creates logical project state; it is not a filesystem `cd`.
- Absolute-path writes under an added workspace root can be read back successfully.
- Local v1.1.10 rejects `--cwd` and has no `doctor` subcommand.

## Codex

Command:

```bash
codex --version
codex login status
codex exec --skip-git-repo-check --sandbox read-only --ephemeral --json \
  'Reply with exactly CODEX_VERIFY_OK and do not use tools.'
```

Observed:

- Version: `codex-cli 0.146.0`.
- Authentication status command succeeded using configured API-key authentication; the credential value was not recorded.
- Process exited `0` without PTY.
- JSONL emitted `thread.started`, `turn.started`, `item.completed`, and `turn.completed`.
- Agent response: `CODEX_VERIFY_OK`.
- Thread ID: `019fc7d9-e326-7851-99c8-745f34f92738`.
- A non-fatal warning reported skill descriptions shortened to fit the 2% skills context budget.

Earlier bounded probes in the same audit also established:

- `workspace-write` can create and read back a file without PTY.
- `--skip-git-repo-check` permits non-Git execution.
- `codex exec` approval policy and sandbox are separate; unattended editing uses `-c 'approval_policy="never"' --sandbox workspace-write`.
- JSONL, output schema, final-message file, resume, review, plugins, hooks, MCP, and multi-agent surfaces are present in local help/features.

## Claude Code

Commands:

```bash
claude --version
claude doctor
claude auth status
claude agents --json
```

Observed:

- Version: `2.1.212`.
- `claude doctor`: `No installation issues found`.
- Search: bundled and healthy.
- Authentication: `loggedIn: false`, `authMethod: none`.
- Model execution was intentionally not attempted while unauthenticated.
- `claude agents --json` succeeded without TTY and returned one idle background session.

Official documentation and local help jointly verified print/stream JSON, permission modes, tool restrictions, native background agents, sessions, worktrees, hooks, MCP, subagents, and agent-team behavior.

## Skill consistency scan

The updated skill tree was scanned for stale positive guidance including:

```text
Print mode skips ALL
CWD Not Inherited
requires the exact display name
.fable-5
Always use `pty=true`
Git repo required
All 8 Hook Types
claude upgrade
```

No stale positive claims remained. The only match for `CLAUDE_TOOL_INPUT` / `CLAUDE_FILE_PATHS` is an explicit warning not to rely on those invented variables.

## OpenSpec validation

The installed CLI syntax is positional:

```bash
openspec validate --strict validate-coding-agent-cli-skills
openspec validate --strict --all
```

`openspec validate --strict --change ...` is not supported by this installed OpenSpec version; `openspec validate --help` documents `[item-name]`, `--changes`, `--specs`, and `--all`.

## Known limitations

- Antigravity public docs currently contain version skew relative to local v1.1.10 and include at least one unsupported `--cwd` example.
- Claude Code is installed but unauthenticated in this environment; runtime model execution remains unverified until authentication is restored.
- Codex reports that some skill descriptions are shortened due to its 2% skill-context budget; this did not prevent execution.
- Model availability, UI dialog layouts, and experimental agent-team behavior may change independently of these skill versions.
