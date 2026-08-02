# Sprint Report Target/Verdict Analysis & Fix Plan

**Date:** 2026-05-27 17:25 UTC  
**Issue:** Target Status, Actual Status, Verdict columns not properly filled for all issues  
**Root Cause:** Bucket sheets not updated with Sprint 15 targets

---

## Current Behavior

### What Works ✅
- **Work Type column:** All 56 issues have work_type populated (Task/Epic/Story)
- **Actual Status:** All 56 issues have current Jira status
- **Verdict logic:** Correctly calculates ✅ Met / ❌ Behind / 🚫 Rejected / — No Target / ? Unknown

### What's Missing ⚠️
- **Target Status:** Only 5-6 issues have targets (carry-over from Sprint 14)
- **Verdict:** 50+ issues show "— No Target" (91% of sprint)

### Live Data (Filter 15235)
```
Total issues: 56
With targets: 5-6 (9-11%)
Without targets: 50-51 (89-91%)

Issues with targets (Sprint 14 carry-overs):
  RMD-2359: target=DONE, actual=Code Review, verdict=❌ Behind
  FUN-1859: target=DONE, actual=Code Review, verdict=❌ Behind
  STABI-1636: target=Done, actual=Code Review, verdict=❌ Behind
  TJ-1916: target=Done, actual=In Progress, verdict=❌ Behind
  STABI-1646: target=Done, actual=SIT, verdict=❌ Behind
  AM-1716: target=Done, actual=Draft, verdict=? (Draft not in STATUS_ORDER)

Issues without targets (Sprint 15 new scope):
  50+ issues: target=—, actual=<various>, verdict=— No Target
```

---

## Root Cause Analysis

### 1. Bucket Sheet Structure
```
Spreadsheet: 1ZB_CE4xQMOrBbDPe2jxRniMh8adFYC5-EQ4eqSd1ok8 (Sprint 15)
Expected tabs:
  - Buckets (Prod, Perf, Bug)
  - Bucket (New Feature)
  - Bucket (Crash)
  
Each bucket sheet should have:
  Column A: ID (issue key like AM-2026)
  Column X: Target Status (Done, In Progress, etc.)
```

### 2. Target Reading Logic
```python
# delivery/sheet.py:52
def read_bucket_targets(spreadsheet_id: str) -> dict[str, str]:
    """Read all bucket sheets and return {issue_key: target_status}."""
    # Reads from BUCKET_RANGES:
    #   - "Buckets (Prod, Perf, Bug)!A1:Z200"
    #   - "Bucket (New Feature)!A1:Z200"
    #   - "Bucket (Crash)!A1:Z200"
    
    # For each sheet:
    #   1. Find "ID" column (issue key)
    #   2. Find "Target Status" column
    #   3. Extract {key: target} pairs
    #   4. Filter: only valid target statuses (lowercase in VALID_TARGET_STATUSES)
```

### 3. Valid Target Statuses
```python
# sprint_report_sheet.py:56
VALID_TARGET_STATUSES = set(STATUS_ORDER.keys())
# = {"to do", "in progress", "code review", "deploy in dev", "deploy in prod", 
#    "sit", "test done", "done", "closed", "completed"}
```

### 4. Why Only 5-6 Matches?
```
Sprint 14 bucket sheets had 64 targets (AM-2026, AM-2066, etc.)
Sprint 15 filter 15235 has 56 issues (RMD-2359, FUN-1859, STABI-*, TJ-*, etc.)
Overlap: Only 5-6 issues (carry-overs still in active sprint)
```

---

## Problem Statement

**Expected:** All 56 Sprint 15 issues should have Target Status and Verdict  
**Actual:** Only 5-6 issues have targets (9-11%)  
**Reason:** Bucket sheets contain Sprint 14 data, not Sprint 15 scope

---

## Solution Options

### Option 1: Update Bucket Sheets (Recommended)
**Approach:** Populate bucket sheets with Sprint 15 targets manually or via script

**Pros:**
- Follows existing design
- Stakeholders control targets
- Historical tracking works

**Cons:**
- Manual work required each sprint
- Delay at sprint start

**Implementation:**
1. Export filter 15235 issues to CSV
2. Add "Target Status" column (e.g., all "Done" for sprint goal)
3. Import to bucket sheets
4. Re-run sprint-sheet command

### Option 2: Auto-Generate Targets from Sprint Goal
**Approach:** If no target in bucket sheet, default to sprint goal status (e.g., "Done")

**Pros:**
- Automatic, no manual work
- All issues get verdict immediately

**Cons:**
- Less granular (all same target)
- Loses per-issue target flexibility

**Implementation:**
```python
# sprint_report_sheet.py:run()
for issue in issues:
    key = issue["key"]
    target = self._targets.get(key, "")
    
    # NEW: Auto-generate target if missing
    if not target:
        target = os.getenv("DEFAULT_SPRINT_TARGET", "Done")  # or "Test Done", "SIT", etc.
    
    # Continue with verdict calculation...
```

### Option 3: Hybrid Approach (Best)
**Approach:** Use bucket sheet targets when available, fall back to default

**Pros:**
- Flexible: manual targets override default
- Automatic: new issues get default target
- Gradual: can add targets over sprint

**Cons:**
- Slightly more complex logic

**Implementation:**
```python
# sprint_report_sheet.py:run()
DEFAULT_TARGET = os.getenv("SPRINT_TARGET_STATUS", "Done")

for issue in issues:
    key = issue["key"]
    target = self._targets.get(key, "")
    
    # Hybrid: use bucket target if present, else default
    if not target:
        target = DEFAULT_TARGET
        target_source = "default"
    else:
        target_source = "bucket"
    
    # Calculate verdict with target
    verdict = self._calculate_verdict(target, actual_status)
    
    issue_data.append({
        "key": key,
        "target": target,
        "target_source": target_source,  # NEW: track source
        "actual": actual_status,
        "verdict": verdict,
        "work_type": itype,
        # ... rest of fields
    })
```

---

## Recommended Fix: Option 3 (Hybrid)

### Code Changes

**1. Add DEFAULT_TARGET env var**
```bash
# ~/.tdt/.env
SPRINT_TARGET_STATUS="Done"  # or "Test Done", "SIT", etc.
```

**2. Update sprint_report_sheet.py**
```python
# Line ~186 in run()
DEFAULT_TARGET = os.getenv("SPRINT_TARGET_STATUS", "Done")

for issue in issues:
    # ... existing code ...
    
    target = self._targets.get(key, "")
    target_source = "bucket"
    
    # NEW: Auto-generate target if missing
    if not target:
        target = DEFAULT_TARGET
        target_source = "default"
    
    # Calculate verdict (existing logic)
    verdict = "—"
    if not target:
        no_target_count += 1
    elif actual_status.lower() in ("rejected/duplicated", "rejected", "cancelled"):
        rejected_count += 1
        verdict = "🚫 Rejected"
    else:
        target_rank = _status_rank(target)
        actual_rank = _status_rank(actual_status)
        if target_rank < 0 or actual_rank < 0:
            no_target_count += 1
            verdict = "?"
        elif actual_rank >= target_rank:
            met_count += 1
            verdict = "✅ Met"
        else:
            behind_count += 1
            verdict = "❌ Behind"
    
    issue_data.append({
        "key": key,
        "summary": issue_summary,
        "target": target,
        "target_source": target_source,  # NEW
        "actual": actual_status,
        "verdict": verdict,
        "assignee": assignee,
        "work_type": itype,
        # ... rest
    })
```

**3. Update sheet output to show target source**
```python
# Line ~686 in build_sheet_rows()
rows.append([
    "Key",
    "Summary",
    "Target Status",
    "Target Source",  # NEW column
    "Actual Status",
    "Verdict",
    "Assignee",
    "Work Type",
    # ... rest
])

for item in sorted_data:
    rows.append([
        _hyperlink(f"{self.site}/browse/{key}", key),
        item["summary"],
        item["target"],
        item["target_source"],  # NEW
        item["actual"],
        item["verdict"],
        item["assignee"],
        item["work_type"],
        # ... rest
    ])
```

**4. Update spec.md**
```markdown
### Sprint Report Enrichment Requirements

3. **Sprint report SHALL include per-work-item target status.**
   - Target status from bucket sheet (manual planning)
   - Fallback to `SPRINT_TARGET_STATUS` env var (default: "Done")
   - Target source tracked: "bucket" or "default"
   - Verdict calculated: ✅ Met / ❌ Behind / 🚫 Rejected / ? Unknown
   - All issues MUST have target (no "— No Target" state)
```

---

## Expected Outcome After Fix

### Before (Current)
```
Total: 56 issues
With targets: 5-6 (9-11%)
Verdicts:
  ❌ Behind: 5
  ? Unknown: 1
  — No Target: 50
```

### After (Hybrid Fix)
```
Total: 56 issues
With targets: 56 (100%)
Verdicts:
  ✅ Met: 22 (Done status)
  ❌ Behind: 27 (not Done yet)
  🚫 Rejected: 6
  ? Unknown: 1 (Draft status)

Target sources:
  bucket: 5-6 (manual planning)
  default: 50 (auto-generated)
```

---

## Implementation Steps

1. **Add env var** to `~/.tdt/.env`:
   ```bash
   SPRINT_TARGET_STATUS="Done"
   ```

2. **Update code** in `sprint_report_sheet.py`:
   - Add DEFAULT_TARGET logic in `run()`
   - Add `target_source` field to `issue_data`
   - Update sheet header to include "Target Source"

3. **Update spec** in `spec.md`:
   - Add requirement for default target fallback
   - Document target source tracking

4. **Update tests** in `test_sprint_report_sheet.py`:
   - Test default target behavior
   - Test target_source field
   - Verify 100% target coverage

5. **Update docs**:
   - `SKILL.md`: Document `SPRINT_TARGET_STATUS` env var
   - `report-templates.md`: Update column list

6. **Run tests**:
   ```bash
   cd jira-daily-reports
   uv run pytest tests/test_sprint_report_sheet.py -v
   ```

7. **Generate report**:
   ```bash
   SPRINT_TARGET_STATUS="Done" ./bin/run sprint-sheet
   ```

8. **Verify output**:
   - All 56 issues have target
   - Verdict distribution makes sense
   - Target Source column shows "bucket" vs "default"

---

## Alternative: Quick Fix (No Code Change)

If code changes not desired, manually update bucket sheets:

```bash
# 1. Export Sprint 15 issues
cd jira-daily-reports
./bin/run sprint-sheet --output json --out-dir /tmp
jq -r '.summary.issue_data[] | [.key, .actual, "Done"] | @csv' /tmp/sprint-*.json > /tmp/sprint15-targets.csv

# 2. Import to Google Sheets
# Open: https://docs.google.com/spreadsheets/d/1ZB_CE4xQMOrBbDPe2jxRniMh8adFYC5-EQ4eqSd1ok8
# Tab: "Buckets (Prod, Perf, Bug)"
# Paste CSV data (ID, Current Status, Target Status)

# 3. Re-run report
./bin/run sprint-sheet
```

---

**Recommendation:** Implement Option 3 (Hybrid) for best balance of automation and flexibility.

**Next Step:** Anh muốn em implement Option 3 ngay không?
