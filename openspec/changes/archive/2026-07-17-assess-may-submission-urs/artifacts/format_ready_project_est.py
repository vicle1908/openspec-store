"""Apply matching color + border formatting to the 7 new project sections in
the Ready_Project_Est tab, matching the style of the existing 4 projects.

Format pattern (extracted from existing rows 3-16):
  - Project title row (col B): bold size 15, white text on dark green bg, SOLID borders
  - Column header row (col B-F): size 11, dark text on light gray bg, SOLID borders
  - Column header row (col G — Use AI): BOLD, medium gray bg, SOLID borders
  - Data rows (col B-F): size 11, dark text on white, SOLID borders
  - Data rows (col G): size 10, on white, SOLID borders
  - Total row (col B): bold size 11, SOLID borders
  - Total row (col F-G): bold, ORANGE bg, SOLID borders
"""
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

SPREADSHEET_ID = "1_MIasMUIaDwauGsmSIQPiC7allQLDOxm9aW_t5a2vbk"
TAB = "Ready_Project_Est"
CREDS_PATH = "/Users/lekhanhvinh/.tdt/philip-project-1-496009-aecd4c291640.json"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# Color palette extracted from existing 4 projects in the sheet
COLOR_DARK_GREEN = {"red": 0.15294118, "green": 0.30588236, "blue": 0.07450981}
COLOR_LIGHT_GRAY = {"red": 0.9411765, "green": 0.94509804, "blue": 0.9490196}
COLOR_MED_GRAY = {"red": 0.8509804, "green": 0.8509804, "blue": 0.8509804}
COLOR_ORANGE = {"red": 1.0, "green": 0.6, "blue": 0.0}
COLOR_DARK_TEXT = {"red": 0.16078432, "green": 0.16470589, "blue": 0.18039216}
COLOR_WHITE = {"red": 1.0, "green": 1.0, "blue": 1.0}
BORDER_COLOR = {"red": 0, "green": 0, "blue": 0}


def build_border():
    return {"style": "SOLID", "width": 1, "color": BORDER_COLOR}


def borders_full():
    b = build_border()
    return {"top": b, "bottom": b, "left": b, "right": b}


def format_title_row(sheet_id, row_idx):
    return [{
        "repeatCell": {
            "range": {"sheetId": sheet_id, "startRowIndex": row_idx, "endRowIndex": row_idx + 1,
                      "startColumnIndex": 1, "endColumnIndex": 2},
            "cell": {
                "userEnteredFormat": {
                    "backgroundColor": COLOR_DARK_GREEN,
                    "textFormat": {"bold": True, "fontSize": 15, "foregroundColor": COLOR_WHITE},
                    "horizontalAlignment": "LEFT",
                    "verticalAlignment": "MIDDLE",
                    "borders": borders_full(),
                }
            },
            "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment,verticalAlignment,borders)",
        }
    }]


def format_header_row(sheet_id, row_idx):
    return [
        {
            "repeatCell": {
                "range": {"sheetId": sheet_id, "startRowIndex": row_idx, "endRowIndex": row_idx + 1,
                          "startColumnIndex": 1, "endColumnIndex": 6},
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": COLOR_LIGHT_GRAY,
                        "textFormat": {"bold": False, "fontSize": 11, "foregroundColor": COLOR_DARK_TEXT},
                        "horizontalAlignment": "CENTER",
                        "verticalAlignment": "MIDDLE",
                        "borders": borders_full(),
                    }
                },
                "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment,verticalAlignment,borders)",
            }
        },
        {
            "repeatCell": {
                "range": {"sheetId": sheet_id, "startRowIndex": row_idx, "endRowIndex": row_idx + 1,
                          "startColumnIndex": 6, "endColumnIndex": 7},
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": COLOR_MED_GRAY,
                        "textFormat": {"bold": True, "fontSize": 11, "foregroundColor": COLOR_DARK_TEXT},
                        "horizontalAlignment": "CENTER",
                        "verticalAlignment": "MIDDLE",
                        "borders": borders_full(),
                    }
                },
                "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment,verticalAlignment,borders)",
            }
        },
    ]


def format_data_row(sheet_id, row_idx):
    return [
        {
            "repeatCell": {
                "range": {"sheetId": sheet_id, "startRowIndex": row_idx, "endRowIndex": row_idx + 1,
                          "startColumnIndex": 1, "endColumnIndex": 6},
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": COLOR_WHITE,
                        "textFormat": {"bold": False, "fontSize": 11, "foregroundColor": COLOR_DARK_TEXT},
                        "horizontalAlignment": "LEFT",
                        "verticalAlignment": "MIDDLE",
                        "borders": borders_full(),
                    }
                },
                "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment,verticalAlignment,borders)",
            }
        },
        {
            "repeatCell": {
                "range": {"sheetId": sheet_id, "startRowIndex": row_idx, "endRowIndex": row_idx + 1,
                          "startColumnIndex": 6, "endColumnIndex": 7},
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": COLOR_WHITE,
                        "textFormat": {"bold": False, "fontSize": 10, "foregroundColor": COLOR_DARK_TEXT},
                        "horizontalAlignment": "CENTER",
                        "verticalAlignment": "MIDDLE",
                        "borders": borders_full(),
                    }
                },
                "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment,verticalAlignment,borders)",
            }
        },
    ]


def format_total_row(sheet_id, row_idx):
    return [
        {
            "repeatCell": {
                "range": {"sheetId": sheet_id, "startRowIndex": row_idx, "endRowIndex": row_idx + 1,
                          "startColumnIndex": 1, "endColumnIndex": 2},
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": COLOR_WHITE,
                        "textFormat": {"bold": True, "fontSize": 11, "foregroundColor": COLOR_DARK_TEXT},
                        "horizontalAlignment": "LEFT",
                        "verticalAlignment": "MIDDLE",
                        "borders": borders_full(),
                    }
                },
                "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment,verticalAlignment,borders)",
            }
        },
        {
            "repeatCell": {
                "range": {"sheetId": sheet_id, "startRowIndex": row_idx, "endRowIndex": row_idx + 1,
                          "startColumnIndex": 2, "endColumnIndex": 5},
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": COLOR_WHITE,
                        "borders": borders_full(),
                    }
                },
                "fields": "userEnteredFormat(backgroundColor,borders)",
            }
        },
        {
            "repeatCell": {
                "range": {"sheetId": sheet_id, "startRowIndex": row_idx, "endRowIndex": row_idx + 1,
                          "startColumnIndex": 5, "endColumnIndex": 6},
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": COLOR_ORANGE,
                        "textFormat": {"bold": True, "fontSize": 11, "foregroundColor": COLOR_DARK_TEXT},
                        "horizontalAlignment": "CENTER",
                        "verticalAlignment": "MIDDLE",
                        "borders": borders_full(),
                    }
                },
                "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment,verticalAlignment,borders)",
            }
        },
        {
            "repeatCell": {
                "range": {"sheetId": sheet_id, "startRowIndex": row_idx, "endRowIndex": row_idx + 1,
                          "startColumnIndex": 6, "endColumnIndex": 7},
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": COLOR_ORANGE,
                        "textFormat": {"bold": True, "fontSize": 11, "foregroundColor": COLOR_DARK_TEXT},
                        "horizontalAlignment": "CENTER",
                        "verticalAlignment": "MIDDLE",
                        "borders": borders_full(),
                    }
                },
                "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment,verticalAlignment,borders)",
            }
        },
    ]


def main():
    creds = Credentials.from_service_account_file(CREDS_PATH, scopes=SCOPES)
    service = build("sheets", "v4", credentials=creds)

    meta = service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
    sheet_id = None
    for s in meta["sheets"]:
        if s["properties"]["title"] == TAB:
            sheet_id = s["properties"]["sheetId"]
            break
    if sheet_id is None:
        raise RuntimeError(f"Tab {TAB!r} not found")

    # Section boundaries (from the appended data, 0-indexed rows in the spreadsheet):
    # Row 93 = last existing Total row (Smart Portfolio)
    # Row 97 = Gami - Amalgamated Trade title
    # Row 113 = Gami - Amalgamated Total
    # Row 116 = Gami - Cash Coupon title (3 rows after Amalgamated Total: blank, blank, title)
    # Row 130 = Gami - Cash Coupon Total
    # Row 133 = Refer A Friend title
    # Row 145 = Refer A Friend Total
    # Row 148 = UT Enhancements title
    # Row 158 = UT Enhancements Total
    # Row 161 = WM Accredited Investor title
    # Row 174 = WM Accredited Investor Total
    # Row 177 = DDA Linking title
    # Row 194 = DDA Linking Total
    # Row 197 = Shareholder Meeting title
    # Row 212 = Shareholder Meeting Total
    sections = [
        (97, 113),
        (116, 130),
        (133, 145),
        (148, 158),
        (161, 174),
        (177, 194),
        (197, 212),
    ]

    requests = []
    for title_row, total_row in sections:
        # Title row (1-based)
        requests.extend(format_title_row(sheet_id, title_row - 1))
        # Header row (title_row + 1)
        requests.extend(format_header_row(sheet_id, title_row))
        # Data rows (title_row + 2 ... total_row - 1)
        for data_row in range(title_row + 2, total_row):
            requests.extend(format_data_row(sheet_id, data_row - 1))
        # Total row
        requests.extend(format_total_row(sheet_id, total_row - 1))

    print(f"Applying {len(requests)} formatting requests to 7 new sections...")
    # Batch in chunks of 100
    for i in range(0, len(requests), 100):
        chunk = requests[i:i + 100]
        service.spreadsheets().batchUpdate(
            spreadsheetId=SPREADSHEET_ID, body={"requests": chunk}
        ).execute()
    print("Done.")


if __name__ == "__main__":
    main()
