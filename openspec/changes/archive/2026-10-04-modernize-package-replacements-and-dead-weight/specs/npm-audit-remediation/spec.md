# Spec Delta: npm-audit-remediation

## ADDED Requirements

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
