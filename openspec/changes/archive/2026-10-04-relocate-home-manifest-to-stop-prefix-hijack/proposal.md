# Proposal: Relocate the Home-Directory Manifest to Stop Prefix Hijack

## Why
A `package.json` at `/Users/androidteam/package.json` causes `npm` and `npx` invoked from any
directory beneath `$HOME` that lacks its own manifest to resolve to the home directory — the
mechanism that turned an `npm audit fix --force` run in `~/Developer` into a mutation of an
unrelated home-level toolbelt.

## What Changes
- Copy the manifest, lockfile, and a freshly installed dependency tree to a dedicated
  location outside `$HOME`'s resolution path: `~/.local/share/home-toolchain/`.
- Verify at the new location that all three tools unique to the manifest (`bru`,
  `yaml-language-server`, `newman-reporter-htmlextra`) execute, that `npm audit` reports the
  same 12 high advisories, and that the `@faker-js/faker` split resolution is preserved.
- Expose those three tools by name through explicit symlinks in `~/.local/bin` (already on
  PATH), so usability is retained without any manifest in `$HOME`.
- Remove `/Users/androidteam/package.json`, `/Users/androidteam/package-lock.json`, and
  `/Users/androidteam/node_modules`.

## Capabilities

### New Capabilities
None.

### Modified Capabilities
- `npm-audit-remediation`: Extends the existing "Home-Directory Manifest Footgun Recording"
  requirement from *recording* the hazard to *eliminating* it. Adds the requirement that a
  `package.json` SHALL NOT reside directly in `$HOME`, that tooling previously resolved through
  it SHALL be relocated to an explicit non-hijacking location, and that the absence of the
  hijack SHALL be verified by `npm prefix` resolving to the invoking directory.

## Non-Goals
- Reducing or remediating the 12 residual advisories; they are already established as
  irreducible under the upgrade-only constraint.
- Changing versions during relocation; the relocated tree is a faithful copy.
- Removing or altering `~/.npm-global`, which is the sanctioned global npm prefix used by
  `~/Developer/scripts/workstation-daily-update.sh`.
- Modifying any repository under `~/Developer`.

## Affected Ownership Boundaries
- `/Users/androidteam/package.json` — **removed**
- `/Users/androidteam/package-lock.json` — **removed**
- `/Users/androidteam/node_modules` — **removed** (3.1 GB reclaimed)
- `/Users/androidteam/.local/share/home-toolchain/` — **created** (new home for the tooling)
- `/Users/androidteam/.local/bin/` — three symlinks added
- `platform/openspec-store` — spec delta, change artifacts, evidence
