# Design: Restore Workstation Root Manifest After Failed `npm audit fix --force`

## Context
See `proposal.md`. The failure is a resolution contradiction, not a network or registry
problem. `/Users/androidteam/package.json` has no git history, so there is no rollback path;
the design therefore minimizes destructive steps and prefers a single coordinated upgrade.

## Diagnosis (verified)
Measured facts, re-derived from disk and registry rather than memory:

| Fact | Evidence |
|---|---|
| `npm prefix` from `~/Developer` | `/Users/androidteam` |
| Root `~/Developer/package.json` | absent |
| Manifest under audit | `/Users/androidteam/package.json` (446 deps) |
| Audit result | 12 vulnerabilities (3 moderate, 9 high) |
| Packages on disk | `node_modules/newman` **MISSING**, `node_modules/newman-reporter-htmlextra` **MISSING** |
| Lockfile record | `newman → 5.3.2`, `newman-reporter-htmlextra → 1.23.1` |
| Failed run exit | code 1, `ELSPROBLEMS` |
| `htmlextra@1.22.5` peer | `newman: ^5.1.2` (conflicts with newman 6) |
| `htmlextra@1.23.1` peer | `newman: ^6.0.0` (compatible with newman 6) |
| `newman@6.2.2` pinned `csv-parse` | `4.16.3` vs manifest override `7.0.3` |
| `adm-zip` override | `0.6.1` — already applied, no change needed |

### Root cause chain
1. `npm audit fix --force` correctly identifies that all 12 advisories collapse to the
   `newman@5.3.2` chain and that the only fix is `newman@6.2.2` (a breaking major).
2. `--force` overrides the `htmlextra@1.22.5` → `newman@^5.1.2` peer edge, but
   `--force` does **not** override manifest `overrides`. The `csv-parse: 7.0.3` override
   contradicts `newman@6`'s pinned `4.16.3`, so no consistent tree exists under `--force`.
3. The install aborts (`ELSPROBLEMS`), and because it was a re-resolution, the previously
   installed `newman` and `newman-reporter-htmlextra` directories are already removed.

### Corrected earlier misreading
An initial hypothesis that `lodash@4.18.1` was a nonexistent version was **false**;
`npm view` confirms `4.18.1` exists and is the current latest. All 16 overrides were
individually resolved against the registry and all 16 are real, resolvable versions. Only
`csv-parse` genuinely conflicts with the selected parent.

## Goals / Non-Goals

**Goals:**
- Restore `newman` and `newman-reporter-htmlextra` as working, present, modern-version CLI tools.
- Clear the 12 advisories attributable to the `newman@5` chain.
- Leave an override set that resolves without `ERESOLVE`.
- Produce identity-level audit evidence.

**Non-Goals:**
- Re-running `--force` in any form.
- Touching any `~/Developer` repository (authority belongs to other changes).
- Introducing `@usebruno/cli` (owned by `modernize-package-replacements-and-dead-weight`).
- Deleting the `$HOME` manifest; that is a separate hygiene proposal.

## Decisions

### Decision 1: Coordinated dual upgrade instead of force
- **Rationale**: The peer conflict exists only because the two packages are upgraded
  separately. Upgrading `newman` and `newman-reporter-htmlextra` in one edit makes the peer
  edge satisfiable, so a plain `npm install` succeeds. This directly satisfies the existing
  spec requirement "Workstation Root Manifest Peer Conflict Resolution", whose scenario
  already prescribes `newman@^6.2.2`.
- **Reference to existing pattern**: This mirrors the already-remediated pattern used for
  `mcp-router` and `realtime/frontend` in the same capability — apply additive-safe upgrades
  and record residuals, rather than forcing resolution.

### Decision 2: Reconcile the `csv-parse` override, do not delete the override block
- **Rationale**: The other 15 overrides are security-relevant pins with live advisories behind
  them; removing the block would reintroduce vulnerabilities. Only `csv-parse` contradicts
  `newman@6`. Two acceptable resolutions: pin `csv-parse` to a version compatible with
  `newman@6`'s expectations, or relax the override so `newman@6`'s own pin holds. The chosen
  resolution is recorded in `evidence.md` with the resolved version read back from the
  lockfile.
- **Transaction boundary**: Manifest edit and install are one atomic step; if install fails,
  the manifest is restored to the pre-change text before any further attempt.

### Decision 3: Evidence by identity, not by count
- **Rationale**: The governing specs (`npm-audit-remediation`,
  `verify-npm-audit-remediation`) both require residual advisories be identified by package
  and no-fix marker. A bare count cannot distinguish "remediation failed" from "advisory has
  no upstream fix".
- **Transaction boundary**: Evidence is written only from command output read back from disk
  after the final install, never from the planning text.

## Risks / Trade-offs

- **Risk: no git rollback in `/Users/androidteam`** → *Mitigation*: capture the exact current
  manifest text to `evidence.md` as the recorded pre-state before editing, so a manual
  restore is possible.
- **Risk: `newman@6` is a major bump and may break existing collection runs** →
  *Mitigation*: verify `newman --version` and `newman run --help` execute; note in evidence
  that collection-level regression is out of scope for this change but flagged for the owner.
- **Risk: other tools depend on the `newman` CLI being on PATH** → *Mitigation*: the recovery
  restores presence, which is strictly better than the current deleted state; verify
  `npx newman --version` resolves.
