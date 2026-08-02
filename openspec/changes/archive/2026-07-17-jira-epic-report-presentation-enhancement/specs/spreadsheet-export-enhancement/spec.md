# Spreadsheet Export Enhancement — Specification

**Capability:** spreadsheet-export-enhancement
**Status:** Implemented
**Date:** 2026-06-02 (updated 2026-06-03)
**Version:** 1.3 (added subtask filtering option)

---

## Context

The `epic_report/reporters/spreadsheet_reporter.py` generates Google Sheets via direct Google Sheets API (Python SDK) with multiple tabs: Executive Summary, Epic Overview, per-epic tabs, Risks, Project Bugs. This enhancement adds:

1. Service account authentication for headless Google Sheets access
2. Blocking dependency context to existing tabs
3. New "Blocking Dependencies" tab with root blockers, blocked items, and dependency chains
4. Sprint report presentation with blocking context (target vs actual + health tier)
5. Person capacity presentation with blocking impact per person

**Implementation Note:** Uses direct Google Sheets Python SDK (`google-api-python-client`) for headless access. Configuration uses `~/.tdt/.env` and `~/.tdt/epic-report-config.toml`.

---

## Configuration

### Environment Variables (from `~/.tdt/.env`)

| Variable | Description | Source |
|----------|-------------|--------|
| `SPREADSHEET_ID` | Primary sprint spreadsheet ID | Sprint 15: `1ZB_CE4xQMOrBbDPe2jxRniMh8adFYC5-EQ4eqSd1ok8` |
| `SPRINT_14_SPREADSHEET_ID` | Sprint 14 spreadsheet | `1WQE0DOPVgRVdBraMVJWO9BfuPtwwmQD6aCziVMLliSA` |
| `GOOGLE_APPLICATION_CREDENTIALS` | Service account JSON path | `~/.tdt/google-service-account.json` |

### App Config (`~/.tdt/epic-report-config.toml`)

```toml
[output]
spreadsheet_url = "https://docs.google.com/spreadsheets/d/1ZB_CE4xQMOrBbDPe2jxRniMh8adFYC5-EQ4eqSd1ok8/edit?gid=508115400#gid=508115400"
include_subtasks = false  # Set to true to include subtasks, false for stories/tasks only
```

### Subtask Filtering

The `include_subtasks` config option controls whether subtasks are included in the spreadsheet:

| Value | Behavior |
|-------|----------|
| `true` | Include all items: Stories, Tasks, Subtasks, Bugs |
| `false` | Include only Stories, Tasks, and Bugs (exclude Subtasks) |

When `include_subtasks = false`:
- Per-epic tabs show only Stories and Tasks
- Epic Overview task counts reflect filtered items
- Blocking analysis excludes subtasks
- Executive Summary metrics are based on filtered items

### URL Parsing

The `spreadsheet_url` field supports full Google Sheets URLs:
- Format: `https://docs.google.com/spreadsheets/d/{ID}/edit?gid={GID}#gid={GID}`
- `ID` is extracted and used as `spreadsheet_id`
- `GID` (sheet ID) is used to identify the target sheet tab

---

## ADDED Requirements

### Requirement: Add blocking context columns to existing sheets

The system SHALL add blocking dependency columns to existing spreadsheet tabs where relevant.

#### Scenario: Epic Overview sheet gets blocking columns

- **WHEN** rendering Epic Overview tab
- **THEN** add columns: "Root Blockers" (count), "Blocked Items" (count), "Avg Impact Radius"

#### Scenario: Per-epic tabs get blocking columns

- **WHEN** rendering per-epic tabs
- **THEN** add columns to task table: "Blocked By" (comma-separated keys), "Blocks" (count), "Chain Depth", "Impact Radius"

#### Scenario: Risks sheet gets blocking context

- **WHEN** rendering Risks tab
- **THEN** add column: "Is Root Blocker" (Yes/No) for risks of type BLOCKED_TASK

### Requirement: Add new "Blocking Dependencies" sheet

The system SHALL create a new dedicated sheet for blocking dependency analysis.

#### Scenario: Blocking Dependencies sheet structure

- **WHEN** generating spreadsheet with blocking data
- **THEN** create new tab named "Blocking Dependencies" with sections:
  1. Root Blockers table (Key, Type, Status, Assignee, Blocks Count, Impact Radius, Priority)
  2. Blocked Items table (Key, Type, Status, Assignee, Blocked By, Chain Depth, Root Blocker)
  3. Dependency Chains (ASCII tree rendering in text cells)

#### Scenario: Root Blockers sorted by impact

- **WHEN** rendering Root Blockers section
- **THEN** sort by Impact Radius descending (highest impact first)

#### Scenario: Blocked Items sorted by chain depth

- **WHEN** rendering Blocked Items section
- **THEN** sort by Chain Depth ascending (shallowest first, easier to unblock)

### Requirement: Add blocking metrics to Executive Summary sheet

The system SHALL add blocking dependency metrics to the Executive Summary tab.

#### Scenario: Summary includes blocking stats

- **WHEN** rendering Executive Summary tab
- **THEN** add metrics: Total Root Blockers, Total Blocked Items, % Sprint Blocked, Avg Impact Radius, Highest Impact Blocker

#### Scenario: Health tier includes blocking risk

- **WHEN** calculating sprint health tier
- **THEN** factor in: blocked item count, root blocker count, avg impact radius

#### Scenario: Health tier display

- **WHEN** rendering health tier in summary
- **THEN** show: tier emoji + tier name + blocking metrics (e.g., "🟡 AT RISK — 25% blocked, 2 root blockers")

### Requirement: Add service account authentication using official Google Sheets Python quickstart pattern

The system SHALL use the canonical `tdt-sheets` service-account authentication path for headless Sheets access. Value reads, writes, and clears MUST use public `tdt-sheets` operations. Drive and formatting operations MAY use the authenticated Google API service exposed by the same client until equivalent public primitives exist. The epic-report path MUST NOT depend on the `gws` CLI.

#### Scenario: Service account credentials loading (quickstart style)

- **WHEN** generating a spreadsheet
- **THEN** the system SHALL construct the supported `tdt-sheets` client with Sheets and Drive scopes
- **AND** credential loading and refresh SHALL follow the shared `TDT_HOME` service-account contract

#### Scenario: Path resolution (consistent ecosystem convention)

- **WHEN** `GOOGLE_SERVICE_ACCOUNT_PATH` env var is set
- **THEN** use it
- **WHEN** `GOOGLE_APPLICATION_CREDENTIALS` (standard Google) is set and no explicit
- **THEN** use it (for broader compatibility with gws-shared docs etc.)
- **WHEN** neither
- **THEN** default to `~/.tdt/google-service-account.json`

#### Scenario: Credentials caching and refresh

- **WHEN** creds loaded
- **THEN** cache the Credentials object keyed by path
- **AND** on subsequent calls, if near expiry, refresh (60s buffer)
- **AND** reuse for service builds

#### Scenario: Sheets and Drive service build (quickstart)

- **WHEN** creds available
- **THEN** `build("sheets", "v4", credentials=creds, cache_discovery=False)` for sheets
- **AND** similar `build("drive", "v3", ...)` for drive (used for folder moves)
- **AND** cache the service objects

#### Scenario: Service account missing/invalid

- **WHEN** no valid service-account credential is available
- **THEN** the spreadsheet output operation SHALL fail with an actionable authentication error
- **AND** it MUST NOT report a successful or partially successful managed output

#### Scenario: Explicit override / no mint for gws here

- Note: this feature uses direct API client (not token mint for gws subprocess). Other ecosystem parts (daily-reports) mint token str and inject GOOGLE_WORKSPACE_CLI_TOKEN for gws CLI. Both use equivalent SA file + scopes + tdt env load + cache + default path logic for consistency.

### Requirement: Use Google Sheets/Drive API client (v4/v3) for sheet operations (quickstart)

The system SHALL perform value update and clear operations through public `tdt-sheets` APIs. It MAY use the authenticated Google API service from the same client for spreadsheet creation, Drive movement, structural batch updates, and formatting until those operations have public `tdt-sheets` equivalents. Managed operation failures SHALL propagate.

#### Scenario: Sheet creation uses API client

- **WHEN** creating new spreadsheet with blocking tabs
- **THEN** use `_create_spreadsheet()` which does service.spreadsheets().create(body=...)

#### Scenario: Sheet updates use API client

- **WHEN** writing blocking data / metrics / trees
- **THEN** use `_update_sheet()` which does service.spreadsheets().values().update(..., valueInputOption="USER_ENTERED")

#### Scenario: Drive folder move (for org)

- **WHEN** spreadsheet created, move to default folder
- **THEN** use `_move_to_folder()` via drive service.files().update(addParents=...)

#### Scenario: Formatting via API

- **WHEN** applying conditional / header styles for blocking
- **THEN** use `_apply_formatting()` via service.spreadsheets().batchUpdate(requests=...) or get+update

This aligns with official quickstart and keeps the implementation independent of gws binary (while daily-reports/jira skills continue using gws CLI where appropriate). Specs/docs updated for the direct SA+client solution applied here.

### Requirement: Preserve existing sheet structure

The system SHALL NOT modify existing sheet tabs or remove existing functionality.

#### Scenario: Existing tabs unchanged

- **WHEN** generating enhanced spreadsheet
- **THEN** all existing tabs (Executive Summary, Epic Overview, per-epic, Risks, Project Bugs) remain with same structure

#### Scenario: New tabs are additive

- **WHEN** comparing v2.1 and v2.2 spreadsheet exports
- **THEN** v2.2 has all v2.1 tabs plus new "Blocking Dependencies" tab

#### Scenario: Backward compatibility for consumers

- **WHEN** external tool reads existing tabs
- **THEN** tab names and column order unchanged for existing columns

### Requirement: Add conditional formatting for blocking status

The system SHALL apply conditional formatting to highlight blocking relationships.

#### Scenario: Root blocker rows highlighted

- **WHEN** rendering Root Blockers section
- **THEN** apply red background (#FFCCCC) to rows with Impact Radius >= 10

#### Scenario: Blocked item rows highlighted

- **WHEN** rendering Blocked Items section
- **THEN** apply yellow background (#FFFFCC) to rows with Chain Depth >= 2

#### Scenario: Ready items highlighted

- **WHEN** rendering Ready to Work section
- **THEN** apply green background (#CCFFCC) to rows with no blockers

### Requirement: Add HYPERLINK formulas for Jira keys

The system SHALL use HYPERLINK formulas for all Jira issue keys in blocking columns.

#### Scenario: Blocked By column has hyperlinks

- **WHEN** rendering Blocked By column
- **THEN** each key is a HYPERLINK formula: `=HYPERLINK("https://psplit.atlassian.net/browse/PDS-100", "PDS-100")`

#### Scenario: Root Blocker column has hyperlinks

- **WHEN** rendering Root Blocker column
- **THEN** key is a HYPERLINK formula to Jira browse URL

### Requirement: Handle empty blocking data gracefully

The system SHALL create blocking tabs even when no blocking relationships exist.

#### Scenario: No root blockers

- **WHEN** no items qualify as root blockers
- **THEN** Blocking Dependencies tab shows headers with message: "✅ No blocking dependencies detected"

#### Scenario: No blocked items

- **WHEN** no items have blockers
- **THEN** Blocked Items section shows: "✅ All items are unblocked and ready to work"

---

### Requirement: Support blocking data in Google Sheets formulas

The system SHALL embed Google Sheets formulas for automatic blocking metric calculations.

#### Scenario: % Blocked formula

- **WHEN** rendering blocking metrics
- **THEN** cell contains formula: `=IF(B2>0, A2/B2, 0)` where A2=Blocked Items, B2=Total Items

#### Scenario: Impact Radius sum

- **WHEN** rendering total impact
- **THEN** cell contains formula: `=SUM(D2:D100)` for Impact Radius column

#### Scenario: Root Blocker count

- **WHEN** rendering root blocker count
- **THEN** cell contains formula: `=COUNTIF(E2:E100, "Yes")` for Is Root Blocker column

### Requirement: Add blocking data to per-epic tabs

The system SHALL enhance per-epic tabs with blocking dependency context for each epic.

#### Scenario: Per-epic blocking summary

- **WHEN** rendering per-epic tab
- **THEN** add section showing: Root Blockers in this epic, Blocked Items in this epic, Total Impact Radius

#### Scenario: Cross-epic blocking chains

- **WHEN** item in epic A is blocked by item in epic B
- **THEN** show cross-epic reference: "Blocked by PDS-100 (Epic B)"

### Requirement: Add blocking filter views to sheets

The system SHALL create filter views for easy blocking data exploration.

#### Scenario: Filter by blocking status

- **WHEN** user opens Blocking Dependencies tab
- **THEN** filter view available: "Show root blockers only", "Show blocked items only", "Show ready items only"

#### Scenario: Filter by impact radius

- **WHEN** user applies filter
- **THEN** can filter by Impact Radius: >= 10 (high), 5-9 (medium), < 5 (low)

#### Scenario: Filter by assignee

- **WHEN** user applies filter
- **THEN** can filter by Assignee to see blocking impact per person

### Requirement: Add blocking data reconciliation

The system SHALL reconcile blocking data across sheets to ensure consistency.

#### Scenario: Root blocker count matches

- **WHEN** comparing Executive Summary and Blocking Dependencies tabs
- **THEN** Root Blockers count matches exactly

#### Scenario: Blocked item count matches

- **WHEN** comparing per-epic tabs and Blocking Dependencies tab
- **THEN** total blocked items across all epics equals Blocked Items count

#### Scenario: Impact radius consistency

- **WHEN** comparing sheets
- **THEN** Impact Radius values match across all tabs for same items

### Requirement: Add sprint report presentation with blocking context

The system SHALL enhance the sprint report section in the spreadsheet with blocking dependency context, including target vs actual comparison and health tier.

#### Scenario: Sprint report header includes blocking metrics

- **WHEN** rendering sprint report section in Executive Summary tab
- **THEN** include: Sprint Name, Date Range, Health Tier (with blocking risk), Completion %, Total Items, Root Blockers, Blocked Items, % Blocked

#### Scenario: Health tier calculation with blocking risk

- **WHEN** calculating sprint health tier
- **THEN** factor in: blocked item count, root blocker count, avg impact radius, % of sprint blocked

#### Scenario: Health tier thresholds

- **WHEN** blocked items <= 10% of sprint AND root blockers <= 1
- **THEN** Health Tier = "GREEN" with green background

- **WHEN** blocked items 10-30% of sprint OR root blockers 2-3
- **THEN** Health Tier = "YELLOW" with yellow background

- **WHEN** blocked items > 30% of sprint OR root blockers >= 4
- **THEN** Health Tier = "RED" with red background

#### Scenario: Target vs Actual comparison with blocking columns

- **WHEN** rendering sprint report section
- **THEN** add columns to target vs actual table: "Blocked By" (comma-separated keys), "Blocks" (count), "Impact Radius" (transitive blocked count)

#### Scenario: Root blockers highlighted in sprint report

- **WHEN** item is a root blocker (blocks others but not blocked itself)
- **THEN** row has red background and "ROOT BLOCKER" badge in Verdict column

#### Scenario: Sprint summary metrics with blocking

- **WHEN** rendering sprint summary
- **THEN** include: Total Items, Done, In Progress, Blocked, Root Blockers, Avg Impact Radius, % Sprint Blocked, Behind Target, Overdue

### Requirement: Add person capacity presentation with blocking impact

The system SHALL enhance the person capacity section in the spreadsheet with blocking dependency impact per person.

#### Scenario: Person capacity table includes blocking columns

- **WHEN** rendering person capacity section
- **THEN** add columns: "Blockers Owned" (count of root blockers owned by this person), "Items Blocked" (count of person's items that are blocked), "Blocked %" (percentage of person's items blocked), "Blocking Impact" (total impact radius of person's root blockers)

#### Scenario: Blockers Owned calculation

- **WHEN** person Alice owns PDS-100 (root blocker, blocks 12 items) and PDS-102 (root blocker, blocks 8 items)
- **THEN** "Blockers Owned" shows: "2" with red background

#### Scenario: Items Blocked calculation

- **WHEN** person Bob has 5 items, 3 are blocked by others' root blockers
- **THEN** "Items Blocked" shows: "3" with yellow background

#### Scenario: Blocked % calculation

- **WHEN** person Carol has 8 total items, 4 are blocked
- **THEN** "Blocked %" shows: "50%" with formula: `=IF(C2>0, D2/C2, 0)` where C2=Assigned Tickets, D2=Items Blocked

#### Scenario: Blocking Impact calculation

- **WHEN** person Alice owns root blockers with impact radii [12, 8]
- **THEN** "Blocking Impact" shows: "20" (sum of impact radii)

#### Scenario: Person capacity utilization with blocking adjustment

- **WHEN** person has 40h planned, 32h logged, but 12h spent on blocked items
- **THEN** "Effective Utilization" shows: "50%" ((32-12)/40) with formula: `=MIN(100%, IF(F2>0, (E2-G2)/F2, 0))` where E2=Logged Total, F2=Planned Estimate, G2=Blocked Time

#### Scenario: Utilization color coding

- **WHEN** effective utilization >= 90%
- **THEN** cell shows green background (well-utilized)

- **WHEN** effective utilization 70-89%
- **THEN** cell shows yellow background (under-utilized due to blocking)

- **WHEN** effective utilization < 70%
- **THEN** cell shows red background (significantly under-utilized)

#### Scenario: Person capacity action recommendations

- **WHEN** person owns root blockers with high impact
- **THEN** Action column shows: "Prioritize PDS-100 (blocks 12 items)" with red background

- **WHEN** person has >50% items blocked
- **THEN** Action column shows: "60% blocked - request alternative work" with yellow background

- **WHEN** person has 90%+ utilization and no blocking issues
- **THEN** Action column shows: "Well-utilized" with green background

#### Scenario: Person capacity team summary

- **WHEN** rendering person capacity section
- **THEN** include team summary row: Total Persons, Avg Utilization %, Total Blockers Owned, Total Items Blocked, Team Blocked %, Team Health

#### Scenario: Team health indicator

- **WHEN** team blocked % <= 20%
- **THEN** Team Health shows: "GREEN" with green background

- **WHEN** team blocked % 20-40%
- **THEN** Team Health shows: "YELLOW" with yellow background

- **WHEN** team blocked % > 40%
- **THEN** Team Health shows: "RED" with red background

#### Scenario: Person capacity role-based grouping

- **WHEN** rendering person capacity section
- **THEN** add "Role" column and support grouping by role (Dev, QA, PM, Design, etc.)

#### Scenario: Role-level summary

- **WHEN** user requests role-level view
- **THEN** show: Role, Persons, Avg Utilization %, Total Blockers, Total Blocked, Role Health
