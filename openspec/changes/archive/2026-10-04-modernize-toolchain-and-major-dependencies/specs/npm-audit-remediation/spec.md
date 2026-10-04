# Spec Delta: npm-audit-remediation

## ADDED Requirements

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
