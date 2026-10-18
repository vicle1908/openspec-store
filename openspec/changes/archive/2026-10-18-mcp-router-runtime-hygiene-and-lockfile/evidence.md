# Evidence: MCP Router Runtime Hygiene and Lockfile Reconciliation

## Execution Summary

- **Repository Root**: `/Users/androidteam/Developer/platform/mcp-router`
- **Toolchain**: `pnpm@12.14.0` (/opt/homebrew/bin/pnpm), Node.js `v26.12.0`, macOS Darwin arm64
- **Hygiene Commit SHA**: `266e16702de30323ed3649560949b4eabf7397b1`
- **Commit Subject**: `chore(hygiene): reconcile pnpm 12.14.0 lockfile header and ignore .graphify`

## 1. Working Tree Hygiene & Lockfile Reconciliation

### Lockfile Header Reconciled
- Pre-flight `git diff pnpm-lock.yaml` inspection confirmed the native multi-document `packageManagerDependencies` header (+158 lines for `pnpm@12.14.0` and its 14 `@pnpm/exe.*` optional platform packages) completing commit `7bce8df`.
- Removed stale `ts-node` specifier in `apps/electron` devDependencies within `pnpm-lock.yaml` matching commit `1c13b09` where `ts-node` was replaced by `tsx` and esbuild.
- Reconciled `onlyBuiltDependencies` in `pnpm-workspace.yaml` to pnpm 12's native `allowBuilds` mapping with `argon2: true`, resolving `ERR_PNPM_IGNORED_BUILDS`.

### Ignore Rules Hardening & Ephemeral State Removal
- Edited `/Users/androidteam/Developer/platform/mcp-router/.gitignore` to add `.graphify/` under `# graphify internal state (regenerable)`.
- Safely removed untracked `.graphify/` directory without `rm -rf`:
  ```bash
  rm -f /Users/androidteam/Developer/platform/mcp-router/.graphify/needs_update && rmdir /Users/androidteam/Developer/platform/mcp-router/.graphify
  ```
- Tracked core `graphify-out/` artifacts (`graph.json`, `graph.html`, `GRAPH_REPORT.md`, `manifest.json`, `.graphify_labels.json`, `.graphify_labels.json.sig`) were staged and committed alongside `.gitignore` and `pnpm-lock.yaml`.
- Executed commit with `GRAPHIFY_SKIP_HOOK=1` to prevent `.git/hooks/post-commit` from triggering an asynchronous re-indexing:
  ```bash
  GRAPHIFY_SKIP_HOOK=1 git commit -m "chore(hygiene): reconcile pnpm 12.14.0 lockfile header and ignore .graphify"
  ```
  Result: commit `266e167` (9 files changed, 871 insertions(+), 121220 deletions(-)).

## 2. Gate Verification Evidence

### A. Frozen Lockfile Install Gate
- **Command**: `/opt/homebrew/bin/pnpm install --frozen-lockfile`
- **Exit Code**: `0`
- **Output**:
  ```
  [WARN] The "$" version reference syntax in overrides is deprecated (used by: @types/react, @types/react-dom). Define the version in a catalog and reference it with the "catalog:" protocol instead. See https://pnpm.io/catalogs
  Scope: all 7 workspace projects
  Agent skills awaiting approval: @trpc/client, @trpc/server.
  Run "pnpm approve" to review them.
  ✓ Lockfile passes supply-chain policies (verified 5m ago)
  Lockfile is up to date, resolution step is skipped
  Done in 297ms using pnpm v12.14.0
  ```

### B. Monorepo Test Suites Gate
- **Command**: `/opt/homebrew/bin/pnpm -r test`
- **Exit Code**: `0`
- **Test Results Breakdown**:
  * `apps/cli`: 3 tests passed, 1 suite, 0 failed
  * `packages/shared`: 4 tests passed, 0 failed
  * `apps/electron`: 64 tests passed, 16 suites, 0 failed
  * **Total**: 71 tests passed across 17 suites, 0 cancelled, 0 failed, 0 skipped

### C. TypeScript Typecheck Gate
- **Command**: `/opt/homebrew/bin/pnpm typecheck`
- **Exit Code**: `0`
- **Output**: Clean exit with 0 diagnostic errors across all monorepo packages.

### D. Monorepo Build Gate
- **Command**: `/opt/homebrew/bin/pnpm build`
- **Exit Code**: `0`
- **Output**: Clean compilation and packaging across all packages.

### E. Clean Working Tree Verification
- **Command**: `git status --porcelain`
- **Exit Code**: `0`
- **Output**: `(empty)` — Clean working tree on `HEAD` (commit `266e16702de30323ed3649560949b4eabf7397b1`).
