## 1. Modeling and data extraction

- [x] 1.1 Add canonical person identity helper for assignee and worklog author records
- [x] 1.2 Add worklog daily aggregation helper that buckets `timeSpentSeconds` by person+date
- [x] 1.3 Add complete worklog retrieval path and tests for paginated worklogs (`total > returned`)
- [x] 1.4 Add ownership aggregation helper for assigned ticket count and original estimation totals
- [x] 1.5 Add activity aggregation helper for worked-ticket count (deduped per person+issue)
- [x] 1.6 Add spreadsheet-timezone lookup helper for daily bucketing

## 2. Report generation and sheet output

- [x] 2.1 Add person-capacity row builder with `No.` column and stable deterministic sorting
- [x] 2.2 Add date-window resolver (sprint-window preferred, rolling 14-day fallback)
- [x] 2.3 Add `Person Capacity` tab writer in the sprint-sheet flow without breaking existing `Sprint Report` tab
- [x] 2.4 Add summary header rows explaining ownership vs activity metrics in the person tab
- [x] 2.5 Include explicit columns for `Assigned Tickets`, `Worked Tickets`, `Original Estimation Total`, `Logged Total`, and daily date columns
- [x] 2.6 Make person tab name/title configurable while defaulting to `Person Capacity`
- [x] 2.7 Read spreadsheet timezone and use it for daily bucket boundaries

## 3. Validation and correctness checks

- [x] 3.1 Add unit tests for assignee vs worklog-author attribution rules
- [x] 3.2 Add unit tests for daily column generation, window fallback behavior, and timezone bucketing
- [x] 3.3 Add reconciliation checks: sum of daily cells equals person logged totals
- [x] 3.4 Add tests for multi-author same-issue attribution and per-person worked-ticket dedupe
- [x] 3.5 Add live verification script/runbook steps for spreadsheet update and sample cross-check

## 4. Documentation and rollout

- [x] 4.1 Update README and skill docs with person-capacity semantics and column definitions
- [x] 4.2 Update OpenSpec consolidation docs to reference the new person-capacity tab
- [x] 4.3 Record known limitations and operational guidance (sparse logs, timezone interpretation)
- [x] 4.4 Execute final live run, capture evidence, and mark rollout ready
