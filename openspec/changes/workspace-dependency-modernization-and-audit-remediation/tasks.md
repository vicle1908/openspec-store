# Tasks

## 1. Workstation Root Manifest Modernization

- [x] 1.1 Update `newman` to `^6.2.2` and `newman-reporter-htmlextra` to `^1.23.1` in `/Users/androidteam/package.json`
- [x] 1.2 Bump overrides (`sharp` 0.35.5, `jose` 6.2.12, `csv-parse` 7.0.3) and remove breaking `@faker-js/faker` override
- [x] 1.3 Verify CLI tools execution (`npx newman --version`, `npx newman run -r htmlextra --help`, `npx gitnexus --version`, `npx pyright --version`)

## 2. Realtime Frontend Modernization & Dual Overrides

- [x] 2.1 Upgrade `react` and `react-dom` to `19.3.0` with matching `@types/react` and `@types/react-dom`
- [x] 2.2 Upgrade `axios` (`^1.20.0`), `@tanstack/react-query` (`^5.104.1`), `ably` (`^2.29.0`), `react-router-dom` (`^7.18.4`), and test dependencies
- [x] 2.3 Synchronize dual overrides for `dompurify` (`>=3.4.16`) and `brace-expansion` (`>=5.0.12`) in both `overrides` and `pnpm.overrides`
- [x] 2.4 Verify type-check (`tsc --noEmit`), property tests (`CorrelationCoefficientDisplay.property.test.tsx`), and production build

## 3. MCP Router Platform Upgrades & Security Overrides

- [x] 3.1 Upgrade root devDependencies (`prettier` 3.9.9, `@types/node` 26.6.4, `@types/react` 19.3.0, `@typescript-eslint` 8.71.0, `eslint` 10.12.0, `knip` 6.39.0, `turbo` 2.11.7)
- [x] 3.2 Upgrade package dependencies (`@modelcontextprotocol/sdk` ^1.32.0, Radix UI suite, `@codemirror/*`, `zustand` 5.0.15, `semver` 7.8.5, `posthog-js` 1.435.8)
- [x] 3.3 Pin `pnpm.overrides` for `fast-uri`, `ip-address`, `hono`, `brace-expansion`, `undici`, and `image-size`
- [x] 3.4 Verify Electron typecheck (`pnpm --filter @mcp_router/electron run typecheck`), full build (`pnpm run build`), and lockfile hygiene (no `package-lock.json`)

## 4. Prime Agent Platform Upgrades & Workspace Deduplication

- [x] 4.1 Upgrade `@anthropic-ai/sandbox-runtime` to `^0.0.77` in root and `packages/coding-agent/examples/extensions/sandbox`
- [x] 4.2 Upgrade `concurrently` (`^10.0.5`), `tsx` (`^4.23.15`), and `get-east-asian-width` (`^1.7.0`)
- [x] 4.3 Add root security overrides for `ip-address` (`>=10.7.1`) and `brace-expansion` (`>=5.0.12`)
- [x] 4.4 Verify release gate (`npm run check` with Biome, tsgo, check:installer, check:browser-smoke)

## 5. Audit Verification & Upstream Residual Documentation

- [x] 5.1 Re-run audit across all 4 targets (`npm audit` and `pnpm audit`)
- [x] 5.2 Record verifiable evidence of unpatched upstream residuals (`http-cache-semantics`, `extract-zip`, `node-forge`, `basic-ftp`, `braces`)
