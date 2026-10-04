# Verification Evidence: Reconcile Specs With the Removal of the Home Directory Manifest

**Date:** 2026-10-04
**Change:** `reconcile-specs-with-home-manifest-removal`

All values are read back from disk or command output.

---

## 1. The Contradiction Found

`relocate-home-manifest-to-stop-prefix-hijack` removed `/Users/androidteam/package.json`, but the
canonical spec still asserted its existence in the present tense:

```console
$ grep -n '/Users/androidteam/package.json' openspec/specs/npm-audit-remediation/spec.md
9:   ... SHALL resolve all peer dependency conflicts ... (`/Users/androidteam/package.json`)
12:  - WHEN `newman` is updated ... in `/Users/androidteam/package.json`
144: ... SHALL declare strict version overrides ... (`/Users/androidteam/package.json`)
147: - WHEN overrides ... are active in `/Users/androidteam/package.json`
```

Lines 9, 12, 144, and 147 were **live assertions** about a file that no longer exists. The
originating change was the archived `2026-09-21-remediate-npm-audit-vulnerabilities`.

---

## 2. Classification of All Eight References

| Lines | Nature | Action taken |
|---|---|---|
| 9, 12 | Live assertion about a removed file | MODIFIED → re-scoped to relocated toolchain |
| 144, 147 | Live assertion + unachievable "zero vulnerabilities" claim | MODIFIED → re-scoped, claim corrected |
| 173, 211, 225 | Historical references inside evidence-type scenarios | Left intact |
| 289 | Correctly describes the removal | Left intact |

`verify-npm-audit-remediation` references the path once, describing what the 2026-09-20 session
covered. That is historical, not a live contract; left unchanged.

---

## 3. A Second Defect Corrected

The original scenario claimed the override set would make `npm audit` "report zero non-residual
vulnerabilities" for the Bruno chain. Measurement showed this is unachievable:

- `@faker-js/faker` is pulled at `9.9.0` (via `@usebruno/requests`) and `5.5.3` (via
  `postman-collection`)
- raising it breaks `newman` and `bru` (faker v10 removed the legacy API)
- `bun audit fix` independently reports the upgrade as **"blocked by a dependent's range"**

The modified requirement now records the residual rather than asserting it away.

---

## 4. Validator Caught Two Real Errors During Authoring

The OpenSpec validator rejected two intermediate drafts, each correctly:

```console
✗ MODIFIED failed for header "### Requirement: Relocated Toolchain Peer Conflict Resolution" - not found
```

`MODIFIED` requires the **exact existing header**; my first draft renamed it. Corrected by
preserving the original header names.

```console
✗ MODIFIED "Workstation Root Manifest Peer Conflict Resolution" omits scenario(s) the current
  spec still has: "newman and htmlextra peer alignment", "npm audit execution after upgrade"
```

`MODIFIED` replaces the whole block, so original scenarios must be carried forward. Corrected by
retaining both, with their content updated to the relocated path.

Final state:

```console
$ openspec validate reconcile-specs-with-home-manifest-removal --type change
Change 'reconcile-specs-with-home-manifest-removal' is valid
```

---

## 5. Archive Integrity Preserved

No file in any archived change directory was modified — verified by a clean
`git status --short openspec/changes/archive/`. The original text remains recoverable from
`2026-09-21-remediate-npm-audit-vulnerabilities`, satisfying the store's immutability rule that
corrections are written to a new active change.

---

## 6. Independent Corroboration (Latest Practice)

The residual analysis was independently reproduced by a different resolver. **Bun 1.4.2**
(current release) ships `bun audit fix` with an explicitly conservative policy: *"upgrades
vulnerable packages to the lowest safe version that still satisfies every dependent's range."*

```console
$ bun audit
3 vulnerabilities (3 high)
  @faker-js/faker@9.9.0, 5.5.3   GHSA-qxc2-j82w-r537  (<=10.4.0)
  braces@3.0.3                   GHSA-vfj7-8cjw-p6xm  (<=3.0.3)
  node-forge@1.4.0               GHSA-86w9-cpqp-85rv  (<=1.4.0)

$ bun audit fix
blocked by a dependent's range:
  ^ @faker-js/faker 5.5.3 -> 10.5.0   postman-collection@4.4.0 depends on @faker-js/faker@5.5.3
  ^ @faker-js/faker 9.9.0 -> 10.5.0   @usebruno/requests@0.21.0 depends on @faker-js/faker@^9.7.0
no published version fixes:
  braces@3.0.3  GHSA-vfj7-8cjw-p6xm
  node-forge@1.4.0  GHSA-86w9-cpqp-85rv
Fixed 0 of 3 vulnerabilities (checked 748)
```

Bun's verdict matches the npm-based analysis exactly on all three roots: one upgrade blocked by
consumer ranges, two with no published fix. **An independent implementation confirms no
upgrade-only remedy exists.**

---

## 7. Additional Latest-Practice Confirmations

| Practice | Finding |
|---|---|
| `npm audit fix --dry-run --json` before any fix | npm's own docs recommend this; the original incident skipped it |
| `bun audit fix` compatible-upgrade policy | Newer, more conservative than npm's `--force`; corroborates the finding |
| `pnpm` available (12.8.1) | Present for repos that prefer pnpm's stricter resolution |
| `node-forge` has no 2.x | Confirmed by enumerating all published versions: latest is `1.4.0` |
| `postman-collection@5.3.1` (latest) still pins faker `5.5.3` | Even a major upgrade of the parent would not clear the advisory |
| `postman-runtime@7.56.1` (latest) still pins `node-forge@1.4.0` | Same |

---

## 8. Final State

- Canonical spec assertions reconciled with the machine.
- All 437 specs validate.
- No archived change was modified.
- No live assertion of a `$HOME` manifest remains in the canonical spec.
