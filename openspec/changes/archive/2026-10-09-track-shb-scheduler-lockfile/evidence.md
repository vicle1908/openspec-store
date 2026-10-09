# Apply Evidence: track-shb-scheduler-lockfile

## Scope and authorization

Implementation root: `/Users/androidteam/Developer/shb/shb-schedule`.
Planning root: `/Users/androidteam/Developer/platform/openspec-store`.
The user authorized apply and then explicitly authorized extending scope as needed to close the source-lint gate. The extension is limited to the seven reported runtime-source diagnostics, their behavior regression, and README guidance. No dependency upgrade, lock regeneration, deployment restart, remote push, archive edit, or unrelated workstation change is included.

## Immutable identities and lock integrity

- Implementation baseline: `d0729567d2d819a570a9f49bde86a78a02f22a35`.
- Implementation commit: `413f023823e869105f77fe21db4d9e5bbc34218b`.
- Lockfile SHA-256 before and after implementation/build/checks: `3ad697e6c39c82bfe40a09b11f74d765c6c9742583f40f830cd117f1eb69541b`.
- Locked package count: 61; the lockfile was not regenerated.
- Locked URL metadata inspection found no credentials or query strings; registry/artifact hosts were `pypi.org` and `files.pythonhosted.org`.
- The eight committed implementation paths are `.gitignore`, `uv.lock`, `README.md`, `src/shb_schedule/config.py`, `src/shb_schedule/engine/ownership.py`, `src/shb_schedule/engine/reloader.py`, `src/shb_schedule/server/health.py`, and `tests/test_server.py`.
- Existing dirty Graphify files were hash-compared before staging and were unchanged; no Graphify path was staged or committed.

## Ignore policy and clean checkout

- `.gitignore` now places `!uv.lock` after `*.lock`.
- In an isolated temporary runtime-state fixture, `git check-ignore --quiet --no-index` exited 1 for `uv.lock` (not ignored), and 0 for runtime `.lock`, `.db`, `.db-wal`, `.db-shm`, `.sqlite`, `.sqlite-wal`, and `.sqlite-shm` files (ignored).
- The temporary fixture was removed.
- A fresh local clone at implementation commit `413f023823e869105f77fe21db4d9e5bbc34218b` contained the tracked lockfile: `git ls-files --error-unmatch uv.lock` exited 0 and its SHA-256 matched the original.
- The clone used the existing sibling `shb-core` and `shb-tools` repositories through temporary directory symlinks, matching the project's declared sibling dependency layout. It was not a standalone single-repository portability claim.
- `uv lock --check --offline` in the fresh clone exited 0 with matching metadata.
- Changing only the cloned project's version to `99.0.0` made the same check exit 1 with a stale-lock error; the lock hash remained unchanged. The temporary clone was removed.

## Frozen installation and container build

Earlier completed apply verification:
- `uv sync --frozen --no-dev --no-editable`: exit 0, unchanged lock hash.
- `docker compose config --quiet`: exit 0.
- `docker compose build scheduler`: exit 0; its frozen installation consumed the lockfile.

After the authorized source fixes, final Docker verification built the existing Dockerfile with parent context `/Users/androidteam/Developer/shb`, without changing image versions or dependency declarations:
- Verification tag: `shb-scheduler:lockfile-apply-verify` (separate from the live deployment tag).
- Image ID: `sha256:5819b7580b80488658c24f3b45fe589d0ed9acc87f57e6611b30d57716cb99aa`.
- Build exit: 0; frozen sync installed 40 production packages.
- Image `shb-schedule --help`: exit 0.
- With networking disabled, a synthetic read-only manifest, and `SHB_SCHEDULER_ENABLED=false`, image `shb-schedule run-now eod-settlement-recon` exited 0 and returned `ACTION_REQUIRED` for absent ledgers, not `BALANCED`.
- No scheduler database file was created by that smoke. No real banking inputs or production workspace were used.
- Running production containers and database volumes were left in place; no Compose up/down or deployment restart was performed.

## Runtime source fixes and regression verification

Seven diagnosed source issues were resolved without suppressions:
- Preserve directory permission logic while merging the equivalent nested conditions and removing the unused noqa in `config.py`.
- Combine equivalent connection/cursor contexts in `ownership.py`.
- Keep strong references to every pending signal reload task until completion in `reloader.py`.
- Expose a public reloader idle-wait operation and remove health's private-lock access; simplify equivalent boolean returns in `health.py`.

Final commands against the changed implementation:
- `uv lock --check`: exit 0, 61 packages resolved, no lock change.
- `uv run --locked ruff check src`: exit 0, all checks passed.
- `uv run --locked mypy src`: exit 0, no issues in 17 source files.
- `uv run --locked pytest tests/ -q`: exit 0, **73 passed in 86.29s**.
- Added regression: `test_reloader_wait_for_idle_and_signal_task_retention`.
- Focused read-only review found no issues in permission, ownership, reload-task lifetime, idle-wait, shutdown, or lockfile handling; the regression exercises real runtime components without mocks.
- Repository-wide test-file style cleanup is not included; the lint gate exercised here is `ruff check src`, not `ruff check .`.

## Actual isolated CLI smoke

The actual installed `shb-schedule serve` command ran with a temporary home, synthetic manifest, disabled persistence, and an ephemeral loopback port:
- Health returned HTTP 200 with `is_leader=true`.
- Exactly one synthetic schedule was visible.
- SIGUSR1 reloaded its changed cron from `0 23 * * *` to `5 23 * * *`.
- HTTP POST `/scheduler/reload` returned HTTP 200 with `status=reloaded`.
- The synthetic reconciliation trigger returned `ACTION_REQUIRED` without ledger input.
- No `.db` file or traceback was observed.
- On SIGTERM, Uvicorn logged `Application shutdown complete.` before exiting with signal status -15. This is recorded as graceful signal termination, not falsely reported as exit 0.
- The temporary smoke directory was removed.

## Specification correction and documentation

Official uv documentation distinguishes `--frozen` (consume the lock without checking freshness) from `--locked` or `uv lock --check` (reject stale metadata without rewriting). The proposal, design, spec scenarios, tasks, and README now use that distinction. Docker's existing frozen installation is unchanged.

Source: https://docs.astral.sh/uv/concepts/projects/sync/

## Remaining lifecycle boundary

This is an apply completion record. The change remains active for the user's archive workflow; no completed historical archive is rewritten and no archive operation is performed by this apply step.

## Final lifecycle receipt and bounded timestamps

- Scope reconciliation and execution proof committed in OpenSpec store commit `4ce21c5f0b4bcf40f17ca17b5d467642775d7f76` before closing the remaining task checkboxes.
- Source Ruff: 2026-10-09T06:34:08.051399Z through 06:34:08.301622Z, exit 0.
- Mypy: 2026-10-09T06:34:08.301810Z through 06:34:09.696635Z, exit 0.
- Full pytest: 2026-10-09T06:34:09.696785Z through 06:35:37.659076Z, exit 0, 73 passing tests.
- Fresh local checkout and unchanged tracked-lock read-back: 2026-10-09T06:40:29.831033Z through 06:40:30.646127Z, command exits 0.
- Matching metadata lock check: 2026-10-09T06:40:30.646551Z through 06:40:30.767915Z, exit 0.
- Deliberately stale cloned metadata check: 2026-10-09T06:40:30.769035Z through 06:40:30.860830Z, expected exit 1, original and cloned lockfiles unchanged.
- Final strict change validation: 2026-10-09T06:43:35.993508Z through 06:43:37.270021Z, exit 0, `valid: true`, `issues: []`.
- Final apply instructions: 2026-10-09T06:43:37.270176Z through 06:43:38.313326Z, exit 0, `state: all_done`, `total: 7`, `complete: 7`, `remaining: 0`.
- The original scheduler and corrective archive directories had zero changes relative to the recorded store baseline. Unrelated workstation files and generated Graphify outputs were excluded from all scoped commits.

