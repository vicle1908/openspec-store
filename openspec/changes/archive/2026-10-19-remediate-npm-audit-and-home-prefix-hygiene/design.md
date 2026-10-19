# Design: Remediate NPM/PNPM Audit Regressions and Enforce Home-Directory Prefix Hygiene

## Context

See `proposal.md - Why` for problem motivation. Four technical constraints shape the remediation design:
1. **`@npmcli/config` Prefix Discovery**: `Config.loadLocalPrefix()` (`/opt/homebrew/lib/node_modules/npm/node_modules/@npmcli/config/lib/index.js:689-712`) walks upward from `cwd` and stops at the first ancestor where `hasPackageJson || await dirExists(p, 'node_modules')` is true. Removing `~/package.json` and `~/package-lock.json` is insufficient if `~/node_modules` exists: `npm prefix`, `npm audit`, and `npm audit fix` invoked from `/Users/androidteam/Developer` still adopt `/Users/androidteam` as `localPrefix` and fail inside `Arborist.loadVirtual()` (`@npmcli/arborist/lib/arborist/load-virtual.js:39-48`) with `ENOLOCK`.
2. **`npm audit -g` vs `Arborist.reify()` Quick Audit**: During `npm update -g`, `Arborist.reify()` (`@npmcli/arborist/lib/arborist/reify.js:1221-1247`) submits a quick audit of `/Users/androidteam/.npm-global/lib/node_modules` and `reifyOutput()` prints `run npm audit fix`, whereas `Arborist.audit({ global: true })` (`@npmcli/arborist/lib/arborist/index.js:252-257`) unconditionally throws `EAUDITGLOBAL`.
3. **`pnpm@12.14.0` Exotic Subdependency Policy**: Native Rust `pnpm@12.14.0` in `platform/mcp-router` enables `blockExoticSubdeps` by default, which rejects `@electron/rebuild@^4.2.0`'s git-repository transitive dependency `@electron/node-gyp` with `ERR_PNPM_EXOTIC_SUBDEP` during lockfile resolution unless `blockExoticSubdeps: false` is set in `pnpm-workspace.yaml`.
4. **Central OpenSpec Multi-Root Governance**: `platform/openspec-store` is the central planning and governance repository (`allowedEditRoots: ["/Users/androidteam/Developer/platform/openspec-store"]`). Mutations to workstation paths (`$HOME`, `~/.local/share/home-toolchain`, `~/.npm-global`) and external repositories (`platform/mcp-router`, `tdt/realtime/frontend`, `legacy/kafka-microservices`) are governed as explicit cross-root execution and verification gates with separate Git histories and commits.

## Goals / Non-Goals

**Goals:**
- Ensure `npm prefix` executed from `/Users/androidteam/Developer` (and any non-manifest directory beneath it) resolves to that directory rather than `/Users/androidteam`, and detect any future `$HOME` `node_modules` or lockfile creation in `inventory-workstation-toolchain.py`.
- Eliminate all newly published Critical, High, Moderate, and Low advisories that have compatible upstream fixes across `~/.local/share/home-toolchain`, `platform/mcp-router`, `tdt/realtime/frontend`, and `legacy/kafka-microservices`.
- Reconcile `openspec/specs/npm-audit-remediation/spec.md`, `docs/mac-development-setup.md`, and `docs/runbooks/workstation-toolchain-inventory.md` with measured residual counts, active CLI versions (`bru@4.2.1`, `yaml-language-server@2.0.0`), and current upstream no-fix boundaries (`patched_versions: null`).
- Clean retired dot-symlinks and empty `@scope` directories in `~/.npm-global`.

**Non-Goals:**
- Mutating tracked files in `~/Omniroute` or `~/.hermes` (governed by separate upstream-clean worktree contracts).
- Applying `--force` downgrades (`newman@5.3.2`, `markdownlint-cli2@0.0.4`) or unvetted forks for unpatched upstream advisories.
- Altering the `prime-agent` `target_misalignment` authority check in `inventory-workstation-toolchain.py` covered by `test-version-authority-governance.py` or the `bru` candidate classification in `report-toolchain-candidates.py` covered by `tests/test_portable_workstation_slice_a.py`.

## Decisions

### Decision 1: Detect `$HOME` `node_modules` and Stray Lockfiles in `inventory-workstation-toolchain.py`
- **Choice**:
  1. Extend `PrefixReconciliation` in `platform/openspec-store/scripts/inventory-workstation-toolchain.py` with `home_prefix_hijacked: bool = False` and `home_forbidden_artifacts: list[str] = field(default_factory=list)`.
  2. Update `check_prefix_reconciliation(declared_prefix: str, home_dir: Path | None = None, workspace_dir: Path | None = None) -> PrefixReconciliation` to inspect `home_dir` (defaulting to `Path.home()`) for `("package.json", "package-lock.json", "pnpm-lock.yaml", "pnpm-workspace.yaml", "bun.lock", "bun.lockb", "yarn.lock", "node_modules")` and verify whether `npm prefix` executed in `workspace_dir` (defaulting to `home_dir / "Developer"`) resolves to `home_dir`. Set `home_prefix_hijacked = bool(home_forbidden_artifacts) or (workspace_npm_prefix == str(home_dir.resolve()))`, `has_split = (npm_resolved != declared_resolved) or (npm_resolved != pipeline_prefix) or home_prefix_hijacked`, and `status = "split_detected" if has_split else "reconciled"`.
  3. In `main()` text output (`=== Workstation Prefix Reconciliation ===`), print `  home prefix hijacked:` and `  home forbidden artifacts:` while preserving `  Status:                      {prefix_check.status.upper()}` (22 spaces after `Status:`) so `workstation-daily-update.sh:813` (`grep -q "Status:                      SPLIT_DETECTED"`) triggers automatically.
  4. Add `"adhoc-home": home / "node_modules"` to `locations` in `inventory_tools()`, populate `is_sanctioned` / `sanctioned_replacement` on `ToolCopy` and `unsanctioned_copies` on `ToolInventoryItem`, and surface `unsanctioned_count` and `summary["unsanctioned"]` / `items["unsanctioned"]` in `reconcile_with_manifest()`.
- **Rationale**: Optional `home_dir` and `workspace_dir` parameters enable deterministic unit testing in `scripts/test-version-authority-governance.py` using `tempfile.TemporaryDirectory()` without mutating the live host `$HOME`.

### Decision 2: Verify `~/.local/bin` Symlinks Before Removing `$HOME` Package Artifacts
- **Choice**: Before removing `/Users/androidteam/node_modules`, `/Users/androidteam/pnpm-lock.yaml`, `/Users/androidteam/pnpm-workspace.yaml`, `/Users/androidteam/bun.lock`, `/Users/androidteam/bun.lock.bun-backup-20260813_100505`, and `/Users/androidteam/package.json.bun-backup-20260813_100505`, verify that `~/.local/bin/{bru,yaml-language-server,newman-reporter-htmlextra}` resolve to `/Users/androidteam/.local/share/home-toolchain/node_modules/.bin/*` and execute cleanly.
- **Rationale**: Running Zed `yaml-language-server` processes invoke `/Users/androidteam/.local/bin/yaml-language-server` (`-> ../share/home-toolchain/node_modules/.bin/yaml-language-server`). Confirming that no active symlink points into `/Users/androidteam/node_modules` guarantees zero disruption to running language servers.

### Decision 3: Upgrade `handlebars` Override, Direct Dependencies, and In-Range Pins in `~/.local/share/home-toolchain`
- **Choice**:
  - `~/.local/share/home-toolchain/package.json` contains 4 direct `dependencies`: raise `"@usebruno/cli"` (`"^4.2.0"` -> `"^4.2.1"`) and `"yaml-language-server"` (`"^1.24.0"` -> `"^2.0.0"`), while keeping `"newman-reporter-htmlextra": "^1.23.1"` and `"pyright": "^1.1.414"`. Do **not** add `"newman"` to `dependencies` (authoritative `newman` is `/opt/homebrew/bin/newman`; `node_modules/newman` is installed automatically via `newman-reporter-htmlextra@1.23.1`'s `peerDependencies: { "newman": "^6.0.0" }`).
  - In the 22 top-level string `overrides` (+ 1 scoped `@usebruno/requests` override), raise `"handlebars"` (`"4.7.9"` -> `"4.7.10"`), `"uuid"` (`"14.0.2"` -> `"14.0.3"`), `"qs"` (`"6.16.0"` -> `"6.16.1"`), `"fast-uri"` (`"4.2.1"` -> `"4.2.2"`), `"ip-address"` (`"10.7.3"` -> `"10.7.4"`), and `"hono"` (`"4.13.12"` -> `"4.13.13"`).
  - Run `npm update` (not merely `npm install`) in `/Users/androidteam/.local/share/home-toolchain` so peer `newman` (`6.2.2 -> 6.2.3`), `js-yaml` (`5.4.2 -> 5.5.0` via `">=4.3.2"`), and all in-range transitive dependencies are updated.
- **Rationale**: Verified in an isolated `/tmp` APFS clone: after `npm update`, `npm outdated` exits 0 with empty output, `npm outdated --all --json` has 0 in-range (`current != wanted`) moves, `npm audit --json` drops from `11 (4 critical, 7 high)` to `10 (0 critical, 10 high)`, and `bru --version` (`4.2.1`), `yaml-language-server --version` (`2.0.0`), and `newman-reporter-htmlextra --version` (`1.23.1`) all exit 0.

### Decision 4: Remediate 10 Patched Advisories in `platform/mcp-router` Under `pnpm@12.14.0`
- **Choice**: In `platform/mcp-router/pnpm-workspace.yaml`:
  1. Add `blockExoticSubdeps: false` so `pnpm@12.14.0` permits `@electron/rebuild -> @electron/node-gyp`.
  2. Update/add overrides:
     - `"proxy-addr@<2.0.8": ">=2.0.8"` (fixes Critical `GHSA-jqcg-44mw-7w3h`)
     - `"shell-quote@<1.11.0": ">=1.11.0"` (replaces `"shell-quote@<1.10.0": "1.10.0"`, fixing Critical `GHSA-pqg4-j6r4-53mv`)
     - `"compression@<1.8.2": ">=1.8.2"` (fixes High `GHSA-vc2v-76pw-4v95`)
     - `"http-cache-semantics@<=4.2.0": ">=4.3.0"` (fixes High `GHSA-ch52-4w7c-c8xp`)
     - `"source-map-js@<1.2.2": ">=1.2.2"` (fixes High `GHSA-68fv-2mgg-jv7q`)
     - `"postcss-selector-parser@<7.1.6": ">=7.1.6"` (replaces `<7.1.3` / `<6.1.3` pins, fixing Moderate `GHSA-rj75-hqrm-r3gf`)
     - `"handlebars@<4.7.10": ">=4.7.10"` (replaces `<4.7.9`)
     - `"electron@<41.10.7": ">=41.10.7"` and update `apps/electron/package.json` `"electron": "^41.10.7"` (fixes 4 High Electron advisories `GHSA-hq2x-r82h-9wj4`, `GHSA-gr2m-v5gq-v685`, `GHSA-j84w-jfhq-vhvj`, `GHSA-9qh4-3jw8-366w`).
  3. Run `/opt/homebrew/bin/pnpm install`, rebuild native Electron addons (`better-sqlite3`, `argon2`), and verify `pnpm typecheck`, `pnpm test`, and `pnpm build`.
- **Rationale**: Verified in `/tmp`: reduces `pnpm audit` from 15 advisories (`2C/11H/2M`) to the 5 unpatched upstream residuals (`0C/4H/1M`, all `patched_versions: null`: `extract-zip <=2.0.1` x2, `braces <=3.0.3`, `node-forge <=1.4.0`, `sprintf-js <=1.1.3`). Commits in `platform/mcp-router` must use `GRAPHIFY_SKIP_HOOK=1` when reconciling tracked `graphify-out/` artifacts.

### Decision 5: Dual-Override Parity in `tdt/realtime/frontend` and Overrides in `legacy/kafka-microservices`
- **Choice**:
  - In `tdt/realtime/frontend/package.json`, add `"http-cache-semantics": ">=4.3.0"` and `"source-map-js": ">=1.2.2"` to both `overrides` and `pnpm.overrides` (and align `overrides.dompurify: ">=3.4.17"` and `pnpm.overrides` `handlebars: "4.7.10"`, `qs: "6.16.1"`, `uuid: "14.0.3"`, `smol-toml: "1.9.1"`, `fast-uri: "4.2.2"`, `dompurify: ">=3.4.17"`), run `npm audit fix`, remove the stale gitignored `package-lock 2.json` (matched by `tdt/realtime/.gitignore:64`), and verify `npm run type-check` and `npm run build` exit 0 with `0` audit vulnerabilities across both `npm audit` and `pnpm audit`.
  - In `legacy/kafka-microservices/package.json`, add `"overrides": { "smol-toml": ">=1.9.1", "katex": ">=0.19.0" }`, exclude `"#docs/deprecated"` in `lint:md` / `lint:md:fix`, refresh `package-lock.json` on disk (note: `package-lock.json` is listed in `legacy/kafka-microservices/.gitignore:27`), and verify `npm run lint:md` exits 0 (`Linting: 104 files; Summary: 0 issues in 0 files`) with only the 5 High `braces <=3.0.3` unpatched residuals remaining. Use path-scoped staging (`git add package.json`) so the 89 unrelated modified/untracked files on `feature/temporal-workflow-orchestration` remain untouched.

## Risks / Trade-offs

- **Electron ABI Upgrade (`39.8.10 -> 41.10.7`) in `platform/mcp-router`**: Upgrading `electron` changes the Electron Node ABI, requiring `electron-rebuild` of `better-sqlite3` and `argon2`. Mitigation: Follow the `electron-forge-macos-ts7-node26-packaging` procedure (`pnpm install` triggers `postinstall: electron-rebuild`, verified by `pnpm -r test`, `pnpm typecheck`, and `pnpm build`).
- **Graphify Post-Commit Hook in `platform/mcp-router`**: Committing in `platform/mcp-router` triggers `.git/hooks/post-commit`, which can asynchronously dirty tracked `graphify-out/` files. Mitigation: Stage regenerated `graphify-out/` files and commit with `GRAPHIFY_SKIP_HOOK=1`, then verify `git status --short` is empty.
- **Unrelated Worktree Changes in `legacy/kafka-microservices`**: `legacy/kafka-microservices` has 89 modified/untracked files on `feature/temporal-workflow-orchestration`. Mitigation: Strictly scope `git diff` and `git add` to `package.json package-lock.json`.
