# Design — sprint-switch-config-consolidation

## Architecture

### Before (current state)
```
~/.tdt/.env  ──→  os.environ  ──→  9+ consumers read via os.getenv()
     │
     └── SHEET_LINKS gid cache (write-back loop)

~/.tdt/config.toml  ──→  kbs pipeline, scheduler
~/.tdt/config.yaml   ──→  SchedulerSettings
dbos_scheduling.py   ──→  hardcoded fallback
```

### After (target state)
```
~/.tdt/config.toml [current_sprint]  ← SSOT
       │
       ├──→ load_sprint_config() bridge → os.environ (backward compat)
       ├──→ sprint-switch CLI writes here + derives .env
       └──→ config.yaml updated by sprint-switch (SchedulerSettings)

~/.tdt/.env  ← credentials ONLY (no sprint config)
       │
       └── load_tdt_env() loads, bridge injects config.toml values

SHEET_LINKS  ← DELETED (tab IDs discovered dynamically via Sheets API)
_env_quoting.py  ← DELETED
persist_gid_to_sheet_links()  ← DELETED (2 files)
migrate_legacy_state_*()  ← DELETED (dead code)
```

## Config schema (`~/.tdt/config.toml`)

```toml
current_sprint = 19

[google_sheets]
sprint_spreadsheet_id = "1_Nc_6H7KoKTD_gMQoItK6PSLUnIr9kDArTfsx_iFdto"
epic_report_url = "https://docs.google.com/spreadsheets/d/..."
android_scan_id = "1DSaaBD3-..."
ios_scan_id = "1BcmLpeE-..."

[sprint_sheets.sprint_19]
spreadsheet_id = "1_Nc_6H7KoKTD_gMQoItK6PSLUnIr9kDArTfsx_iFdto"
filter_id = 15571
board_id = 1273
created_at = "2026-07-21"

[sprint_sheets.sprint_18]  # archived
spreadsheet_id = "1f7T-sY-dCw4O9vWjoj8Djdr0sqNFIFxaNSY3W5sfesc"
filter_id = 15487
board_id = 1241
archived_at = "2026-07-21"

[jira]
site = "https://psplit.atlassian.net"
project_key = "PUB"
filter_id = 15571
board_id = 1273
default_filter_ids = "15571"

[sprint]
target_status = "Done"

[person_capacity]
timezone = "Asia/Ho_Chi_Minh"
window_days = 14
sheet_name = "Person Capacity"
mapping_sheet_name = "Dropdown Keys - Do Not Delete -"

[dev_performance]
lookback_hours = 720
dev_in_charge_field = "customfield_11520"

[report_freshness]
enabled = true
target = "sprint-sheet"
debounce_seconds = 300
```

## Bridge function (`tdt_core.config`)

New module `tdt_core.config` with `load_sprint_config()`:

```python
def load_sprint_config() -> None:
    """Read config.toml and inject values into os.environ for backward compat."""
    config = _load_toml()
    sprint_num = config.get("current_sprint")
    if not sprint_num:
        return  # No new schema yet, .env is the SSOT
    section = config.get("sprint_sheets", {}).get(f"sprint_{sprint_num}", {})
    if sid := section.get("spreadsheet_id"):
        os.environ.setdefault("SPREADSHEET_ID", sid)
    jira = config.get("jira", {})
    if fids := jira.get("default_filter_ids"):
        os.environ.setdefault("JIRA_DEFAULT_FILTER_IDS", str(fids))
    if pk := jira.get("project_key"):
        os.environ.setdefault("JIRA_PROJECT_KEY", pk)
    pc = config.get("person_capacity", {})
    if tz := pc.get("timezone"):
        os.environ.setdefault("PERSON_CAPACITY_TIMEZONE", tz)
    if wd := pc.get("window_days"):
        os.environ.setdefault("PERSON_CAPACITY_WINDOW_DAYS", str(wd))
    # ... dev_performance, report_freshness, sprint
```

Called in `load_tdt_env()` after `.env` is loaded. `setdefault` ensures `.env` values still override if present (backward compat during migration).

**Graceful fallback:** If `config.toml` doesn't exist or lacks `current_sprint`, `load_sprint_config()` is a no-op. Consumers continue reading from `.env`.

## `sprint-switch` CLI command

```
jira-daily-reports sprint-switch <spreadsheet-url-or-id> [--dry-run]
```

### Steps

1. **Parse input** — Extract spreadsheet ID from URL or raw ID
2. **Read workbook title** — Via Sheets API → parse sprint number + dates
3. **Read current config** — Load `config.toml`, find current sprint number
4. **Update `config.toml`**:
   - Set `current_sprint = <new>`
   - Add `[sprint_sheets.sprint_<new>]` with spreadsheet_id
   - Archive previous sprint (add `archived_at`)
   - Update `[google_sheets] sprint_spreadsheet_id`
   - Update `[jira] filter_id`, `board_id`, `default_filter_ids`
5. **Derive `.env` updates**:
   - Set `SPREADSHEET_ID=<new>`
   - Clear `SHEET_LINKS=""`
   - Set `JIRA_DEFAULT_FILTER_IDS=<new_filter_id>`
6. **Delete stale freshness state**
7. **Run `sprint-bootstrap --live`** — Create Jira filter + board
8. **Update `config.toml` with resolved IDs** — Write filter_id and board_id
9. **Print summary**

### Error handling

- Missing credentials → clear error with remediation
- Workbook title doesn't match "Sprint N (dates)" → reject
- Sprint-bootstrap failure → report error, leave config partially updated
- Network/timeout → retry 3x with backoff

## Var migration map

| Current `.env` key | New `config.toml` location | Consumer |
|---------------------|---------------------------|----------|
| `SPREADSHEET_ID` | Derived from `[sprint_sheets.sprint_N].spreadsheet_id` | 9+ modules, webhook-receiver Settings, freshness dispatcher |
| `SHEET_LINKS` | Derived, not stored (cleared on switch) | tdt_sheet.py, catalog/writer.py, dev_performance/sheet_writer.py |
| `JIRA_DEFAULT_FILTER_IDS` | `[jira] default_filter_ids` | config.py:require_jira_filter_id() |
| `JIRA_PROJECT_KEY` | `[jira] project_key` | ReportConfig, _get_jira_and_project() |
| `SPRINT_TARGET_STATUS` | `[sprint] target_status` | sprint_report_sheet.py |
| `PERSON_CAPACITY_TIMEZONE` | `[person_capacity] timezone` | sprint_report_sheet.py |
| `PERSON_CAPACITY_WINDOW_DAYS` | `[person_capacity] window_days` | sprint_report_sheet.py |
| `PERSON_CAPACITY_SHEET_NAME` | `[person_capacity] sheet_name` | sprint_report_sheet.py |
| `PERSON_CAPACITY_MAPPING_SHEET_NAME` | `[person_capacity] mapping_sheet_name` | person_worklog_source.py |
| `DEV_PERFORMANCE_LOOKBACK_HOURS` | `[dev_performance] lookback_hours` | dev_performance/cli.py |
| `DEV_PERFORMANCE_DEV_IN_CHARGE_FIELD` | `[dev_performance] dev_in_charge_field` | dev_performance/cli.py |
| `REPORT_FRESHNESS_ENABLED` | `[report_freshness] enabled` | webhook-receiver Settings |
| `REPORT_FRESHNESS_TARGET` | `[report_freshness] target` | webhook-receiver Settings |
| `REPORT_FRESHNESS_DEBOUNCE_SECONDS` | `[report_freshness] debounce_seconds` | webhook-receiver Settings |
| `REPORT_FRESHNESS_COMMAND` | `[report_freshness] command` | webhook-receiver FreshnessDispatcher |

## Deployment constraints (from research)

### Docker scheduler container

- **Volume mount**: `~/.tdt:/home/agent/.tdt:rw` — config.toml is accessible
- **env_file**: `~/.tdt/.env` loaded into container env
- **Hardcoded override**: `PERSON_CAPACITY_MAPPING_SHEET_NAME` in compose.yaml OVERRIDES config.toml. **Must be removed.**
- **Bridge timing**: `load_tdt_env()` is called by scheduler_setup.py at startup → `load_sprint_config()` runs → config.toml values injected into os.environ → subprocesses inherit

### launchd webhook-receiver

- **No env_file**: launchd plist only sets PATH and HOME
- **App calls `load_tdt_env()`** in Settings.__init__() → bridge runs
- **Freshness dispatcher passes `**os.environ`** to subprocess → SPREADSHEET_ID inherited
- **`REPORT_FRESHNESS_COMMAND`** uses `$SPREADSHEET_ID` in shell string → evaluated at subprocess runtime → bridge must inject before webhook-receiver starts

### config.yaml (SchedulerSettings)

- **Loaded independently** by `tdt_core.scheduler.settings` from `$TDT_HOME/config.yaml`
- **Contains `sprint_report.spreadsheet_url`** — used by scheduler
- **Options**: (a) sprint-switch also updates config.yaml, OR (b) SchedulerSettings reads from config.toml. **Recommendation: (a)** — simpler, no code change in tdt-core scheduler.

### dbos_scheduling.py fallback

- **Hardcoded spreadsheet ID** (line 343) — used when SPREADSHEET_ID env var is missing
- **Must be updated** to read from config.toml via `get_sprint_config()` instead of hardcoding

### TOML writing approach

- **`tomllib`** (Python 3.11+) available for reading — no writer
- **`tomlkit`** NOT installed — must add as dependency for comment-preserving writes
- **Recommendation**: add `tomlkit` to `tdt-core/pyproject.toml` — standard Python TOML library with comment preservation

### SHEET_LINKS dual-format bug

- **jira-daily-reports**: `;`-separated `"Tab Name|URL#gid=N"` entries (via `_env_quoting.py`)
- **kbs config.py**: `,`-separated URLs (via `v.split(",")`)
- **The .env uses `;` separator** — kbs parsing is broken (treats entire string as one entry)
- **Resolution**: both should use `tdt_sheets.resolve_gid()` API instead of parsing env var
