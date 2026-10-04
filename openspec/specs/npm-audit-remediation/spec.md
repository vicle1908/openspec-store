# npm-audit-remediation Specification

## Purpose
Governs remediation contracts, dependency upgrade matrices, peer-resolution conflict reconciliation, and unpatched upstream residual tracking across workstation and repository package manifests.

## Requirements

### Requirement: Workstation Root Manifest Peer Conflict Resolution
The workstation root package manifest (`/Users/androidteam/package.json`) SHALL resolve all peer dependency conflicts and version deadlocks between `newman` and its reporter plugins by pinning semver-compatible major versions, updating overrides to non-vulnerable thresholds, and ensuring `npm audit` and `npm outdated` exit without `ERESOLVE` errors.

#### Scenario: newman and htmlextra peer alignment
- **WHEN** `newman` is updated to `^6.2.2` and `adm-zip` override is updated to `0.6.1` in `/Users/androidteam/package.json`
- **THEN** npm installs cleanly without `--force` or `--legacy-peer-deps`, and peer dependency resolution succeeds

#### Scenario: npm audit execution after upgrade
- **WHEN** `npm audit` is executed in `/Users/androidteam`
- **THEN** the command evaluates the dependency graph without `ERESOLVE` errors, and the 28 vulnerabilities associated with the Newman v4 dependency chain are resolved

### Requirement: Transitive Vulnerability Elimination via Package Overrides
Node.js package manifests across `mcp-router`, `prime-agent`, and `realtime/frontend` SHALL declare explicit version overrides for transitive dependencies with published security advisories where parent packages have not released updated dependency ranges. In dual-manager environments like `realtime/frontend`, overrides MUST be synchronized across both `overrides` and `pnpm.overrides` to ensure deterministic resolution.

#### Scenario: transitive overrides applied in mcp-router
- **WHEN** `mcp-router` specifies `pnpm.overrides` for `smol-toml` (`<=1.7.0` -> `>=1.7.1`) and `fflate` (`>=0.8.0 <0.8.3` -> `>=0.8.3`, `>=0.4.5 <0.4.9` -> `>=0.4.9`)
- **THEN** `pnpm install` resolves only versions meeting or exceeding the patched version thresholds, resolving 3 out of 7 reported vulnerabilities

#### Scenario: transitive overrides applied in realtime frontend
- **WHEN** `realtime/frontend` specifies `overrides` in `package.json` for `js-yaml` (`>=4.3.2`) and `fflate` (`>=0.8.3`)
- **THEN** `npm install` binds the override versions throughout the dependency tree, resolving the high-severity `js-yaml` advisory and moderate `fflate` advisory

#### Scenario: dual-override parity in realtime frontend
- **WHEN** security overrides are declared in `realtime/frontend/package.json`
- **THEN** both `overrides` and `pnpm.overrides` contain identical version pins for `dompurify` (`>=3.4.16`) and `brace-expansion` (`>=5.0.12`), eliminating DOM XSS and regex DoS advisories across both npm CI and pnpm workspaces

#### Scenario: prime-agent security overrides and extension deduplication
- **WHEN** overrides are added to `platform/prime-agent/package.json`
- **THEN** `ip-address` resolves to `>=10.7.1` and `brace-expansion` resolves to `>=5.0.12`, while `@anthropic-ai/sandbox-runtime` in root devDependencies and `packages/coding-agent/examples/extensions/sandbox` are aligned to `^0.0.77` without duplicate older dependency trees

### Requirement: Test Runner Security Alignment
The `prime-agent` and `realtime/frontend` workspaces SHALL pin test framework dependencies (`vitest` and `@vitest/mocker`) across all workspace packages to versions containing security patches for arbitrary file read and path traversal vulnerabilities without downgrading unrelated tooling packages.

#### Scenario: vitest path traversal fix in prime-agent
- **WHEN** `vitest` is updated to `^4.1.11` in `packages/agent/package.json`, `packages/ai/package.json`, and `packages/coding-agent/package.json`
- **THEN** `npm audit` in `prime-agent` reports zero vulnerabilities, and workspace test suites execute normally

#### Scenario: vitest path traversal fix in realtime frontend
- **WHEN** `vitest`, `@vitest/coverage-v8`, and `@vitest/ui` are updated to `^4.1.11` in `realtime/frontend/package.json`
- **THEN** `npm audit` confirms the `@vitest/mocker` path traversal vulnerability is eliminated

### Requirement: Unpatched Upstream Residual Documentation
When a package manager audit reports vulnerabilities for which no upstream patched version exists (`patched: <0.0.0`), the remediation SHALL record verifiable evidence identifying each residual advisory by package name, advisory ID, and dependency chain rather than attempting unvetted monkey-patches or breaking downgrades.

#### Scenario: unpatched residuals identified in mcp-router
- **WHEN** `pnpm audit` is executed in `mcp-router` after applying overrides
- **THEN** exactly 4 residual advisories are reported (`image-size` x 2, `extract-zip` x 2), each carrying `patched: <0.0.0` with no available upstream fix

#### Scenario: unpatched residuals identified across workspace
- **WHEN** audit commands are executed post-remediation
- **THEN** residual advisories are documented with no-fix markers: `http-cache-semantics <=4.2.0` (in `realtime/frontend` and `mcp-router`), `extract-zip <=2.0.1` (in `mcp-router`), `node-forge <=1.4.0` (in `mcp-router`, `prime-agent`, and `~`), `basic-ftp <=6.2.0` (in `prime-agent`), and `braces <=3.0.3` (in `mcp-router`, `prime-agent`, and `~`)

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
Development tooling manifests in repository roots (`legacy/kafka-microservices`) SHALL maintain linter CLIs (`markdownlint-cli2`) at current major versions (v0.23+) that resolve modern non-vulnerable YAML and Markdown parsers (`js-yaml@5.4.1`, `markdown-it@15.0.1`).

#### Scenario: linter execution on modern dependency graph
- **WHEN** `markdownlint-cli2` is upgraded to `^0.23.3` in `legacy/kafka-microservices`
- **THEN** `npm run lint:md` executes as configured, resolving clean dependency trees

### Requirement: Modern Git-Native API Test Tooling Availability
The workstation root tooling manifest SHALL make modern, offline-first API testing CLIs (`@usebruno/cli`) available to run API collections formatted as plain text files in version control.

#### Scenario: bruno CLI verification
- **WHEN** `bru --version` is executed
- **THEN** the command reports version 4.2.0 or higher and exits with status 0

### Requirement: Downgrade-Only Remedy Indicates Unpatched Upstream

When `npm audit` reports an advisory for a package that is already installed at its latest
published version, and the only remedy the audit offers is a version *downgrade*, the
remediation SHALL classify that advisory as unpatched-upstream, SHALL record its identity,
and SHALL NOT apply the proposed downgrade.

#### Scenario: latest-pinned direct dependency reported vulnerable

- **WHEN** `newman@6.2.2` is the latest published release of `newman`, `npm audit` reports
  `newman` within range `>=6.0.0`, and the offered fix is `newman@5.3.2` (a downgrade)
- **THEN** the advisory is recorded as unpatched-upstream with the installed version and the
  offered downgrade cited, and `newman` is left at `6.2.2`

#### Scenario: force-fix convergence is impossible

- **WHEN** every direct dependency in the manifest is at its latest published version and each
  residual advisory's only offered remedy is a downgrade
- **THEN** `npm audit fix --force` is recorded as non-convergent, and is not re-run as a
  remediation step

### Requirement: Workstation Root Manifest Residual Identity Coverage

The unpatched-upstream residual inventory SHALL cover `/Users/androidteam/package.json`
alongside the repository surfaces already governed, and SHALL record each residual by package
name, advisory identity, and dependency path.

#### Scenario: residual inventory enumerates the workstation root manifest

- **WHEN** `npm audit` is executed in `/Users/androidteam` on 2026-10-04
- **THEN** evidence enumerates the reported advisories by package and dependency chain,
  recording the total as 19 vulnerabilities (2 moderate, 17 high)

#### Scenario: residual surfaces are attributed distinctly

- **WHEN** residuals are recorded
- **THEN** the two contributing surfaces are distinguished — the `newman` |
  `newman-reporter-htmlextra` chain and the `@usebruno/cli` chain — rather than merged into a
  single undifferentiated count

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

Before a remediation change asserts a dependency upgrade is outstanding, the change SHALL
check the store's archive for a completed change covering the same manifest, so the upgrade is
not repeated.

#### Scenario: already-archived upgrades are recognised

- **WHEN** a remediation proposal is authored for `/Users/androidteam/package.json`
- **THEN** the proposal references the archived changes that already performed the
  `newman`/`newman-reporter-htmlextra`/`@usebruno/cli` upgrades and does not re-execute them
