# Tasks: openspec-progress-exit-status-correction

## Audit and implementation

- [x] 1.1 Capture the current store HEAD, active/archive ownership, installed OpenSpec version, and exact four live masked-progress matches. Baseline: `1a13e211a486e63d0f5f20234250bb9dc68d1e8c`, OpenSpec `1.8.0`; predecessor is archived; four live matches were found in the primary workflow skill, `active-change-triage.md`, `implementation-pitfalls.md`, and `pre-archive-validation.md`.
- [x] 1.2 Reproduce the failed `instructions apply` pipeline with and without `pipefail`, retaining exact exit codes and output classification. Nonexistent change: ordinary pipe exit `0` with a parsed JSON diagnostic; `pipefail` exit `1`; the new temporary-file helper exit `1` with no progress claim.
- [x] 1.3 Replace the primary workflow task-progress example with status-preserving temporary-file parsing.
- [x] 1.4 Replace the `active-change-triage.md` task-progress example with status-preserving temporary-file parsing.
- [x] 1.5 Replace the `implementation-pitfalls.md` task-progress example with status-preserving temporary-file parsing.
- [x] 1.6 Replace the `pre-archive-validation.md` task-progress example with status-preserving temporary-file parsing.

## Review and closure

- [x] 2.1 Sweep both live workflow trees for remaining direct `instructions apply | python3` task-progress pipelines; archived predecessor matches are historical and must remain untouched. Result: zero live matches; the archived predecessor remains unchanged.
- [x] 2.2 Validate this change with `openspec validate openspec-progress-exit-status-correction --strict --store openspec-store`. Result: exit 0, 1/1 change passed.
- [x] 2.3 Run active-change and full-store validation with explicit selectors, preserving complete JSON and exact exit codes; classify unrelated failures. Result: active 13/13 passed; full store 374/374 passed; doctor healthy with no issues.
- [x] 2.4 Re-read all four corrected examples and verify the command failure path cannot emit a progress claim or mask the OpenSpec exit code. All four changed blocks pass `bash -n`; positive active-change formatter returned `0/154 remaining=154`; nonexistent-change helper returned exit 1 with no progress output.
- [x] 2.5 Commit only the successor OpenSpec artifacts in the shared store; record SHA-256 hashes for the four live user-local guidance files and preserve unrelated store paths. Hashes at verification: `SKILL.md=c0fcdf57b1f9f1fd00b1afd3354f8d944993ec6ded3608073f728a608af748c4`; `active-change-triage.md=5c826add35f66c5eb965aafac61314177caad08b930d5eb3b61078a0ac89d6e7`; `implementation-pitfalls.md=09e51c797c4ae9c1f9db648b0b6073ae4e7f154f32fdfb69599d813a92642dc4`; `pre-archive-validation.md=9b2a5f5d95f214a501f092749c8465448265963c02168e0e1c3b8763a6ab2019`. Commit `74e67df0` contains only the five successor OpenSpec artifact paths; the unrelated research report remains untracked.
- [x] 2.6 Confirm archive readiness with `progress.remaining == 0`, focused validation, full validation, scoped commit evidence, and explicit archive authorization. Result after commit `74e67df0`: focused 1/1 passed, active 13/13 passed, full 374/374 passed, doctor healthy; this ledger update brings progress to `12/12`, and the user authorized archiving completed changes. Archive mutation and post-archive verification are separate lifecycle gates; post-archive evidence is recorded after mutation rather than as unchecked tasks in this ledger.
