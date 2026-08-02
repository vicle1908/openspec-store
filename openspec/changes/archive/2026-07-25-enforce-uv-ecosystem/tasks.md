## 1. Agent-Docs-Sync (missing uv.lock)

- [x] 1.1 Run `uv sync` in agent-docs-sync to generate uv.lock (validates pyproject.toml deps)
- [x] 1.2 Add .python-version with `3.14.5` (matches requires-python >=3.14,<3.15)
- [x] 1.3 Verify uv.lock is committed and .python-version exists

## 2. Add .python-version to Missing Repos

- [x] 2.1 Create .python-version in code-daily-scan with `3.14.5` (matches requires-python >=3.14,<3.15)
- [x] 2.2 Create .python-version in tdt-observability with `3.12` (matches requires-python >=3.12)
- [x] 2.3 Create .python-version in tdt-sheets with `3.14.5` (matches requires-python >=3.14,<3.15)
- [x] 2.4 Verify all .python-version files match their pyproject.toml requires-python

## 3. Update AGENTS.md with uv Practices

- [x] 3.1 Update ai-review/AGENTS.md with uv practices section
- [x] 3.2 Update agent-docs-sync/AGENTS.md with uv practices section
- [x] 3.3 Update jira-epic-report/AGENTS.md with uv practices section
- [x] 3.4 Update tdt-meta/AGENTS.md with uv practices section
- [x] 3.5 Update webhook-receiver/AGENTS.md with uv practices section
- [x] 3.6 Verify all Python repos have uv practices documented

## 4. Fix pip References in Docs

- [x] 4.1 Fix agent-docs-sync/docs/cli.md: replace pip install with uv add
- [x] 4.2 Fix agent-core/docs/research/pydanticai-langgraph.md: note these are external references (keep as-is)
- [x] 4.3 Fix tdt-meta/docs/scheduler/MIGRATION.md: replace pip install with uv add
- [x] 4.4 Fix tdt-meta/docs/skills/jira-comprehensive-management.md: replace pip install with uv add
- [x] 4.5 Fix tdt-meta/docs/superpowers/plans/2026-05-08-vds-tdt-migration-plan.md: replace pip install
- [x] 4.6 Fix tdt-meta/docs/reports/rag-chunking-frameworks-guide.md: replace pip install
- [x] 4.7 Fix tdt-meta/docs/superpowers/specs/2026-05-08-vds-tdt-migration-design.md: replace pip install
- [x] 4.8 Verify no active docs reference pip install

## 5. Standardize [tool.uv] Config

- [x] 5.1 Add [tool.uv] section to repos missing it (agent-docs-sync, webhook-receiver, tdt-core, tdt-observability)
- [x] 5.2 Verify all repos have consistent uv config per official best practices:
  - `default-groups = ["dev"]` — dev deps installed by default
  - `required-version = ">=0.11.15"` — minimum uv version
  - `python-preference = "only-managed"` — uv uses its own Python installs
  - `package = true` — editable install for development

## 6. Workspace Root Enforcement

- [x] 6.1 Update tdt-meta/AGENTS.md with uv enforcement rules
- [x] 6.2 Document uv as mandatory package manager in workspace conventions
- [x] 6.3 Add uv version pinning requirement (>=0.11.15)
- [x] 6.4 Document CI usage: `uv sync --frozen` for reproducible builds
