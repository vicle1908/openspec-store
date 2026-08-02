# Jira Kanban From Spreadsheet (Python) - Proposal

**Status:** Implemented (All Phases)  
**Date:** 2026-05-22  
**Author:** lekhanhvinh  
**Predecessor:** `openspec/changes/archive/kanban-board-from-spreadsheet/` (bash skill v1.3)

---

## Problem

The kanban-board-from-spreadsheet workflow exists as **bash scripts** at `.agents/skills/kanban-board-from-spreadsheet/scripts/` (~465 LOC across 4 scripts). It works in production but has structural pain:

- **External CLI dependencies**: requires `acli` v1.3.18+ AND `gws` (Google Workspace) CLI installed and authenticated. Onboarding new operators is fragile.
- **No type safety**: bash + jq + python3 inline scripts mixed. Spreadsheet rows are untyped dicts.
- **Hard to test**: bash workflows are tested manually. No unit tests, no mocks.
- **No reuse**: cannot import from `jira-skill.board` (2,498 LOC of board operations sitting unused).
- **Brittle JQL generation**: regex-based parsing of issue keys, prone to edge cases.
- **No versioned templates**: every sprint is bespoke; cannot define team-standard board configs.
- **Cron-unfriendly**: bash scripts assume interactive terminal (color codes, prompts).

The bash skill works for the current operator but does not scale to multiple teams or unattended automation.

---

## Proposed Solution

Create a new Python repo `jira-kanban-from-spreadsheet` that:

1. Reuses the ecosystem stack: `tdt-core[jira]` for auth, `jira-skill` for board operations
2. Replaces `gws` CLI with `gspread` (or google-api-python-client) for Google Sheets read
3. Replaces `acli` with python-gitlab/atlassian-python-api via `tdt-core` (Jira side already uses tdt-core)
4. Provides typer CLI: `kbs sync`, `kbs preview`, `kbs validate`, `kbs templates`
5. Pydantic models for spreadsheet rows + filter configs (type-safe parsing)
6. YAML team-standard templates (mobile, platform, data, etc.)
7. Pytest with mocks for Sheets and Jira (real API calls in opt-in integration tests)

The bash skill remains as historical reference. The new Python repo becomes the maintained path.

---

## Why Now

- Sprint 14: bash skill consumed ~30 minutes of manual operator time per cycle
- Onboarding two more operators requires `acli` + `gws` CLI setup on each machine
- Need to support ad-hoc cross-project boards beyond filter #15128 / board #1066
- Want to integrate with `jira-daily-reports` reminders (e.g., "this ticket is in board but missing estimation")
- Ecosystem now has `tdt-core` and `jira-skill` ready to be dependencies

---

## Scope

### In Scope (Phase 1 — MVP)

- Read Google Sheets sprint planning tab via gspread
- Parse issue keys from "ID" column with type validation
- Generate cross-project JQL spanning all unique projects
- Update existing Jira filter (filter ID configurable, default 15113)
- Verify board (board ID configurable) shows expected count
- typer CLI with `sync`, `preview`, `validate` commands
- Default reminder-policies-style YAML config
- Pytest with mocks (≥80% coverage)

### In Scope (Phase 2 — Templates)

- YAML team-standard templates (board name, columns, swimlanes, default labels)
- `kbs templates list/apply` commands
- Template-driven filter naming

### In Scope (Phase 3 — Reports + Cron)

- Integration with `jira-daily-reports` (post-sync triggers a fresh report)
- Cron schedule for nightly board verification
- Slack/email summary (when delivery infra exists)

### Out of Scope

- Creating new Jira filters or boards (reuse existing IDs — same as bash skill)
- Modifying issue fields beyond what's already populated (e.g., assignee, labels, estimates) — bash already does this
- Scrum boards (kanban only — same as bash skill)
- Reverse sync (Jira → spreadsheet)
- Replacing `acli` for issue field updates (Phase 4 if needed)

---

## Success Criteria

1. Operator runs `uv run kbs sync --spreadsheet <id>` and gets a working updated board in under 60s
2. Onboarding a new operator requires only `uv sync` + `~/.tdt/.env` (no extra CLI installs)
3. Bash skill matches Python output (same JQL, same filter contents) for Sprint 14 verification run
4. `pytest --cov` passes with ≥80% coverage
5. Type check via `mypy --strict src/` passes clean
6. Cron-friendly: zero color codes, structured logging, exit codes 0/1/2

---

## Alternatives Considered

| Alternative | Verdict |
|-------------|---------|
| Keep bash, add tests | Bash testing is bad. Coverage tooling weak. |
| Python in `jira-skill` directly | Out of scope for that library — it's domain library, not CLI |
| Python in `jira-daily-reports` | Wrong concern — reports vs sync workflows |
| New repo using tdt-core + jira-skill | ✅ Chosen — fits ecosystem pattern (jira-daily-reports, jira-epic-report) |
| Use `acli` from Python via subprocess | Defeats purpose — keep external CLI dep |

---

## Decision

**Build new Python repo** `jira-kanban-from-spreadsheet`. Bash skill stays as historical reference and operator fallback for one sprint, then deprecate.

Use the same toolchain pattern as `jira-daily-reports`:
- `tdt-core[jira]` + `jira-skill` (path deps)
- `typer` + `rich` for CLI
- `gspread` for Google Sheets
- `pydantic` for validation
- `pytest` + `ruff` + `mypy` strict

Implementation effort estimate: **2-3 days for Phase 1 MVP**.
