# npm-audit-remediation Specification

## Purpose
Governs remediation contracts, dependency upgrade matrices, peer-resolution conflict reconciliation, and unpatched upstream residual tracking across workstation and repository package manifests.

## Requirements

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

### Requirement: Test Runner Security Alignment
The `prime-agent` and `realtime/frontend` workspaces SHALL pin test framework dependencies (`vitest` and `@vitest/mocker`) across all workspace packages to versions containing security patches for arbitrary file read and path traversal vulnerabilities without downgrading unrelated tooling packages.

#### Scenario: vitest path traversal fix in prime-agent
- **WHEN** `vitest` is updated to `^4.1.11` in `packages/agent/package.json`, `packages/ai/package.json`, and `packages/coding-agent/package.json`
- **THEN** `npm audit` in `prime-agent` reports zero vulnerabilities, and workspace test suites execute normally

#### Scenario: vitest path traversal fix in realtime frontend
- **WHEN** `vitest`, `@vitest/coverage-v8`, and `@vitest/ui` are updated to `^4.1.11` in `realtime/frontend/package.json`
- **THEN** `npm audit` confirms the `@vitest/mocker` path traversal vulnerability is eliminated

### Requirement: Unpatched Upstream Residual Documentation
When a package manager audit reports vulnerabilities for which no upstream patched version exists (`patched: <0.0.0` or `null`), the remediation SHALL record verifiable evidence identifying each residual advisory by package name, advisory ID, and dependency chain rather than attempting unvetted monkey-patches or breaking downgrades.

#### Scenario: unpatched residuals identified in mcp-router
- **WHEN** `pnpm audit` is executed in `mcp-router` after applying patched overrides
- **THEN** exactly 5 residual advisories are reported (`extract-zip <=2.0.1` x 2, `braces <=3.0.3` x 1, `node-forge <=1.4.0` x 1, and `sprintf-js <=1.1.3` x 1), each carrying `patched_versions: null` with no available upstream fix

#### Scenario: unpatched residuals identified across workspace
- **WHEN** audit commands are executed post-remediation across governed manifests
- **THEN** residual advisories are documented with no-fix markers and without referencing `$HOME`: `extract-zip <=2.0.1` (in `mcp-router`), `node-forge <=1.4.0` (in `mcp-router`, `~/.local/share/home-toolchain`, and `prime-agent` `backup/ts-custom-patches`), `basic-ftp <=6.2.0` (in `prime-agent` `backup/ts-custom-patches`), `braces <=3.0.3` (in `mcp-router`, `legacy/kafka-microservices`, `~/.local/share/home-toolchain`, and `prime-agent` `backup/ts-custom-patches`), `sprintf-js <=1.1.3` (in `mcp-router`), and `@faker-js/faker <=10.4.0` (nested under `postman-collection` in `~/.local/share/home-toolchain`), while `realtime/frontend` reports 0 vulnerabilities

### Requirement: React 19.3 Ecosystem Parity
Client frontend applications SHALL upgrade to React 19.3.0 and corresponding type definitions without breaking rendering, router integration, or property test suites.

#### Scenario: realtime frontend react 19.3 upgrade
- **WHEN** `realtime/frontend/package.json` is updated to `react@19.3.0`, `react-dom@19.3.0`, `@types/react@^19.3.0`, and `@types/react-dom@^19.3.0`
- **THEN** `npm run type-check`, property-based test suites, and production build succeed with exit code 0

### Requirement: TypeScript 7 Toolchain Configuration Normalization
TypeScript configuration files in frontend projects (`tsconfig.json`, `tsconfig.test.json`) SHALL eliminate obsolete `baseUrl` compiler options upon upgrading to TypeScript 7, and SHALL declare path aliases exclusively through `paths` object mappings.

#### Scenario: compilation without baseUrl warning or error
- **WHEN** `npm run type-check` (`tsc --noEmit`) is executed against TypeScript 7.0.2 in `tdt/realtime/frontend`
- **THEN** compilation completes with exit code 0, without emitting TS5102 error regarding removed `baseUrl`

#### Scenario: production asset bundling under TypeScript 7
- **WHEN** `npm run build` (`tsc && vite build`) is executed in `tdt/realtime/frontend`
- **THEN** Vite and Rolldown transform modules and generate the production bundle with exit code 0

### Requirement: Presentation Toolkit Major CLI Modernization
The presentation toolkit in `ascend/tmz-case-challenge` SHALL integrate Commander v15+ and jszip v3.10.2, preserving all existing CLI options, subcommands, and report outputs without argument parsing errors.

#### Scenario: CLI execution with Commander 15
- **WHEN** `node output/pptx-toolkit/cli.js --help` or `node output/pptx-toolkit/cli.js info` is executed
- **THEN** the CLI exits with status 0, displaying all toolkit capabilities and commands

#### Scenario: package audit cleanliness in partner workspace
- **WHEN** `npm audit` is executed in `ascend/tmz-case-challenge`
- **THEN** 0 vulnerabilities are reported across the dependency tree

### Requirement: Native Upstream Engine Synchronization
The workspace SHALL preserve custom TypeScript patches in a dedicated backup branch before synchronizing `platform/prime-agent` with upstream remote repositories, and SHALL ensure the global CLI binary resolves to the official release channel version (v0.9.8).

#### Scenario: local patch preservation
- **WHEN** `platform/prime-agent` is synchronized with upstream `origin/main`
- **THEN** local commits are captured in branch `backup/ts-custom-patches` and working tree artifacts are safely archived in `.git/ts-working-tree-backup/`

#### Scenario: global binary release verification
- **WHEN** `prime-agent -v` or `prime-agent --help` is executed
- **THEN** the command executes the official v0.9.8 Mach-O executable and exits with code 0

### Requirement: Dead Weight Dependency Elimination
Frontend application manifests operating under Vite and Rolldown/esbuild toolchains SHALL NOT maintain legacy Babel configuration files (`babel.config.cjs`) or Babel transpilation presets (`@babel/preset-*`) in their dependencies when scripts do not invoke Babel. Furthermore, uncalled utility dependencies (`html2canvas`, `@types/html2canvas`) SHALL be pruned from manifests.

#### Scenario: elimination of redundant babel dependencies
- **WHEN** Babel presets and config are removed from `tdt/realtime/frontend`
- **THEN** `npm run type-check` and `npm run build` execute cleanly with exit code 0, eliminating peer conflict barriers with Babel v8

#### Scenario: elimination of unused canvas capture dependencies
- **WHEN** `html2canvas` and `@types/html2canvas` are removed from `tdt/realtime/frontend`
- **THEN** package installation and application bundling proceed without missing module resolution errors

### Requirement: Modern Utility Replacement (clsx)
Component styling class concatenation in frontend projects SHALL utilize modern, lightweight utility packages (`clsx`) in place of legacy `classnames`, preserving exact conditional class resolution semantics.

#### Scenario: component rendering with clsx
- **WHEN** components utilizing class concatenation (`Avatar.tsx`, `Modal.tsx`) are compiled and rendered
- **THEN** conditional CSS class strings are generated identically without runtime error

### Requirement: Microservices Tooling Vulnerability Elimination
Development tooling manifests in repository roots (`legacy/kafka-microservices`) SHALL maintain linter CLIs (`markdownlint-cli2`) at current major versions (v0.23+) that resolve modern non-vulnerable YAML, TOML, math, and Markdown parsers (`js-yaml@5.4.1`, `markdown-it@15.0.1`, `smol-toml@>=1.9.1`, `katex@>=0.19.0`) via explicit overrides where necessary, while recording unpatched `braces <=3.0.3` transitive advisories without downgrading `markdownlint-cli2`.

#### Scenario: linter execution on modern dependency graph
- **WHEN** `markdownlint-cli2` is maintained at `^0.23.3` with `"overrides": { "smol-toml": ">=1.9.1", "katex": ">=0.19.0" }` and `"#docs/deprecated"` excluded in `legacy/kafka-microservices/package.json`
- **THEN** `npm run lint:md` executes cleanly with exit code 0 (`Linting: 104 files; Summary: 0 issues in 0 files`), `smol-toml` and `katex` advisories are eliminated, and the remaining 5 high findings rooted in `braces <=3.0.3` are recorded as unpatched upstream residuals whose only offered audit fix (`markdownlint-cli2@0.0.4`) is a rejected downgrade

### Requirement: Modern Git-Native API Test Tooling Availability
The workstation root tooling manifest SHALL make modern, offline-first API testing CLIs (`@usebruno/cli`) available to run API collections formatted as plain text files in version control.

#### Scenario: bruno CLI verification
- **WHEN** `bru --version` is executed
- **THEN** the command reports version 4.2.0 or higher and exits with status 0

### Requirement: Electron Workspace TypeScript 7 and Playwright Alignment
Electron desktop applications in monorepos (`apps/electron` in `platform/mcp-router`) SHALL align their local compiler and testing toolchains to root workspace versions (`typescript@^7.0.2`, `playwright@^1.63.0`), configure `moduleResolution: "bundler"` without obsolete `baseUrl` options, and declare ambient CSS type definitions for side-effect styling imports.

#### Scenario: turbo typecheck execution across packages
- **WHEN** `pnpm run typecheck` (`turbo run typecheck`) is executed in `platform/mcp-router`
- **THEN** all 6 workspace packages (`cli`, `electron`, `remote-api-types`, `shared`, `tailwind-config`, `ui`) pass compilation with exit code 0

#### Scenario: native rebuild completion
- **WHEN** `pnpm install` triggers `electron-rebuild`
- **THEN** native modules (`argon2`, `better-sqlite3`) compile and link successfully against the target Electron ABI

### Requirement: ts-node Deprecation and tsx Test Runner Migration
Node.js test runners executing TypeScript test suites in monorepos SHALL NOT invoke legacy `ts-node` loaders or registrations, and SHALL utilize `tsx` (via `node --import tsx` or `require("tsx/cjs")`) and `esbuild` for runtime TypeScript transpilation under TypeScript 7 and Node 26.

#### Scenario: execution of electron unit tests with tsx
- **WHEN** `pnpm run test` (`node --test tests/*.test.cjs`) is executed in `apps/electron`
- **THEN** all 17 unit tests execute and pass with status 0 without `ts.sys` undefined errors

#### Scenario: execution of CLI tests with tsx ESM import
- **WHEN** `pnpm run test` (`node --import tsx --test tests/*.test.mjs`) is executed in `apps/cli`
- **THEN** all test suites pass with status 0, resolving workspace packages without loader errors

### Requirement: TypeScript 7 Relative Path Mapping Strictness
When `compilerOptions.baseUrl` is omitted from `tsconfig.json` files operating under TypeScript 7, all path values defined in `paths` mappings SHALL explicitly begin with a relative prefix (`./` or `../`), adhering to TS5090 validation rules.

#### Scenario: tsc compilation without TS5090 errors
- **WHEN** `tsc --build` is executed across workspace packages
- **THEN** compiler path resolution completes without emitting TS5090 non-relative path errors

### Requirement: Root Manifest Transitive Override Hardening
The relocated workstation toolchain manifest SHALL declare strict version overrides for the
transitive HTTP, form handling, and parser libraries required by the Git-native API testing
tooling (`axios`, `form-data`, `js-yaml`, `yaml`, `@faker-js/faker`), and SHALL record which
residual advisories remain regardless of those overrides, because no published version resolves
them.

#### Scenario: elimination of bruno transitive CVEs
- **WHEN** overrides for `axios@^1.20.0`, `form-data@4.0.6`, `js-yaml@>=4.3.2`, and
  `yaml@>=2.8.3` are active in `~/.local/share/home-toolchain/package.json`
- **THEN** `npm audit` reports no vulnerabilities attributable to the Bruno dependency chain
  other than the `@faker-js/faker` residual, which is recorded as irreducible because raising
  it breaks `newman` and `bru`

#### Scenario: override set survives relocation intact

- **WHEN** the relocated manifest is inspected
- **THEN** it declares the same override set as before relocation, and `axios@^1.20.0`,
  `form-data@4.0.6`, `js-yaml@>=4.3.2`, and `yaml@>=2.8.3` are all present and active

#### Scenario: residual set is recorded rather than claimed resolved

- **WHEN** `npm audit` is executed against the relocated manifest
- **THEN** the residuals rooted in `@faker-js/faker`, `braces`, and `node-forge` are recorded as
  irreducible with their no-fix evidence, and the remediation does NOT claim zero vulnerabilities
  for the Bruno dependency chain, because `@faker-js/faker` cannot be raised without breaking
  `newman` and `bru`

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

### Requirement: Home-Directory Manifest Footgun Recording

Because a `package.json` in `$HOME` causes `npm` and `npx` to resolve to it from any directory
beneath `$HOME` that lacks its own manifest, the remediation SHALL record the hazard and the
resulting invocation discipline.

#### Scenario: prefix resolution hazard is documented

- **WHEN** the incident is recorded in evidence
- **THEN** the evidence states that `npm prefix` from `~/Developer` resolves to
  `/Users/androidteam` and that dependency commands MUST be issued from the owning repository
  root

### Requirement: Archived Prior Art Reconciliation Before New Remediation
Before a remediation change asserts a dependency upgrade is outstanding, the change SHALL check
the store's archive for a completed change covering the same manifest, so the upgrade is not
repeated.

#### Scenario: already-archived upgrades are recognised

- **WHEN** a remediation proposal is authored for the relocated toolchain manifest at
  `~/.local/share/home-toolchain/package.json`
- **THEN** the proposal references the archived changes that already performed the
  `newman`/`newman-reporter-htmlextra`/`@usebruno/cli` upgrades and does not re-execute them

### Requirement: Upgrade-Only Override Compatibility Gate

A transitive-dependency override proposed as a security remedy SHALL be validated against the
runtime API of every installed consumer before it is retained. When a forward-only override
clears an advisory but breaks a consumer's execution, it SHALL be reverted to the pre-change
state and recorded as a rejected remedy, not as a remediation. Where a shared transitive package
is consumed by multiple parents with differing API compatibility, the override SHALL be **scoped
to the consumer that tolerates the newer version** rather than applied globally, and the scoped
consumer's entry point SHALL be exercised after installation.

#### Scenario: faker override clears the advisory but breaks the consumer

- **WHEN** `"@faker-js/faker": ">=10.5.0"` is added as a **global** `overrides` entry in the
  workstation toolchain manifest, resolving `@faker-js/faker` from the vulnerable `9.9.0`
  to `10.6.0` and reducing the audit from 12 high to 7 high
- **THEN** `newman --version` fails with `TypeError: Cannot read properties of undefined
  (reading 'city')` originating in `postman-collection`'s `faker.address.city` call, the
  override is reverted, and the global form is recorded as rejected despite reducing the count

#### Scenario: a rejected remedy is not reported as a remediation

- **WHEN** the global override has been reverted
- **THEN** the audit total is recorded as restored to 12 high, and the manifest is verified
  unchanged by that reverted experiment

#### Scenario: scoping the override to the compatible consumer retains the fix

- **WHEN** the override is instead scoped as
  `"@usebruno/requests": { "@faker-js/faker": ">=10.5.0" }` in
  `~/.local/share/home-toolchain/package.json`
- **THEN** `node_modules/@faker-js/faker` resolves to `10.6.0` while
  `node_modules/postman-collection/node_modules/@faker-js/faker` remains at the compatible
  `5.5.3`, the audit falls from 12 high to 10 high, and no dependency is downgraded

#### Scenario: scoped consumer is exercised before retention

- **WHEN** the scoped override is installed
- **THEN** `bru --help` and `bru --version` both exit 0, and requiring
  `postman-collection/lib/superstring/dynamic-variables.js` succeeds, confirming neither
  consumer is broken

#### Scenario: the deeper scope is rejected when it breaks the other consumer

- **WHEN** the override is scoped further to
  `"postman-collection": { "@faker-js/faker": ">=10.5.0" }`
- **THEN** the audit falls to 7 high but `postman-collection` fails to load with
  `Cannot read properties of undefined (reading 'city')`, so that scope is rejected and the
  Bruno-only scope is retained as the safe maximum

### Requirement: Forward-Fix Sweep Across All Affected Packages

Before concluding that an advisory set is irreducible, the remediation SHALL evaluate the
latest published version of every affected package against the advisory's vulnerable range,
and SHALL record the verdict per package.

#### Scenario: forward-fix sweep recorded per package

- **WHEN** the sweep is performed across `newman`, `newman-reporter-htmlextra`,
  `@usebruno/cli`, `@usebruno/requests`, `braces`, `micromatch`, `node-forge`,
  `postman-collection`, `postman-runtime`, `postman-sandbox`,
  `@budibase/handlebars-helpers`, and `@faker-js/faker`
- **THEN** each package is recorded with its latest published version and one of the verdicts:
  latest already selected, no fix (latest within vulnerable range), no fix (all versions), or
  forward fix available-but-incompatible

#### Scenario: nested chains are shown to be unresolvable

- **WHEN** `@budibase/handlebars-helpers@0.14.3` (latest) is found to depend on
  `micromatch@^4.0.5`, which depends on `braces@^3.0.3`, and `braces@3.0.3` is itself the
  latest published version and within the vulnerable range
- **THEN** the `braces` inheritance chain is recorded as unresolvable by any version change at
  any level

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

### Requirement: Sanctioned Global Prefix Preservation

Relocation SHALL NOT disturb `~/.npm-global`, the sanctioned global npm prefix used by the
workspace's daily update script, nor any tool installed within it.

#### Scenario: global prefix tooling unaffected

- **WHEN** the home-directory manifest is removed
- **THEN** `gitnexus --version` still reports `1.6.12`, and `~/.npm-global/lib/node_modules`
  retains its contents
