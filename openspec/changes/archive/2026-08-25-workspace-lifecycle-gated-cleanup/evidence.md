# Evidence: workspace-lifecycle-gated-cleanup (task 4.3)

Recorded: 2026-08-25T15:12:56Z. Method: read-only verification only
(focused test runs, `openspec validate`, one CLI dry-run smoke against
synthetic reviewed fixtures, read-only `git status --porcelain` /
`git worktree list` / `diff` / `sha256` comparisons). No deletion, pruning,
reset, clean, checkout, push, archive, commit, or runtime mutation was
performed. No credential values were read, copied, hashed, or exposed.

## Focused lifecycle test suite

Run: `python3 <test file>` for each of the 12 files under
`~/Developer/openspec-store/scripts/workspace-lifecycle/tests/`
(2026-08-25, re-run fresh at evidence time). Result: **345 passed, 0 failed**.

- test_approval.py: 22 passed
- test_classify.py: 29 passed
- test_dryrun.py: 20 passed
- test_e2e_dryrun.py: 39 passed
- test_index_inputs.py: 38 passed
- test_manifest.py: 26 passed
- test_observations.py: 19 passed
- test_retention_gate.py: 18 passed
- test_retirement_git.py: 34 passed
- test_retirement_orca.py: 21 passed
- test_retirement_transitions.py: 55 passed
- test_runtime_ownership.py: 24 passed

Coverage notes: task 1.2's six required cases are test_classify.py T1–T6;
task 2.2's `git status --porcelain` + in-scope file-list checksum stability
is test_dryrun.py T2; task 4.2's ten scenario paths are all present in
`tests/fixtures/e2e-dryrun.fixture.json`; `authority-observations.fixture.json`
covers all five authorities (openspec, git, orca, runtime, index).

## Strict OpenSpec validation

- `openspec validate workspace-lifecycle-gated-cleanup --strict --store openspec-store`
  → `Change 'workspace-lifecycle-gated-cleanup' is valid`, exit 0.
- `openspec validate --all --strict --store openspec-store`
  → `Totals: 383 passed, 0 failed (383 items)` at evidence time.

## Final read-only workspace scan (CLI smoke)

Command (default dry-run mode; observations and retention inputs are the
reviewed synthetic fixtures; `--generated-at` supplied for replay because
fixture evidence timestamps are 2026-08-25T20:30Z):

```text
python3 ~/Developer/openspec-store/scripts/workspace-lifecycle/workspace-lifecycle.py \
  --observations ~/Developer/openspec-store/scripts/workspace-lifecycle/tests/fixtures/e2e-dryrun.fixture.json \
  --retention ~/Developer/openspec-store/scripts/workspace-lifecycle/tests/fixtures/retention-inventory.protected-and-candidate.json \
  --plan-id plan-final-verification-2026-08-25 \
  --generated-at 2026-08-25T21:00:00Z
```

Result: exit 0. Plan identity
`b6817ad0c643f001f27f3a8cd6ef500462e670354ebf98ad6cdf2744af4c6e60`.
Paths scanned: 10 — PROTECTED 7, REVIEW_REQUIRED 2, RECLAIMABLE 1
(review-only proposal), RECLAIMED 0; matches the task 4.2 expectations
one-for-one. Retention policy attached (`sha256:fixture-identity-0001`).

Reports written only to the documented workspace-state directory
(design Decision B, task 0.1):

- `~/Developer/.workspace-lifecycle/cleanup-manifest-b6817ad0c643f001.json`
- `~/Developer/.workspace-lifecycle/cleanup-summary-b6817ad0c643f001.txt`

The directory was absent before the smoke run and contained exactly these
two files after it.

## Manifest schema check

The on-disk smoke manifest passes `manifest.validate_manifest` (strict
schema: identity, evidence freshness, credential-shaped-field rejection),
is in `dry-run` mode, carries the plan identity above, and contains no
fixture secret values (`sk-live-e2e-999`, `hunter2-e2e`, `leak-me` absent).

## Non-mutation proof

- `git -C ~/Developer/openspec-store status --porcelain` captured before and
  after the smoke run: byte-identical
  (SHA256 `f58c4a0bbfbe4c34f70e2534cfd065fa619aa6d7802dd202e883ba0fedfc1ffe`,
  `diff` exit 0).
- `git -C ~/Developer/openspec-store worktree list` captured before and
  after: identical (6 worktrees, `diff` exit 0).
- No branch, worktree, OpenSpec artifact, runtime state, or generated index
  was created, modified, or removed by verification; the only writes were
  the two manifest/summary reports inside `~/Developer/.workspace-lifecycle/`.
