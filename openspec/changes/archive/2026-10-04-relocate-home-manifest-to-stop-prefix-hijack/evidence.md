# Verification Evidence: Relocate the Home-Directory Manifest

**Date:** 2026-10-04
**Change:** `relocate-home-manifest-to-stop-prefix-hijack`
**Goal:** Eliminate the `$HOME` npm prefix hijack while preserving all tooling.

All values are read back from disk or command output. None are hand-typed from memory.

---

## 1. The Hijack, Demonstrated Live (before)

The manifest at `/Users/androidteam/package.json` was adopted by npm for invocations made from
any directory beneath `$HOME` lacking its own manifest:

```console
$ cd /Users/androidteam/Developer && npm prefix
/Users/androidteam

$ cd /Users/androidteam/Developer && npx --no-install bru --version
npm notice run 'bru' --version
4.2.0
```

`bru` resolved through the home manifest although the command was issued in `~/Developer`.

---

## 2. Consumer Analysis Before Removing Anything

| Package | Home manifest | `~/.npm-global` (sanctioned) | On PATH |
|---|---|---|---|
| `gitnexus` | 1.6.12 | 1.6.12 | `~/.local/bin/gitnexus` |
| `@usebruno/cli` | 4.2.0 | — | — |
| `newman` | 6.2.2 | — | `/opt/homebrew/bin/newman` |
| `newman-reporter-htmlextra` | 1.23.1 | — | — |
| `pyright` | 1.1.414 | — | `/opt/homebrew/bin/pyright` |
| `yaml-language-server` | 1.24.0 | — | — |

**Unique to the home manifest:** `@usebruno/cli` (`bru`), `newman-reporter-htmlextra`,
`yaml-language-server`.
**Redundant there:** `newman` and `pyright` (Homebrew), `gitnexus` (`~/.npm-global` + `~/.local`).

The sanctioned global prefix is `~/.npm-global`, used by
`~/Developer/scripts/workstation-daily-update.sh`:

```console
$ sed -n '275,282p' ~/Developer/scripts/workstation-daily-update.sh
npm outdated -g --prefix "${HOME}/.npm-global" ...
npm install -g ${OUTDATED_PKGS} --prefix "${HOME}/.npm-global" ...
```

A search of `~/Developer/scripts` and `~/.agents/skills` for `bru` / `newman` /
`yaml-language-server` invocations returned none.

---

## 3. Relocation Built and Verified Before Removal

```console
$ mkdir -p ~/.local/share/home-toolchain && cp package.json package-lock.json ~/.local/share/home-toolchain/
$ cd ~/.local/share/home-toolchain && npm install
added 820 packages in 21s
```

### Tools functional at the new location

```console
bru                        4.2.0
yaml-language-server       1.24.0
newman-reporter-htmlextra  1.23.1
```

### Audit identical to the original

```console
12 high severity vulnerabilities
```

### Faker split resolution preserved

```console
node_modules/@faker-js/faker -> 9.9.0
node_modules/postman-collection/node_modules/@faker-js/faker -> 5.5.3
```

### Manifest fidelity

```console
dependencies match: true
overrides match:    true      (20 overrides)
overall faithful:   true
```

---

## 4. Removal

```console
$ rm -f ~/package.json ~/package-lock.json
$ rm -rf ~/node_modules

$ ls ~/package.json ~/package-lock.json ~/node_modules
ls: /Users/androidteam/node_modules: No such file or directory
ls: /Users/androidteam/package-lock.json: No such file or directory
ls: /Users/androidteam/package.json: No such file or directory
```

---

## 5. Hijack Eliminated (after)

```console
from ~/Developer            -> /Users/androidteam/Developer
from ~/Developer/platform   -> /Users/androidteam/Developer/platform
from /tmp                   -> /private/tmp
```

`npm prefix` now resolves to the invoked directory in every case. Previously, the first two
reported `/Users/androidteam`.

---

## 6. Usability Preserved Without a Manifest in `$HOME`

Three symlinks were added to `~/.local/bin` (already on PATH), each pointing into the relocated
toolchain rather than relying on npm's implicit upward resolution:

```console
bru                       -> ../share/home-toolchain/node_modules/.bin/bru
yaml-language-server      -> ../share/home-toolchain/node_modules/.bin/yaml-language-server
newman-reporter-htmlextra -> ../share/home-toolchain/node_modules/.bin/newman-reporter-htmlextra
```

Each resolves and reports its version when invoked by name:

```console
bru                        4.2.0
yaml-language-server       1.24.0
newman-reporter-htmlextra  1.23.1
```

---

## 7. Unrelated Installations Untouched

```console
$ gitnexus --version
1.6.12                     # unchanged

$ ls ~/.npm-global/lib/node_modules/ | wc -l
30                         # unchanged; sanctioned global prefix intact
```

No repository under `~/Developer` was modified by this change.

---

## 8. Disk Reclaimed

| Location | Size |
|---|---|
| `~/node_modules` (removed) | **3.1 GB** |
| `~/.local/share/home-toolchain` (new) | 1.4 GB |

Net reclaim: ~1.7 GB, because the fresh install deduplicates trees the old one duplicated.

---

## 9. Reversibility

The relocation is reversible: the original manifest and lockfile were preserved at the
relocation target and verified faithful (`dependencies match: true`, `overrides match: true`),
and the pre-state was recorded at `/tmp/newman-remediation/package.json.before-faker`. Restoring
the old layout is a copy-back plus `npm install`.

---

## 10. Outstanding State (unchanged and expected)

The relocated toolchain reports the same **12 high** advisories, established by
`verify-no-upgrade-only-audit-remedy` as irreducible under an upgrade-only constraint. This
change deliberately did not alter any version.

**Remaining recommendation:** if the faker advisory must ever be cleared, the only
upgrade-compatible route is for `postman-collection` and `@usebruno/requests` to migrate off
the legacy faker API — an upstream change outside this workspace's control.
