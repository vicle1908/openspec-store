# May Submission URS Assessment — Feature Delta Addendum

This addendum extends `ASSESSMENT_ENHANCED.md` by separating **current-state features** from **targeted features / requested changes** so teams can reason about what is already part of the baseline capability versus what each source is attempting to introduce, refine, or correct.

## Evaluation Lens

### Current-state feature

A feature, workflow, behavior, or system interaction that appears to already exist in the ecosystem, either because the source describes it as an established workflow, assumes it as pre-existing context, or frames the document as enhancing/modifying rather than creating it from scratch.

### Targeted feature

A feature, workflow, correction, rollout phase, or UX/system change that the source explicitly wants to add, revise, replace, extend, or operationalize.

### Why the distinction matters

The May Submission source set mixes:

- documents that mainly describe **new target-state behavior**,
- documents that refine an **existing current-state feature**,
- and documents that blur current-state and target-state behavior inside the same source.

That distinction materially affects:

1. **readiness** — documents that mix baseline and target behavior are harder to implement safely,
2. **scoping** — teams need to know whether a requirement is net-new or a change request,
3. **migration planning** — target features often depend on legacy/current-state compatibility,
4. **test planning** — current-state regressions and future-state ACs must be validated differently.

---

## Per-File Current vs Target Assessment

### Gami - Amalgamated Trade.pdf

**Current-state features identified**
- Coupon/rebate flow already exists as an operational concept.
- Settled trades already participate in a reward/rebate treatment.
- Downstream processing and batching already appear to exist in some form.

**Targeted features / changes identified**
- Clarify or formalize grouped same-day trade rebate handling.
- Clarify downstream timing/cutoff behavior into explicit buildable rules.
- Tighten exception behavior and ownership around partial settlements and timing edge cases.

**Assessment**
- This source reads less like a net-new product capability and more like a formalization of an existing rewards flow.
- The document is currently weak because it assumes the baseline flow is already understood but does not fully contract the target clarifications it expects engineering to implement.

**Planning implication**
- Treat as **existing capability formalization + rule hardening**, not a pure net-new feature.
- Best next step: extract the actual current production lifecycle from P3/GBO/coupon flow owners and reconcile it against the target rule wording.

---

### Gami - Cash Coupon Global Admin.pdf

**Current-state features identified**
- A coupon data exchange between P3 and a back-office/admin process likely already exists or is expected as current operational behavior.
- Marketing approval/rejection is framed as part of an existing operational control layer.
- GBO crediting is treated as an established downstream fulfillment step.

**Targeted features / changes identified**
- Introduce or formalize the Global Admin approval workflow as a system-contract surface.
- Expose explicit rejection/approval handling semantics.
- Define operational error notification path from GBO back to marketing.

**Assessment**
- This source sits at the boundary of current operational practice and target systemization.
- The biggest problem is that it appears to document a target-state approval workflow while still leaking legacy/current-state status semantics from P3.

**Planning implication**
- Treat as **workflow formalization + state model refactor**.
- Before implementation, document the current actual state model in P3 and define the target canonical state machine the new admin flow should enforce.

---

### ITSR 330853 Refer A Friend URS Revised 1.1.pdf

**Current-state features identified**
- Refer A Friend campaign capability already exists at least partially.
- Campaign creation, referral participation, and reward monitoring already appear in baseline form.
- Some user stories in the source are explicitly framed as already done.

**Targeted features / changes identified**
- Eligibility blocking.
- Invite history updates.
- Progress display.
- Coupon status display.
- Reward notifications.
- Tooltips and UX refinements.

**Assessment**
- This is the clearest example of a document that mixes baseline capability with target-state change requests.
- The main readiness problem is not missing domain intent; it is the failure to cleanly separate **what exists now** from **what is being requested next**.

**Planning implication**
- Treat as **current feature + CR pack**, not as a single coherent net-new URS.
- Split into:
  1. baseline capability summary,
  2. delta CR list,
  3. acceptance criteria for each target enhancement.

---

### ITSR 369004 SMART Portfolio Phase 2.pdf

**Current-state features identified**
- PMIP flow and Smart Portfolio ecosystem already exist.
- CQB/P3 form patterns already exist.
- e-Giro journey already exists as surrounding context.

**Targeted features / changes identified**
- Move PMIP form into CQB4.
- Enforce account uniqueness in PMIP form.
- Auto-populate account holder name.
- Add/standardize mandatory fund source behavior.
- Enforce decimal precision for collection amount.

**Assessment**
- This is a classic **existing feature modernization / structured enhancement** document.
- The document is relatively strong because the current baseline is obvious and the targeted deltas are concrete.

**Planning implication**
- Treat as **phase enhancement on an existing feature**, not a greenfield workflow.
- Validation should focus on regression of current PMIP behavior plus delta acceptance tests for CQB4-specific rules.

---

### ITSR [369574] RECAPTCHA TO REPLACE GEETESTv1.0.pdf

**Current-state features identified**
- Existing OTP protection and anti-abuse controls already exist.
- GeeTest is the current baseline CAPTCHA/protection mechanism.
- Registered-user and account-holder auth/OTP flows already exist.

**Targeted features / changes identified**
- Replace GeeTest with Google invisible reCAPTCHA.
- Add SMS Defender as part of the protection model.
- Roll out in two phases.
- Make protection configurable without redeployment.
- Extend controls into admin portal/account-holder contexts in phase 2.

**Assessment**
- This is a well-defined **replacement / migration feature** anchored on an existing current-state control plane.
- The key implementation risk is migration architecture, not business ambiguity.

**Planning implication**
- Treat as **current-state replacement with phased rollout**.
- Implementation planning should explicitly include migration safety, fallback, observability, and old-vs-new protection comparators.

---

### Phillip GPT on POEMS v1.0.pdf

**Current-state features identified**
- P3/P2Web screen architecture already exists.
- User identity/session/context parameters already exist in surrounding systems.
- Feature flag patterns already exist in the ecosystem.
- Compliance/risk review expectations already exist as organizational constraints.

**Targeted features / changes identified**
- Introduce Ask AI entry points across targeted screens.
- Load GPT experience with contextual iframe parameters.
- Track disclaimer acceptance/display per user/platform.
- Gate feature by source/flags.
- Define safe response structure and multi-intent handling.

**Assessment**
- This is a strong **new capability on top of an existing platform surface**.
- It is not a simple CR; it introduces a meaningful new AI feature while leveraging current platform structure.

**Planning implication**
- Treat as **new product capability on established platform**.
- Plan should separate: platform embedding, context passing, compliance policy, rollout controls, and model-source governance.

---

### URS_P3_Stock Trade ticket - Lite mode.pdf

**Current-state features identified**
- Existing Pro trade ticket already exists.
- Market-specific order-type rules already exist.
- Device persistence and telemetry patterns likely already exist on platform.

**Targeted features / changes identified**
- Introduce Lite Mode as simplified trade ticket UX.
- Restrict surface to simpler fields and order types.
- Persist preferred mode and section expansion state.
- Add comparative telemetry for Lite vs Pro behavior.

**Assessment**
- This is a clear **target UX mode layered onto an existing current-state trading feature**.
- The baseline/current-state is well understood; the target mode is explicitly scoped.

**Planning implication**
- Treat as **existing feature variant / UX simplification layer**.
- Implementation should maintain shared validation core while swapping the presentation/state model.

---

### UT Enhancements - Phase 2 2026.pdf

**Current-state features identified**
- UT domain, reporting, charting, and news flows already exist.
- A number of known defects/pain points in the existing UT experience are implied.

**Targeted features / changes identified**
- Fix CKA/CAR reporting issue.
- Add Fund Screener.
- Automate UT news updates.
- Hide minutes/hours in UT chart filter.
- Potentially add more discovered enhancements.

**Assessment**
- This is a bundle of **current-state fixes and targeted enhancements**, but it is not framed as a clean change set.
- It behaves more like a backlog bucket than a single feature spec.

**Planning implication**
- Treat as **enhancement bundle / backlog container**, not as an implementation-ready URS.
- Break into separate targeted feature items, each with its own current-state problem statement and future-state acceptance criteria.

---

### WM - Accredited Investor Form.pdf

**Current-state features identified**
- Accredited investor criteria and periodic status lifecycle already exist as domain/business rules.
- A web/iframe-based form experience likely already exists.
- Reminder/distribution channels (email, MoEngage) already exist.

**Targeted features / changes identified**
- Bring the form access into P3 from the Me tab.
- Improve onboarding/renewal exposure in the native journey.
- Clarify support for individual and joint accounts in app flow.

**Assessment**
- This is a **channel migration / experience upgrade** for an already-existing business process.
- The business rules are stable; the real change is where/how the capability is surfaced.

**Planning implication**
- Treat as **existing business process + target delivery-surface migration**.
- Implementation planning should prioritize ownership of native shell vs web form engine vs backend criteria validation.

---

### CashCOupon.drawio

**Current-state features identified**
- Queue/listener architecture already exists or is at least assumed.
- GamiAPI, Mambo, GBO, TaskAPI, and P3DB interactions reflect an established operational flow.
- Retry/reconciliation behavior appears to exist in current or intended runtime design.

**Targeted features / changes identified**
- The diagram may be attempting to formalize/systematize current coupon/rebate behavior.
- It likely serves as the desired operational model that the text URS docs should align to.

**Assessment**
- This artifact is best treated as a **system-flow baseline / target alignment diagram** rather than a standalone feature request.
- Its value is highest when used to validate whether current behavior and target textual requirements agree.

**Planning implication**
- Use as the **canonical integration flow candidate** for coupon-family reconciliation.
- Compare against current implementation and textual URS state model before build or refactor work begins.

---

## Cross-File Feature Delta Analysis

### 1. Documents that are mainly target-new capability

These introduce a substantial new end-user or operator-facing feature on top of an existing platform:

- `Phillip GPT on POEMS v1.0.pdf`
- `URS_P3_Stock Trade ticket - Lite mode.pdf`

**Implication:** prioritize product rollout, UX acceptance, feature gating, and regression isolation from baseline platform behavior.

### 2. Documents that are mainly current-feature enhancements / formalizations

These refine, migrate, clarify, or harden an already-existing feature/process:

- `Gami - Amalgamated Trade.pdf`
- `Gami - Cash Coupon Global Admin.pdf`
- `ITSR 369004 SMART Portfolio Phase 2.pdf`
- `ITSR [369574] RECAPTCHA TO REPLACE GEETESTv1.0.pdf`
- `WM - Accredited Investor Form.pdf`
- `CashCOupon.drawio`

**Implication:** main risks are migration, state alignment, contract completeness, and regression against existing workflows.

### 3. Documents that mix current-state and target-state too heavily

These should be decomposed before engineering planning:

- `ITSR 330853 Refer A Friend URS Revised 1.1.pdf`
- `UT Enhancements - Phase 2 2026.pdf`

**Implication:** these are the least planning-ready because teams cannot cleanly distinguish baseline behavior from requested delta.

---

## Prioritized Correction Guidance by Feature Delta Type

### A. Current-state enhancement docs

For these documents, the main correction question is:

> “What exactly is changing relative to the current baseline?”

Mandatory correction pattern:
1. Add a **Current-State Summary** section.
2. Add a **Target-State Change** section.
3. Add a **What remains unchanged** section.
4. Add migration or compatibility notes where relevant.

Applies especially to:
- `Gami - Cash Coupon Global Admin.pdf`
- `ITSR [369574] RECAPTCHA TO REPLACE GEETESTv1.0.pdf`
- `WM - Accredited Investor Form.pdf`
- `ITSR 369004 SMART Portfolio Phase 2.pdf`

### B. New capability docs

For these documents, the main correction question is:

> “How does the new feature plug into current platform surfaces without ambiguity?”

Mandatory correction pattern:
1. Add explicit platform dependencies.
2. Add rollout/flag strategy.
3. Add regression boundaries versus current platform behavior.
4. Add analytics and compliance acceptance criteria if applicable.

Applies especially to:
- `Phillip GPT on POEMS v1.0.pdf`
- `URS_P3_Stock Trade ticket - Lite mode.pdf`

### C. Mixed baseline + CR docs

For these documents, the main correction question is:

> “What is already true today, and what exactly is being requested now?”

Mandatory correction pattern:
1. Split the doc into **Baseline Capability** and **Requested Delta**.
2. Mark each requested delta independently.
3. Remove already-done stories from the target acceptance criteria.
4. Produce itemized acceptance criteria per delta feature.

Applies especially to:
- `ITSR 330853 Refer A Friend URS Revised 1.1.pdf`
- `UT Enhancements - Phase 2 2026.pdf`

---

## Final Feature-Oriented Verdict

The source set is much easier to reason about when grouped by **feature delta type** rather than by file alone.

- The strongest docs are those with a clear baseline and a well-bounded target delta.
- The weakest docs are those that combine historical/current-state behavior with new requests in one undifferentiated contract.
- The coupon-family artifacts are the most integration-sensitive because they appear to formalize or refactor an existing capability without first pinning the current canonical lifecycle.

### Highest-value next corrections

1. **Coupon family:** define current-state lifecycle vs target-state lifecycle.
2. **Refer A Friend:** split baseline capability from requested CR deltas.
3. **UT Enhancements:** convert backlog-bundle wording into itemized target features.
4. **Accredited Investor form:** state current web baseline and target native-entry experience explicitly.
5. **reCAPTCHA replacement:** add migration/fallback/current-vs-target security model.
