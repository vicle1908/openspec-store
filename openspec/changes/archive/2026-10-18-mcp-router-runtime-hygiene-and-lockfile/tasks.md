# Tasks: MCP Router Runtime Hygiene and Lockfile Reconciliation

## 1. Lockfile reconciliation

- [x] 1.1 Validate `platform/mcp-router/pnpm-lock.yaml` against `"packageManager": "pnpm@12.14.0"` using host `pnpm install --frozen-lockfile` (`pnpm@12.14.0`), avoiding `npx pnpm@10.22.0` (which crashes with ENOENT during self-switch to incomplete `~/Library/pnpm/.tools/pnpm/12.14.0/bin/pnpm` stub)
- [x] 1.2 Verify `git diff pnpm-lock.yaml` contains exclusively the native multi-document `packageManagerDependencies` header (+158 lines for `pnpm@12.14.0` and its 14 `@pnpm/exe.*` optional platform packages) completing commit `7bce8df`, with zero unexpected workspace dependency drift, and stage/commit `pnpm-lock.yaml`

## 2. Ignore rules hardening

- [x] 2.1 Add `.graphify/` to `platform/mcp-router/.gitignore` (preserving existing lines 88–98 that ignore `graphify-out/cache/`, `graphify-out/.graphify_*`, `graphify-out/needs_update`, `graphify-out/.graphify_root`, `graphify-out/.rebuild.lock`, `graphify-out/20*/` while explicitly tracking core `graphify-out/` artifacts)
- [x] 2.2 Remove untracked `.graphify/` directory and stage the 6 regenerated tracked `graphify-out/` files (`graph.json`, `graph.html`, `GRAPH_REPORT.md`, `manifest.json`, `.graphify_labels.json`, `.graphify_labels.json.sig`) produced by `.git/hooks/post-commit` following commit `abb7c11`
- [x] 2.3 Commit reconciled hygiene changes (`pnpm-lock.yaml`, `.gitignore`, `graphify-out/*`) with `GRAPHIFY_SKIP_HOOK=1` to prevent post-commit hook from spawning an asynchronous rebuild that re-dirties `graphify-out/`, and verify `git status --porcelain` in `platform/mcp-router` is empty

## 3. Monorepo gate verification

- [x] 3.1 Run host `pnpm -r test` (`pnpm@12.14.0`) across all workspace projects and verify all test suites pass cleanly
- [x] 3.2 Run host `pnpm typecheck` and `pnpm build` (`pnpm@12.14.0`) to confirm zero compilation or packaging regressions across the monorepo
