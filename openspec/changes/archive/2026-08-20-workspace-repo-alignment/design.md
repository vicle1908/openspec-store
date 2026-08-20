# Design: Workspace Repo Alignment

## Changes

### 1. AGENTS.md Workspace Layout

Add to the Python repos section:

```
├── claude-code-provider-adapter/  ← Python: Anthropic→OpenAI adapter for Claude Code
├── hermes-webui/                  ← Python: Hermes web UI
```

Update Python repo count from 16 to 18.

### 2. GDrive Sync REPOS List

Add `claude-code-provider-adapter` and `hermes-webui` to the REPOS variable in the GDrive sync section.

### 3. Repo Table

Add rows for both repos in the Python repos table with file counts, Python version, and test counts.

## Verification

- Both repos have `pyproject.toml` (verified)
- Both are git repos with recent commits (verified)
- Both use `uv` for dependency management (verified)
- GDrive sync filters already apply (generic .git/, .venv/ exclusions)
