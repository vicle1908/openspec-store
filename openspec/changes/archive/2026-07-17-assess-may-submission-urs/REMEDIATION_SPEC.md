# May Submission URS Remediation Spec

This document converts the assessment into a document-improvement blueprint. For each source, it specifies exactly what to add, split, or rewrite so the URS can become a build-ready contract.

## Remediation Model

Each document is evaluated using the following improvement contract:

### Required section types

- **Current-State Summary** — what exists today and is assumed baseline
- **Target-State Change** — what this document is trying to add or modify
- **What Stays Unchanged** — explicit non-changes to reduce implementation drift
- **System Boundaries / Ownership** — which systems and teams own each part
- **State Model / Workflow Contract** — canonical transitions, triggers, and error paths
- **Acceptance Criteria** — testable feature outcomes
- **Migration / Rollout Notes** — how to move from current to target safely
- **Open Questions / BA Follow-up** — unresolved issues to close before build

### Remediation priority levels

- **P0** — must be corrected before engineering starts
- **P1** — should be corrected during planning / before detailed design
- **P2** — quality/documentation improvement; not blocking initial build

---

## Per-Document Remediation Spec

### 1. Gami - Amalgamated Trade.pdf

**Document role**
- Existing capability formalization and rule hardening for coupon/rebate processing.

**Primary problems**
- Missing explicit cutoff/timing contract.
- Missing exception ownership.
- Missing definition of grouped-trade trigger.

**Required changes**

**P0**
1. Add a `Current-State Summary` section describing the existing rebate lifecycle at a business level.
2. Add a `Target-State Change` section describing exactly what this URS changes versus current behavior.
3. Add a `Cutoff and Timing Rules` section with:
   - cutoff timestamp definition,
   - batch window definition,
   - end-of-day handling,
   - same-day grouping rule,
   - late-settlement rule.
4. Add an `Exception Handling` section covering:
   - partial settlement,
   - missing coupon eligibility,
   - downstream rejection,
   - retry/not-retry decision.

**P1**
5. Add a `System Ownership` section for P3 vs downstream rebate fulfillment owner.
6. Add a `What Stays Unchanged` section to limit unintended rework.

**P2**
7. Add explicit examples of grouped vs non-grouped trade cases.

**Target revised outline**
- Purpose
- Current-State Summary
- Target-State Change
- Business Rules
- Cutoff and Timing Rules
- Exception Handling
- Ownership / System Boundaries
- What Stays Unchanged
- Acceptance Criteria

---

### 2. Gami - Cash Coupon Global Admin.pdf

**Document role**
- Workflow formalization and state-model refactor for back-office coupon approval.

**Primary problems**
- Critical state conflict (`pending` vs `rejected`).
- Missing GBO error-notification contract.
- Template placeholders reduce trustworthiness.

**Required changes**

**P0**
1. Add a `Canonical Coupon State Model` section with a single lifecycle table:
   - `pending`
   - `approved`
   - `rejected`
   - `processing`
   - `gbocall`
   - `settled`
   - `error`
   - `retry`
2. For each state define:
   - owner,
   - entry trigger,
   - visible actor,
   - exit transition.
3. Rewrite any contradictory wording so P3 and Global Admin use the same state names.
4. Add a `GBO Error Notification Contract` section with:
   - trigger condition,
   - recipients,
   - delivery channel,
   - SLA,
   - retry/escalation rule.
5. Remove all template placeholders and incomplete metadata.
6. **New from grooming:** add `Reconciliation Policy` (retry/timeout, mark-as-failed/rejected fallback) and `External System Update Timing Rule` (Mambu/member view update only on `settled`).

**P1**
6. Add a `Current Operational Flow` section to describe legacy/current process.
7. Add a `Target Systemized Flow` section showing what the admin workflow standardizes.
8. Add an `Operational Manual Handling` section for rejected cases.

**P2**
9. Add example state transition scenarios.

**Target revised outline**
- Purpose
- Current Operational Flow
- Target Systemized Flow
- Canonical Coupon State Model
- Approval / Rejection Workflow
- GBO Error Notification Contract
- Manual Handling Rules
- Acceptance Criteria

---

### 3. ITSR 330853 Refer A Friend URS Revised 1.1.pdf

**Document role**
- Existing feature plus change-request pack.

**Primary problems**
- Baseline and requested delta are mixed together.
- Wrong purpose/template text.
- No clean CR decomposition.

**Required changes**

**P0**
1. Rewrite the `Purpose` section so it refers to Refer A Friend only.
2. Split document into two major parts:
   - `Baseline Capability (Current State)`
   - `Requested Changes (Target State)`
3. Under `Requested Changes`, create one subsection per enhancement:
   - eligibility blocking,
   - invite history,
   - progress display,
   - coupon status,
   - reward notifications,
   - tooltips.
4. Add separate acceptance criteria for each requested enhancement.

**P1**
5. Add a `Campaign Ownership / Authoring` section clarifying who creates campaigns and who approves them.
6. Add `What Stays Unchanged` for existing referral mechanics.

**P2**
7. Add a release-history note so already-done stories are tracked but not confused with pending scope.

**Target revised outline**
- Purpose
- Baseline Capability (Current State)
- Requested Changes (Target State)
  - CR-01 Eligibility Blocking
  - CR-02 Invite History
  - CR-03 Progress Display
  - CR-04 Coupon Status
  - CR-05 Reward Notifications
  - CR-06 Tooltips
- Campaign Ownership / Authoring
- What Stays Unchanged
- Acceptance Criteria by CR

---

### 4. ITSR 369004 SMART Portfolio Phase 2.pdf

**Document role**
- Existing-feature modernization with concrete field-level deltas.

**Primary problems**
- Weak metadata/glossary.
- Loose phase naming references.

**Required changes**

**P1**
1. Add a `Current-State PMIP Flow` summary.
2. Add a `Target-State CQB4 Delta` section listing only the new/changed rules.
3. Add a `What Stays Unchanged` section for inherited PMIP behavior.
4. Clarify relationship between this phase and earlier SMART Portfolio phases.
5. **New from grooming:** add `Payment Redirect Contract` (PayNow/eGIRO/internal transfer), `eGIRO Return Flow` (webview callback/deep link), `Failure / Cancel Flows`, `RSP State Transition Table` (Pending/Active/Suspended/Restarted/Amended/Ended), and clarify suspend = stop future deductions, plan remains restartable.

**P2**
5. Complete glossary and metadata.
6. Add test examples for uniqueness and decimal precision.

**Target revised outline**
- Purpose
- Current-State PMIP Flow
- Target-State CQB4 Delta
- Field Validation Rules
- What Stays Unchanged
- Acceptance Criteria
- Phase Naming / Release Context

---

### 5. ITSR [369574] RECAPTCHA TO REPLACE GEETESTv1.0.pdf

**Document role**
- Current-state control replacement with phased rollout.

**Primary problems**
- Admin portal phase-2 boundary unclear.
- Migration/fallback path should be more explicit.

**Required changes**

**P0**
1. Add a `Current-State Protection Model` section describing GeeTest + existing OTP abuse controls.
2. Add a `Target-State Protection Model` section describing invisible reCAPTCHA + SMS Defender.
3. Add a `Migration and Rollback` section with:
   - cutover strategy,
   - fallback trigger,
   - comparison/monitoring period,
   - observability requirements.
4. Add a `Phase 2 Admin Portal Scope` section defining intervention boundary, ownership, and trigger cases.

**P1**
5. Add a `What Stays Unchanged` section for auth/OTP flows not impacted by this change.

**P2**
6. Complete glossary/committee sections.

**Target revised outline**
- Purpose
- Current-State Protection Model
- Target-State Protection Model
- Phase 1 Scope
- Phase 2 Scope
- Migration and Rollback
- Admin Portal Intervention Rules
- Acceptance Criteria

---

### 6. Phillip GPT on POEMS v1.0.pdf

**Document role**
- New capability on top of existing platform.

**Primary problems**
- Product UX and compliance policy are blended.

**Required changes**

**P1**
1. Add a `Platform Dependencies` section describing current platform assumptions.
2. Split the document logically into:
   - `Product Experience Contract`
   - `Compliance / Safety Contract`
3. Add a `Rollout / Gating Strategy` section for flags, source selection, and enablement boundaries.

**P2**
4. Add a `Regression Boundaries` section specifying what existing screens/flows must remain unaffected.
5. Add analytics and disclaimer telemetry acceptance criteria if not already explicit enough.

**Target revised outline**
- Purpose
- Platform Dependencies
- Product Experience Contract
- Context Passing Contract
- Compliance / Safety Contract
- Rollout / Gating Strategy
- Analytics / Telemetry
- Acceptance Criteria

---

### 7. URS_P3_Stock Trade ticket - Lite mode.pdf

**Document role**
- New feature variant layered onto existing trade ticket capability.

**Primary problems**
- Lite-to-Pro transition edge case is underspecified.

**Required changes**

**P0**
1. Add explicit `Mode Transition Contract` (reset/retention matrix per field, default reset for safety).
2. Add explicit `Persistence Behavior` (device-level storage; multi-account note; new device → Pro).
3. Add explicit `Event Tracking Spec` (Light vs Pro event on Review Order; GA4 primary, Firebase TBD).
4. Add `Market Behavior Rules` (SG limit-focused; US/HK market order available; default currency = traded market; fallback SGD for non-multi-currency accounts).
5. Add `Order-Type Support Matrix` (Light: Limit + Market-eligible; Pro: advanced orders including stop limit, limit-if-touched).

**P1**
6. Document `Performance Strategy` decision (partial reload vs full refresh — pending dev feasibility analysis).
7. Document `Multi-Account UX Risk` and proposed mitigations.

**P2**
8. Add analytics acceptance criteria for Lite vs Pro usage comparison.
9. Add `What Stays Unchanged` for validation/business-rule core.

**Target revised outline**
- Purpose
- Current-State Pro Ticket Baseline
- Lite Mode Delta
- Market-Specific Rules
- Mode Transition Rules
- Persistence Rules
- Telemetry / Analytics
- Acceptance Criteria

---

### 8. UT Enhancements - Phase 2 2026.pdf

**Document role**
- Enhancement bundle / backlog container.

**Primary problems**
- Open-ended scope wording.
- Uneven detail across multiple enhancements.

**Required changes**

**P0**
1. Replace open-ended discovery wording with an explicit itemized backlog.
2. Split the document into one subsection per enhancement:
   - UT-01 CKA/CAR reporting fix
   - UT-02 Fund Screener
   - UT-03 Automated UT news updates
   - UT-04 Chart filter minute/hour hiding
3. Add a current-state problem statement and target-state outcome for each enhancement.
4. Add acceptance criteria for each enhancement.

**P1**
5. Add a `Not in Scope` section to stop uncontrolled scope growth.
6. Add owner/system impact per enhancement.

**P2**
7. Add rollout sequencing notes if items are not intended to ship together.

**Target revised outline**
- Purpose
- Enhancement Backlog Overview
- UT-01 CKA/CAR reporting fix
- UT-02 Fund Screener
- UT-03 Automated UT news updates
- UT-04 Chart filter minute/hour hiding
- Not in Scope
- Acceptance Criteria by enhancement

---

### 9. WM - Accredited Investor Form.pdf

**Document role**
- Existing business process with target channel/surface migration.

**Primary problems**
- Native vs iframe/web ownership boundary unclear.

**Required changes**

**P0**
1. Add a `Current-State Access Model` section describing today’s web/iframe baseline.
2. Add a `Target-State P3 Entry Experience` section describing the Me-tab exposure and user journey.
3. Add a `System Ownership` section defining:
   - native shell owner,
   - form-rendering owner,
   - eligibility-validation owner,
   - reminder/notification owner.

**P1**
4. Add `What Stays Unchanged` for AI criteria and renewal business rules.
5. Add explicit acceptance criteria for joint-account handling.

**P2**
6. Complete metadata/glossary.

**Target revised outline**
- Purpose
- Current-State Access Model
- Target-State P3 Entry Experience
- Business Eligibility Rules
- Ownership / System Boundaries
- Reminder / Renewal Rules
- Acceptance Criteria

---

### 10. CashCOupon.drawio

**Document role**
- System-flow baseline and alignment diagram for coupon-family integration.

**Primary problems**
- Terminology not fully aligned with URS text.
- Late failure/recovery paths need explicit narrative pairing.

**Required changes**

**P0**
1. Create a companion text section or note describing the canonical state names used by the diagram.
2. Align diagram labels with the same lifecycle terminology used in coupon URS text.
3. Add explicit failure/recovery path notes for scheduled scans, status checks, and retry behavior.

**P1**
4. Add a `Current-State Flow` vs `Target-State Flow` legend if the diagram mixes both.
5. Add owner/system responsibility annotations for each major lane.

**P2**
6. Add sequence-numbered narrative steps to improve auditability.

**Target revised companion structure**
- Diagram Purpose
- Canonical State Names
- Sequence Narrative
- Failure / Recovery Paths
- Owner / System Responsibility Legend

---

## Cross-Document Standardization Recommendations

### P0 Standardization

All weak or mixed docs should adopt these mandatory additions:
1. `Current-State Summary`
2. `Target-State Change`
3. `What Stays Unchanged`
4. `Acceptance Criteria`

### P1 Standardization

Integration-heavy docs should also add:
1. `System Boundaries / Ownership`
2. `Migration / Rollout Notes`
3. `Error / Exception Handling`

### P2 Standardization

Quality uplift for all docs:
1. remove placeholders,
2. complete metadata/glossary,
3. add examples or scenario tables,
4. add release-history context where helpful.

---

## Remediation Sequence

### Wave 1 — Blocking corrections
1. `Gami - Cash Coupon Global Admin.pdf`
2. `ITSR 330853 Refer A Friend URS Revised 1.1.pdf`
3. `UT Enhancements - Phase 2 2026.pdf`
4. `WM - Accredited Investor Form.pdf`
5. `CashCOupon.drawio`

### Wave 2 — Contract hardening
1. `Gami - Amalgamated Trade.pdf`
2. `ITSR [369574] RECAPTCHA TO REPLACE GEETESTv1.0.pdf`
3. `ITSR 369004 SMART Portfolio Phase 2.pdf`

### Wave 3 — Quality optimization
1. `Phillip GPT on POEMS v1.0.pdf`
2. `URS_P3_Stock Trade ticket - Lite mode.pdf`

---

## Final Remediation Verdict

The highest-value improvement is not rewriting every URS from scratch. It is systematically adding the same missing contract layers:

- baseline vs target separation,
- canonical state/workflow definitions,
- system ownership,
- and testable acceptance criteria.

If those layers are added in the priority order above, the folder can move from a research artifact to a dependable engineering handoff set.
