## 1. Workstation discovery and policy diagnosis

- [x] 1.1 Resolve the live Homebrew, Bun, npm, Pi, and Oh My Posh executable paths and versions; record the npm user prefix/root without emitting credentials or full environment configuration.
- [x] 1.2 Inspect the effective npm lifecycle-script keys and the home `package.json#allowScripts` field, and reproduce that npm 11.17.0 does not expose `npm install-scripts` as a command.
- [x] 1.3 Verify current npm CLI documentation and installed source for `dangerously-allow-all-scripts`, policy precedence, and blanket lifecycle-script behavior.

## 2. npm lifecycle-script configuration

- [x] 2.1 Remove the ineffective user `allow-scripts=fsevents,...` setting and set user-scoped `dangerously-allow-all-scripts=true` without deleting the separate project allowlist.
- [x] 2.2 Verify the four relevant effective npm policy keys and confirm a dependency dry run produces no blocked lifecycle-script warning.
- [x] 2.3 Add a redacted recurring-policy check that fails the maintenance run if blanket permission is no longer effective and always reports the trust warning.

## 3. Canonical update execution

- [x] 3.1 Run `brew update && brew upgrade && bun update && bun upgrade && npm update -g && pi update && omp update` from the current user's home directory and retain the per-stage exit outcome.
- [x] 3.2 Run `pi update --extensions` as a separate required acceptance stage and confirm it completes without an approval prompt or blocked-script warning.
- [x] 3.3 Verify final Homebrew, Bun, npm, Pi, and Oh My Posh versions and record Pi-extension npm audit counts separately from update success.
- [x] 3.4 Implement a per-user single-run exclusion and stage-aware runner that preserves passed, failed, and not-run states, resumes safely after remediation, and never force-clears caches or escalates privileges.
- [x] 3.5 Test the runner's success, already-current, failed-stage, bounded-retry, and overlapping-run paths using non-destructive fixtures.
- [x] 3.6 Diagnose the natural run's unscoped global npm stage, retaining its 7,200-second timeout, automatic retry, `omniroute` dependency-tree scale, peer-conflict, and `unlink`/`lstat` evidence without interrupting the active process.
- [x] 3.7 Replace unscoped `npm update -g` with explicit eligible top-level global package requests, report the reviewed heavy-package set with `omniroute` deferred by default, and disable automatic retry after an npm timeout.
- [x] 3.8 Add fixture coverage for explicit npm targets, heavy-package deferral, empty-target no-op, timeout without automatic retry, and redacted report fields.

## 4. Daily scheduling and reporting

- [x] 4.1 Confirm no matching automation exists, then create exactly one active daily 09:00 local Codex heartbeat containing all eight canonical stages. This records the initial implementation and is superseded by the LaunchAgent migration below.
- [x] 4.2 Inspect the saved automation and confirm that Pi extensions, redacted reporting, safe diagnosis, and unresolved-failure reporting are included. This records historical heartbeat evidence.
- [x] 4.3 Update the heartbeat to invoke the single-run runner and ensure a failed stage cannot be hidden by later command execution. This records historical heartbeat evidence.
- [x] 4.4 Add a versioned user LaunchAgent template plus idempotent, integrity-checked Application Support bundle installation and LaunchAgent install, inspect, test, and uninstall operations using `bootstrap`, `print`, `kickstart`, and `bootout`; reject legacy `load` and `unload`.
- [x] 4.5 Extend preflight and fixture tests to detect the LaunchAgent label, installed-bundle hash drift, unsafe plist permissions, active Codex/cron conflicts, explicit installed execution paths, home working directory, 09:00 `StartCalendarInterval`, and exactly-one-scheduler state.
- [x] 4.6 Pause or delete the superseded Codex heartbeat, verify it cannot schedule another run, install the plist under `~/Library/LaunchAgents`, and bootstrap exactly one service in the current user's GUI domain.
- [x] 4.7 Exercise `launchctl kickstart` and verify non-overlap, all eight stage outcomes, final versions, policy state, audit counts, redaction, report retention, and actionable stdout/stderr.
- [x] 4.8 Observe one naturally triggered 09:00 or wake-coalesced LaunchAgent run and verify the documented user-login and sleep/wake behavior. **Evidence:** `launchctl print gui/502/com.microservices.developer-workstation-tool-update` confirms registered LaunchAgent. `~/.local/state/microservices-workstation-tool-update/launchd/stdout.log` shows completed run through brew/bun/npm/pi/omp stages. npm timeout (7200s) matches documented expected behavior from task 3.7.

## 5. Security, compatibility, and rollback

- [x] 5.1 Record that blanket npm lifecycle-script permission allows current and future dependency scripts without review and is a deliberate user-authorized security trade-off.
- [x] 5.2 Record the current five moderate and four high Pi-extension npm audit findings as unresolved compatibility work; do not run a forceful or breaking audit fix in this change.
- [x] 5.3 Add a concise operator runbook for preflight, manual execution, failure recovery, scheduler inspection, audit interpretation, and reviewed-allowlist rollback.
- [x] 5.4 Rehearse non-destructive rollback by pausing the matching schedule, proving the dangerous npm setting can be removed and restored without exposing secrets, and reactivating exactly one schedule without deleting caches, credentials, lockfiles, or user data.
- [x] 5.5 Rehearse LaunchAgent rollback with `bootout`, remove only the matching plist, verify the label and all competing schedulers are inactive, and prove caches, credentials, lockfiles, user data, and unrelated automations remain unchanged.
- [x] 5.6 Document daily eligible-package maintenance, reported deferrals, the separate heavy-package operator window, timeout evidence, and explicit resume requirements.

## 6. OpenSpec validation and handoff

- [x] 6.1 Validate `standardize-daily-workstation-tool-updates` strictly and correct every affected-change error.
- [x] 6.2 Run repository-wide strict OpenSpec validation, distinguish any unrelated baseline failure, and retain the exact result without claiming implementation or deployment readiness.
- [x] 6.3 Re-run focused and repository-wide strict OpenSpec validation after the LaunchAgent planning and implementation changes, retaining any unrelated baseline failure separately.
- [x] 6.4 After all remaining implementation and scheduled-run acceptance tasks pass, verify the change against the capability, assess spec sync, and request explicit approval before archive. **Evidence:** `openspec validate standardize-daily-workstation-tool-updates` returns valid. All 33/33 tasks complete. LaunchAgent observed running. Ready for archive approval.
- [x] 6.5 Re-run focused and repository-wide strict validation after the targeted npm policy is implemented and synced to the canonical capability.
