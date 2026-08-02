## Why

The `May-submission-assessment` Google Sheet currently uses a manual-development estimation model (`ScreenBase Hours (1P)`, `Platform (x2)`, `Coordination`, `Final Hours (2P)`, `Use AI(2P)`). This model was designed for human developers building features on one platform at a time.

With the AI-driven mobile feature pipeline now active, the estimation model must reflect three distinct phases with different actors: spec preparation (human), implementation generation (AI, simultaneous iOS + Android), and per-platform verification (human). The model also needs to capture spec metadata — tier, status, AI iteration loops, token budget — as the primary estimation driver, not raw function-level hour estimates.

The sheet must also serve as the **output sink** for the AI: the AI reads this OpenSpec's `design.md` to understand the expected format, then fills in projected estimates and actuals directly into the sheet.

## What Changes

- Replace the current estimation tab (gid=615805776) column layout entirely.
- Replace 7 columns (`ScreenBase Hours (1P)`, `Platform (x2)`, `Coordination`, `Final Hours (2P)`, `Use AI(2P)`, `QA Effort`) with a new 7-column spec-driven layout (`Function`, `Spec Preparation (1P)`, `Implementation Generation`, `iOS Verification`, `Android Verification`, `Coordination`, `QA Effort`).
- Add a Spec Metadata row above each feature block with: Spec Title, Spec Owner, Spec Status, Complexity Tier, AI Iteration Loops (est), AI Token Budget (est).
- Add auto-formulas for Total row hours via `=SUM(...)`.
- Create a new `Legend` tab documenting the estimation methodology.
- Preserve URS links, feature names, function rows, SIT rows, and total rows from the current tab.

## Capabilities

### New Capabilities
- `spec-driven-mobile-estimation`: A sheet-based estimation and tracking model for AI-driven mobile feature development. The AI reads the OpenSpec design, generates iOS + Android from specs, and logs projected estimates and actuals into the sheet.

### Modified Capabilities
- None.

## Impact

- Affected area: the `May-submission-assessment` Google Sheet tab (gid=615805776) and a new `Legend` tab in the same spreadsheet.
- Dependencies: the `assess-may-submission-urs` OpenSpec change must be complete; the sheet must be accessible via `tdt-sheets`.
- Non-goals: no application code changes in any mobile repo; no Jira integration; no changes to the `tdt-sheets` library itself.
