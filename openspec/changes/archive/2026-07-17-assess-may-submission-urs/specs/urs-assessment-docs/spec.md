## ADDED Requirements

### Requirement: Mandatory full-folder URS coverage
The system SHALL evaluate the full selected URS folder as a source package and SHALL cover every URS file currently present in that folder within the assessment output.

#### Scenario: Evaluate the current May Submission source set
- **WHEN** an analyst evaluates `docs/urs/may-submission/`
- **THEN** the assessment SHALL include findings for all 10 current source artifacts in the folder, consisting of the 9 PDFs and the 1 draw.io file currently present

#### Scenario: Record exact assessed inventory
- **WHEN** the assessment is created
- **THEN** it SHALL list the exact file inventory reviewed so readers can verify that no current URS file in the folder was omitted from scope

### Requirement: File-by-file reading and synthesis
The system SHALL read each URS file in scope and SHALL capture both per-file findings and a consolidated cross-file synthesis.

#### Scenario: Extract PDF findings
- **WHEN** a URS file is a readable PDF such as `Gami - Amalgamated Trade.pdf`, `Gami - Cash Coupon Global Admin.pdf`, `ITSR 330853 Refer A Friend URS Revised 1.1.pdf`, `ITSR 369004 SMART Portfolio Phase 2.pdf`, `ITSR [369574] RECAPTCHA TO REPLACE GEETESTv1.0.pdf`, `Phillip GPT on POEMS v1.0.pdf`, `URS_P3_Stock Trade ticket - Lite mode.pdf`, `UT Enhancements - Phase 2 2026.pdf`, or `WM - Accredited Investor Form.pdf`
- **THEN** the assessment SHALL record the major business rules, acceptance details, workflows, operational timing, and unresolved source questions found in that PDF

#### Scenario: Extract diagram findings
- **WHEN** a URS file is a diagram source such as `CashCOupon.drawio`
- **THEN** the assessment SHALL record the actors, systems, workflow steps, state transitions, and embedded business conditions described by the diagram

#### Scenario: Produce a cross-file synthesis
- **WHEN** all current URS files in the folder have been reviewed
- **THEN** the assessment SHALL synthesize where the files reinforce, extend, overlap, or contradict one another

### Requirement: Business-rule and workflow evaluation
The system SHALL identify the explicit business rules, workflow conditions, and operational constraints described by the URS package.

#### Scenario: Record explicit business rules
- **WHEN** the URS package states rules such as `1 coupon for 1 settled trade`, same-day trade grouping, FIFO coupon use, market-level coupon configuration, or batch-window behavior
- **THEN** the assessment SHALL record those rules as explicit findings without reinterpreting them as implementation behavior

#### Scenario: Record workflow timing and batching rules
- **WHEN** the URS package specifies batch timing or operational windows such as `7.40pm SGT` processing or next-day handling after cutoff
- **THEN** the assessment SHALL document those timing rules and note any unclear, incomplete, or conflicting timing statements

### Requirement: Ambiguity, contradiction, and source-quality findings
The system SHALL identify ambiguities, contradictions, placeholders, and incomplete sections within the URS package.

#### Scenario: Detect incomplete sections
- **WHEN** a source file contains placeholders, empty sections, unresolved questions, or incomplete illustrations such as `???`, `n/a`, or `INK - HERE`
- **THEN** the assessment SHALL record those items as document-quality gaps

#### Scenario: Detect conflicting or unclear behavior
- **WHEN** multiple source files describe behavior that appears inconsistent, incomplete, overlapping, or difficult to reconcile
- **THEN** the assessment SHALL record the conflict or ambiguity and explain why it prevents confident interpretation

### Requirement: Spreadsheet delivery through TDT Sheets ecosystem
The system SHALL write the final assessment result to the shared Google Sheet `May-submission-assessment` using the TDT-approved Sheets ecosystem.

#### Scenario: Initialize standard TDT Sheets client
- **WHEN** the analyst prepares to inspect or publish spreadsheet results
- **THEN** the workflow SHALL load environment configuration through the standard TDT path from `~/.tdt/.env`, create auth with `ServiceAccountAuth.from_env()`, and use `tdt_sheets.SheetsClient(..., backend="sdk")`

#### Scenario: Inspect target spreadsheet before writing
- **WHEN** the analyst prepares to deliver the assessment result
- **THEN** the workflow SHALL inspect the target spreadsheet metadata and existing tabs through `tdt-sheets` before determining the worksheet/tab and column layout

#### Scenario: Write assessment result to Google Sheet
- **WHEN** the assessment findings are ready for publication
- **THEN** the workflow SHALL write the result into `https://docs.google.com/spreadsheets/d/1_MIasMUIaDwauGsmSIQPiC7allQLDOxm9aW_t5a2vbk/edit?usp=sharing` using `tdt_sheets.SheetsClient` rather than non-standard sheet tooling or manual browser editing

#### Scenario: Preserve traceability between local notes and spreadsheet output
- **WHEN** local working notes are used during analysis
- **THEN** the workflow SHALL preserve a mapping between local findings and spreadsheet-delivered results so the shared output remains auditable

### Requirement: Assessment-only source handling
The system SHALL keep URS evaluation work within planning and documentation artifacts and SHALL preserve source files unchanged.

#### Scenario: Separate derived findings from sources
- **WHEN** the analyst extracts text or notes from URS files
- **THEN** the workflow SHALL store derived findings separately from the original URS files and SHALL NOT modify the source artifacts

#### Scenario: No downstream planning side effects
- **WHEN** the assessment is performed
- **THEN** the workflow SHALL avoid Jira linkage, ticket updates, implementation edits, or production-state changes as part of the URS-only evaluation scope
