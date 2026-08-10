# Design: Prime Agent Coding CLI Skill

## Skill structure

The skill follows the established coding-cli pattern (Pi, Codex, Goose, Grok):

```yaml
---
name: prime-agent
description: "Delegate coding to Prime Agent CLI (prime-agent)."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos]
metadata:
  hermes:
    tags: [Coding-Agent, Prime-Agent, Code-Review, Refactoring, Automation]
    related_skills: [claude-code, codex, pi, opencode]
---
```

## Verified flags (from `prime-agent --help`)

| Category | Flag | Description |
|---|---|---|
| Run | `-p, --print` | Print mode — one-shot, exit after response |
| Run | `--mode <text\|json\|rpc\|acp\|daemon>` | Output format |
| Run | `--cwd <dir>` | Set working directory |
| Model | `--provider <name>` | Select provider |
| Model | `--model <id>` | Select model |
| Model | `--thinking <level>` | off, minimal, low, medium, high, xhigh, max |
| Session | `-c, --continue` | Continue previous session |
| Session | `-r, --resume <path\|id>` | Resume saved session |
| Session | `--no-session` | Don't save session |
| Session | `--goal <objective>` | Seed persistent goal |
| Tools | `-t, --tools <list>` | Allowlist tools |
| Tools | `-nt, --no-tools` | Disable all tools |
| Tools | `-nbt, --no-builtin-tools` | Disable built-in tools |
| Tools | `-e, --extension <source>` | Load extension (repeatable) |
| Tools | `-ne, --no-extensions` | Disable extension discovery |
| Tools | `--skill <path>` | Load skill (repeatable) |
| Tools | `-ns, --no-skills` | Disable skill discovery |
| Tools | `-nc, --no-context-files` | Disable AGENTS.md/CLAUDE.md discovery |
| Autonomous | `--autonomous` | Continue until gates pass |
| Autonomous | `--autonomous-max-turns <n>` | Assistant-turn limit (default 12) |
| Autonomous | `--autonomous-timeout-ms <n>` | Wall-clock limit (default 1800000) |

## Provider catalog (verified)

| Provider | Protocol | Models |
|---|---|---|
| shopapikey | openai-responses | fable-5 |
| giaoduc | anthropic-messages | Advance |
| cockpit | openai-responses | gpt-5.6-sol, gpt-5.6-luna, gpt-5.6-terra |

## Sections

1. **Verified local setup** — v0.7.1, `/opt/homebrew/bin/prime-agent`, 3 providers/5 models
2. **Readiness** — `command -v`, `--version`, `model list`, `doctor`
3. **Preferred orchestration** — `prime-agent -p --provider <name> --model <id> --no-session -nt -ns -ne`
4. **Provider selection** — table of providers/models
5. **Tool scoping** — `-nt` for review, `-t read,write,edit,bash` for coding
6. **Sessions** — `-c` continue, `-r` resume, `--no-session` disposable
7. **Autonomous mode** — `--autonomous` with gate/turn/token limits
8. **ACP mode** — `--mode acp` for IDE integration
9. **JSON output** — `--mode json` for automation
10. **Complexity-adaptive limits** — timeout guidelines
11. **Verification checklist** — post-run validation
12. **Official sources** — docs links

## Key differences from other skills

- No `--sandbox` or `--dangerously-skip-permissions` (Prime Agent has no sandbox model)
- No `--max-turns` as top-level flag (use `--autonomous-max-turns` in autonomous mode)
- Provider selection via `--provider`/`--model` flags (not config profiles)
- Built-in tools always available without permission prompts
- ACP mode via `--mode acp` (not a separate command)
- `-nt`/`-ns`/`-ne` short flags for disabling tools/skills/extensions
