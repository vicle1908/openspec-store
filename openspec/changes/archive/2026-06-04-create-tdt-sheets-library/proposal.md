## Why

The tdt ecosystem has **4 projects** using Google Sheets with **inconsistent implementations**: different libraries (googleapiclient, gspread, gws CLI), duplicated authentication code, and no shared patterns. This creates maintenance burden, prevents code reuse, and makes it harder to improve Sheets integration across the ecosystem. A shared library will provide consistent authentication, unified API, and backend flexibility while reducing code duplication from ~3,165 lines across 4 projects to a single maintained implementation.

**Modern Technology Stack**:

- Python 3.14+ (all ecosystem projects use 3.14.5)
- google-api-python-client (official, actively maintained, API v4)
- Modern type hints (X | Y, dataclasses with slots=True, functools.cache)
- Batch operations as primary feature (90% API call reduction)
- **gspread dropped entirely** (unmaintained, API v3, slow)

## What Changes

- **New Repository**: Create `tdt-sheets` shared Python library
- **Unified Authentication**: Single service account authentication with 3-level fallback and credential caching
- **Security Enhancements** ⭐ NEW (2026-06-03): Cache invalidation on file mtime, configurable scopes, credential validation, structured logging, file permission warnings
- **Backend Abstraction**: Support multiple backends (googleapiclient SDK, gws CLI) via Protocol pattern
- **Modern Python Patterns**: Python 3.14 features (lazy annotations, slots=True dataclasses, modern type hints)
- **Batch Operations Primary**: batch_read, batch_write, batch_clear as core features (not optional)
- **Common Operations**: Standardized read/write/clear operations for spreadsheets
- **Utility Functions**: URL parsing, GID-to-sheet-name resolution
- **Migration Path**: Replace existing implementations in 4 projects:
  - **jira-kanban-from-spreadsheet** ⭐ MIGRATE FIRST (security priority): Replace `sheets/reader.py` (~400 lines), remove unmaintained gspread
  - android-scan-agent: Replace `sheet_writer.py` (~300 lines), gains 3-level fallback + token refresh
  - jira-daily-reports: Replace `delivery/sheet.py` (~800 lines)
  - jira-epic-report: Replace `spreadsheet_reporter.py` (1,665 lines)

## Capabilities

### New Capabilities

- `sheets-authentication`: Service account authentication with credential caching, token refresh, and 3-level fallback path resolution (GOOGLE_SERVICE_ACCOUNT_PATH → GOOGLE_APPLICATION_CREDENTIALS → ~/.tdt/google-service-account.json)
- `sheets-authentication-security` ⭐ NEW: Cache invalidation on file mtime (zero-downtime rotation), configurable scopes, credential JSON validation, file permission warnings, structured logging
- `sheets-client`: Unified client interface with backend selection (sdk/cli) for read/write/clear/batch operations on Google Sheets
- `sheets-backends`: Backend abstraction supporting googleapiclient SDK (primary) and gws CLI (OAuth workflows)
- `sheets-utils`: Utility functions for URL parsing (spreadsheet ID + GID extraction) and GID-to-sheet-name resolution via Sheets API

### Modified Capabilities

<!-- No existing capabilities are being modified - this is a net-new library extraction -->

## Impact

**Code Changes**:

- **New Repository**: `tdt-sheets` (~500-800 lines extracted and unified)
- **jira-epic-report**: Remove `epic_report/reporters/spreadsheet_reporter.py`, replace with `tdt-sheets` dependency
- **jira-daily-reports**: Remove `src/jira_daily_reports/delivery/sheet.py`, replace with `tdt-sheets` dependency
- **jira-kanban-from-spreadsheet**: Remove `src/kbs/sheets/reader.py`, replace with `tdt-sheets` dependency
- **android-scan-agent**: Remove `src/android_scan_agent/sheet_writer.py`, replace with `tdt-sheets` dependency

**Dependencies**:

- All 4 projects add: `tdt-sheets>=0.1.0`
- tdt-sheets library requires: `google-auth>=2.0.0`, `google-api-python-client>=2.0.0`
- Python version: `>=3.14` (matches ecosystem standard)

**Configuration**:

- Standardize on: `GOOGLE_SERVICE_ACCOUNT_PATH` environment variable
- Maintain backward compatibility with `GOOGLE_APPLICATION_CREDENTIALS`
- Use consistent `~/.tdt/google-service-account.json` default across ecosystem

**Testing**:

- New: Comprehensive test suite for tdt-sheets (~50 tests: 40 base + 10 security)
- Security tests: File permissions, cache invalidation, credential validation, structured logging
- Migrate: Existing tests from all 4 projects
- Integration: Verify no regression in functionality for all 4 consumers

**Timeline** ⭐ UPDATED (2026-06-03):

- Phase 1: Create tdt-sheets library (2.5 days) — +0.5 days for security enhancements
- Phase 2: Migrate 4 projects (2-3 days) — jira-kanban first (security priority)
- Phase 3: Documentation and standards (0.5 days) — includes security docs
- **Total**: 4-5 days (was 3-4 days)

**Security Analysis** (2026-06-03):

- Authentication patterns validated across all 4 projects
- jira-epic-report + jira-daily-reports have identical 99% auth code (production-verified)
- Service account credentials verified: `~/.tdt/philip-project-1-496009-1be73cdedca8.json`
- 5 critical security enhancements identified and added to v0.1.0
- jira-kanban migration prioritized (unmaintained gspread dependency = security risk)

**Documentation**:

- See `AUTHENTICATION_ANALYSIS.md` for detailed implementation analysis
- See `SECURITY_ENHANCEMENTS.md` for security features and test requirements
- See `RESEARCH_SUMMARY.md` for executive summary and recommendations
