# Design: Record Unpatched-Upstream Advisory Residue on the Workstation Root Manifest

## Context
See `proposal.md`. This change records an inventory; it does not change any dependency version.
The original investigation began as a `--force` breakage hypothesis and converged, through
measurement and coordination with three concurrent sessions, on a different finding.

## Diagnosis (measured, not assumed)

| Fact | Evidence |
|---|---|
| `npm prefix` from `~/Developer` | `/Users/androidteam` |
| Root `~/Developer/package.json` | absent — the command resolved to `$HOME` |
| Manifest audited | `/Users/androidteam/package.json` (446 deps) |
| `newman` installed | `6.2.2` — equal to `npm view newman version` (latest) |
| `newman-reporter-htmlextra` installed | `1.23.1` — equal to latest |
| `@usebruno/cli` installed | `4.2.0` — equal to latest |
| `npm audit` | 19 vulnerabilities (2 moderate, 17 high) |
| Offered remedies | downgrades only: `newman@5.3.2`, `htmlextra@1.22.11`, `@usebruno/cli@4.1.0` |
| `npm install --dry-run` | `up to date in 2s`, no `ERESOLVE` |
| `csv-parse` override `7.0.3` | resolves cleanly; does **not** block the tree |

### The actual blocker
`npm audit fix --force` cannot converge because it is being asked to reach a state that does
not exist: for each residual advisory the newest non-vulnerable version is *older* than the
installed one. Following the advice would downgrade `newman` to `5.3.2`, reinstating the
`postman-runtime`/`postman-collection`/`node-forge` advisories this manifest was upgraded to
clear. The command is therefore structurally circular on this manifest, not merely failing.

Residuals arrive via two chains:
1. `newman` → `postman-runtime` / `postman-collection` / `postman-sandbox` / `node-forge`
2. `@usebruno/cli` → `@usebruno/js` / `@usebruno/requests` / `axios` / `js-yaml` / `form-data` /
   `@usebruno/filestore` / `@usebruno/converters` / `yaml` / `@faker-js/faker`
3. `newman-reporter-htmlextra` → `@budibase/handlebars-helpers` / `micromatch` / `braces`

### Corrections to earlier conclusions in this investigation
Recorded because the design must not carry forward disproven claims:
- "`--force` left the tree broken / packages deleted" — **false**; the observed absence was a
  transient mid-install snapshot. The final state was correct.
- "`lodash@4.18.1` does not exist" — **false**; it exists and is the current latest.
- "the `csv-parse` override contradicts `newman@6`'s pin and blocks resolution" — **false**;
  `overrides` legitimately supersede transitive pins and the tree resolves without error.
- "the change `modernize-package-replacements-and-dead-weight` is in flight and owns the
  manifest" — **superseded**; that change completed and was archived at `895aacd9`.

### Concurrent-writer finding
The manifest was rewritten at `2026-10-04 09:01:18` by the then-active
`modernize-package-replacements-and-dead-weight` change. Three other agent sessions were live
in `~/Developer` during this investigation. Per the store's `openspec-runtime-governance`
requirement "Dirty-state and ownership preflight", ownership was resolved by direct
interrogation of each session before any write; two disclaimed the file and the third
identified the archived owner. No write was made to the manifest or lockfile.

## Goals / Non-Goals

**Goals:**
- Record the 19 residuals by identity and chain.
- Record the downgrade-only evidence establishing unpatched-upstream status.
- Record the `$HOME`-manifest footgun.

**Non-Goals:**
- Any manifest version change; every direct dependency is already latest.
- Applying any downgrade.
- Repeating the archived upgrades.

## Decisions

### Decision 1: Record residue; apply nothing
- **Rationale**: Existing spec requirement "Unpatched Upstream Residual Documentation" already
  forbids unvetted monkey-patches and breaking downgrades. Applying the audit's downgrade would
  directly violate that requirement *and* reintroduce cleared advisories.
- **Reference to existing pattern**: Mirrors how `mcp-router`'s 4 no-fix residuals
  (`image-size`, `extract-zip`, `patched: <0.0.0>`) were handled in the same capability.

### Decision 2: Classify by "downgrade-only" rather than by count
- **Rationale**: The `verify-npm-audit-remediation` spec explicitly requires residuals be
  "identified, not just counted" and warns that a delta must be explained as an
  unpatched-upstream residual or newly published advisory. A downgrade-only remedy is the
  mechanical signal of the former.
- **Transaction boundary**: evidence is written only from command output read back from disk
  after the final `npm audit`, never from the planning text.

### Decision 3: No manifest write at all
- **Rationale**: The governing spec's peer-conflict requirement is already satisfied
  (`newman@^6.2.2` declared and installed). There is nothing left to change, and the manifest is
  contended by other sessions, so a read-only change is both sufficient and safest.

## Risks / Trade-offs

- **Risk: 19 open advisories remain** → *Accepted and documented*. No upstream fix exists at
  this time; the record enables re-checking when upstream publishes.
- **Risk: a future session re-runs `--force` and silently downgrades** → *Mitigation*: the
  evidence records the circularity explicitly, and the spec adds a non-convergence scenario.
- **Risk: the `$HOME` manifest remains a footgun for every `npm`/`npx` call under `$HOME`** →
  *Mitigation*: recorded in evidence; removal raised as a separate hygiene decision, not bundled.
