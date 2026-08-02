# Design — dev-performance-sprint-scoping

## Architecture

### Current State

```
┌─────────────────────────────────────────────────────────────┐
│                    CURRENT DATA FLOW                        │
└─────────────────────────────────────────────────────────────┘

┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│ Sprint Sheet │     │Person Capacity│     │Dev Performance│
│              │     │              │     │              │
│ Scoped to:   │     │ Scoped to:   │     │ Scoped to:   │
│ Filter #15571│     │ Workbook     │     │ Rolling      │
│ (Sprint 19)  │     │ dates        │     │ 30-day window│
└──────────────┘     └──────────────┘     └──────────────┘
       │                   │                    │
       ▼                   ▼                    ▼
  Jira filter          Jira worklogs      Jira updated
  query               by date range       >= -720h
```

### Proposed State

```
┌─────────────────────────────────────────────────────────────┐
│                    PROPOSED DATA FLOW                       │
└─────────────────────────────────────────────────────────────┘

┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│ Sprint Sheet │     │Person Capacity│     │Dev Performance│
│              │     │              │     │              │
│ Scoped to:   │     │ Scoped to:   │     │ Scoped to:   │
│ Filter #15571│     │ Workbook     │     │ Sprint dates │
│ (Sprint 19)  │     │ dates        │     │ (default)    │
└──────────────┘     └──────────────┘     └──────────────┘
       │                   │                    │
       ▼                   ▼                    ▼
  Jira filter          Jira worklogs      Jira updated
  query               by date range       >= sprint_start
                                           AND <= sprint_end
                                           
                                  OR (if override):
                                           updated >= -N hours
```

## Config Schema

### config.toml changes

```toml
[dev_performance]
lookback_hours = 720          # Fallback when sprint_scoped=false
dev_in_charge_field = "customfield_11520"
sprint_scoped = true          # NEW: use sprint dates by default
```

### Precedence (highest to lowest)

1. CLI flag: `--lookback-days 30` (explicit override)
2. ENV var: `DEV_PERFORMANCE_LOOKBACK_HOURS=720` (explicit override)
3. Config: `[dev_performance] sprint_scoped = false` + `lookback_hours = 720`
4. Sprint dates from config.toml (default when `sprint_scoped = true`)
5. Hardcoded fallback: 720 hours (30 days)

## Implementation

### Modified `_lookback_hours()` function

```python
def _lookback_hours() -> int:
    """Get lookback hours: sprint period (default) or override.
    
    Precedence:
    1. CLI --lookback-days flag (passed as env var)
    2. DEV_PERFORMANCE_LOOKBACK_HOURS env var
    3. Config.toml [dev_performance] sprint_scoped + lookback_hours
    4. Sprint dates from config.toml
    5. Hardcoded fallback: 720 hours
    """
    # 1. Check for explicit override (env var)
    override = os.getenv("DEV_PERFORMANCE_LOOKBACK_HOURS")
    if override:
        return int(override)
    
    # 2. Check config.toml for sprint_scoped setting
    from tdt_core.config import get_sprint_config
    config = get_sprint_config()
    dev_perf = config.get("dev_performance", {})
    
    if not dev_perf.get("sprint_scoped", True):
        # sprint_scoped=false: use lookback_hours from config
        return dev_perf.get("lookback_hours", DEFAULT_LOOKBACK_HOURS)
    
    # 3. Try sprint dates from config.toml
    from tdt_core.config import get_current_sprint_section
    from tdt_core.sprint_scope import parse_sprint_dates, parse_sprint_date_range
    
    section = get_current_sprint_section()
    spreadsheet_id = section.get("spreadsheet_id", "")
    if spreadsheet_id:
        try:
            from jira_daily_reports.delivery.tdt_sheet import read_spreadsheet_title
            title = read_spreadsheet_title(spreadsheet_id)
            sprint_dates = parse_sprint_dates(title)
            window = parse_sprint_date_range(sprint_dates)
            if window:
                start, end = window
                sprint_hours = (end - start).days * 24
                return sprint_hours
        except Exception:
            pass  # Fall through to default
    
    # 4. Fallback to 30 days
    return DEFAULT_LOOKBACK_HOURS
```

### CLI flag addition

Add `--lookback-days` flag to dev-performance CLI:

```python
@app.callback(invoke_without_command=True)
def dev_performance_callback(
    ctx: typer.Context,
    spreadsheet_id: str = typer.Option(None, "--spreadsheet-id"),
    prune_cache: bool = typer.Option(False, "--prune-cache"),
    dry_run: bool = typer.Option(False, "--dry-run"),
    lookback_days: int = typer.Option(None, "--lookback-days"),  # NEW
) -> None:
    if lookback_days is not None:
        os.environ["DEV_PERFORMANCE_LOOKBACK_HOURS"] = str(lookback_days * 24)
    # ... rest of callback
```

## Data Flow Changes

### JQL Query Modification

Current:
```python
base_filter = f"{dev_in_charge_field_id} in ({quoted_ids}) AND updated >= -{lookback_hours}h"
```

Proposed (when sprint_scoped=true):
```python
if sprint_window:
    start, end = sprint_window
    base_filter = f"{dev_in_charge_field_id} in ({quoted_ids}) AND updated >= '{start}' AND updated <= '{end}'"
else:
    base_filter = f"{dev_in_charge_field_id} in ({quoted_ids}) AND updated >= -{lookback_hours}h"
```

### Window Calculation

Current:
```python
window_start = now - timedelta(hours=lookback_hours)
window_end = now
```

Proposed (when sprint_scoped=true):
```python
if sprint_window:
    window_start, window_end = sprint_window
    window_start = datetime.combine(window_start, datetime.min.time())
    window_end = datetime.combine(window_end, datetime.max.time())
else:
    window_start = now - timedelta(hours=lookback_hours)
    window_end = now
```

## Testing

1. **Unit tests** for `_lookback_hours()` with various config combinations
2. **Integration test** with mock sprint dates
3. **Manual test**: run dev-performance with sprint 19 dates, verify window is 20 Jul – 31 Jul
4. **Override test**: run with `--lookback-days 30`, verify override works
5. **Backward compat test**: run with `DEV_PERFORMANCE_LOOKBACK_HOURS=720`, verify override works
