## Why

The `docs/urs/may-submission/` folder contains a full set of May Submission URS source documents that need to be read and evaluated as one coherent package, but there is no structured artifact that consolidates the contents, business rules, ambiguities, and evaluation findings across the complete source set. A focused URS evaluation is needed now so the team can understand what the current document set actually specifies, what remains unclear, and what source-level gaps exist before any downstream planning or implementation work.

The assessment output also needs to land in the shared team surface already prepared for this work: the `May-submission-assessment` Google Sheet at `https://docs.google.com/spreadsheets/d/1_MIasMUIaDwauGsmSIQPiC7allQLDOxm9aW_t5a2vbk/edit?usp=sharing`, using the TDT-approved Sheets ecosystem (`tdt-sheets` via `tdt_core` patterns) rather than ad hoc manual copy/paste or generic Google tooling.

## What Changes

- Create an OpenSpec-backed URS evaluation workflow for the full `docs/urs/may-submission/` folder.
- Define a documentation capability that reads and evaluates every URS file currently present in the folder and produces a structured assessment result.
- Capture the current May Submission source set as the first evaluated URS package, explicitly covering:
  - `Gami - Amalgamated Trade.pdf`
  - `Gami - Cash Coupon Global Admin.pdf`
  - `ITSR 330853 Refer A Friend URS Revised 1.1.pdf`
  - `ITSR 369004 SMART Portfolio Phase 2.pdf`
  - `ITSR [369574] RECAPTCHA TO REPLACE GEETESTv1.0.pdf`
  - `Phillip GPT on POEMS v1.0.pdf`
  - `URS_P3_Stock Trade ticket - Lite mode.pdf`
  - `UT Enhancements - Phase 2 2026.pdf`
  - `WM - Accredited Investor Form.pdf`
  - `CashCOupon.drawio`
- Standardize the assessment output around source inventory, extracted business rules, stated workflows, ambiguities, contradictions, gaps, and source-quality observations.
- Write the assessment result into the shared Google Sheet `May-submission-assessment` using `tdt_sheets.SheetsClient` with `ServiceAccountAuth.from_env()` and the TDT ecosystem’s standard credential/config flow rooted in `~/.tdt/.env`.
- Keep the change scoped to research and documentation artifacts in `tdt-meta` plus the approved spreadsheet output surface; no Jira linkage, product implementation, or application code changes are included.

## Capabilities

### New Capabilities
- `urs-assessment-docs`: Produce structured evaluation documents for URS folders so teams can understand source contents, business rules, workflows, ambiguities, contradictions, and document quality before any planning or implementation work, and publish the structured result into the approved shared spreadsheet through the TDT Sheets ecosystem.

### Modified Capabilities
- None.

## Impact

- Affected area: `tdt-meta/openspec/changes/assess-may-submission-urs/`, research-oriented documentation under the metadata/docs planning surface, and the shared Google Sheet `May-submission-assessment`.
- Source inputs: every current file under `docs/urs/may-submission/`, specifically the 9 PDFs and 1 draw.io file listed above.
- Output destination: `https://docs.google.com/spreadsheets/d/1_MIasMUIaDwauGsmSIQPiC7allQLDOxm9aW_t5a2vbk/edit?usp=sharing`.
- Evaluation focus: all stated business rules, workflows, acceptance details, unresolved questions, placeholders, and source-quality issues across the full May Submission URS set.
- Dependencies: Existing PDF extraction workflow in `browser-cli`, current OpenSpec process, and the approved `tdt-sheets` / `tdt_core` ecosystem only.
- Non-goals: This change does not implement product behavior, coupon logic changes, Jira analysis, Jira automation, or mobile/backend code updates.
