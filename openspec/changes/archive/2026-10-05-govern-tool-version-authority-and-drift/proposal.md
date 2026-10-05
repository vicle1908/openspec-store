# Proposal

## Why

Workstation maintenance needs one installation-compatible version authority for
each active agent CLI so that updates neither compete across mechanisms nor
target an inactive copy. Existing source and coverage records do not establish
actual updater dispatch, target alignment, or reporter health; the previously
asserted downgrade matrix is not supported by current evidence.

## What Changes

- Record the active executable, installing asset, update command, actual version
  writer, target scope, and applicable release channel as distinct facts.
- Prefer a supported tool-native update command when it is compatible with the
  active installation. Recognize delegation to the installing manager as the
  same authority, and permit a supported owner-manager path when no compatible
  native path exists.
- Determine authority conflicts from configured or scheduled independent writers,
  not updater capability alone. Distinguish conflict risks from observed version
  drift; Homebrew `auto_updates` is not an exclusive authority waiver.
- Govern relevant package-manager and agent-CLI mutation stages consistently.
  Unknown or misaligned update paths are reported rather than executed through
  a guessed mechanism.
- Separate offline, read-only local audits from time-bounded, networked apply
  backstops. Check mode does not execute update verbs or mutate installations,
  configuration, or package-manager metadata.
- Report coverage status, authority findings, update outcomes, and measurement
  health independently. Preserve valid reports containing domain findings,
  including their documented nonzero exit status.
- Replace hardcoded tool/conflict expectations with current provenance and
  installation-specific evidence. Reassess completion claims where verification
  did not exercise the relevant behavior.

## Non-Goals

- Removing, relocating, reinstalling, or intentionally downgrading installed tools.
- Forcing every tool onto one installation channel or package manager.
- Changing the declared npm prefix, sanctioned-location rules, credentials, or
  user-selected background-update configuration.
- Editing archived changes or creating new capabilities or planning files.
- Implementing code or executing tool updates during this planning revision.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `workstation-toolchain-inventory`: refine documented-source selection and add
  installation-aware version authority, target alignment, and native-first
  update/backstop governance.
- `agent-cli-inventory-coverage`: align declared handling with verified update
  paths and distinguish coverage, authority, update, and measurement findings.

## Impact

- Revise the existing proposal, design, tasks, and two capability delta files.
- Future implementation affects the live workstation maintenance script, its
  store mirror, and existing inventory/coverage reporters. That implementation
  is not performed by this planning-update workflow.
- Preserve existing authoritative-copy, prefix, location, identity, and
  duplicate-retention contracts.
- Main specifications are changed only through a later spec-sync/archive
  workflow, not by this revision.
