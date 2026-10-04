# Spec Delta: npm-audit-remediation

## ADDED Requirements

### Requirement: Electron Workspace TypeScript 7 and Playwright Alignment
Electron desktop applications in monorepos (`apps/electron` in `platform/mcp-router`) SHALL align their local compiler and testing toolchains to root workspace versions (`typescript@^7.0.2`, `playwright@^1.63.0`), configure `moduleResolution: "bundler"` without obsolete `baseUrl` options, and declare ambient CSS type definitions for side-effect styling imports.

#### Scenario: turbo typecheck execution across packages
- **WHEN** `pnpm run typecheck` (`turbo run typecheck`) is executed in `platform/mcp-router`
- **THEN** all 6 workspace packages (`cli`, `electron`, `remote-api-types`, `shared`, `tailwind-config`, `ui`) pass compilation with exit code 0

#### Scenario: native rebuild completion
- **WHEN** `pnpm install` triggers `electron-rebuild`
- **THEN** native modules (`argon2`, `better-sqlite3`) compile and link successfully against the target Electron ABI

### Requirement: Root Manifest Transitive Override Hardening
The workstation root manifest (`/Users/androidteam/package.json`) SHALL declare strict version overrides for transitive HTTP, form handling, and parser libraries (`axios`, `form-data`, `js-yaml`, `yaml`) required by Git-native API testing tooling (`@usebruno/cli`), ensuring `npm audit` reports zero non-residual vulnerabilities.

#### Scenario: elimination of bruno transitive CVEs
- **WHEN** overrides for `axios@^1.20.0`, `form-data@4.0.6`, `js-yaml@>=4.3.2`, and `yaml@>=2.8.3` are active in `/Users/androidteam/package.json`
- **THEN** `npm audit` reports zero vulnerabilities associated with Bruno dependencies
