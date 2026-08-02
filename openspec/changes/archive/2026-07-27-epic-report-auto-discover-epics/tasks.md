## 1. Config Changes (config.py)

- [x] 1.1 Update `ScheduleConfig` docstring (line 153-165) to document `"from_plan"` as valid value for `epics` field
- [x] 1.2 Update `AppConfig.from_env()` (line 390-392) to resolve `["from_plan"]` to epic plan keys:
  ```python
  if raw_epics == ["from_plan"]:
      if epic_plan.enabled and epic_plan.epics:
          schedule.epics = list(epic_plan.epics.keys())
      else:
          schedule.epics = []
          logger.warning("from_plan requested but epic_plan disabled/empty")
  else:
      schedule.epics = [str(e) for e in raw_epics]
  ```
- [x] 1.3 Update `AppConfig.validate()` (line 464) to skip validation when `schedule.epics` is empty but `from_plan` was requested

## 2. CLI Changes (cli.py)

- [x] 2.1 Add `--epics` parameter to `scheduled_run()` function (line 1454):
  ```python
  epic_override: Annotated[
      str | None,
      typer.Option("--epics", help="Comma-separated epic keys to analyze (overrides config)")
  ] = None,
  ```
- [x] 2.2 Add override logic after config loading (line ~1494):
  ```python
  if epic_override:
      schedule.epics = [k.strip() for k in epic_override.split(",")]
  ```
- [x] 2.3 Update help text to document `"from_plan"` option

## 3. Default Config

- [x] 3.1 Set `~/.tdt/epic-report-config.toml` `[schedule].epics` to `["TJ-1635", "AU-348", "TJ-1773", "TJ-1960", "RMD-4160"]`
- [x] 3.2 Verify `AppConfig.from_env()` resolves hardcoded keys correctly

## 4. Integration & Unit Tests

- [x] 4.1 Run `uv run ruff check epic_report/` — zero warnings
- [x] 4.2 Run `uv run pytest tests/ -q` — all tests pass
- [x] 4.3 Test with `epics = ["from_plan"]` in TOML — verify epic plan keys used
- [x] 4.4 Test with explicit `epics = ["RMD-4160"]` — verify backward compatibility
- [x] 4.5 Test with `--epics RMD-4160,TJ-1656` — verify CLI override

## 5. Operational Verification

- [x] 5.1 Run `epic-report scheduled-run` with hardcoded keys — verify command completes without error
- [x] 5.2 Read spreadsheet **Epic Overview** tab — verify 5 rows (TJ-1635, AU-348, TJ-1773, TJ-1960, RMD-4160)
- [x] 5.3 Read spreadsheet **detail tabs** — verify 5 tabs with task-level data
- [x] 5.4 Read spreadsheet **Delivery Plan Analysis** tab — verify 5 rows
- [x] 5.5 Read spreadsheet **Risks** tab — verify risks listed for each epic
- [x] 5.6 Clean up spreadsheet — remove old RMD tabs, keep only current 5 epic tabs
- [x] 5.7 Confirm all 5 configured epics present in spreadsheet output
