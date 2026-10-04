# Proposal: Verified Absence of an Upgrade-Only Remedy for the Workstation Root Manifest

## Why
The workstation root manifest `/Users/androidteam/package.json` carries 12 high-severity
advisories, and the operator requires they be cleared **by upgrade only, never by downgrade**;
research was required to decide whether such a path exists, and it does not — every candidate
forward fix either does not exist upstream or breaks the installed tooling.

## What Changes
- Record the completed upgrade-only research, including the applied-and-reverted
  `@faker-js/faker@>=10.5.0` override that cleared 5 advisories but broke `newman` and `bru`.
- Record the full forward-fix sweep across all 12 affected packages, establishing that no
  upgrade-only remedy exists for the residual set.
- Record the conclusion that the manifest must be held at its current, latest, working
  versions, with the residual advisories accepted as irreducible.

## Capabilities

### New Capabilities
None.

### Modified Capabilities
- `npm-audit-remediation`: Adds a compatibility gate to the upgrade-only override constraint —
  a forward override SHALL be validated for consumer API compatibility before it is retained,
  and SHALL be reverted when it breaks an installed consumer even if it clears the advisory.
  Adds the requirement that a candidate remedy clearing an advisory at the cost of breaking the
  dependent CLI SHALL be recorded as a rejected remedy, not as a remediation.

## Non-Goals
- Any downgrade, for any package.
- Retaining the `@faker-js/faker` override; it was applied, found to break `newman` and `bru`,
  and reverted to the verified pre-change state.
- Modifying any repository under `~/Developer`.
- Substituting an unvetted patched fork of `braces` or `node-forge`.

## Affected Ownership Boundaries
- `/Users/androidteam/package.json` — **final state identical to pre-research** (no net change)
- `platform/openspec-store` — spec delta, change artifacts, evidence
