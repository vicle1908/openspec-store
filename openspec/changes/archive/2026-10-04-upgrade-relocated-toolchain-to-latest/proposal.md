# Proposal: Upgrade the Relocated Toolchain to the Latest Permitted Versions

## Why
The relocated workstation toolchain still carried transitive dependencies behind their published
latest versions within their own declared semver ranges, so an operator asking for "latest where
possible" had outstanding in-range upgrades that no direct-dependency change would reach.

## What Changes
- Apply `npm update` against `~/.local/share/home-toolchain` to raise every transitive dependency
  that its parent's declared range already permits.
- Add two upgrade-only overrides for dependencies that are exact-pinned by their parents and so
  cannot move by range resolution alone: `aws4` to `>=1.13.2` and `extsprintf` to `>=1.4.1`.
- Verify that no direct dependency or override pin remains behind its latest published version,
  and that the audit residual set is unchanged (it belongs to different packages).

## Capabilities

### New Capabilities
None.

### Modified Capabilities
- `npm-audit-remediation`: Extends the upgrade-only constraint to cover **in-range transitive
  refresh**, not only advisory-driven overrides. Adds the requirement that a toolchain declared
  "at latest" SHALL be verified by an empty `npm outdated --all` restricted to in-range moves,
  with exact-pinned stragglers raised by upgrade-only override.

## Non-Goals
- Applying any version lower than the currently installed one.
- Clearing the 12 residual advisories; they are rooted in packages whose latest published version
  is still inside the advisory range, which no upgrade can fix.
- Removing any dependency.

## Affected Ownership Boundaries
- `~/.local/share/home-toolchain/package.json` — two overrides added
- `~/.local/share/home-toolchain/package-lock.json` — transitive refresh
- `platform/openspec-store` — spec delta, change artifacts, evidence
