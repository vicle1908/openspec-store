## Why

The `sprint-sheet` report computes health status (HEALTHY/AT RISK/CRITICAL) based on blocked tickets and code review counts, but this status is not rendered in the Google Sheet output. The SKILL.md documentation incorrectly attributes health thresholds to the "person-capacity view" when they actually apply to the Sprint Report. Additionally, health models are inconsistent across reports (blocked-count-based vs days-based), and the conditional sort behavior in Person Capacity is undocumented.

## What Changes

1. **Add health status to Sprint Report sheet output** - Render HEALTHY/AT RISK/CRITICAL in the Sprint Summary section of the sheet
2. **Fix SKILL.md health attribution** - Correct documentation to state health applies to Sprint Report, not Person Capacity
3. **Document conditional sort behavior** - Clarify that sort order changes based on planning availability
4. **Document health model inconsistencies** - Add explicit documentation about different health models across reports (optional enhancement)

## Capabilities

### New Capabilities

- `sprint-sheet-health-display`: Display sprint health status (HEALTHY/AT RISK/CRITICAL) in the Sprint Report Google Sheet output alongside other Sprint Summary metrics

### Modified Capabilities

- (none - existing behavior is clarified but not changed at the spec level)

## Impact

**Affected code:**
- `jira-daily-reports/src/jira_daily_reports/reports/sprint_report_sheet.py` - `build_sheet_rows()` needs to render health in Sprint Summary section
- `jira-daily-reports/.agents/skills/jira-daily-reports/SKILL.md` - Health threshold documentation needs correction

**Documentation only:**
- No changes to spec contracts or data models
- No changes to API interfaces or behavior

**Testing:**
- Update unit tests to verify health is rendered in sheet output
