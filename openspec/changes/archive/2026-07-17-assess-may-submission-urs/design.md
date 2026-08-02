## Context

The May Submission URS set under `docs/urs/may-submission/` currently contains 10 source artifacts that must all be covered by the assessment:
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

These files span multiple feature areas and likely contain both independent requirements and overlapping business context. They have not been consolidated into a structured assessment artifact that explains what the folder specifies, what business rules are explicit, what source ambiguities remain, and where the documents are incomplete or internally inconsistent.

The final assessment result must be written to the shared Google Sheet `May-submission-assessment` at `https://docs.google.com/spreadsheets/d/1_MIasMUIaDwauGsmSIQPiC7allQLDOxm9aW_t5a2vbk/edit?usp=sharing`, using the TDT-approved Sheets ecosystem: `tdt_sheets.SheetsClient` with `ServiceAccountAuth.from_env()` and standard environment loading via `tdt_core` from `~/.tdt/.env`. Local files in `tdt-meta` remain useful as working notes and change artifacts, but the spreadsheet is the delivery surface.

During execution prep, we confirmed workspace policy explicitly routes Google Sheets operations through `tdt-sheets`. Existing TDT repo patterns in `jira-daily-reports` and `jira-skill` show the canonical auth and client setup needed for implementation.

## Goals / Non-Goals

**Goals:**
- Produce a structured assessment for the full `docs/urs/may-submission/` folder.
- Cover every URS file currently present in the folder rather than focusing on a subset.
- Extract and organize the stated business rules, workflow steps, operational timing, constraints, ambiguities, contradictions, and source-quality issues across the whole source set.
- Preserve a file-by-file breakdown while also synthesizing cross-file relationships and conflicts.
- Write the final assessment result into the shared Google Sheet using the TDT-approved Sheets ecosystem rather than manual spreadsheet editing or generic Google tooling.
- Mirror existing TDT implementation patterns so execution can reuse a proven auth and client setup.
- Establish a repeatable assessment pattern for future URS folders that need spreadsheet-delivered outputs.
- Leverage existing local tooling: `browser-cli` for PDF extraction, draw.io XML parsing for diagram review, and `tdt-sheets` for spreadsheet reads/writes.

**Non-Goals:**
- Do not implement any product behavior in any production service.
- Do not modify existing mobile or backend code.
- Do not create or update Jira work.
- Do not depend on ad hoc browser copy/paste workflows or non-standard Google APIs when the TDT sheets path exists.

## Decisions

### How to define the scope of assessment

**Decision:** Treat the entire current `docs/urs/may-submission/` directory contents as mandatory assessment scope.

**Rationale:** The user explicitly requested that the assessment contain all URS. The current folder contains a fixed known inventory of 10 source artifacts, and the assessment must not stop at representative examples. Evaluating the complete folder prevents silent gaps in coverage and produces a trustworthy handoff artifact.

### How to deliver the assessment result

**Decision:** Write the assessment result into the shared Google Sheet `May-submission-assessment` using `tdt_sheets.SheetsClient` and `ServiceAccountAuth.from_env()`.

**Rationale:** Workspace policy explicitly requires routing Google Sheets operations through `tdt-sheets`. Existing code in `jira-daily-reports` and `jira-skill` already uses this client and auth pattern, making it the correct and repeatable execution path.

**Alternative considered:** Keeping the result only in local markdown under the OpenSpec change. Rejected because the user explicitly wants the assessment result written to the shared spreadsheet and workspace policy already defines the standard Sheets path.

### How to handle Sheets auth and client setup

**Decision:** Use the standard TDT setup pattern: load environment via `tdt_core.load_tdt_env()` from `~/.tdt/.env`, create auth with `ServiceAccountAuth.from_env()`, and instantiate `SheetsClient(auth=auth, backend="sdk")`.

**Rationale:** This matches existing TDT implementations and uses the ecosystem’s 3-level credential fallback and standard backend behavior.

### How to extract and parse source documents

**Decision:** Use `browser-cli` for PDF text extraction and direct XML reading for draw.io files.

**Rationale:** `browser-cli` is already installed and verified in this workspace for page-by-page PDF extraction. draw.io artifacts are stored as readable XML, which can be inspected directly for actors, steps, and system touchpoints.

### How to structure working artifacts

**Decision:** Keep working notes and change artifacts inside `openspec/changes/assess-may-submission-urs/`, while treating the Google Sheet as the final assessment delivery surface.

**Rationale:** This preserves OpenSpec traceability and lets the team keep intermediate notes locally without losing the required shared output destination.

## Risks / Trade-offs

**Risk:** The target spreadsheet may not yet have a finalized schema or dedicated tabs for the assessment.
**Mitigation:** The assessment workflow SHALL first inspect sheet metadata and existing tabs through `tdt-sheets`, then write results using an explicit worksheet/layout plan.

**Risk:** Service-account access may be missing for the target spreadsheet.
**Mitigation:** The workflow SHALL verify spreadsheet metadata or a successful read through `tdt-sheets` before attempting writes and SHALL treat access failures as execution blockers to resolve at the sharing/credential layer.

**Risk:** Full-folder assessment is broader and more time-consuming than evaluating one document.
**Mitigation:** The task plan SHALL require inventory-first execution and per-file progress tracking so coverage remains explicit and measurable.

**Risk:** Source documents may contain placeholders, contradictory notes, or incomplete acceptance criteria.
**Mitigation:** The assessment SHALL distinguish confirmed rules from open questions and document quality issues without guessing missing requirements.

**Risk:** Folder contents may change over time, making assessments stale.
**Mitigation:** The assessment SHALL record the exact assessed file inventory and treat later additions as scope changes requiring an updated assessment pass.

## Open Questions

- What worksheet/tab and column schema should hold the per-file assessment results if the target spreadsheet is currently blank? [Google Sheet](https://docs.google.com/spreadsheets/d/1_MIasMUIaDwauGsmSIQPiC7allQLDOxm9aW_t5a2vbk/edit?usp=sharing)
- Should the spreadsheet contain one row per source file, one row per finding, or a hybrid layout with summary + detail tabs?
- If new files are added to `docs/urs/may-submission/` after the first pass, should they extend the same spreadsheet tab or trigger a follow-up change?
