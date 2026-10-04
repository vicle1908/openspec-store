# Proposal: Restore Workstation Root Manifest After Failed `npm audit fix --force`

## Why
An `npm audit fix --force` run executed in the `~/Developer` workspace root (which has no
`package.json`) silently resolved upward to the stray home-directory manifest
`/Users/androidteam/package.json`, aborted mid-install with `ELSPROBLEMS`, and left
`newman` and `newman-reporter-htmlextra` deleted from `node_modules` while the lockfile
still records their previous versions — so the workstation API-testing toolchain is both
unpatched and uninstalled.

## What Changes
- Restore a coherent dependency tree in `/Users/androidteam/package.json` by upgrading the
  Newman chain in one coordinated step: `newman` `^5.3.2` → `^6.2.2` and
  `newman-reporter-htmlextra` `^1.22.11` → `^1.23.1` (whose peer range accepts `newman@^6`),
  eliminating the `^5.1.2` peer conflict that blocks the naive upgrade.
- Reconcile the `csv-parse` override (`7.0.3`) against `newman@6.2.2`'s pinned transitive
  `csv-parse@4.16.3` so the resolver is not instructed to build a contradictory tree.
- Reinstall and verify `newman --version` and the CLI presence of the htmlextra reporter.
- Re-run `npm audit` and record the residual state as verifiable evidence, distinguishing
  fixed advisories from any unpatched-upstream residual.
- Record the `$HOME`-manifest footgun so future `npm`/`npx` invocations are run from a real
  repository root rather than the workspace root.

## Capabilities

### New Capabilities
None.

### Modified Capabilities
- `npm-audit-remediation`: Re-asserts the existing requirement "Workstation Root Manifest
  Peer Conflict Resolution" against the manifest's actual post-incident state, extending it
  with an explicit recovery clause: a failed `--force` run that deletes packages SHALL be
  repaired by a coordinated peer-consistent upgrade rather than by re-running `--force`, and
  the residual advisory set SHALL be recorded by identity rather than by count.

## Non-Goals
- Re-running `npm audit fix --force` (it is the cause of the breakage and cannot resolve the
  peer/override contradiction).
- Migrating existing Postman collections to Bruno format, or introducing `@usebruno/cli`
  (owned separately by `modernize-package-replacements-and-dead-weight`).
- Modifying any repository under `~/Developer` (`mcp-router`, `realtime/frontend`,
  `prime-agent`, `kafka-microservices`); those surfaces are owned by other changes.
- Removing the home-directory manifest outright; this change treats that as a separate
  hygiene decision to be raised, not bundled.

## Affected Ownership Boundaries
- `/Users/androidteam/package.json` and `/Users/androidteam/package-lock.json`
  (workstation root tooling manifest; **not** a git repository — no rollback available)
- `/Users/androidteam/node_modules` (restoration target)
- `platform/openspec-store` (spec delta and change artifacts only)
