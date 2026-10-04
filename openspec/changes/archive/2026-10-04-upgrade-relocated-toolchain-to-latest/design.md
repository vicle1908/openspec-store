# Design: Upgrade the Relocated Toolchain to the Latest Permitted Versions

## Context
See `proposal.md`. The operator asked to upgrade to latest wherever possible. All direct
dependencies were already at latest, so the remaining levers were transitive refresh within
declared ranges and upgrade-only overrides for exact-pinned stragglers.

## Findings (measured)

### Direct dependencies — already at latest (no action possible)
| Package | Installed | Latest |
|---|---|---|
| `gitnexus` | 1.6.12 | 1.6.12 |
| `@usebruno/cli` | 4.2.0 | 4.2.0 |
| `newman` | 6.2.2 | 6.2.2 |
| `newman-reporter-htmlextra` | 1.23.1 | 1.23.1 |
| `pyright` | 1.1.414 | 1.1.414 |
| `yaml-language-server` | 1.24.0 | 1.24.0 |

### Transitive refresh applied by `npm update`
24 in-range upgrades were applied, 20 net version increases, including
`@hono/node-server` 1.19.17 → 2.1.3, `@modelcontextprotocol/sdk` 1.30.0 → 1.32.0,
`picomatch` 2.3.2 → 4.0.7, `zod` 4.5.1 → 4.6.5, `yaml` 2.8.3 → 2.9.1, and
`@types/node` 25.9.8 → 26.6.4.

### Apparent downgrades were hoisting relocations, not regressions
Some top-level slots dropped after `npm update` while the higher version remained present deeper
in the tree:

```console
BEFORE: node_modules/chalk@4.1.2          + node_modules/@usebruno/cli/node_modules/chalk@3.0.0
AFTER:  node_modules/chalk@3.0.0          + node_modules/newman-reporter-htmlextra/node_modules/chalk@4.1.2
```

A name@version diff confirmed only 16 versions disappeared, and each was replaced by its own
newer version. No package version was genuinely lowered.

### Exact-pinned stragglers raised by override
Range resolution could not move two packages:
- `aws4` — reachable only via `aws4@"^1.12.0"`, yet `npm update` left `1.12.0`
- `extsprintf` — exact-pinned at `1.3.0` by `jsprim@2.0.2`

Both were raised in the allowed direction via `overrides`:
`"aws4": ">=1.13.2"` → `1.13.2`, `"extsprintf": ">=1.4.1"` → `1.4.1`.

### Result
```console
$ npm outdated --all        # in-range moves remaining
(empty)

$ npm outdated              # direct deps behind latest
(empty)
```
All 22 `overrides` pins resolve to the latest published version of their package.

### The residual set is untouched, and cannot be touched
`npm audit` remains at 12 high. The three roots each have no reachable clean version:

| Root | Advisory range | Latest published |
|---|---|---|
| `braces` | `<=3.0.3` | `3.0.3` |
| `node-forge` | `<=1.4.0` | `1.4.0` |
| `@faker-js/faker` | `<=10.4.0` | `10.6.0` (but breaks `newman` + `bru`) |

No upgrade moves these, which is why the refresh cannot reduce the count.

## Goals / Non-Goals

**Goals:**
- Raise every dependency that any upgrade can raise.
- Prove nothing was downgraded.
- Confirm tools still function and the residual set is understood.

**Non-Goals:**
- Any downgrade.
- Clearing the 12 residuals.
- Removing dependencies.

## Decisions

### Decision 1: `npm update` for in-range refresh, not `npm audit fix`
- **Rationale**: `npm update` respects declared semver ranges and never proposes downgrades.
  `npm audit fix --force` proposes only downgrades here and is prohibited.
- **Reference to existing pattern**: Consistent with the upgrade-only constraint already
  established for this manifest.

### Decision 2: Upgrade-only overrides for the two exact-pinned stragglers
- **Rationale**: `extsprintf` is pinned to an exact version by its parent, so only an override can
  move it. Both overrides use floor or exact-but-newer syntax, never a lower version.
- **Transaction boundary**: The pre-change manifest and lockfile were captured to
  `/tmp/hometoolchain-*.before-upgrade` for rollback.

### Decision 3: Accept that the audit count is unchanged
- **Rationale**: The count is governed by packages whose latest published version is inside the
  advisory range. The upgrade work is still correct and worth recording; conflating "upgraded to
  latest" with "audit reduced" would misreport the outcome.

## Risks / Trade-offs

- **Risk: `npm update` re-hoisting a package into a slot a consumer cannot use** →
  *Mitigation*: tools were re-executed after the refresh and the name@version diff was checked for
  genuine losses.
- **Risk: a major-version transitive bump (e.g. `@hono/node-server` 1.x → 2.x) breaks a consumer**
  → *Mitigation*: the bump occurred because a parent's declared range permitted it; all CLI entry
  points were verified to execute after the refresh.
