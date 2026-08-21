# Final release cleanup review

Date: 2026-08-21
Scope: OpenSpec archive, Pydantic AI documentation updates, provenance correction,
and preservation of unrelated worktree changes.

## Verdict

**COMMIT-READY for the reviewed archive/documentation scope.** The one blocker from
the initial review was the stale audit-commit hash in
`agent-harness/docs-update-report.md`; commit `1fe76f1` corrected it and the
bounded re-review passed. This verdict does not claim provider-backed, live-network,
credential, clean-install, or durable cross-process acceptance.

## OpenSpec archive

- Archive commit: `450cfa385b9711eec2d5dc487d6141ad43b0f9c8`
  (`archive establish agent observability contract`).
- Archive path: `openspec/changes/archive/2026-08-21-establish-agent-observability-contract/`.
- Release evidence commit: `6d027aeed892d33b0a02ad14ae2f55ce77754cd3`
  (`docs: record archive release evidence`).
- The archive contains the expected 13 renamed OpenSpec artifacts; the former
  active directory is absent. The archive commit contains no main-spec edits.
- Active OpenSpec state contains only `align-jti-skill-runtime-contract`,
  still in progress (`0/35` tasks).
- `openspec validate --all --strict --store openspec-store`: **373 passed,
  0 failed (373 items)**.

## Documentation commits

### agent-harness

- `3598a84ad944e5c3da3d5ae1643309884f0fcd0c` (`docs: align Pydantic AI runtime contract`)
  changes only the seven intended documentation files: `README.md`,
  `CHANGELOG.md`, and five `docs/*.md` files.
- `571f43acc81ddaa9ffe8ef5709573efbfc070e90` (`docs: record contract audit`)
  changes only `docs-update-report.md`.
- `1fe76f16a1c68a0eaeeb80348b59e1c70bf20e0d` (`docs: correct audit commit provenance`)
  changes only `docs-update-report.md`, replacing the stale predecessor hash
  with the actual audit commit `571f43acc81ddaa9ffe8ef5709573efbfc070e90`.
- The provenance re-review passed: the correction is one-file bounded, `git
  diff --check` passes, and no source/test/lockfile/Graphify path is in the
  correction commit.

### agent-core and agent-docs-sync

- agent-core documentation was already current at
  `28868da51cf7751bc6d2a3d8afe4d627c27f4a4d`; no additional docs change was
  required. Current HEAD is `24826738db022d55202c8f34b730b96c00a75b1b`.
- agent-docs-sync documentation was already current at
  `5ca0e478768e56d1228a1fc2c4e46d498563be0f0`; no additional docs change was
  required. Current HEAD is `757b045980e3edec59398f3204cd6c430c2acbd4`.

## Verification

- agent-harness full suite: passed; one existing `UnpricedModelWarning`.
- agent-docs-sync full suite: passed; existing lifecycle `FutureWarning`s.
- agent-core full suite: **not fully passing**. Two failures remain in the
  concurrent observability area: the short-lived OTEL CLI export test times out,
  and the observability lifecycle test receives an unrelated `Settings.agent`
  validation error. These failures are outside the documentation/archive changes
  and prevent a global all-repositories-green claim.
- `uv lock --check` passed in agent-core, agent-harness, and agent-docs-sync.
- `git diff --check` passed for the reviewed documentation and OpenSpec paths.

## Preservation boundaries

Unrelated work was preserved: Graphify output changes remain dirty in the three
product repositories; agent-docs-sync's concurrent
`tests/test_write_containment.py` edit remains untouched. The in-progress
`align-jti-skill-runtime-contract` change remains active and was not archived.
No provider credentials or live-provider results were fabricated.
