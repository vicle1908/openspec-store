# Proposal: Modernize Package Replacements and Eliminate Dead Weight

## Why
Following the comprehensive modernization research, several legacy packages and unused dependencies across `tdt/realtime/frontend`, `legacy/kafka-microservices`, and workstation root tooling can be replaced with faster, lighter, modern alternatives or eliminated entirely. Removing dead weight (`@babel/preset-*`, `babel.config.cjs`, `html2canvas`) unblocks dependency peer resolutions and slims node modules, replacing `classnames` with `clsx` modernizes component styling utilities, upgrading `markdownlint-cli2` eliminates `js-yaml` and `linkify-it` vulnerabilities in microservices dev tooling, and adding `@usebruno/cli` establishes a modern, Git-friendly API test runner alongside Newman.

## What Changes
- **TDT Realtime Frontend (`tdt/realtime/frontend`)**:
  - Remove dead-weight Babel tooling (`babel.config.cjs`, `@babel/preset-env`, `@babel/preset-react`, `@babel/preset-typescript`) since Vite 8 and Vitest handle module bundling and transpilation natively via Rolldown and esbuild.
  - Remove uncalled dependency `html2canvas` and its type definitions `@types/html2canvas`.
  - Replace `classnames` with `clsx` (5x faster, 228-byte modern utility) in `Avatar.tsx` and `Modal.tsx`.
- **Legacy Kafka Microservices (`legacy/kafka-microservices`)**:
  - Upgrade `markdownlint-cli2` from `^0.19.1` to `^0.23.3`, resolving transitive vulnerabilities in `js-yaml`, `markdown-it`, and `linkify-it`.
- **Workstation Tooling (`/Users/androidteam/package.json`)**:
  - Add `@usebruno/cli` (`^4.2.0`) to provide modern, plain-text `.bru` API testing without cloud lock-in or legacy Postman runtime dependencies.

## Capabilities

### New Capabilities
None.

### Modified Capabilities
- `npm-audit-remediation`: Extend requirements to mandate dead-weight package elimination (`html2canvas`, redundant Babel presets in Vite environments), modern utility drop-in migrations (`classnames` to `clsx`), linter toolchain updates (`markdownlint-cli2@0.23.3`), and modern Git-native API testing tooling.

## Non-Goals
- Rewriting `apiClient.ts` to replace `axios` (which would require deep refactoring of request/response interceptors and token refresh handlers).
- Migrating existing Postman collections to Bruno format in this change (Bruno CLI is introduced as an available modern runner).

## Affected Ownership Boundaries
- `tdt/realtime/frontend`
- `legacy/kafka-microservices`
- `/Users/androidteam/package.json`
