# Add Reopened Field to Core Task/Subtask Issue Types Design

## Context

The TDT workspace uses `customfield_11523` ("Reopened", float) as the canonical global custom field for tracking how many times an issue has been reopened. The field exists with a single global context (`id=12638`, `isAnyIssueType=true`) but is not currently exposed on the `Task` or `Subtask` issue types of the 14 canonical core projects.

Live Jira research confirmed the following API surface:

- `GET /rest/api/3/issue/createmeta/{project}/issuetypes/{id}` — legacy endpoint, returns per-issue-type field metadata for team-managed projects. Usable for read-only detection.
- `POST /rest/api/3/field/{id}/context` — returns `"Only one global context is allowed per field."` for `cf_11523`. Adding project-specific contexts is blocked.
- `GET /rest/api/3/field/{id}/context/{contextId}/projectmapping` — not exposed by this Jira Cloud instance.
- `GET /rest/api/3/fieldconfigurationscheme/project?projectId={id}` — returns `{"values": []}` for team-managed projects.
- `GET /rest/api/3/issuetypescreenscheme/project?projectId={id}` — returns `{"values": []}` for team-managed projects.
- `DELETE /rest/api/3/field/{fieldId}` — supported (confirmed via `OPTIONS` probe: `Allow: DELETE,PUT,OPTIONS`). Applies to the three stale scoped duplicates.

This means:

- **Team-managed projects** (`AM`, `SR`, `TJ`, `RMD`, `PWM`, `COM`, `FUN`, `AU`, `STABI`, `P3AP`, `POEMS2`, `EW`, `BACKEND`): no REST write path for field-to-issue-type association. Manual UI steps required per project × issue type.
- **PUB** (classic): field can be added to the Task screen via `FieldConfig.add_field_to_screen`, idempotent and read-back-verified.
- **Stale duplicates** (`cf_11768`, `cf_11623`, `cf_11696`): safe to delete via REST.

`jira-space-setup-standard` already defines the evidence contract for these scenarios: `implemented-and-supported` for REST-available paths, `unsupported-by-current-api-surface` for team-managed field exposure.

## Goals / Non-Goals

**Goals:**

- Expose `customfield_11523` on `Task` and `Subtask` for all 14 core projects.
- Delete the three stale project-scoped duplicates.
- Backfill historical reopen counts from issue changelogs.
- Produce durable per-project evidence per the `jira-space-setup-standard` taxonomy.

**Non-Goals:**

- Creating a new custom field (the canonical field already exists).
- Attempting a REST-based field exposure for team-managed projects (not supported).
- Backfilling values on issues that already have a non-zero `cf_11523` value (no-overwrite guard).
- Modifying the field schema or adding options/contexts to `cf_11523`.

## Decisions

1. **Reuse the legacy createmeta endpoint for team-managed detection, not the v3 `/issuetypemetadata` surface**
   - Rationale: the v3 endpoint returned `{"fields": []}` on live inspection; the legacy endpoint (`/rest/api/3/issue/createmeta/{project}/issuetypes/{id}`) returns field metadata with stable `fieldId` keys. Fall back to "field absent" if the endpoint errors.
   - Alternative: use `GET /rest/api/3/field/search?projectIds={id}`. This returns 50 fields for EW including `cf_11523`, but the field count suggests it's the global field surface, not the issue-type-specific view. Prefer createmeta for the authoritative per-issue-type view.

2. **Duplicate deletion is gated by a live-state probe before issuing DELETE**
   - Rationale: `DELETE /rest/api/3/field/{id}` is supported but irreversible. The gate checks that the field reports 404 on `/context` and zero issues are populated. A `--force` flag bypasses the gate with a warning.
   - Alternative: skip the gate and delete blindly. Rejected because the gate is a one-line check and prevents accidental deletion of future live fields.

3. **Backfill uses a conservative two-string allowlist for transition detection**
   - Rationale: counting "reopen" transitions requires distinguishing intentional vs. incidental status moves. The allowlist `fromStatus ∈ {Done, Closed, Resolved}` × `toStatus ∈ {Reopened, Open}` covers the most common reopen patterns. A `--status-from` / `--status-to` flag pair lets the operator override.
   - Alternative: use a single status-name approach (any status containing "Reopened"). Rejected because it can overcount sibling transitions.

4. **Evidence is written to Markdown files in `output/` rather than printed only**
   - Rationale: `jira-space-setup-standard` requires durable evidence. The output directory is standard in `jira-skill` (`output/` is gitignored). Timestamped filenames prevent overwrites.
   - Alternative: print to stdout only. Rejected because evidence must survive the terminal session.

5. **CLIs are split into `field-expose-reopened` and `field-backfill-reopened`**
   - Rationale: consolidation/plan/instructions/apply are one workflow; backfill is a separate batch operation with different rate-limit and overwrite concerns. Splitting them lets each be invoked independently and reduces blast radius.
   - Alternative: one monolithic command. Rejected because the two workflows have different apply guards, retry semantics, and operator cadences.

## API Surface Summary

| Operation | Jira endpoint | Team-managed | Classic (PUB) |
|---|---|---|---|
| Detect cf_11523 presence on issue type | `GET /rest/api/3/issue/createmeta/{proj}/issuetypes/{id}` | yes | yes |
| Expose field on issue type | N/A (not supported) | `unsupported-by-current-api-surface` | `add_field_to_screen` |
| Delete stale duplicate | `DELETE /rest/api/3/field/{id}` | yes | yes |
| Backfill from changelog | `GET /rest/api/3/issue/{key}/changelog` | yes | yes |
| Write field value | `PUT /rest/api/3/issue/{key}` `{"fields": {"cf_11523": N}}` | yes | yes |

## Canonical 14-Project List

| Project key | Jira ID | Style | Task | Subtask |
|---|---|---|---|---|
| PUB | 11351 | classic | yes | no |
| AM | 11264 | next-gen | yes | yes |
| AU | 11263 | next-gen | yes | yes |
| SR | 11276 | next-gen | yes | yes |
| TJ | 11277 | next-gen | yes | yes |
| RMD | 11275 | next-gen | yes | yes |
| PWM | 11282 | next-gen | yes | yes |
| COM | 11267 | next-gen | yes | yes |
| FUN | 11271 | next-gen | yes | yes |
| STABI | 11278 | next-gen | yes | yes |
| P3AP | 11269 | next-gen | yes | yes |
| POEMS2 | 10036 | next-gen | yes | yes |
| EW | 11266 | next-gen | yes | yes |
| BACKEND | 10012 | next-gen | yes | yes |

## File Structure

```
src/jira_skill/
  field_consolidation.py   # Duplicate detection + safe delete
  field_backfill.py        # Changelog-driven backfill
  field_config.py          # Add is_field_present_in_createmeta helper

src/jira_skill/cli.py     # field-expose-reopened (4 subcommands) + field-backfill-reopened

docs/operations/
  reopened-field-task-subtask.md   # Ops doc

tests/
  test_field_consolidation.py
  test_field_expose_reopened_plan.py
  test_field_backfill.py
```

## Risks / Trade-offs

- **[Risk] DELETE is irreversible via REST (recovery requires Jira support)** → Mitigation: live-state gate refuses to delete anything that has active context or populated issues; dry-run is the default; `--force` emits a warning.
- **[Risk] createmeta returns empty for some team-managed projects** → Mitigation: treat empty as "field absent" and include the API error in evidence; the operator instruction covers both absent and error states.
- **[Risk] Status allowlist misses non-standard reopen patterns** → Mitigation: `--status-from` / `--status-to` flags; default allowlist is conservative (only Done/Closed/Resolved → Reopened/Open).
- **[Risk] Backfill rate limits on large projects** → Mitigation: `--continuous 24h` flag introduces a 24h sleep between batches; Jira's published rate limit is 100 req/min.
