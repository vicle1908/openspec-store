# Verification Evidence

Date: 2026-08-03

## Environment

- Kimi Code CLI: `0.31.1`
- Binary: `/opt/homebrew/bin/kimi`
- Skill: `/Users/androidteam/.hermes/skills/autonomous-ai-agents/kimi-code/SKILL.md`
- Skill version: `1.0.1`
- Skill file size: `7344` bytes

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

No authentication mutation was attempted. Version/help/config validity proves installation and local configuration validity, not account authorization.

## Real skill-backed execution

Command executed from a disposable empty directory:

```bash
kimi --skills-dir /Users/androidteam/.hermes/skills/autonomous-ai-agents/kimi-code \\
  -p 'Perform a read-only verification of this workspace. Report exactly: (1) current working directory, (2) whether the directory is a Git repository, (3) the first five entries in the directory, and (4) confirm that you did not modify any files. Do not write files, run destructive commands, or access credentials.' \\
  --output-format stream-json
```

Observed:

- Exit code: `0`.
- Kimi emitted structured assistant/tool JSONL events, including `Bash` calls for `pwd`, Git repository detection, and directory listing.
- Reported working directory: `/private/tmp/kimi-code-skill-verification`.
- Reported Git repository: `No`.
- Reported directory contents: empty.
- Reported file modification status: `No files were modified.`
- Session ID: `session_73b942af-8133-4258-9e29-b77fa6762273`.

A second smoke run after the documentation correction used the same skill path and exited `0`, reported `/private/tmp/kimi-code-skill-verification`, and confirmed no files or credentials were accessed. Its session ID was `session_668b05e4-c888-43ed-b22d-8055ea7e838f`.

The installed CLI emitted the absolute working directory as a plain first line before the JSONL events in both runs. The skill now explicitly requires tolerant parsing of that preamble.

This is real model/tool execution through the new skill's prescribed `--skills-dir`, `-p`, and `--output-format stream-json` path. No files were written by either Kimi task.

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
