# Proposal: Reconcile Specs With the Removal of the Home Directory Manifest

## Why
Two requirements in the canonical `npm-audit-remediation` spec still assert in the present tense
that `/Users/androidteam/package.json` exists and is the object of remediation, but the change
`relocate-home-manifest-to-stop-prefix-hijack` removed that file, leaving the spec contradicting
the verified state of the machine.

## What Changes
- MODIFY the requirement "Workstation Root Manifest Peer Conflict Resolution" so it no longer
  presupposes a manifest at `$HOME`, and instead scopes its peer-resolution contract to the
  relocated toolchain.
- MODIFY the requirement "Root Manifest Transitive Override Hardening" so its override contract
  targets the relocated toolchain and reflects the measured irreducibility of the residual set
  rather than claiming zero non-residual vulnerabilities can be asserted from the retired path.
- Record the reconciliation as a change so the already-archived change that authored the stale
  text remains immutable, per the store's archive rule.

## Capabilities

### New Capabilities
None.

### Modified Capabilities
- `npm-audit-remediation`: Re-scopes two existing requirements from the removed
  `/Users/androidteam/package.json` to `~/.local/share/home-toolchain/package.json`, and aligns
  their normative claims with the verified facts (no manifest in `$HOME`; residual set
  irreducible under an upgrade-only constraint).

## Non-Goals
- Re-introducing any manifest at `$HOME`; the removal is correct and verified.
- Editing any archived change directory; the store's archive rule makes those immutable.
- Remediating the residual advisories; that is established as impossible without breaking tooling.
- Modifying `verify-npm-audit-remediation`'s historical sentence, which correctly refers to the
  manifest as it existed during the 2026-09-20 session and is not a live assertion.

## Affected Ownership Boundaries
- `platform/openspec-store/openspec/specs/npm-audit-remediation/spec.md` — two requirements modified
- `platform/openspec-store/openspec/changes/reconcile-specs-with-home-manifest-removal/` — change artifacts
