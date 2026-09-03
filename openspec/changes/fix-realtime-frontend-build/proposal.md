# Proposal: fix-realtime-frontend-build

## Why
Fresh verification of the npm audit remediation found that `realtime/frontend` still fails its declared production build before Vite runs. TypeScript references Jest types that are not declared or locked, and property-based test setup code is compiled despite being test-only. This prevents a clean install from producing a successful build and leaves the verification change with an owner-visible defect.

## What Changes
- Align the frontend TypeScript configuration with the actual Vitest test environment and build boundary.
- Remove the stale Jest type dependency from the production TypeScript program and exclude test-only setup files from the application build.
- Preserve the existing Vitest test configuration and ensure the production build still type-checks application code and runs Vite.
- Update verification evidence to show the defect was fixed rather than merely classified as pre-existing.

## Scope
Only `/Users/androidteam/Developer/realtime/frontend` TypeScript configuration and directly related test/build configuration are in scope. No dependency downgrade, audit exception, or unrelated test rewrite.

## Expected Outcome
`npm run build` exits 0 on a clean dependency tree; `npm audit` remains at 0 vulnerabilities; the application bundle still builds successfully.
