# Design: Reconcile Specs With the Removal of the Home Directory Manifest

## Context
See `proposal.md`. The migration in `relocate-home-manifest-to-stop-prefix-hijack` removed
`/Users/androidteam/package.json`. Two requirements authored by the earlier archived change
`2026-09-21-remediate-npm-audit-vulnerabilities` still reference that path in the present tense,
so the canonical spec now asserts something the machine contradicts.

## Diagnosis (measured)

```console
$ grep -n '/Users/androidteam/package.json' openspec/specs/npm-audit-remediation/spec.md
9:   ... SHALL resolve all peer dependency conflicts ... (`/Users/androidteam/package.json`)
12:  - WHEN `newman` is updated ... in `/Users/androidteam/package.json`
144: ... SHALL declare strict version overrides ... (`/Users/androidteam/package.json`)
147: - WHEN overrides ... are active in `/Users/androidteam/package.json`
173: The unpatched-upstream residual inventory SHALL cover `/Users/androidteam/package.json`
211: - WHEN a remediation proposal is authored for `/Users/androidteam/package.json`
225:   `/Users/androidteam/package.json`, resolving `@faker-js/faker` ...
289: - WHEN `/Users/androidteam/package.json` has been removed ...
```

Classification of the eight occurrences:

| Lines | Nature | Action |
|---|---|---|
| 9, 12 | **Stale present-tense assertion** — the file no longer exists | MODIFY |
| 144, 147 | **Stale present-tense assertion** and an unachievable "zero vulnerabilities" claim | MODIFY |
| 173, 211, 225 | Historical references inside evidence-type scenarios, describing what was recorded | Keep |
| 289 | Correctly describes the removal | Keep |

The `verify-npm-audit-remediation` spec references the path once, in a sentence describing what
the 2026-09-20 session covered. That is a historical statement, not a live contract, and is left
unchanged.

## Goals / Non-Goals

**Goals:**
- Remove the contradiction between the spec and the verified machine state.
- Correct the unachievable "zero non-residual vulnerabilities" claim for the Bruno chain.
- Preserve the audit trail by not editing archived changes.

**Non-Goals:**
- Editing `2026-09-21-remediate-npm-audit-vulnerabilities` or any archived directory.
- Restoring a manifest to `$HOME`.
- Rewriting requirements whose path references are correctly historical.

## Decisions

### Decision 1: Reconcile via a new change rather than editing the archive
- **Rationale**: The store's archive rule states archived change directories are immutable and
  that corrective work is written to a new active change. The stale text lives in the main spec,
  which is mutable — but its authorship belongs to an archived change, so the correction is
  recorded as its own change for traceability.
- **Reference to existing pattern**: Matches the store's documented convention for corrective
  evidence and corrections.

### Decision 2: Re-scope rather than delete the two requirements
- **Rationale**: The peer-conflict and override-hardening contracts remain valuable; only their
  subject path is wrong. Deleting them would lose governance of the relocated toolchain, which
  is the same dependency set under a new location.

### Decision 3: Correct the "zero non-residual vulnerabilities" claim
- **Rationale**: The original scenario asserted the Bruno chain would report zero vulnerabilities.
  Measurement showed `@faker-js/faker` cannot be raised without breaking `newman` and `bru`,
  independently corroborated by `bun audit fix` reporting the upgrade as "blocked by a
  dependent's range". Leaving the claim would make the spec unachievable and invite a future
  session to repeat the rejected override.

## Risks / Trade-offs

- **Risk: re-scoping loses the historical record of the original path** → *Mitigation*: the
  archived change retains the original text, and this change's evidence records the before/after.
- **Risk: another session edits the same spec concurrently** → *Mitigation*: the store is
  committed and the working tree was verified clean for this file before editing.
