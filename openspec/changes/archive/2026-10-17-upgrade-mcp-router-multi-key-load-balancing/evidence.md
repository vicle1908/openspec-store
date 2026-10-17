# Verification Evidence: `upgrade-mcp-router-multi-key-load-balancing`

- **Change Name**: `upgrade-mcp-router-multi-key-load-balancing`
- **Planning Store**: `/Users/androidteam/Developer/platform/openspec-store` (`store_id: openspec-store`)
- **External Implementation Root**: `/Users/androidteam/Developer/platform/mcp-router`
- **Date**: `2026-10-16`

## 1. Monorepo Typecheck (`npx pnpm@10.22.0 typecheck`)

- **Command**: `npx pnpm@10.22.0 typecheck` (`turbo run typecheck`)
- **Exit Code**: `0`
- **Result**: 8/8 tasks succeeded (`@mcp_router/shared`, `@mcp_router/remote-api-types`, `@mcp_router/ui`, `@mcp_router/cli`, `@mcp_router/electron`).

## 2. Unit & Workspace Tests (`npx pnpm@10.22.0 test`)

- **Command**: `npx pnpm@10.22.0 --filter @mcp_router/electron test && npx pnpm@10.22.0 test`
- **Exit Code**: `0`
- **Results**:
  - `@mcp_router/electron`: **64/64 tests passed across 16 suites**:
    - `QuotaErrorDetector`: HTTP 429/402 exceptions, `Retry-After` header/field extraction, quota message matching, 401 invalid key vs quota distinction, Tavily-style `CallToolResult` JSON `"status": 429` payload detection, `isError: true` quota text detection, and false-positive prose search defense (`isError: false` prose text containing `"HTTP 429 Too Many Requests"` does not trigger cooldown via `QuotaErrorDetector.inspectToolResult`).
    - `MCPKeyPoolManager`: `round-robin`, `weighted-round-robin`, `tiered-fallback`, and `least-used` selection; `url-template`, `bearer-token`, `custom-header`, `env-var`, and `cli-arg` derived config injection (preserving `inputParams` and JIT-decrypting `mcpr-secret:v1:` secrets); primary client slot seeding via `registerClientSlot`; hot-reload slot teardown via `reconcileServer`; transparent failover on HTTP 429 exception and 429 tool payload; RPM limit enforcement, `resetKeyCooldown`, `resetKeyUsage`, and `reset()` teardown.
    - `security-utils`: `secretToStorage` / `decryptSecret` (`mcpr-secret:v1:` prefix), `sanitizeForSecurityBoundary` (including shared non-circular DAG reference preservation), `redactSensitiveText`, `normalizeRemoteMcpUrl` (including IPv6 `[::1]` and IPv4-mapped IPv6 `[::ffff:127.0.0.1]` SSRF rejection), `normalizeRemoteMcpUrlTemplate` (raw & percent-encoded authority placeholder rejection + `{{KEY}}` preservation), `interpolateRemoteMcpUrl` (both literal `{{KEY}}`/`${KEY}` and WHATWG percent-encoded `%7B%7BKEY%7D%7D`/`%24%7BKEY%7D` in pathname), and `validateCustomHeaders` (CRLF / control-char rejection).
    - `TokenManager`: legacy token compatibility, expired token compatibility, `neverExpires: true` / `expiresIn: 0` omitting `expiresAt`, `rotateToken` preserving `serverAccess`, and `rotateToken` preserving `neverExpires` (`expiresAt === undefined`) when `options` is omitted.
    - `MCPHttpServer Authorization compatibility` & `service-retirement` suites: all passed.
  - `@mcp_router/shared`: **4/4 tests passed**.
  - `@mcp_router/cli`: **3/3 tests passed**.

## 3. Locale, Formatting, Knip, and Build Gates

- **i18n Scanner**: `node tools/find-unused-i18n.mjs` $\rightarrow$ `No unused i18n keys found.` (`exit code 0`, synchronized across `en.json`, `ja.json`, `zh.json`).
- **Prettier Formatting**: `npx prettier --write` / `--check` on all 38 touched files $\rightarrow$ **0 formatting issues** (`exit code 0`).
- **Knip Unused Export Check (`npx pnpm@10.22.0 knip`)**:
  - Verified that **zero** newly added or modified files (`quota-error-detector.ts`, `mcp-key-pool-manager.ts`, `ServerDetailsKeyPool.tsx`, `mcp-types.ts`, `token-types.ts`, `servers.ts`) appear in `knip`'s unused files or unused exports lists (overall `knip` command exits `1` solely due to 7 pre-existing unused files and 18 pre-existing unused exports in untouched legacy modules such as `LoginScreen.tsx`, `mcp-apps-manager.service.ts`, and `ProjectSettingsModal.tsx`).
- **ESLint Note**: `@typescript-eslint/parser@8.71.0` / `typescript-estree` does not yet support the workspace's TypeScript `7.0.2` AST API (`typescript-eslint does not support TS 7.0`, upstream issue `#10940`). Custom type placement rules (`no-scattered-types`, `no-type-reexport`) and formatting were verified directly against all touched files alongside `tsc --noEmit` (`8/8` passing).
- **Production Build**: `npx pnpm@10.22.0 build` (`turbo run build`) $\rightarrow$ 4/4 build targets succeeded (`exit code 0`).
- **Whitespace / Diff Check**: `git diff --check` $\rightarrow$ `0` warnings/errors (`exit code 0`).
- **OpenSpec Strict Validation**: `openspec validate "upgrade-mcp-router-multi-key-load-balancing" --strict --store openspec-store` $\rightarrow$ `Change 'upgrade-mcp-router-multi-key-load-balancing' is valid`.

## 4. Edge-Case Safeguards & Path-Scoped Git Commit Verification (2026-10-17)

- **External Git Commits (`/Users/androidteam/Developer/platform/mcp-router`)**:
  - Commit `68c047d9f2902ff3f784a6982aab0697d61cd451` (`feat(mcp-router): add multi-key pool load balancing, quota failover, and JIT secret encryption`, `41` files changed, `+5022 -413`).
  - Commit `8550cb9cb5ad66ac745e718f5955b1d0d6659388` (`fix(mcp-router): propagate resource read 429 failover and harden secret edit masking`, `4` files changed, `+163 -39`).
- **Verified Edge-Case Safeguards & Bug Fixes (`11/11` tasks complete)**:
  - **Safeguard 1 (WHATWG URL Path Percent-Encoding — Task 2.2)**: `remote-url-security.ts:235-238` (`interpolateRemoteMcpUrl`) and `mcp-client.ts:88` replace both literal `{{KEY}}`/`${KEY}` and percent-encoded `%7B%7BKEY%7D%7D`/`%24%7BKEY%7D` with `encodeURIComponent(secret)`.
  - **Safeguard 2 (False-Positive Quota Defense on Tool Search Outputs — Task 3.1)**: `quota-error-detector.ts:214-279` gates prose matching on `isExplicitError` (`resObj.isError === true`) or strict JSON `status === 429` / `402` (`64/64` unit tests pass in `apps/electron`).
  - **Safeguard 3 (Renderer IPC Secret Boundary — Tasks 2.1 & 4.1)**: `mcp-server-manager.repository.ts:211-215` retains encrypted `mcpr-secret:v1:` secrets in `mapRowToEntity` via `secretToStorage` and decrypts strictly just-in-time in `mcp-client.ts` (`decryptIfSecret`) and `mcp-key-pool-manager.ts`.
  - **Safeguard 4 (Hot-Reload Reconnect Failure State — Task 3.3)**: `mcp-server-manager.ts:433-462` transitions `server.status = "error"`, records `server.errorMessage`, and emits `server-updated` when `updateServer` reconnection fails.
  - **Bug Fix 1 (`readResourceByUri` Multi-URI Variant Quota Propagation)**: `request-handlers.ts:411-415` immediately rethrows `429` quota and `401` invalid-key errors inside `readResourceByUri`'s `uriVariants` loop so fallback URI errors never mask upstream quota errors from `executeWithFailover`.
  - **Bug Fix 2 (`ServerDetailsRemote.tsx` Edit-Mode Custom Header Secret Masking)**: `ServerDetailsRemote.tsx:140-200` masks sensitive custom header values (`SENSITIVE_HEADER_PATTERN`) with `type="password"` and an Eye/EyeOff toggle in edit mode.
  - **Bug Fix 3 (`ServerDetailsKeyPool.tsx` Encrypted Key Pre-Hydration on Focus)**: `ServerDetailsKeyPool.tsx:423-456` binds `value={revealedSecrets[key.id] ?? key.secret}` across both masked and unmasked states and pre-hydrates decrypted secret values on `onFocus` when `key.secret` carries `mcpr-secret:v1:`.
