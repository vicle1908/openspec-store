# realtime-vitest-docs Specification

## Purpose
TBD - created by archiving change align-realtime-vitest-docs. Update Purpose after archive.

## Requirements

### Requirement: Frontend testing uses documented Vitest workflow
The tracked frontend SHALL use Vitest configuration and APIs consistently, SHALL document that workflow, and SHALL have a green actual Vitest suite after migration-related failures are resolved.

#### Scenario: baseline is established
- **WHEN** the pre-alignment commit `f196754` is tested with its dependency/configuration state
- **THEN** baseline failures are recorded separately from migration-caused failures

#### Scenario: actual Vitest suite runs
- **WHEN** the documented frontend Vitest command runs after alignment
- **THEN** it executes all discovered tracked tests without stale Jest-only configuration or globals and exits 0

#### Scenario: production build remains green
- **WHEN** `npm run build` runs
- **THEN** TypeScript and Vite complete successfully
