# AI-Driven Mobile Estimation Tasks

## 1. OpenSpec Artifacts

- [x] 1.1 Create `openspec/changes/ai-driven-mobile-estimation/` directory with `.openspec.yaml`, `proposal.md`, `design.md`, `tasks.md`

## 2. Sheet Schema Update

- [x] 2.1 Read the current tab (gid=615805776) via `tdt-sheets` to confirm current structure and URS links are intact
- [x] 2.2 Replace Row 5 column headers from 7-column manual format to 7-column spec-driven format (Function, Spec Preparation (1P), Implementation Generation, iOS Verification, Android Verification, Coordination, QA Effort)
- [x] 2.3 Add auto-formula for Total row hours = `=SUM(B:F)` per column on the Total row only

## 3. Spec Metadata Rows

- [x] 3.1 Insert Spec Metadata row above column headers for Trade Ticket Lite Mode (Tier L, draft, 3 loops, $2.00)
- [x] 3.2 Insert Spec Metadata row for PhillipGPT on POEMS (Tier L, finalized, 2 loops, $0.50)
- [x] 3.3 Insert Spec Metadata row for Google ReCaptcha Phase 1 (Tier XL, draft, 4 loops, $3.00)
- [x] 3.4 Insert Spec Metadata row for Google ReCaptcha Phase 2 (Tier XL, draft, 3 loops, $2.50)
- [x] 3.5 Insert Spec Metadata row for Smart Portfolio Phase 2 (Tier L, draft, 3 loops, $2.00)
- [x] 3.6 Defer Gami - Amalgamated Trade (status: NOT READY → Spec Status=draft, Loops=4, Budget=$3.00)

## 4. Legend Tab

- [x] 4.1 Create new sheet tab named `Legend`
- [x] 4.2 Populate Legend with column definitions, tier guide, formula docs, metadata guide, pipeline workflow

## 5. Pilot Validation

- [x] 5.1 Fill projected values for PhillipGPT on POEMS function rows using new column layout
- [x] 5.2 Fill Spec Metadata row for PhillipGPT: Tier M [actually L per latest update], Status finalized, AI Loops 2, Token Budget $0.50
- [x] 5.3 Verify Total row `=SUM(...)` formulas compute correctly

## 6. Verification

- [x] 6.1 Run `openspec validate --strict` on the new change → passes
- [x] 6.2 Confirm the sheet tab reflects all updates (7 columns, no `AI Reduction %` column)
