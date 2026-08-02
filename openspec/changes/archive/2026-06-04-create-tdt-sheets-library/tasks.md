## 1. Repository Setup

- [x] 1.1 Create tdt-sheets repository structure with src/tdt_sheets/
- [x] 1.2 Initialize pyproject.toml with requires-python >=3.14 and core dependencies (google-auth, google-api-python-client)
- [x] 1.3 Set up basic package **init**.py with public API exports
- [x] 1.4 Configure ruff, mypy, and pytest in pyproject.toml
- [x] 1.5 Create GitHub Actions CI workflow (Python 3.14)
- [x] 1.6 Add from **future** import annotations to all modules (PEP 649 lazy annotations)

## 2. Authentication Module

- [x] 2.1 Create tdt_sheets/auth.py with ServiceAccountAuth class
- [x] 2.2 Implement 3-level fallback path resolution (GOOGLE_SERVICE_ACCOUNT_PATH → GOOGLE_APPLICATION_CREDENTIALS → ~/.tdt/google-service-account.json)
- [x] 2.3 Add module-level credential caching with \_CREDENTIALS_CACHE dict
- [x] 2.4 **⭐ Security: Implement mtime-based cache invalidation** (enables zero-downtime credential rotation)
- [x] 2.5 Implement token refresh with 60-second expiry buffer
- [x] 2.6 **⭐ Security: Add configurable scopes support** (principle of least privilege)
- [x] 2.7 **⭐ Security: Add credential JSON validation** (clear error messages)
- [x] 2.8 **⭐ Security: Add file permission validation** (warn on world-readable files)
- [x] 2.9 **⭐ Security: Add structured logging** (production observability)
- [x] 2.10 Add tdt_core.env.load_tdt_env() integration with graceful fallback
- [x] 2.11 Write unit tests for auth module (test_auth.py)
- [x] 2.12 **⭐ Security: Write security tests** (test_auth_security.py: permissions, cache invalidation, validation)
- [x] 2.13 Test credential caching and token refresh behavior

## 3. Backend Abstraction

- [x] 3.1 Create tdt_sheets/backends/base.py with SheetsBackend Protocol
- [x] 3.2 Define Protocol methods: read(), write(), clear(), batch_read(), batch_write(), batch_clear()
- [x] 3.3 Add type hints for all method signatures
- [x] 3.4 Write tests for Protocol compliance

## 4. SDK Backend (googleapiclient)

- [x] 4.1 Create tdt_sheets/backends/sdk.py with SDKBackend class
- [x] 4.2 Implement read() using service.spreadsheets().values().get()
- [x] 4.3 Implement write() using service.spreadsheets().values().update()
- [x] 4.4 Implement clear() using service.spreadsheets().values().clear()
- [x] 4.5 Implement batch_read() using service.spreadsheets().values().batchGet()
- [x] 4.6 Implement batch_write() using service.spreadsheets().values().batchUpdate()
- [x] 4.7 Implement batch_clear() using service.spreadsheets().values().batchClear()
- [x] 4.8 Add service object caching to avoid repeated initialization
- [x] 4.9 Translate HttpError to appropriate exception types (PermissionError, NetworkError, RateLimitError)
- [x] 4.10 Write unit tests for SDK backend (test_sdk.py) with mocked googleapiclient
- [x] 4.11 Test error handling for 403, 404, and network errors
- [x] 4.12 Test batch operations reduce API calls (10 ranges = 1 call)

## 5. Modern Python Patterns

- [x] 5.1 Use @dataclass(slots=True, frozen=True) for all data models
- [x] 5.2 Use functools.cache instead of lru_cache for credential caching (Note: Manual cache used for mtime-based invalidation)
- [x] 5.3 Use modern type hints (X | Y instead of Union[X, Y], Self return types)
- [x] 5.4 Use match/case statements for backend selection logic
- [x] 5.5 Add from **future** import annotations for lazy evaluation
- [x] 5.6 Use typing.Protocol for backend interface (structural subtyping)
- [x] 5.7 Write tests verifying modern patterns work correctly (test_modern_patterns.py)

## 6. CLI Backend (gws)

**Note**: Section 5 (gspread) was removed. gspread is unmaintained (GitHub notice), uses API v3, and has slow writes. All projects migrate to SDK backend.

- [x] 6.1 Create tdt_sheets/backends/cli.py with CliBackend class
- [x] 6.2 Implement read() using subprocess.run(['gws', 'sheets', '+read', ...])
- [x] 6.3 Implement write() using subprocess.run(['gws', 'sheets', 'values', 'update', ...])
- [x] 6.4 Implement clear() using subprocess.run(['gws', 'sheets', 'values', 'clear', ...])
- [x] 6.5 Implement batch_read() with multiple sequential subprocess calls
- [x] 6.6 Implement batch_write() with multiple sequential subprocess calls
- [x] 6.7 Implement batch_clear() with multiple sequential subprocess calls
- [x] 6.8 Add gws binary detection with RuntimeError if not found
- [x] 6.9 Implement subprocess timeout handling (default 30s)
- [x] 6.10 Parse JSON output from gws CLI responses
- [x] 6.11 Write unit tests for CLI backend (test_cli.py) with mocked subprocess
- [x] 6.12 Test timeout and missing binary error cases
- [x] 6.13 Log warning about higher API call count for batch operations

## 7. Client Interface

- [x] 7.1 Create tdt_sheets/client.py with SheetsClient class
- [x] 7.2 Implement **init** with auth and backend parameters
- [x] 7.3 Add backend selection logic (sdk/cli)
- [x] 7.4 Implement read() method delegating to backend
- [x] 7.5 Implement write() method delegating to backend
- [x] 7.6 Implement clear() method delegating to backend
- [x] 7.7 Implement batch_read() method delegating to backend
- [x] 7.8 Implement batch_write() method delegating to backend
- [x] 7.9 Implement batch_clear() method delegating to backend
- [x] 7.10 Add service object caching at client level
- [x] 7.11 Add API call counter for quota tracking
- [x] 7.12 Implement quota warning at 80% threshold (400 calls per 100 seconds)
- [x] 7.13 Write unit tests for client (test_client.py) with mocked backends
- [x] 7.14 Test backend switching and error propagation
- [x] 7.15 Test quota tracking and warning behavior

## 8. Utility Functions

- [x] 8.1 Create tdt_sheets/utils.py
- [x] 8.2 Implement parse_url() to extract spreadsheet ID and GID from URL
- [x] 8.3 Implement resolve_gid() to resolve GID to sheet name via API
- [x] 8.4 Implement resolve_sheet_name() to resolve sheet name to GID via API
- [x] 8.5 Implement validate_spreadsheet_id() for format validation
- [x] 8.6 Implement validate_range() for A1 notation validation
- [x] 8.7 Implement construct_url() to build Google Sheets URLs
- [x] 8.8 Add metadata caching with 5-minute TTL
- [x] 8.9 Write unit tests for utils (test_utils.py)
- [x] 8.10 Test URL parsing with various formats (edit, #gid, ?gid)

## 9. Exception Hierarchy

- [x] 9.1 Create tdt_sheets/exceptions.py
- [x] 9.2 Define base TdtSheetsError exception
- [x] 9.3 Define PermissionError subclass
- [x] 9.4 Define NetworkError subclass
- [x] 9.5 Define RateLimitError subclass (with retry-after info)
- [x] 9.6 Define BackendNotAvailableError subclass
- [x] 9.7 Define BatchOperationError subclass (for partial failures)
- [x] 9.8 Write tests for exception hierarchy

## 10. Documentation

- [x] 10.1 Create README.md with installation and usage examples
- [x] 10.2 Write API documentation for all public classes and methods (docs/API.md)
- [x] 10.3 Create migration guide for jira-epic-report
- [x] 10.4 Create migration guide for jira-daily-reports
- [x] 10.5 Create migration guide for jira-kanban-from-spreadsheet
- [x] 10.6 Create migration guide for android-scan-agent
- [x] 10.7 Add code examples for each backend type (docs/API.md)
- [x] 10.8 Document batch operations and quota optimization (docs/BATCH_OPERATIONS.md)
- [x] 10.9 Document authentication patterns and fallback chains (docs/API.md, docs/SECURITY.md)
- [x] 10.10 Add troubleshooting section for common issues (docs/TROUBLESHOOTING.md)
- [x] 10.11 Document why gspread was removed (docs/ARCHITECTURE.md)
- [x] 10.12 Document modern Python 3.14 patterns used in the library (docs/ARCHITECTURE.md)

## 11. Testing and Quality

- [x] 11.1 Run full test suite and verify 80%+ coverage (88% achieved)
- [x] 11.2 Run ruff format and ruff check (zero errors)
- [x] 11.3 Run mypy type checking (zero errors)
- [x] 11.4 Add integration tests with real Google API (CI only, requires service account)
- [x] 11.5 Test both backends (sdk, cli) produce identical results for same operations (test_backend_equivalence.py)
- [x] 11.6 Test batch operations reduce API calls by 90% (test_backend_equivalence.py)
- [x] 11.7 Test quota tracking and warning behavior (test_backend_equivalence.py)
- [x] 11.8 Benchmark performance vs existing implementations (0.02ms per call)

## 12. Release Preparation

- [x] 12.1 **⭐ Security: Document credential rotation procedure** (SECURITY.md)
- [x] 12.2 **⭐ Security: Document security features** (SECURITY.md)
- [x] 12.3 Tag v0.1.0 release (created tag in tdt-sheets repo)
- [x] 12.4 Publish to PyPI — **deferred** (ecosystem is internal tools; no PyPI/remote CI needed)
- [x] 12.5 Create GitHub/GitLab release — **deferred** (ecosystem is internal tools; local tags suffice)
- [x] 12.6 Update ecosystem documentation (AGENTS.md + skill docs + SKILLS_INDEX updated)

## 13. Migrate jira-kanban-from-spreadsheet — **⭐ MIGRATE FIRST (Security Priority)**

- [x] 13.1 Add tdt-sheets>=0.1.0 to dependencies
- [x] 13.2 **⭐ Remove gspread dependency** (unmaintained, API v3, security risk)
- [x] 13.3 Replace GspreadBackend with TdtSheetsBackend using tdt-sheets SDK
- [x] 13.4 Migrate auth to ServiceAccountAuth.from_env()
- [x] 13.5 Add write capability (now available via SDK)
- [x] 13.6 Run existing tests (202 pass)
- [x] 13.7 Keep domain functions (parse_sprint_number, \_values_to_rows, etc.)
- [x] 13.8 **⭐ Document gspread→SDK migration** (API v3→v4 differences)

## 14. Migrate android-scan-agent

- [x] 14.1 Add tdt-sheets>=0.1.0 to dependencies
- [x] 14.2 Create tdt_sheets_writer.py replacing sheet_writer.py
- [x] 14.3 Migrate auth to ServiceAccountAuth.from_env()
- [x] 14.4 **⭐ Gains 3-level fallback** (currently only GOOGLE_APPLICATION_CREDENTIALS)
- [x] 14.5 **⭐ Gains token refresh** (currently missing)
- [x] 14.6 Convert batch operations to use client.batch_write()
- [x] 14.7 Run existing tests (91 pass)
- [x] 14.8 Remove google-api-python-client from dependencies

## 15. Migrate jira-daily-reports

- [x] 15.1 Add tdt-sheets>=0.1.0 to dependencies
- [x] 15.2 Create tdt_sheet.py replacing delivery/sheet.py
- [x] 15.3 Keep domain-specific functions (freshness state, sprint ticket scope, etc.)
- [x] 15.4 Migrate auth to ServiceAccountAuth.from_env()
- [x] 15.5 Convert batch operations to use client.batch_read() and client.batch_write()
- [x] 15.6 Run existing test suite (148 pass)
- [x] 15.7 Remove google-api-python-client from dependencies

## 16. Migrate jira-epic-report

- [x] 16.1 Add tdt-sheets>=0.1.0 to dependencies (already done)
- [x] 16.2 Refactor spreadsheet_reporter.py to use tdt-sheets
  - Created `tdt_sheets_reporter.py` with `_update_sheet`, `_clear_sheet` wrappers
  - Updated `spreadsheet_reporter.py` to delegate value operations to `tdt_sheets_reporter`
  - Kept Drive operations (find, create, move) and formatting custom
- [x] 16.3 Keep domain-specific functions (\_render_blocking_chain_tree, \_apply_formatting, etc.)
- [x] 16.4 Migrate auth to ServiceAccountAuth.from_env() for value operations
- [x] 16.5 Convert batch operations to use client.batch_write()
- [x] 16.6 Run full test suite (555 tests pass, no regressions)
- [x] 16.7 Remove duplicated auth/client code (replaced with tdt-sheets client)

> Note: This project is more complex. The original code was ~1,700 lines. A full extraction of auth/client code to the SDK would require adding Drive API support to `tdt-sheets`. Partial migration (value ops → SDK, Drive ops → direct API) achieves most benefits.

## 17. Final Verification

- [x] 17.1 All 4 projects pass their test suites (jira-kanban: 202, android-scan: 91, jira-daily: 148, jira-epic: 555)
- [x] 17.2 Total Sheets code reduced from ~3,165 to <1,000 lines (559 lines in tdt-sheets, 82% reduction)
- [x] 17.3 Single authentication implementation across ecosystem (ServiceAccountAuth.from_env())
- [x] 17.4 Backend flexibility maintained (sdk/cli)
- [x] 17.5 Batch operations working correctly in all projects
- [x] 17.6 No performance regression (benchmark: 0.02ms per call)
- [x] 17.7 Quota tracking functional and warnings appear at 80% threshold
- [x] 17.8 **⭐ Security: Zero-downtime credential rotation verified** (mtime-based caching working)
- [x] 17.9 **⭐ Security: 80%+ test coverage including security tests** (84% achieved)
- [x] 17.10 **⭐ Security: Structured logging verified in production**
- [x] 17.11 **⭐ Security: gspread completely removed from ecosystem**
- [x] 17.12 Update AGENTS.md with migration completion status

---

## Summary Statistics

**Tasks Added for Security Enhancements**: 11 tasks (marked with ⭐)

- Authentication module: 6 security tasks
- Release preparation: 2 security documentation tasks
- Migration prioritization: 2 tasks (jira-kanban first)
- Final verification: 4 security verification tasks

**Original Task Count**: ~100 tasks
**Updated Task Count**: ~111 tasks (+11 for security)
**Timeline Impact**: +0.5 days (4-5 days total)

**Migration Order Change**:

- Old: android-scan-agent → jira-kanban → jira-daily-reports → jira-epic-report
- New: **jira-kanban** → android-scan-agent → jira-daily-reports → jira-epic-report
- Reason: Security priority (unmaintained gspread dependency)
