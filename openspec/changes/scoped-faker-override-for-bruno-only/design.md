# Design: Scoped Faker Override for the Bruno Consumer Only

## Context
See `proposal.md`. A prior change concluded the `@faker-js/faker` advisory was unreachable by
upgrade. That conclusion was correct for the global override but over-general: the two consumers
of faker have different compatibility, so a scoped override reaches one of them safely.

## Findings (measured)

### Two consumers, two faker copies
```console
$ node -e "resolve '@faker-js/faker' from each consumer"
postman-collection   -> node_modules/postman-collection/node_modules/@faker-js/faker  (5.5.3)
@usebruno/requests   -> node_modules/@faker-js/faker                                 (9.9.0 → 10.6.0)
```

`postman-collection` requires `@faker-js/faker/locale/en` and uses the **legacy API**
(`faker.address.city`, `faker.datatype`, `faker.random`, `faker.phone`), removed in faker v10.
`@usebruno/requests` declares `@faker-js/faker@^9.7.0` but **bundles its own faker internally**,
so the npm-level resolution under it does not govern its runtime behaviour.

### Scoping ladder, each tested
| Scope applied | Audit | Outcome |
|---|---|---|
| none (baseline) | 12 high | — |
| global `@faker-js/faker` | 7 high | **breaks `newman`** — rejected |
| `"@usebruno/requests": { faker >=10.5.0 }` | **10 high** | **safe — retained** |
| `"postman-collection": { faker >=10.5.0 }` | 7 high | **breaks `postman-collection`** — rejected |

The safe maximum is the Bruno-only scope: it clears the `@faker-js/faker`,
`@usebruno/cli`, and `@usebruno/requests` advisories without touching the consumer that needs
the legacy API.

### Parent upgrades cannot substitute
Every candidate parent was raised to latest in a sandbox
(`postman-collection@5.3.1`, `postman-runtime@7.56.1`, `postman-sandbox@6.7.4`,
`@budibase/handlebars-helpers@0.14.3`) and the audit remained at 12, because the latest
parents still pin the vulnerable versions:

```console
postman-collection@5.3.1 (latest)  -> @faker-js/faker 5.5.3
postman-runtime@7.56.1   (latest)  -> node-forge 1.4.0
micromatch@4.0.8         (latest)  -> braces ^3.0.3
```

### The remaining two roots are genuinely unreachable
```console
braces      newest published 3.0.3, advisory range <=3.0.3
node-forge  newest published 1.4.0, advisory range <=1.4.0
```
No published version of either lies outside its advisory range, so no override, parent upgrade,
or dependency substitution can clear them.

## Goals / Non-Goals

**Goals:**
- Clear every advisory that scoping can clear without breaking a consumer.
- Prove the retained scope does not break either consumer.
- Verify no downgrade.

**Non-Goals:**
- A global faker override (rejected, breaks `newman`).
- The `postman-collection` scope (rejected, breaks that package).
- Clearing `braces`/`node-forge` (no clean version exists).
- Removing dependencies.

## Decisions

### Decision 1: Scope the override to the tolerant consumer
- **Rationale**: The advisory is on a shared transitive package, but only one consumer requires
  the vulnerable API. npm's nested-`overrides` form lets the incompatible consumer keep its
  compatible version. This satisfies the upgrade-only constraint and clears 2 advisories.
- **Reference to existing pattern**: Continues the same capability's scoped/nested override
  precedent (the dual `overrides`/`pnpm.overrides` parity already governing `realtime/frontend`).

### Decision 2: Prove the boundary by testing the rejected deeper scope
- **Rationale**: Asserting "Bruno-only is safe" is weaker than demonstrating that the next scope
  inwards breaks. The `postman-collection` scope was applied, observed to reach 7 but fail to
  load, and discarded — establishing 10 as the true maximum rather than an arbitrary stopping
  point.
- **Transaction boundary**: Each scope was tested in an isolated sandbox before touching the real
  manifest; pre-change manifest and lockfile were captured for rollback.

### Decision 3: Verify the consumer entry point, not just the version flag
- **Rationale**: The earlier rejected global override was not caught by `--version` alone for the
  library case; `faker.address` is only reached at call time. Both `bru --help` and a direct
  `require` of `postman-collection`'s `dynamic-variables` module were exercised, since the latter
  is the module that actually dereferences `faker.address.city`.

## Risks / Trade-offs

- **Risk: `@usebruno/requests` might reach the top-level faker rather than its bundled copy** →
  *Mitigation*: inspected its dist output; the `faker.address` references resolve to identifiers
  within its own bundled code, and `bru --help` executes successfully under the scoped override.
- **Risk: a future `@usebruno/requests` release relies on the npm-level faker** →
  *Mitigation*: the override is a floor (`>=10.5.0`), so a future release requiring faker ≥10
  remains satisfied.
- **Risk: the scoped override silently masks a real incompatibility** → *Mitigation*: the
  `postman-collection` scope was tested and rejected, so the retained scope is the measured
  maximum rather than an unexamined choice.
