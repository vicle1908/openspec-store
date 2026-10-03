# Design: Workspace Dependency Modernization & Audit Remediation

## Context
See `proposal.md` for overall motivation. Across the workspace, multiple package managers operate side-by-side:
- `/Users/androidteam/`: Root CLI environment managing developer tools (`npm`).
- `platform/mcp-router`: Multi-package monorepo strictly managed with `pnpm` (pnpm workspaces + Electron + tRPC).
- `platform/prime-agent`: Multi-package monorepo managed with `npm` workspaces.
- `tdt/realtime/frontend`: Web application managed with `npm` while connecting to an ecosystem monorepo reading `pnpm` configurations.

## Goals / Non-Goals

**Goals:**
- Eliminate fixable vulnerabilities using semver-compatible upgrades and version overrides.
- Establish strict dual-override parity (`overrides` + `pnpm.overrides`) in `tdt/realtime/frontend`.
- Remove unneeded version constraints to modernize to React 19.3.0 and latest tooling.
- Strictly maintain lockfile hygiene: zero `package-lock.json` in `mcp-router`, zero `pnpm-lock.yaml` in `realtime/frontend`.
- Document all unpatched upstream residuals with `patched: <0.0.0` markers.

**Non-Goals:**
- Upgrading to unpatched major releases that break public APIs without available patches (e.g. `braces` 3.0.3, `node-forge` 1.4.0, `basic-ftp` 6.2.0, `ably` 1.2.14 downgrade).
- Bumping `@biomejs/biome` to 2.5 in `prime-agent` until upstream schema and linter rules (`useOptionalChain`) are triaged in a separate code-cleanup change.

## Decisions

### Decision 1: Dual-Manager Lockstep in `tdt/realtime/frontend`
- **Choice**: Duplicate all dependency overrides in both `"overrides"` and `"pnpm.overrides"` in `package.json`.
- **Rationale**: `npm` only reads `"overrides"`, while `pnpm` reads `"pnpm.overrides"`. Lacking parity causes CI (npm) or local developer workflows (pnpm) to resolve different versions of transitive dependencies like `dompurify` and `brace-expansion`.

### Decision 2: Remove Faker Override in Workstation Root
- **Choice**: Omit `"@faker-js/faker": "10.6.0"` from `/Users/androidteam/package.json`.
- **Rationale**: Newman v6 depends on `postman-collection@4.4.0`, which calls `faker.address.city`. Faker v6+ removed the `address` namespace. Pinning Faker to v10 caused a fatal runtime crash upon CLI execution.

### Decision 3: Sandbox Runtime Deduplication in `platform/prime-agent`
- **Choice**: Update `@anthropic-ai/sandbox-runtime` in root `devDependencies` and `packages/coding-agent/examples/extensions/sandbox` simultaneously to `^0.0.77`.
- **Rationale**: Keeps the sandbox extension aligned with root runtime without pulling older transitive dependencies (`node-forge` older versions).

## Risks / Trade-offs

- **Risk: Upstream Unpatched Advisories**: Five packages have known vulnerabilities without upstream fixes (`<0.0.0`).
  - *Mitigation*: Fail-closed documentation. Rather than forcing `--force` downgrades (which break modern protocols like Ably or proxy agents), document them as upstream residuals.
- **Risk: React 19.3 API Shifts**: React 19.3 updates internal hook behaviors.
  - *Mitigation*: Validated with full property-based tests (`CorrelationCoefficientDisplay.property.test.tsx`), TypeScript typechecking, and production bundle compilation.
