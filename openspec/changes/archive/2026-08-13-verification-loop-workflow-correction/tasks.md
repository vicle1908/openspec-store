# Tasks: verification-loop-workflow-correction

## Audit and reproduction

- [x] 1.1 Freeze the shared store and OpenSpec CLI provenance (`openspec` 1.8.0, store SHA/branch/status, active-change inventory).
- [x] 1.2 Reproduce the planning-vs-implementation state mismatch with `status --json` and `instructions apply --json` on an active change with incomplete tasks.
- [x] 1.3 Reproduce the unscoped validation behavior from a consumer repository and the passing store-scoped equivalent.
- [x] 1.4 Reproduce the missing-task-file checkbox arithmetic failure from the legacy shell snippet.
- [x] 1.5 Run focused and full-store structural validation and `openspec store doctor`; retain exact exit codes and totals.

## Workflow corrections

- [x] 2.1 Update the primary OpenSpec workflow guidance to distinguish planning, implementation, structural validation, and closure state.
- [x] 2.2 Update plan-review and code-review guidance to use explicit store-scoped validation and preserve verifier exit codes.
- [x] 2.3 Add finite, state-change-gated multi-round verification guidance.
- [x] 2.4 Replace fragile checkbox arithmetic in the primary workflow guidance with a parser matching the OpenSpec task grammar.
- [x] 2.5 Add the state-semantics and structural-only warning to review governance guidance.

## Remaining reference sweep and closure

- [x] 3.1 Sweep all OpenSpec-related user-local references for stale unscoped validation, masked OpenSpec verifier pipelines, and status/implementation conflation; classify each remaining match as corrected, historical, or requiring a follow-up patch. All actionable high-risk workflow/review examples were corrected; CLI help/history examples remain intentionally illustrative.
- [x] 3.2 Validate this change with `openspec validate verification-loop-workflow-correction --strict --store openspec-store`.
- [x] 3.3 Run `openspec validate --all --strict --no-interactive --store openspec-store` and classify any unrelated result: current run at `7928ddd772e671cacbf592511411b6a30cda5599` reports 374 items, 374 passed, 0 failed.
- [x] 3.4 Re-read the corrected guidance and confirm the exact state model, bounded retry rule, safe task-counting recipe, and closure-only archive semantics are present.
- [x] 3.5 Commit only this change directory in the shared store after explicit closure authorization; commit `e3354e62` contains only the corrective evidence/task paths, and unrelated paths remain unstaged.
- [x] 3.6 Confirm archive readiness: tasks 3.1–3.5 are evidenced and checked, focused validation passes, implementation progress reports `remaining=0` after this ledger update, and the user explicitly authorized the archive command. Archive mutation and post-archive verification are separate lifecycle gates.
