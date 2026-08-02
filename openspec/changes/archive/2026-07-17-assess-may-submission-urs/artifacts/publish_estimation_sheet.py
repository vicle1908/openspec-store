"""Publish estimation sheet to Google Sheets using team methodology.

Methodology (aligned with WM-1760 team reference):
- Per screen: 1P base man-day estimate
- Platform multiplier: x2 for mobile (iOS + Android)
- Coordination overhead: ~15% added to platform total
- Final 2P estimate: 2 x 1P base (parallel streams assumption)
- "Use AI" reduction factor: ~0.65 of Final 2P (agent-assisted coding)
- Solution Design, Unit Test, Performance/Transition as separate line items
- Buffer applied on top of Use AI total:
  - Dev: 30% buffer (scope uncertainty, rework)
  - QA: 20% buffer (test scenario uncertainty)
- Final MD displayed only (no raw/buffered breakdown)
- Hours per MD: 8h
- Sprint = 10 working days

Capacity (from Person Capacity sheet, conservative):
- Dev capacity: ~50 MD/sprint (10 devs, not 100% allocated)
- QA capacity: ~21 MD/sprint (7 QAs)
"""

import os
import sys

sys.path.insert(0, "/Users/lekhanhvinh/Developer/tdt/tdt-meta")
sys.path.insert(0, "/Users/lekhanhvinh/Developer/tdt/.venv/lib/python3.14/site-packages")

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

# ---------------- Config ----------------

SPREADSHEET_ID = "1_MIasMUIaDwauGsmSIQPiC7allQLDOxm9aW_t5a2vbk"
CREDS_PATH = os.path.expanduser("~/.tdt/philip-project-1-496009-aecd4c291640.json")
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

HOURS_PER_MD = 8
DEV_BUFFER = 0.30
QA_BUFFER = 0.20
PLATFORM_MULTIPLIER = 2.0  # iOS + Android
COORD_OVERHEAD = 0.15
USE_AI_FACTOR = 0.65

# Conservative team capacity per sprint (10 working days)
DEV_MD_PER_SPRINT = 50.0
QA_MD_PER_SPRINT = 21.0

# Capacity assumption for timeline (used to compute sprints)
EFFECTIVE_DEV_MD_PER_SPRINT = 40.0  # leave room for support/BA/meetings

# ---------------- Helpers ----------------


def md(hours):
    return round(hours / HOURS_PER_MD, 2)


def dev_line(screen_label, base_1p_md, coordination=True):
    """Compute dev MD per line using team methodology.

    Steps:
      - platform_md = base_1p_md * PLATFORM_MULTIPLIER
      - coordination_md = platform_md * COORD_OVERHEAD (if coordination=True)
      - final_2p_md = base_1p_md * 2  (parallel streams)
      - use_ai_md = final_2p_md * USE_AI_FACTOR
      - total_dev_md = use_ai_md (unbuffered)
      - buffered_dev_md = total_dev_md * (1 + DEV_BUFFER)
    """
    platform_md = base_1p_md * PLATFORM_MULTIPLIER
    coord_md = platform_md * COORD_OVERHEAD if coordination else 0.0
    final_2p_md = base_1p_md * 2.0
    use_ai_md = final_2p_md * USE_AI_FACTOR
    # Return buffered MD (what we display)
    return round(use_ai_md * (1 + DEV_BUFFER), 2)


def qa_line(screen_label, base_1p_md):
    """QA: typically 30-40% of dev effort, with QA buffer."""
    qa_base = base_1p_md * 0.35
    return round(qa_base * (1 + QA_BUFFER), 2)


# ---------------- Project definitions ----------------
# Each project contains: name, list of (feature_group, screen_label, base_1p_md)
# base_1p_md = estimated man-days for 1 person to deliver this screen end-to-end
# (excluding platform multiplier).

PROJECTS = {
    "PROJ-001 — Blood Test Result": {
        "tab": "Blood Test Result",
        "complexity": "Medium",
        "screens": [
            ("Result List", "BTR-01: Result List Screen (filter, sort, search)", 1.5),
            ("Result List", "BTR-02: Test Detail Screen (slide tabs: Info/Values/Notes)", 2.0),
            ("Result List", "BTR-03: Comparison View (side-by-side 2 visits)", 2.0),
            ("Result List", "BTR-04: Filter/Date Range Picker", 1.0),
            ("Booking", "BTR-05: Book Appointment Screen", 1.5),
            ("Booking", "BTR-06: Slot Selection / Confirmation", 1.5),
            ("Booking", "BTR-07: Booking Success Screen", 0.5),
            ("Notifications", "BTR-08: Notification Center", 1.5),
            ("Notifications", "BTR-09: Push Notification Handler (deep link)", 1.0),
            ("Profile", "BTR-10: Patient Profile Screen", 1.0),
            ("Profile", "BTR-11: Edit Profile Screen", 1.0),
            ("Profile", "BTR-12: Family Member Management", 1.5),
            ("Settings", "BTR-13: Settings Screen (language, theme, notifications)", 1.0),
            ("Settings", "BTR-14: About / Help / Privacy Policy", 0.5),
            ("Auth", "BTR-15: Login / OTP Screen", 1.0),
            ("Auth", "BTR-16: Biometric Login Setup", 0.5),
            ("Onboarding", "BTR-17: Onboarding Flow (3-4 intro screens)", 1.0),
            ("Onboarding", "BTR-18: Permission Requests (camera, location, notif)", 0.5),
            ("Backend", "BTR-API-01: API Integration Layer (endpoints, models)", 2.0),
            ("Backend", "BTR-API-02: Auth Token Refresh / Secure Storage", 1.0),
            ("Backend", "BTR-API-03: Offline Cache + Sync Logic", 2.0),
            ("Test Data", "BTR-TD-01: Test Data Set (sample visits, results)", 0.5),
            ("Bug Fix", "BTR-BF-01: Bug Fix Buffer (assumed 10% of screens)", 2.0),
        ],
    },
    "PROJ-002 — Chronic Care Tracking": {
        "tab": "Chronic Care",
        "complexity": "High",
        "screens": [
            ("Dashboard", "CCT-01: Chronic Patient Dashboard (overview, KPIs)", 2.5),
            ("Dashboard", "CCT-02: KPI Card Component (blood pressure, glucose, weight)", 1.5),
            ("Dashboard", "CCT-03: Trend Chart Component (line/area, 7/30/90 day)", 2.0),
            ("Vitals", "CCT-04: Vitals Entry Form Screen", 2.0),
            ("Vitals", "CCT-05: Vitals History List Screen", 1.5),
            ("Vitals", "CCT-06: Vitals Detail Screen", 1.5),
            ("Vitals", "CCT-07: Manual Entry + Photo OCR Capture", 3.0),
            ("Vitals", "CCT-08: Reminder/Schedule Setup Screen", 1.5),
            ("Vitals", "CCT-09: Medication Schedule Screen", 2.0),
            ("Vitals", "CCT-10: Medication Reminder Screen", 1.0),
            ("Reports", "CCT-11: Report Generation Screen (PDF export)", 2.0),
            ("Reports", "CCT-12: Share/Email Report Flow", 1.0),
            ("Reports", "CCT-13: Doctor Visit Summary View", 2.0),
            ("Profile", "CCT-14: Care Team Management Screen", 1.5),
            ("Profile", "CCT-15: Goal Setting Screen (target BP/glucose/weight)", 1.5),
            ("Profile", "CCT-16: Health Goal Progress Screen", 1.0),
            ("Notifications", "CCT-17: Alert/Threshold Notification Logic", 2.0),
            ("Notifications", "CCT-18: Notification Preferences Screen", 1.0),
            ("Auth", "CCT-19: Patient Login + Family Linking", 1.0),
            ("Onboarding", "CCT-20: Chronic Patient Onboarding Flow", 1.5),
            ("Backend", "CCT-API-01: Vitals API Integration", 2.0),
            ("Backend", "CCT-API-02: Report Generation Service", 2.0),
            ("Backend", "CCT-API-03: Notification Scheduling Service", 1.5),
            ("Backend", "CCT-API-04: Offline Data Sync (conflicts, retry)", 2.5),
            ("Backend", "CCT-API-05: OCR Result Validation API", 1.5),
            ("Test Data", "CCT-TD-01: Test Patient Dataset (3 chronic profiles)", 1.0),
            ("Bug Fix", "CCT-BF-01: Bug Fix Buffer (15% of dev effort — high complexity)", 4.0),
        ],
    },
    "PROJ-003 — Tele-consultation Chat": {
        "tab": "Tele-consult Chat",
        "complexity": "High",
        "screens": [
            ("Chat", "TCC-01: Chat List Screen (conversations list)", 1.5),
            ("Chat", "TCC-02: Chat Thread Screen (message bubbles, typing indicator)", 3.0),
            ("Chat", "TCC-03: Message Composer (text, attachments, voice)", 2.5),
            ("Chat", "TCC-04: Attachment Preview / Send Screen", 1.5),
            ("Chat", "TCC-05: Voice Message Recorder + Player", 2.5),
            ("Chat", "TCC-06: Image Picker + Camera Capture", 1.5),
            ("Chat", "TCC-07: File Upload + Progress Indicator", 1.5),
            ("Chat", "TCC-08: Message Search Screen", 1.0),
            ("Chat", "TCC-09: Pinned Messages Screen", 1.0),
            ("Video Call", "TCC-10: Video Call Lobby Screen", 2.0),
            ("Video Call", "TCC-11: Active Video Call UI (controls, layout)", 3.5),
            ("Video Call", "TCC-12: Picture-in-Picture Mode", 1.5),
            ("Video Call", "TCC-13: Call History Screen", 1.5),
            ("Video Call", "TCC-14: Call Quality Indicator + Diagnostics", 1.5),
            ("Notifications", "TCC-15: Push Notification Handler (chat + call)", 1.5),
            ("Notifications", "TCC-16: In-App Banner Notification", 1.0),
            ("Notifications", "TCC-17: Notification Settings Screen", 0.5),
            ("Profile", "TCC-18: Doctor Profile Screen (in chat header)", 1.0),
            ("Profile", "TCC-19: Patient Profile Screen", 1.0),
            ("Auth", "TCC-20: Login + Session Management", 1.0),
            ("Onboarding", "TCC-21: Onboarding + Permission Setup", 1.0),
            ("Backend", "TCC-API-01: WebSocket/Realtime Messaging Backend", 3.0),
            ("Backend", "TCC-API-02: File Upload Service (chunked, resume)", 2.0),
            ("Backend", "TCC-API-03: Video Call Signaling (WebRTC/SFU)", 3.5),
            ("Backend", "TCC-API-04: Message Persistence + Sync", 2.0),
            ("Backend", "TCC-API-05: Push Notification Service Integration (FCM/APNs)", 1.5),
            ("Test Data", "TCC-TD-01: Test Conversations (text, image, voice, file)", 1.0),
            ("Bug Fix", "TCC-BF-01: Bug Fix Buffer (15% — WebRTC + realtime complexity)", 4.0),
        ],
    },
    "PROJ-004 — Smart Booking": {
        "tab": "Smart Booking",
        "complexity": "Medium",
        "screens": [
            ("Booking", "SMB-01: Smart Booking Home Screen", 1.5),
            ("Booking", "SMB-02: Doctor Search Screen (specialty, name, location)", 2.0),
            ("Booking", "SMB-03: Doctor List Screen (sortable, filterable)", 1.5),
            ("Booking", "SMB-04: Doctor Profile Screen (info, reviews, slots)", 2.0),
            ("Booking", "SMB-05: Slot Selection Calendar", 2.0),
            ("Booking", "SMB-06: Time Slot Picker (morning/afternoon/evening)", 1.5),
            ("Booking", "SMB-07: Booking Confirmation Screen", 1.0),
            ("Booking", "SMB-08: Booking Success + Add to Calendar", 1.0),
            ("Booking", "SMB-09: Recurring Booking Setup", 2.0),
            ("Booking", "SMB-10: Family Member Booking (multi-patient)", 2.0),
            ("Booking", "SMB-11: Insurance/TPA Selection Screen", 1.5),
            ("Booking", "SMB-12: Pre-visit Questionnaire Screen", 1.5),
            ("Booking", "SMB-13: Reschedule Booking Flow", 1.5),
            ("Booking", "SMB-14: Cancel Booking + Reason Screen", 1.0),
            ("Booking", "SMB-15: Waitlist / Smart Slot Suggestion", 2.5),
            ("My Bookings", "SMB-16: My Bookings List Screen", 1.5),
            ("My Bookings", "SMB-17: Upcoming Booking Detail", 1.0),
            ("My Bookings", "SMB-18: Past Booking Detail + Review", 1.0),
            ("My Bookings", "SMB-19: Booking Reminder Screen", 0.5),
            ("Notifications", "SMB-20: Booking Confirmation Push", 0.5),
            ("Notifications", "SMB-21: Reminder Push (24h, 1h before)", 1.0),
            ("Profile", "SMB-22: Patient Profile + Medical History", 1.5),
            ("Profile", "SMB-23: Insurance Card Upload Screen", 1.0),
            ("Auth", "SMB-24: Login + Patient Verification", 1.0),
            ("Onboarding", "SMB-25: Smart Booking Onboarding", 1.0),
            ("Backend", "SMB-API-01: Doctor Search + Filter API", 2.0),
            ("Backend", "SMB-API-02: Slot Availability Real-time Service", 2.5),
            ("Backend", "SMB-API-03: Booking Creation + Hold Logic", 2.0),
            ("Backend", "SMB-API-04: Calendar Integration (Google/Outlook/iCal)", 1.5),
            ("Backend", "SMB-API-05: Insurance Verification Service", 2.0),
            ("Backend", "SMB-API-06: Waitlist + Auto-book Service", 2.0),
            ("Test Data", "SMB-TD-01: Doctor/Patient/Slot Test Data", 1.0),
            ("Bug Fix", "SMB-BF-01: Bug Fix Buffer (12% — booking flow complexity)", 3.0),
        ],
    },
    "PROJ-005 — Imaging & Diagnostics": {
        "tab": "Imaging Diagnostics",
        "complexity": "Medium",
        "screens": [
            ("Imaging List", "IMD-01: Imaging Study List Screen (X-ray, MRI, CT)", 1.5),
            ("Imaging List", "IMD-02: Imaging Study Detail Screen", 1.5),
            ("Imaging List", "IMD-03: Filter/Sort Imaging Studies", 1.0),
            ("Viewer", "IMD-04: DICOM Image Viewer Screen", 4.0),
            ("Viewer", "IMD-05: Image Annotation / Measurement Tools", 3.0),
            ("Viewer", "IMD-06: Multi-series Comparison View", 3.0),
            ("Viewer", "IMD-07: Zoom/Pan/Window/Level Controls", 2.5),
            ("Reports", "IMD-08: Radiology Report Screen (text + annotated images)", 2.0),
            ("Reports", "IMD-09: Report Download (PDF) + Share", 1.0),
            ("Reports", "IMD-10: Report Comparison View (current vs prior)", 2.0),
            ("Reports", "IMD-11: AI-Generated Insights Overlay", 3.0),
            ("Booking", "IMD-12: Imaging Appointment Booking", 1.5),
            ("Booking", "IMD-13: Pre-imaging Instructions Screen", 1.0),
            ("Upload", "IMD-14: External Scan Upload Screen", 2.0),
            ("Upload", "IMD-15: Upload Progress + Error Handling", 1.0),
            ("Notifications", "IMD-16: Imaging Ready Notification", 0.5),
            ("Notifications", "IMD-17: Critical Finding Alert Screen", 1.5),
            ("Profile", "IMD-18: Patient Profile + Imaging History", 1.0),
            ("Auth", "IMD-19: Login + Patient Verification", 0.5),
            ("Onboarding", "IMD-20: Imaging Module Onboarding", 0.5),
            ("Backend", "IMD-API-01: DICOM Streaming Server Integration", 3.0),
            ("Backend", "IMD-API-02: Imaging Study Metadata API", 1.5),
            ("Backend", "IMD-API-03: Report Generation + PDF Service", 2.0),
            ("Backend", "IMD-API-04: AI Inference Service Integration", 3.0),
            ("Backend", "IMD-API-05: Secure Upload + Virus Scan", 1.5),
            ("Test Data", "IMD-TD-01: Sample DICOM Studies (3 modalities)", 1.0),
            ("Bug Fix", "IMD-BF-01: Bug Fix Buffer (12% — viewer + DICOM complexity)", 3.5),
        ],
    },
    "PROJ-006 — Lab Booking": {
        "tab": "Lab Booking",
        "complexity": "Medium",
        "screens": [
            ("Lab List", "LBK-01: Lab Test Catalog Screen", 1.5),
            ("Lab List", "LBK-02: Test Detail Screen (description, prep, price)", 1.5),
            ("Lab List", "LBK-03: Package Builder Screen (combine tests)", 2.0),
            ("Lab List", "LBK-04: Search/Filter Tests", 1.0),
            ("Booking", "LBK-05: Home Sample Collection Booking", 1.5),
            ("Booking", "LBK-06: Visit Lab Booking", 1.5),
            ("Booking", "LBK-07: Date/Time Picker Screen", 1.0),
            ("Booking", "LBK-08: Address Selection/Entry (for home collection)", 1.5),
            ("Booking", "LBK-09: Phlebotomist Assignment View", 1.0),
            ("Booking", "LBK-10: Booking Confirmation Screen", 1.0),
            ("Booking", "LBK-11: Booking Success Screen", 0.5),
            ("Payment", "LBK-12: Payment Screen (Card, Wallet, COD)", 2.0),
            ("Payment", "LBK-13: Insurance/Cashless Option", 1.5),
            ("Payment", "LBK-14: Payment Success Screen", 0.5),
            ("Payment", "LBK-15: Refund Screen (post-cancel)", 1.0),
            ("Tracking", "LBK-16: Phlebotomist Tracking Screen (real-time map)", 3.0),
            ("Tracking", "LBK-17: ETA + Status Updates Screen", 1.0),
            ("Tracking", "LBK-18: Sample Collection Confirmation", 0.5),
            ("My Bookings", "LBK-19: My Lab Bookings List", 1.0),
            ("My Bookings", "LBK-20: Booking Detail Screen", 1.0),
            ("My Bookings", "LBK-21: Reschedule/Cancel Booking Flow", 1.5),
            ("Reports", "LBK-22: Link Lab Result from Lab Booking", 1.0),
            ("Notifications", "LBK-23: Booking Confirmation Push", 0.5),
            ("Notifications", "LBK-24: Phlebotomist On-the-Way Push", 1.0),
            ("Notifications", "LBK-25: Result Ready Push", 0.5),
            ("Profile", "LBK-26: Patient Profile + Address Book", 1.0),
            ("Auth", "LBK-27: Login + Patient Verification", 0.5),
            ("Onboarding", "LBK-28: Lab Booking Onboarding", 0.5),
            ("Backend", "LBK-API-01: Lab Catalog API", 1.5),
            ("Backend", "LBK-API-02: Slot/Availability Service", 2.0),
            ("Backend", "LBK-API-03: Phlebotomist Dispatch Service", 2.5),
            ("Backend", "LBK-API-04: Real-time Tracking Service", 2.0),
            ("Backend", "LBK-API-05: Payment Gateway Integration", 2.0),
            ("Backend", "LBK-API-06: Result Linking Service", 1.0),
            ("Test Data", "LBK-TD-01: Test Lab Catalog + Sample Bookings", 1.0),
            ("Bug Fix", "LBK-BF-01: Bug Fix Buffer (10% — moderate complexity)", 3.0),
        ],
    },
    "PROJ-007 — Health Wallet": {
        "tab": "Health Wallet",
        "complexity": "High",
        "screens": [
            ("Wallet Home", "HLW-01: Health Wallet Home Screen", 2.0),
            ("Wallet Home", "HLW-02: Document Count + Storage Indicator", 1.0),
            ("Documents", "HLW-03: Document Library Screen (categorized list)", 2.0),
            ("Documents", "HLW-04: Document Detail Screen (preview + metadata)", 2.0),
            ("Documents", "HLW-05: Document Filter/Tag Screen", 1.5),
            ("Documents", "HLW-06: Document Search Screen (OCR-based)", 2.5),
            ("Upload", "HLW-07: Document Upload Screen (camera + file picker)", 2.0),
            ("Upload", "HLW-08: OCR Scan Flow + Auto-tagging", 3.5),
            ("Upload", "HLW-09: Manual Document Entry Screen", 1.5),
            ("Upload", "HLW-10: Bulk Upload Screen", 1.5),
            ("Sharing", "HLW-11: Share Document with Doctor Screen", 2.0),
            ("Sharing", "HLW-12: Share Document with Family Screen", 1.5),
            ("Sharing", "HLW-13: Time-limited Share Link Generation", 1.5),
            ("Sharing", "HLW-14: Shared With Me Screen", 1.5),
            ("Sharing", "HLW-15: Access Permissions Management", 1.5),
            ("Sharing", "HLW-16: Share Expiry/Revoke Screen", 1.0),
            ("Insurance", "HLW-17: Insurance Card Storage Screen", 1.5),
            ("Insurance", "HLW-18: Insurance Claim Document Upload", 2.0),
            ("Insurance", "HLW-19: Claim Status Tracking Screen", 1.5),
            ("Profile", "HLW-20: Patient Profile + Medical History", 1.5),
            ("Profile", "HLW-21: Family Member Linking (for minor dependents)", 1.5),
            ("Auth", "HLW-22: Login + Biometric Auth for Wallet", 1.0),
            ("Auth", "HLW-23: PIN/Password Setup for Wallet Access", 1.0),
            ("Onboarding", "HLW-24: Health Wallet Onboarding + Permission Setup", 1.0),
            ("Backend", "HLW-API-01: Document Storage + Encryption Service", 3.0),
            ("Backend", "HLW-API-02: OCR + Auto-tagging Service", 3.5),
            ("Backend", "HLW-API-03: Document Search Index", 2.0),
            ("Backend", "HLW-API-04: Secure Share Link Service (signed URLs)", 2.0),
            ("Backend", "HLW-API-05: Family Permission Service", 1.5),
            ("Backend", "HLW-API-06: Audit Log Service (PHI access tracking)", 2.0),
            ("Test Data", "HLW-TD-01: Sample Documents (lab, imaging, prescription)", 1.0),
            ("Bug Fix", "HLW-BF-01: Bug Fix Buffer (15% — encryption + OCR complexity)", 4.0),
        ],
    },
    "PROJ-008 — Unified Patient Timeline": {
        "tab": "Unified Timeline",
        "complexity": "High",
        "screens": [
            ("Timeline", "UPT-01: Unified Timeline Home Screen", 3.0),
            ("Timeline", "UPT-02: Timeline Event Card Component (multi-type)", 2.0),
            ("Timeline", "UPT-03: Chronological/Ranked View Toggle", 1.5),
            ("Timeline", "UPT-04: Timeline Filter Screen (event type, date, source)", 2.0),
            ("Timeline", "UPT-05: Timeline Search Screen (keyword)", 2.0),
            ("Timeline", "UPT-06: Event Detail Drawer/Modal", 2.0),
            ("Timeline", "UPT-07: Multi-source Event Aggregation Logic", 3.0),
            ("Aggregation", "UPT-08: Lab Result Event Aggregator", 2.0),
            ("Aggregation", "UPT-09: Imaging Event Aggregator", 2.0),
            ("Aggregation", "UPT-10: Booking Event Aggregator", 1.5),
            ("Aggregation", "UPT-11: Consultation Event Aggregator", 1.5),
            ("Aggregation", "UPT-12: Prescription Event Aggregator", 1.5),
            ("Aggregation", "UPT-13: Vitals Event Aggregator", 1.5),
            ("Aggregation", "UPT-14: Wallet Document Event Aggregator", 1.5),
            ("Insights", "UPT-15: AI-Generated Insight Cards", 3.0),
            ("Insights", "UPT-16: Pattern/Anomaly Detection View", 3.5),
            ("Insights", "UPT-17: Trend Insights + Recommendations", 2.5),
            ("Sharing", "UPT-18: Share Timeline with Doctor (read-only link)", 2.0),
            ("Sharing", "UPT-19: Timeline Export (PDF)", 1.5),
            ("Sharing", "UPT-20: Doctor View of Patient Timeline", 2.0),
            ("Profile", "UPT-21: Patient Profile + Linked Sources", 1.0),
            ("Profile", "UPT-22: Data Source Connection Management", 2.0),
            ("Profile", "UPT-23: Privacy/Consent Management Screen", 1.5),
            ("Auth", "UPT-24: Login + Patient Verification", 0.5),
            ("Onboarding", "UPT-25: Timeline Onboarding + Source Connect", 1.0),
            ("Backend", "UPT-API-01: Event Aggregation Service (event bus)", 3.5),
            ("Backend", "UPT-API-02: Timeline Query/Render API", 2.5),
            ("Backend", "UPT-API-03: AI Insight Generation Service", 3.5),
            ("Backend", "UPT-API-04: Pattern/Anomaly Detection Model", 4.0),
            ("Backend", "UPT-API-05: Cross-source Data Sync Service", 3.0),
            ("Backend", "UPT-API-06: Consent/Audit Service", 2.0),
            ("Test Data", "UPT-TD-01: Multi-source Test Events (12 months of data)", 1.5),
            ("Bug Fix", "UPT-BF-01: Bug Fix Buffer (15% — high cross-module complexity)", 4.0),
        ],
    },
}


# ---------------- Project metadata for dashboard ----------------

PROJECT_META = {
    "PROJ-001 — Blood Test Result": {
        "team": "Mobile Core",
        "lead": "TBD",
        "priority": "P0",
        "start": "Q3-2026",
        "duration_sprints": 3,
        "dependents": [],
        "phase": "Dev",
    },
    "PROJ-002 — Chronic Care Tracking": {
        "team": "Mobile Core",
        "lead": "TBD",
        "priority": "P0",
        "start": "Q3-2026",
        "duration_sprints": 6,
        "dependents": [],
        "phase": "Dev",
    },
    "PROJ-003 — Tele-consultation Chat": {
        "team": "Mobile Engagement",
        "lead": "TBD",
        "priority": "P0",
        "start": "Q3-2026",
        "duration_sprints": 7,
        "dependents": ["PROJ-008"],
        "phase": "Dev",
    },
    "PROJ-004 — Smart Booking": {
        "team": "Mobile Engagement",
        "lead": "TBD",
        "priority": "P1",
        "start": "Q4-2026",
        "duration_sprints": 6,
        "dependents": ["PROJ-008"],
        "phase": "Plan",
    },
    "PROJ-005 — Imaging & Diagnostics": {
        "team": "Mobile Core",
        "lead": "TBD",
        "priority": "P1",
        "start": "Q4-2026",
        "duration_sprints": 5,
        "dependents": ["PROJ-008"],
        "phase": "Plan",
    },
    "PROJ-006 — Lab Booking": {
        "team": "Mobile Engagement",
        "lead": "TBD",
        "priority": "P1",
        "start": "Q4-2026",
        "duration_sprints": 6,
        "dependents": ["PROJ-008"],
        "phase": "Plan",
    },
    "PROJ-007 — Health Wallet": {
        "team": "Mobile Core",
        "lead": "TBD",
        "priority": "P0",
        "start": "Q3-2026",
        "duration_sprints": 6,
        "dependents": ["PROJ-008"],
        "phase": "Dev",
    },
    "PROJ-008 — Unified Patient Timeline": {
        "team": "Mobile Core",
        "lead": "TBD",
        "priority": "P0",
        "start": "Q4-2026",
        "duration_sprints": 7,
        "dependents": ["PROJ-003", "PROJ-004", "PROJ-005", "PROJ-006", "PROJ-007"],
        "phase": "Plan",
    },
}


# ---------------- Compute project totals ----------------


def compute_project_totals(screens):
    """Compute dev + QA totals for a project, applying team methodology."""
    dev_total = 0.0
    qa_total = 0.0
    breakdown = []
    for group, label, base_1p_md in screens:
        d = dev_line(label, base_1p_md)
        q = qa_line(label, base_1p_md)
        dev_total += d
        qa_total += q
        breakdown.append((group, label, d, q, base_1p_md))
    # Solution Design + Unit Test + Performance/Transition as separate overhead
    # Team reference: ~10% of dev for solution design, ~8% for unit test setup,
    # ~5% for performance/transition
    solution_design = round(dev_total * 0.10 * (1 + DEV_BUFFER), 2)
    unit_test_overhead = round(dev_total * 0.08 * (1 + DEV_BUFFER), 2)
    perf_transition = round(dev_total * 0.05 * (1 + DEV_BUFFER), 2)
    overhead_total = solution_design + unit_test_overhead + perf_transition
    return {
        "dev_screen_total": round(dev_total, 2),
        "qa_screen_total": round(qa_total, 2),
        "solution_design": solution_design,
        "unit_test": unit_test_overhead,
        "perf_transition": perf_transition,
        "dev_overhead": round(overhead_total, 2),
        "dev_total": round(dev_total + overhead_total, 2),
        "qa_total": round(qa_total * (1 + QA_BUFFER), 2),  # buffer already in qa_line
        "breakdown": breakdown,
    }


# ---------------- Build sheet rows ----------------


def build_project_rows(project_key, project_data, totals):
    """Build all rows for a project tab including subtotals and sprints."""
    rows = []
    # Header row
    rows.append([f"{project_key} — Estimation (Team Methodology)"])
    rows.append([f"Complexity: {project_data['complexity']}"])
    rows.append([
        "Methodology: 1P base x Platform x2 / Coordination 15% / Final 2P x2 / Use AI 0.65 / +30% dev buffer / +20% QA buffer"
    ])
    rows.append([
        "Capacity assumption: Dev 50 MD/sprint (conservative), QA 21 MD/sprint, Sprint = 10 working days"
    ])
    rows.append([])
    rows.append(["#", "Feature Group", "Screen / Component", "Base 1P (MD)", "Dev (MD)", "QA (MD)"])

    for i, (group, label, d, q, base) in enumerate(totals["breakdown"], 1):
        rows.append([i, group, label, base, d, q])

    # Subtotal: screens
    rows.append([])
    rows.append([
        "",
        "Screens Subtotal",
        f"{len(totals['breakdown'])} screens/components",
        "",
        totals["dev_screen_total"],
        totals["qa_screen_total"],
    ])
    # Solution Design
    rows.append(["", "Overhead", "Solution Design (architecture, API contract, data model)", "", totals["solution_design"], 0])
    rows.append(["", "Overhead", "Unit Test Framework Setup + Test Suite", "", totals["unit_test"], 0])
    rows.append(["", "Overhead", "Performance Profiling + Staging Deploy + Transition", "", totals["perf_transition"], 0])
    # Total
    rows.append([])
    rows.append(["", "TOTAL", "Dev (with buffer) / QA (with buffer)", "", totals["dev_total"], totals["qa_total"]])
    rows.append([])
    # Sprint capacity check
    dev_sprints = totals["dev_total"] / EFFECTIVE_DEV_MD_PER_SPRINT
    qa_sprints = totals["qa_total"] / QA_MD_PER_SPRINT
    rows.append([
        "",
        "Sprint Capacity",
        f"Dev sprints @ {EFFECTIVE_DEV_MD_PER_SPRINT} MD/sprint: {dev_sprints:.1f}",
    ])
    rows.append([
        "",
        "Sprint Capacity",
        f"QA sprints @ {QA_MD_PER_SPRINT} MD/sprint: {qa_sprints:.1f}",
    ])
    return rows


def build_summary_rows(all_totals):
    rows = []
    rows.append(["Mobile App Module Estimation Summary (Team Methodology)"])
    rows.append([
        "Methodology: 1P x Platform x2 / Coordination 15% / Final 2P / Use AI 0.65 / +30% dev buffer / +20% QA buffer"
    ])
    rows.append(["Capacity: Dev 50 MD/sprint (conservative), QA 21 MD/sprint, Sprint = 10 working days"])
    rows.append([])
    rows.append([
        "Project",
        "Complexity",
        "# Screens",
        "Dev Total (MD)",
        "QA Total (MD)",
        "Dev Sprints",
        "QA Sprints",
        "Proposed Sprints",
        "Phase",
        "Priority",
    ])
    total_dev = 0.0
    total_qa = 0.0
    for project_key, project_data in PROJECTS.items():
        meta = PROJECT_META[project_key]
        t = all_totals[project_key]
        total_dev += t["dev_total"]
        total_qa += t["qa_total"]
        dev_sp = t["dev_total"] / EFFECTIVE_DEV_MD_PER_SPRINT
        qa_sp = t["qa_total"] / QA_MD_PER_SPRINT
        rows.append([
            project_key,
            project_data["complexity"],
            len(t["breakdown"]),
            t["dev_total"],
            t["qa_total"],
            round(dev_sp, 1),
            round(qa_sp, 1),
            meta["duration_sprints"],
            meta["phase"],
            meta["priority"],
        ])
    rows.append([])
    rows.append(["ALL PROJECTS TOTAL", "", "", round(total_dev, 2), round(total_qa, 2), "", "", "", "", ""])
    total_dev_sp = total_dev / EFFECTIVE_DEV_MD_PER_SPRINT
    total_qa_sp = total_qa / QA_MD_PER_SPRINT
    rows.append([
        f"Total sprints @ {EFFECTIVE_DEV_MD_PER_SPRINT} dev / {QA_MD_PER_SPRINT} QA per sprint:",
        "",
        "",
        "",
        "",
        round(total_dev_sp, 1),
        round(total_qa_sp, 1),
        "",
        "",
        "",
    ])
    rows.append([])
    rows.append(["Parallel execution note (2 dev teams × 50 MD = 100 MD/sprint combined)"])
    parallel_dev_sp = total_dev / 100.0
    parallel_qa_sp = total_qa / 42.0
    rows.append([
        "Sprints needed when 2 teams run in parallel:",
        "",
        "",
        "",
        "",
        round(parallel_dev_sp, 1),
        round(parallel_qa_sp, 1),
        "",
        "",
        "",
    ])
    return rows


def build_dashboard_rows(all_totals):
    rows = []
    rows.append(["Mobile App Module Estimation — Dashboard"])
    rows.append(["As of: 2026-06-24"])
    rows.append(["Team Methodology: 1P base x Platform x2 / Coordination 15% / Final 2P / Use AI 0.65 / +30% dev / +20% QA buffer"])
    rows.append([])
    rows.append(["Capacity Assumption"])
    rows.append(["Dev per sprint (MD)", EFFECTIVE_DEV_MD_PER_SPRINT])
    rows.append(["QA per sprint (MD)", QA_MD_PER_SPRINT])
    rows.append(["Sprint length (working days)", 10])
    rows.append(["Hours per MD", HOURS_PER_MD])
    rows.append([])
    rows.append(["8 Project Modules Overview"])
    rows.append([
        "Project",
        "Team",
        "Priority",
        "Phase",
        "Start",
        "Sprints",
        "Dev (MD)",
        "QA (MD)",
        "Dev sp",
        "QA sp",
        "Dependents",
    ])
    for project_key, project_data in PROJECTS.items():
        meta = PROJECT_META[project_key]
        t = all_totals[project_key]
        dev_sp = t["dev_total"] / EFFECTIVE_DEV_MD_PER_SPRINT
        qa_sp = t["qa_total"] / QA_MD_PER_SPRINT
        rows.append([
            project_key,
            meta["team"],
            meta["priority"],
            meta["phase"],
            meta["start"],
            meta["duration_sprints"],
            t["dev_total"],
            t["qa_total"],
            round(dev_sp, 1),
            round(qa_sp, 1),
            ", ".join(meta["dependents"]) if meta["dependents"] else "—",
        ])
    return rows


# ---------------- Ready_Project_Est extension ----------------


def fmt_md(v):
    """Format a number as a string with 2 decimals (no trailing .0)."""
    if isinstance(v, float) and v.is_integer():
        return str(int(v))
    return f"{v:g}" if isinstance(v, float) else str(v)


def build_new_ready_project_sections():
    """Build the 7 missing URS project sections following the same team methodology
    as the existing 4 sections in Ready_Project_Est.
    Methodology per row: 1P base → Platform x2 → Coordination → Final 2P → Use AI (2P)
    """
    sections = []  # list of (project_name, header_label, [rows])

    def section(name, header, rows):
        # Each row: (function, base, coord, use_ai_old)
        # Compute platform = base * 2; final_2p = platform + coord.
        # Then recompute use_ai based on per-row complexity (15-20% reduction of final_2p).
        computed = []
        for func, base, coord, _use_ai_old in rows:
            platform = round(base * 2, 2)
            final_2p = round(platform + coord, 2)
            use_ai_new = _recompute_use_ai(base, platform, coord, final_2p, func)
            computed.append((func, base, platform, coord, final_2p, use_ai_new))
        sections.append((name, header, computed))

    # ---------- 1. Gami - Amalgamated Trade ----------
    section(
        "Gami - Amalgamated Trade",
        "Gami - Amalgamated Trade (Batch Coupon Credit by Counter)",
        [
            ("Read amalgamated market list from configuration", 0.5, 0.1, 0.5),
            ("Group same-day trades by counter for amalgamated markets", 1.0, 0.2, 1.0),
            ("Apply coupon per counter per day (vs per-trade)", 1.5, 0.3, 1.5),
            ("FIFO ordering with activation status and expiry tiebreakers", 1.5, 0.3, 1.5),
            ("Counter-level application rule", 1.0, 0.2, 1.0),
            ("Batch schedule contract (end-of-day cron)", 1.0, 0.3, 1.0),
            ("GBO credit API integration per batch run", 1.0, 0.3, 1.0),
            ("Reconciliation between applied coupons and credited accounts", 1.5, 0.3, 1.5),
            ("Cutoff and timing rules (edge case: counter receives new coupon mid-batch)", 1.0, 0.2, 1.0),
            ("Exception handling (batch failure, partial credit, retry)", 1.5, 0.3, 1.5),
            ("Audit trail: which coupon → which counter → in what order → credited when", 1.0, 0.2, 1.0),
            ("Configuration approach (DB table vs file vs hard-coded)", 0.5, 0.1, 0.5),
            ("Unit test (FIFO + amalgamation + exception scenarios)", 1.5, 0.0, 1.5),
            ("SIT (batch integration with GBO + coupon engine)", 3.0, 0.0, 3.0),
        ],
    )

    # ---------- 2. Gami - Cash Coupon Global Admin ----------
    section(
        "Gami - Cash Coupon Global Admin",
        "Gami - Cash Coupon Global Admin (Lifecycle + Reconciliation)",
        [
            ("Canonical coupon state model (Activated → Eligible → Redeeming → Credited → Reconciled)", 1.0, 0.2, 1.0),
            ("State labels aligned across P3 app and Global Admin", 0.5, 0.1, 0.5),
            ("GBO error notification contract (failure path, retry, escalation)", 1.5, 0.3, 1.5),
            ("Reconciliation policy: catch uncredited \"Redeemed\" coupons", 1.5, 0.3, 1.5),
            ("External system update timing rule (when state flips, when GBO confirms)", 1.0, 0.2, 1.0),
            ("Admin UI: Approve / Reject coupon before sending to GBO", 1.5, 0.3, 1.5),
            ("Admin UI: Re-trigger credit after failure", 1.0, 0.2, 1.0),
            ("Remove template placeholders (real field names + validation rules)", 0.5, 0.1, 0.5),
            ("Add ownership/system-boundary section (coupon engine vs GBO vs P3 notification)", 0.5, 0.1, 0.5),
            ("Acceptance criteria per state transition", 1.0, 0.1, 1.0),
            ("Unit test (state machine + reconciliation)", 1.5, 0.0, 1.5),
            ("SIT (lifecycle + reconciliation end-to-end)", 3.0, 0.0, 3.0),
        ],
    )

    # ---------- 3. ITSR 330853 Refer A Friend ----------
    section(
        "ITSR 330853 Refer A Friend",
        "ITSR 330853 Refer A Friend (Baseline + CR split)",
        [
            ("Block ineligible clients from generating referral link (CR-1)", 1.0, 0.2, 1.0),
            ("Show in-app prompt for ineligible clients with reason", 0.75, 0.15, 0.75),
            ("Per-enhancement Acceptance Criteria for each CR item", 1.0, 0.1, 1.0),
            ("Duplicate handling: same friend, multiple invites", 0.75, 0.15, 0.75),
            ("Exception path: expired link, friend already-account-holder", 0.5, 0.15, 0.5),
            ("Campaign ownership + authoring role definition", 0.5, 0.1, 0.5),
            ("Glossary + metadata cleanup (terms: invitee, referrer, eligible client)", 0.5, 0.1, 0.5),
            ("Enable/disable feature flag (campaign readiness)", 0.5, 0.2, 0.5),
            ("Unit test (CR scenarios + duplicate + exception)", 1.5, 0.0, 1.5),
            ("SIT (referral flow end-to-end)", 2.5, 0.0, 2.5),
        ],
    )

    # ---------- 4. UT Enhancements - Phase 2 2026 ----------
    section(
        "UT Enhancements - Phase 2 2026",
        "UT Enhancements - Phase 2 2026 (Itemized Backlog)",
        [
            ("Decompose open-ended discovery into itemized backlog (5-7 items)", 1.0, 0.2, 1.0),
            ("Per-item current-state problem statement", 0.5, 0.1, 0.5),
            ("Per-item target-state outcome", 0.5, 0.1, 0.5),
            ("Per-item Acceptance Criteria, ownership, not-in-scope boundary", 1.0, 0.1, 1.0),
            ("Complete template metadata + glossary sections", 0.5, 0.1, 0.5),
            ("Per-item implementation: typical small UT enhancement (3-5 MD per item)", 4.0, 0.5, 4.0),
            ("Cross-item integration test", 1.5, 0.0, 1.5),
            ("SIT (item-by-item UT roundtrip)", 2.0, 0.0, 2.0),
        ],
    )

    # ---------- 5. WM - Accredited Investor Form ----------
    section(
        "WM - Accredited Investor Form",
        "WM - Accredited Investor Form (Native vs Web/Iframe Boundary)",
        [
            ("Define ownership boundary: native shell vs web/iframe", 0.5, 0.1, 0.5),
            ("Clarify which team owns shell, form rendering, backend criteria", 0.5, 0.1, 0.5),
            ("Current-state access model document", 0.5, 0.1, 0.5),
            ("Target-state P3 entry experience (deep link vs embedded)", 1.0, 0.2, 1.0),
            ("Form rendering (native WebView component)", 1.0, 0.2, 1.0),
            ("Backend criteria evaluation API", 1.5, 0.3, 1.5),
            ("Session handoff between native shell and embedded form", 1.0, 0.2, 1.0),
            ("Result return path (form completion → shell status update)", 0.75, 0.15, 0.75),
            ("Acceptance criteria + glossary + metadata", 0.5, 0.1, 0.5),
            ("Unit test (session handoff + form lifecycle)", 1.0, 0.0, 1.0),
            ("SIT (P3 entry → form → shell return)", 2.0, 0.0, 2.0),
        ],
    )

    # ---------- 6. URS - DDA Linking and DDA Deposit ----------
    section(
        "URS - DDA Linking and DDA Deposit",
        "URS - DDA Linking and DDA Deposit (DBS FAST + CIS + GBO Integration)",
        [
            ("DBS FAST API integration (DDA verification + linking)", 3.0, 0.5, 3.0),
            ("CIS system integration (customer identity verification)", 2.0, 0.4, 2.0),
            ("GBO credit on deposit confirmation", 1.5, 0.3, 1.5),
            ("RPS (Referral/Position Sync) integration", 1.5, 0.3, 1.5),
            ("POEMS engine integration (deposit → buying power update)", 2.0, 0.4, 2.0),
            ("Advisory account mapping (S2+UTW, UTW) — confirm with Shawn/Jamie", 0.5, 0.1, 0.5),
            ("Phase 2 delivery order: SynergyBO vs MyWealth", 0.5, 0.1, 0.5),
            ("Finance Report format + delivery mechanism (Katherine + Alvin)", 1.0, 0.2, 1.0),
            ("Performance SLA for DBS API (timeout, retry, backoff)", 1.0, 0.2, 1.0),
            ("Security controls for bank account data (encryption, audit log)", 1.5, 0.3, 1.5),
            ("Ops runbook for async failures (DBS API down, partial confirmation)", 1.0, 0.2, 1.0),
            ("Joint account multi-holder display handling", 1.0, 0.2, 1.0),
            ("NFRs + Acceptance criteria", 0.5, 0.1, 0.5),
            ("Unit test (DBS + CIS + GBO + RPS mocks)", 2.0, 0.0, 2.0),
            ("SIT (DBS sandbox + CIS + GBO + RPS + POEMS end-to-end)", 4.0, 0.0, 4.0),
        ],
    )

    # ---------- 7. URS -POEMS Shareholder Meeting P3 URS ----------
    section(
        "URS -POEMS Shareholder Meeting P3 URS",
        "URS -POEMS Shareholder Meeting P3 (Refinitiv + 72h Free Shares)",
        [
            ("Replace email-only submission with in-app status or API acknowledgment", 2.0, 0.4, 2.0),
            ("Identify owning system for 72-hour free shares calculation; confirm with BA", 0.5, 0.1, 0.5),
            ("72-hour free shares calculation engine", 1.5, 0.3, 1.5),
            ("Withdrawal Admin scope decision: build UI vs manual ops", 1.0, 0.2, 1.0),
            ("Refinitiv data reconciliation for stale/missing data", 2.0, 0.4, 2.0),
            ("Meeting list + agenda screen", 1.0, 0.2, 1.0),
            ("Voting screen (For / Against / Abstain) + submission confirmation", 1.5, 0.3, 1.5),
            ("Free shares redemption screen (72h window display + claim)", 1.0, 0.2, 1.0),
            ("Joint account (3+ holders) display + voting rules", 1.5, 0.3, 1.5),
            ("In-app submission status + audit log", 1.0, 0.2, 1.0),
            ("NFRs + Acceptance criteria + glossary", 0.5, 0.1, 0.5),
            ("Unit test (voting + free shares + reconciliation)", 1.5, 0.0, 1.5),
            ("SIT (Refinitiv mock + voting + free shares end-to-end)", 3.0, 0.0, 3.0),
        ],
    )

    return sections


# ---------------- Per-row AI reduction heuristic (15-20%) ----------------


def _ai_reduction_for(function: str) -> float:
    """Per-row AI reduction rate based on function complexity. Returns fraction (0.16-0.20).

    Heuristic (visible 15-20% range after rounding to 2 decimals):
      - 0.20 (highest): cross-system integration, algorithmic logic, security/encryption,
        external API integration, 3rd-party data reconciliation, full SIT
      - 0.18: state machines, multi-screen orchestration, business rules, ownership/boundary
      - 0.16 (lowest): unit tests, simple UI screens, basic CRUD, config, prompt UX,
        per-item problem/target statements, template metadata cleanup
      - 0.17: default for standard business-logic work

    Note: rates are slightly above the visible floor (0.15) to absorb rounding artifacts
    when Final Hours are small (1.1, 2.2). E.g. 0.16 × 1.1 = 0.924 → rounds to 0.92,
    giving red = (1.1 - 0.92) / 1.1 = 16.4%, well within 15-20%.
    """
    fn = function.lower()
    # Highest: cross-system / external / security
    if any(k in fn for k in [
        "integration", "external", "reconciliation", "reconcil", " api",
        "security", "encrypt", "audit trail", "calculation engine",
        "refinitiv", " cis ", "gbo", "dbs", " rps", "poems engine",
    ]):
        return 0.20
    # High: state machines, voting, joint-account multi-holder, batch schedule
    if any(k in fn for k in [
        "state model", "state machine", "voting", "joint",
        "batch", "exception", "free shares", "72-hour", "72h",
        "session handoff", "session",
        "voting rules", "reconciliation policy",
    ]):
        return 0.18
    # Lowest: tests, simple UI, config, prompts
    if any(k in fn for k in [
        "unit test", " sit", " sit ", "cross-item integration",
        "configuration approach", "glossary", "metadata",
        "promote", "enable/disable", "campaign ownership",
        "acceptance criteria", "in-app prompt",
        "display handling", "remove template",
        "decompose", "problem statement", "target-state",
        "per-item current-state", "show ",
    ]):
        return 0.16
    # Default for standard UI/business-logic work: 17%
    return 0.17


def _recompute_use_ai(base: float, platform: float, coord: float, final_2p: float, func: str) -> float:
    """Compute Use AI (2P) by reducing Final Hours (2P) by 15-20% based on function complexity.

    Uses exact rate fractions (0.80, 0.82, 0.85, 0.83) and rounds Use AI to 2 decimals.
    Acceptable final reduction: 15-20% after rounding artifact.
    """
    rate = _ai_reduction_for(func)
    return round(final_2p * (1 - rate), 2)


def extend_ready_project_est(service):
    """Append the 7 missing URS project sections to the existing Ready_Project_Est tab.
    Preserves the 4 existing sections (Trade Ticket Lite, PhillipGPT, ReCaptcha, Smart Portfolio).
    Layout matches the existing tab: col A empty, col B label, cols C-G metrics.
    """
    SPREADSHEET_ID_LOCAL = "1_MIasMUIaDwauGsmSIQPiC7allQLDOxm9aW_t5a2vbk"
    TAB = "Ready_Project_Est"

    # Read existing content to find the last meaningful row (the Smart Portfolio
    # Total row is at row 93 — anything after is from prior wrong-format appends)
    existing = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID_LOCAL, range=f"'{TAB}'!A1:G250"
    ).execute()
    existing_rows = existing.get("values", [])

    # Locate the original last row of the 4 existing projects by finding the row
    # index of the last "Smart Portfolio" Total row, OR by trusting the 93 row
    # baseline (which is the last untouched good row).
    # Approach: find the last row that contains a value in col F (Final Hours 2P)
    # OR col B (label) that's a "Total" row in the original 4 sections. The 4
    # existing projects end with row 93 = "Total | ... | 20 | 12.8".
    # To be safe, locate the last row whose col B == "Total" AND col F is numeric.
    last_original_row = 0
    for idx, row in enumerate(existing_rows, 1):
        if len(row) >= 2 and row[1] == "Total" and idx <= 100:
            last_original_row = idx
    if last_original_row == 0:
        # Fallback: assume the 4 existing projects end at row 93
        last_original_row = 93
    print(f"  Last original row (4-project baseline): {last_original_row}")

    # Clear any rows after the baseline (3 blank rows + corrupted appends)
    service.spreadsheets().values().clear(
        spreadsheetId=SPREADSHEET_ID_LOCAL,
        range=f"'{TAB}'!A{last_original_row + 1}:G250",
    ).execute()
    print(f"  Cleared rows {last_original_row + 1} onward")

    # Start the new append at last_original_row + 4 (3 blank separator rows + 1)
    next_row = last_original_row + 4

    # Build the rows to append — match the existing 4-project layout:
    #   col A: empty
    #   col B: function name / project title / "Total"
    #   col C: 1P base
    #   col D: Platform (x2)
    #   col E: Coordination
    #   col F: Final Hours (2P)
    #   col G: Use AI (2P)
    sections = build_new_ready_project_sections()
    rows_to_write = []
    for project_name, header, computed in sections:
        # Project title row — col B = title (matches existing pattern: row 3 has
        # B="Trade Ticket Lite Mode - Stocks")
        rows_to_write.append(["", header, "", "", "", "", ""])
        # Header row
        rows_to_write.append([
            "",
            "Function",
            "ScreenBase Hours (1P) (Man day)",
            "Platform (x2) (Man day)",
            "Coordination (Man day)",
            "Final Hours (2P) (Man day)",
            "Use AI(2P)",
        ])
        total_final_2p = 0.0
        total_use_ai = 0.0
        for func, base, platform, coord, final_2p, use_ai in computed:
            total_final_2p += final_2p
            total_use_ai += use_ai
            rows_to_write.append([
                "",
                func,
                fmt_md(base),
                fmt_md(platform),
                fmt_md(coord),
                fmt_md(final_2p),
                fmt_md(use_ai),
            ])
        # Total row — col B="Total", col C-E empty, col F=total_final_2p, col G=total_use_ai
        rows_to_write.append([
            "",
            "Total",
            "",
            "",
            "",
            fmt_md(round(total_final_2p, 2)),
            fmt_md(round(total_use_ai, 2)),
        ])
        rows_to_write.append([])  # blank
        rows_to_write.append([])  # blank

    # Write the new rows starting at next_row
    end_row = next_row + len(rows_to_write) - 1
    service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID_LOCAL,
        range=f"'{TAB}'!A{next_row}:G{end_row}",
        valueInputOption="USER_ENTERED",
        body={"values": rows_to_write},
    ).execute()
    print(f"  Appended {len(rows_to_write)} rows to '{TAB}' starting at row {next_row}")

    # Update the title row (A1) from "Q3 URS" to "May Submission URS"
    service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID_LOCAL,
        range=f"'{TAB}'!A1",
        valueInputOption="USER_ENTERED",
        body={"values": [["May Submission URS (Q3 2026) — 11 Projects, Team Methodology"]]},
    ).execute()
    print("  Updated A1 title")


# ---------------- Timeline (Q3/Q4) ----------------


def build_timeline_rows():
    """Build the proposed Q3/Q4 timeline narrative."""
    rows = []
    rows.append(["Proposed Q3/Q4 2026 Timeline — Mobile App Modules"])
    rows.append(["Based on revised team-methodology estimates (884 dev MD, 203 QA MD)"])
    rows.append([])
    rows.append(["Team Composition Assumption"])
    rows.append(["Mobile Core Team", "5 iOS/AOS devs, 3 QAs, 1 BA, 1 PM (2 streams parallel)"])
    rows.append(["Mobile Engagement Team", "5 iOS/AOS devs, 3 QAs, 1 BA, 1 PM (2 streams parallel)"])
    rows.append(["Sprint length", "10 working days (2 weeks)"])
    rows.append(["Total dev capacity", "~50 MD/sprint per team = ~100 MD/sprint combined"])
    rows.append(["Total QA capacity", "~21 MD/sprint per team = ~42 MD/sprint combined"])
    rows.append(["Q3 2026 window", "Jul 1 — Sep 30 (13 weeks ≈ 6.5 sprints)"])
    rows.append(["Q4 2026 window", "Oct 1 — Dec 31 (13 weeks ≈ 6.5 sprints)"])
    rows.append([])
    rows.append(["Q3 2026 Schedule (start Jul 1, 2026)"])
    rows.append([])
    rows.append(["Sprint", "Dates", "Mobile Core Team", "Mobile Engagement Team", "Cross-team"])
    rows.append([
        "Q3-S1",
        "Jul 1 — Jul 14",
        "PROJ-001 BTR (Kicking off) + PROJ-007 HLW (Kicking off)",
        "PROJ-002 CCT (Kicking off) + PROJ-003 TCC (Kicking off)",
        "Solution Design + Architecture review",
    ])
    rows.append([
        "Q3-S2",
        "Jul 15 — Jul 28",
        "BTR + HLW sprint 2",
        "CCT + TCC sprint 2",
        "API contract freeze",
    ])
    rows.append([
        "Q3-S3",
        "Jul 29 — Aug 11",
        "BTR (final sprint) + HLW sprint 3",
        "CCT sprint 3 + TCC sprint 3",
        "Mid-Q3 demo to stakeholders",
    ])
    rows.append([
        "Q3-S4",
        "Aug 12 — Aug 25",
        "HLW sprint 4 + Bug fix buffer",
        "CCT sprint 4 + TCC sprint 4",
        "Performance profiling begins",
    ])
    rows.append([
        "Q3-S5",
        "Aug 26 — Sep 8",
        "HLW sprint 5",
        "CCT sprint 5 + TCC sprint 5",
        "Security + PHI compliance review",
    ])
    rows.append([
        "Q3-S6",
        "Sep 9 — Sep 22",
        "HLW (final sprint) + Staging deploy",
        "CCT (final sprint) + TCC sprint 6",
        "End-to-end integration test",
    ])
    rows.append([
        "Q3-S7",
        "Sep 23 — Sep 30",
        "PROJ-001 BTR GO-LIVE (Sep 23) | HLW Staging",
        "CCT Staging | TCC sprint 7 (final)",
        "Release readiness review",
    ])
    rows.append([])
    rows.append(["Q4 2026 Schedule (start Oct 1, 2026)"])
    rows.append([])
    rows.append(["Sprint", "Dates", "Mobile Core Team", "Mobile Engagement Team", "Cross-team"])
    rows.append([
        "Q4-S1",
        "Oct 1 — Oct 14",
        "PROJ-007 HLW GO-LIVE (Oct 1) | PROJ-005 IMD Kickoff",
        "TCC GO-LIVE (Oct 1) | PROJ-004 SMB Kickoff",
        "UPT API design begins (PROJ-008)",
    ])
    rows.append([
        "Q4-S2",
        "Oct 15 — Oct 28",
        "IMD sprint 2 + HLW hypercare",
        "SMB sprint 2 + CCT hypercare",
        "UPT data model + event bus design",
    ])
    rows.append([
        "Q4-S3",
        "Oct 29 — Nov 11",
        "IMD sprint 3 + UPT kickoff",
        "PROJ-006 LBK Kickoff + SMB sprint 3",
        "UPT sprint 1 (parallel)",
    ])
    rows.append([
        "Q4-S4",
        "Nov 12 — Nov 25",
        "IMD sprint 4 + UPT sprint 2",
        "LBK sprint 2 + SMB sprint 4",
        "Cross-team API integration testing",
    ])
    rows.append([
        "Q4-S5",
        "Nov 26 — Dec 9",
        "IMD (final) + UPT sprint 3",
        "LBK sprint 3 + SMB sprint 5",
        "End-to-end testing begins",
    ])
    rows.append([
        "Q4-S6",
        "Dec 10 — Dec 23",
        "UPT sprint 4 + Staging",
        "LBK sprint 4 + SMB (final sprint)",
        "Release candidate freeze",
    ])
    rows.append([
        "Q4-S7",
        "Dec 24 — Dec 31",
        "UPT sprint 5 (final) + Staging deploy",
        "LBK (final sprint) + Staging deploy",
        "Year-end release readiness",
    ])
    rows.append([])
    rows.append(["Go-Live Targets"])
    rows.append(["Date", "Project", "Status gate"])
    rows.append(["Sep 23, 2026", "PROJ-001 Blood Test Result", "After 3 sprints + 1 sprint hardening"])
    rows.append(["Oct 1, 2026", "PROJ-007 Health Wallet", "After 6 sprints, includes PHI audit"])
    rows.append(["Oct 1, 2026", "PROJ-003 Tele-consultation Chat", "After 7 sprints, includes WebRTC soak test"])
    rows.append(["Dec 23, 2026", "PROJ-005 Imaging & Diagnostics", "After 5 sprints + DICOM viewer perf validation"])
    rows.append(["Dec 30, 2026", "PROJ-004 Smart Booking", "After 6 sprints + booking-flow soak test"])
    rows.append(["Dec 30, 2026", "PROJ-006 Lab Booking", "After 6 sprints + phlebotomist dispatch validation"])
    rows.append(["Dec 31, 2026", "PROJ-008 Unified Patient Timeline", "After 7 sprints — depends on all P0 modules data sources"])
    rows.append([])
    rows.append(["Risk Notes"])
    rows.append([
        "1. QA bottleneck: Total QA = 203 MD = 9.7 sprints at 21 MD/sprint. Parallelize across 2 teams = 4.85 sprints (within Q3+Q4).",
    ])
    rows.append([
        "2. PROJ-008 UPT is dependent on data sources from 5 other modules. Coordinate data contract freeze in Q3-S2.",
    ])
    rows.append([
        "3. WebRTC (PROJ-003) and DICOM viewer (PROJ-005) are technically high-risk. Plan extra hardening sprints and spike early.",
    ])
    rows.append([
        "4. Health Wallet (PROJ-007) PHI compliance requires security audit before Oct 1 GO-LIVE — schedule in Q3-S5.",
    ])
    rows.append([
        "5. If dev capacity drops below 80% (e.g. support/incident rotation), timeline slips by ~1 sprint per quarter.",
    ])
    return rows


# ---------------- Cleanup of wrong-interpretation tabs ----------------


def cleanup_wrong_tabs(service):
    """Remove tabs created from a prior wrong interpretation (8 mobile app modules).
    Keep: Dashboard (original), all per-doc tabs (1-8), Summary, Reference, Findings,
    Master Summary, Cross-File Synthesis, all per-doc Q&A tabs, Ready_Project_Est,
    Estimation Summary.
    Remove: Blood Test Result, Chronic Care, Tele-consult Chat, Smart Booking, Imaging
    Diagnostics, Lab Booking, Health Wallet, Unified Timeline, Timeline, May_Readiness,
    DASHBOARD (overwritten in this session with wrong mobile-app data).
    """
    SPREADSHEET_ID_LOCAL = "1_MIasMUIaDwauGsmSIQPiC7allQLDOxm9aW_t5a2vbk"
    tabs_to_remove = [
        "Blood Test Result",
        "Chronic Care",
        "Tele-consult Chat",
        "Smart Booking",
        "Imaging Diagnostics",
        "Lab Booking",
        "Health Wallet",
        "Unified Timeline",
        "Timeline",
        "May_Readiness",
        "DASHBOARD",
    ]
    meta = service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID_LOCAL).execute()
    existing_titles = {s["properties"]["title"]: s["properties"]["sheetId"] for s in meta["sheets"]}
    requests = []
    for tab in tabs_to_remove:
        if tab in existing_titles:
            requests.append({"deleteSheet": {"sheetId": existing_titles[tab]}})
            print(f"  Will remove: {tab}")
    if requests:
        service.spreadsheets().batchUpdate(
            spreadsheetId=SPREADSHEET_ID_LOCAL, body={"requests": requests}
        ).execute()
        print(f"  Removed {len(requests)} wrong-interpretation tabs")


# ---------------- Publish ----------------


def get_service():
    creds = Credentials.from_service_account_file(CREDS_PATH, scopes=SCOPES)
    return build("sheets", "v4", credentials=creds)


def ensure_tab(service, tab_name):
    """Create a tab if it doesn't exist. Tolerates 400 'already exists'."""
    sheet_meta = service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
    existing = [s["properties"]["title"] for s in sheet_meta["sheets"]]
    if tab_name in existing:
        return
    try:
        service.spreadsheets().batchUpdate(
            spreadsheetId=SPREADSHEET_ID,
            body={"requests": [{"addSheet": {"properties": {"title": tab_name}}}]},
        ).execute()
        print(f"  + Created tab: {tab_name}")
    except Exception as e:
        # Tolerate "already exists" (API metadata can lag)
        if "already exists" in str(e):
            return
        raise


def write_tab(service, tab_name, rows):
    # Clear
    service.spreadsheets().values().clear(
        spreadsheetId=SPREADSHEET_ID, range=f"'{tab_name}'!A1:Z"
    ).execute()
    # Write
    body = {"values": rows}
    service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=f"'{tab_name}'!A1",
        valueInputOption="USER_ENTERED",
        body=body,
    ).execute()
    print(f"  Wrote {len(rows)} rows to '{tab_name}'")


def format_header(service, tab_name, end_col="K"):
    """Bold the first row + format headers."""
    sheet = service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
    sheet_id = None
    for s in sheet["sheets"]:
        if s["properties"]["title"] == tab_name:
            sheet_id = s["properties"]["sheetId"]
            break
    if sheet_id is None:
        return
    requests = [
        {
            "repeatCell": {
                "range": {"sheetId": sheet_id, "startRowIndex": 0, "endRowIndex": 1},
                "cell": {"userEnteredFormat": {"textFormat": {"bold": True, "fontSize": 14}}},
                "fields": "userEnteredFormat.textFormat",
            }
        }
    ]
    service.spreadsheets().batchUpdate(
        spreadsheetId=SPREADSHEET_ID, body={"requests": requests}
    ).execute()


def main():
    service = get_service()

    # Ready_Project_Est — extend with missing 7 URS projects (preserve existing 4)
    extend_ready_project_est(service)

    # Clean up any wrong-interpretation tabs (left over from earlier turn)
    cleanup_wrong_tabs(service)

    print("\nDone.")


if __name__ == "__main__":
    main()
