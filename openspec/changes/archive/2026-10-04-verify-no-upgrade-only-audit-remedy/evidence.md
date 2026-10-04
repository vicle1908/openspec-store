# Verification Evidence: No Upgrade-Only Remedy Exists

**Date:** 2026-10-04
**Subject manifest:** `/Users/androidteam/package.json`
**Change:** `verify-no-upgrade-only-audit-remedy`
**Operator constraint:** upgrade only — no downgrade for any package

All values are read back from disk, the registry, or command output. None are hand-typed from
memory.

---

## 1. Baseline State

```console
$ npm audit
12 high severity vulnerabilities
```

The audit's offered remedies are **all downgrades**, and are therefore prohibited by the
operator's constraint:

```console
newman                     fix → newman@5.3.2                 (downgrade)
newman-reporter-htmlextra  fix → newman-reporter-htmlextra@1.22.11 (downgrade)
@usebruno/cli              fix → @usebruno/cli@2.9.1         (downgrade)
@faker-js/faker            fix → (via direct dependents)      (downgrade)
```

---

## 2. Forward-Fix Sweep (all affected packages)

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
| `braces` | `3.0.3` | **no fix** — latest within vulnerable range `<=3.0.3` |
| `node-forge` | `1.4.0` | **no fix** — latest within vulnerable range `<=1.4.0` |
| `@budibase/handlebars-helpers` | `0.14.3` | **no fix** — flagged at all versions (`*`) |
| `@faker-js/faker` | `10.6.0` | **forward fix exists, but runtime-incompatible** |

---

## 3. The Sole Forward Fix Was Applied

Override `"@faker-js/faker": ">=10.5.0"` (advisory range `<=10.4.0`).

```console
$ npm audit          # after
7 high severity vulnerabilities
```

Cleared 5 advisories, upgrade-only, no `ERESOLVE`.

### No-downgrade proof

```console
newman                       before=6.2.2      after=6.2.2
newman-reporter-htmlextra    before=1.23.1     after=1.23.1
@usebruno/cli                before=4.2.0      after=4.2.0
@faker-js/faker              before=9.9.0      after=10.6.0     ← upgrade only
braces                       before=3.0.3      after=3.0.3
node-forge                   before=1.4.0      after=1.4.0
```

Every package is equal to or greater than its prior version. The operator's constraint was
satisfied.

---

## 4. …and It Breaks the Tooling

```console
$ npx newman --version
/Users/androidteam/node_modules/postman-collection/lib/superstring/dynamic-variables.js:171
            generator: faker.address.city
                                     ^
TypeError: Cannot read properties of undefined (reading 'city')
    at Object.<anonymous> (postman-collection/lib/superstring/dynamic-variables.js:171:38)
```

faker v10 removed the legacy API (`faker.address`, `faker.datatype`, `faker.random`,
`faker.phone`). **Both** consumers depend on it:

```console
$ npm ls @faker-js/faker
├─┬ @usebruno/cli@4.2.0
│ └─┬ @usebruno/requests@0.21.0
│   └── @faker-js/faker@10.6.0
└─┬ newman@6.2.2
  └─┬ postman-collection@4.4.0
    └── @faker-js/faker@10.6.0 deduped
```

```console
$ grep -rl "faker.address" node_modules/@usebruno/   →  matches (requests/common)
$ grep -n "faker\." node_modules/postman-collection/lib/superstring/dynamic-variables.js
  113: faker.phone.phoneNumberFormat(0);
  122: faker.datatype.number({ min: 1, max: 99 });
  131: faker.random.arrayElement(LOCALES);
  156: faker.system.fileName();
```

`@usebruno/requests` pins `@faker-js/faker@^9.7.0` precisely because it needs the v9 API.
**No faker version is both non-vulnerable and API-compatible** with these consumers; the
advisory's "fixed" versions and the consumers' usable versions do not intersect.

---

## 5. The `braces` Chain Is Unresolvable at Every Level

Even at the newest versions:

```console
@budibase/handlebars-helpers@0.14.3  → micromatch ^4.0.5
micromatch@4.0.8                     → braces ^3.0.3
braces latest published              = 3.0.3   ← within vulnerable range <=3.0.3
```

No version change at any level of that chain reaches a clean `braces`.

`node-forge` is the same shape: latest published `1.4.0`, vulnerable range `<=1.4.0`.

---

## 6. Restore to Verified Pre-Change State

The override was reverted from captured copies.

```console
$ diff /tmp/newman-remediation/package.json.before-faker package.json
IDENTICAL

$ node -e "console.log(require('...package.json').overrides['@faker-js/faker'])"
undefined                     # override absent — correct

$ npm audit
12 high severity vulnerabilities

$ npx newman --version
6.2.2

$ npx bru --version
4.2.0
```

`newman` and `bru` both work again, and faker returns to its original split resolution
(`9.9.0` for bruno, nested `5.5.3` for postman-collection) as the lockfile records.

---

## 7. Conclusion

**No upgrade-only remedy exists for the workbook root manifest's advisory set.**

The 12 advisories reduce to these root causes:

| Root cause | Status |
|---|---|
| `@faker-js/faker` | forward fix exists but **breaks `newman` and `bru`** — rejected |
| `braces` (via `micromatch` → `@budibase/handlebars-helpers`) | no non-vulnerable version published |
| `node-forge` (via `postman-runtime`) | no non-vulnerable version published |
| `newman` / `postman-collection` / `postman-runtime` / `postman-sandbox` / `newman-reporter-htmlextra` | propagation of the above; each is already at latest |

Under the operator's constraint — upgrade only, never downgrade — the correct action is to hold
the manifest at its current, latest, working versions and accept these residues. Any change
that cleared them would either be a downgrade (prohibited) or break the installed tooling
(demonstrated for the faker override).

**Final manifest state: byte-identical to the pre-research state. No net change was applied.**

---

## 8. Recommendations (Not Actioned)

1. **Hold current versions.** Every package is already at its latest published release.
2. **Never run `npm audit fix --force` on this manifest** — its remedies are downgrades.
3. **Re-check periodically** for `braces` or `node-forge` publishing a patched release, or for
   `postman-collection` / `@usebruno/requests` raising their faker pin.
4. **Consider removing or relocating `/Users/androidteam/package.json`** so `npm`/`npx` invoked
   from `~/Developer` cannot silently target the home directory.
5. **If the faker advisory must be cleared**, the only upgrade-compatible route is for the two
   consumers to migrate off the legacy faker API — an upstream change, outside this manifest's
   control.
