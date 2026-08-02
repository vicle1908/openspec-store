# Kanban Board OpenSpec Deep Alignment Cleanup

**Date:** 2026-05-16  
**Scope:** OpenSpec, skill docs, scripts docs, and stale reference cleanup for `kanban-board-from-spreadsheet` + deferred automation enhancement.

## Actions performed

1. Rewrote `openspec/changes/kanban-board-automation-enhancement/spec.md` as a clear deferred requirements delta.
2. Rewrote `openspec/changes/kanban-board-automation-enhancement/INDEX.md` to point to canonical production files.
3. Added canonical archive notices to:
   - `openspec/changes/archive/kanban-board-from-spreadsheet/spec.md`
   - `openspec/changes/archive/kanban-board-from-spreadsheet/README.md`
   - `openspec/changes/archive/kanban-board-from-spreadsheet/INDEX.md`
4. Normalized stale path references from `tools/agents/skills/...` to `.agents/skills/...` where relevant.
5. Normalized stale active OpenSpec references from `openspec/changes/archive/kanban-board-from-spreadsheet` to `openspec/changes/archive/kanban-board-from-spreadsheet`.
6. Added an explicit automation-rule/board-configuration boundary to `.agents/skills/kanban-board-from-spreadsheet/SKILL.md`.
7. Added generated-artifact hygiene guidance to `.agents/skills/kanban-board-from-spreadsheet/scripts/README.md`.

## Canonical state after cleanup

| Concern | Canonical location | State |
|---|---|---|
| Production skill | `.agents/skills/kanban-board-from-spreadsheet/` | Active |
| Completed OpenSpec | `openspec/changes/archive/kanban-board-from-spreadsheet/` | Archived canonical |
| JQL patterns | `.agents/skills/jira-jql-builder/` | Active dependency |
| Reporting | `.agents/skills/jira-daily-reports/` and `run_reports.sh` | Active dependency |
| Automation rules | `openspec/changes/kanban-board-automation-enhancement/` | Deferred decision record |

## Production boundary

The workflow updates a Jira filter from spreadsheet-derived issue-key JQL and verifies board visibility. It does not create automation rules or mutate board configuration.

## Verification commands

```bash
grep -RIn ".agents/skills/kanban-board-from-spreadsheet" openspec .agents docs 2>/dev/null
grep -RIn "openspec/changes/archive/kanban-board-from-spreadsheet" openspec .agents docs 2>/dev/null
find .agents/skills/kanban-board-from-spreadsheet -name "*.bak" -o -name "*.broken" -o -name "*.tmp"
```

Residual matches, if any, should be historical report prose only and not active instructions.
