# kbs-resolve-sprint-scope-signature-fix

## Why

On 2026-06-11, commit `2437c9f` in `tdt-core` refactored `resolve_sprint_scope()` to remove the `filter_id_override` and `board_id_override` parameters, replacing the `override > find > create` resolution chain with a simpler `find > create` chain. The kbs CLI (`jira-kanban-from-spreadsheet`) was **not updated** to match this new signature.

As a result, `kbs sync` and `kbs verify` crash with a `TypeError` whenever they call `resolve_sprint_scope`:

```
TypeError: resolve_sprint_scope() got an unexpected keyword argument 'filter_id_override'
```

The kbs pipeline never completes. No filter is created, no board is created, and no report handoff occurs. The Sprint Report sheet subsequently runs in standalone mode, falling back to an arbitrary old filter (filter 10394, "17-Aug-2024-LiveDeployment") whose JQL is unrelated to the Sprint 17 scope. The report header shows the wrong filter link and no sprint/board/dashboard links.

Two call sites are affected:
- `cli.py:409-410` in the `sync` command
- `cli.py:797-798` in the `verify` command

The `ai-review` deployment at `deployments/ai-review/deps/jira-kanban-from-spreadsheet/` ships its own copy of kbs that also carries the same bug.

## What Changes

- Fix **both** kbs CLI command call sites (`sync` and `verify`) by removing the stale `filter_id_override` and `board_id_override` kwargs
- Keep the existing post-call fallback pattern (`scope.filter_id or cfg.filter_id`) — this correctly handles pre-seeded filter/board ids from config without needing them as function kwargs
- Also fix a secondary issue in `jira-daily-reports`: the board id assignment in `_resolve_scope_from_spreadsheet` unconditionally overwrites the board id even when a kbs-resolved scope was already handed off via `RESOLVED_BOARD_ID`; add a `not self.has_resolved_scope` guard to match the filter assignment behavior

## Capabilities

### New Capabilities

(None — this is a bug fix, not a new feature.)

### Modified Capabilities

- `kbs-cli`: Remove stale kwargs from `resolve_sprint_scope` call so the pipeline no longer crashes; post-call fallback logic already handles pre-seeded ids correctly
- `jdr-sprint-report-sheet`: Add `has_resolved_scope` guard to board id fallback in `_resolve_scope_from_spreadsheet` so kbs-resolved board ids are preserved

## Impact

- `tdt-core`: No changes needed — the refactor was correct; the fix belongs in kbs
- `jira-kanban-from-spreadsheet` / kbs: Remove two stale kwargs from both `cli.py` call sites (lines ~409-410 in `sync`, lines ~797-798 in `verify`); add targeted test asserting both commands complete without `TypeError`
- `jira-daily-reports`: Add one-line guard in `_resolve_scope_from_spreadsheet`; add test asserting kbs-resolved board id is not overwritten by spreadsheet fallback
- `ai-review` deployment: Update the shipped copy at `deployments/ai-review/deps/jira-kanban-from-spreadsheet/src/kbs/cli.py` with the same two-kwargs removal
- External systems: Jira Cloud and Google Sheets readback validation only

## Non-Goals

- Do not re-add `filter_id_override`/`board_id_override` to `resolve_sprint_scope` — the post-call fallback pattern is correct and should be kept
- Do not change JQL generation, report calculations, or sheet layout
- Do not change the dashboard find-or-create behavior
