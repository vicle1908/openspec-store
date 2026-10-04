# Proposal: Repoint the Residual Inventory to the Relocated Toolchain

## Why
Two requirements in the canonical `npm-audit-remediation` spec still name
`/Users/androidteam/package.json` as the object of their contracts, but that file was removed by
`relocate-home-manifest-to-stop-prefix-hijack`, so the requirements now point at a nonexistent
path.

## What Changes
- MODIFY "Workstation Root Manifest Residual Identity Coverage" so the residual inventory covers
  the relocated manifest at `~/.local/share/home-toolchain/package.json`, and update its recorded
  total to the current measured 12 high advisories attributed to their three roots.
- MODIFY "Archived Prior Art Reconciliation Before New Remediation" so the prior-art check is
  scoped to the relocated manifest.

## Capabilities

### New Capabilities
None.

### Modified Capabilities
- `npm-audit-remediation`: Repoints the residual-inventory and prior-art-reconciliation contracts
  from the removed `$HOME` manifest to the relocated toolchain manifest, completing the
  reconciliation begun in `reconcile-specs-with-home-manifest-removal`.

## Non-Goals
- Re-introducing a manifest at `$HOME`.
- Editing archived change directories.
- Remediating the residual advisories.

## Affected Ownership Boundaries
- `platform/openspec-store/openspec/specs/npm-audit-remediation/spec.md` — two requirements modified
- `platform/openspec-store/openspec/changes/repoint-residual-inventory-to-relocated-toolchain/`
