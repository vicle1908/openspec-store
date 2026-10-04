# Verification Evidence: Record Unpatched-Upstream Advisory Residue

**Date:** 2026-10-04
**Subject manifest:** `/Users/androidteam/package.json` (workstation root tooling manifest, not a git repository)
**Change:** `record-workstation-unpatched-audit-residue`

All values below are programmatically read back from disk, the registry, or command output —
none are hand-typed from memory.

---

## 1. The `$HOME` Manifest Footgun

```console
$ cd /Users/androidteam/Developer && npm prefix
/Users/androidteam

$ cd /Users/androidteam/Developer && ls package.json
ls: package.json: No such file or directory
```

`npm prefix` resolves to `/Users/androidteam` from `~/Developer` because that directory has no
`package.json` of its own. The original `npm audit fix --force` therefore operated on the
`$HOME` manifest, not on any repository. **A `package.json` in `$HOME` silently captures every
`npm`/`npx` invocation made from any directory beneath `$HOME` that lacks its own manifest.**
Dependency commands MUST be issued from the owning repository root.

---

## 2. Direct Dependencies Are Already at Latest

```console
newman: installed=6.2.2 latest=6.2.2
newman-reporter-htmlextra: installed=1.23.1 latest=1.23.1
@usebruno/cli: installed=4.2.0 latest=4.2.0
```

```console
$ npm ls --depth=0
androidteam@ /Users/androidteam
├── @usebruno/cli@4.2.0
├── gitnexus@1.6.12
├── newman-reporter-htmlextra@1.23.1
├── newman@6.2.2
├── pyright@1.1.414
└── yaml-language-server@1.24.0
```

Every direct dependency is at the latest published version. There is no upgrade available.

---

## 3. Audit Result

```console
totals: {"info":0,"low":0,"moderate":2,"high":17,"critical":0,"total":19}
```

19 vulnerabilities (2 moderate, 17 high).

---

## 4. The Offered Remedies Are Downgrades (Non-Convergence Proof)

```console
newman                     range >=6.0.0      fix → newman@5.3.2                    (downgrade)
newman-reporter-htmlextra  range >=1.22.6     fix → newman-reporter-htmlextra@1.22.11 (downgrade)
@usebruno/cli              range >=2.10.0     fix → @usebruno/cli@4.1.0             (downgrade)
```

For each direct dependency, the newest non-vulnerable version the audit proposes is **older**
than the installed version. Following the advice would downgrade `newman` to `5.3.2`,
reinstating the `postman-runtime` / `postman-collection` / `node-forge` advisories this
manifest was upgraded to clear.

**Conclusion:** `npm audit fix --force` is structurally non-convergent on this manifest. It is
not "failing"; it is being asked to reach a state that does not exist upstream.

---

## 5. Resolution Is Not Broken

```console
$ npm install --dry-run
up to date in 455ms
146 packages are looking for funding
run `npm fund` for details
```

No `ERESOLVE`. In particular the `csv-parse` override at `7.0.3` does **not** block the tree;
`overrides` legitimately supersede a parent's pinned transitive dependency. This disproves the
earlier hypothesis that an override/pin contradiction blocked resolution.

---

## 6. Residual Advisory Identity Inventory

| Package | Severity | Direct | Vulnerable range | Reached via |
|---|---|---|---|---|
| `@budibase/handlebars-helpers` | high | false | `*` | newman-reporter-htmlextra |
| `@faker-js/faker` | high | false | `<=10.4.0` | @usebruno/requests, postman-collection |
| `@usebruno/cli` | high | true | `>=2.10.0` | — |
| `@usebruno/converters` | high | false | `>=0.24.0` | @usebruno/cli |
| `@usebruno/filestore` | moderate | false | `>=0.13.0` | @usebruno/cli |
| `@usebruno/js` | high | false | `>=0.49.0` | @usebruno/cli |
| `@usebruno/requests` | high | false | `>=0.8.0` | @usebruno/cli |
| `axios` | high | false | `1.0.0 - 1.19.0` | @usebruno/cli, @usebruno/js, @usebruno/requests |
| `braces` | high | false | `*` | micromatch |
| `form-data` | high | false | `4.0.0 - 4.0.5` | @usebruno/cli |
| `js-yaml` | high | false | `4.0.0 - 4.3.1` | @usebruno/cli, @usebruno/converters |
| `micromatch` | high | false | `>=0.2.0` | @budibase/handlebars-helpers |
| `newman` | high | true | `>=6.0.0` | newman-reporter-htmlextra |
| `newman-reporter-htmlextra` | high | true | `>=1.22.6` | — |
| `node-forge` | high | false | `*` | postman-runtime |
| `postman-collection` | high | false | `>=4.1.2` | newman, postman-runtime, postman-sandbox |
| `postman-runtime` | high | false | `6.4.2 - 7.0.0-beta.2 \|\| 7.4.0-beta.1 - 7.4.0 \|\| >=7.29.1` | newman |
| `postman-sandbox` | high | false | `>=4.1.2` | postman-runtime |
| `yaml` | moderate | false | `2.0.0 - 2.8.2` | @usebruno/filestore, @usebruno/js |

### Contributing chains
1. `newman` → `postman-runtime` / `postman-collection` / `postman-sandbox` / `node-forge`
2. `@usebruno/cli` → `@usebruno/js` / `@usebruno/requests` / `axios` / `js-yaml` / `form-data` /
   `@usebruno/filestore` / `@usebruno/converters` / `yaml` / `@faker-js/faker`
3. `newman-reporter-htmlextra` → `@budibase/handlebars-helpers` / `micromatch` / `braces`

### Classification
All 19 are classified **unpatched-upstream** on the evidence of §4: their only offered remedy
is a downgrade, and their owning direct dependencies are already at their latest published
versions (§2). None is a remediation regression.

A non-zero `npm audit` exit status caused by these residuals is recorded as an
unpatched-upstream condition, **not** as a failure of this change.

---

## 7. Prior Art: The Upgrades Were Already Performed and Archived

The dependency upgrades this investigation originally proposed were executed and archived
earlier the same day:

- `modernize-package-replacements-and-dead-weight` — archived, commit `895aacd9`
  ("chore(archive): archive modernize-package-replacements-and-dead-weight — sync delta to
  npm-audit-remediation"). Added `@usebruno/cli@^4.2.0`; recorded `newman --version` → `6.2.2`.
- `modernize-toolchain-and-major-dependencies` — archived, commit `b2453c16`, synced into the
  same `npm-audit-remediation` spec.

The mutation of the manifest detected at `2026-10-04 09:01:18` was that change's execution.

---

## 8. Corrections to Earlier Findings

Recorded so disproven claims are not carried forward:

| Earlier claim | Status | Disproof |
|---|---|---|
| `--force` left `newman`/`htmlextra` deleted | **false** | transient mid-install snapshot; final state `newman@6.2.2` + `htmlextra@1.23.1` present |
| `lodash@4.18.1` does not exist | **false** | `npm view lodash@4.18.1` → `4.18.1`; it is the current latest |
| the `csv-parse` override blocks resolution | **false** | `npm install --dry-run` → `up to date`, no `ERESOLVE` |
| `modernize-package-replacements-and-dead-weight` is in flight and owns the manifest | **superseded** | archived at `895aacd9` |

---

## 9. Concurrent-Writer Preflight

Three other agent sessions were live in `~/Developer` during this investigation. Per the
store's `openspec-runtime-governance` requirement *"Dirty-state and ownership preflight"*,
ownership of the manifest mutation was resolved by direct interrogation before any write:

- two sessions disclaimed ownership (with independently verifiable write-scopes);
- the third identified the archived change as the owner via commit `895aacd9`.

**No write was made to `/Users/androidteam/package.json` or its lockfile by this change.**

---

## 10. Recommendations (Not Actioned Here)

1. **Leave the 19 residuals open**; they are unpatched upstream. Re-check when `newman`,
   `newman-reporter-htmlextra`, or `@usebruno/cli` publish newer releases.
2. **Never run `npm audit fix --force` on this manifest** — it is non-convergent and would
   downgrade `newman` to a vulnerable version.
3. **Consider removing `/Users/androidteam/package.json`** or relocating its tooling, so
   `npm`/`npx` invoked from `~/Developer` cannot silently target it. Separate hygiene decision.
4. **Run dependency commands from the owning repository root**, never from `~/Developer`.
