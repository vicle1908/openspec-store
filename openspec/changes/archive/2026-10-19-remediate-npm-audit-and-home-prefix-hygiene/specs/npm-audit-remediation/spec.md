# npm-audit-remediation Specification Delta

## MODIFIED Requirements

### Requirement: Workstation Root Manifest Peer Conflict Resolution
The relocated workstation toolchain manifest (`~/.local/share/home-toolchain/package.json`) SHALL
retain the peer-resolution outcome achieved before relocation: `newman-reporter-htmlextra` pinned
to `^1.23.1` with its peer `newman` (`^6.0.0` resolving `6.2.3`) installed automatically without
adding a duplicate direct `newman` CLI entry, overrides held at non-vulnerable thresholds, and
`npm install` / `npm update` completing without `ERESOLVE` errors and without `--force` or
`--legacy-peer-deps`. No manifest, lockfile, or `node_modules` directory SHALL exist at `$HOME`.

#### Scenario: newman and htmlextra peer alignment
- **WHEN** `newman-reporter-htmlextra` is pinned to `^1.23.1` in
  `~/.local/share/home-toolchain/package.json` (resolving peer `newman@6.2.3`), with the `adm-zip`
  override held at `0.6.1`
- **THEN** npm installs and updates cleanly without `--force` or `--legacy-peer-deps`, and peer
  dependency resolution succeeds

#### Scenario: relocated manifest preserves the peer resolution
- **WHEN** `~/.local/share/home-toolchain/package.json` declares `newman-reporter-htmlextra@^1.23.1`
  (resolving peer `newman@6.2.3`) and `npm update` is executed there
- **THEN** the update completes with exit code 0 without `--force` or `--legacy-peer-deps`, and
  no `ERESOLVE` error is emitted

#### Scenario: npm audit execution after upgrade
- **WHEN** `npm audit` is executed in `~/.local/share/home-toolchain` with `"handlebars": "4.7.10"`
  and the scoped `@usebruno/requests` `"@faker-js/faker": ">=10.5.0"` override active
- **THEN** the command evaluates the dependency graph without `ERESOLVE` errors, reports 0
  critical vulnerabilities, and reports the 10 high advisories recorded as irreducible rather
  than the historical Newman v4 chain count

#### Scenario: no manifest remains at the home directory
- **WHEN** the home directory is inspected
- **THEN** no `package.json`, `package-lock.json`, `pnpm-lock.yaml`, `pnpm-workspace.yaml`,
  `bun.lock`, `bun.lockb`, `yarn.lock`, or `node_modules` exists directly in `$HOME`, and
  `npm prefix` executed from any workspace directory resolves to that directory

### Requirement: Transitive Vulnerability Elimination via Package Overrides
Node.js package manifests across `mcp-router`, `realtime/frontend`, `legacy/kafka-microservices`,
the relocated workstation toolchain (`~/.local/share/home-toolchain`), and the preserved TypeScript
branch of `prime-agent` (`backup/ts-custom-patches`) SHALL declare explicit version overrides for
transitive dependencies with published security advisories where parent packages have not released
updated dependency ranges, and SHALL additionally raise any transitive dependency that remains
behind its latest published version while its parent's declared range already permits the newer
version. In dual-manager environments like `realtime/frontend`, overrides MUST be synchronized
across both `overrides` and `pnpm.overrides` to ensure deterministic resolution.

#### Scenario: transitive overrides applied in mcp-router
- **WHEN** `mcp-router` specifies `blockExoticSubdeps: false` and `overrides` in `pnpm-workspace.yaml` for `smol-toml` (`<1.7.1` -> `>=1.7.1`), `fflate` (`>=0.8.0 <0.8.3` -> `0.8.3`, `>=0.4.5 <0.4.9` -> `0.4.9`), `proxy-addr` (`<2.0.8` -> `>=2.0.8`), `shell-quote` (`<1.11.0` -> `>=1.11.0`), `compression` (`<1.8.2` -> `>=1.8.2`), `http-cache-semantics` (`<=4.2.0` -> `>=4.3.0`), `source-map-js` (`<1.2.2` -> `>=1.2.2`), `postcss-selector-parser` (`<7.1.6` -> `>=7.1.6`), `handlebars` (`<4.7.10` -> `>=4.7.10`), and `electron` (`<41.10.7` -> `>=41.10.7`) alongside `electron@^41.10.7` in `apps/electron/package.json`
- **THEN** `pnpm install` resolves only versions meeting or exceeding the patched version thresholds, eliminating all 10 patched advisories (2 critical, 7 high, 1 moderate) and leaving only the 5 unpatched upstream residuals

#### Scenario: transitive overrides applied in realtime frontend
- **WHEN** `realtime/frontend` specifies `overrides` in `package.json` for `js-yaml` (`>=4.3.2`), `fflate` (`>=0.8.3`), `http-cache-semantics` (`>=4.3.0`), and `source-map-js` (`>=1.2.2`)
- **THEN** `npm install` binds the override versions throughout the dependency tree, resolving `js-yaml`, `fflate`, `http-cache-semantics`, and `source-map-js` advisories so `npm audit` reports 0 vulnerabilities

#### Scenario: dual-override parity in realtime frontend
- **WHEN** security overrides are declared in `realtime/frontend/package.json`
- **THEN** both `overrides` and `pnpm.overrides` contain synchronized patched version pins for `dompurify` (`>=3.4.17`), `brace-expansion` (`>=5.0.12`), `http-cache-semantics` (`>=4.3.0`), and `source-map-js` (`>=1.2.2`), eliminating advisories across both npm CI and pnpm workspaces

#### Scenario: prime-agent security overrides and extension deduplication
- **WHEN** overrides are inspected on the preserved TypeScript branch `backup/ts-custom-patches` of `platform/prime-agent/package.json` (while `main` operates as a native Rust Cargo workspace)
- **THEN** `ip-address` resolves to `>=10.7.1` and `brace-expansion` resolves to `>=5.0.12`, while `@anthropic-ai/sandbox-runtime` in root devDependencies and `packages/coding-agent/examples/extensions/sandbox` are aligned to `^0.0.77` without duplicate older dependency trees

#### Scenario: in-range transitive refresh in the relocated toolchain
- **WHEN** `npm update` is executed in `~/.local/share/home-toolchain`
- **THEN** every transitive dependency whose parent range already permits a newer version is
  raised to it (including peer `newman@6.2.3` and `js-yaml@5.5.0`), and a subsequent
  `npm outdated --all` reports no in-range moves (`current != wanted`) remaining

#### Scenario: exact-pinned stragglers raised by upgrade-only override
- **WHEN** `aws4` is reachable only via `aws4@"^1.12.0"` and `extsprintf` is exact-pinned at
  `1.3.0` by `jsprim@2.0.2`
- **THEN** `aws4` resolves to `1.13.2` and `extsprintf` to `1.4.1` via `overrides` entries
  `">=1.13.2"` and `">=1.4.1"` respectively, with no downgrade of any package

#### Scenario: direct dependencies and override pins are at latest
- **WHEN** the relocated toolchain is inspected after raising direct dependencies
  (`@usebruno/cli@^4.2.1`, `yaml-language-server@^2.0.0`) and updating the 22 top-level string
  `overrides` (`handlebars@4.7.10`, `uuid@14.0.3`, `qs@6.16.1`, `fast-uri@4.2.2`,
  `ip-address@10.7.4`, `hono@4.13.13`) plus the scoped `@usebruno/requests` override
- **THEN** `npm outdated` reports no direct dependency behind latest, and every active override
  pin resolves to the latest published version of its package

#### Scenario: residual set is unchanged by the refresh
- **WHEN** `npm audit` is executed after the refresh
- **THEN** the count is 0 critical and 10 high, because the residuals are rooted in `braces`
  (`<=3.0.3`), `node-forge` (`<=1.4.0`), and the `postman-collection` nested `@faker-js/faker`
  (`5.5.3` / `<=10.4.0`), each of which has no compatible published version outside its advisory
  range reachable by upgrade

### Requirement: Unpatched Upstream Residual Documentation
When a package manager audit reports vulnerabilities for which no upstream patched version exists (`patched: <0.0.0` or `null`), the remediation SHALL record verifiable evidence identifying each residual advisory by package name, advisory ID, and dependency chain rather than attempting unvetted monkey-patches or breaking downgrades.

#### Scenario: unpatched residuals identified in mcp-router
- **WHEN** `pnpm audit` is executed in `mcp-router` after applying patched overrides
- **THEN** exactly 5 residual advisories are reported (`extract-zip <=2.0.1` x 2, `braces <=3.0.3` x 1, `node-forge <=1.4.0` x 1, and `sprintf-js <=1.1.3` x 1), each carrying `patched_versions: null` with no available upstream fix

#### Scenario: unpatched residuals identified across workspace
- **WHEN** audit commands are executed post-remediation across governed manifests
- **THEN** residual advisories are documented with no-fix markers and without referencing `$HOME`: `extract-zip <=2.0.1` (in `mcp-router`), `node-forge <=1.4.0` (in `mcp-router`, `~/.local/share/home-toolchain`, and `prime-agent` `backup/ts-custom-patches`), `basic-ftp <=6.2.0` (in `prime-agent` `backup/ts-custom-patches`), `braces <=3.0.3` (in `mcp-router`, `legacy/kafka-microservices`, `~/.local/share/home-toolchain`, and `prime-agent` `backup/ts-custom-patches`), `sprintf-js <=1.1.3` (in `mcp-router`), and `@faker-js/faker <=10.4.0` (nested under `postman-collection` in `~/.local/share/home-toolchain`), while `realtime/frontend` reports 0 vulnerabilities

### Requirement: Microservices Tooling Vulnerability Elimination
Development tooling manifests in repository roots (`legacy/kafka-microservices`) SHALL maintain linter CLIs (`markdownlint-cli2`) at current major versions (v0.23+) that resolve modern non-vulnerable YAML, TOML, math, and Markdown parsers (`js-yaml@5.4.1`, `markdown-it@15.0.1`, `smol-toml@>=1.9.1`, `katex@>=0.19.0`) via explicit overrides where necessary, while recording unpatched `braces <=3.0.3` transitive advisories without downgrading `markdownlint-cli2`.

#### Scenario: linter execution on modern dependency graph
- **WHEN** `markdownlint-cli2` is maintained at `^0.23.3` with `"overrides": { "smol-toml": ">=1.9.1", "katex": ">=0.19.0" }` and `"#docs/deprecated"` excluded in `legacy/kafka-microservices/package.json`
- **THEN** `npm run lint:md` executes cleanly with exit code 0 (`Linting: 104 files; Summary: 0 issues in 0 files`), `smol-toml` and `katex` advisories are eliminated, and the remaining 5 high findings rooted in `braces <=3.0.3` are recorded as unpatched upstream residuals whose only offered audit fix (`markdownlint-cli2@0.0.4`) is a rejected downgrade

### Requirement: Downgrade-Only Remedy Indicates Unpatched Upstream
When `npm audit` reports an advisory for a package that is already installed at its latest
published version, and the only remedy the audit offers is a version *downgrade*, the
remediation SHALL classify that advisory as unpatched-upstream, SHALL record its identity,
and SHALL NOT apply the proposed downgrade.

#### Scenario: latest-pinned direct dependency reported vulnerable
- **WHEN** `newman@6.2.3` (resolved via `newman-reporter-htmlextra@1.23.1`) is the latest
  published release of `newman`, `npm audit` reports `newman` within range `>=4.5.2`, and the
  offered fix is `newman-reporter-htmlextra@1.22.5` / `newman@5.3.2` (a downgrade)
- **THEN** the advisory is recorded as unpatched-upstream with the installed version and the
  offered downgrade cited, and `newman-reporter-htmlextra` (`1.23.1`) and `newman` (`6.2.3`) are
  retained without downgrade

#### Scenario: force-fix convergence is impossible
- **WHEN** every direct dependency in the manifest is at its latest published version and each
  residual advisory's only offered remedy is a downgrade
- **THEN** `npm audit fix --force` is recorded as non-convergent, and is not re-run as a
  remediation step

### Requirement: Workstation Root Manifest Residual Identity Coverage
The unpatched-upstream residual inventory SHALL cover the relocated workstation toolchain manifest
(`~/.local/share/home-toolchain/package.json`) alongside the repository surfaces already governed,
and SHALL record each residual by package name, advisory identity, and dependency path. No
inventory entry SHALL reference a manifest in `$HOME`, which no longer exists.

#### Scenario: residual inventory enumerates the workstation root manifest
- **WHEN** `npm audit` is executed in `~/.local/share/home-toolchain`
- **THEN** evidence enumerates the reported advisories by package and dependency chain,
  recording the total as 0 critical and 10 high vulnerabilities and attributing them to the
  `postman-collection` `@faker-js/faker`, `braces`, and `node-forge` roots

#### Scenario: residual surfaces are attributed distinctly
- **WHEN** residuals are recorded
- **THEN** the contributing surfaces are distinguished — the `newman` |
  `newman-reporter-htmlextra` chain (`postman-collection`, `postman-runtime`, `postman-sandbox`,
  `@budibase/handlebars-helpers`) and the scoped `@usebruno/cli` override — rather than merged
  into a single undifferentiated count

### Requirement: Irreducible Residual Determination
An advisory SHALL be classified as irreducible when the latest published version of the
responsible package is within the advisory's vulnerable range, or when the only non-vulnerable
version is runtime-incompatible with an installed consumer.

#### Scenario: braces and node-forge are irreducible
- **WHEN** `braces` is vulnerable at `<=3.0.3` with latest published `3.0.3`, and `node-forge`
  is vulnerable at `<=1.4.0` with latest published `1.4.0`
- **THEN** both are recorded as irreducible unpatched-upstream residuals citing the latest
  published version as evidence, and no version change is applied

#### Scenario: residual count attributed to root causes
- **WHEN** the 10 high residual advisories in `~/.local/share/home-toolchain` are recorded
- **THEN** they are attributed to their root causes (`braces`, `node-forge`,
  `postman-collection` nested `@faker-js/faker`, and the `newman`/`postman-*` chain) rather than
  reported as 10 independent findings

### Requirement: No Package Manifest Directly in the Home Directory
Neither a `package.json`, a package-manager lockfile (`package-lock.json`, `pnpm-lock.yaml`,
`pnpm-workspace.yaml`, `bun.lock`, `bun.lockb`, `yarn.lock`), nor a `node_modules` directory SHALL
reside directly in `$HOME`, because `@npmcli/config` (`Config.loadLocalPrefix()`) resolves its
prefix upward from the current directory whenever `package.json` OR `node_modules` is present and
will adopt `$HOME` for any invocation made from a directory beneath `$HOME` that lacks its own.

#### Scenario: prefix resolution no longer hijacked
- **WHEN** `/Users/androidteam/package.json`, `/Users/androidteam/node_modules`, and all
  home-directory lockfiles (`pnpm-lock.yaml`, `pnpm-workspace.yaml`, `bun.lock`, and `.bun-backup*`
  files) have been removed and `npm prefix` is executed from `/Users/androidteam/Developer`
- **THEN** the command reports `/Users/androidteam/Developer`, not `/Users/androidteam`

#### Scenario: nested directories resolve to themselves
- **WHEN** `npm prefix` is executed from `/Users/androidteam/Developer/platform`
- **THEN** the command reports that directory, confirming the upward walk terminates at the
  invoked directory rather than at `$HOME`

### Requirement: Tooling Relocation Before Manifest Removal
Where a home-directory manifest provides tooling that is not available elsewhere, that tooling
SHALL be relocated to an explicit location outside the `$HOME` resolution path and verified
functional BEFORE the original manifest and dependency tree are removed.

#### Scenario: relocated tooling executes at the new location
- **WHEN** the manifest at `~/.local/share/home-toolchain/` is installed and updated to latest
- **THEN** `bru --version` reports `4.2.1` (or higher), `yaml-language-server --version` reports
  `2.0.0` (or higher), and `newman-reporter-htmlextra --version` reports `1.23.1` (or higher),
  each with exit status 0

#### Scenario: relocation is faithful
- **WHEN** the relocated tree is audited with `"handlebars": "4.7.10"` and the scoped
  `"@usebruno/requests": { "@faker-js/faker": ">=10.5.0" }` override active
- **THEN** `npm audit` reports 0 critical and 10 high irreducible advisories, and the
  `@faker-js/faker` resolution is `10.6.0` for `@usebruno/requests` and `5.5.3` nested under
  `postman-collection`

#### Scenario: tools remain reachable by name without a manifest in $HOME
- **WHEN** symlinks for `bru`, `yaml-language-server`, and `newman-reporter-htmlextra` are present
  in `~/.local/bin`
- **THEN** each command resolves and reports its version when invoked by name, with no
  `package.json`, lockfile, or `node_modules` present in `$HOME`
