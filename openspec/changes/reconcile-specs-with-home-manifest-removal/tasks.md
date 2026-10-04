# Tasks

## 1. Identify the Stale Spec Assertions

- [x] 1.1 Locate every reference to `/Users/androidteam/package.json` in the canonical specs
- [x] 1.2 Classify each reference as a live assertion or a historical record
- [x] 1.3 Confirm the stale text originates from the archived change `2026-09-21-remediate-npm-audit-vulnerabilities`
- [x] 1.4 Confirm the removal of the manifest is verified and correct

## 2. Reconcile the Canonical Spec

- [x] 2.1 MODIFY "Workstation Root Manifest Peer Conflict Resolution" to scope to the relocated toolchain
- [x] 2.2 MODIFY "Root Manifest Transitive Override Hardening" to scope to the relocated toolchain
- [x] 2.3 Correct the unachievable "zero non-residual vulnerabilities" claim for the Bruno chain
- [x] 2.4 Confirm historical references (lines 173, 211, 225, 289) are left intact

## 3. Preserve Archive Integrity

- [x] 3.1 Confirm no file in any archived change directory was edited
- [x] 3.2 Confirm the original text remains recoverable from the archived change
- [x] 3.3 Leave `verify-npm-audit-remediation`'s historical sentence unchanged

## 4. Verification and Spec Sync

- [x] 4.1 Confirm no live assertion of a `$HOME` manifest remains in the canonical spec
- [x] 4.2 Run `openspec validate --all` and confirm the delta spec validates
- [x] 4.3 Sync the delta spec into the main `npm-audit-remediation` spec at archive time
- [x] 4.4 Archive the change and commit the store
