# google-sheets-migration Specification

## Purpose

Define the migration path from direct `googleapiclient` usage to the canonical `tdt_sheets` library in code-daily-scan and related packages.

## ADDED Requirements

### Requirement: Use tdt_sheets for all Google Sheets operations
All Google Sheets operations SHALL use `tdt_sheets.SheetsClient` with `ServiceAccountAuth.from_env()`. Direct usage of `googleapiclient.discovery.build()` is prohibited.

#### Scenario: Migrate FP-Tracking writes to tdt_sheets
- **WHEN** code needs to write false positive records to Google Sheets
- **THEN** use `append_row()` from `sheets/writer.py`
- **AND** use `ensure_tab_exists()` to create tabs if needed

#### Scenario: Migrate report-metrics to tdt_sheets (DEFERRED)
- **WHEN** migrating the `report-metrics` command in `code_daily_scan/cli.py`
- **THEN** use `SheetsClient` from `tdt_sheets` via `sheets/writer.py`
- **AND** use batch operations for Metrics tab writes

### Requirement: Leverage existing tdt_sheets infrastructure
Code MUST delegate to existing `sheets/writer.py` infrastructure before implementing new sheet logic.

#### Scenario: Reuse existing writer module
- **WHEN** code needs to write to Google Sheets
- **THEN** import from `code_daily_scan.sheets.writer`
- **AND** use the existing `SheetsClient` instance via `_get_client()`

#### Scenario: Add new helper functions to writer.py
- **WHEN** needed operations are not available in writer.py
- **THEN** add new helpers (e.g., `append_row()`, `ensure_tab_exists()`)
- **AND** do NOT use direct `googleapiclient` in CLI code

### Requirement: Centralize budget configuration
Budget configuration SHALL be read from environment variables with a consistent pattern, not hardcoded in multiple places.

#### Scenario: Consistent budget env var pattern
- **WHEN** reading monthly budget configuration
- **THEN** use `get_monthly_budget(platform)` from `health.py`
- **AND** use `{PLATFORM}_SCAN_MONTHLY_BUDGET_USD` env var pattern
- **AND** centralize default value in `health.py` constants

## Implementation Notes

### Completed Migrations

1. **FP-Tracking writes** - Uses `ensure_tab_exists()` and `append_row()` from `sheets/writer.py`
2. **Budget configuration** - Uses `get_monthly_budget()` from `health.py`

### Helper functions in `code_daily_scan/sheets/writer.py`:

```python
def _get_client() -> SheetsClient:
    """Get or create the SheetsClient using tdt-sheets 3-level credential fallback."""
    auth = ServiceAccountAuth.from_env()
    return SheetsClient(auth=auth, backend="sdk")

def ensure_tab_exists(spreadsheet_id: str, tab_name: str) -> None:
    """Ensure a tab exists in the spreadsheet, creating it if necessary."""
    # Implementation uses tdt_sheets internally

def append_row(spreadsheet_id: str, tab_name: str, row: list[str]) -> None:
    """Append a row to a sheet tab using tdt-sheets."""
    # Implementation uses tdt_sheets internally
```

### Centralized budget in `code_daily_scan/health.py`:

```python
DEFAULT_MONTHLY_BUDGET_USD = 5.0
DEFAULT_SCAN_COST_USD = 0.12

def get_monthly_budget(platform: str) -> float:
    """Get monthly budget from environment variable or default."""
    import os
    return float(os.getenv(f"{platform.upper()}_SCAN_MONTHLY_BUDGET_USD", str(DEFAULT_MONTHLY_BUDGET_USD)))
```

## REMOVED Requirements

### Requirement: Direct googleapiclient usage in cli.py
**Reason**: Replaced by tdt_sheets via writer.py helpers
**Migration**: Use `append_row()` and `ensure_tab_exists()` from `sheets/writer.py`

## Files Affected

| File | Change | Status |
|------|--------|--------|
| `code_daily_scan/cli.py` | FP-Tracking uses tdt_sheets | ✅ Complete |
| `code_daily_scan/cli.py` | `report-metrics` uses googleapiclient | ⏳ Deferred |
| `code_daily_scan/health.py` | Budget helpers centralized | ✅ Complete |
| `code_daily_scan/sheets/writer.py` | Added `append_row()`, `ensure_tab_exists()` | ✅ Complete |

## Deferred Work

### report-metrics command migration
The `report-metrics` command in `cli.py` still uses direct `googleapiclient` imports. Migration should:
1. Use `SheetsClient` from `sheets/writer.py`
2. Create Metrics tab via `ensure_tab_exists()`
3. Write metrics rows via batch operations
