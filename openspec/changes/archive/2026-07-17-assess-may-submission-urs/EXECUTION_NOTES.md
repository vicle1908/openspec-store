# May Submission URS Assessment Execution Notes

## Source Inventory

Reviewed source directory: `docs/urs/may-submission`

| File | Type | Role | Reviewed |
| --- | --- | --- | --- |
| `CashCOupon.drawio` | draw.io XML | Workflow / system diagram for cash coupon flow | yes |
| `Gami - Amalgamated Trade.pdf` | PDF | URS source document | yes |
| `Gami - Cash Coupon Global Admin.pdf` | PDF | URS source document | yes |
| `ITSR 330853 Refer A Friend URS Revised 1.1.pdf` | PDF | URS source document | yes |
| `ITSR 369004 SMART Portfolio Phase 2.pdf` | PDF | URS source document | yes |
| `ITSR [369574] RECAPTCHA TO REPLACE GEETESTv1.0.pdf` | PDF | URS source document | yes |
| `Phillip GPT on POEMS v1.0.pdf` | PDF | URS source document | yes |
| `URS_P3_Stock Trade ticket - Lite mode.pdf` | PDF | URS source document | yes |
| `UT Enhancements - Phase 2 2026.pdf` | PDF | URS source document | yes |
| `WM - Accredited Investor Form.pdf` | PDF | URS source document | yes |
| `URS - DDA Linking and DDA Deposit.pdf` | PDF | URS source document (added 19 Jun 2026) | yes |
| `URS -POEMS Shareholder Meeting P3 URS.pdf` | PDF | URS source document (added 19 Jun 2026) | yes |

## Confirmed Scope
| `URS - DDA Linking and DDA Deposit.pdf` | PDF | URS source document (added 19 Jun 2026) | yes |
| `URS -POEMS Shareholder Meeting P3 URS.pdf` | PDF | URS source document (added 19 Jun 2026) | yes |

- Total artifacts in scope: 10
- PDF count: 9
- draw.io count: 1
- Inventory matches OpenSpec scope: yes

## TDT Sheets Execution Pattern

Canonical implementation pattern confirmed from existing TDT repos:

```python
from tdt_core.env import load_tdt_env
from tdt_sheets import ServiceAccountAuth, SheetsClient

load_tdt_env()  # loads ~/.tdt/.env first
auth = ServiceAccountAuth.from_env(
    scopes=[
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
)
client = SheetsClient(auth=auth, backend="sdk")
metadata = client.get_metadata(SPREADSHEET_ID)
```

## Sheet Access Probe

- `~/.tdt/.env` is the canonical environment source for the TDT ecosystem and is present on this machine.
- `load_tdt_env()` loads `~/.tdt/.env` before any optional repo-local override.
- `tdt-sheets` client initialization path is correct.
- The earlier failed probe was caused by the shell command not exporting the env vars into the Python process in a way that `ServiceAccountAuth.from_env()` could consume during that run.
- Re-running with a proper exported env path succeeded.

Resolved interpretation:

- The canonical TDT environment source already contained valid Google credential paths.
- The credential JSON file existed at the configured path.
- Spreadsheet metadata inspection and spreadsheet writes are now verified and complete.

## Pending Probes

- None. Google Sheet access and write path are now verified through `tdt-sheets`.

## Extraction Coverage

- Extracted PDFs:
  - `Gami - Amalgamated Trade.pdf`
  - `Gami - Cash Coupon Global Admin.pdf`
  - `ITSR 330853 Refer A Friend URS Revised 1.1.pdf`
  - `ITSR 369004 SMART Portfolio Phase 2.pdf`
  - `ITSR [369574] RECAPTCHA TO REPLACE GEETESTv1.0.pdf`
  - `Phillip GPT on POEMS v1.0.pdf`
  - `URS_P3_Stock Trade ticket - Lite mode.pdf`
  - `UT Enhancements - Phase 2 2026.pdf`
  - `WM - Accredited Investor Form.pdf`
- Draw.io source loaded directly from `docs/urs/may-submission/CashCOupon.drawio`.
- Assessment draft created at `ASSESSMENT_DRAFT.md` with per-file findings and draft cross-file synthesis.
- Enhanced assessment created at `ASSESSMENT_ENHANCED.md` with readiness levels, blockers, correction owners, and overall verdict.
- Feature-delta addendum created at `ASSESSMENT_FEATURE_DELTA.md` with current-state vs targeted-feature analysis for each source.
- Remediation spec created at `REMEDIATION_SPEC.md` with exact per-document section additions, rewrites, and priority waves.
- Engineering-detail addendum created at `ASSESSMENT_ENGINEERING_DETAIL.md` with testability, integration dependency, operational dependency, regression risk, and observability analysis.
- Canonical consolidated report created at `MASTER_ASSESSMENT.md` combining readiness, feature delta, engineering detail, and remediation guidance into one source of truth.

## Google Sheets delivery status

- `tdt-sheets` authentication succeeded after exporting `~/.tdt/.env` correctly into the shell environment.
- Root cause of the earlier failed probe: the credential JSON file existed, but the earlier shell probe did not export the env vars in a way that `ServiceAccountAuth.from_env()` could resolve during that command.
- Workbook title confirmed as `May-submission-assessment`.
- Tabs created and populated:
  - `Summary`
  - `Findings`
  - `Cross-File Synthesis`
- `Sheet1` was also updated with local traceability pointers.
- Verification after feature-delta write:
  - `Summary` rows read back: 12
  - `Cross-File Synthesis` rows read back: 7
  - `Summary` header includes `Feature Delta Type`, `Current-State Feature Summary`, and `Targeted Feature Summary`
  - `OVERALL` verdict row present with readiness `3.5 / Conditionally ready`
- Verification after remediation write:
  - `Sheet1` rows read back: 12
  - `Sheet1` header includes remediation wave and P0/P1/P2 action columns
  - `OVERALL` remediation blueprint row present
- Verification after engineering-detail write:
  - `Summary` rows read back: 12
  - `Summary` header includes `Testability`, `Integration Dependency`, `Operational Dependency`, `Regression Risk`, and `Observability Need`
  - `OVERALL` engineering-detail row present with averaged portfolio ratings
- Master assessment authored locally at `MASTER_ASSESSMENT.md` as the canonical detailed report.
- Attempted additional sheet tab for master summary hit range-parsing limitations in the current `tdt-sheets` wrapper for the chosen tab name; existing verified tabs remain the authoritative shared delivery surface.

## Extraction Evidence

- `Gami - Amalgamated Trade.pdf` extracted with `browser-cli`.
- Output: `artifacts/Gami - Amalgamated Trade.md`
- Extraction stats: 13 pages, 19011 characters, 19434 bytes.
- Warnings: none reported by extractor.

## Grooming-grounded re-publish (5 June 2026 sessions)

Inputs integrated from these grooming sessions:

- Smart Portfolio Phase 2 (Day 3) — RSP scope clarified; new P0 contract gaps around payment redirect, eGIRO return, failure/cancel.
- Trade Ticket (Light Mode) (Day 2) — Mode switch and persistence decisions now explicit; four open decisions tracked; readiness downgraded from `5/5` to `4/5`.
- Amalgamated Trade — Batch + amalgamation architecture confirmed; Marketing's amalgamated-market list still blocking.
- Cash Coupon — Happy-path lifecycle correction agreed; reconciliation/retry policy still open.

Local artifacts updated:

- `GROOMING_INPUTS.md` — new canonical reference for the 5 Jun 2026 meeting outputs and their per-doc impact.
- `MASTER_ASSESSMENT.md` — updated SMART Portfolio Phase 2, Amalgamated Trade, Cash Coupon, and Trade Ticket sections with grooming-grounded verdicts, including revised engineering profile numbers and grooming impact notes.
- `ASSESSMENT_ENGINEERING_DETAIL.md` — updated SMART Portfolio, Amalgamated Trade, and Trade Ticket engineering profiles to reflect grooming outcomes.
- `ASSESSMENT_ENHANCED.md` — cross-linked to `GROOMING_INPUTS.md`.
- `REMEDIATION_SPEC.md` — added Gami Amalgamated Trade, Cash Coupon, SMART Portfolio Phase 2, and Trade Ticket grooming-derived P0/P1/P2 actions; corrected Lite Mode P2 numbering.

Shared Google-Sheet delivery re-published:

- Tabs repopulated with grooming-grounded data via `artifacts/publish_grooming_grounded.py`.
- `ensure_sheet()` was used to create `Cross-File Synthesis` and `Sheet1` tabs (the `tdt-sheets` wrapper's `clear()` cannot address tabs that do not exist).
- Verification after grooming-grounded publish:
  - `Summary` rows read back: 12 (now includes `Grooming Impact` column)
  - `Findings` rows read back: 19 (new SMART, Trade Ticket, Amalgamated, Cash Coupon, and CashCOupon.drawio findings tagged with grooming source)
  - `Cross-File Synthesis` rows read back: 5 (4 themes + header)
  - `Sheet1` rows read back: 7 (now includes `Grooming Updates` column)
  - `OVERALL` rows present in all four tabs
- Environment loading for the publish script:
  - `~/.tdt/.env` line 64 (`SHEET_LINKS=...`) is malformed for shell sourcing (unquoted value with `|`/`,`). Workaround: source the env with `SHEET_LINKS` line filtered out.
  - `tdt_core.env.load_tdt_env` is not available in the `tdt-sheets` venv; `ServiceAccountAuth.from_env()` already tries to load it gracefully, so the script no longer imports `tdt_core` directly.
