# Design: Verified Absence of an Upgrade-Only Remedy

## Context
See `proposal.md`. The operator's constraint is decisive: clear the advisories by **upgrade
only, never downgrade**. This change records what that constraint permits, by testing the
candidate forward fixes rather than asserting their absence.

## Research Findings (measured)

### Forward-fix sweep across all affected packages

| Package | Latest published | Verdict |
|---|---|---|
| `newman` | `6.2.2` | latest already selected |
| `newman-reporter-htmlextra` | `1.23.1` | latest already selected |
| `@usebruno/cli` | `4.2.0` | latest already selected |
| `@usebruno/requests` | `0.21.0` | latest already selected |
| `micromatch` | `4.0.8` | latest already selected |
| `postman-collection` | `5.3.1` | latest already selected |
| `postman-runtime` | `7.56.1` | latest already selected |
| `postman-sandbox` | `6.7.4` | latest already selected |
| `braces` | `3.0.3` | **no fix** — latest is within vulnerable range `<=3.0.3` |
| `node-forge` | `1.4.0` | **no fix** — latest is within vulnerable range `<=1.4.0` |
| `@budibase/handlebars-helpers` | `0.14.3` | **no fix** — flagged at all versions (`*`) |
| `@faker-js/faker` | `10.6.0` | **forward fix exists but is runtime-incompatible** |

### The one forward fix was tested and rejected

`@faker-js/faker` is vulnerable at `<=10.4.0` with clean versions `10.5.0`/`10.6.0` published,
so an override *does* clear the advisory. It was applied:

```console
before: 12 high (0 moderate)
after:   7 high (0 moderate)   ← 5 advisories cleared, upgrade-only, no downgrade
```

and the no-downgrade proof held exactly:

```console
@faker-js/faker  9.9.0 → 10.6.0   (upgrade)
newman, newman-reporter-htmlextra, @usebruno/cli, braces, node-forge  (unchanged)
```

**But it breaks the tooling.** `npx newman --version` then failed:

```console
TypeError: Cannot read properties of undefined (reading 'city')
    at postman-collection/lib/superstring/dynamic-variables.js:171  →  faker.address.city
```

faker v10 removed the legacy API (`faker.address`, `faker.datatype`, `faker.random`, `faker.phone`)
that **both** consumers rely on — `postman-collection` (via `newman`) and `@usebruno/requests`
(via `bru`, which pins `^9.7.0`). There is no faker version that is both non-vulnerable and
API-compatible with these consumers.

### The braces chain is unresolvable at every level

Even the newest `@budibase/handlebars-helpers@0.14.3` depends on `micromatch@^4.0.5`, which
depends on `braces@^3.0.3`, and `braces@3.0.3` is itself the latest published version within
the vulnerable range. No override at any level of that chain can reach a clean `braces`.

### Conclusion

**No upgrade-only remedy exists.** The 12 advisories reduce to root causes that are either
already at their latest published version, have no non-vulnerable version published at all, or
have a non-vulnerable version only at the cost of breaking the installed tooling. Under the
operator's constraint the correct action is to hold the manifest at its current working
versions and accept the residues — which is what this change does.

## Goals / Non-Goals

**Goals:**
- Establish, by measurement, whether an upgrade-only remedy exists.
- Prove the one candidate forward fix is incompatible, rather than leaving it assumed.
- Leave the manifest in its verified pre-research state.

**Non-Goals:**
- Any downgrade, for any package, at any point.
- Retaining a remedy that breaks tooling.
- Substituting unvetted forks of `braces`/`node-forge`.

## Decisions

### Decision 1: Test the forward fix in a sandbox, then on the real manifest, then revert
- **Rationale**: The faker override looked correct by the audit's own numbers and by the
  no-downgrade constraint. Only execution proved it breaks `newman`. The remedy was therefore
  applied, the breakage demonstrated, and the pre-change state restored from captured backups.
- **Reference to existing pattern**: Mirrors the sandbox-validation step already used for the
  upgrade-only override investigation earlier on this manifest.

### Decision 2: Attribute residues to root causes, not to node counts
- **Rationale**: 12 advisories are really a handful of roots (`braces`, `node-forge`,
  `@faker-js/faker`, `postman-*`/`newman`). Reporting the count alone invites a future session
  to re-attempt the same rejected remedy.
- **Transaction boundary**: The manifest was restored from captured copies and verified
  byte-identical; no residue of the experiment remains.

### Decision 3: Accept the residues under the operator's constraint
- **Rationale**: The governing capability forbids unvetted monkey-patches and breaking
  downgrades. Since the operator forbids downgrades and no compatible upgrade exists, the
  residue set is irreducible by construction and must be documented, not forced.

## Risks / Trade-offs

- **Risk: 12 advisories remain open** → *Accepted and documented*; no compliant remedy exists.
- **Risk: `--force` is attempted again and silently downgrades** → *Mitigation*: evidence
  records that the audit's offered remedies are all downgrades and are prohibited.
- **Risk: a future session re-applies the faker override and breaks `newman`** →
  *Mitigation*: the breakage is recorded as a rejected remedy with the exact `TypeError`, and
  the spec adds a compatibility gate requiring consumer-API validation before retention.
