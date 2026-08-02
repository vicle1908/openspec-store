## Context

Current review confirmed the ecosystem now has the right building blocks:

- `tdt-core` exposes Jira client extensions for filter, board, and dashboard operations.
- `jira-sprint-spreadsheet-ssot` completed the spreadsheet-as-source-of-truth model for sprint number, dates, issue scope, filter, and board resolution.
- `kbs-extra-sheets-and-linked-tickets` completed the broader pipeline contracts for sheet extraction, linked-ticket expansion, agile sprint creation, report refresh, and report links.
- `jira-dashboard-automation` completed the canonical shared dashboard lifecycle in `jira-skill.dashboard` with declarative layouts and validation.
- `jira-daily-reports` remains the live sprint report/person-capacity output path.

The remaining risk is not a missing primitive; it is ecosystem drift. The same sprint identity is described across multiple completed changes and repos, while the current report path can find/create a per-sprint dashboard link without obviously populating or validating that dashboard in the report constructor. A follow-up alignment change should make the runtime handoff explicit, document exact ownership, and require live readback evidence.

## Goals / Non-Goals

**Goals:**

- Define one observable `SprintContext` / resolved-scope handoff that carries spreadsheet id/title, sprint number/dates, issue keys, filter id/name, board id/name, optional sprint id, optional dashboard id, and project key.
- Ensure every downstream stage consumes that handoff rather than re-deriving a narrower or different scope.
- Clarify per-sprint dashboard semantics: link-only versus fully built dashboard, with the shared `jira-skill.dashboard` engine as the only builder.
- Add live validation and documentation tasks so active skills/specs/readmes agree with the current implementation.
- Keep dry-run/live mutation boundaries intact.

**Non-Goals:**

- Rebuild Jira's native sprint report API surface; custom aggregation remains the intended reporting model.
- Replace Jira native dashboards with Forge/app-owned dashboards.
- Change report row calculations, sheet layout, or person-capacity reconciliation rules unless a bug is found during validation.
- Create new raw Jira/GitLab clients or shell out to `acli`/`glab`.

## Decisions

### Decision 1: Treat this as a follow-up change, not a reopen

`jira-sprint-spreadsheet-ssot` is marked complete with 33/33 tasks. Reopening it would blur completed evidence. This change records only the gaps discovered after ecosystem review.

### Decision 2: Make sprint context the integration contract

The pipeline should expose a single typed or serialized resolved context to report/dashboard stages. Environment variables such as `RESOLVED_FILTER_ID` remain acceptable process-boundary transport, but code/tests should treat them as a representation of the resolved context, not independent sources of truth.

### Decision 3: Dashboard ownership stays in `jira-skill.dashboard`

The report path may render dashboard links, but dashboard creation/build/rebuild/validation logic should use `jira-skill.dashboard`. If KBS or `jira-daily-reports` creates the per-sprint dashboard, it must either call the shared build path and validate readback, or explicitly label the behavior as link-only and surface the command needed to build the dashboard.

### Decision 4: Validation requires live readback plus dry-run proof

Dry-run validation proves no writes occur. Live validation must read back the created/resolved Jira objects and report sheet output, then clean up any temporary probe objects if validation uses a temp dashboard/filter/board.

### Decision 5: Docs and skills are part of the deliverable

The user-facing skills must tell agents which repo owns each stage. Stale guidance is considered a gap because it leads future agents to use the wrong CLI or manually edit per-sprint Jira IDs.

## Risks / Trade-offs

- [Risk] Live validation can mutate shared Jira state. → Mitigation: prefer active sprint objects when safe; if probes are needed, prefix names clearly and delete them immediately.
- [Risk] Dashboard gadget APIs may accept config writes but not persist expected state. → Mitigation: use the existing dashboard validation readback and report required/best-effort mismatches explicitly.
- [Risk] Environment-variable handoff can be opaque. → Mitigation: log the resolved context with non-secret IDs/names and add tests that assert the handoff is honored.
- [Risk] Multiple completed OpenSpec changes describe overlapping sprint behaviors. → Mitigation: add an alignment report/index that points to canonical ownership instead of duplicating all details.

## Migration Plan

1. Audit active code and docs for sprint context, dashboard, and board/sprint ownership claims.
2. Add or update tests around resolved-context handoff and dashboard build/link behavior.
3. Update docs/skills to state canonical commands and ownership.
4. Run targeted unit tests in affected repos.
5. Run dry-run validation against the active sprint spreadsheet.
6. Run live validation/readback only where safe, with explicit cleanup for any temporary objects.
7. Record validation evidence in this change directory.
