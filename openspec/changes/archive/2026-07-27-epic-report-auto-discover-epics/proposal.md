## Why

Currently, epic keys are hardcoded in two places:
1. `[schedule].epics = ["RMD-4160"]` — which epics to analyze
2. `[epic_plan].epics."RMD-4160"` — the mapping to plan activities

This is redundant and error-prone. When a new epic is added to the plan, the schedule config must be manually updated. The system should derive the epic list from the epic plan mapping automatically.

## What Changes

- **Auto-discover epics from plan**: When `epics = ["from_plan"]` in `[schedule]`, the scheduler reads all mapped epic keys from `[epic_plan].epics`
- **Default config**: `~/.tdt/epic-report-config.toml` ships with `[schedule].epics = ["from_plan"]` so scheduled runs auto-discover epics without manual edits
- **Read epic keys from spreadsheet**: The epic plan reader can parse the spreadsheet to discover all mapped epic keys (not just the TOML mapping)
- **Fallback behavior**: If `[epic_plan]` is disabled, `from_plan` falls back to an empty list (no epics analyzed)
- **Override flag**: `--epics` CLI flag can override the auto-discovered list
- **Spreadsheet verification**: After running with `from_plan`, the spreadsheet output contains all mapped epics across Epic Overview, detail tabs, Delivery Plan Analysis, and Risks tabs

### Config Examples

```toml
# Auto-discover from epic plan (DEFAULT — ships with this)
[schedule]
epics = ["from_plan"]
enabled = true
cron = "0 7 * * *"

# Explicit override (opt-in)
[schedule]
epics = ["RMD-4160", "TJ-1656"]
enabled = true
cron = "0 7 * * *"
```

## Capabilities

### Modified Capabilities

- `scheduled-epic-report`: Schedule config now supports `"from_plan"` as a special value for `epics` field; default config uses `from_plan`
- `epic-plan-extraction`: Reader can extract all mapped epic keys from the spreadsheet

### Verification Capabilities

- `spreadsheet-output-verification`: After a `from_plan` run, the spreadsheet contains every mapped epic in Epic Overview, detail tabs, Delivery Plan Analysis, and Risks tabs — zero epics missing

## Impact

- **Code:** `epic_report/config.py` (ScheduleConfig), `epic_report/cli.py` (scheduled-run), `epic_report/epic_plan_reader.py`
- **Config:** `~/.tdt/epic-report-config.toml` — `epics` field defaults to `"from_plan"`
- **Backward compatible:** Existing hardcoded epic lists continue to work
