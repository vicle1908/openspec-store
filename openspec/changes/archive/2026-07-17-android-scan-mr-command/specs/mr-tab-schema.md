# scan-mr Sheet Tab Schema

## Tab Naming

Tab name format: `MR-{slug}-{iid}`

Example: `MR-poems-team-poems-mobile3-android-23318`

Slug is derived from the project path (`git remote get-url origin`):
- `git@git.ecomedic.vn:poems-team/poems-mobile3-android.git` → `poems-team-poems-mobile3-android`

## MR-{slug}-{IID} Tab

Each `scan-mr` run writes findings to a tab named `MR-{slug}-{IID}`. Tab is created implicitly by `tdt-sheets.batch_write()` on first write.

### Column Schema

| # | Column Name | Type | Source | Notes |
|---|---|---|---|---|
| 1 | `Rule ID` | string | `Finding.rule_id` | E.g., `ANDROID-LIFECYCLE-001` |
| 2 | `Related Rules` | string | `Finding.related_rule_ids` | Comma-separated, empty if none |
| 3 | `Title` | string | `Finding.rule_title` or `Finding.message` | Human-readable rule title |
| 4 | `Priority` | string | `Finding.priority` | `P0`, `P1`, `P2`, `P3` |
| 5 | `Category` | string | `Finding.category` | E.g., `Memory`, `Security`, `Lifecycle` |
| 6 | `File Path` | string | `Finding.file_path` | **Workspace-relative path**, e.g., `app/src/main/java/com/tdt/pmobile3/trade/TradeViewModel.kt` |
| 7 | `Symbol` | string | `Finding.symbol` | Function/class name where finding was raised |
| 8 | `Issue` | string | `Finding.evidence` or `Finding.snippet` | The problematic code snippet |
| 9 | `Recommended Solution` | string | `Finding.recommended_solution` | Suggested fix |
| 10 | `Solution Review by Team Lead` | string | — | Empty on scan; filled manually |
| 11 | `Impact / Scope Testing` | string | `Finding.impact` | Assessment of fix scope |
| 12 | `Man Day` | string | — | Empty on scan; filled manually |
| 13 | `Status` | string | `Finding.status` | Default: `Open` |
| 14 | `Jira Ticket` | string | — | Empty on scan; filled manually |
| 15 | `Target Fix in Version` | string | — | Empty on scan; filled manually |
| 16 | `MR Context` | string | Diff snippet | **NEW** — changed lines from MR diff that surround the finding |

### `MR Context` Column Detail

The `MR Context` value for each finding is populated by finding the **diff hunk** from the MR that covers the file and line number of the finding.

**Population logic:**
1. `gitlab_mr.py` fetches `mr.changes()` which returns `{"changes": [{"diff": "...", "new_path": "...", "old_path": "..."}]}`
2. For each finding, match `finding.file_path` → corresponding diff entry
3. Extract the hunk header and the lines from the diff that correspond to the finding's `line` number
4. Write as plain text (truncated to 500 chars if > 10 lines)

**Example:**
```
@@ -42,6 +42,8 @@ class TradeViewModel {
  private val tradeRepository: TradeRepository
+ private val analytics: AnalyticsTracker
+ private val logger: Logger
  override fun onCreate() {
```

**If diff is unavailable:** column is left empty (not a fatal error).

### Tab naming

Findings are written to a tab named `MR-{slug}-{iid}`, e.g.:

```
MR-poems-team-poems-mobile3-android-23318
```

Slug is derived from the project path (`git remote get-url origin`). Same IID in different projects get different tabs — no collision.

### Summary row

The first data row (Row 2) of every `MR-{slug}-{iid}` tab is a summary row:

```
["MR Scan Summary", "Total: 12", "P0: 1", "P1: 3", "P2: 8", "", "", "", "", "", "", "", "", "", "", "", ""]
```

Columns 6–17 are empty in the summary row.

### Tab Header Row (Row 1)

Row 1 of every `MR-{IID}` tab:
```
[Rule ID, Related Rules, Title, Priority, Category, File Path, Symbol, Issue, Recommended Solution, Solution Review by Team Lead, Impact / Scope Testing, Man Day, Status, Jira Ticket, Target Fix in Version, MR Context]
```

### Sorting

Rows are sorted by:
1. `Priority` (P0 → P3)
2. `File Path` (alphabetical)
3. `line` number (ascending)
4. `Rule ID` (alphabetical)

### Empty Finding Set

If `scan-mr` finds no issues, the tab is still created/overwritten with only the header row. This is intentional — it signals that the scan ran and found nothing.

### Daily Scan Tabs (Unchanged)

Daily `scan` tabs (Auth, Home, Trade, etc.) are **not modified**. The `MR Context` column is present in those tabs but empty for all rows, preserving schema compatibility.
