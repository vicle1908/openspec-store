# Tasks

## 1. Declare the script provenance manifest

- [x] 1.1 Add a manifest under `openspec-store/config/` listing every executed maintenance script with its executed path, recorded path, and which copy is authoritative; verify the manifest parses and names each of the seven scripts under `~/Developer/scripts/`, and that `workstation-daily-update.sh` and `workspace-worktree-scan.sh` are marked as having no recorded copy yet.
- [x] 1.2 Verify the manifest names only paths that currently exist, so it cannot declare a script that is not installed; verify by resolving every executed path in the manifest and confirming each is a readable file.

## 2. Record the unversioned executed scripts

- [x] 2.1 Copy `~/Developer/scripts/workstation-daily-update.sh` into `openspec-store/scripts/` as a recorded mirror and confirm the copy is byte-identical to the executed file (`shasum -a 256` of both match); verify the recorded file is tracked by `git ls-files` after adding.
- [x] 2.2 Copy `~/Developer/scripts/workspace-worktree-scan.sh` into `openspec-store/scripts/` as a recorded mirror and confirm byte-identity the same way; verify it is tracked.
- [x] 2.3 Confirm the recorded copies are inert, i.e. no LaunchAgent executes them; verify by grepping every plist in `~/Library/LaunchAgents/` for `openspec-store/scripts` and confirming no match, and that both jobs still reference their `~/Developer/scripts/` paths.
- [x] 2.4 Update the manifest to record the two newly recorded paths as present; verify the manifest states a recorded path for every executed script it lists.

## 3. Reconcile the recorded knowledge-refresh pair

- [x] 3.1 Bring `openspec-store/scripts/knowledge-refresh/knowledge-refresh-inventory.tsv` in line with the executed inventory, which lists 32 repositories against the recorded 20; verify entry counts match (`grep -vc '^#'` on both reports 32) and that no entry present in the executed copy is absent from the recorded copy.
- [x] 3.1b Confirm the reconciliation direction by evidence before recording it: verify each of the 12 added `shb/*` repositories exists as a Git repository and carries a live `.gitnexus` or `graphify-out` index, and that no repository appears only in the recorded copy, so reconciling cannot silently drop an indexed repository or omit a gone one.
- [x] 3.2 Regenerate `openspec-store/scripts/knowledge-refresh/knowledge-refresh-approval.sha256` over the reconciled inventory in the documented `<sha256>  <filename>` format; verify `shasum -a 256` of the recorded inventory equals the digest recorded beside it.
- [x] 3.3 Confirm reconciling the recorded copy did not alter the executed copy or the running job's approval state; verify the executed inventory still matches its own digest, so `com.developer.index-refresh` continues to pass its approval gate.
- [x] 3.4 Confirm the remaining six knowledge-refresh files stay byte-identical between the two copies; verify with a diff over each recorded file against its executed counterpart and report any that differ.
  - **Finding (reported, not reconciled):** five of the six are byte-identical, but `sync-notion-knowledge.sh` differs. The executed copy (mtime 2026-10-04 10:17) is newer and adds two wiki entity paths (`wiki/entities/shb.md`, `wiki/entities/omniroute.md`); both referenced files exist, so the edit is complete. This task authorises reporting differences, not reconciling them, so it is left drifted for the drift stage (group 4) to report, and reconciling it is deliberate follow-up work.
- [x] 3.5 Correct the conflicting requirement in `organization-namespaces` ("Tooling and script path resolution invariants") so it no longer names a fixed 20-repository count and no longer asserts a zero exit from the freshness check; verify with `openspec show organization-namespaces --type spec --store openspec-store` that the requirement names no repository count and that both copies agreeing is the assertion, while its path-resolution and fail-closed scenarios remain intact.
  - **Applied via the delta, not by hand-editing the main spec.** Per the store's own workflow a `MODIFIED` requirement merges into the main spec at *archive*, so the main spec deliberately still holds the old text until then. Verified the delta contains no `20-repo` literal, no unconditional `return code 0` assertion, states agreement (`same repository entries`, `taken from the installed inventory`), and retains all three original scenarios plus two freshness scenarios.

## 4. Drift detection in the daily job

- [x] 4.1 Add a `detect_script_drift()` helper to `~/Developer/scripts/workstation-daily-update.sh` that reads the manifest, computes a SHA-256 over each executed/recorded pair, and prints one line per pair with its state; verify by running it while the copies agree and confirming it reports no drift.
- [x] 4.2 Compare content only, not mode or mtime; verify by changing only the permission bits on a recorded copy (`chmod`) and confirming the helper still reports agreement, then restoring the mode.
- [x] 4.3 Make the helper report a drifted script by name and indicate which copy differs; verify by appending a temporary marker to a recorded copy, confirming the helper names that script, then reverting the marker and confirming agreement returns.
- [x] 4.4 Confirm the helper never writes to either copy; verify by hashing both copies before and after a drift-detecting run, including the deliberately drifted case, and asserting both hashes are unchanged.
- [x] 4.5 Add the drift stage to the pipeline after the skills parity check and before the store validation gate, renumbering the stage banners; verify the banners read `1/9` through `9/9` in order and that the parity banner precedes the drift banner which precedes the validation banner.
- [x] 4.6 Report drift through a `SCRIPT_DRIFT` flag in the run summary as a degradation, without triggering the parity stage's fail-closed exit; verify by forcing drift and confirming the run prints a drift degradation, still reaches the validation gate, and does not return the fail-closed failure status.
- [x] 4.7 Ensure the drift stage exits successfully when every pair agrees; verify by running it with consistent copies and confirming exit `0` and an explicit no-drift report.

## 5. Verification and integration

- [x] 5.1 Verify the daily job still honors `--check`: run it in check mode and confirm the drift stage reports without mutating either copy; verify with a SHA-256 tree digest of `openspec-store/scripts/` taken before and after, asserting equality.
- [x] 5.2 Run the full daily job end-to-end and confirm the drift stage reports agreement, all nine stages execute, and `openspec validate --all --strict --store openspec-store` reports zero regressions; verify the validation totals show no failures.
- [x] 5.3 Confirm idempotence: run the job twice in immediate succession and verify the second run reports the same drift state as the first.
- [x] 5.4 Confirm no LaunchAgent change is required; verify with `plutil -p` on both plists that their program paths and schedules are unchanged from before this change.
- [x] 5.5 Record verification evidence in `evidence.md` in the change directory, per the store's `cleanup-archive-verification` requirement; verify the file exists and contains the exact commands and observed outputs, including the deliberate-drift and permission-only-change cases.
- [x] 5.6 Commit the change artifacts and the newly recorded script copies so they are protected from the untracked-path removal observed on 2026-10-04; verify with `git ls-files` that every artifact and recorded script is tracked.
- [x] 5.7 Confirm no requirement anywhere still asserts a fixed 20-repository knowledge-refresh inventory; verify by searching all specs for the literal count and confirming every remaining reference describes agreement between the copies rather than a fixed number.
