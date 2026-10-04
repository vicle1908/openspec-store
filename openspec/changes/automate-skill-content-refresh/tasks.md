# Tasks

## 1. Refresh stage scaffolding and output parsing

- [x] 1.1 Add a `refresh_skill_content()` helper to `~/Developer/scripts/workstation-daily-update.sh` that runs `skills update -y` from the workspace root, captures combined stdout/stderr, and strips ANSI escape sequences; verify it can be sourced/called in isolation without mutating the tree by pointing it at a scratch copy of `skills-lock.json` and confirming it returns the captured text.
- [x] 1.2 Implement the five-outcome classifier inside the helper, matching `Found N update(s)`, `Refreshing N skill(s)`, `✓ Updated N skill(s)`, and `Multiple current paths match`; verify each branch by feeding it captured sample output for: a global drift run, a project refresh run, an already-current run, and a path-ambiguous run.
- [x] 1.3 Make an unrecognized summary classify as `refresh_failed` rather than `already_current`, and verify by feeding the classifier a truncated/garbled summary and asserting it reports failure.
- [x] 1.4 Ensure the classifier never compares `skills-lock.json` `computedHash` against a locally computed digest, so the refresh cannot key off the non-reproducible internal digest; verify by grepping the helper for `computedHash` and confirming no match.

## 2. Pipeline integration and stage ordering

- [x] 2.1 Insert the refresh stage between the skills parity check and the OpenSpec validation gate, renumbering the seven existing stage banners accordingly; verify with `sed -n '/Stage/p'` that the banners read 1..8 in order and that the refresh banner sits after the parity banner and before the validation banner.
- [x] 2.2 Wire the refresh stage to report its outcome and set a local `REFRESH_FAILED` flag, then log a summary line recording refreshed / already-current / path-ambiguous / failed counts; verify by running the script in apply mode and confirming the summary line appears in `~/Library/Logs/workstation-daily-update.log`.
- [x] 2.3 Confirm the refresh stage returns success to the pipeline so a failed refresh does not abort later stages, matching the existing `|| true` treatment of network-bound stages; verify by forcing the classifier into `refresh_failed` via an unreachable upstream (e.g. temporary bogus DNS entry or `HTTPS_PROXY` pointing at a dead port) and confirming the validation gate still runs afterward.
- [x] 2.4 Confirm the existing parity stage's fail-closed behavior is unchanged and still returns nonzero on unresolved links; verify by running `python3 ~/Developer/platform/openspec-store/scripts/sync-workspace-agent-skills.py --check` and confirming its exit code still propagates through `SYNC_FAILED`.

## 3. Path-ambiguity handling

- [x] 3.1 Count entries from the `Multiple current paths match … skipping them` warning into a distinct `path_ambiguous` bucket that is neither refreshed nor failed; verify that a project-scope run reports `path_ambiguous=1` (for `docfork-docs`) and does not increment the failed count.
- [ ] 3.2 Assert that a run whose only unrefreshed entry is path-ambiguous still concludes successfully; verify by running the full script in apply mode and confirming the run completes without the fail-closed exit path being triggered.
- [x] 3.3 Record in the log that the path-ambiguous entry is informational, including the upstream source name, so a reviewer can distinguish it from staleness; verify the log line names `docfork/docfork` and does not label the entry stale or broken.

## 4. Agent CLI coverage

- [x] 4.1 Replace the single `claude update` call with a loop over the declared covered set (`claude`, `codex`, `opencode`, `kilo`, `auggie`, `qoder`, `pi`), using each tool's own verb, and log the declared set; verify the loop updates every covered agent that is installed and the log records the covered set.
- [x] 4.2 Pass `auggie update --skip-confirmation` so the stage never blocks on a confirmation prompt under launchd, and verify by running the stage with stdin closed (`</dev/null`) and confirming it completes without waiting.
- [x] 4.3 Skip a covered-but-absent agent without reporting a failure, and report an installed agent outside the covered set as uncovered; verify by running the loop and confirming no absent agent produces an error and that `droid` (native, no scriptable update verb) is reported as uncovered.
- [x] 4.4 Bound each agent update with the timeout helper so a hanging updater cannot stall the job, and continue to the next agent on timeout while reporting that agent as failed; verify by running the loop with an artificially low bound and confirming the loop completes and reports the timeout for the affected agent.
- [x] 4.5 Detect an updater that exits zero while reporting an error and report it as a failure rather than a successful update; verify against `kilo update` (which prints `Error: Failed to change directory to …` and exits `0`) and confirm the stage reports that agent as failed and the run reports a degraded agent outcome.

## 5. Time-bounded refresh

- [x] 5.1 Source (or copy) the PID-aware `run_with_timeout()` helper from `~/Developer/scripts/knowledge-refresh/refresh-knowledge-indexes.sh` into the daily job, or extract it to a shared location both scripts source, and verify the daily job still runs end-to-end after the change.
- [x] 5.2 Wrap the `skills update` invocation in `run_with_timeout` with a configured bound, and classify a `124` return as `refresh_failed`; verify by invoking the wrapper against a deliberately slow command (e.g. `run_with_timeout 2 sleep 30`) and confirming it returns `124` and is classified as a failure.
- [x] 5.3 Confirm a timed-out refresh does not stall the maintenance run and does not abort later stages; verify by forcing a refresh timeout and confirming the validation gate still executes.

## 6. Documentation and integration verification

- [ ] 6.1 Document the refresh stage, its five outcomes, the timeout bound, and the path-ambiguity exception in the workstation maintenance notes that accompany `workstation-daily-update.sh`; verify the documented manual command reproduces the logged outcome when run as written.
- [ ] 6.2 Verify that drift is observable before content is replaced: capture the stage's reported drift-availability line and confirm it is emitted before any `Updating <name>` line; verify by diffing line order in the captured output.
- [ ] 6.3 Document explicitly that `skills update` has no dry-run mode, so readers do not assume a `--check`/`--dry-run` exists; verify by running `skills update --help` and confirming no such flag is listed.
- [ ] 6.4 Run the full script end-to-end and confirm the log records all five outcome fields and that `openspec validate --all --strict --store openspec-store` still reports zero regressions; verify the validation totals show the same pass count as the pre-change baseline.
- [ ] 6.5 Verify idempotence by running apply mode twice in immediate succession and confirming the second run reports no content change (already-current) and the same single path-ambiguous entry; verify by diffing the logged outcome fields of the two runs.
- [ ] 6.6 Confirm no plist change is needed and the modified script is picked up by the existing schedule; verify by running `plutil -p ~/Library/LaunchAgents/com.developer.workstation-daily-update.plist` and confirming it still points at `~/Developer/scripts/workstation-daily-update.sh` with the 08:00 calendar interval.
- [ ] 6.7 Record verification evidence in `evidence.md` inside the change directory, per the store's `cleanup-archive-verification` requirement; verify the file exists and contains the exact commands and observed outputs for each completed group.

## 7. Change-durability hardening

- [x] 7.1 Commit the change artifacts to the store's git so they are protected from the untracked-path removal observed on 2026-10-04; verify with `git -C ~/Developer/platform/openspec-store ls-files openspec/changes/automate-skill-content-refresh` that every artifact is tracked.
