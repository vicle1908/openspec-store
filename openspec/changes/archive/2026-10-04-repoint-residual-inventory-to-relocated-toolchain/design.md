# Design: Repoint the Residual Inventory to the Relocated Toolchain

## Context
See `proposal.md`. This completes the reconciliation started in
`reconcile-specs-with-home-manifest-removal`, which corrected the two requirements whose text made
live claims about the removed manifest. Two further requirements authored by the residual-recording
changes on the same day still name the removed path.

## Diagnosis (measured)

```console
$ grep -n '/Users/androidteam/package.json' openspec/specs/npm-audit-remediation/spec.md
214: The unpatched-upstream residual inventory SHALL cover `/Users/androidteam/package.json`
252: - WHEN a remediation proposal is authored for `/Users/androidteam/package.json`
266:   `/Users/androidteam/package.json`, resolving `@faker-js/faker` ...
330: - WHEN `/Users/androidteam/package.json` has been removed and `npm prefix` ...
```

| Line | Nature | Action |
|---|---|---|
| 214 | Live contract naming a removed path | MODIFY |
| 252 | Live contract naming a removed path | MODIFY |
| 266 | Scenario recording the rejected faker override, as it was tested | Keep |
| 330 | Correctly describes the removal | Keep |

Line 266 is a historical record of an experiment performed against the path as it then existed and
is intentionally preserved; rewriting it would falsify the evidence.

## Goals / Non-Goals

**Goals:**
- Remove the last live references to the removed manifest.
- Update the recorded residual total to the current measurement.

**Non-Goals:**
- Editing archived changes.
- Rewriting historical evidence scenarios.

## Decisions

### Decision 1: Preserve original header names and scenario names
- **Rationale**: `MODIFIED` replaces the whole requirement block and the store's validator refuses
  a delta that drops a scenario the current spec still has. Both the requirement headers and all
  existing scenario names are therefore carried forward verbatim, with only their content updated.
- **Reference to existing pattern**: The same constraint was encountered and resolved in
  `reconcile-specs-with-home-manifest-removal`.

### Decision 2: Correct the recorded total from 19 to 12
- **Rationale**: The inventory requirement records a figure of 19 vulnerabilities. Measurement after
  the `axios`/`js-yaml`/`yaml`/`form-data` overrides settled shows 12 high, rooted in
  `@faker-js/faker`, `braces`, and `node-forge`. Recording the stale figure would mislead triage.
- **Transaction boundary**: The figure is read from a fresh `npm audit` against the relocated
  manifest, not from prior text.

## Risks / Trade-offs

- **Risk: another session edits the same spec concurrently** → *Mitigation*: the spec was committed
  and its state re-read immediately before authoring this delta.
- **Risk: repeated `MODIFIED` blocks across changes confuse readers** → *Mitigation*: this is the
  second and final correction pass; after it, no live reference to the removed path remains.
