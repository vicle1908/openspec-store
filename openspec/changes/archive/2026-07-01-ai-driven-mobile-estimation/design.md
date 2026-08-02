## Context

The `May-submission-assessment` Google Sheet at `https://docs.google.com/spreadsheets/d/1_MIasMUIaDwauGsmSIQPiC7allQLDOxm9aW_t5a2vbk/edit?gid=615805776` contains the May Submission URS (Q3 2026) feature list with estimation data. The current tab (gid=615805776) uses a manual-development column format that does not reflect the AI-driven mobile feature pipeline.

This design specifies the replacement format. The sheet is the output sink: the AI reads `design.md` to understand the format, then fills in projected estimates and actuals.

## Goals / Non-Goals

**Goals:**
- Replace the current 7-column manual-dev format with a 7-column spec-driven format (same column count, different semantics).
- Add Spec Metadata rows that serve as fast sprint-planning inputs (tier, status, AI loops, token budget).
- Add an auto-formula for the Total row so hours accumulate correctly.
- Create a `Legend` tab that documents the methodology for human reviewers and future AI sessions.
- Preserve existing function rows, URS links, SIT rows, and total rows.

**Non-Goals:**
- Do not modify any mobile application code.
- Do not change the `tdt_core` / `tdt-sheets` libraries.
- Do not add Jira integration.

## Decisions

### Column layout

**Decision:** Replace the current 7-column layout with this 7-column spec-driven layout:

| Col | Header | Type | Actor | Notes |
|---|---|---|---|---|
| A | `Function` | input | human | unchanged |
| B | `Spec Preparation (1P)` | input | human | hours to draft + finalize spec from URS |
| C | `Implementation Generation` | input | AI/human | AI effort estimate, both platforms (includes both code generation + AI's own iteration overhead) |
| D | `iOS Verification` | input | human | review + CI pass |
| E | `Android Verification` | input | human | review + CI pass |
| F | `Coordination` | input | human | cross-platform sync + merge |
| G | `QA Effort` | input | QA | unchanged from current |

Auto-calculated on the Total row only:
- `Total Spec Prep`, `Total Impl Gen`, `Total iOS Verif`, `Total Android Verif`, `Total Coord` via `=SUM(...)`

**Rationale:** The 3-phase model (spec, implementation, verification) directly maps to the pipeline actors. `Implementation Generation` is one column because AI reads the spec once and generates both platforms simultaneously — this is the key efficiency insight. Verification is split per-platform because iOS and Android may have different iteration counts and pass rates.

**Why no `AI Reduction %` column:** the AI effort is already visible as `Implementation Generation` (col C). Adding a derived percentage column gives the same information in a redundant form, and creates an implicit promise that "AI will reduce hours" — which is not always true (negative reduction occurs when AI iteration exceeds manual baseline). Reviewers comparing C against the human-effort columns (B + D + E + F) already see the AI's relative cost at a glance. We keep `Implementation Generation` small when AI is fast, and large when AI iterates heavily — that's the single source of truth for AI cost in this model.

### Spec Metadata row

**Decision:** Insert a metadata row above each feature's column header row with 6 fields:

| Cell | Values | Notes |
|---|---|---|
| Spec Title | free text | e.g. "PhillipGPT on POEMS" |
| Spec Owner | free text | e.g. "Ronnie" |
| Spec Status | `draft` / `finalized` / `impl-ready` | drives AI readiness |
| Complexity Tier | `S` / `M` / `L` / `XL` | sprint-level planning |
| AI Iteration Loops (est) | integer | generate / review / fix cycles |
| AI Token Budget (est) | USD or token count | cost projection |

**Rationale:** Spec metadata is the fast input for sprint planning. Tier classification at spec-finalization time is faster than function-level hour estimates and provides sufficient granularity for velocity tracking.

### Tier classification guide

| Tier | Criteria | Example from current sheet |
|---|---|---|
| `S` | 1 screen, 1 API, no new models | toggle a feature flag |
| `M` | 2-3 screens, 2-3 APIs, new models | OTP dialog integration |
| `L` | 4+ screens, cross-module, new navigation | PhillipGPT integration |
| `XL` | Platform APIs, real-time, auth flows | reCAPTCHA SDK integration |

### Sheet row layout

```
Row 1: Title (existing)
Row 2: (blank)
Row 3: Feature name | URS link (existing)
Row 4: Spec Metadata row (new)
Row 5: Column headers (replaced)
Row 6+: Function rows (existing function text, new columns)
... SIT row ...
... Total row ...
```

### Legend tab

**Decision:** Create a new `Legend` sheet tab with:
1. Column definitions — what each column means, who fills it, when
2. Tier classification criteria — S/M/L/XL with examples
3. Spec metadata field guide — what each field means, valid values
4. AI pipeline workflow — how AI reads spec metadata to generate code

**Rationale:** The Legend tab serves as the contract between human reviewers and AI sessions. It ensures both actors interpret the columns and metadata consistently.

## Risks / Trade-offs

**Risk:** Removing `Platform (x2)` loses the explicit iOS vs Android hour breakdown.
**Mitigation:** Per-platform verification columns (D and E) preserve iOS/Android differentiation for the verification phase. The implementation phase (C) covers both platforms with one estimate — this is intentional as it reflects the simultaneous generation model.

**Risk:** Without `AI Reduction %` displayed in the sheet, sprint velocity may not surface AI efficiency directly.
**Mitigation:** Each Total row still computes `Total Implementation Generation` and `Total Human Effort` (sum of B + D + E + F) via `=SUM(...)`. Reviewers compare those two numbers to see AI's relative cost per feature. Aggregate velocity is captured by the per-feature totals across the tab.

**Risk:** Spec Metadata rows need manual population by humans before AI can use them.
**Mitigation:** Tier and status are fast to fill (seconds per feature). The AI can proceed with generation using estimated defaults if metadata is missing.

## Open Questions

- Should the AI log actual token counts and iteration loops after generation, so the sheet accumulates calibration data?
- Should there be a separate "actual" column for each phase (filled post-implementation), distinct from the projected estimate column?
