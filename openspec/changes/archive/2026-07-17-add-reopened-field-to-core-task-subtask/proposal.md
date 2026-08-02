# Add Reopened Field to Core Task/Subtask Issue Types Proposal

## Why

`customfield_11523` ("Reopened", float) is the canonical global `Reopened` field for the psplit.atlassian.net Jira instance. The TDT workspace requires this field to be present on `Task` and `Subtask` issue types across the 14 canonical core projects to support changelog-driven reopen counting, reporting, and automation. Additionally, three project-scoped duplicate `Reopened` fields (`customfield_11768`, `customfield_11623`, `customfield_11696`) exist as stale ghosts from past team-managed project configurations — they are unreachable via `field/{id}/context` (404), report zero populated issues, and are deletable via REST. Leaving them creates confusion and violates the "one global standalone field" principle. A previous OpenSpec change (`standardize-jira-space-setup`) established the `jira-space-setup-standard` contract for detecting and reporting these gaps; this change applies it to the `Reopened` field.

## What Changes

- Detect which of the 14 core projects already expose `customfield_11523` on their `Task` and `Subtask` issue types via the legacy `createmeta` endpoint, capturing per-project × per-issue-type evidence against the `jira-space-setup-standard` taxonomy.
- Generate per-project, per-issue-type operator instructions for the 13 team-managed projects where no REST-supported apply path exists.
- Apply the field to the single classical project (PUB) that has a Task type, via the existing `FieldConfig.add_field_to_screen` idempotent screen-tab write path.
- Delete the three stale project-scoped duplicate `Reopened` fields via `DELETE /rest/api/3/field/{fieldId}`, gated by a live-state check that refuses to delete any field with active context or populated issues.
- Backfill `customfield_11523` on existing `Task` and `Subtask` issues across all 14 projects by counting appropriate status transitions from each issue's changelog, gated by a no-overwrite guard.

## Capabilities

### New Capabilities

- `jira-reopened-field-standalone-coverage`: Standard workflow, evidence contract, and CLI for exposing the global `Reopened` field (`customfield_11523`) on `Task` and `Subtask` issue types of the 14 canonical core projects, consolidating to a single global field, and backfilling historical reopen counts from changelog.

### Modified Capabilities

- `jira-space-setup-standard`: Extended by `jira-reopened-field-standalone-coverage` to produce per-project × per-issue-type field-exposure evidence, consume the stale-duplicate deletion result, and emit an explicit partial-success outcome (`implemented-and-supported` for classical, `unsupported-by-current-api-surface` for team-managed, `implemented-and-supported` for duplicate deletion).

## Impact

- `jira-skill`: gains `field_expose_reopened` and `field_backfill_reopened` CLI groups, `field_consolidation.py`, and an evidence-first workflow for custom field exposure on team-managed projects.
- `tdt-core`: `PatchedJira` remains the required transport layer. `get_issue_changelog` is already exported and used for paginated backfill reads.
- `.agents` Jira skills gain a stable reference for how to handle team-managed field exposure gaps: detection + manual instructions + REST-available cleanup (duplicates).
- Jira Cloud operator workflows become repeatable with explicit unsupported/not-applicable checkpoints, backed by durable evidence.
