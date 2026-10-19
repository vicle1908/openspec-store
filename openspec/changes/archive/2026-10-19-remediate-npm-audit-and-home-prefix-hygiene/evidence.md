# Evidence: Remediate NPM/PNPM Audit Regressions and Enforce Home-Directory Prefix Hygiene

- **Change**: `remediate-npm-audit-and-home-prefix-hygiene`
- **Store**: `openspec-store` (`/Users/androidteam/Developer/platform/openspec-store`)
- **Date**: `2026-10-19`
- **Privacy / Security Posture**: Value-blind (no raw credentials, API keys, or secrets recorded).

---

## 1. Central Store Inventory, Prefix-Hijack Detection & Documentation (`platform/openspec-store`)

### Tasks 1.1, 1.2 & 1.3 (`scripts/inventory-workstation-toolchain.py` & `scripts/test-version-authority-governance.py`)

- **Files Modified**:
  - `/Users/androidteam/Developer/platform/openspec-store/scripts/inventory-workstation-toolchain.py`
  - `/Users/androidteam/Developer/platform/openspec-store/scripts/test-version-authority-governance.py`
- **Verification Commands & Results**:
  1. `uv run --directory /Users/androidteam/Developer/platform/openspec-store pytest scripts/test-version-authority-governance.py`
     - **Exit code**: `0`
     - **Output**: `33 passed in 8.65s` (including `TestHomePrefixHijackReconciliation.test_clean_home_dir_reports_not_hijacked`, `test_dirty_home_dir_with_node_modules_and_lockfile_reports_hijacked`, and `test_unsanctioned_adhoc_home_copy_reported_with_sanctioned_replacement`)
  2. `uv run --directory /Users/androidteam/Developer/platform/openspec-store pytest`
     - **Exit code**: `0`
     - **Output**: `277 passed in 102.20s`

### Task 1.4 (`docs/mac-development-setup.md` & `docs/runbooks/workstation-toolchain-inventory.md`)

- **Files Modified**:
  - `/Users/androidteam/Developer/platform/openspec-store/docs/mac-development-setup.md`
  - `/Users/androidteam/Developer/platform/openspec-store/docs/runbooks/workstation-toolchain-inventory.md`
- **Summary**:
  - Updated Bruno (`@usebruno/cli`) active version to `4.2.1` and `yaml-language-server` to `2.0.0` (with `newman-reporter-htmlextra@1.23.1`, `pyright@1.1.414`, and peer `newman@6.2.3`) in `~/.local/share/home-toolchain`.
  - Documented `EAUDITGLOBAL` behavior during `npm update -g` (`Arborist.reify()` `_submitQuickAudit()` summary vs `npm audit -g` throwing `EAUDITGLOBAL`) and recorded the 2 global packages with upstream transitive advisories (`@agentmemory/agentmemory@0.9.30` [11 vulns via `iii-sdk -> @opentelemetry/*`] and `happy@1.2.5` [9 vulns via `@modelcontextprotocol/sdk@1.29.0`, `braces <=3.0.3`, `@fastify/busboy@2.1.1`, `undici@5.29.0`]).
  - Documented `adhoc-home` (`~/node_modules`), `home_prefix_hijacked`, and `home_forbidden_artifacts` in `docs/runbooks/workstation-toolchain-inventory.md`.

---

## 2. Home-Directory Prefix Hygiene & `~/.npm-global` Cleanup Gate

### Tasks 2.1 & 2.2 (`$HOME` Cleanup & Prefix Resolution Verification)

- **User Confirmation**: Explicitly approved via interactive confirmation (`Approve removal of ~/node_modules and 5 stray $HOME lockfiles`).
- **Pre-Removal Symlink & Smoke Verification**:
  - `/Users/androidteam/.local/bin/bru` -> `../share/home-toolchain/node_modules/.bin/bru` (`4.2.1`, exit `0`)
  - `/Users/androidteam/.local/bin/yaml-language-server` -> `../share/home-toolchain/node_modules/.bin/yaml-language-server` (`2.0.0`, exit `0`)
  - `/Users/androidteam/.local/bin/newman-reporter-htmlextra` -> `../share/home-toolchain/node_modules/.bin/newman-reporter-htmlextra` (`1.23.1`, exit `0`)
- **Removed Stray `$HOME` Artifacts**:
  - `/Users/androidteam/node_modules`
  - `/Users/androidteam/pnpm-lock.yaml`
  - `/Users/androidteam/pnpm-workspace.yaml`
  - `/Users/androidteam/bun.lock`
  - `/Users/androidteam/bun.lock.bun-backup-20260813_100505`
  - `/Users/androidteam/package.json.bun-backup-20260813_100505`
- **Post-Removal Prefix Verification**:
  - `cd /Users/androidteam/Developer && npm prefix` -> `/Users/androidteam/Developer` (exit `0`)
  - `cd /Users/androidteam/Developer/platform && npm prefix` -> `/Users/androidteam/Developer/platform` (exit `0`)
  - `python3 /Users/androidteam/Developer/platform/openspec-store/scripts/inventory-workstation-toolchain.py --json | jq '.prefix_reconciliation'` (exit `0`):
    ```json
    {
      "npm_config_prefix": "/Users/androidteam/.npm-global",
      "maintenance_pipeline_prefix": "/Users/androidteam/.npm-global",
      "declared_prefix": "~/.npm-global",
      "has_split": false,
      "status": "reconciled",
      "home_prefix_hijacked": false,
      "home_forbidden_artifacts": []
    }
    ```
  - Human-readable header (`python3 /Users/androidteam/Developer/platform/openspec-store/scripts/inventory-workstation-toolchain.py | sed -n '1,6p'`):
    ```text
    === Workstation Prefix Reconciliation ===
      npm config get prefix:       /Users/androidteam/.npm-global
      maintenance pipeline prefix: /Users/androidteam/.npm-global
      declared prefix:             ~/.npm-global
      home prefix hijacked:        False
      Status:                      RECONCILED
    ```

### Task 2.3 (`~/.npm-global` Retired Artifact Cleanup)

- **Removed Dangling `.bin-HASH` Symlinks in `/Users/androidteam/.npm-global/bin`**:
  - `.amp-1TDgNqTm`, `.dgrep-EmxC0FXp`, `.tsc-w3Kv8tVZ`
- **Removed Empty `@*` Scope Directories in `/Users/androidteam/.npm-global/lib/node_modules` via `rmdir` (exit `0`)**:
  - `@anthropic-ai`, `@earendil-works`, `@mariozechner`, `@openai`, `@qoder-ai`, `@sentropic`, `@sourcegraph`, `@vtsls`
- **Verification**:
  - `active_count=19 hidden=[] broken=[] empty_scopes=[]` (exit `0`); all 19 active CLI symlinks (`agentmemory`, `agentmemory-mcp`, `anydoc`, `auggie`, `bdata`, `brightdata`, `codexuse`, `deepwiki`, `exa`, `exa-cli`, `gitnexus`, `grepai`, `happy`, `happy-mcp`, `kilo`, `kilocode`, `mcpr`, `node-gyp`, `openspec`) resolve to existing executables.

---

## 3. Relocated Workstation Toolchain Refresh (`~/.local/share/home-toolchain`)

### Tasks 3.1 & 3.2

- **Manifest Updated**: `/Users/androidteam/Developer` external root `/Users/androidteam/.local/share/home-toolchain/package.json`
  - Direct `dependencies` (4 total; `newman` not added as direct dependency):
    - `"@usebruno/cli": "^4.2.1"` (`4.2.1`)
    - `"newman-reporter-htmlextra": "^1.23.1"` (`1.23.1`, resolving peer `newman@6.2.3`)
    - `"pyright": "^1.1.414"` (`1.1.414`)
    - `"yaml-language-server": "^2.0.0"` (`2.0.0`)
  - Updated `overrides`: `"handlebars": "4.7.10"`, `"uuid": "14.0.3"`, `"qs": "6.16.1"`, `"fast-uri": "4.2.2"`, `"ip-address": "10.7.4"`, `"hono": "4.13.13"` (with `"js-yaml": ">=4.3.2"` resolving `5.5.0` and `"@usebruno/requests": { "@faker-js/faker": ">=10.5.0" }` resolving `10.6.0` at root and `5.5.3` under `postman-collection`).
- **Execution**:
  - Command: `/opt/homebrew/bin/npm update` in `/Users/androidteam/.local/share/home-toolchain`
  - Exit code: `0` (`added 108 packages, removed 15 packages, and changed 62 packages in 25s`)
- **Verification**:
  - `/opt/homebrew/bin/npm outdated` -> exit code `0`, empty output (`""`)
  - `/opt/homebrew/bin/npm outdated --all --json` -> `0` installed in-range (`current != wanted`) mismatches
  - `/opt/homebrew/bin/npm audit --json` -> `{"info": 0, "low": 0, "moderate": 0, "high": 10, "critical": 0, "total": 10}` (`0 critical, 10 high` irreducible advisories)
  - Smoke checks:
    - `/Users/androidteam/.local/bin/bru --version` -> `4.2.1` (exit `0`)
    - `/Users/androidteam/.local/bin/yaml-language-server --version` -> `2.0.0` (exit `0`)
    - `/Users/androidteam/.local/bin/newman-reporter-htmlextra --version` -> `1.23.1` (exit `0`)

| Residual Package (`~/.local/share/home-toolchain`) | Severity | Root Advisory / Via | Offered Remedy & Irreducibility |
|---|---|---|---|
| `braces` (`3.0.3`) | High | `GHSA-vfj7-8cjw-p6xm` (`<=3.0.3`) | Latest published is `3.0.3` (`patched_versions: null`) |
| `micromatch` (`4.0.8`) | High | via `braces` | Metavuln via `@budibase/handlebars-helpers -> micromatch -> braces` |
| `@budibase/handlebars-helpers` (`0.14.3`) | High | via `micromatch` | Metavuln via `newman-reporter-htmlextra` |
| `node-forge` (`1.4.0`) | High | `GHSA-86w9-cpqp-85rv` (`<=1.4.0`) | Latest published is `1.4.0` (`patched_versions: null`) |
| `@faker-js/faker` (`5.5.3` under `postman-collection`) | High | `<=10.4.0` | Raising `postman-collection` faker to `>=10.5.0` breaks `faker.address.city` at runtime; root `@usebruno/requests` is scoped to `10.6.0` |
| `postman-collection` (`4.5.1`) | High | via `@faker-js/faker` | Metavuln via `newman` |
| `postman-sandbox` (`4.2.2`) | High | via `postman-collection` | Metavuln via `postman-runtime` |
| `postman-runtime` (`7.52.2`) | High | via `node-forge`, `postman-collection`, `postman-sandbox` | Metavuln via `newman` |
| `newman` (`6.2.3`) | High | via `postman-collection`, `postman-runtime` | Only offered audit fix is downgrade `newman-reporter-htmlextra@1.22.5` / `newman@5.3.2` |
| `newman-reporter-htmlextra` (`1.23.1`) | High | via `@budibase/handlebars-helpers`, `newman` | Only offered audit fix is downgrade `1.22.5` |

---

## 4. Governed Repository Audit Remediation Gates

### Task 4.1 (`/Users/androidteam/Developer/platform/mcp-router`)

- **Files Modified**:
  - `/Users/androidteam/Developer/platform/mcp-router/apps/electron/package.json` (`"electron": "^41.10.7"`)
  - `/Users/androidteam/Developer/platform/mcp-router/pnpm-workspace.yaml` (`blockExoticSubdeps: false` and overrides for `electron@<41.10.7`, `shell-quote@<1.11.0`, `handlebars@<4.7.10`, `postcss-selector-parser@<7.1.6`, `proxy-addr@<2.0.8`, `compression@<1.8.2`, `http-cache-semantics@<=4.2.0`, `source-map-js@<1.2.2`)
  - `/Users/androidteam/Developer/platform/mcp-router/pnpm-lock.yaml`
- **Verification Commands & Results**:
  - `/opt/homebrew/bin/pnpm install --no-frozen-lockfile` -> exit code `0` (rebuilt `argon2` and `better-sqlite3` against Electron `41.10.7`)
  - `/opt/homebrew/bin/pnpm install --frozen-lockfile` -> exit code `0` (`Lockfile is up to date`)
  - `/opt/homebrew/bin/pnpm audit --json` -> `{"info": 0, "low": 0, "moderate": 1, "high": 4, "critical": 0}` across `1,464` total dependencies. All 5 remaining advisories have `patched_versions: null`:
    1. `1139346` (`GHSA-jmr9-qjv8-65gv`): `extract-zip <=2.0.1` (`high`, `patched_versions: null`)
    2. `1193685` (`GHSA-7pqw-9j4j-h8q3`): `extract-zip <=2.0.1` (`high`, `patched_versions: null`)
    3. `1240912` (`GHSA-86w9-cpqp-85rv`): `node-forge <=1.4.0` (`high`, `patched_versions: null`)
    4. `1240992` (`GHSA-vfj7-8cjw-p6xm`): `braces <=3.0.3` (`high`, `patched_versions: null`)
    5. `1241202` (`GHSA-hp3w-g68c-fv3c`): `sprintf-js <=1.1.3` (`moderate`, `patched_versions: null`)
  - `/opt/homebrew/bin/pnpm typecheck` -> exit code `0` (`Tasks: 8 successful, 8 total`)
  - `/opt/homebrew/bin/pnpm test` -> exit code `0` (`apps/cli`: 3/3 pass; `packages/shared`: 4/4 pass; `apps/electron`: 64/64 pass across 16 suites)
  - `/opt/homebrew/bin/pnpm build` -> exit code `0` (`Tasks: 4 successful, 4 total`)

### Task 4.2 (`/Users/androidteam/Developer/tdt/realtime/frontend`)

- **Files Modified / Removed**:
  - `/Users/androidteam/Developer/tdt/realtime/frontend/package.json` (`overrides` and `pnpm.overrides` updated with `http-cache-semantics >=4.3.0`, `source-map-js >=1.2.2`, `dompurify >=3.4.17`, `handlebars: "4.7.10"`, `qs: "6.16.1"`, `uuid: "14.0.3"`, `smol-toml: "1.9.1"`, `fast-uri: "4.2.2"`)
  - `/Users/androidteam/Developer/tdt/realtime/frontend/package-lock.json`
  - Removed stale gitignored `/Users/androidteam/Developer/tdt/realtime/frontend/package-lock 2.json`
- **Verification Commands & Results**:
  - `/opt/homebrew/bin/npm audit fix` -> exit code `0` (`found 0 vulnerabilities`)
  - `/opt/homebrew/bin/npm audit --json` -> exit code `0`, `{"info": 0, "low": 0, "moderate": 0, "high": 0, "critical": 0, "total": 0}` across `655` dependencies
  - `/opt/homebrew/bin/npm run type-check` -> exit code `0` (`tsc --noEmit`)
  - `/opt/homebrew/bin/npm run build` -> exit code `0` (`✓ 2981 modules transformed. ✓ built in 836ms`)

### Task 4.3 (`/Users/androidteam/Developer/legacy/kafka-microservices`)

- **Files Modified**:
  - `/Users/androidteam/Developer/legacy/kafka-microservices/package.json` (added `"overrides": { "smol-toml": ">=1.9.1", "katex": ">=0.19.0" }` and `"#docs/deprecated"` exclusion in `lint:md` / `lint:md:fix`)
  - `/Users/androidteam/Developer/legacy/kafka-microservices/package-lock.json`
- **Verification Commands & Results**:
  - `/opt/homebrew/bin/npm install` -> exit code `0` (`katex@0.19.0`, `smol-toml@1.9.1`, `markdownlint-cli2@0.23.3`)
  - `/opt/homebrew/bin/npm audit --json` -> `{"info": 0, "low": 0, "moderate": 0, "high": 5, "critical": 0, "total": 5}` (only the 5 `braces <=3.0.3` chain findings where `fixAvailable` offers downgrade `markdownlint-cli2@0.0.4`)
  - `/opt/homebrew/bin/npm run lint:md` -> exit code `0` (`markdownlint-cli2 v0.23.3 (markdownlint v0.41.1)`, `Linting: 104 files`, `Summary: 0 issues in 0 files`)
  - `git -C /Users/androidteam/Developer/legacy/kafka-microservices diff --stat package.json package-lock.json` -> `package.json | 8 ++++++-- (1 file changed, 6 insertions(+), 2 deletions(-))` (path-scoped; 89 unrelated worktree files untouched)
