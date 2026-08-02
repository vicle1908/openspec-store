## 1. Evidence and Gap Audit

- [x] 1.1 Re-run targeted code audit for sprint context handoff across `tdt-core`, KBS/`jira-kanban-from-spreadsheet`, `jira-daily-reports`, and `jira-skill.dashboard`.
- [x] 1.2 Record a gap matrix in `openspec/changes/jira-sprint-ecosystem-gap-closure/VALIDATION.md` covering expected vs actual behavior for report, dashboard, board/sprint, and docs/skills.
- [x] 1.3 Confirm whether per-sprint dashboard handling currently builds a configured dashboard or only find-or-creates a link target.

## 2. Contract and Implementation Closure

- [x] 2.1 If missing, add an explicit resolved sprint context handoff or adapter so report/dashboard stages consume the same issue keys, filter id, board id, sprint id, dashboard id, and project key.
- [x] 2.2 Confirm sprint-sheet remains link-only; the configured build/validate path stays on `jira-daily-reports dashboard` / `jira-skill.dashboard`.
- [x] 2.3 If the dashboard path is intended to be link-only, update output/logging/docs to label it link-only and show the canonical `jira-skill dashboard` command.
- [x] 2.4 Add or update unit tests for context handoff, optional link omission, dashboard build-vs-link mode, and dry-run no-write behavior.

## 3. Docs and Skills Alignment

- [x] 3.1 Update `.agents/skills/jira-daily-reports/SKILL.md` to describe active sprint report ownership, spreadsheet-derived context, and dashboard handoff semantics.
- [x] 3.2 Update `.agents/skills/kanban-board-from-spreadsheet/SKILL.md` or equivalent KBS guidance to describe board/sprint creation from the resolved filter and live gating.
- [x] 3.3 Update `.agents/skills/jira-dashboard/SKILL.md` to state that `jira-skill.dashboard` is the canonical dashboard builder/validator for sprint dashboards.
- [x] 3.4 Update relevant README/docs to remove stale manual per-sprint Jira id wording and point to the resolved context model.

## 4. Verification

- [x] 4.1 Run `openspec validate jira-sprint-ecosystem-gap-closure --type change --strict`.
- [x] 4.2 Run targeted pytest suites for affected repos (`tdt-core`, KBS/`jira-kanban-from-spreadsheet`, `jira-daily-reports`, `jira-skill`) based on actual changed files.
- [x] 4.3 Run a dry-run sprint pipeline against the active sprint spreadsheet and capture planned filter, board/sprint, dashboard, and report actions.
- [x] 4.4 Run live readback validation where safe; clean up any temporary Jira objects and record evidence in `VALIDATION.md`.
