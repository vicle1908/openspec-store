# Design: fix-realtime-frontend-build

## Decision
Keep the existing application `tsconfig.json` for source compilation, but remove `jest` from `compilerOptions.types` because this repository uses Vitest and has no `@types/jest` dependency. Exclude test-only paths that are currently included accidentally: `src/tests/**` and `src/test-utils.tsx`.

## Rationale
The current build is `tsc && vite build`. `tsc` includes all `src` files, including property-based test setup and shared test utilities, then fails on missing Jest types and test-only mock typing. Those files are not application inputs. Existing explicit excludes already cover several test layouts; extending them to the remaining test paths restores the intended build boundary without adding a dead Jest dependency.

## Verification
Run `npm run build`, `npm audit --json`, and the existing focused jspdf smoke. If the build reaches Vite, confirm generated output and no jspdf-related errors. Record exact output in the existing central OpenSpec change evidence.

## Non-goals
Do not change test semantics, replace Vitest, add Jest, or fix unrelated property-based test typing that is excluded from the production build.
