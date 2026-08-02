## Context

The `sprint-sheet` report computes a sprint health status (🟢 HEALTHY / 🟡 AT RISK / 🔴 CRITICAL) based on blocked ticket count and code review count. This status is:

1. **Stored in `result.summary["health"]`** - computed in `sprint_report_sheet.py:1121-1125`
2. **Rendered in CLI output** - via `format_markdown()` 
3. **NOT rendered in Google Sheet** - `build_sheet_rows()` never writes health to the Sprint Summary section

The SKILL.md documentation at lines 284-292 says health "apply to the sprint-sheet's consolidated person-capacity view" but this is inaccurate - health is computed from sprint-level status counts (`status_counts["Blocked"]` and `status_counts["Code Review"]`) and applies to the Sprint Report, not Person Capacity.

## Goals / Non-Goals

**Goals:**
- Render health status (🟢/🟡/🔴 + text) in the Sprint Summary section of the Sprint Report sheet
- Fix SKILL.md to correctly attribute health to Sprint Report
- Document the conditional sort behavior in SKILL.md

**Non-Goals:**
- Changing the health computation logic (thresholds, blocked/CR counts)
- Changing other Sprint Summary fields
- Modifying Person Capacity behavior
- Adding new health models or thresholds

## Decisions

### 1. Health Display Location

**Decision:** Add "Health" row to Sprint Summary section, after "Narrative" row.

**Rationale:**
- Sprint Summary is the logical place for health status
- Aligns with SKILL.md line 203: "Sprint Health Summary" 
- Minimal code change - just one more `rows.append()` call

**Alternative considered:** Add as a separate "Sprint Health Summary" block at top. Rejected because existing Sprint Summary section is the canonical place for aggregate metrics.

### 2. Health Row Format

**Decision:** Display as `["Sprint Health", health_status]` (e.g., `["Sprint Health", "🟢 HEALTHY"]`)

**Rationale:**
- Matches existing Sprint Summary row format
- Human-readable with emoji for quick visual scanning
- Status already computed in `s["health"]`

### 3. SKILL.md Fix

**Decision:** Change line 284 from:
> "Health thresholds apply to the sprint-sheet's consolidated person-capacity view"

To:
> "Health thresholds apply to the Sprint Report's sprint-wide metrics and are computed from blocked and code review status counts."

**Rationale:**
- Accurately describes where health is computed
- Distinguishes from standalone `sprint-health` report which counts issue states without verdicts

### 4. SKILL.md Sort Documentation

**Decision:** Add documentation about conditional sort behavior in Person Capacity section.

**Rationale:**
- Users should understand why row order may change between runs
- Planning availability is a key operational state that affects output

## Risks / Trade-offs

- **[Risk] Adding health row may shift existing row positions** → Mitigation: Health row added after "Narrative", before empty row separator. Existing data rows start at same relative positions.
- **[Risk] Health emoji may not render in all spreadsheet clients** → Mitigation: Status text is included alongside emoji (e.g., "🟢 HEALTHY") so text is readable even if emoji fails.

## Migration Plan

1. **Update `build_sheet_rows()` in `sprint_report_sheet.py`**
   - Add health row after narrative row
   - No changes to data model or computation logic

2. **Update SKILL.md**
   - Fix health attribution text
   - Add sort behavior documentation

3. **Update tests**
   - Add assertion that sheet rows contain health status
   - Verify health row position

4. **Verify in-session**
   - Run `sprint-sheet` and confirm health appears in sheet
   - Run unit tests

## Open Questions

None - the change is straightforward and well-understood.
