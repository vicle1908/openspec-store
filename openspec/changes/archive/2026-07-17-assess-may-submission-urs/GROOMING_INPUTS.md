# Grooming Session Inputs — May Submission URS

> Source notes from grooming sessions on 5 June 2026.
> Used to update the master assessment and the shared sheet so research reflects what the team actually agreed in the rooms.

## 1. Smart Portfolio Phase 2 — Day 3

### Confirmed decisions
- Phase 2 introduces **Recurring Saving Plan (RSP)** capability to Smart Portfolio.
- Phase 2 is **additive** to the existing lump-sum flow. No breaking change to lump sum.
- Includes minor enhancements (graphs) plus backend PMIP/CQB form updates.

### Three user journeys
- **J1 — New user:** portfolio value = 0, no prior deposit.
- **J2 — Existing user starting RSP.**
- **J3 — Existing user amending RSP** (increase/decrease amount, suspend).

### Core RSP rules confirmed
- Frequency: **monthly only** (no dropdown).
- Execution date: **7th of each month** (ops constraint).
- Two start options:
  - **Today:** triggers immediate lump-sum deposit, then sets up recurring from next month.
  - **Next month:** straight to recurring, no immediate lump sum.
- "No deposit" = portfolio value = 0 (never deposited before).
- If portfolio value = 0 → only "Today" option is available.
- Edge case: account closes if balance becomes 0 after withdrawal. (Resolved.)

### Payment & setup flow
- Payment methods:
  - PayNow (lump sum)
  - eGIRO (recurring)
  - Internal transfer
- After payment setup, user must be redirected back to the **portfolio screen**.
- Confirmation page should ideally include:
  - start timing clarity,
  - deposit amount,
  - frequency,
  - payment method.

### RSP management (J3)
- User actions allowed: amend amount, change payment method, **suspend** (not terminate).
- System behavior on suspend:
  - future deductions stopped,
  - plan remains restartable,
  - UI shows "RSP suspended" status.

### Portfolio UI display logic
- Show bank account + giro status if eGIRO.
- Show source account if transfer.
- Show suspension message if applicable.
- Show nothing if no RSP exists.

### Gaps confirmed during grooming
- UX/flow:
  - Missing screen between PayNow → return → RSP.
  - Redirect behavior after payment needs definition.
  - Flow continuity unclear for developers.
- Content/messaging:
  - Confusing disclaimer about deposit vs recurring start.
  - Confirmation page lacks clarity on start date.
- Technical/integration:
  - eGIRO (webview) → status callback handling unclear.
  - Deep link / callback mechanism needed to return to the app.
- Documentation:
  - URS missing failure/cancel flows, redirect logic, payment return handling.
  - Some logic only in discussion, not yet documented.

### Action owners
- **Steven (BA, primary owner):** update URS — add missing screens/flow transitions, redirect behavior, failure/cancel flows, clarify "no deposit", add transaction history, eGIRO return flow, fix wording, add Figma refs. Deliver by next week.
- **Product/UX (Steven + Debbie):** rework disclaimer wording, confirmation page clarity, add suspension state UI, start-date visibility.
- **Tech/Engineering:** confirm eGIRO callback + status handling (central UI team), define deep link / redirect, validate native vs central UI for payment flows.
- **Product/Business (Ronnie, Nizam):** decide whether to merge Phase 1 + Phase 2 scope or estimate separately; send updated URS to Kok Kien's team for estimation and scheduling.

### Implication for assessment
- Readiness for `ITSR 369004 SMART Portfolio Phase 2.pdf` improves **only after** Steven's URS update lands.
- Until then, it remains **Conditionally ready** but with newly explicit P0 contract gaps:
  - missing redirect/cancel/failure flow,
  - missing eGIRO return handling,
  - ambiguous start-date messaging,
  - placeholder disclaimer wording.
- Engineering detail:
  - **Integration Dependency** increases (PayNow, eGIRO, internal transfer, central UI).
  - **Operational Dependency** increases (RSP execution on 7th is ops-driven).
  - **Observability Need** increases (status transitions, payment return, suspended state).
  - **Regression Risk** is moderate (lump-sum flow must remain unchanged).

### Updated engineering profile
- **Testability:** 4 (slight downgrade from 5; redirect/cancel flows not yet testable).
- **Integration Dependency:** 4 (PayNow, eGIRO webview, internal transfer, central UI callback).
- **Operational Dependency:** 3 (RSP execution on 7th, suspension state follow-up).
- **Regression Risk:** 4 (lump-sum must remain unchanged; new payment methods create new branches).
- **Observability Need:** 4 (RSP state transitions, payment return events, suspension events).

---

## 2. Trade Ticket (Light Mode) — Day 2

### Confirmed decisions
- Light Mode is a UX simplification for new traders.
- Reduce cognitive load: remove unnecessary icons/fields, show only essential inputs (price, quantity, direction).
- Default behavior still reflects existing system rules (no backend logic changes).
- Key principle: keep ~90% of common cases (limit order, cash, day validity) in Light Mode.
- Less-used options moved to "More Settings" (collapsed).
- Consistency with Pro mode logic preserved; fields are hidden, not removed from validation.

### What is shown in Light Mode
- Counter name/code, price, bid/ask.
- Buy/Sell/Short actions.
- Price & quantity.
- Available cash.
- Password (if needed).

### What is hidden / simplified
- Advanced fields (order type, settlement, currency, validity).
- Volume data and extra indicators.
- Search button (UX choice to reduce distraction).

### Supported order types
- Light Mode: **Limit order (default)** and **Market order** for eligible markets (US/HK).
- Pro Mode only: advanced orders (stop limit, limit-if-touched, etc.).
- Rationale: avoid complexity (e.g., trigger price) in Light Mode.

### Market behavior rules
- Follow existing rules per market (no changes).
  - SG: limit-focused.
  - US/HK: market order available.
- Currency:
  - Default to traded market currency.
  - Exception: non-multi-currency accounts → fallback to SGD.

### Mode switching (Light ↔ Pro)
- Default: **Pro mode** for all users.
- User can switch manually to Light Mode.
- Trigger: UI toggle or order-type selection.
- **Current leaning:** reset fields on mode switch for safety (avoid incorrect trade submission).
- Possible exception: retain price & quantity for basic orders (still under discussion).

### Settings persistence
- Original idea: per-account preference.
- Actual constraint: **device-level storage** (applies to all accounts on the same device).
- New device → resets to Pro mode.
- Risk flagged: poor experience for users with multiple accounts on the same device.

### Performance considerations
- Dev suggestion: avoid reloading the whole screen; reload only changing values.
- Concern: stale/incorrect data risk on a dynamic, sensitive surface.
- Decision: dev team to analyze feasibility before finalizing.

### Analytics & tracking
- Track Light vs Pro usage via event on **Review Order** click.
- Tools: GA4 (primary); Firebase or other logs under discussion.
- Concern: multiple logging systems increase QA/testing effort.

### Action items
- **Product/UX:** review field reset vs retention; validate if price/quantity can be safely retained; re-evaluate order-type handling; ensure no risk of incorrect trade submission; validate removal of search button; monitor post-launch feedback.
- **Engineering:** reassess mode persistence approach; investigate alternatives to device-level storage; study performance optimization (partial reload vs full refresh); clarify multi-account scenarios.
- **Analytics/QA:** confirm logging architecture; finalize GA4-only vs GA4 + Firebase + others; define event tracking clearly.

### Open follow-ups
- Clarify multi-currency account scenarios.
- Validate behavior for non-opted-in users.
- Provide URS / SharePoint access to QA; resolve access limitations.

### Implication for assessment
- `URS_P3_Stock Trade ticket - Lite mode.pdf` readiness **downgrades slightly** because:
  - field reset vs retention is not yet decided,
  - multi-account / device-level persistence has open UX concerns,
  - performance strategy is undecided,
  - analytics logging architecture is undecided.
- It is no longer "Ready" outright; it should now be tracked as **Conditionally ready (4/5)** until the four open decisions close.
- Engineering detail:
  - **Testability** remains high for defined order/market rules.
  - **Regression Risk** remains high (incorrect submission risk is explicitly flagged).
  - **Observability Need** increases (event tracking on Review Order; mode-usage analytics).

### Updated engineering profile
- **Testability:** 4 (downgraded from 5; mode-switch behavior not yet testable).
- **Integration Dependency:** 2 (mostly UI-state layer; no new backend systems).
- **Operational Dependency:** 1 (no manual ops).
- **Regression Risk:** 5 (upgraded from 4; incorrect submission risk explicitly flagged).
- **Observability Need:** 4 (upgraded from 3; Light vs Pro event tracking on Review Order).

---

## 3. Amalgamated Trade — Grooming

### Confirmed decisions
- Current implementation:
  - Coupons sent real-time to GBO.
  - Each coupon sent individually (no grouping).
  - Even if multiple coupons exist, all are sent.
- New requirement (to-be):
  - **Batch processing** (end-of-day scheduler).
  - Coupons sent to GBO per client, one-by-one in the batch job.

### Amalgamation logic (new concept)
- Distinction between:
  - Amalgamated markets.
  - Non-amalgamated markets.
- Rules:
  - **Non-amalgamated markets:** apply coupon per trade (no restriction).
  - **Amalgamated markets:** apply only **once per counter**.
- Additional coupons:
  - Not applied if same counter.
  - Next valid coupon used for different counters.

### Coupon prioritization
- **FIFO** (First-In-First-Out) for application order.
- Must also consider:
  - Activation status.
  - Expiry.

### Open decisions / uncertainties
- Which markets are amalgamated vs non-amalgamated.
- How grouping rules should be defined.
- Whether logic should be:
  - config-driven,
  - market-based,
  - or coupon-based.
- Should coupons be grouped by:
  - market,
  - counter,
  - campaign?

### Action points
- Implement batch processing (real-time → end-of-day).
- Define amalgamation rules (which markets).
- Introduce application logic:
  - amalgamated: once per counter,
  - non-amalgamated: per-trade.
- Define grouping behavior (by market/counter/campaign).
- Confirm requirements with Marketing:
  - grouping logic,
  - amalgamated market definitions,
  - coupon usage rules.
- Design configuration approach:
  - prefer market-level configuration,
  - or backend logic/flags.

### Implication for assessment
- `Gami - Amalgamated Trade.pdf` readiness **remains at 3/5** because the market-level amalgamation definitions and grouping criteria are still unconfirmed.
- The new critical contract gap is the **canonical amalgamated-market list** plus the **FIFO-with-activation-and-expiry** ordering rule.
- Batch processing timing is now an explicit P0 contract: end-of-day scheduler, per-client send.
- Engineering detail:
  - **Integration Dependency** increases (scheduler + GBO + coupon master).
  - **Operational Dependency** increases (Marketing validation of market list and grouping).
  - **Observability Need** increases (batch outcomes, per-coupon counter logic, FIFO trace).

### Updated engineering profile
- **Testability:** 2 (downgraded from 3; amalgamated-market list and grouping still open).
- **Integration Dependency:** 5 (upgraded from 4; end-of-day scheduler added).
- **Operational Dependency:** 4 (upgraded from 3; Marketing-driven market/grouping rules).
- **Regression Risk:** 4 (real-time → batch migration changes downstream timing).
- **Observability Need:** 5 (upgraded from 4; batch outcomes, FIFO trace, per-counter application).

---

## 4. Cash Coupon — Grooming

### Confirmed end-to-end flow
- User receives and activates a stock coupon.
- When a trade executes, order alert triggers the gamification engine.
- System validates:
  - coupon is activated,
  - coupon is applicable (e.g., correct market like US).
- If valid:
  - coupon applied to the order.
  - status moves through: `Pending → Processing → Redeemed`.
  - GBO API is called to credit funds to client account.
- GBO handles actual crediting.
- After success, status updated to "Redeemed".

### Identified gaps / issues
- Current flow updates "Redeemed" before confirmation from GBO → inconsistency.
- Users sometimes see "Redeemed" but no funds credited.
- If GBO fails/rejects: coupon may remain "Processing" indefinitely.
- No proper fallback or status correction mechanism.
- External system (Mambu / member view) is updated too early:
  - should only update after successful GBO credit confirmation.

### Action points
- Fix coupon status flow:
  - `Pending → Processing → Redeemed` **only after GBO success**.
- Correct notification timing:
  - update Mambu/member view only after successful GBO credit.
- Handle failure scenarios:
  - GBO rejection,
  - API failures,
  - avoid indefinite "Processing".
- Introduce status reconciliation:
  - retry, timeout, fallback (e.g., mark as failed/rejected).
- Update system flow / documentation:
  - reflect correct sequence (current flow outdated).

### Implication for assessment
- `Gami - Cash Coupon Global Admin.pdf` readiness **does not improve yet**; the lifecycle now has a clearly documented happy-path correction, but failure and reconciliation behavior are still being defined.
- The canonical lifecycle must encode:
  - `Pending → Processing → GBO-call → {Settled, Error, Retry}`,
  - explicit Mambu/member-view update only on Settled,
  - reconciliation/retry policy.
- Engineering detail:
  - **Testability** stays low until failure path is fully specified.
  - **Observability Need** stays at the top tier (GBO outcomes, retry events, status drift).
  - **Operational Dependency** stays at the top tier (manual reconciliation of stuck Processing cases).

### Updated engineering profile
- **Testability:** 2 (unchanged; failure/reconciliation still open).
- **Integration Dependency:** 5 (unchanged; P3, Global Admin, GBO, Mambu).
- **Operational Dependency:** 5 (unchanged; manual reconciliation of stuck Processing).
- **Regression Risk:** 5 (unchanged; Mambu update timing bug already seen in production).
- **Observability Need:** 5 (unchanged; GBO outcomes, retry events, status drift).

---

## 5. Cross-Cutting Implications

### New P0 contract gaps across the source set
1. **SMART Portfolio Phase 2** — RSP redirect, failure/cancel, eGIRO return.
2. **Amalgamated Trade** — canonical amalgamated-market list + batch schedule contract.
3. **Cash Coupon** — canonical lifecycle with explicit GBO outcome and reconciliation path.
4. **Light Mode Trade Ticket** — open field-retention, persistence, performance, and analytics decisions.

### Confirmed next moves
- Steven to deliver updated URS for SMART Portfolio Phase 2 by next week.
- Marketing to confirm amalgamated market list and grouping behavior.
- GBO owner to confirm reconciliation/retry policy for Cash Coupon.
- Trade Ticket team to close the four open decisions before locking the spec.
- All updated URS go to Kok Kien's team for estimation and scheduling.
