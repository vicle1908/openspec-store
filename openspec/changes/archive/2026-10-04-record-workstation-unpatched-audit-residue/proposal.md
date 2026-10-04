# Proposal: Record Unpatched-Upstream Advisory Residue on the Workstation Root Manifest

## Why
The workstation root manifest `/Users/androidteam/package.json` is already upgraded to the
current release of every package it depends on, yet `npm audit` reports 19 vulnerabilities
(2 moderate, 17 high) whose only offered remedy is a *downgrade*, so `npm audit fix --force`
cannot converge and the residual set is currently undocumented and therefore re-litigated on
every audit run.

## What Changes
- Record the 19 residual advisories by identity (package, advisory, dependency path) against
  `/Users/androidteam/package.json`, classifying each as unpatched-upstream rather than as a
  remediation failure.
- Record the evidence that every direct dependency is already at its latest published version,
  so the absence of a forward fix is demonstrated rather than assumed.
- Record the detection of the `$HOME`-manifest footgun that caused the original command to
  operate on `/Users/androidteam` while the operator was in `~/Developer`.

## Capabilities

### New Capabilities
None.

### Modified Capabilities
- `npm-audit-remediation`: Extends the existing "Unpatched Upstream Residual Documentation"
  requirement to the workstation root manifest, which that requirement's scenarios did not
  previously cover (they named `mcp-router`, `realtime/frontend`, and `prime-agent` only).
  Adds the determination rule that a residual whose only audit remedy is a version
  *downgrade* SHALL be classified as unpatched-upstream, and SHALL NOT be actioned.

## Non-Goals
- Re-running `npm audit fix --force` or applying any downgrade it proposes; the downgrades
  would reintroduce the very advisories just cleared and cannot converge.
- Modifying `newman`, `newman-reporter-htmlextra`, or `@usebruno/cli` versions; all three are
  already at their latest published releases.
- Touching `tdt/realtime/frontend`, `legacy/kafka-microservices`, `mcp-router`, or
  `prime-agent`; those surfaces are owned by other changes and by already-archived ones.
- Deleting or relocating the `$HOME` manifest; raising it as hygiene only.

## Prior Art (verified)
The dependency upgrades this change would otherwise have performed were already executed and
archived on 2026-10-04:
- `modernize-package-replacements-and-dead-weight` — archived at commit `895aacd9`, added
  `@usebruno/cli@^4.2.0` and recorded `newman --version` → `6.2.2`.
- `modernize-toolchain-and-major-dependencies` — archived at commit `b2453c16`, synced into the
  same `npm-audit-remediation` spec.
This change therefore does **not** repeat those upgrades; it records only the residual state
those changes left undocumented.

## Affected Ownership Boundaries
- `/Users/androidteam/package.json` — **read-only** in this change; no version is modified
- `platform/openspec-store` — spec delta, change artifacts, and evidence
