# Assess May Submission URS Tasks

## 1. File Inventory

- [x] 1.1 List and catalog every current file in `docs/urs/may-submission/`, recording file name, type, apparent role, and whether it has been reviewed in this assessment.
- [x] 1.2 Confirm the current mandatory source set contains all 10 known artifacts: 9 PDFs and 1 draw.io file.
- [x] 1.3 Record the exact assessed inventory in the local change workspace so later folder additions can be detected as scope changes.

## 2. PDF Extraction (all 9 current URS PDFs)

- [x] 2.1 Verify and record extraction output for `Gami - Amalgamated Trade.pdf`, including page count, output path, and any extraction warnings.
- [x] 2.2 Extract and review `Gami - Cash Coupon Global Admin.pdf` and record major business rules, workflows, ambiguities, and source-quality issues.
- [x] 2.3 Extract and review `ITSR 330853 Refer A Friend URS Revised 1.1.pdf` and record major business rules, workflows, ambiguities, and source-quality issues.
- [x] 2.4 Extract and review `ITSR 369004 SMART Portfolio Phase 2.pdf` and record major business rules, workflows, ambiguities, and source-quality issues.
- [x] 2.5 Extract and review `ITSR [369574] RECAPTCHA TO REPLACE GEETESTv1.0.pdf` and record major business rules, workflows, ambiguities, and source-quality issues.
- [x] 2.6 Extract and review `Phillip GPT on POEMS v1.0.pdf` and record major business rules, workflows, ambiguities, and source-quality issues.
- [x] 2.7 Extract and review `URS_P3_Stock Trade ticket - Lite mode.pdf` and record major business rules, workflows, ambiguities, and source-quality issues.
- [x] 2.8 Extract and review `UT Enhancements - Phase 2 2026.pdf` and record major business rules, workflows, ambiguities, and source-quality issues.
- [x] 2.9 Extract and review `WM - Accredited Investor Form.pdf` and record major business rules, workflows, ambiguities, and source-quality issues.

## 3. Diagram Extraction

- [x] 3.1 Parse `CashCOupon.drawio` and extract the named actors, systems, workflow steps, state transitions, and embedded business conditions.
- [x] 3.2 Record any business rules or workflow constraints embedded in the diagram that are not explicit in the PDFs.
- [x] 3.3 Note where the diagram overlaps with, extends, or conflicts with statements in the PDFs.

## 4. Cross-File Evaluation

- [x] 4.1 Compile all explicit business rules found across the full 10-file source set.
- [x] 4.2 Record workflow timing, batching rules, and operational constraints across the full source set.
- [x] 4.3 Identify overlapping, conflicting, or redundant requirements across the evaluated files.
- [x] 4.4 Identify missing acceptance details, placeholders, unresolved questions, and incomplete sections across the evaluated files.

## 5. TDT Sheets Delivery Design

- [x] 5.1 Initialize environment/config by loading `~/.tdt/.env` through the standard TDT path and create a `tdt_sheets.SheetsClient` with `ServiceAccountAuth.from_env()`.
- [x] 5.2 Inspect the target Google Sheet `May-submission-assessment` at `https://docs.google.com/spreadsheets/d/1_MIasMUIaDwauGsmSIQPiC7allQLDOxm9aW_t5a2vbk/edit?usp=sharing` using `tdt-sheets` and determine the worksheet/tab structure.
- [x] 5.3 Define the assessment output schema for the spreadsheet, including whether the result is written as one row per source file, one row per finding, or a hybrid tab structure.
- [x] 5.4 Confirm the exact `tdt-sheets` read/write methods and target ranges / tabs before publishing results.

## 6. Assessment Result Authoring and Publish

- [x] 6.1 Prepare a structured assessment result that includes mandatory per-file findings for all 10 current source artifacts plus a cross-file synthesis.
- [x] 6.2 Write the final assessment result into the target Google Sheet using `tdt_sheets.SheetsClient`.
- [x] 6.3 Preserve local traceability notes in the change workspace showing how spreadsheet entries map back to source files and findings.

## 7. Verification

- [x] 7.1 Verify every one of the 10 current source artifacts has at least one finding represented in the spreadsheet-delivered assessment result.
- [x] 7.2 Verify the PDF extraction workflow still produces output for at least one known source using `browser-cli` and record the output path.
- [x] 7.3 Verify the target Google Sheet reflects the written assessment result after the `tdt-sheets` write step.
- [x] 7.4 Confirm the OpenSpec change workspace contains enough supporting notes to audit the spreadsheet output.
