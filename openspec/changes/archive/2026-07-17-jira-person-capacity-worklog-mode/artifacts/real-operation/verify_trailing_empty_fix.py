"""Verify the trailing-empty fix by calling build_person_sheet_rows + writing to scratch."""
import sys
sys.path.insert(0, "/Users/lekhanhvinh/Developer/tdt/jira-daily-reports/src")

from datetime import date
from datetime import datetime
from unittest.mock import MagicMock, patch
from tdt_core.env import load_tdt_env
load_tdt_env()

from jira_daily_reports.reports.sprint_report_sheet import SprintReportSheetReport
from tdt_sheets import SheetsClient
from tdt_sheets.auth import ServiceAccountAuth

auth = ServiceAccountAuth.from_env(
    scopes=[
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ],
)
sheets = SheetsClient(auth=auth, backend="sdk")
SPREADSHEET_ID = "1pqFsRRLQ9OsCOf9siuZwJ--azT4s2qdO4hpXH954usg"
TEST_SHEET = "scratch_fix_verify"

sheets.ensure_sheet(SPREADSHEET_ID, TEST_SHEET)
sheets.clear(SPREADSHEET_ID, f"'{TEST_SHEET}'!A1:Z10")

# Build a sparse active row (only 1 of 12 days has worklog)
jira = MagicMock()
report = SprintReportSheetReport.__new__(SprintReportSheetReport)
report.person_sheet_name = TEST_SHEET
report.person_sheet_title = "Person Capacity"
report.person_timezone = "Asia/Ho_Chi_Minh"

# Mimic the _build_person_capacity result with sparse daily_seconds
result = MagicMock()
result.generated_at = datetime(2026, 6, 15, 12, 0)
result.summary = {
    "person_capacity": {
        "window": {"start": "2026-06-08", "end": "2026-06-19"},
        "summary": {"people": 1, "worked_tickets": 1, "logged_total_seconds": 3600},
        "date_keys": [f"2026-06-{d:02d}" for d in range(8, 20)],
        "date_labels": [f"{d} Jun" for d in range(8, 20)],
        "active_rows": [
            {
                "no": 1,
                "person": "Alice",
                "account_id": "acc-1",
                "role": "",  # empty
                "worked_tickets": 1,
                "logged_total": "1h",
                "worked_ticket_links": "",  # empty
                "daily_ticket_details": "",  # empty
                "daily_seconds": {"2026-06-10": 3600},  # only 1 day
            },
        ],
        "inactive_rows": [],
        "reconciliation": {
            "roster_row_missing_display_name": [],
            "roster_row_duplicate_member_key": [],
            "roster_display_name_collision": [],
            "jira_display_name_collision": [],
            "unmapped_worklog_authors": [],
            "roster_without_worklogs": [],
        },
    }
}

rows = report.build_person_sheet_rows(result)
print(f"rows: {len(rows)}")
for i, row in enumerate(rows):
    if any(c for c in row):
        print(f"  [{i:3d}] len={len(row):2d}: {row[:5]}...{row[-3:]}")

# Write the actual rows
sheets.write(SPREADSHEET_ID, f"'{TEST_SHEET}'", rows, input_option="USER_ENTERED")
data = sheets.read(SPREADSHEET_ID, f"'{TEST_SHEET}'!A1:T10")
out = data.values if hasattr(data, "values") else data
print(f"\nafter write + read, max col: {max(len(r) for r in out)}")
for i, row in enumerate(out):
    if any(c for c in row):
        print(f"  [{i:3d}] len={len(row):2d}: {row[:5]}...{row[-3:]}")

# Clean up
md = sheets.get_metadata(SPREADSHEET_ID)
sheet = md.get_sheet_by_name(TEST_SHEET)
if sheet:
    sheets._backend._get_sheets_service().spreadsheets().batchUpdate(
        spreadsheetId=SPREADSHEET_ID,
        body={"requests": [{"deleteSheet": {"sheetId": sheet.sheet_id}}]},
    ).execute()
    print("cleaned")
