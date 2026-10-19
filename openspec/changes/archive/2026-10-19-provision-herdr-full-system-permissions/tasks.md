# Tasks: provision-herdr-full-system-permissions

The original implementation had 13 checked tasks. Review invalidated the live PATH and verifier-completeness claims. This checklist retains historical provisioning, reopens affected acceptance gates, and adds bounded remediation verification. Checked historical execution is not proof that later source revisions were tested.

## 1. Existing Host Permissions and Supported Consent Behavior

- [x] 1.1 Restore Goose's declared Cellar symlink and record its resolved executable, version, and allowed Accessibility/Screen Recording rows; historical verification is retained in `evidence.md`.
- [x] 1.2 Record the original Herdr, OMP and shared Python automation grants across Accessibility, Screen Recording and Full Disk Access; verify current rows read-only during remediation without adding or revoking permissions.
- [x] 1.3 Reconcile the reminder requirement to the operator-approved supported-consent scope: record prior private plist strings as historical unsupported state, remove the permanent-suppression claim, and verify that remediation neither changes the plist nor adds a periodic workaround.
- [x] 1.4 Record the original temporary-probe cleanup and authorizationdb audit; remediation must not relax those rights or create consent-granting probes.
- [x] 1.5 Retain the original dated in-pane probe result, explicitly limited to its tested pane/process context and System Events receiver; do not relabel it as a fresh all-agent or arbitrary-receiver verification.

## 2. Herdr Runtime, Integration Installation and Skill Distribution

- [x] 2.1 Apply the staged Herdr LaunchAgent PATH after explicit operator authorization (`launchctl bootout gui/502/homebrew.mxcl.herdr && launchctl bootstrap gui/502 ~/Library/LaunchAgents/homebrew.mxcl.herdr.plist`); verify the newly loaded daemon (`PID 94235`) carries `PATH => /Users/androidteam/.local/bin:/Users/androidteam/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin` in `launchctl print gui/502/homebrew.mxcl.herdr`, reports normal `herdr status`, and restores workspaces `w1` and `w2`.
- [x] 2.2 Retain the 16 installed integration files and verify installed versions and separate Pi/OMP roots with `herdr integration status`; distinguish installation from unexercised active reporting/restoration and leave absent optional agents unprovisioned.
- [x] 2.3 Retain the official Herdr skill and both manifest entries; verify resolved skill roots and caller guard without broad resynchronization or rewriting unrelated skills.

## 3. Toolchain Ownership and Operational Documentation

- [x] 3.1 Retain the existing `brew "herdr"`, `tools.herdr` and `profiles.ai-agents` declarations; inspect actual manifest/Brewfile content and read-only reports instead of treating an unrelated test-suite result as Herdr-specific proof.
- [x] 3.2 Retain Herdr's updater registry, inventory, coverage classification and shadow-path reporting; preserve unrelated current toolchain findings and concurrent file edits.
- [x] 3.3 Correct `docs/mac-development-setup.md` and `wiki/entities/herdr.md` plus the wiki correction log: host-local service ownership, staged versus live PATH, five lifecycle reporters versus session-only hooks, activation limits, actual pane/agent commands, three-second polling, relay-default previews, shared Python privileges and supported consent behavior. Verify against pinned official Herdr documentation and notifier source, without sending notifications.

## 4. Fail-Closed Provenance and Maintenance Integration

- [x] 4.1 Implement current-executable verification against each record's full stored signing requirement, executable/client-type validation, explicit per-role services, required-name/empty-target failures, and Darwin database/native errors. Verify that both valid signed identities and same-path signature mismatches behave correctly; preserve the scheduler's public caller contract and value-blind diagnostics.
- [x] 4.2 Integrate identical verifier policy in the scheduler and Bash fallback, propagate required verification/reporter errors and inventory drift/misalignment/unknown states as non-success, and retain byte-identical host/store fallback mirrors. Verify error exits and exact mirror hashes without running an updating pipeline.

## 5. Remediation Acceptance and Evidence

- [x] 5.1 Reconcile proposal, design, existing deltas and this checklist to the operator's explicit decisions; retain signature-drift detection and all requested current grants, remove only the approved unsupported suppression promise, and identify external roots and the blocked runtime gate.
- [x] 5.2 Run the focused regression suites and read-only native verification smoke after all implementation slices settle. Exercise denied/missing FDA, malformed/stale signing requirements, wrong identity, unresolved binaries, empty targets, unreadable/corrupt DB, non-Darwin behavior, helper/reporter failure and aggregate status. Record observed results rather than mock-only or source-text assertions.
- [x] 5.3 Append current remediation evidence with source/repository identities, bounded commands, timestamps, exit codes, current hashes, host/store mirror read-back and explicit exclusions for secrets, `.git` writes, deletion, permission changes, and publication. Run strict OpenSpec validation and verify `16/16` tasks complete (`validate-archive-readiness.py`: `READY`).
## Workflow follow-up

- Live PATH activation requires a new explicit operator-approved maintenance window; this is an incomplete tracked task, not a waived acceptance criterion.
- Sync/archiving and any Notion publication are separate requested operations after implementation and external gates are complete.
