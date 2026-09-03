# realtime-frontend-build Specification

## Purpose
TBD - created by archiving change fix-realtime-frontend-build. Update Purpose after archive.

## Requirements

### Requirement: Production build excludes test-only TypeScript inputs
The realtime frontend production TypeScript program SHALL use the repository's Vitest test environment rather than undeclared Jest types, and SHALL exclude test-only utilities and suites from the application build.

#### Scenario: clean production build
- **WHEN** `npm run build` runs from `realtime/frontend`
- **THEN** TypeScript completes without missing-Jest-type errors and Vite generates the production bundle with exit code 0

#### Scenario: audit remains clean
- **WHEN** `npm audit --json` runs after the configuration correction
- **THEN** the vulnerability total remains 0

#### Scenario: application dependency smoke remains valid
- **WHEN** the existing jspdf runtime smoke executes against the installed dependency
- **THEN** it generates a valid PDF buffer and exits 0
