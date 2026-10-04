# Design: Modernize Package Replacements and Eliminate Dead Weight

## Context
See `proposal.md`. Research during the previous dependency modernization identified several packages that are either unused (dead weight), legacy utilities superseded by faster standards, or carrying known vulnerabilities in tooling sub-dependencies.

## Goals / Non-Goals

**Goals:**
- Prune unused packages (`html2canvas`, `@types/html2canvas`, `@babel/preset-env`, `@babel/preset-react`, `@babel/preset-typescript`, and `babel.config.cjs`) from `tdt/realtime/frontend`.
- Migrate `classnames` to `clsx` in `Avatar.tsx` and `Modal.tsx`.
- Modernize `markdownlint-cli2` in `legacy/kafka-microservices` to resolve 9 sub-dependency CVEs.
- Add `@usebruno/cli` to workstation root manifest for modern plain-text API testing.

**Non-Goals:**
- Refactoring `axios` in `apiClient.ts` (retained for existing auth interceptor logic).
- Migrating test assertions from Playwright or Vitest.

## Decisions

### Decision 1: Drop Babel configuration in Vite 8 environment
- **Rationale**: Vite 8 uses Rolldown and esbuild for client production builds and development serving. Vitest compiles through Vite plugins. No script in `package.json` references Babel. Removing Babel presets eliminates unnecessary dependencies and resolves peer conflict warnings.

### Decision 2: Drop-in replacement `classnames` -> `clsx`
- **Rationale**: `clsx` provides identical conditional argument handling with less than 250 bytes of code and 5x performance. `Avatar.tsx` and `Modal.tsx` only use simple conditional class expressions (`classNames('base', { 'active': condition })`), making `clsx` 100% compatible.

### Decision 3: Modernize `markdownlint-cli2` to 0.23.3
- **Rationale**: `0.23.3` incorporates `js-yaml@5.4.1` and `markdown-it@15.0.1`, which eliminates the quadratic-complexity DoS vulnerabilities present in the older 0.19.x dependency chain.

## Risks / Trade-offs

- **Risk: Component styling mismatch with clsx**:
  - *Mitigation*: Run `npm run type-check`, `npm run build`, and Vitest component tests to confirm identical DOM output and compilation.
