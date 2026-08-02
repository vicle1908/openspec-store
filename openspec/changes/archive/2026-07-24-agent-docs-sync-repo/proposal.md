## Why

Documentation drifts from code over time. Currently, docs must be manually updated when code changes — a process that's error-prone and often forgotten. An automated agent that syncs docs and specs on commits would:

1. **Prevent drift** — Catch doc inaccuracies before they accumulate
2. **Save time** — Auto-generate doc sections from code
3. **Enforce quality** — Validate links, examples, and spec coverage
4. **Scale across repos** — Work for agent-core, ai-review, jira-skill, etc.

## What Changes

- **New repository**: `agent-docs-sync` — dedicated doc sync tool
- **Uses agent-core features**: BaseAgent, ToolRegistry, HookRegistry, Flavor, WorkflowBuilder, SchedulerEngine
- **CLI commands**: `docs-sync check`, `docs-sync update`, `docs-sync validate`, `docs-sync sync`
- **Multi-repo support**: Sync docs for any TDT repository
- **Durable execution**: Optional DBOS-backed crash recovery via SchedulerEngine

## Capabilities

### New Capabilities

- `agent-docs-sync`: Automated documentation synchronization agent
- `doc-detection`: Git diff analysis and change detection
- `doc-generation`: Auto-generate doc sections from code (docstrings, type hints)
- `doc-validation`: Link checking, code example verification, openspec validate
- `durable-pipeline`: Crash-recoverable sync operations via SchedulerEngine

## Impact

- **New repository**: `agent-docs-sync/` in TDT workspace
- **Dependencies**: agent-core, typer, GitPython, markdown-it-py, httpx, ruamel.yaml
- **Breaking changes**: None — new standalone tool

## Dependencies (Verified on Python 3.14)

| Dependency | Version | Python 3.14 | Purpose |
|------------|---------|-------------|---------|
| agent-core | >=0.1.0 | ✅ | Agent framework |
| typer | >=0.27.0 | ✅ | CLI (vendored Click) |
| GitPython | >=3.1.55 | ✅ | Git operations (security-hardened) |
| markdown-it-py | >=4.2.0 | ✅ | Markdown parsing |
| httpx | >=0.28.1 | ✅ | Async HTTP for link validation |
| ruamel.yaml | >=0.19.1 | ✅ | YAML config (round-trip preservation) |
