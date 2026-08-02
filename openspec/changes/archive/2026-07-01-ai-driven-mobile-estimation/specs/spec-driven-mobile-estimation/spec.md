# spec-driven-mobile-estimation Specification

## ADDED Requirements

### Requirement: Column layout — 7-column spec-driven format

The `Ready_Project_Est_Spec_driven` tab SHALL present estimation rows using a 7-column layout, replacing the previous manual-development layout. The columns, in order, SHALL be:

| Col | Header                            | Type   | Actor     |
|-----|-----------------------------------|--------|-----------|
| A   | `Function`                        | input  | human     |
| B   | `Spec Preparation (1P) (Man day)` | input  | human     |
| C   | `Implementation Generation`       | input  | AI/human  |
| D   | `iOS Verification`                | input  | human     |
| E   | `Android Verification`            | input  | human     |
| F   | `Coordination (Man day)`          | input  | human     |
| G   | `QA Effort`                       | input  | QA        |

Column headers SHALL be placed on the row immediately following each feature's Spec Metadata row. The previous `AI Reduction %` column SHALL NOT appear in the new layout — `Implementation Generation` (column C) is the single source of truth for AI cost and effort.

#### Scenario: Tab uses the 7-column spec-driven header layout
- **WHEN** an operator opens `Ready_Project_Est_Spec_driven` and inspects a feature's column header row
- **THEN** row 5 (for the first feature) SHALL contain the seven headers above, in that order, with no `AI Reduction %` column
- **AND** each subsequent feature's column-header row SHALL match the same layout

#### Scenario: Row 1 title is preserved
- **WHEN** an operator inspects the tab
- **THEN** row 1 SHALL still carry the `May Submission URS (Q3 2026) — 11 Projects, Spec-Driven Estimation` title
- **AND** previously captured URS links and feature name rows SHALL remain intact

### Requirement: Spec Metadata rows per feature

Each feature block in the `Ready_Project_Est_Spec_driven` tab SHALL be preceded by a Spec Metadata row with 6 fields. The fields, in cell order, SHALL be:

- **A:** `[Spec Metadata]` (sentinel)
- **B:** Spec Title (free text)
- **C:** Spec Owner (free text)
- **D:** Spec Status — `draft` / `finalized` / `impl-ready`
- **E:** Complexity Tier — `S` / `M` / `L` / `XL`
- **F:** AI Iteration Loops (est) — integer
- **G:** AI Token Budget (est) — USD or token count

The metadata row SHALL appear immediately above the feature's column-header row.

#### Scenario: Each feature has a Spec Metadata row with 6 fields
- **WHEN** an operator inspects any feature block
- **THEN** the row immediately above its column-header row SHALL have `[Spec Metadata]` in column A
- **AND** columns B–G SHALL carry the Spec Title, Spec Owner, Spec Status, Complexity Tier, AI Iteration Loops, and AI Token Budget fields respectively

#### Scenario: Deferred features have a NOT READY status
- **WHEN** a feature is not yet ready for development (e.g. `Gami - Amalgamated Trade`)
- **THEN** its Spec Status SHALL be `draft`
- **AND** the row's feature-name line SHALL annotate `(NOT READY)` so reviewers can filter it out

### Requirement: Total row formulas

The Total row for each feature block SHALL contain `=SUM(...)` formulas on columns B–F that sum the corresponding column from the function rows above. Column G (`QA Effort`) is intentionally not summed by `=SUM(...)` because it carries qualitative values (e.g. `tbc`) rather than numeric hours.

#### Scenario: Total row computes via SUM formula
- **WHEN** an operator inspects the Total row of any feature
- **THEN** cells B–F SHALL contain formulas of the form `=SUM(B<first>:B<last>)` (and analogous for C, D, E, F)
- **AND** the rendered numeric value SHALL equal the sum of the function rows above

#### Scenario: QA Effort column is not summed
- **WHEN** the operator reads the Total row
- **THEN** cell G SHALL NOT contain a `=SUM(...)` formula
- **AND** the qualitative QA Effort value SHALL be left blank (or `tbc` pending)

### Requirement: Legend tab

The spreadsheet SHALL contain a separate `Legend` tab that documents the methodology. The Legend tab SHALL include four sections:

1. **Column Definitions** — what each column means, who fills it, when
2. **Spec Metadata Field Guide** — meaning and valid values for each Spec Metadata field
3. **Tier Classification Guide** — `S` / `M` / `L` / `XL` criteria with examples
4. **AI Pipeline Workflow** — how AI reads Spec Metadata to drive code generation

#### Scenario: Legend tab exists with all four sections
- **WHEN** an operator opens the spreadsheet's tab list
- **THEN** a tab named `Legend` SHALL be present
- **AND** the Legend tab SHALL contain sections for Column Definitions, Spec Metadata Field Guide, Tier Classification Guide, and AI Pipeline Workflow

### Requirement: Existing data preserved

The migration SHALL preserve all URS links, feature names, function row text, and existing pilot-function values. No previously captured row may be deleted; only column headers and any structural inserts (Spec Metadata rows, formulas) may be modified.

#### Scenario: Function row text and URS links are retained
- **WHEN** the operator compares the migrated tab to the pre-migration state
- **THEN** every original function row's text SHALL still be present in column A
- **AND** every URS link embedded in feature-name rows SHALL still be a clickable link
- **AND** SIT rows and their values SHALL remain at the end of each feature block, immediately above the Total row

### Requirement: Pilot function rows filled

For each feature whose Spec Status is `finalized` (or that has reached pilot validation), the function rows SHALL contain projected hour values matching the new column layout (one numeric value per B/C/D/E/F column).

#### Scenario: Finalized features have populated function rows
- **WHEN** an operator inspects a feature whose Spec Status is `finalized` or `impl-ready`
- **THEN** each function row SHALL have numeric values in columns B–F
- **AND** column G SHALL either hold a numeric QA Effort value or the placeholder `tbc`
