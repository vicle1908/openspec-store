## Context

Three Node.js projects have accumulated npm vulnerabilities through direct and transitive dependencies. The workspace uses npm with standard package.json/package-lock.json. Projects are independent (no shared lockfiles).

Current state:
- `realtime/frontend`: axios 1.13.2, vitest 4.0.16, 6 vulnerabilities
- `prime-agent`: postcss vulnerable, protobufjs vulnerable, 26 vulnerabilities
- `goose-docs/documentation`: Docusaurus 3.9.2 with vulnerable transitive deps, 42 vulnerabilities

## Goals / Non-Goals

**Goals:**
- Patch all vulnerabilities with available fixes via semver-compatible upgrades
- Validate no breaking changes in existing test suites
- Document any vulnerabilities without upstream fixes

**Non-Goals:**
- Major version upgrades (e.g., Docusaurus 3.x → 4.x)
- Replacing packages with alternatives (e.g., axios → got)
- Restructuring dependency trees
- Fixing vulnerabilities in packages with no upstream fix (e.g., image-size)

## Decisions

### 1. Use `npm audit fix` for transitive dependencies
**Choice**: Run `npm audit fix` (non-force) on each project
**Rationale**: Safest approach - only applies semver-compatible patches
**Alternatives considered**:
- `npm audit fix --force`: Rejected - may introduce breaking changes
- Manual resolution overrides: Rejected - more maintenance burden

### 2. Upgrade direct dependencies explicitly
**Choice**: Upgrade axios, vitest, postcss directly in package.json
**Rationale**: Direct deps need explicit version bumps to ensure latest patches
**Versions**:
- axios: ^1.13.2 → ^1.19.0
- vitest + @vitest/*: ^4.0.16 → ^4.1.10
- postcss: current → ^8.5.26

### 3. Order of operations
**Choice**: Upgrade direct deps first, then run `npm audit fix` for transitive
**Rationale**: Direct dep upgrades may resolve some transitive vulnerabilities automatically

### 4. Skip spec-level changes
**Choice**: Set `skip_specs: true` in .openspec.yaml
**Rationale**: Dependency versions are implementation details, not behavior changes

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| Minor version upgrade breaks API | Run existing test suites after each project upgrade |
| Transitive dep conflict after fix | Use `npm audit fix` (non-force) to avoid conflicts |
| Docusaurus vulnerable deps persist | Accept risk - no upstream fix; monitor for Docusaurus 3.10+ |
| vitest upgrade affects test behavior | Run full test suite; vitest minor versions are stable |

## Migration Plan

1. **realtime/frontend**:
   - `npm install axios@latest vitest@latest @vitest/coverage-v8@latest @vitest/ui@latest`
   - `npm audit fix`
   - Run `npm test`

2. **prime-agent**:
   - `npm audit fix`
   - Verify postcss/protobufjs updated

3. **goose-docs/documentation**:
   - `npm audit fix`
   - Note: image-size, uuid remain vulnerable (no upstream fix)

4. **Validation**:
   - Run `npm audit` on each project to confirm reduction
   - Run test suites where applicable

## Open Questions

None - all decisions are straightforward semver-compatible upgrades.
