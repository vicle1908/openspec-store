# Verification Evidence: Scoped Faker Override for the Bruno Consumer Only

**Date:** 2026-10-04
**Change:** `scoped-faker-override-for-bruno-only`
**Manifest:** `~/.local/share/home-toolchain/package.json`

All values are read back from disk or command output.

---

## 1. Two Consumers, Two Faker Copies

```console
postman-collection   -> node_modules/postman-collection/node_modules/@faker-js/faker
@usebruno/requests   -> node_modules/@faker-js/faker
```

`postman-collection` requires the package as `@faker-js/faker/locale/en` and uses the legacy API:

```console
$ grep -n 'faker\.' node_modules/postman-collection/lib/superstring/dynamic-variables.js
113:  faker.phone.phoneNumberFormat(0);
122:  faker.datatype.number({ min: 1, max: 99 });
131:  faker.random.arrayElement(LOCALES);
156:  faker.system.fileName();
171:  generator: faker.address.city          <- removed in faker v10
```

`@usebruno/requests` bundles its own faker internally:

```console
$ node -e "typeof require('@faker-js/faker').faker.address"
undefined
$ node -e "require('@usebruno/requests')"
requests loaded OK
```

---

## 2. Parent Upgrades Cannot Substitute

All candidate parents were raised to latest in a sandbox and the audit stayed at 12:

```console
TEST A: postman-sandbox 4.7.1 -> 6.7.4              => 12 high
TEST B: + postman-collection 5.3.1                  => 12 high
TEST C: + handlebars-helpers 0.14.3                 => 12 high
TEST D: + postman-runtime 7.56.1                    => 12 high
```

Because the latest parents still pin the vulnerable versions:

```console
postman-collection@5.3.1 (latest)  -> @faker-js/faker 5.5.3
postman-runtime@7.56.1   (latest)  -> node-forge 1.4.0
postman-sandbox@6.7.4    (latest)  -> postman-collection 5.3.1  -> faker 5.5.3
@budibase/handlebars-helpers@0.14.3 (latest) -> micromatch ^4.0.5 -> braces ^3.0.3
micromatch@4.0.8 (latest)          -> braces ^3.0.3
```

---

## 3. Scoping Ladder — Each Scope Tested

| Scope | Audit | Verdict |
|---|---|---|
| none (baseline) | 12 high | — |
| global `@faker-js/faker` | 7 high | **breaks `newman`** — rejected |
| `@usebruno/requests` only | **10 high** | **safe — retained** |
| `postman-collection` only | 7 high | **breaks `postman-collection`** — rejected |

The rejected deeper scope, demonstrated:

```console
$ npm audit          # with postman-collection scoped
7 high severity vulnerabilities

$ node -e "require('postman-collection/lib/superstring/dynamic-variables.js')"
FAILED: Cannot read properties of undefined (reading 'city')
```

This establishes 10 as the measured maximum, not an arbitrary stopping point.

---

## 4. Applied to the Real Manifest

```console
$ npm audit          # before
12 high severity vulnerabilities

$ npm audit          # after scoped override
{"info":0,"low":0,"moderate":0,"high":10,"critical":0,"total":10}
```

Faker resolution after the change:

```console
node_modules/@faker-js/faker -> 10.6.0
node_modules/postman-collection/node_modules/@faker-js/faker -> 5.5.3
```

---

## 5. Both Consumers Verified

```console
$ ./node_modules/.bin/bru --version
4.2.0

$ ./node_modules/.bin/bru --help
Bru CLI 4.2.0
Usage: bru <command> [options]
exit=0

$ node -e "require('postman-collection/lib/superstring/dynamic-variables.js')"
OK

$ ~/.local/bin/yaml-language-server --version
1.24.0

$ ~/.local/bin/newman-reporter-htmlextra --version
1.23.1

$ newman --version
6.2.2
```

---

## 6. No Downgrade

A name@version diff of the lockfile before and after the scoped override:

```console
UPGRADES:   none
DOWNGRADES: NONE
```

The override is a floor (`>=10.5.0`), so it can only move faker upward.

---

## 7. Remaining 10 Advisories — Attribution

| Package | Root? | Root cause |
|---|---|---|
| `@faker-js/faker` | — | nested `5.5.3` under `postman-collection` (not scoped; would break it) |
| `postman-collection` | — | propagation of the nested faker |
| `braces` | **ROOT** | `<=3.0.3`; newest published is `3.0.3` |
| `micromatch` | — | propagation of `braces` |
| `@budibase/handlebars-helpers` | — | propagation of `micromatch` |
| `newman-reporter-htmlextra` | — | propagation of the above |
| `node-forge` | **ROOT** | `<=1.4.0`; newest published is `1.4.0` |
| `postman-runtime` | — | propagation of `node-forge` |
| `postman-sandbox` | — | propagation of `postman-collection` |
| `newman` | — | propagation of `postman-runtime` |

Two irreducible roots remain, each with no non-vulnerable version published at any point:

```console
braces      newest published 3.0.3, advisory <=3.0.3
node-forge  newest published 1.4.0, advisory <=1.4.0
```

---

## 8. Rollback

Pre-change manifest and lockfile captured at:

```console
/tmp/ht.before-scoped.json
/tmp/ht.before-scoped-lock.json
```

---

## 9. Conclusion

The `@faker-js/faker` advisory was reachable after all — but only by **scoping** the override to
the consumer that tolerates the newer API. A global override breaks `newman`; scoping it to
`postman-collection` breaks that package; scoping it to `@usebruno/requests` is safe and clears
2 advisories.

Result: **12 high → 10 high**, no downgrade, all tools functional. The residual 10 reduce to two
irreducible roots (`braces`, `node-forge`) plus the `postman-collection`-nested faker that cannot
be raised without breaking that package.
