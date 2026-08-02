## Context

The tdt ecosystem currently has **4 projects** (jira-epic-report, jira-daily-reports, jira-kanban-from-spreadsheet, android-scan-agent) using Google Sheets with inconsistent implementations. Each project has duplicated authentication code, different libraries (googleapiclient, gspread, gws CLI), and no shared patterns. This creates ~3,165 lines of duplicated code across projects and makes it difficult to improve Sheets integration ecosystem-wide.

**Current State**:

- jira-epic-report: 1,665 lines using googleapiclient, full CRUD, 3-level auth fallback, load_tdt_env()
- jira-daily-reports: ~800 lines using googleapiclient, full CRUD, 3-level auth fallback, load_tdt_env()
- jira-kanban: ~400 lines using gspread + gws CLI, read-only, backend abstraction via Protocol
- android-scan-agent: ~300 lines using googleapiclient, write-only, basic auth (1-level fallback)

**Constraints**:

- Must maintain backward compatibility for all 4 consumers during migration
- Cannot break existing authentication flows (service account paths, caching)
- Must support both Python SDK and CLI workflows (some users prefer gws OAuth)
- New library should be <1,000 lines (simpler than any existing implementation)
- **Python 3.14+ required** (all ecosystem projects use 3.14.5)
- **gspread dropped entirely** (unmaintained, API v3, slow writes)

**Stakeholders**:

- All 4 project maintainers
- Future tdt projects needing Sheets integration
- Users relying on current authentication patterns

## Goals / Non-Goals

**Goals**:

- Extract and unify Google Sheets code into reusable `tdt-sheets` library
- Provide consistent authentication with 3-level fallback across ecosystem
- Support multiple backends (googleapiclient SDK, gws CLI) via Protocol abstraction
- Reduce total Sheets-related code from ~3,165 lines to ~500-800 lines
- Zero regression in functionality for all 4 consumers
- Clear migration path with <1 day effort per project
- Leverage modern Python 3.14 features (lazy annotations, slots=True dataclasses, functools.cache)
- Make batch operations primary feature (90% API call reduction)

**Non-Goals**:

- Advanced Sheets features (formatting, charts, formulas) - focus on read/write/clear only
- Drive API features beyond basic spreadsheet access - separate concern
- OAuth flow implementation - leverage existing gws CLI for OAuth users
- Synchronous multi-user conflict resolution - consumers handle their own locking
- Async support - no mature async Google Sheets library, sync is fine for batch ops
- gspread support - dropped entirely (unmaintained, API v3)

## Decisions

### Decision 1: Extract as separate repository vs add to tdt-core

**Choice**: Separate `tdt-sheets` repository

**Rationale**:

- tdt-core is low-level (env, config) - Sheets integration is higher-level
- Avoids adding Google API dependencies to tdt-core (keep it lightweight)
- Allows independent versioning and release cycle
- Easier to deprecate/replace in future if needed

**Alternatives considered**:

- Add to tdt-core as `tdt_core.sheets`: Rejected - wrong abstraction level, bloats core
- Keep in each project: Rejected - doesn't solve duplication problem

### Decision 2: Backend abstraction via Protocol vs inheritance

**Choice**: Python Protocol (typing.Protocol) for backend interface

**Rationale**:

- Structural subtyping - implementations don't need explicit inheritance
- Better for wrapping existing libraries (googleapiclient, gws CLI)
- Type-checker friendly (mypy, pyright validation)
- Mirrors successful pattern from jira-kanban project
- Modern Python 3.14 supports Protocol with lazy annotations

**Alternatives considered**:

- Abstract Base Class: Rejected - requires explicit inheritance, more coupling
- Duck typing only: Rejected - loses type safety and IDE support

### Decision 3: Authentication strategy

**Choice**: Extract exact authentication pattern from jira-epic-report and jira-daily-reports (most complete, nearly identical)

**Rationale**:

- Both jira-epic-report and jira-daily-reports have identical 3-level fallback patterns
- Proven credential caching with token refresh (60-second buffer)
- Integrates with tdt_core.env.load_tdt_env()
- Well-tested in production across 2 projects
- android-scan-agent uses simpler 1-level fallback (will be upgraded)

**Implementation**:

```python
# tdt_sheets/auth.py
class ServiceAccountAuth:
    @classmethod
    def from_env(cls, scopes=None):
        # 1. Try GOOGLE_SERVICE_ACCOUNT_PATH
        # 2. Fall back to GOOGLE_APPLICATION_CREDENTIALS
        # 3. Fall back to ~/.tdt/google-service-account.json
        # Load credentials, cache at module level, return Auth object
```

**Alternatives considered**:

- OAuth support: Deferred - users can use gws CLI backend for OAuth workflows
- Multiple auth strategies: Rejected - YAGNI, service account covers 99% of use cases

### Decision 3.1: Security Enhancements

**Choice**: Add production-grade security features to authentication (based on 2026-06-03 authentication analysis)

**Features**:

1. **Cache invalidation on file mtime** — Automatic cache refresh when service account JSON is modified (enables zero-downtime credential rotation)
2. **Configurable scopes** — Allow consumers to specify minimal scopes (principle of least privilege)
3. **Credential JSON validation** — Validate structure before auth (clear error messages vs cryptic google-auth errors)
4. **Structured logging** — Production observability with context-rich log events
5. **File permission warnings** — Alert on world-readable service account files (security awareness)

**Rationale**:

- jira-epic-report authentication verified working in production (2026-06-03)
- Security analysis revealed 5 critical gaps in existing implementations
- Minimal code overhead (~100 lines total across all enhancements)
- Significantly improves operational safety and debugging experience
- Enables zero-downtime credential rotation (current implementations require service restart)
- All enhancements maintain backward compatibility

**Implementation Examples**:

```python
# Cache invalidation on file mtime
def _credentials_cache_key(path: Path) -> str:
    mtime = path.stat().st_mtime
    return f"{path}:{mtime}"

# Configurable scopes
class ServiceAccountAuth:
    def __init__(self, scopes: Sequence[str] | None = None):
        self.scopes = tuple(scopes) if scopes else DEFAULT_SCOPES

# Credential JSON validation
REQUIRED_SA_FIELDS = {"type", "project_id", "private_key", "client_email", ...}
def _validate_service_account_json(path: Path) -> None:
    data = json.load(path.open())
    missing = REQUIRED_SA_FIELDS - set(data.keys())
    if missing:
        raise ValueError(f"Missing fields: {missing}")

# Structured logging
logger.info("credentials_cache_hit", extra={"expires_in": f"{remaining:.0f}s"})
logger.warning("credentials_refresh_failed", extra={"error": str(exc)})

# File permission warning
mode = path.stat().st_mode
if mode & (stat.S_IROTH | stat.S_IWOTH):
    logger.warning("service_account_insecure_permissions", extra={"mode": oct(mode)})
```

**Timeline Impact**: +0.5 days implementation time

**Documentation**: See AUTHENTICATION_ANALYSIS.md and SECURITY_ENHANCEMENTS.md for detailed analysis

**Alternatives considered**:

- Skip security enhancements: Rejected - production safety is critical
- Defer to v0.2.0: Rejected - better to get authentication right in v0.1.0
- Only implement subset: Rejected - all 5 enhancements are complementary and equally important

### Decision 4: Dependency management for backends

**Choice**: Core dependencies only (SDK backend), no optional extras

**Rationale**:

- Single backend (googleapiclient) simplifies maintenance and testing
- gspread dropped entirely (unmaintained, API v3, slow writes)
- gws CLI is external binary, not a Python dependency
- Keeps installation minimal and predictable
- All 4 projects can use same dependency set

**Implementation**:

```toml
[project]
requires-python = ">=3.14"
dependencies = [
    "google-auth>=2.0.0",
    "google-api-python-client>=2.0.0",
]
```

**Alternatives considered**:

- Optional gspread backend: Rejected - library unmaintained, API v3
- Optional pygsheets backend: Deferred - last push 8 months ago, evaluate if community requests
- Separate packages per backend: Rejected - too much overhead for maintenance

### Decision 5: API design - class-based vs function-based

**Choice**: Class-based SheetsClient with backend injection

**Rationale**:

- Natural fit for stateful operations (caching, service initialization)
- Easy to mock for testing (inject fake backend)
- Familiar OOP pattern for Python developers

**API**:

```python
from tdt_sheets import SheetsClient, ServiceAccountAuth

auth = ServiceAccountAuth.from_env()
client = SheetsClient(auth=auth, backend='sdk')  # or 'cli'

# Read
data = client.read(spreadsheet_id, range='Sheet1!A1:D10')

# Write
client.write(spreadsheet_id, range='Sheet1!A1', values=[['Hello']])

# Clear
client.clear(spreadsheet_id, range='Sheet1!A1:D10')

# Batch operations (PRIMARY feature - 90% API call reduction)
data = client.batch_read(spreadsheet_id, ranges=['Sheet1!A1:D10', 'Sheet2!A1:Z100'])
client.batch_write(spreadsheet_id, data=[
    {'range': 'Sheet1!A1', 'values': [['A']]},
    {'range': 'Sheet2!A1', 'values': [['B']]},
])
```

**Alternatives considered**:

- Functional API: Rejected - harder to manage state, less idiomatic Python
- Context manager: Considered for future - not needed for MVP

### Decision 6: Migration strategy

**Choice**: Gradual migration project-by-project, **prioritizing jira-kanban first** (updated 2026-06-03)

**Migration Order** (revised based on security analysis):

1. **jira-kanban-from-spreadsheet** (3-4 hours) — **HIGHEST PRIORITY** - remove unmaintained gspread dependency
2. android-scan-agent (3-4 hours) — Gains 3-level fallback + token refresh
3. jira-daily-reports (4-6 hours) — Validates full CRUD with simpler codebase
4. jira-epic-report (4-6 hours) — Most complex, validates at scale

**Rationale**:

- **jira-kanban uses unmaintained gspread** (GitHub deprecation notice, API v3, security risk)
- Removing gspread reduces ecosystem security exposure immediately
- android-scan-agent gains robustness (token refresh, 3-level fallback)
- jira-daily-reports validates full CRUD with simpler codebase
- jira-epic-report validates all features work at scale with most complex case

**Original Order Rejected**: android-scan-agent first was based on code simplicity, not risk. Security analysis (2026-06-03) revealed jira-kanban's unmaintained dependency is higher priority than code complexity.

**Per-project steps**:

1. Add tdt-sheets dependency
2. Replace import statements
3. Migrate auth code to ServiceAccountAuth.from_env()
4. Replace operations with client.read/write/clear and batch operations
5. Run existing test suite (verify no regression)
6. Remove old implementation file

### Decision 7: Testing strategy

**Choice**: Comprehensive unit tests + integration tests per backend

**Test Structure**:

```
tests/
├── test_auth.py              # Authentication logic
├── test_client.py            # Client operations (mocked backends)
├── test_utils.py             # URL parsing, GID resolution
├── test_batch_operations.py  # Batch read/write/clear operations
├── backends/
│   ├── test_sdk.py          # SDK backend (mock googleapiclient)
│   └── test_cli.py          # CLI backend (mock subprocess)
└── integration/
    └── test_live_api.py      # Real API tests (CI only, requires service account)
```

**Coverage Target**: 80%+ (match jira-epic-report's standard)

**Alternatives considered**:

- Only integration tests: Rejected - too slow, requires real credentials
- Only unit tests: Rejected - misses backend-specific issues

## Risks / Trade-offs

### Risk 1: Breaking changes during migration

- **Risk**: API differences break existing consumers
- **Mitigation**: Comprehensive test suite per project, gradual rollout, keep old code until tests pass

### Risk 2: Performance regression

- **Risk**: New abstraction layer adds overhead
- **Mitigation**: Benchmark before/after for each project, cache aggressively, use same underlying APIs

### Risk 3: Backend feature parity

- **Risk**: Advanced features work on SDK but fail on CLI
- **Mitigation**: Document supported operations per backend, raise NotImplementedError early for unsupported features

### Risk 4: Dependency version conflicts

- **Risk**: google-api-python-client version conflicts across projects
- **Mitigation**: Use loose version constraints (>=2.0.0), test with multiple versions in CI

### Risk 5: Maintenance burden of new repo

- **Risk**: New repo to maintain, release, document
- **Mitigation**: Shared maintenance across 4+ teams, automated CI/CD, comprehensive docs from day 1

### Risk 8: gspread removal breaks jira-kanban

- **Risk**: jira-kanban currently uses gspread, removal may break functionality
- **Mitigation**: Migrate jira-kanban to SDK backend (googleapiclient), add write capability, test thoroughly

### Risk 6: CLI backend fragility

- **Risk**: Subprocess-based CLI backend brittle (path issues, timeouts, parsing)
- **Mitigation**: Document SDK backend as recommended, CLI as fallback for OAuth users only, timeout handling

### Risk 7: Cache invalidation bugs

- **Risk**: Stale cached credentials cause auth failures
- **Mitigation**: 60-second expiry buffer, auto-refresh on 401 errors, clear cache on token refresh failure

## Migration Plan

### Phase 1: Create tdt-sheets library (2.5 days) — **Updated 2026-06-03**

**Day 1**: Core + Security Enhancements

1. Create tdt-sheets repo with proper structure
2. Extract auth.py from jira-epic-report (baseline implementation)
3. **Add cache invalidation on file mtime** (security enhancement)
4. **Add configurable scopes** (security enhancement)
5. **Add credential JSON validation** (security enhancement)
6. **Add file permission warning** (security enhancement)
7. **Add structured logging** (security enhancement)
8. Create client.py with SheetsClient class
9. Implement SDK backend (from jira-epic-report)
10. Implement CLI backend (from jira-kanban)

**Day 2**: Features + Utils

1. Extract utils.py (URL parsing, GID resolution)
2. Add batch operations (batch_read, batch_write, batch_clear)
3. Add exception hierarchy (TdtSheetsError, PermissionError, NetworkError, RateLimitError)

**Day 2.5**: Testing + Docs

1. Write comprehensive unit tests (~40 tests base + 10 security tests = 50 total)
2. Write security-specific tests (file permissions, cache invalidation, validation)
3. Set up CI/CD (GitHub Actions: Python 3.14 test matrix)
4. Write README with examples
5. Write migration guide (4 projects)
6. **Write security documentation** (credential rotation, best practices)
7. Tag v0.1.0 release

**Timeline Change**: +0.5 days for security enhancements (originally 2 days, now 2.5 days)

### Phase 2: Migrate projects (2-3 days) — **Updated 2026-06-03**

**jira-kanban-from-spreadsheet** (3-4 hours) — **MIGRATE FIRST** (security priority):

1. Add `tdt-sheets>=0.1.0` to dependencies
2. **Remove gspread dependency** (unmaintained, security risk)
3. Replace GspreadBackend with tdt-sheets SDK backend
4. Add write capability (now available via SDK)
5. Run tests
6. Remove old sheets/reader.py

**android-scan-agent** (3-4 hours):

1. Add `tdt-sheets>=0.1.0` to dependencies
2. Replace sheet_writer.py with tdt-sheets imports
3. **Gains 3-level fallback** (currently only GOOGLE_APPLICATION_CREDENTIALS)
4. **Gains token refresh** (currently missing)
5. Run tests, fix any issues
6. Remove old sheet_writer.py

**jira-daily-reports** (4-6 hours):

1. Add `tdt-sheets>=0.1.0` to dependencies
2. Refactor delivery/sheet.py to use tdt-sheets
3. Keep domain-specific functions (freshness state, sprint ticket scope, etc.)
4. Run existing test suite
5. Remove duplicated auth/client code (~500 lines)

**jira-epic-report** (4-6 hours):

1. Add `tdt-sheets>=0.1.0` to dependencies
2. Refactor spreadsheet_reporter.py to use tdt-sheets
3. Keep domain-specific functions (\_render_blocking_chain_tree, \_apply_formatting, etc.)
4. Run full test suite (49 tests)
5. Remove duplicated auth/client code (~1,000 lines)

**Migration Order Change**: jira-kanban moved to first position (from second) due to unmaintained gspread dependency identified in security analysis.

### Phase 3: Documentation and standards (0.5 days)

1. Update ecosystem documentation
2. Create "TDT Google Sheets Standards" guide
3. Document when to use tdt-sheets vs gws CLI directly
4. Add examples for common patterns

### Rollback Strategy

If migration fails for a project:

1. Revert dependency change
2. Restore old implementation file from git
3. Project continues using original code
4. Other projects unaffected (independent migrations)

### Success Criteria

**Original Criteria**:
- ✅ All 4 projects use tdt-sheets
- ✅ All existing tests pass (no regression)
- ✅ Total Sheets code reduced from ~3,165 to <1,000 lines
- ✅ Single authentication implementation across ecosystem
- ✅ Backend flexibility maintained (sdk/cli)
- ✅ gspread completely removed, jira-kanban migrated to SDK
- ✅ Batch operations working in all projects (90% API call reduction)

**Additional Criteria** (from 2026-06-03 security analysis):
- ✅ Zero-downtime credential rotation capability (mtime-based caching)
- ✅ 80%+ test coverage including security tests
- ✅ Structured logging for all authentication operations
- ✅ File permission warnings documented and implemented
- ✅ Configurable scopes for least-privilege access
- ✅ Credential JSON validation with clear error messages

## Open Questions

1. **Versioning strategy**: Semantic versioning starting at 0.1.0, or 1.0.0? → Decision: Start at 0.1.0, allows breaking changes pre-1.0
2. **Repository location**: Under tdt GitHub org or separate? → Decision: TBD based on org structure
3. **License**: Match tdt ecosystem license (if any) or MIT? → Decision: Match ecosystem
4. **PyPI package name**: `tdt-sheets` or `tdt_sheets`? → Decision: `tdt-sheets` (hyphen, matches proposal)
5. **Drive API features**: Should we include Drive operations (folder management, permissions)? → Decision: Deferred to v0.2.0, focus on Sheets operations for MVP

## Research and Analysis

**Authentication Deep Dive** (2026-06-03):

Comprehensive security analysis conducted across all 4 existing implementations revealed:
- jira-epic-report and jira-daily-reports have 99% identical authentication code (production-verified)
- 5 critical security gaps identified in existing patterns
- Service account credentials validated: `/Users/lekhanhvinh/.tdt/philip-project-1-496009-1be73cdedca8.json`
- jira-kanban uses unmaintained gspread library (security risk, requires urgent migration)

**Documentation**:
- `AUTHENTICATION_ANALYSIS.md` — 15 sections analyzing patterns, security, token refresh, environment config
- `SECURITY_ENHANCEMENTS.md` — 7 proposed enhancements with implementation details and test requirements
- `RESEARCH_SUMMARY.md` — Executive summary, findings, recommendations, updated timeline

**Key Findings**:
1. All SDK-using projects already implement batch operations (validates batch-first approach)
2. Token refresh with 60s buffer is proven pattern (extract from jira-epic-report)
3. Cache invalidation on file change enables zero-downtime credential rotation
4. Configurable scopes allow least-privilege (android-scan-agent only needs spreadsheets scope)
5. Structured logging essential for production debugging
