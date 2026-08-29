# Tasks: Security Audit & Dependency Upgrades

## Completed Tasks

### 1.1 Home Directory Audit ✅
**Status:** Complete
**Owner:** AI Assistant
**Completed:** 2026-08-28

- [x] Run `npm audit` on `~/` packages
- [x] Identify 51 vulnerabilities (15 moderate, 23 high, 13 critical)
- [x] Document vulnerable packages and their sources

### 1.2 Remove Deprecated npx ✅
**Status:** Complete
**Owner:** AI Assistant
**Completed:** 2026-08-28

- [x] Identify `npx@3.0.0` as deprecated standalone package
- [x] Verify modern npm includes npx built-in (v12.0.2)
- [x] Run `npm uninstall npx`
- [x] Verify removal: 135 packages removed, 17 vulnerabilities fixed

### 1.3 Upgrade Newman ✅
**Status:** Complete
**Owner:** AI Assistant
**Completed:** 2026-08-28

- [x] Upgrade `newman` from 4.6.1 to 6.2.2
- [x] Replace `newman-reporter-html` with `newman-reporter-htmlextra`
- [x] Verify compatibility (peer dependencies resolved)
- [x] Test CLI: `newman --version` returns 6.2.2

### 1.4 Apply Dependency Overrides ✅
**Status:** Complete
**Owner:** AI Assistant
**Completed:** 2026-08-28

- [x] Add 10 overrides to `~/package.json`
- [x] Force resolve: lodash, uuid, qs, node-forge, underscore, flatted, sharp, adm-zip, handlebars, jose
- [x] Clean install with `rm -rf node_modules && npm install`
- [x] Verify: 0 vulnerabilities ✅

### 1.5 mcp-router Assessment ✅
**Status:** Complete
**Owner:** AI Assistant
**Completed:** 2026-08-28

- [x] Run `pnpm audit` (62 vulnerabilities found)
- [x] Identify outdated dev dependencies
- [x] Update to latest versions (ESLint, TypeScript, Turbo, etc.)
- [x] Add 15 new pnpm overrides
- [x] Update existing overrides to latest patches
- [x] Verify rebuild: electron-rebuild completes successfully
- [x] Result: 62 → 40 vulnerabilities (32% reduction)

### 1.6 prime-agent Verification ✅
**Status:** Complete
**Owner:** AI Assistant
**Completed:** 2026-08-28

- [x] Run `npm audit`
- [x] Verify: 0 vulnerabilities
- [x] No changes needed

## Completed Tasks (Continued)

### 2.1 hermes-webui Investigation ✅
**Status:** Complete
**Owner:** AI Assistant
**Completed:** 2026-08-28

**Findings:**
- hermes-webui is primarily a Python project (FastAPI backend)
- `package.json` exists but is minimal: only ESLint as dev dependency
- Purpose: Runtime-error guard for static JS files (not a build step)
- No `node_modules` directory exists
- No lockfile exists (`package-lock.json` or `pnpm-lock.yaml`)
- `npm audit` fails: requires existing lockfile
- Earlier audit results (47 vulnerabilities) were from cached/incorrect context

**Conclusion:** No action required. The package.json is intentionally minimal and doesn't introduce vulnerabilities.

## Pending Tasks (Deferred at Archive — Outside Scope of Archived Change)

Archived 2026-08-29 with the security-remediation work that was actually
completed (tasks 1.1-2.1). Tasks 3.1-3.4 and 4.1-4.2 were explicitly NOT
completed before archiving. They remain open follow-up work outside this
archived change and require new change records with owners before any
further action.

### 3.1 Remaining mcp-router Vulnerabilities 📋
**Status:** Deferred at archive (2026-08-29) — needs new change with named owner
**Owner:** TBD
**Priority:** Medium

**Remaining:** 40 vulnerabilities
- 3 low severity
- 15 moderate severity
- 20 high severity
- 2 critical severity

**Root Cause:** Deep transitive dependencies in Electron/Webpack tooling

**Options:**
1. Wait for upstream patches
2. Fork and patch vulnerable packages
3. Accept risk (local development tool only)
4. Major version upgrades (breaking changes)

**Recommendation:** Monitor upstream, accept risk for now

### 3.2 hermes-webui Documentation 📋
**Status:** Deferred at archive (2026-08-29) — needs new change with named owner
**Owner:** TBD

- [ ] Add comment to `package.json` explaining ESLint purpose
- [ ] Document that no lockfile is intentional (dev-only tooling)
- [ ] Clarify in ARCHITECTURE.md that JS linting is optional

### 3.3 Documentation Update 📋
**Status:** Deferred at archive (2026-08-29) — needs new change with named owner
**Owner:** TBD

- [ ] Add comments to package.json explaining overrides
- [ ] Document override strategy in workspace README
- [ ] Create security audit runbook
- [ ] Update CLAUDE.md with override conventions

### 3.4 Monitoring Setup 📋
**Status:** Deferred at archive (2026-08-29) — needs new change with named owner
**Owner:** TBD

- [ ] Configure automated weekly audit reports
- [ ] Set up alerts for new critical vulnerabilities
- [ ] Create dashboard for vulnerability trends
- [ ] Schedule monthly review meetings

## Deferred Tasks

### 4.1 Python Repository Audits ⏸️
**Status:** Deferred
**Reason:** Different toolchain (uv, not npm)

**Action Required:**
- Run `uv audit` or equivalent for each Python repo
- Check for PyPI vulnerabilities
- Update `pyproject.toml` dependencies

### 4.2 Go Module Audits ⏸️
**Status:** Deferred
**Reason:** Different toolchain (go mod)

**Action Required:**
- Run `govulncheck` for go-microservices
- Check for Go module vulnerabilities
- Update `go.mod` dependencies

## Task Dependencies

```
1.1 Home Directory Audit
    ↓
1.2 Remove Deprecated npx ──┐
1.3 Upgrade Newman ─────────┤
1.4 Apply Overrides ────────┤
                            ↓
                    1.5 mcp-router Assessment
                            ↓
                    1.6 prime-agent Verification
                            ↓
                    2.1 hermes-webui Investigation ✅
                            ↓
                    3.1 Remaining mcp-router Vulnerabilities
                    3.2 hermes-webui Documentation
                    3.3 Documentation Update
                    3.4 Monitoring Setup
```

## Time Tracking

| Task | Estimated | Actual | Status |
|------|-----------|--------|--------|
| 1.1 Home Directory Audit | 15 min | 10 min | ✅ |
| 1.2 Remove Deprecated npx | 5 min | 2 min | ✅ |
| 1.3 Upgrade Newman | 10 min | 5 min | ✅ |
| 1.4 Apply Overrides | 20 min | 15 min | ✅ |
| 1.5 mcp-router Assessment | 30 min | 25 min | ✅ |
| 1.6 prime-agent Verification | 5 min | 2 min | ✅ |
| 2.1 hermes-webui Investigation | 15 min | 8 min | ✅ |
| 3.1 Remaining mcp-router | 60 min | Pending | 📋 |
| 3.2 hermes-webui Documentation | 10 min | Pending | 📋 |
| 3.3 Documentation Update | 30 min | Pending | 📋 |
| 3.4 Monitoring Setup | 45 min | Pending | 📋 |
| **Total** | **4.5 hrs** | **67 min** | **25%** |
