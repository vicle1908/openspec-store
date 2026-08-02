## Why

The completed `jira-sprint-spreadsheet-ssot`, `kbs-extra-sheets-and-linked-tickets`, and `jira-dashboard-automation` changes established the major pieces of the sprint ecosystem, but follow-up review found the contracts are still split across completed changes and do not explicitly require one observable handoff from spreadsheet scope to filter, board/sprint, dashboard, and report links. This makes it easy for future work to regress into partial dashboard creation, stale Jira id fallbacks, or inconsistent docs/skills even though the underlying capabilities now exist.

## What Changes

- Add a follow-up alignment contract that requires a single sprint context object to be produced and consumed across the KBS pipeline, sprint report refresh, and dashboard link/build paths.
- Require live validation evidence that the active sprint spreadsheet resolves to the same issue scope, filter, board/sprint, dashboard link, and report rows.
- Require the per-sprint dashboard path to either build/validate a configured dashboard through the shared `jira-skill.dashboard` layout engine or explicitly document that only a link is created and route dashboard build requests to `jira-skill dashboard`.
- Require active docs and skills to reflect the current ownership split: `tdt-core` for Jira primitives/resolver, KBS for orchestration, `jira-daily-reports` for sprint report/person capacity output, and `jira-skill.dashboard` for dashboard lifecycle.
- No breaking CLI behavior is intended; this change tightens contracts and closes documentation/validation gaps.

## Capabilities

### New Capabilities
- `sprint-ecosystem-alignment`: End-to-end sprint ecosystem contract covering shared sprint context handoff, dashboard build/link semantics, validation evidence, and docs/skill alignment.

### Modified Capabilities

## Impact

- `tdt-meta`: new OpenSpec follow-up artifacts and likely docs/skill updates under `.agents/skills` and `docs`.
- `tdt-core`: verification only unless the shared sprint resolver lacks fields needed for the sprint context contract.
- `jira-kanban-from-spreadsheet` / KBS pipeline: may need small handoff or logging updates so resolved context is explicit and testable.
- `jira-daily-reports`: may need small changes to consume/render the resolved context consistently and clarify per-sprint dashboard behavior.
- `jira-skill`: dashboard lifecycle should remain canonical; may need docs/tests proving sprint dashboard layouts use the shared engine.
- External systems: Jira Cloud and Google Sheets live validation only; no new third-party dependency.
