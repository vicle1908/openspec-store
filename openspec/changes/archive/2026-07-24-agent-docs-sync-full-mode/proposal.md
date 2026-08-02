## Why

The current agent-docs-sync only handles partial doc updates. Users need a "full mode" that:

1. **Reads all source code** — Python files, configuration, deployment configs
2. **Reads skills** — `.agents/skills/` directory
3. **Reads deployment configs** — Dockerfile, docker-compose.yaml
4. **Reads project metadata** — pyproject.toml, README.md
5. **Generates comprehensive docs** — Updates ALL documentation, not just changed files

The current agent can't handle this because:
- It only reads changed files (from git diff)
- It doesn't read deployment configs or skills
- It doesn't have context compaction for large codebases

## What Changes

- **Add `--full` flag** to CLI commands for full mode
- **Add new tools** for reading pyproject, skills, deployment configs
- **Integrate harness context compaction** for large codebases
- **Generate comprehensive docs** from all sources
- **Update existing docs** and create new ones where needed

## Architecture Decision

```
┌─────────────────────────────────────────────────────────────┐
│  FULL MODE STRATEGY                                          │
└─────────────────────────────────────────────────────────────┘

  Use harness context compaction from agent-core:
  ├─ SummarizingCompaction (manages context size)
  ├─ ClampOversizedMessages (truncates large files)
  └─ DeduplicateFileReads (avoids redundant reads)

  This allows reading many files without exceeding context limits.
```

## Capabilities

### New Capabilities

- `agent-docs-sync-full`: Full mode documentation synchronization

### Modified Capabilities

- `agent-docs-sync`: Add --full flag and new tools

## Impact

- **Code changes:** `cli.py`, `tools/`, `agents/generation.py`
- **New tools:** ReadPyprojectTool, ReadSkillTool, ReadDeploymentTool
- **Dependencies:** pydantic-ai-harness (already in agent-core)
