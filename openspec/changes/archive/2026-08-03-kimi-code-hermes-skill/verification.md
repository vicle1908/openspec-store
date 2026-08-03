# Verification Evidence

Date: 2026-08-03

## Environment

- Kimi Code CLI: `0.31.1`
- Binary: `/opt/homebrew/bin/kimi`
- Skill: `/Users/androidteam/.hermes/skills/autonomous-ai-agents/kimi-code/SKILL.md`
- Skill version: `1.0.0`
- Skill file size: `7183` bytes

## Kimi CLI checks

Commands:

```bash
command -v kimi
kimi --version
kimi --help
kimi acp --help
kimi doctor config
```

Observed:

- `command -v kimi` returned `/opt/homebrew/bin/kimi`.
- `kimi --version` returned `0.31.1`.
- Top-level help exposed `-p/--prompt`, `--output-format text|stream-json`, `--plan`, `--yolo`, `--auto`, `--continue`, `--session`, `--skills-dir`, `--agent`, `--agent-file`, `--add-dir`, `acp`, `provider`, `login`, and `doctor`.
- `kimi acp --help` confirmed ACP server mode over stdio.
- `kimi doctor config` returned `OK config.toml /Users/androidteam/.kimi-code/config.toml` and `All checked config files are valid.`

No model execution or authentication mutation was attempted. Version/help/config validity proves installation and local configuration validity, not account authorization.

## Skill checks

- `skill_view(name="kimi-code")` successfully reloaded the skill.
- Frontmatter contains `name`, `description`, `version`, `author`, `license`, `platforms`, and Hermes metadata.
- The skill documents the verified Kimi command surface and explicitly avoids unsupported cross-CLI flags.
- Official sources are linked to `MoonshotAI/kimi-code`, `MoonshotAI/kimi-cli`, Kimi Code command reference, ACP/IDE docs, and Kimi Code.
- No credential values are present in the skill.

## OpenSpec checks

```bash
openspec validate --all
```

Observed before this change: `351 passed, 0 failed (351 items)`.

The change is tooling-only and uses `.openspec.yaml` with `skip_specs: true`; no delta specs are required.

## Known limitations

- Native MCP tool calls through the current Hermes session were not available in the exposed tool registry, so this change does not claim an MCP Router end-to-end call.
- Kimi model execution was not tested because the request was to create and verify the reusable skill, not to start a billable coding task.
