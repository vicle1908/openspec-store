# Proposed Spreadsheet Schema for `May-submission-assessment`

## Recommended Layout

Use a hybrid workbook structure with 4 tabs, now enhanced for readiness evaluation:

1. `Summary`
- One row per source file plus an overall portfolio verdict row.
- Purpose: coverage tracking, readiness scoring, primary blockers, correction ownership, and current-state vs targeted-feature analysis.

2. `Findings`
   - One row per finding.
   - Purpose: normalized business rules, workflows, ambiguities, conflicts, and quality issues.

3. `Cross-File Synthesis`
   - One row per synthesis item.
   - Purpose: overlaps, contradictions, repeated patterns, and final assessment implications.

4. `Sheet1` (Remediation Blueprint)
   - One row per source file plus an overall portfolio remediation row.
   - Purpose: document-improvement actions, priority waves, and exact P0/P1/P2 correction scope.

## Tab 1: `Summary`

Recommended columns:

- `File Name`
- `File Type`
- `Feature Area`
- `Reviewed` (`yes` / `no`)
- `Assessment Status` (`reviewed`, `blocked`)
- `Readiness Level`
- `Readiness Label`
- `Feature Delta Type`
- `Quality Score`
- `Testability`
- `Integration Dependency`
- `Operational Dependency`
- `Regression Risk`
- `Observability Need`
- `Blocks Build`
- `Primary Corrections Needed`
- `Correction Owner`
- `Local Evidence Path`

## Tab 2: `Findings`

Recommended columns:

- `Finding ID`
- `File Name`
- `Finding Type` (`business_rule`, `workflow`, `timing`, `ambiguity`, `conflict`, `quality_issue`)
- `Title`
- `Detail`
- `Severity` (`critical`, `high`, `medium`, `low`, `info`)
- `Blocks Build` (`yes`, `no`)
- `Correction Owner`
- `Recommended Correction`
- `Readiness Impact`
- `Source Evidence Path`

## Tab 3: `Cross-File Synthesis`

Recommended columns:

- `Synthesis ID`
- `Category` (`overlap`, `conflict`, `shared_pattern`, `quality_theme`, `assessment_implication`)
- `Files Involved`
- `Summary`
- `Why It Matters`
- `Recommended Follow-up`
- `Severity`

## Tab 4: `Sheet1` (Remediation Blueprint)

Recommended columns:

- `Doc`
- `Document Role`
- `Priority Wave`
- `Top Remediation Priority`
- `P0 Actions`
- `P1 Actions`
- `P2 Actions`
- `Local Spec Path`


### `Summary`

- Clear and fully overwrite the target range on each publish.
- Write header row plus 10 source rows and one overall portfolio verdict row.

### `Findings`

- Clear and fully overwrite the target range on each publish.
- Write normalized findings enriched with build-block status, correction owner, recommended correction, and readiness impact.

### `Cross-File Synthesis`

- Clear and fully overwrite the target range on each publish.
- Write synthesized items derived from `ASSESSMENT_ENHANCED.md`, including critical blockers and overall readiness verdict.

## Why this schema fits the source set

- One-row-per-file is too coarse for the breadth of findings in the coupon, GPT, and RAF documents.
- One-row-per-finding only would make it harder to prove full 10-file coverage quickly.
- Hybrid tabs satisfy both auditability and high-level scanning.

## Mapping to local artifacts

- Inventory and execution evidence: `EXECUTION_NOTES.md`
- Per-file enhanced assessment and cross-file readiness synthesis: `ASSESSMENT_ENHANCED.md`
- Feature delta analysis: `ASSESSMENT_FEATURE_DELTA.md`
- Remediation blueprint: `REMEDIATION_SPEC.md`
- Canonical consolidated report: `MASTER_ASSESSMENT.md`
- Earlier draft / working notes: `ASSESSMENT_DRAFT.md`
- Raw extracted sources: `artifacts/*.md`

## Blocked live steps

No live steps remain blocked.

Completed with `tdt-sheets`:

- Read spreadsheet metadata and existing tabs
- Created and populated `Summary`, `Findings`, and `Cross-File Synthesis` tabs
- Verified the written result by reading back populated ranges
