# May Submission URS Assessment Draft

## File-by-File Findings

### Gami - Amalgamated Trade.pdf

- Status: reviewed
- Apparent feature area: coupon/rebate flow for amalgamated trades
- Key business rules:
  - One coupon is awarded for one settled trade.
  - Same-day trades can be grouped into one rebate treatment.
  - Rebate processing includes downstream timing/cutoff handling.
- Workflow notes:
  - Trade/coupon flow spans P3, coupon/reward handling, and downstream rebate processing.
- Ambiguities / gaps:
  - Exact exception behavior and ownership boundaries need clearer specification.
  - Some operational details appear process-oriented rather than system-contract precise.
- Source quality notes:
  - Generally readable extraction; requires cross-check against the coupon global-admin and draw.io flow.

### Gami - Cash Coupon Global Admin.pdf

- Status: reviewed
- Apparent feature area: marketing approval/rejection control for cash coupons before GBO crediting.
- Key business rules:
  - P3 sends cash-coupon data to Global Admin.
  - Marketing can approve or reject each coupon.
  - Approved items go to GBO for crediting.
  - Rejected items are sent back to P3 and handled manually by marketing.
  - If GBO rejects or errors, marketing must be updated via email.
  - While pending approval, coupon status in P3 remains `pending`.
- Workflow notes:
  - Introduces an explicit risk-management approval layer between P3 and GBO.
  - Couples user-facing status transitions with operational team actions.
- Ambiguities / gaps:
  - Document uses placeholders (`ITSR ???`, `n/a`, template remnants).
  - Rejected flow says coupon remains pending in P3, which is semantically confusing versus explicit rejection in Global Admin.
  - Error-notification details are high level; no exact recipient/format/SLA.
- Source quality notes:
  - Strong acceptance criteria section, but the document still has template residue and incomplete metadata.

### ITSR 330853 Refer A Friend URS Revised 1.1.pdf

- Status: reviewed
- Apparent feature area: referral campaign lifecycle, referral UX, eligibility, and reward attribution.
- Key business rules:
  - Holder-account users refer friends to P3/open-account journeys.
  - Rewards depend on downstream qualification activities such as account opening/funding/trading.
  - Existing change requests add eligibility blocking, invite history updates, progress display, coupon status display, reward notifications, and tooltips.
- Workflow notes:
  - Covers end-to-end campaign creation, referrer participation, referee participation, reward monitoring, and campaign expiry.
  - Mixes already-done stories with change-request stories in the same URS.
- Ambiguities / gaps:
  - Purpose section incorrectly references `Paper Trading capability`, indicating copied template text.
  - Several sections are structurally broad and may require decomposition to implementation-ready slices.
  - Need careful separation between already-delivered scope and new CR scope.
- Source quality notes:
  - Richest flow coverage in the source set, but also broad and partly inconsistent in document hygiene.

### ITSR 369004 SMART Portfolio Phase 2.pdf

- Status: reviewed
- Apparent feature area: PMIP form modernization / Smart Portfolio RSP support.
- Key business rules:
  - PMIP form moves into CQB4.
  - Account number must be unique in CQB PMIP form.
  - Account holder name auto-populates after valid account entry.
  - Fund source is mandatory with `Cash` as default and enumerated source options.
  - Collection amount accepts decimals up to 2 places.
- Workflow notes:
  - Strong emphasis on form fields, validation, and backend form reuse.
  - Includes P3 e-Giro journey in scope.
- Ambiguities / gaps:
  - Metadata and glossary are incomplete/template-like.
  - Scope references PMIP and Smart Portfolio but framing around phase naming/references is somewhat loose.
- Source quality notes:
  - Better field-level specificity than many docs, but still contains substantial template leftovers.

### ITSR [369574] RECAPTCHA TO REPLACE GEETESTv1.0.pdf

- Status: reviewed
- Apparent feature area: fraud/bot mitigation for auth + OTP workflows.
- Key business rules:
  - Replace GeeTest with Google invisible reCAPTCHA and SMS Defender.
  - Phase 1 applies to Registered Users; Phase 2 extends to Account Holders and admin portal support.
  - CAPTCHA enforcement and related controls must be configurable without redeployment.
  - Existing front-end and API-side OTP abuse controls remain relevant context.
- Workflow notes:
  - Security controls are phased and tied to contract/renewal timing.
  - Combines risk-control policy with user-story delivery requirements.
- Ambiguities / gaps:
  - Committee/glossary sections are incomplete.
  - Implementation boundaries between reCAPTCHA, SMS Defender, and admin-portal intervention need careful interface definition.
- Source quality notes:
  - Clear rationale and phased rollout, with better risk framing than many docs.

### Phillip GPT on POEMS v1.0.pdf

- Status: reviewed
- Apparent feature area: client-facing AI assistant embedded in trading platforms.
- Key business rules:
  - P3/P2Web show Ask AI entry points across many screens.
  - Iframe loads with contextual parameters such as PhillipID, AccountNo, Nickname, Query, Screen Context, PC Code, and UI Theme.
  - Disclaimer display is tracked per user/platform.
  - Feature flags and `GPT_Source` determine availability and backend source.
  - Chat loading logic differs based on query/context presence.
  - Responses must follow a structured compliance-oriented format.
  - Multi-intent handling must block advisory risk while still serving safe informational/analytical content.
- Workflow notes:
  - Strong product vision plus detailed UX, parameter-passing, compliance, and chat behavior requirements.
- Ambiguities / gaps:
  - Mixture of product vision, UX wire behavior, compliance logic, and AI policy in one document may complicate implementation ownership.
  - Several formatting/extraction artifacts make some sections dense.
- Source quality notes:
  - One of the most detailed and implementation-relevant documents in the set.

### URS_P3_Stock Trade ticket - Lite mode.pdf

- Status: reviewed
- Apparent feature area: simplified trade ticket UX for retail/new users.
- Key business rules:
  - Lite Mode supports only basic order types.
  - SG and most markets restrict Lite Mode to Limit Orders; US/HK allow Limit and Market Orders.
  - Secondary fields move under collapsible `More Settings`.
  - Preferred mode and expand/collapse state are persisted on device.
  - Telemetry is required to compare Lite vs Pro usage.
- Workflow notes:
  - Explicitly framed as UI/UX rearrangement, not downstream validation changes.
  - Market-specific behavior varies but follows a common simplification pattern.
- Ambiguities / gaps:
  - Need precise edge-case handling when users pivot from Lite to Pro to reach advanced orders.
- Source quality notes:
  - Clear purpose/scope and reasonably actionable rules.

### UT Enhancements - Phase 2 2026.pdf

- Status: reviewed
- Apparent feature area: rolling minor UT improvements.
- Key business rules:
  - Scope includes fixing CKA/CAR reporting issue, adding Fund Screener, automating UT news updates, and hiding minutes/hours for UT chart filter.
  - Email-reporting logic spans AOP, CQB, and CIS responsibilities.
- Workflow notes:
  - This is a bundle URS for multiple small enhancements rather than one tightly-scoped feature.
- Ambiguities / gaps:
  - Scope is intentionally open-ended: “items are discovered to be built”, which weakens contract precision.
  - Multiple enhancements are grouped with uneven depth.
- Source quality notes:
  - Useful for backlog context, weaker as a strict requirement contract.

### WM - Accredited Investor Form.pdf

- Status: reviewed
- Apparent feature area: P3 AI-form onboarding for accredited investor status.
- Key business rules:
  - AI criteria include income/assets thresholds.
  - AI status validity is 2 years.
  - Users can renew before expiry; new submission resets validity.
  - Reminder is sent via email/MoEngage.
  - Scope is limited to individual and joint accounts, excluding corporate accounts.
  - P3 should expose the form from the Me tab instead of forcing web-only completion.
- Workflow notes:
  - Cross-team flow includes P3, CQB, Web/iframe, and Risk & Quality.
- Ambiguities / gaps:
  - Metadata and glossary remain incomplete.
  - Boundary between native P3 experience and iframe/web ownership should be clarified.
- Source quality notes:
  - Strong business framing and eligibility criteria; moderate template residue.

### CashCOupon.drawio

- Status: reviewed
- Apparent feature area: operational coupon/redemption/rebate processing across systems.
- Key business rules observed from diagram labels:
  - Mobile reward inventory triggers coupon redemption by ID.
  - GamiAPI calls Mambo coupon-details endpoint and GBO rebate endpoint.
  - Coupon status is updated to `PROCESSING` in P3DB.
  - Done orders flow into a queue/listener in TaskAPI.
  - Listener retrieves activated coupons by user ID and coupon details by ID.
  - If order matches coupon criteria, coupon status moves to processing and rebate request is sent with unique ID + rebate amount.
  - Failed rebate records are scanned on schedule and transaction status is checked later.
- Workflow notes:
  - Diagram reinforces a queue-driven, asynchronous rebate architecture with retry/reconciliation behavior.
- Ambiguities / gaps:
  - Need full page review to capture later steps and all failure-state transitions.
- Source quality notes:
  - Valuable system interaction map; must be synthesized with the cash-coupon URS text.

## Cross-File Synthesis (Draft)

### Reinforcing themes

- Multiple documents use staged approval, status transitions, and operational intervention rather than purely synchronous user flows.
- P3 is a repeated orchestration surface, while downstream systems such as CQB, GBO, CIS, Mambo, and admin portals handle validation, fulfillment, or oversight.
- Several features rely on feature flags, config-driven behavior, or status persistence rather than hardcoded rollout paths.

### Overlaps

- `Gami - Amalgamated Trade.pdf`, `Gami - Cash Coupon Global Admin.pdf`, and `CashCOupon.drawio` clearly belong to the same reward/coupon/rebate family and should be assessed together, not independently.
- `Phillip GPT on POEMS v1.0.pdf` and `WM - Accredited Investor Form.pdf` both depend on iframe/native-boundary decisions in P3/P2Web-like surfaces.
- `ITSR [369574] RECAPTCHA TO REPLACE GEETESTv1.0.pdf` and `Phillip GPT on POEMS v1.0.pdf` both include compliance/safety controls beyond plain UI requirements.

### Contradictions or tensions

- Cash coupon rejection semantics are inconsistent: Global Admin exposes explicit rejection, while P3-facing status wording suggests rejected coupons may remain `pending`.
- Several docs present themselves as formal URS contracts but still contain template placeholders, missing project refs, incomplete glossaries, or copied purpose text from unrelated features.
- UT Enhancements is intentionally discovery-driven, which conflicts with the usual expectation that a URS is a bounded requirement contract.

### Common source-quality issues

- Template residue (`ITSR ???`, `n/a`, empty committee/glossary sections, placeholder titles).
- Mixed “done” work and change-request work inside the same specification.
- Uneven granularity: some docs define field-level validation, others only define high-level intent.
- Ownership and integration boundaries are often implied rather than explicitly contracted.

### Assessment implications

- Spreadsheet output should likely use a hybrid model: one summary row per file plus a detailed findings tab for rule/gap/conflict entries.
- The coupon-related sources need a consolidated subsection because their real meaning emerges only when read together.
- The final assessment should separate confirmed business rules from operational assumptions and from document-quality defects.
