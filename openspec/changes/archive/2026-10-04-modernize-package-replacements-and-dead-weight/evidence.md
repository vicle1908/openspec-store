# Verification Evidence: Modernize Package Replacements and Eliminate Dead Weight

## Date: 2026-10-04

### 1. TDT Realtime Frontend (`tdt/realtime/frontend`)

#### 1.1 Dead Weight Removal
- **Files Removed**: `babel.config.cjs`
- **Packages Removed**: `@babel/preset-env`, `@babel/preset-react`, `@babel/preset-typescript`, `html2canvas`, `@types/html2canvas`, `classnames`.
- **Node Modules Impact**: Removed 99 transitive dead-weight packages on `npm install`.

#### 1.2 `clsx` Utility Migration
- **Installed**: `clsx@^2.1.1`
- **Components Updated**:
  - `src/components/Avatar/Avatar.tsx`: `import classNames from 'clsx'`
  - `src/components/Modal/Modal.tsx`: `import classNames from 'clsx'`

#### 1.3 Compilation and Test Verification
- **Type Check**: `npm run type-check` (`tsc --noEmit`) -> 0 errors (Exit: 0).
- **Production Build**: `npm run build` (`tsc && vite build`) -> 2,981 modules transformed, built clean production bundle in 1.52s (Exit: 0).
- **Unit and Component Tests**:
  - `src/__tests__/smoke.test.ts`: 1/1 passed.
  - `src/components/ErrorBoundary/__tests__/ErrorBoundary.test.tsx`: 7/7 passed.
  - `src/components/Avatar/__tests__/` & `src/components/Modal/__tests__/`: 15 passed, 38 skipped.

### 2. Legacy Kafka Microservices (`legacy/kafka-microservices`)

#### 2.1 Tooling Modernization
- **Manifest**: `markdownlint-cli2@^0.23.3` (upgraded from `^0.19.1`).
- **Dependencies Resolved**: `js-yaml@5.4.1`, `markdown-it@15.0.1`, `micromatch@4.0.8`.
- **CLI Verification**: `npx markdownlint-cli2 --version` -> `markdownlint-cli2 v0.23.3 (markdownlint v0.41.1)` (Exit: 0).
- **Audit Impact**: Eliminated 4 CVEs in `js-yaml`, `linkify-it`, and `markdown-it`. Only unpatched upstream residual `braces <=3.0.3` remains.

### 3. Workstation Root Manifest (`/Users/androidteam/package.json`)

#### 3.1 Bruno CLI Addition
- **Installed**: `@usebruno/cli@^4.2.0`
- **CLI Command**: `bru --version`
- **Output**: `4.2.0` (Exit: 0).
- **Newman Retained**: `newman --version` -> `6.2.2` (Exit: 0).
