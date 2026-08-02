## Context

The epic-report system uses hardcoded epic keys in `[schedule].epics`. The `from_plan` feature provides an optional auto-discovery mode.

**Current data flow (default mode):**
```
config.py: AppConfig.from_env()
  → schedule.epics = ["TJ-1635", "AU-348", "TJ-1773", "TJ-1960", "RMD-4160"]  # hardcoded
  → epic_plan.epics[key] = EpicPlanMapping(...)    # plan mapping

cli.py: scheduled_run()
  → config.schedule.epics  # reads hardcoded list
  → generate(*schedule.epics, ...)
```

**Optional from_plan mode:**
```
config.py: AppConfig.from_env()
  → if raw_epics == ["from_plan"]:
      → schedule.epics = list(epic_plan.epics.keys())  # auto-discover
  → else: schedule.epics = [str(e) for e in raw_epics]  # hardcoded list

cli.py: scheduled_run(--epics=override)
  → if override: epics = override
  → elif schedule.epics == ["from_plan"]:
      → epics = list(config.epic_plan.epics.keys())
  → else: epics = schedule.epics
  → generate(*epics, ...)
```

## Goals / Non-Goals

**Goals:**
- Support hardcoded epic keys as the default operational mode
- Support `"from_plan"` as optional auto-discovery mode
- Fallback to empty list when epic plan is disabled
- CLI `--epics` flag provides manual override
- Cross-project epic support (TJ, AU, RMD)

**Non-Goals:**
- Parse epic keys directly from the spreadsheet (future enhancement)
- Change the epic plan mapping structure
- Modify the analysis pipeline

## Decisions

### D1: Config field format

**Decision:** `[schedule].epics` accepts either:
- `["TJ-1635", "AU-348", "TJ-1773", "TJ-1960", "RMD-4160"]` — explicit list (default)
- `["from_plan"]` — auto-discover from epic_plan mapping (optional)

**Rationale:** Hardcoded keys give operators full control over which epics are analyzed. `from_plan` is available for teams that prefer auto-discovery.

### D2: Discovery logic (validated)

**Decision:** Resolution happens in `AppConfig.from_env()` so downstream code receives a resolved list.

**Implementation:**
```python
# In config.py, after loading schedule_section:
raw_epics = schedule_section.get("epics", [])
if isinstance(raw_epics, list):
    if raw_epics == ["from_plan"]:
        # Resolve from epic_plan keys
        if epic_plan.enabled and epic_plan.epics:
            schedule.epics = list(epic_plan.epics.keys())
        else:
            schedule.epics = []
            logger.warning("from_plan requested but epic_plan disabled/empty")
    else:
        schedule.epics = [str(e) for e in raw_epics]
```

### D3: Fallback when epic_plan disabled

**Decision:** If `[epic_plan].enabled = false`, `from_plan` returns empty list.

**Rationale:** Safe default — no epics analyzed rather than error.

### D4: CLI override

**Decision:** `--epics` flag on `scheduled-run` subcommand overrides the config value.

```bash
epic-report scheduled-run --epics TJ-1635,AU-348,TJ-1773,TJ-1960,RMD-4160
```

### D5: Spreadsheet verification contract

**Decision:** After a run, the spreadsheet output MUST contain all configured epics across every relevant tab:
- **Epic Overview**: one row per epic (key, project, status, risk, tasks, completion)
- **Detail tab per epic**: e.g. `RMD-4160 DLC Visibility` with task-level breakdown
- **Delivery Plan Analysis**: plan-state alignment per epic
- **Risks**: all identified risks per epic

**Rationale:** Ensures no epic is silently dropped. The spreadsheet is the operator-facing artifact — completeness here is the correctness signal.

## Impact Analysis

| File | Change | Risk |
|------|--------|------|
| `config.py:390-392` | Add `from_plan` resolution in `AppConfig.from_env()` | Low — additive |
| `config.py:464` | Update validation to skip when `from_plan` | Low — additive |
| `cli.py:1454` | Add `--epics` flag parameter | Low — additive |
| `cli.py:1494` | Add `--epics` override logic | Low — additive |

**Files NOT modified:** epic_plan_reader.py, collector.py, reporters/

## Risks / Trade-offs

| Risk | Mitigation |
|------|-----------|
| Empty epic list from from_plan | Log warning, exit cleanly |
| Epic plan has no mapped epics | Same as above |
| Config has both from_plan and explicit | Explicit wins (override) |
