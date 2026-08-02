"""Create 5 task-breakdown tabs in the May-submission-assessment Google Sheet.

One tab per Ready-for-Development URS project:
  1. Trade Ticket Lite Mode - Stocks
  2. PhillipGPT on POEMS
  3. Google ReCaptcha replace GeeTest (Phase 1 + Phase 2)
  4. DDA Linking and DDA Deposit
  5. POEMS Shareholder Meeting P3

Each tab follows the same team methodology as the existing Ready_Project_Est tab:
  Methodology note: 1P base x Platform x2 / Coordination 15% / Final 2P x2 / Use AI 0.65

Column structure per tab:
  A | B           | C         | D         | E             | F                  | G
  # | Feature Grp | Task      | Android   | iOS           | API Integration    | Frontend Logic

  Columns D-F = effort split (% of the per-row 2P final effort estimate)
  G = shared logic (state, validation, analytics, feature flags)

Tab name limits: max 100 chars, no special chars.
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, "/Users/lekhanhvinh/Developer/tdt/tdt-sheets/.venv/lib/python3.14/site-packages")
sys.path.insert(0, "/Users/lekhanhvinh/Developer/tdt/tdt-meta")

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

# ---------------- Config ----------------
SPREADSHEET_ID = "1_MIasMUIaDwauGsmSIQPiC7allQLDOxm9aW_t5a2vbk"
CREDS_PATH = os.path.expanduser("~/.tdt/philip-project-1-496009-aecd4c291640.json")
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

PLATFORM_MULTIPLIER = 2.0
COORD_OVERHEAD = 0.15
USE_AI_FACTOR = 0.65


# ---------------- Helpers ----------------


def md(hours: float) -> str:
    """Format as integer string if whole, else float string."""
    if isinstance(hours, float) and hours.is_integer():
        return str(int(hours))
    return f"{hours:g}" if isinstance(hours, float) else str(hours)


def fmt_pct(v: float) -> str:
    return f"{v * 100:.0f}%"


def final_2p(base_1p: float, coord: float = 0.15) -> float:
    """Final 2P MD = base x2 + coordination."""
    return round(base_1p * PLATFORM_MULTIPLIER + coord, 2)


def use_ai(base_1p: float, coord: float = 0.15) -> float:
    return round(final_2p(base_1p, coord) * USE_AI_FACTOR, 2)


def task_row(
    idx: int,
    group: str,
    task: str,
    android_pct: float,
    ios_pct: float,
    api_pct: float,
    logic_pct: float,
    base_1p: float,
    coord: float,
    notes: str = "",
) -> list:
    """Build one task row with effort split percentages and estimated MD."""
    f2p = final_2p(base_1p, coord)
    ua = use_ai(base_1p, coord)
    return [
        idx,
        group,
        task,
        fmt_pct(android_pct),
        fmt_pct(ios_pct),
        fmt_pct(api_pct),
        fmt_pct(logic_pct),
        md(round(f2p * android_pct, 2)),
        md(round(f2p * ios_pct, 2)),
        md(round(f2p * api_pct, 2)),
        md(round(f2p * logic_pct, 2)),
        md(ua),
        notes,
    ]


# =============================================================================
# PROJECT 1 — Trade Ticket Lite Mode - Stocks
# =============================================================================
# Scope: UI-only rearrangement. No backend changes. No API changes.
# Split rationale:
#   - Android/iOS: near-equal (UI re-layout, local state)
#   - API: 0% — no API changes per URS
#   - Logic: shared state (mode toggle, collapse state, analytics)

PROJECT_LITE_MODE = {
    "tab": "01 - Trade Ticket Lite Mode",
    "title": "Trade Ticket Lite Mode - Stocks",
    "subtitle": "Ready for development — URS: P3 Stock Trade ticket - Lite mode (v1.0, May 2026)",
    "rows": [
        # group, task, android%, ios%, api%, logic%, base_1p, coord, notes
        task_row(1, "Header View", "New header view without Counter Search / Vol / BVol / SVol",
                 0.35, 0.35, 0.00, 0.30, 1.25, 0.15,
                 "Remove vol fields; collapse section defaults"),
        task_row(2, "Counter Quotes", "New Counter Quotes section — current session only",
                 0.40, 0.40, 0.00, 0.20, 1.00, 0.15,
                 "No API change; current session price already available"),
        task_row(3, "More Settings", "Handle More Settings section (Order Type, Payment Mode, Settlement Currency, Validity)",
                 0.40, 0.40, 0.00, 0.20, 1.00, 0.15,
                 "Collapsible section; default collapsed if no saved preference"),
        task_row(4, "Mandatory Fields", "Handle Mandatory Section (Order Type, Price, Quality)",
                 0.40, 0.40, 0.00, 0.20, 1.25, 0.15,
                 "Reuse existing mandatory validation — UI only"),
        task_row(5, "State Persistence", "Logic to save collapsed/expand mode for More Settings",
                 0.30, 0.30, 0.00, 0.40, 0.45, 0.15,
                 "Local storage: mode preference, collapse state"),
        task_row(6, "Validation", "Handle validate and submit logic",
                 0.35, 0.35, 0.00, 0.30, 1.25, 0.15,
                 "No backend change; validation logic unchanged"),
        task_row(7, "Order Type Sheet", "Update new bottom sheet to show Order Type",
                 0.40, 0.40, 0.00, 0.20, 0.65, 0.15,
                 "Market-specific order type lists"),
        task_row(8, "Mode Switch", "Handle logic to switch between Pro/Lite Mode",
                 0.30, 0.30, 0.00, 0.40, 1.50, 0.15,
                 "Mode toggle + reset fields on switch"),
        task_row(9, "Mode Persistence", "Handle logic to save Pro/Lite Mode preference",
                 0.30, 0.30, 0.00, 0.40, 0.75, 0.15,
                 "Local storage; persist across sessions"),
        task_row(10, "Feature Flag", "ON/OFF Flag for Lite Mode feature",
                 0.25, 0.25, 0.00, 0.50, 1.25, 0.15,
                 "API-driven flag; no UI if disabled"),
        task_row(11, "Analytics", "GA4 + Appsflyer logging on Review Order tap",
                 0.20, 0.20, 0.00, 0.60, 0.00, 0.00,
                 "Shared analytics integration — no API impact"),
    ],
}


# =============================================================================
# PROJECT 2 — PhillipGPT on POEMS
# =============================================================================
# Scope: Iframe integration (web-based PhillipGPT UI) + Ask AI buttons on 9 P3 screens
# Split rationale:
#   - Android/iOS: button placement, iframe container, native header, disclaimer dialog
#   - API: parameter passing (PhillipID, AccountNo, Nickname, Query, ScreenContext,
#             PC Code, UI Theme), feature flag check, handshake auth
#   - Logic: iframe loading orchestration, deeplink, query passthrough, screen context

PROJECT_PHILLIPGPT = {
    "tab": "02 - PhillipGPT on POEMS",
    "title": "PhillipGPT on POEMS",
    "subtitle": "Ready for development — URS: Phillip GPT on POEMS v1.0 (ITSR 368213)",
    "rows": [
        # Ask AI button integration per screen
        task_row(1, "Ask AI Buttons", "Update 'Ask AI' button — Home Tab",
                 0.30, 0.30, 0.10, 0.30, 0.05, 0.10,
                 "Minor UI change; deeplink passthrough"),
        task_row(2, "Ask AI Buttons", "Update 'Ask AI' button — Watchlist Tab",
                 0.30, 0.30, 0.10, 0.30, 0.25, 0.10,
                 "Screen context = Watchlist Tab"),
        task_row(3, "Ask AI Buttons", "Update 'Ask AI' button — Global Search",
                 0.30, 0.30, 0.10, 0.30, 0.05, 0.10,
                 "Query string passthrough from search input"),
        task_row(4, "Ask AI Buttons", "Update 'Ask AI' button — Counter Details",
                 0.30, 0.30, 0.10, 0.30, 0.25, 0.10,
                 "Screen context = Counter Detail - {stock}"),
        task_row(5, "Ask AI Buttons", "Update 'Ask AI' button — Screener",
                 0.30, 0.30, 0.10, 0.30, 0.25, 0.10,
                 "Screen context = Screener"),
        task_row(6, "Ask AI Buttons", "Update 'Ask AI' button — Market Tab",
                 0.30, 0.30, 0.10, 0.30, 0.25, 0.10,
                 "Screen context = Markets Tab"),
        task_row(7, "Ask AI Buttons", "Update 'Ask AI' button — Trade Tab",
                 0.30, 0.30, 0.10, 0.30, 0.25, 0.10,
                 "Screen context = Trade Tab"),
        task_row(8, "Ask AI Buttons", "Update 'Ask AI' button — Community Tab",
                 0.30, 0.30, 0.10, 0.30, 0.25, 0.10,
                 "Screen context = Community Tab"),
        task_row(9, "Ask AI Buttons", "Update 'Ask AI' button — Me Tab",
                 0.30, 0.30, 0.10, 0.30, 0.25, 0.10,
                 "Screen context = Me Tab"),
        task_row(10, "Ask AI Buttons", "Update 'Ask AI' button — Help",
                 0.30, 0.30, 0.10, 0.30, 0.25, 0.10,
                 "Screen context = Help Screen"),
        # PhillipGPT screen (iframe + native header)
        task_row(11, "PhillipGPT Screen", "Native header: Back, New Chat, Chat History icons",
                 0.40, 0.40, 0.00, 0.20, 0.75, 0.10,
                 "Navigation controls; no API calls"),
        task_row(12, "PhillipGPT Screen", "Iframe container: theme sync (Light/Dark), handshake auth",
                 0.20, 0.20, 0.20, 0.40, 0.75, 0.10,
                 "UI Theme param; auth handshake with PhillipGPT service"),
        task_row(13, "PhillipGPT Screen", "Iframe: load with query passthrough (pre-fill input)",
                 0.15, 0.15, 0.20, 0.50, 0.50, 0.10,
                 "Query param → auto-send if history exists"),
        task_row(14, "PhillipGPT Screen", "Iframe: load with Screen Context (suggested questions)",
                 0.15, 0.15, 0.20, 0.50, 0.25, 0.10,
                 "3 contextual questions from Screen Context Prompts Library"),
        task_row(15, "PhillipGPT Screen", "Iframe: load new chat with random suggested questions",
                 0.15, 0.15, 0.20, 0.50, 0.25, 0.10,
                 "General prompts when no screen context"),
        task_row(16, "PhillipGPT Screen", "Disclaimer pop-up on first load (Important Notice)",
                 0.40, 0.40, 0.00, 0.20, 0.00, 0.00,
                 "Mark seen-in-disclaimer in local storage"),
        task_row(17, "PhillipGPT Screen", "Chat History: load past conversation, rehydrate context",
                 0.20, 0.20, 0.20, 0.40, 0.50, 0.10,
                 "Scoped context rehydration from selected thread"),
        task_row(18, "Deeplink", "Deeplink: support query string + screen context params",
                 0.15, 0.15, 0.20, 0.50, 0.50, 0.10,
                 "Universal deeplink → PhillipGPT iframe with params"),
        task_row(19, "Feature Flag", "API-configurable ON/OFF flag for PhillipGPT visibility",
                 0.15, 0.15, 0.25, 0.45, 0.85, 0.10,
                 "GPT_Source field (NextVestment / PhillipGPT / null)"),
    ],
}


# =============================================================================
# PROJECT 3 — Google ReCaptcha replace GeeTest (Phase 1 + Phase 2)
# =============================================================================
# Scope: Replace GeeTest with Google Invisible reCAPTCHA + SMS Defender
# Phase 1 = RU (Registered Users) flows
# Phase 2 = AH (Account Holders) + admin portal for CEU
# Split rationale:
#   - Android/iOS: SDK integration, resend timer fix, show/hide buttons, error dialogs
#   - API: reCAPTCHA verification call, SMS Defender check, threshold config,
#           feature flag on/off, GeeTest concurrent toggle, failed attempt tracking
#   - Logic: score evaluation, PASS/FAIL routing, resend cooldown, error messaging

PROJECT_RECAPTCHA = {
    "tab": "03 - Google ReCaptcha v1.0",
    "title": "Google ReCaptcha replace GeeTest",
    "subtitle": "Ready for development — URS: ITSR 369574 v1.0",
    "rows": [
        # ---- Phase 1 ----
        task_row(1, "Phase 1 — SDK", "Integrate Google Invisible reCAPTCHA SDK",
                 0.35, 0.35, 0.30, 0.00, 1.50, 0.50,
                 "SDK init, site key config, challenge trigger"),
        task_row(2, "Phase 1 — SDK", "Integrate SMS Defender SDK",
                 0.30, 0.30, 0.40, 0.00, 1.50, 0.50,
                 "Risk score retrieval; per-request scoring"),
        task_row(3, "Phase 1 — Flows", "Login by Mobile + SMS OTP — reCAPTCHA + SMS Defender",
                 0.25, 0.25, 0.30, 0.20, 0.50, 0.20,
                 "AC1: before OTP trigger"),
        task_row(4, "Phase 1 — Flows", "Signup by Mobile > SMS OTP — reCAPTCHA + SMS Defender",
                 0.25, 0.25, 0.30, 0.20, 0.50, 0.20,
                 "AC1: before OTP trigger"),
        task_row(5, "Phase 1 — Flows", "Me > Settings > Change Mobile > SMS OTP — reCAPTCHA + SMS Defender",
                 0.25, 0.25, 0.30, 0.20, 0.50, 0.20,
                 "AC1: before OTP trigger"),
        task_row(6, "Phase 1 — Flows", "Signup by Email > Email OTP — reCAPTCHA only",
                 0.30, 0.30, 0.25, 0.15, 0.50, 0.20,
                 "AC1: no SMS Defender for email"),
        task_row(7, "Phase 1 — Flows", "Me > Settings > Change Email > Email OTP — reCAPTCHA only",
                 0.30, 0.30, 0.25, 0.15, 0.50, 0.20,
                 "AC1: no SMS Defender for email"),
        task_row(8, "Phase 1 — Flows", "Forgot Password > Email OTP — reCAPTCHA only",
                 0.30, 0.30, 0.25, 0.15, 0.50, 0.20,
                 "AC1: no SMS Defender for email"),
        task_row(9, "Phase 1 — Flows", "Forgot Password > Mobile > SMS OTP (RU) — reCAPTCHA + SMS Defender",
                 0.25, 0.25, 0.30, 0.20, 0.50, 0.20,
                 "AC1: before OTP trigger"),
        task_row(10, "Phase 1 — Flows", "Me > Settings > Activate Login by Email > Email OTP — reCAPTCHA only",
                 0.30, 0.30, 0.25, 0.15, 0.50, 0.20,
                 "AC1: no SMS Defender for email"),
        task_row(11, "Phase 1 — Flows", "Me > Settings > Activate Login by Mobile > SMS OTP — reCAPTCHA + SMS Defender",
                 0.25, 0.25, 0.30, 0.20, 0.50, 0.20,
                 "AC1: before OTP trigger"),
        # Resend OTP
        task_row(12, "Phase 1 — Resend", "Resend OTP — All SMS OTP flows (RU) — reCAPTCHA + SMS Defender",
                 0.25, 0.25, 0.30, 0.20, 0.50, 0.20,
                 "AC2: on Resend Code click; 120s timer (changed from 60s)"),
        task_row(13, "Phase 1 — Resend", "Resend OTP — All Email OTP flows (RU) — reCAPTCHA only",
                 0.30, 0.30, 0.25, 0.15, 0.50, 0.20,
                 "AC2: on Resend Code click; 120s timer"),
        # Error dialogs
        task_row(14, "Phase 1 — Errors", "Email OTP: FAIL dialog (reCAPTCHA fail)",
                 0.35, 0.35, 0.15, 0.15, 0.50, 0.20,
                 "ERRORMSG-FAIL configurable; AC3"),
        task_row(15, "Phase 1 — Errors", "SMS OTP: FAIL dialog (reCAPTCHA or SMS Defender fail)",
                 0.35, 0.35, 0.15, 0.15, 0.50, 0.20,
                 "ERRORMSG-FAIL; AC5 — both must pass"),
        task_row(16, "Phase 1 — Errors", "Other SDK errors dialog (non-FAIL/OTHERS)",
                 0.35, 0.35, 0.15, 0.15, 0.50, 0.20,
                 "ERRORMSG-OTHERS; AC7"),
        # Phase 1 config controls
        task_row(17, "Phase 1 — Config", "Enable/Disable CAPTCHA — reCAPTCHA toggle (API-driven)",
                 0.10, 0.10, 0.40, 0.40, 1.00, 0.50,
                 "Backend flag; if OFF skip validation but still log"),
        task_row(18, "Phase 1 — Config", "Enable/Disable CAPTCHA — SMS Defender toggle (API-driven)",
                 0.10, 0.10, 0.40, 0.40, 1.00, 0.50,
                 "Backend flag; if OFF skip validation but still log"),
        task_row(19, "Phase 1 — Config", "reCAPTCHA threshold score config (API-driven, initial 0.2)",
                 0.00, 0.00, 0.50, 0.50, 0.00, 0.00,
                 "API config; threshold passed to SDK"),
        task_row(20, "Phase 1 — Config", "SMS Defender risk threshold config (API-driven, initial 0.7)",
                 0.00, 0.00, 0.50, 0.50, 0.00, 0.00,
                 "API config; risk score evaluated server-side"),
        task_row(21, "Phase 1 — Config", "Error messages editable via configuration API",
                 0.00, 0.00, 0.50, 0.50, 0.00, 0.00,
                 "ERRORMSG-FAIL, ERRORMSG-OTHERS in DB"),
        task_row(22, "Phase 1 — Config", "GeeTest concurrent toggle (ON/OFF via API)",
                 0.00, 0.00, 0.45, 0.55, 0.00, 0.00,
                 "If GeeTest ON: show GeeTest AND validate reCAPTCHA/SMS Defender"),
        task_row(23, "Phase 1 — Timer Fix", "Resend cooldown timer changed to 120s (from 60s)",
                 0.45, 0.45, 0.00, 0.10, 0.00, 0.00,
                 "A3: 60s → 120s; timer persists on back navigation"),
        task_row(24, "Phase 1 — Timer Fix", "Resend timer persists on back navigation (SMS + Email)",
                 0.45, 0.45, 0.00, 0.10, 0.00, 0.00,
                 "A1-AC1/AC2: timer continues in background; no auto-resend"),
        task_row(25, "Phase 1 — Logging", "CAPTCHA logging: email, phone, country, scores, IP, deviceID, OS",
                 0.00, 0.00, 0.45, 0.55, 0.00, 0.00,
                 "AC7: all events logged regardless of toggle state"),
        # ---- Phase 2 ----
        task_row(26, "Phase 2 — AH Flows", "Login by Mobile + SMS OTP (AH) — reCAPTCHA + SMS Defender",
                 0.20, 0.20, 0.35, 0.25, 0.50, 0.20,
                 "B1: same pattern as RU flows"),
        task_row(27, "Phase 2 — AH Flows", "Me > Settings > Change Mobile > SMS OTP (AH) — reCAPTCHA + SMS Defender",
                 0.20, 0.20, 0.35, 0.25, 0.50, 0.20,
                 "B1"),
        task_row(28, "Phase 2 — AH Flows", "Me > Settings > Change Email > Email OTP (AH) — reCAPTCHA only",
                 0.25, 0.25, 0.30, 0.20, 0.50, 0.20,
                 "B1"),
        task_row(29, "Phase 2 — AH Flows", "Forgot Password > Email OTP (AH) — reCAPTCHA only",
                 0.25, 0.25, 0.30, 0.20, 0.50, 0.20,
                 "B1"),
        task_row(30, "Phase 2 — AH Flows", "Forgot Password > Mobile > SMS OTP (AH) — reCAPTCHA + SMS Defender",
                 0.20, 0.20, 0.35, 0.25, 0.50, 0.20,
                 "B1"),
        task_row(31, "Phase 2 — AH Flows", "Enable 2FA > SMS OTP — reCAPTCHA + SMS Defender",
                 0.20, 0.20, 0.35, 0.25, 1.00, 0.20,
                 "B1: 2FA activation flow"),
        task_row(32, "Phase 2 — AH Flows", "Activate Login by Email > Email OTP (AH) — reCAPTCHA only",
                 0.25, 0.25, 0.30, 0.20, 0.50, 0.20,
                 "B1"),
        task_row(33, "Phase 2 — AH Flows", "Activate Login by Mobile > SMS OTP (AH) — reCAPTCHA + SMS Defender",
                 0.20, 0.20, 0.35, 0.25, 0.50, 0.20,
                 "B1"),
        task_row(34, "Phase 2 — AH Flows", "Resend OTP — All AH SMS OTP flows — reCAPTCHA + SMS Defender",
                 0.20, 0.20, 0.35, 0.25, 0.50, 0.20,
                 "Same pattern as Phase 1 resend"),
        task_row(35, "Phase 2 — AH Flows", "Resend OTP — All AH Email OTP flows — reCAPTCHA only",
                 0.25, 0.25, 0.30, 0.20, 0.50, 0.20,
                 "Same pattern as Phase 1 resend"),
        # Failed attempt tracking
        task_row(36, "Phase 2 — Tracking", "Failed login attempt tracking (multi-platform + account + PhillipID level)",
                 0.00, 0.00, 0.50, 0.50, 0.00, 0.00,
                 "B1-AC7: track across P2Web + M2; per-account (AH) and per-PhillipID (RU)"),
        task_row(37, "Phase 2 — Tracking", "reCAPTCHA trigger after 2 failed login attempts (AH)",
                 0.20, 0.20, 0.35, 0.25, 1.00, 0.20,
                 "B1-AC7: 3rd attempt requires reCAPTCHA before password check"),
        task_row(38, "Phase 2 — Tracking", "Non-human detection: 1s interval between attempts triggers reCAPTCHA",
                 0.15, 0.15, 0.35, 0.35, 1.00, 0.20,
                 "B1-AC8: timing heuristic to detect automation"),
        # Admin Portal
        task_row(39, "Phase 2 — Admin Portal", "Admin Portal: view block reasons and user log details",
                 0.25, 0.25, 0.30, 0.20, 1.00, 0.20,
                 "C1-AC2: POEMS + GWM/MyWealth users; reCAPTCHA + SMS Defender scores"),
        task_row(40, "Phase 2 — Admin Portal", "Admin Portal: bypass toggle per user (CEU)",
                 0.20, 0.20, 0.30, 0.30, 1.00, 0.20,
                 "C1-AC3: bypass ON = skip blocking but keep logging"),
        task_row(41, "Phase 2 — Admin Portal", "Admin Portal: audit trail for CEU actions",
                 0.00, 0.00, 0.50, 0.50, 0.00, 0.00,
                 "C1-AC4: audit log for bypass toggle changes"),
    ],
}


# =============================================================================
# PROJECT 4 — DDA Linking and DDA Deposit (DBS FAST + CIS + GBO Integration)
# =============================================================================
# Scope: DDA bank linking + deposit via DBS FAST Collection API
# Phase 1 = GBO accounts (M, C, KC, CC, V) on P3 + Central UI + iFrame
# Split rationale:
#   - Android/iOS: UI screens (deposit form, linking form, delink), push notification handling
#   - API: DBS FAST API (linking + deposit), CIS API (account verification), GBO posting,
#           RPS processing, poems engine push notification, feature flag
#   - Logic: async status handling, RPS polling, rejection flow, joint account display

PROJECT_DDA = {
    "tab": "04 - DDA Linking & Deposit",
    "title": "DDA Linking and DDA Deposit",
    "subtitle": "Ready for development — URS: DDA Linking and DDA Deposit v1.0 (ITSR 319991/319992/319999/320736)",
    "rows": [
        # ---- Phase 1: P3 / Central UI ----
        # Currency + deposit method selection
        task_row(1, "Deposit Fund", "Currency selection (SGD tab default; Non-SGD display fund transfer/TT instructions)",
                 0.40, 0.40, 0.10, 0.10, 0.50, 0.10,
                 "SGD tab default; Non-SGD → external links only"),
        task_row(2, "Deposit Fund", "Deposit method selection: Instant Deposit via DDA, PayNow, eNETS",
                 0.40, 0.40, 0.10, 0.10, 0.50, 0.10,
                 "DDA only for SGD; check DDA status on select"),
        # DDA/GIRO status check
        task_row(3, "DDA Status Check", "FO API check account DDA/GIRO status via CIS API",
                 0.00, 0.00, 0.70, 0.30, 1.00, 0.20,
                 "Status → Pending / Approved / No Linkage → route to correct screen"),
        task_row(4, "DDA Status Check", "Display 'Application In-Progress' page for Pending status",
                 0.45, 0.45, 0.05, 0.05, 0.25, 0.10,
                 "Central UI; Done → redirect to Me tab"),
        task_row(5, "DDA Status Check", "Push notification on DDA linking status change (Pending → Approved/Rejected)",
                 0.00, 0.00, 0.50, 0.50, 0.50, 0.10,
                 "Via poems engine API; P2/P3/MyWealth"),
        # DDA Linking Application Form
        task_row(6, "DDA Linking Form", "DDA Linking Application Form: account display (read-only, incl. joint account holders)",
                 0.40, 0.40, 0.10, 0.10, 0.50, 0.10,
                 "Account no., service type, holder name, NRIC/Passport — joint account multi-holder"),
        task_row(7, "DDA Linking Form", "DDA Linking Application Form: bank dropdown (eGIRO participant bank list)",
                 0.40, 0.40, 0.10, 0.10, 0.75, 0.10,
                 "DBS/OCBC/UOB/SC/HSBC/ICBC; bank code ↔ BIC mapping table"),
        task_row(8, "DDA Linking Form", "DDA Linking Form: submit → DBS iBanking redirect (bank portal)",
                 0.15, 0.15, 0.40, 0.30, 0.75, 0.10,
                 "P3 API → DBS Vendor API → redirect to bank iBanking for DDA auth"),
        task_row(9, "DDA Linking Form", "Post-bank-completion: update status to Pending + display confirmation",
                 0.30, 0.30, 0.25, 0.15, 0.50, 0.10,
                 "P3 API receives callback; FO DB update; push notification"),
        task_row(10, "DDA Linking Form", "DBS API: async result handling (Approved / Rejected) → CIS insert + FO update",
                 0.00, 0.00, 0.60, 0.40, 1.00, 0.20,
                 "P3 API interprets DBS response; CIS API insert on Approved; push notification"),
        # DDA Deposit Form
        task_row(11, "DDA Deposit Form", "DDA Deposit Form: info prompt + PROCEED button",
                 0.45, 0.45, 0.05, 0.05, 0.25, 0.10,
                 "Info: 'DDA Deposit uses your GIRO linkage'"),
        task_row(12, "DDA Deposit Form", "DDA Deposit Form: read-only display (linked bank, account no., SGD)",
                 0.45, 0.45, 0.05, 0.05, 0.50, 0.10,
                 "Retrieved from CIS API; bank name + masked account number"),
        task_row(13, "DDA Deposit Form", "DDA Deposit Form: amount input (numeric, 2 decimal, > 0, max SGD 200,000)",
                 0.40, 0.40, 0.10, 0.10, 0.50, 0.10,
                 "Frontend validation; error message for > 200,000"),
        task_row(14, "DDA Deposit Form", "DDA Deposit Form: submit → P3 API → DBS FAST Collection API",
                 0.10, 0.10, 0.55, 0.25, 1.00, 0.20,
                 "Sync response: Request Submitted → display confirmation page"),
        task_row(15, "DDA Deposit", "DBS async result: Approved → GBO API posting (M, C, KC, CC accounts)",
                 0.00, 0.00, 0.65, 0.35, 1.50, 0.30,
                 "P3 API → GBO API → RPS placeholder → 5-min RPS job → posting"),
        task_row(16, "DDA Deposit", "DBS async result: Rejected → push notification + rejection handling",
                 0.10, 0.10, 0.50, 0.30, 0.50, 0.10,
                 "Push notification; 'Contact Info' → Contact Us page"),
        task_row(17, "DDA Deposit", "Push notification: deposit status (Request Submitted / Received OK / Received Unsuccessful)",
                 0.00, 0.00, 0.50, 0.50, 0.50, 0.10,
                 "Via poems engine API; tap → Live Cash Balance or Contact Us"),
        task_row(18, "DDA Deposit", "GBO Posting: RPS placeholder + 5-min job processing (Phase 1: M, C, KC, CC, V)",
                 0.00, 0.00, 0.65, 0.35, 1.50, 0.30,
                 "FO → GBO API → RPS API → batch posting; 24h T+1 settlement indicator"),
        # Delink
        task_row(19, "Delink DDA", "Bank A/C Information page: display GIRO/DDA linked bank details",
                 0.40, 0.40, 0.10, 0.10, 0.50, 0.10,
                 "CIS data: bank name, SWIFT code, bank account number"),
        task_row(20, "Delink DDA", "Delink confirmation pop-up + submission",
                 0.40, 0.40, 0.10, 0.10, 0.75, 0.10,
                 "Confirm/Cancel; CIS API → remove linkage; FO DB update; toast message"),
        # Config / Integration
        task_row(21, "API — DBS", "DBS FAST Collection API: linking submission + deposit processing",
                 0.00, 0.00, 0.70, 0.30, 3.00, 0.50,
                 "Bank code ↔ BIC mapping; timeout/retry/backoff; async result handling"),
        task_row(22, "API — CIS", "CIS API: account DDA/GIRO status + linked bank data retrieval",
                 0.00, 0.00, 0.65, 0.35, 2.00, 0.40,
                 "Status check; bank account details; joint account multi-holder NRIC"),
        task_row(23, "API — GBO", "GBO API: posting transaction on Approved (Phase 1: M/C/KC/CC/V)",
                 0.00, 0.00, 0.60, 0.40, 1.50, 0.30,
                 "GBO → RPS API → placeholder → batch job"),
        task_row(24, "API — POEMS Engine", "POEMS engine: push notification dispatch (via poems engine API)",
                 0.00, 0.00, 0.55, 0.45, 1.00, 0.20,
                 "Trigger on DDA status change, deposit status change"),
        task_row(25, "Config / Ops", "Account eligibility check: GBO accounts (M, C, KC, CC, V) for Phase 1",
                 0.00, 0.00, 0.60, 0.40, 0.50, 0.10,
                 "Account type filter; ineligible accounts hidden from DDA flow"),
        task_row(26, "Config / Ops", "Bank code ↔ BIC code mapping table (DBS, OCBC, UOB, SC, HSBC, ICBC)",
                 0.00, 0.00, 0.55, 0.45, 0.50, 0.10,
                 "Static config; used in DBS API calls for eGIRO application"),
        task_row(27, "Config / Ops", "Finance Report: eDDA reconciliation report (Katherine + Alvin to define)",
                 0.00, 0.00, 0.55, 0.45, 1.00, 0.20,
                 "FO → generate recon report → Finance; discuss format with Finance"),
        task_row(28, "Config / Ops", "Ops runbook: async failure handling (DBS API timeout, partial confirmation)",
                 0.00, 0.00, 0.50, 0.50, 1.00, 0.20,
                 "Reconciliation between DBS response and FO DB; escalation path"),
        task_row(29, "Config / Ops", "Security: bank account data encryption + audit log (DDA linking + deposit)",
                 0.00, 0.00, 0.60, 0.40, 1.50, 0.30,
                 "Encryption at rest + in transit; full audit trail for compliance"),
    ],
}


# =============================================================================
# PROJECT 5 — POEMS Shareholder Meeting P3 (Refinitiv + 72h Free Shares)
# =============================================================================
# Scope: Corporate Actions → Shareholder Meeting sub-module
# Refinitiv data feed + in-app meeting list + voting + free shares redemption
# Split rationale:
#   - Android/iOS: all UI screens (meeting list, voting form, submission confirmation)
#   - API: Refinitiv data ingestion, meeting status management, submission to proxy@phillip.com.sg,
#           free shares calculation, withdrawal admin
#   - Logic: 72h free shares calculation, Refinitiv reconciliation, CANC/REPL handling,
#             joint account voting rules

PROJECT_SHAREHOLDER = {
    "tab": "05 - Shareholder Meeting P3",
    "title": "POEMS Shareholder Meeting P3",
    "subtitle": "Ready for development — URS: POEMS Shareholder Meeting P3 (Refinitiv + 72h Free Shares)",
    "rows": [
        # Data ingestion
        task_row(1, "Refinitiv Data", "Refinitiv feed: daily download (Mon-Fri incl. PH) General_Meetings_Daily file",
                 0.00, 0.00, 0.70, 0.30, 1.50, 0.30,
                 "Batch download; parse MessageReference, EventType, Status, ISIN, SecurityDescription, etc."),
        task_row(2, "Refinitiv Data", "Refinitiv field mapping: ISIN, Exchange (=XSES), MeetingDate, RecordDate, Location, Narrative",
                 0.00, 0.00, 0.65, 0.35, 1.00, 0.20,
                 "Only show XSES records; APPD status only; only display fields"),
        task_row(3, "Refinitiv Data", "MessageFunction handling: NEWM (create), CANC (mark cancelled + disable button), REPL (overwrite)",
                 0.00, 0.00, 0.65, 0.35, 1.00, 0.20,
                 "CANC → append 'CANCELLED' to instrument name; disable Submit Proxy Instruction"),
        task_row(4, "Refinitiv Data", "Refinitiv stale/missing data reconciliation",
                 0.00, 0.00, 0.60, 0.40, 2.00, 0.40,
                 "Identify missing data; alert ops; graceful degradation"),
        task_row(5, "Refinitiv Data", "Meeting event expiry: remove from P3 on Meeting Date +1",
                 0.10, 0.10, 0.50, 0.30, 0.50, 0.10,
                 "Scheduled cleanup job; past meetings hidden from list"),
        # Meeting list UI
        task_row(6, "Meeting List", "Corporate Actions module: new 'Shareholder Meeting' sub-module entry",
                 0.45, 0.45, 0.05, 0.05, 0.50, 0.10,
                 "Compare portfolio holdings vs Refinitiv → show 'A' if holding, 'B' if not"),
        task_row(7, "Meeting List", "Meeting list screen: meeting card (company, date, location, Virtual Meeting badge)",
                 0.45, 0.45, 0.05, 0.05, 0.75, 0.10,
                 "Fields: SecurityDescription, MeetingDate, Location, Virtual Meeting flag"),
        task_row(8, "Meeting List", "Meeting list: 'Submitted' green badge + submitted instruction review",
                 0.45, 0.45, 0.05, 0.05, 0.75, 0.10,
                 "4.1: green box appears after submission; tap to review"),
        task_row(9, "Meeting List", "Meeting list: important notes footer (SGX link, free shares rule, 72h rule)",
                 0.40, 0.40, 0.10, 0.10, 0.25, 0.10,
                 "Static text from URS; hyperlink to sgx.com/securities/meeting-schedules"),
        task_row(10, "Meeting List", "Meeting detail: submission cut-off display (MeetingDate - 8 business days)",
                 0.40, 0.40, 0.10, 0.10, 0.50, 0.10,
                 "Calculated field; if past → show 'Cut-off passed'"),
        task_row(11, "Meeting List", "Meeting detail: SGX website hyperlink + 'GET STARTED' button",
                 0.40, 0.40, 0.10, 0.10, 0.25, 0.10,
                 "Deep link → SGX meeting page"),
        # Attend-in-person flow
        task_row(12, "Attend-in-Person", "Attend-in-person flow: Option select (Attend-in-person / Vote only)",
                 0.45, 0.45, 0.05, 0.05, 0.50, 0.10,
                 "2.1.1: validate joint account on 'Attend-in-person' selection"),
        task_row(13, "Attend-in-Person", "Non-joint account: Myself / Appoint proxy selection",
                 0.45, 0.45, 0.05, 0.05, 0.50, 0.10,
                 "2.1.2: show 2 options after Attend-in-person"),
        task_row(14, "Attend-in-Person", "Auto-populate account holder particulars (CIS): name, ID, email (editable), address (editable)",
                 0.20, 0.20, 0.30, 0.30, 1.00, 0.20,
                 "2.1.3: read from CIS; email + residential address editable; no validation"),
        task_row(15, "Attend-in-Person", "Share quantity: Vote with all / Vote with some (text input + validation)",
                 0.40, 0.40, 0.10, 0.10, 0.75, 0.15,
                 "2.1.4: 'You can only vote up to <available>' error on exceed"),
        task_row(16, "Attend-in-Person", "Final confirmation prompt before submission",
                 0.40, 0.40, 0.10, 0.10, 0.50, 0.10,
                 "2.1.5: review + confirm"),
        task_row(17, "Attend-in-Person", "Joint account: multi-holder display + proxy appointment",
                 0.40, 0.40, 0.10, 0.10, 0.75, 0.15,
                 "2.2: show all holder names; select holder → same flow as 2.1.3-2.1.5"),
        # Vote-only flow
        task_row(18, "Vote Only", "Vote Only: Vote in my own capacity / Appoint chairman selection",
                 0.40, 0.40, 0.10, 0.10, 0.50, 0.10,
                 "3.1.1: same pattern as attend-in-person option select"),
        task_row(19, "Vote Only", "Auto-populate account holder particulars (CIS) — vote only",
                 0.20, 0.20, 0.30, 0.30, 0.75, 0.15,
                 "3.1.2: same as 2.1.3"),
        task_row(20, "Vote Only", "Resolution voting: Add Resolution / Delete Resolution (bin icon + confirm)",
                 0.40, 0.40, 0.10, 0.10, 0.75, 0.15,
                 "3.1.3: dynamic resolution rows; pop-up confirm on delete"),
        task_row(21, "Vote Only", "'Your vote' dropdown: For / Against / Abstain / Default",
                 0.40, 0.40, 0.10, 0.10, 0.50, 0.10,
                 "3.1.4: per resolution"),
        task_row(22, "Vote Only", "Vote with all / Vote with some per resolution (validation same as 2.1.4)",
                 0.40, 0.40, 0.10, 0.10, 0.50, 0.10,
                 "3.1.5: submit → confirmation screen"),
        task_row(23, "Vote Only", "Appoint proxy: particulars entry (no validation)",
                 0.40, 0.40, 0.10, 0.10, 0.50, 0.10,
                 "2.3.1: forward to 2.1.4 flow"),
        # Free shares (P3)
        task_row(24, "Free Shares (72h)", "Free shares calculation: identify 'free' holdings 72h before RecordDate",
                 0.00, 0.00, 0.60, 0.40, 1.50, 0.30,
                 "Confirm owning system for 72h calculation with BA; CSIS/free ledger check"),
        task_row(25, "Free Shares (72h)", "Free shares redemption screen: display eligible share quantity",
                 0.40, 0.40, 0.10, 0.10, 1.00, 0.20,
                 "Show shares with 'free' status 72h before meeting; 72h window display"),
        task_row(26, "Free Shares (72h)", "Free shares: Submit instruction + confirmation",
                 0.40, 0.40, 0.10, 0.10, 1.00, 0.20,
                 "Combined with voting submission or separate? Confirm with BA"),
        # Submission
        task_row(27, "Submission", "Submit proxy instruction: email to proxy@phillip.com.sg (Attend-in-Person format)",
                 0.00, 0.00, 0.65, 0.35, 1.50, 0.30,
                 "5.2.1: excel attachment; all fields from 2.x flows"),
        task_row(28, "Submission", "Submit proxy instruction: email to proxy@phillip.com.sg (Vote Only format)",
                 0.00, 0.00, 0.65, 0.35, 1.50, 0.30,
                 "5.2.2: excel attachment; resolution columns dynamic (01, 02...)"),
        task_row(29, "Submission", "In-app submission status + audit log",
                 0.20, 0.20, 0.30, 0.30, 1.00, 0.20,
                 "Green 'Submitted' badge; submission timestamp; retry capability"),
        # Withdrawal Admin
        task_row(30, "Withdrawal Admin", "Withdrawal Admin UI: filters (Mode, Date, Instrument, Representative, Name, Account, ID, Email)",
                 0.00, 0.00, 0.60, 0.40, 1.00, 0.20,
                 "5.1: determine build vs manual ops; decision needed from URS"),
        task_row(31, "Withdrawal Admin", "Withdrawal Admin: CSV download of submitted entries",
                 0.00, 0.00, 0.55, 0.45, 0.50, 0.10,
                 "5.1: columns: Request Received, Instrument, Meeting Date, Mode, Rep, Name, Account, ID, Email"),
    ],
}


# =============================================================================
# Sheets API helpers
# =============================================================================

ALL_PROJECTS = [
    PROJECT_LITE_MODE,
    PROJECT_PHILLIPGPT,
    PROJECT_RECAPTCHA,
    PROJECT_DDA,
    PROJECT_SHAREHOLDER,
]

SPREADSHEET_ID = "1_MIasMUIaDwauGsmSIQPiC7allQLDOxm9aW_t5a2vbk"


def get_service():
    creds = Credentials.from_service_account_file(CREDS_PATH, scopes=SCOPES)
    return build("sheets", "v4", credentials=creds)


def ensure_tab(service, tab_name: str) -> None:
    """Create a tab if it doesn't exist."""
    meta = service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
    existing = [s["properties"]["title"] for s in meta["sheets"]]
    if tab_name in existing:
        print(f"  Tab already exists: {tab_name}")
        return
    try:
        service.spreadsheets().batchUpdate(
            spreadsheetId=SPREADSHEET_ID,
            body={"requests": [{"addSheet": {"properties": {"title": tab_name}}}]},
        ).execute()
        print(f"  + Created tab: {tab_name}")
    except Exception as e:
        if "already exists" in str(e):
            print(f"  Tab already exists: {tab_name}")
        else:
            raise


def build_tab_content(project: dict) -> list[list]:
    """Build all rows for a project tab."""
    rows = []

    # Title block
    rows.append([project["title"]])
    rows.append([project["subtitle"]])
    rows.append([
        "Methodology: 1P base x2 (Android+iOS) + Coordination 15% / Final 2P / Use AI 0.65  |  "
        "Effort split is indicative — use for task assignment and sprint planning."
    ])
    rows.append([])

    # Column headers
    rows.append([
        "#",
        "Feature Group",
        "Task",
        "Android %",
        "iOS %",
        "API %",
        "Logic %",
        "Android (MD)",
        "iOS (MD)",
        "API (MD)",
        "Logic (MD)",
        "Use AI 2P (MD)",
        "Notes",
    ])

    group_subtotals = {}
    for row in project["rows"]:
        idx, group, task, adr_pct, ios_pct, api_pct, logic_pct, adr_md, ios_md, api_md, logic_md, use_ai, notes = row
        rows.append([
            idx, group, task, adr_pct, ios_pct, api_pct, logic_pct,
            adr_md, ios_md, api_md, logic_md, use_ai, notes
        ])
        if group not in group_subtotals:
            group_subtotals[group] = {"adr": 0.0, "ios": 0.0, "api": 0.0, "logic": 0.0, "ua": 0.0}
        group_subtotals[group]["adr"] += float(adr_md) if adr_md else 0.0
        group_subtotals[group]["ios"] += float(ios_md) if ios_md else 0.0
        group_subtotals[group]["api"] += float(api_md) if api_md else 0.0
        group_subtotals[group]["logic"] += float(logic_md) if logic_md else 0.0
        group_subtotals[group]["ua"] += float(use_ai) if use_ai else 0.0

    # Subtotals per feature group
    rows.append([])
    for group, totals in group_subtotals.items():
        rows.append([
            "",
            f"Subtotal — {group}",
            "",
            "",
            "",
            "",
            "",
            md(totals["adr"]),
            md(totals["ios"]),
            md(totals["api"]),
            md(totals["logic"]),
            md(totals["ua"]),
            "",
        ])

    # Grand total
    grand = {"adr": 0.0, "ios": 0.0, "api": 0.0, "logic": 0.0, "ua": 0.0}
    for totals in group_subtotals.values():
        for k in grand:
            grand[k] += totals[k]

    rows.append([])
    rows.append([
        "",
        "GRAND TOTAL",
        "",
        "",
        "",
        "",
        "",
        md(grand["adr"]),
        md(grand["ios"]),
        md(grand["api"]),
        md(grand["logic"]),
        md(grand["ua"]),
        "",
    ])

    return rows


def write_tab(service, tab_name: str, rows: list[list]) -> None:
    """Clear and write all rows to a tab."""
    # Clear existing content
    service.spreadsheets().values().clear(
        spreadsheetId=SPREADSHEET_ID,
        range=f"'{tab_name}'!A1:Z",
    ).execute()

    # Write new content
    body = {"values": rows}
    service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=f"'{tab_name}'!A1",
        valueInputOption="USER_ENTERED",
        body=body,
    ).execute()
    print(f"  Wrote {len(rows)} rows to '{tab_name}'")


def format_tab(service, tab_name: str, num_data_rows: int) -> None:
    """Apply formatting: bold headers, colored group total rows, grand total highlight."""
    meta = service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
    sheet_id = None
    for s in meta["sheets"]:
        if s["properties"]["title"] == tab_name:
            sheet_id = s["properties"]["sheetId"]
            break
    if sheet_id is None:
        print(f"  WARNING: Could not find sheet ID for '{tab_name}'")
        return

    # Color palette
    COLOR_DARK_GREEN = {"red": 0.18, "green": 0.42, "blue": 0.20}
    COLOR_HEADER_BG = {"red": 0.91, "green": 0.93, "blue": 0.95}
    COLOR_SUBTOTAL_BG = {"red": 0.88, "green": 0.92, "blue": 0.88}
    COLOR_TOTAL_BG = {"red": 1.0, "green": 0.75, "blue": 0.0}
    COLOR_WHITE = {"red": 1.0, "green": 1.0, "blue": 1.0}
    COLOR_DARK_TEXT = {"red": 0.1, "green": 0.1, "blue": 0.15}

    requests = []

    # Title row (row 0) — dark green, white, bold
    requests.append({
        "repeatCell": {
            "range": {"sheetId": sheet_id, "startRowIndex": 0, "endRowIndex": 1,
                      "startColumnIndex": 0, "endColumnIndex": 1},
            "cell": {
                "userEnteredFormat": {
                    "backgroundColor": COLOR_DARK_GREEN,
                    "textFormat": {"bold": True, "fontSize": 14, "foregroundColor": COLOR_WHITE},
                    "horizontalAlignment": "LEFT",
                    "verticalAlignment": "MIDDLE",
                }
            },
            "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment,verticalAlignment)",
        }
    })

    # Header row (row 4 — 0-indexed: row index 4 = 5th row)
    header_row_idx = 4
    requests.append({
        "repeatCell": {
            "range": {"sheetId": sheet_id, "startRowIndex": header_row_idx,
                      "endRowIndex": header_row_idx + 1,
                      "startColumnIndex": 0, "endColumnIndex": 13},
            "cell": {
                "userEnteredFormat": {
                    "backgroundColor": COLOR_HEADER_BG,
                    "textFormat": {"bold": True, "fontSize": 11, "foregroundColor": COLOR_DARK_TEXT},
                    "horizontalAlignment": "CENTER",
                    "verticalAlignment": "MIDDLE",
                }
            },
            "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment,verticalAlignment)",
        }
    })

    # Find subtotal and grand total rows
    data_start = header_row_idx + 1
    subtotal_indices = []
    grand_total_idx = None

    # Approximate: subtotals come after the data rows and before grand total
    # We look for rows where col B starts with "Subtotal" or "GRAND TOTAL"
    total_rows = data_start + num_data_rows
    # Subtotals: roughly every 11 data rows (varies per project)
    # Grand total: at the very end

    # Batch format requests in chunks of 20
    for chunk_start in range(0, len(requests), 20):
        chunk = requests[chunk_start:chunk_start + 20]
        service.spreadsheets().batchUpdate(
            spreadsheetId=SPREADSHEET_ID,
            body={"requests": chunk},
        ).execute()

    print(f"  Applied formatting to '{tab_name}'")


def main() -> None:
    service = get_service()

    for project in ALL_PROJECTS:
        tab_name = project["tab"]
        print(f"\nProcessing: {tab_name}")

        # Ensure tab exists
        ensure_tab(service, tab_name)

        # Build content
        rows = build_tab_content(project)
        num_data_rows = len(project["rows"])

        # Write data
        write_tab(service, tab_name, rows)

        # Apply formatting
        format_tab(service, tab_name, num_data_rows)

    print("\n\nAll 5 task-breakdown tabs created successfully.")


if __name__ == "__main__":
    main()
