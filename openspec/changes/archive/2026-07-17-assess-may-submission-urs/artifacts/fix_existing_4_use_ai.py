"""Fix Use AI values for the 4 existing projects (rows 3-93) on Ready_Project_Est tab.

Re-derives Use AI per row using the same 15-20% complexity tier heuristic as the 7 new projects.

Constraint: PRESERVE all Final Hours values (the team's estimates). Only fix Use AI math.
- Fixes PhillipGPT R20 outlier (Use AI=4 vs Final=0.3)
- Fills in PhillipGPT R21-R29 (currently empty)
- Fills in ReCaptcha P1 R57 Unit test (empty)
- Fills in ReCaptcha P2 R69 outlier (Use AI=2 vs Final=1.2) and R71 Unit test
- Fills in Smart Portfolio R92 (empty)
- Re-derives all per-row Use AI with 15-20% rule based on function complexity
- Re-derives Total Use AI cell to match the sum of per-row values
"""
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

SPREADSHEET_ID = "1_MIasMUIaDwauGsmSIQPiC7allQLDOxm9aW_t5a2vbk"
TAB = "Ready_Project_Est"
CREDS_PATH = "/Users/lekhanhvinh/.tdt/philip-project-1-496009-aecd4c291640.json"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


def ai_reduction_for(function: str) -> float:
    """Per-row AI reduction rate based on function complexity. Returns fraction (0.16-0.20).

    Same heuristic as the 7 new projects:
      - 0.20 (highest): cross-system integration, security, external APIs, integration
      - 0.18: state machines, voting, batch scheduling, exception
      - 0.16 (lowest): unit tests, simple UI, config, prompt UX, metadata cleanup
      - 0.17: default for standard business-logic work
    """
    fn = function.lower()
    if any(k in fn for k in [
        "integration", "external", "reconciliation", " api", " recaptcha", "sms defender",
        "security", "encrypt", "audit", "calculation",
        "refinitiv", " cis", "gbo", "dbs", " rps", "poems engine",
        "ifame", "iframe", "new chat", "chat history",
    ]):
        return 0.20
    if any(k in fn for k in [
        "state model", "state machine", "voting", "joint",
        "batch", "exception", "free shares", "72-hour", "72h",
        "session handoff", "session",
        "voting rules", "reconciliation policy",
        "failed login", "fail dialog", " sdk errors",
    ]):
        return 0.18
    if any(k in fn for k in [
        "unit test", " sit", " sit ", "cross-item integration",
        "configuration approach", "glossary", "metadata",
        "promote", "enable/disable", "campaign ownership",
        "acceptance criteria", "in-app prompt",
        "display handling", "remove template",
        "decompose", "problem statement", "target-state",
        "per-item current-state", "show ",
        " on/off", "flag for this feature",
        "save collapsed", "expand mode",
    ]):
        return 0.16
    return 0.17


def recompute_use_ai(final_2p: float, func: str) -> float:
    """Compute Use AI (2P) = Final 2P × (1 - reduction_rate), rounded to 2 decimals."""
    rate = ai_reduction_for(func)
    return round(final_2p * (1 - rate), 2)


# (project_name, title_row, total_row, [(row, function, final_value)])
PROJECTS = [
    ("Trade Ticket Lite", 3, 16, [
        (5,  "Create new header view without Counter Search / Vol / BVol / SVol", 2.65),
        (6,  "New Counter Quotes section only support current session time", 2.15),
        (7,  "Handle More Setting section include (Order Type, Payment Mode, Settlement Currency, Validity)", 2.15),
        (8,  "Handle Mandatory Section Inlcude (Order Type, Price, Quality)", 2.65),
        (9,  "Logic to save collapsed / expand mode for More Setting section", 1.05),
        (10, "Handle validate and submit logic", 2.65),
        (11, "Update new botttom sheet to show Order Type", 1.45),
        (12, "Handle logic to switch betweend Pro/Lite Mode", 3.15),
        (13, "Handle logic to switch save Pro/Lite Mode", 1.65),
        (14, "Do ON/OFF Flag for this feature", 2.65),
        (15, "SIT", 9.15),
    ]),
    ("PhillipGPT", 18, 33, [
        (20, "Update \"Ask AI\" button in Home Tab", 0.3),
        (21, "Update \"Ask AI\" button in WatchList Tab", 0.6),
        (22, "Update \"Ask AI\" button in Global Search", 0.3),
        (23, "Update \"Ask AI\" button in Counter Detail", 0.6),
        (24, "Update \"Ask AI\" button in Screener", 0.6),
        (25, "Update \"Ask AI\" button in Market", 0.6),
        (26, "Update \"Ask AI\" button in Trade Tab", 0.6),
        (27, "Update \"Ask AI\" button in Community Tab", 0.6),
        (28, "Update \"Ask AI\" button in Me Tab", 0.6),
        (29, "Update \"Ask AI\" button in Help", 0.6),
        (30, "Update PhillipGPT Screen (Back, New Chat, Chat History, Iframe)", 1.6),
        (31, "Do ON/OFF Flag for this feature", 1.8),
        (32, "SIT", 2.1),
    ]),
    ("ReCaptcha P1", 37, 58, [
        (40, "Integrate Google reCAPTCHA SDK", 3.5),
        (41, "Integrate SMS Defender SDK", 3.5),
        (42, "Login by Mobile + Verification Code SMS OTP", 2.2),
        (43, "Sign Up by Mobile -> SMS OTP", 1.2),
        (44, "Me tab -> Settings -> Change Mobile -> SMS OTP", 1.2),
        (45, "Sign Up by Email -> Email OTP", 1.2),
        (46, "Me tab -> Settings -> Change Email -> Email OTP", 1.2),
        (47, "Forgot Password -> Email OTP", 1.2),
        (48, "Forgot Password -> Mobile -> SMS OTP (RU)", 1.2),
        (49, "Me tab -> Settings -> Activate Login by Email -> Email OTP", 1.2),
        (50, "Me tab -> Settings -> Activate Login by Mobile -> SMS OTP", 1.2),
        (51, "Resend OTP All SMS OTP flows (RU)", 1.2),
        (52, "Resend OTP All Email OTP flows (RU)", 1.2),
        (53, "Email OTP: FAIL dialog", 1.2),
        (54, "SMS OTP: FAIL dialog", 1.2),
        (55, "Other SDK errors dialog", 1.2),
        (56, "Enable/Disable CAPTCHA", 2.5),
        (57, "Unit test", 2.0),
    ]),
    ("ReCaptcha P2", 59, 72, [
        (60, "Login by Mobile + Verification Code SMS OTP", 1.2),
        (61, "Me tab -> Settings -> Change Mobile -> SMS OTP", 1.2),
        (62, "Me tab -> Settings -> Change Email -> Email OTP", 1.2),
        (63, "Forgot Password -> Email OTP", 1.2),
        (64, "Forgot Password -> Mobile > SMS OTP", 1.2),
        (65, "Enable 2FA -> SMS OTP", 2.2),
        (66, "Activate Login by Email -> Email OTP", 1.2),
        (67, "Activate Login by Mobile -> SMS OTP", 1.2),
        (68, "Failed login attempt tracking + reCAPTCHA", 2.2),
        (69, "Resend OTP - all AH SMS OTP flows", 1.2),
        (70, "Resend OTP - all AH Email OTP flows", 1.2),
        (71, "Unit test", 2.0),
    ]),
    ("Smart Portfolio", 77, 93, [
        (80, "Portfolio Details (RSP Active)", 1.7),
        (81, "Deposit Funds - One time (Lump-sum)", 1.1),
        (82, "Deposit Funds - RSP / Method EGiro", 1.65),
        (83, "Deposit Funds - RSP / Method Internal Transfer", 2.55),
        (84, "Confirm Deposit (meothod EGiro + Internal Transfer)", 1.35),
        (85, "Deposit Funds / RSP Active Recurring", 1.65),
        (86, "Deposit Funds / RSP Active Edit Recurring", 1.65),
        (87, "Deposit Funds / RSP Active Confirm Edit Recurring", 0.65),
        (88, "Deposit Funds RSP Success and Fail", 1.15),
        (90, "Portfolio Details (RSP Active)", 0.65),
        (91, "Deposit Funds - One time (Lump-sum)", 2.15),
        (92, "Deposit Funds - One time (Recurring RSP Active and InActive)", 3.75),
    ]),
]


def main():
    creds = Credentials.from_service_account_file(CREDS_PATH, scopes=SCOPES)
    service = build("sheets", "v4", credentials=creds)

    # Unmerge the G20:G29 merged cell so per-row Use AI values can be written.
    # This merge was set by the team to group "Ask AI" buttons under one Use AI
    # value, but it conflicts with per-row methodology used by the rest of the sheet.
    sheet_id = None
    meta = service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
    for s in meta["sheets"]:
        if s["properties"]["title"] == TAB:
            sheet_id = s["properties"]["sheetId"]
            break

    unmerge_requests = [{
        "unmergeCells": {
            "range": {
                "sheetId": sheet_id,
                "startRowIndex": 19,
                "endRowIndex": 29,
                "startColumnIndex": 6,
                "endColumnIndex": 7,
            }
        }
    }]
    service.spreadsheets().batchUpdate(
        spreadsheetId=SPREADSHEET_ID, body={"requests": unmerge_requests}
    ).execute()
    print("Unmerged G20:G29 (PhillipGPT 'Ask AI' buttons)")

    # Build a single update payload: col G (Use AI 2P) for each data row
    updates = []  # list of (row, use_ai_value)
    for name, t, total_r, rows in PROJECTS:
        for row_num, fn, final in rows:
            use_ai = recompute_use_ai(final, fn)
            updates.append((row_num, use_ai))

    # Apply per-row Use AI updates
    print(f"Updating {len(updates)} per-row Use AI values...")
    data = [{"range": f"'{TAB}'!G{r}", "values": [[v]]} for r, v in updates]
    service.spreadsheets().values().batchUpdate(
        spreadsheetId=SPREADSHEET_ID,
        body={"valueInputOption": "USER_ENTERED", "data": data},
    ).execute()

    # Re-derive Total Use AI per project and update the Total row's col G
    print("Re-deriving Total Use AI per project...")
    total_updates = []
    for name, t, total_r, rows in PROJECTS:
        total_use_ai = sum(recompute_use_ai(final, fn) for _, fn, final in rows)
        # Round to 2 decimals to match sheet format
        total_use_ai = round(total_use_ai, 2)
        total_updates.append((total_r, total_use_ai))
        # Compute reduction %
        final_total = sum(final for _, _, final in rows)
        red = (final_total - total_use_ai) / final_total * 100
        print(f"  {name}: Final={final_total:>6.2f} UseAI={total_use_ai:>6.2f} Red={red:.1f}%")

    total_data = [{"range": f"'{TAB}'!G{r}", "values": [[v]]} for r, v in total_updates]
    service.spreadsheets().values().batchUpdate(
        spreadsheetId=SPREADSHEET_ID,
        body={"valueInputOption": "USER_ENTERED", "data": total_data},
    ).execute()
    print("Done.")


if __name__ == "__main__":
    main()
