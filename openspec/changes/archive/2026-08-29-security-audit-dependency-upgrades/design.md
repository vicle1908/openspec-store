# Design: Security Audit & Dependency Upgrades

## Architecture Overview

This change implements a systematic approach to vulnerability remediation across the workspace using npm/pnpm dependency overrides.

## Implementation Strategy

### Phase 1: Home Directory (`~/`)

**Target:** Standalone CLI tools and global packages

```
~/package.json
├── dependencies
│   ├── gitnexus@1.6.10
│   ├── newman@6.2.2 (upgraded from 4.6.1)
│   ├── newman-reporter-htmlextra@1.23.1 (replaced html reporter)
│   ├── pyright@1.1.413
│   └── yaml-language-server@1.24.0
└── overrides
    ├── lodash: 4.18.1
    ├── uuid: 14.0.2
    ├── qs: 6.15.3
    ├── node-forge: 1.4.0
    ├── underscore: 1.13.8
    ├── flatted: 3.4.4
    ├── sharp: 0.35.4
    ├── adm-zip: 0.6.0
    ├── handlebars: 4.7.9
    └── jose: 6.2.10
```

**Key Decisions:**
1. Removed deprecated `npx@3.0.0` - modern npm includes npx built-in
2. Upgraded `newman` to v6 for compatibility with latest reporters
3. Replaced `newman-reporter-html` with `newman-reporter-htmlextra` (supports newman 6)
4. Applied 10 overrides for transitive dependencies with no upstream fixes

### Phase 2: mcp-router

**Target:** Electron desktop application + CLI

```
mcp-router/package.json
└── pnpm.overrides
    ├── Existing: 45+ overrides
    └── Added: 15 new overrides
        ├── d3-color: >=3.1.0
        ├── extract-zip: >=2.0.1
        ├── image-size: >=1.0.2
        ├── js-yaml: >=3.14.0
        ├── launch-editor: >=2.2.1
        ├── nanoid: >=3.3.8
        ├── sanitize-html: >=2.14.0
        ├── semver: >=7.5.2
        ├── shell-quote: >=1.7.3
        ├── underscore: >=1.13.8
        ├── websocket-driver: >=0.6.2
        ├── handlebars: >=4.7.9
        ├── async: >=2.6.4
        ├── crypto-js: >=4.2.0
        └── marked: >=4.0.10
```

**Key Decisions:**
1. Used pnpm's versioned override syntax for precision
2. Updated existing overrides to latest patch versions
3. Maintained Electron compatibility (no major version jumps)
4. Verified native module rebuilds (argon2, better-sqlite3)

## Data Flow

```
User runs npm/pnpm install
    ↓
Package manager resolves dependencies
    ↓
Overrides applied to transitive deps
    ↓
Vulnerable versions replaced with patched versions
    ↓
Audit passes (or vulnerabilities reduced)
```

## Error Handling

### Scenario 1: Override Incompatibility
- **Detection:** `pnpm install` fails with peer dependency errors
- **Response:** Remove problematic override, document as remaining issue
- **Fallback:** Accept vulnerability if no compatible patch exists

### Scenario 2: Build Failure
- **Detection:** Post-install hooks fail (electron-rebuild)
- **Response:** Revert to previous package.json, investigate
- **Fallback:** Manual rebuild with `pnpm rebuild`

### Scenario 3: Runtime Error
- **Detection:** CLI tools fail or produce errors
- **Response:** Check version compatibility, adjust overrides
- **Fallback:** Pin to known-working versions

## Security Considerations

### Override Safety
- Overrides only apply to transitive dependencies
- No direct dependency versions changed without explicit upgrade
- Patch/minor version bumps preferred over major versions
- All overrides tested with clean install

### Audit Trail
- Package.json changes tracked in git
- Lock file changes recorded
- Vulnerability counts documented before/after

## Performance Impact

### Installation Time
- **Before:** ~10s for clean install
- **After:** ~15s with overrides (minimal increase)
- **Reason:** Additional resolution steps for override matching

### Runtime Performance
- **No impact:** Overrides don't affect execution speed
- **Potential improvement:** Some patches fix memory leaks or DoS vulnerabilities

## Testing Strategy

### Verification Commands
```bash
# Home directory
npm audit                    # Expect: 0 vulnerabilities
npm ls --depth=0             # Expect: all packages installed
which npx newman pyright     # Expect: all found

# mcp-router
cd ~/Developer/mcp-router
pnpm audit                   # Expect: reduced vulnerabilities
pnpm install                 # Expect: successful with rebuild
pnpm build                   # Expect: successful
```

### Regression Testing
- CLI tools functional
- Electron app builds
- Development workflow unchanged

## Monitoring

### Automated Checks
- Post-merge hooks run `npm audit`
- CI pipeline includes vulnerability scanning
- Weekly scheduled audits

### Manual Review
- Monthly review of remaining vulnerabilities
- Quarterly review of override necessity
- Annual security audit of workspace
