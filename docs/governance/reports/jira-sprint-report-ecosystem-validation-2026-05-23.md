# Jira Sprint Report Ecosystem Validation — 2026-05-23

## Scope

Validate current Jira sprint-report findings against:

- Official Atlassian docs / API docs
- Current code in `jira-daily-reports/`
- Active skill docs
- Active OpenSpec reports
- Active presentation/docs

## External validation

### Atlassian docs

Validated via Context7 + official Atlassian sources:

- Jira Software Cloud reporting docs confirm a native **Sprint report** exists and is used for mid-sprint checks / retrospectives.
- Jira Software Cloud exposes native report surfaces beyond sprint report (dashboard/reporting ecosystem).
- Jira Software Cloud API docs expose **board**, **sprint**, **board issues**, and **board sprint issues** resources.
- No first-class sprint-report REST resource was found in the validated API excerpts; custom tools still need to aggregate sprint data from board/sprint/issue/JQL primitives.

## Local implementation validation

### Current operational implementation

`jira-daily-reports/` is the live implementation path:

- Python CLI
- `tdt-core`-backed auth/client creation
- `PatchedJira.jql()` for issue aggregation
- 16 commands total:
  - 9 core daily reports
  - `sprint-sheet`
  - `dashboard`
  - `cycle-time`
  - `wip-age`
  - `run-all`
  - `schedule`
  - `remind`

### Legacy / historical implementation

`openspec/changes/archive/jira-daily-reports-skill/` remains the canonical historical OpenSpec for the original bash/acli implementation:

- v1.1
- 9 report scripts
- cron/email/Slack delivery patterns
- filter-based scope (`filter = 15113`)

## Consistency issues found

### Fixed

1. **Broken/obsolete OpenSpec links in skill doc**
   - File: `.agents/skills/jira-daily-reports/SKILL.md`
   - Fix: point references to archived canonical path:
     - `openspec/changes/archive/jira-daily-reports-skill/spec.md`
     - `openspec/changes/archive/jira-daily-reports-skill/design.md`

2. **Stale presentation metadata**
   - File: `docs/presentation.html`
   - Fixes:
     - Board `#1061` → `#1067`
     - legacy report-count wording → current Python CLI / 16 commands
     - legacy acli-centric wording → current Python / dashboard / Sheets wording

3. **Broken legacy-path references in active OpenSpec review**
   - File: `openspec/reports/review-jira-daily-reports-overlap.md`
   - Fix: active references now point to `openspec/changes/archive/jira-daily-reports-skill/...`

4. **OpenSpec synthesis note**
   - File: `openspec/reports/spec-alignment-synthesis.md`
   - Fix: clarify that the referenced daily-reports skill is now archived, not active under the old path

### Still intentionally historical

Archive and historical docs still contain:

- “8 reports” (v1.0 historical only)
- board `#1061`
- old non-archive paths

These were **not mass-rewritten** because they are historical artifacts, not active source-of-truth docs.

## Consolidated understanding

### Native Jira

Best for:

- Scrum-native sprint review/retro views
- aggregate dashboards
- visual exploration

### Custom TDT reporting

Best for:

- automation
- alerting
- quality checks
- Google Sheets delivery
- target-vs-actual comparison
- stuck-work / cycle-time operational analysis

### Architecture

Current architecture is:

`Jira native reports` + `custom Python aggregation` + `delivery adapters (sheet/dashboard/json/markdown/terminal)`

Not:

`rebuild Jira sprint report from scratch as a single standalone artifact`

## Recommended source-of-truth split

- **Historical bash/acli spec:** `openspec/changes/archive/jira-daily-reports-skill/`
- **Current implementation:** `jira-daily-reports/`
- **Current ecosystem architecture:** `openspec/changes/jira-reports-consolidation/`
- **User-facing operational skill:** `.agents/skills/jira-daily-reports/SKILL.md`

## Result

After the fixes above, active skill/docs/spec references are materially more aligned with:

- current code
- current board ID
- archived OpenSpec location
- current Python-first implementation model
