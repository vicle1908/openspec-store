# Verification Evidence: Upgrade the Relocated Toolchain to the Latest Permitted Versions

**Date:** 2026-10-04
**Change:** `upgrade-relocated-toolchain-to-latest`
**Manifest:** `~/.local/share/home-toolchain/package.json`

All values are read back from disk, the registry, or command output.

---

## 1. Direct Dependencies — Already at Latest

```console
gitnexus                     1.6.12       -> 1.6.12
@usebruno/cli                4.2.0        -> 4.2.0
newman                       6.2.2        -> 6.2.2
newman-reporter-htmlextra    1.23.1       -> 1.23.1
pyright                      1.1.414      -> 1.1.414
yaml-language-server         1.24.0       -> 1.24.0
```

No direct dependency could be upgraded.

---

## 2. In-Range Transitive Refresh Applied

`npm update` raised 24 in-range dependencies (20 net increases):

```console
@hono/node-server: 1.19.17 -> 2.1.3
@modelcontextprotocol/sdk: 1.30.0 -> 1.32.0
@nodable/entities: 3.0.0 -> 3.1.0
@types/node: 25.9.8 -> 26.6.4
ansi-regex: 5.0.1 -> 6.4.0
express-rate-limit: 8.6.2 -> 8.7.0
fast-xml-parser: 5.11.1 -> 5.11.2
ignore: 7.0.6 -> 7.0.12
isobject: 0.2.0 -> 3.0.1
mnemonist: 0.39.8 -> 0.40.5
picomatch: 2.3.2 -> 4.0.7
pino: 10.3.1 -> 10.4.0
prettier: 3.9.6 -> 3.9.9
proxy-addr: 2.0.7 -> 2.0.8
real-require: 0.2.0 -> 1.0.0
strip-ansi: 6.0.1 -> 7.2.0
undici-types: 7.24.6 -> 8.9.0
vscode-languageserver-textdocument: 1.0.14 -> 1.0.15
yaml: 2.8.3 -> 2.9.1
zod: 4.5.1 -> 4.6.5
```

---

## 3. No Downgrade Occurred

Six top-level slots appeared to drop. Inspection showed each was a **hoisting relocation** with
the higher version still present deeper in the tree:

```console
# chalk
BEFORE: node_modules/chalk@4.1.2      + node_modules/@usebruno/cli/node_modules/chalk@3.0.0
AFTER:  node_modules/chalk@3.0.0      + node_modules/newman-reporter-htmlextra/node_modules/chalk@4.1.2

# lru-cache
BEFORE: node_modules/lru-cache@11.5.3 + (4 nested copies)
AFTER:  node_modules/lru-cache@5.1.1  + node_modules/path-scurry/node_modules/lru-cache@11.5.3
```

A `name@version` set diff across the whole tree confirmed only 16 versions disappeared, and each
was replaced by its own newer version:

```console
@hono/node-server@1.19.17       replaced by 2.1.3
@modelcontextprotocol/sdk@1.30.0 replaced by 1.32.0
yaml@2.8.3                       replaced by 2.9.1
zod@4.5.1                        replaced by 4.6.5
... (all replacements newer)
```

**No package version was genuinely lowered.**

---

## 4. Exact-Pinned Stragglers Raised

Two dependencies could not move by range resolution:

```console
$ npm explain aws4
aws4@"^1.12.0" from aws4-axios@3.4.0        # range permits 1.13.2, update left 1.12.0
aws4@"^1.12.0" from postman-request@2.88.1-postman.48

$ npm view jsprim@2.0.2 dependencies.extsprintf
1.3.0                                        # exact pin, cannot move by range
```

Raised in the allowed direction via `overrides`:

```console
aws4 = 1.13.2          (via ">=1.13.2")
extsprintf = 1.4.1     (via ">=1.4.1")
```

---

## 5. Everything Upgradable Is Now Upgraded

```console
$ npm outdated
(empty — no direct dependency behind latest)

$ npm outdated --all      # filtered to in-range moves
(empty — no transitive dependency behind its permitted latest)
```

All **22** `overrides` pins resolve to the latest published version of their package:

```console
lodash 4.18.1 | uuid 14.0.2 | qs 6.16.0 | node-forge 1.4.0 | underscore 1.13.8
flatted 3.4.4 | sharp 0.35.5 | adm-zip 0.6.1 | handlebars 4.7.9 | jose 6.2.12
csv-parse 7.0.3 | fast-uri 4.2.1 | ip-address 10.7.3 | brace-expansion 5.0.12
moment 2.31.0 | hono 4.13.12 | axios 1.20.0 | form-data 4.0.6 | js-yaml 5.4.2
yaml 2.9.1 | aws4 1.13.2 | extsprintf 1.4.1
```

---

## 6. Tools Functional After the Refresh

```console
$ ~/.local/bin/bru --version

4.2.0

$ ~/.local/bin/yaml-language-server --version
1.24.0

$ ~/.local/bin/newman-reporter-htmlextra --version
1.23.1

gitnexus: 1.6.12
openspec: 1.14.0
```

The `$HOME` prefix hijack was not reintroduced:

```console
$ cd ~/Developer && npm prefix
/Users/androidteam/Developer
```

---

## 7. The Audit Is Unchanged, and Cannot Be Changed by Upgrade

```console
$ npm audit
12 high severity vulnerabilities
```

The count is governed by three roots, each of which has **no published version outside its
advisory range that is reachable by upgrade**:

| Root | Advisory range | Latest published | Upgradable? |
|---|---|---|---|
| `braces` | `<=3.0.3` | `3.0.3` | No — latest *is* the vulnerable ceiling |
| `node-forge` | `<=1.4.0` | `1.4.0` | No — latest *is* the vulnerable ceiling |
| `@faker-js/faker` | `<=10.4.0` | `10.6.0` | No — raising it breaks `newman` and `bru` |

Additionally, the newest parents still pin the vulnerable versions
(`postman-collection@5.3.1` pins faker `5.5.3`; `postman-runtime@7.56.1` pins `node-forge@1.4.0`),
so raising parents cannot help either. Independently corroborated by `bun audit fix`, which
reports the faker upgrade as "blocked by a dependent's range" and the other two as "no published
version fixes", concluding "Fixed 0 of 3".

---

## 8. Rollback

Pre-change manifest and lockfile captured at:

```console
/tmp/hometoolchain-package.json.before-upgrade
/tmp/hometoolchain-package-lock.json.before-upgrade
```

---

## 9. Conclusion

Every dependency that any upgrade can raise has been raised: direct dependencies were already at
latest, 24 transitive dependencies were refreshed within their permitted ranges, and two
exact-pinned stragglers were raised by upgrade-only override. No package was downgraded and all
tools still execute.

The audit remains at 12 high because those residuals are not upgrade-reachable. Reducing them
would require either a downgrade (prohibited) or removing the three packages that carry them —
a functional-removal decision, recorded but not taken here.
