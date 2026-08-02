## Why

The original `jira-status-hygiene` taxonomy shipped with 14 next-gen + 8 company-managed entries covering only **31 of 362 distinct live status names (8.6%)**. A live `jira-skill status audit` against `psplit.atlassian.net` (211 projects, 750 status records) found 47 duplicate clusters (handled by dedupe) plus ~180 singletons. Of those singletons, ~80% are common synonyms for statuses that should be canonical (e.g. `UAT`, `KIV`, `QAT`, `Blocked`, `Closed`, `In Review`, `On Hold`, `Review`).

Without taxonomy entries for these, the dedupe command can collapse obvious duplicates like "To Do" / "to do" / "TO DO" but cannot collapse "In Review" or "UAT" into a canonical target. Each unmatched singleton either becomes a project-private record or stays as a singleton — neither outcome is a true instance-wide standard.

## What Changes

- **Add 14 new entries to `tdt-meta/canonical_statuses.yaml`** — both `next_gen` and `company_managed` sections — for high-frequency unmatched names found in live data.
- **Bump next-gen count from 14 → 28, company-managed from 8 → 14** — net +20 entries.
- **Bump taxonomy coverage from 8.6% to ~25%** of distinct live status names.
- **No new requirements** — this is an additive change to the existing `jira-status-taxonomy` capability's entry list, not a behavioral change.

## Capabilities

### Modified Capabilities

- `jira-status-taxonomy`: Add the following entries to the `next_gen` and `company_managed` sections of `tdt-meta/canonical_statuses.yaml`. Existing entries SHALL remain unchanged.

## Impact

- **Code**: `tdt-meta/canonical_statuses.yaml` — add ~24 new entries (~100 LOC).
- **Tests**: `jira-skill/tests/status/test_taxonomy.py` — extend the existing test matrix to cover each new entry's canonical name and category. No new test classes needed; add ~30 assertions to existing parameterization.
- **Operations**: No new operations. Existing `audit`, `dedupe`, `classify-singletons` commands will report improved coverage automatically.
- **Migration**: No data migration. The next `render-sheet` run will populate `canonical_key` for previously-unmatched singletons.
- **Non-Goals**: No canonical name changes (e.g. we will NOT rename `Review` → `Code Review`). No deletion of existing taxonomy entries. No new categories beyond `new`/`indeterminate`/`done`.

## Taxonomy Additions

### `next_gen` (14 new entries — 14 → 28)

| Key | Canonical Name | Category | Aliases |
|---|---|---|---|
| `in_review` | In Review | indeterminate | in review |
| `review` | Review | indeterminate | review |
| `uat` | UAT | indeterminate | uat |
| `qat` | QAT | indeterminate | qat |
| `kiv` | KIV | new | kiv |
| `on_hold` | On Hold | indeterminate | on hold, on-hold, hold |
| `blocked` | Blocked | indeterminate | blocked, block, blocker |
| `closed` | Closed | done | closed |
| `completed` | Completed | done | completed |
| `rework` | Rework | indeterminate | rework |
| `rejected` | Rejected | done | rejected |
| `deferred` | Deferred | new | deferred |
| `in_testing` | In Testing | indeterminate | in testing |
| `validation` | Validation | indeterminate | validation |

### `company_managed` (6 new entries — 8 → 14)

| Key | Canonical Name | Category | Aliases |
|---|---|---|---|
| `backlog` | Backlog | new | backlog |
| `in_progress_v2` | In Progress | indeterminate | in progress |
| `ready_for_launch` | Ready for Launch | indeterminate | ready for launch |
| `launched` | Launched | done | launched |
| `resolved` | Resolved | done | resolved |
| `removed` | Removed | done | removed |
| `implementation` | Implementation | indeterminate | implementation |
| `dropped` | Dropped | done | dropped |

(Detailed aliases live in the YAML; this table is the human-readable summary.)

## Open Questions

- **Q1**: Should `KIV` (Keep In View, a Southeast Asian project-management idiom) be a canonical entry or marked as a regional variant for retirement? Decision: add as canonical for now; revisit in v2 after seeing how many projects use it.
- **Q2**: Should `Completed` and `Closed` be separate canonical entries? Decision: yes — `Completed` is the project-completion state and `Closed` is the post-completion archive state; merging them loses semantic information.
- **Q3**: Should we add `removed`, `dropped`, `deferred` to the `done` category even though they aren't true "work finished" states? Decision: yes — Jira's `done` category is the only one that signals "no further action", which is what these statuses convey at the workflow level. The category is a UI color/positioning signal, not a semantic gate.
