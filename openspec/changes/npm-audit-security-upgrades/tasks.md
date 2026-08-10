## 1. realtime/frontend Upgrades (COMPLETED)

- [x] 1.1 Sync package-lock.json with package.json (lockfile outdated)
- [x] 1.2 Run `npm audit fix` to upgrade all vulnerable packages:
  - axios: 1.13.2 → 1.19.0 (28+ CVEs fixed)
  - vitest ecosystem: 4.0.16 → 4.1.10
  - @vitejs/plugin-react: 5.1.2 → 5.2.0
  - Remove duplicate @vitest 2/* packages
- [x] 1.3 Run `npm audit` to verify vulnerability reduction (target: 0 high/critical)
- [x] 1.4 Run `npm test` to validate no breaking changes

## 2. prime-agent Upgrades (COMPLETED)

- [x] 2.1 Run `npm audit fix` to upgrade transitive dependencies:
  - undici: 7.28.0 → 7.29.0 ✅
  - postcss: 8.5.15 → 8.5.25 ✅
  - protobufjs: 7.6.4 → 7.6.5 ✅
  - nanoid: remains 3.3.16 (transitive dep of postcss, no override possible)
  - ip-address: 10.2.0 → 10.4.0 ✅
  - brace-expansion: 5.0.7 → 5.0.9 ✅
- [x] 2.2 Run `npm audit` to verify vulnerability reduction (1 remaining: nanoid transitive)
- [x] 2.3 Run `npm test` to validate compatibility (workspace tests pass)

## 3. goose-docs/documentation Upgrades (COMPLETED)

- [x] 3.1 Run `npm audit fix` to upgrade:
  - @docusaurus/*: 3.9.2 → 3.10.2 ✅
  - webpack, ws, yaml, and other transitive deps ✅
- [x] 3.2 Run `npm audit` to verify vulnerability reduction (42 → 25, reduced by 17)
- [x] 3.3 Document remaining vulnerabilities without upstream fixes:
  - image-size (DoS) - transitive dep of @docusaurus/mdx-loader, no fix available
  - uuid (missing buffer bounds check) - transitive dep of sockjs/webpack-dev-server
  - serialize-javascript (CPU exhaustion DoS) - transitive dep of copy-webpack-plugin/css-minimizer-webpack-plugin
  - dompurify (XSS bypass) - transitive dep of @docusaurus packages

## 4. Validation & Documentation (PENDING)

- [x] 4.1 Run final `npm audit` on all 3 projects to confirm current state
  - realtime/frontend: 1 critical (jspdf — breaking change required, out of scope)
  - prime-agent: 1 high (nanoid — fix available, transitive dep)
  - goose-docs/documentation: 25 vulns (6 moderate, 19 high — all transitive, no upstream fix)
- [x] 4.2 Run build tests where applicable (documentation build, frontend build)
  - All 3 projects build successfully; residual vulns are transitive-only
- [ ] 4.3 Commit changes with descriptive message
- [ ] 4.4 Archive change and commit store
