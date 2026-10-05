# Proposal

## Why

The archived version-authority change established useful reporting and gating, but current live audits still expose inconsistent provenance and updater contracts: Homebrew Node-backed formulas can be mistaken for npm installs, Qoder's wrapper and target can receive different authority findings, Kilo is associated with an invalid updater verb, npm deny filters can miss version-suffixed package names, and unchanged local versions are reported as proof of channel currency. The archived evidence also claims completion beyond what the current roster and apply evidence support, so corrections must be tracked in a new active change without rewriting the archive.

## What Changes

- Introduce one conservative, installation-aware supported-updater registry shared by inventory, coverage reconciliation, and pipeline declarations.
- Correct Homebrew Cellar-versus-ecosystem provenance and duplication reporting, including authoritative-copy inclusion.
- Make wrapper entrypoints inherit authority, target scope, and drift state from their resolved execution target; remove Qoder-specific pipeline branching.
- Align remediation commands with the declared sanctioned npm prefix and normalize version-suffixed npm package names before deny filtering.
- Reconcile Kilo's supported command and current covered/uncovered classification; classify Prime-Agent only from verified receipt and runtime evidence.
- Standardize pause truthiness and apply global pause policy consistently without mutating user configuration.
- Separate local updater idempotence from upstream release-channel currency; unknown currency MUST NOT be reported as current.
- Add bounded, value-blind inspection of accessible macOS LaunchAgents and the user's crontab, with explicit non-exhaustive boundaries.
- Reconcile the live covered roster, runbooks, and evidence contracts while preserving the archived change byte-for-byte.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `workstation-toolchain-inventory`: tighten installation provenance, updater authority, prefix remediation, pause-state, scheduled-writer, and currency-reporting requirements.
- `agent-cli-inventory-coverage`: require conservative supported updater declarations, wrapper inheritance, normalized manager filtering, and truthful idempotence/currency reporting.
- `archive-integrity-reconciliation`: record the stale archived claims and current corrective evidence in a new active change without modifying archived files.

## Impact

Affected implementation and documentation boundaries are the canonical inventory and coverage reporters, both mirrored maintenance runner scripts, the two workstation runbooks, and new delta specifications/tasks in the OpenSpec store. The implementation repository remains the store-owned scripts plus the executed mirror at `/Users/androidteam/Developer/scripts/`; no package installation, updater execution, configuration mutation, or archived-file edit is part of this planning change. Existing manager stages remain in place; the change narrows their eligible targets rather than forcing all tools onto one manager.

## Non-Goals

- Do not rewrite or move `openspec/changes/archive/2026-10-05-govern-tool-version-authority-and-drift`.
- Do not force every CLI onto Homebrew, npm, or a single release channel.
- Do not claim exhaustive visibility into root-owned LaunchDaemons, inaccessible system launchd jobs, container process engines, or updater scripts hidden behind arbitrary indirection.
- Do not infer upstream currency from an unchanged local version, a successful process exit alone, or a package-manager `auto_updates` flag.
- Do not execute live updater commands, package-manager upgrades, network installs, or configuration changes as part of implementation verification.
