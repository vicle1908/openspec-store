# May Submission URS — Human-Readable Assessment

> **Canonical assessment for the May Submission URS folder.**
> All 12 artifacts reviewed (10 PDFs, 1 draw.io diagram, 1 draw.io diagram).
> Updated with grooming-grounded findings (5 June 2026 sessions) and 2 new documents (19 June 2026).
>
> **How to read this document:** Each section below follows the same structure:
> - **Plain-English Summary** — what this feature is, in one paragraph
> - **What Must Already Exist** — preconditions the system must have before this can work
> - **What the URS Proposes to Add or Change** — the actual new or modified behavior
> - **What Will Break If We Build From This URS Today** — specific gaps, named plainly
> - **What Needs to Happen First** — who needs to do what, in plain language
> - **Engineering Risk Profile** — plain-English translation of the technical scoring

---

## Executive Summary

The May Submission folder contains 12 artifacts covering a wide range of business initiatives — from payment infrastructure and shareholder voting to fraud protection and AI assistance. The folder's average readiness is **3.5 out of 5** — which means most documents are usable with clarification, but several cannot be built from as-is.

**One document is fully ready for implementation:** Phillip GPT on POEMS. Six documents are conditionally ready — they describe the right intent but need specific gaps closed before a developer should touch them. Four documents need significant rewriting before any build starts.

**The most important pattern across the folder:** the strongest documents separate "what exists today" from "what we are adding." The weakest documents mix the two, which makes it impossible for a developer to know what to build versus what to leave alone. The second most important pattern: documents that describe happy-path behavior but skip failure and reconciliation scenarios will produce systems that appear to work but silently fail in production.

---

## Portfolio Scorecard

| # | Document | Readiness | Human Verdict |
|---|---|---|---|
| 1 | Gami - Amalgamated Trade.pdf | 3/5 | Cannot build — waiting on Marketing |
| 2 | Gami - Cash Coupon Global Admin.pdf | 3/5 | Cannot build — lifecycle broken |
| 3 | ITSR 330853 Refer A Friend URS Revised 1.1.pdf | 3/5 | Cannot build — old and new mixed |
| 4 | ITSR 369004 SMART Portfolio Phase 2.pdf | 4/5 | Can build after Steven's update |
| 5 | ITSR [369574] RECAPTCHA TO REPLACE GEETESTv1.0.pdf | 4/5 | Can build — needs Phase 2 scope defined |
| 6 | Phillip GPT on POEMS v1.0.pdf | **5/5** | **Ready to build now** |
| 7 | URS_P3_Stock Trade ticket - Lite mode.pdf | 4/5 | Can build after 4 decisions close |
| 8 | UT Enhancements - Phase 2 2026.pdf | 2/5 | Not ready — needs decomposition |
| 9 | WM - Accredited Investor Form.pdf | 4/5 | Can build — needs ownership boundary defined |
| 10 | CashCOupon.drawio | 4/5 | Good as a diagram — needs a written companion |
| 11 | URS - DDA Linking and DDA Deposit.pdf | 4/5 | Can build Phase 1 after Finance signs off |
| 12 | URS -POEMS Shareholder Meeting P3 URS.pdf | 4/5 | Can build — needs email replaced with real tracking |

---

## Plain-English Field Guide to the Scoring

| Score | What it means for a developer or BA |
|---|---|
| **5 — Ready** | You can take this URS and start building. It tells you what to do, when, and what success looks like. |
| **4 — Conditionally Ready** | Mostly fine, but there are specific gaps that will cause rework if you start building today. Come back to these after the gap is closed. |
| **3 — Needs Authoring Work** | The intent is there, but the URS does not yet describe the behavior with enough precision to build from. Expect significant clarification sessions before a developer can start. |
| **2 — Needs Scoping** | The document mixes too many things together or describes vague intentions rather than specific behavior. Not usable as a build contract in current form. |
| **1 — Unusable** | Fundamental contradictions, missing core content, or missing context that makes the document impossible to act on. |

---

## Document-by-Document Assessments

---

### 1. Gami - Amalgamated Trade.pdf

#### Plain-English Summary
This URS covers how stock coupons get applied to trades when a client holds multiple securities. The key idea is that for some markets, coupons should apply once per counter (per stock) per day rather than once per individual trade. This is called "amalgamation." The URS proposes moving from a system that sends coupons in real time to one that collects all the day's trades and processes them together at end of day.

**The gap:** The URS correctly describes the new batch approach and FIFO ordering rules, but it does not say which markets are amalgamated versus which are not. Without that list, a developer cannot write a single line of code.

#### What Must Already Exist
- A working coupon/gami engine that tracks activated coupons, expiry, and applicable markets
- GBO API that accepts coupon credit requests
- Some form of batch scheduling infrastructure

#### What the URS Proposes to Add or Change
- End-of-day batch job instead of real-time coupon processing
- One coupon applied per counter per day for amalgamated markets
- FIFO ordering with activation status and expiry as tiebreakers
- Group same-day trades before applying coupon

#### What Will Break If We Build From This URS Today
> **"Which markets are amalgamated?"** — This is the central gap. The document never lists which markets follow the amalgamated rule versus which follow per-trade rules. Without this list, the batch job cannot be coded. This is a Marketing decision, not an engineering decision.

> **"What if the batch job runs and the counter has already received a coupon today?"** — The FIFO ordering logic is defined in principle but not in concrete scenario terms. What happens at exact cutoff? What if the same counter gets a new coupon between batch runs?

> **"How is the amalgamated market list maintained?"** — Is it a configuration file, a database table, or hard-coded? This determines how Marketing can change it in the future without a developer.

> **"What happens to coupons that expire during the batch?"** — FIFO with expiry as secondary criterion is stated but not walked through in an example.

#### What Needs to Happen First
1. **Marketing must provide the canonical list** of which markets are amalgamated and which are not. This is a business decision, not a technical one.
2. **Marketing must confirm grouping behavior** — does grouping happen by market, by counter, by campaign, or by a combination?
3. **Engineering and BA must agree** on whether the market list is a configuration (easy to change) or code (requires a release).
4. **Cutoff timing and boundary conditions** need to be written out with concrete examples.

#### Engineering Risk in Plain English
This is one of the most integration-heavy changes in the folder. It touches the batch scheduler, the coupon eligibility engine, GBO, and the counter-matching logic simultaneously. A developer who starts building from this URS today will produce a system that runs but applies coupons to the wrong trades in edge cases. The batch logic is sound in principle; it is not yet sound in practice.

| Dimension | Score | Plain English |
|---|---|---|
| Testability | 2/5 | Cannot write meaningful tests without the market list |
| Integration Dependency | 5/5 | Batch scheduler + GBO + coupon engine + counter logic |
| Operational Dependency | 4/5 | Marketing owns the market list; ops must know what the batch did |
| Regression Risk | 4/5 | Changes to timing affect when clients receive money |
| Observability Need | 5/5 | Every batch run needs an audit trail: what was applied, to which counter, in what order |

---

### 2. Gami - Cash Coupon Global Admin.pdf

#### Plain-English Summary
This URS covers the back-office workflow for marketing's cash coupons. When a client receives a coupon and then executes a trade, the system checks the coupon, applies a reward, and credits the client's account via the GBO system. The URS proposes to formalize this into a system contract with explicit status states and a clear admin interface for approving and rejecting coupons before they go to GBO.

**The gap (identified during grooming):** The URS currently says a coupon reaches "Redeemed" status before GBO confirms the credit has landed. This means a client sees "you received your reward" in the app while their account has not actually been credited yet. This has been observed in production.

#### What Must Already Exist
- Gami engine that fires order alerts when trades execute
- GBO API that credits cash rewards to client accounts
- P3 notification system for push alerts
- Mambu (or equivalent member engagement system) that shows coupon status

#### What the URS Proposes to Add or Change
- Explicit admin approval/rejection workflow before coupons go to GBO
- Formal state machine: Pending → Processing → Settled (or Error, or Retry)
- Mambu/member-view updates only after successful GBO credit
- Error notification from GBO when a credit fails

#### What Will Break If We Build From This URS Today
> **"What does the client see while GBO is processing?"** — The current URS shows the client reaching "Redeemed" before GBO has confirmed anything. Building from this means a production bug: clients believe they have received money they have not yet received.

> **"What happens if GBO rejects the credit?"** — The URS does not describe this path. The coupon could sit in "Processing" state forever. No retry, no timeout, no admin alert.

> **"Who handles stuck coupons?"** — There is no ops runbook described. In production, someone must have been manually reconciling these. That manual process is not written down.

> **"How does Mambu know the credit succeeded?"** — The URS says Mambu updates at some point, but not that it waits for GBO confirmation. This timing bug is already appearing in production.

#### What Needs to Happen First
1. **Define the correct lifecycle in plain terms:** Pending → Processing → GBO call → Settled (GBO confirmed) OR Error (GBO rejected) OR Retry (timeout/no response). The "Redeemed" label should only appear after GBO success.
2. **Define the GBO error contract:** What does GBO return when a credit fails? What does the system do with that response?
3. **Define the reconciliation policy:** How often does a job check for "Processing" coupons older than X minutes? What triggers a retry? What triggers an admin alert?
4. **Fix the Mambu timing rule:** Mambu/member view must only update after GBO returns success. Write this as a rule, not a description.

#### Engineering Risk in Plain English
This is the highest-risk document in the folder for an operational reason: it describes a system where clients are told they have received money before they have. This is not a code bug — it is a user trust bug. It will generate support tickets and erode confidence in the gamification feature. The fix is not complex, but the document must be corrected before development starts.

| Dimension | Score | Plain English |
|---|---|---|
| Testability | 2/5 | Cannot test failure paths that are not described |
| Integration Dependency | 5/5 | P3 + Global Admin + GBO + Mambu — four systems in one flow |
| Operational Dependency | 5/5 | Ops currently doing manual reconciliation; that work is not documented |
| Regression Risk | 5/5 | Mambu showing incorrect status is already happening in production |
| Observability Need | 5/5 | Every state transition needs logging; a stuck coupon must be visible immediately |

---

### 3. ITSR 330853 Refer A Friend URS Revised 1.1.pdf

#### Plain-English Summary
This URS covers the Refer A Friend feature — existing clients can invite friends, track referral progress, and receive stock coupons as rewards. The document covers eligibility rules, the invite UX, reward attribution, and campaign management. The document is a revision, which means some parts describe what already exists and some describe what needs to change.

**The gap:** The document does not clearly separate "what was built in version 1.0" from "what is new in version 1.1." A developer reading this document cannot tell which sections describe current behavior to preserve versus new behavior to add.

#### What Must Already Exist
- POEMS account system with holder accounts
- Coupon/gami engine that can award and track stock coupons
- Invite tracking and progress display
- Campaign management interface for the BA/marketing team

#### What the URS Proposes to Add or Change
- Eligibility blocking improvements (who can refer whom)
- Invite history improvements
- Reward progress display
- Coupon status visibility
- Notification improvements
- New tooltip and UX refinements

#### What Will Break If We Build From This URS Today
> **"Which of these changes have already been built?"** — Several sections appear to describe new enhancements, but the document's revision history suggests some items may already exist. Building everything described would duplicate effort or build the wrong thing.

> **"Who owns campaign setup?"** — The document mentions campaigns but does not say who creates them, who approves reward amounts, or who decides when a campaign goes live. This boundary ambiguity will cause scope arguments.

> **"What happens to a referral that fails eligibility check?"** — The eligibility blocking logic is referenced but not described with a clear state model. A developer cannot write an eligibility checker without this.

> **"Wrong template text in the document itself"** — The document uses a wrong purpose statement and some template placeholders. This suggests the document may have been copied from a different feature and not fully updated.

#### What Needs to Happen First
1. **Add a clear "Baseline vs. Change" table** at the top: Column 1 = item description, Column 2 = "Already built" or "New in 1.1." This is the single most important fix.
2. **Rewrite the purpose statement** to correctly describe Refer A Friend.
3. **Define campaign ownership:** Who creates a campaign? Who sets reward amounts? Who activates it?
4. **Write the eligibility state model:** Who is eligible to refer? Who is eligible to be referred? What blocks an invite?
5. **Add acceptance criteria per enhancement item.**

#### Engineering Risk in Plain English
This is a document hygiene problem, not a domain problem. The feature is well understood, but the document has been revised so many times that it no longer reflects a clean state. A developer will waste time distinguishing baseline from change, and a BA will spend sessions correcting scope disagreements. The fix is structural, not conceptual.

| Dimension | Score | Plain English |
|---|---|---|
| Testability | 3/5 | Happy-path is describable; boundary conditions are not |
| Integration Dependency | 3/5 | Coupon engine + account system; not the most complex integration |
| Operational Dependency | 2/5 | Mostly automated; campaign ownership is the main ops question |
| Regression Risk | 4/5 | Building "new" items that are already built risks breaking existing behavior |
| Observability Need | 3/5 | Standard analytics on referral funnel; nothing unusual |

---

### 4. ITSR 369004 SMART Portfolio Phase 2.pdf

#### Plain-English Summary
This URS covers Phase 2 of the Smart Portfolio feature. The existing Phase 1 handles lump-sum deposits. Phase 2 adds Recurring Saving Plans (RSP) — monthly automatic deductions from a linked bank account. A client sets up their monthly amount, picks a day, and the system deducts automatically. Phase 2 also includes form modernization (moving from PMIP to CQB4) and portfolio graph enhancements.

**What grooming clarified (5 June 2026):** RSP is monthly only, executed on the 7th of each month. A client can suspend the plan (not terminate it) and restart later. The plan shows a "suspended" status in the UI. Two start options exist: "Start Today" (immediate deposit + setup recurring from next month) or "Start Next Month" (recurring only). A portfolio at zero balance shows only the "Start Today" option.

**What grooming identified as still missing:** The screen that appears after a PayNow payment completes is not described. There is no redirect contract — the URS does not say where the user lands after paying. The eGIRO webview (for linking a bank account) has no defined callback behavior. There is no description of what happens if a payment fails mid-way.

#### What Must Already Exist
- Smart Portfolio with lump-sum PMIP flow
- PayNow payment integration
- GBO posting for account credits
- eGIRO infrastructure for bank account linking

#### What the URS Proposes to Add or Change
- Monthly RSP execution on the 7th (via PayNow, eGIRO, or internal transfer)
- CQB4 form replacing PMIP
- Enhanced portfolio graph display
- RSP management: suspend, amend amount, change payment method

#### What Will Break If We Build From This URS Today
> **"Where does the user go after paying?"** — After a PayNow or eGIRO setup, the URS does not say what screen the user lands on. Building without this definition means the user completes a payment and sees... nothing, or an error, or the wrong screen. This is a UX critical path gap.

> **"What happens if eGIRO fails?"** — The eGIRO webview is referenced but no failure flow exists. If the bank rejects the eGIRO setup, what does the user see? What retry path exists?

> **"What does the RSP suspended state look like?"** — The grooming session clarified the business behavior (suspend, not terminate; plan remains restartable) but the URS has no description of the suspended-state UI or the restart flow.

> **"The confirmation page wording is confusing"** — The current disclaimer wording does not clearly distinguish "Start Today" (immediate deposit) from "Start Next Month" (recurring only). Users will misunderstand when their first deduction occurs.

#### What Needs to Happen First
1. **Steven (BA) must update the URS** with: the post-payment redirect screen, the eGIRO callback contract, the failure/cancel flow, and the RSP suspended-state UI. Target delivery: next week per grooming action.
2. **Product/UX must rework the disclaimer wording** to clearly explain Today vs. Next Month behavior.
3. **Engineering must confirm the deep link mechanism** for returning from the eGIRO webview to the app.

#### Engineering Risk in Plain English
This is one of the better documents in the folder — the RSP rules are clearly agreed and the feature is well-understood. The remaining gaps are concentrated in the payment completion flow, which is a UX-critical path. If the redirect is not defined, the feature will ship with a broken payment experience even if the RSP logic is correct.

| Dimension | Score | Plain English |
|---|---|---|
| Testability | 4/5 | RSP rules are precise; the missing redirect screen cannot yet be tested |
| Integration Dependency | 4/5 | PayNow + eGIRO webview + internal transfer + central UI callback |
| Operational Dependency | 3/5 | RSP executes on the 7th; ops must handle suspended plan follow-up |
| Regression Risk | 4/5 | Lump-sum PMIP flow must not be affected; new payment branches must not break existing ones |
| Observability Need | 4/5 | RSP state transitions, payment return events, suspended-state events all need logging |

---

### 5. ITSR [369574] RECAPTCHA TO REPLACE GEETESTv1.0.pdf

#### Plain-English Summary
This URS covers replacing the current GeeTest anti-bot protection with Google's invisible reCAPTCHA and SMS Defender. GeeTest requires users to complete a puzzle challenge during login and OTP entry. The replacement would be invisible to the user in most cases, improving the login experience while maintaining protection. The rollout is planned in phases: Phase 1 covers client login and OTP; Phase 2 extends to account-holder contexts and admin portal.

**The key challenge:** You are replacing a security control. That means the risk is not "will it work" but "will it fail in a way that lets bots in or keeps real users out." Migration safety — the ability to roll back to GeeTest instantly if reCAPTCHA behaves unexpectedly — is essential and must be designed in from the start.

#### What Must Already Exist
- GeeTest integration on login and OTP entry points
- Existing OTP journey for account holders
- Runtime feature flags for toggling protection mechanisms

#### What the URS Proposes to Add or Change
- Replace GeeTest challenge with invisible reCAPTCHA v3 on login
- Add SMS Defender as an additional layer
- Keep runtime configurability so protection can be adjusted without redeploying
- Phase 1: client login and OTP. Phase 2: account-holder and admin contexts.

#### What Will Break If We Build From This URS Today
> **"What happens if reCAPTCHA gives a false negative — it says a real user is a bot?"** — The URS does not define the fallback path. Does the user see an error? Are they locked out? Is there a manual override?

> **"Phase 2 admin portal boundary is not defined"** — Phase 2 is mentioned but not specified. Admin portal access is a high-value target for abuse. Without a clear Phase 2 scope, engineers will either over-build or under-build.

> **"What is the rollback procedure?"** — If reCAPTCHA produces unexpected behavior in production, how quickly can you switch back to GeeTest? The URS does not describe this. Without a tested rollback, you are committed to the new system once it ships.

> **"How do we monitor whether reCAPTCHA is working correctly?"** — An invisible security control that nobody sees is only as good as its monitoring. The URS does not describe what observability is needed.

#### What Needs to Happen First
1. **Define the migration contract:** How does the system switch between GeeTest and reCAPTCHA? Is it a feature flag? A deployment? Who controls it?
2. **Define the false-negative fallback:** What does a user see when reCAPTCHA fails them? Is there a challenge fallback? An OTP bypass?
3. **Clarify Phase 2 scope** for the admin portal — what exactly is being protected, and with what mechanism?
4. **Define the monitoring requirements:** What metrics indicate reCAPTCHA is working correctly versus failing silently?

#### Engineering Risk in Plain English
This is a security migration, not a feature build. The risk is not "will it meet requirements" but "will it create a gap in protection during rollout." Security migrations have one golden rule: you must be able to roll back instantly. If that rollback path is not designed before you ship Phase 1, you have committed to reCAPTCHA with no exit.

| Dimension | Score | Plain English |
|---|---|---|
| Testability | 4/5 | Behavior is observable (bots blocked vs. passed); false-negative path needs explicit test cases |
| Integration Dependency | 4/5 | reCAPTCHA API + SMS Defender + existing login flow + admin portal |
| Operational Dependency | 2/5 | Mostly automated; manual override only if fallback is defined |
| Regression Risk | 5/5 | Wrong: bots get in; conservative: real users get blocked — both are production incidents |
| Observability Need | 5/5 | Invisible control; you can only know it's working if you measure it |

---

### 6. Phillip GPT on POEMS v1.0.pdf

#### Plain-English Summary
This URS covers embedding an AI assistant ("Ask AI") across the POEMS trading platforms. The assistant appears as a button on various screens, accepts free-text questions from clients, and responds with information drawn from the platform's data and knowledge base. The URS specifies which screens show the button, what context is passed to the AI, how disclaimer behavior is tracked, and how the feature is gated by source/account type.

**This is the only document in the folder rated Ready (5/5).**

#### What Must Already Exist
- POEMS trading platform with structured screens and data
- User session and account context infrastructure
- Feature flag system for rollout control
- Disclaimer and compliance tracking infrastructure

#### What the URS Proposes to Add or Change
- "Ask AI" entry point on multiple screens
- Context parameter passing (which screen, what account, what data is visible)
- Safe response behavior rules and disclaimer tracking
- Feature/source gating based on account type and subscription level

#### What Will Break If We Build From This URS Today
> Nothing critical. This is the strongest document in the folder.

#### What Needs to Happen First
Optional structural improvements:
- Separate the product-experience contract (what the AI shows) from the compliance contract (what disclaimers must appear) more explicitly.
- Add a rollout section describing the phased activation by source and account type.
- Strengthen the regression-boundary section to document which existing behaviors must not change when the AI button is added.

#### Engineering Risk in Plain English
This document is well-structured because it describes a clear system interface: where the button appears, what context it receives, and what rules govern the response. The risk is low because the boundaries are explicit. The remaining work is execution, not clarification.

| Dimension | Score | Plain English |
|---|---|---|
| Testability | 4/5 | Entry-point rules and context contracts are testable; disclaimer tracking needs integration testing |
| Integration Dependency | 3/5 | AI service + POEMS screens + session context + disclaimer tracking |
| Operational Dependency | 3/5 | AI response quality monitoring; response time SLAs |
| Regression Risk | 3/5 | Adding a button to existing screens is low risk if scoped correctly |
| Observability Need | 4/5 | AI response quality, disclaimer display rate, and escalation paths all need monitoring |

---

### 7. URS_P3_Stock Trade ticket - Lite mode.pdf

#### Plain-English Summary
This URS covers a simplified version of the P3 stock trading screen. Instead of showing every field and option, Lite Mode shows only what a new trader needs: counter, price, quantity, and Buy/Sell. Advanced options are hidden or collapsed. The URS proposes Lite Mode as a user-selectable option, defaulting to Pro (the full-featured version). Users can toggle between modes.

**What grooming confirmed:** Lite Mode supports Limit orders (default) and Market orders for eligible markets (US and HK). Pro Mode retains advanced orders (stop limit, limit-if-touched). Currency defaults to the traded market's currency, with SGD fallback for accounts not enabled for multi-currency. Usage is tracked by firing an event on the "Review Order" screen.

**What is still undecided:** Whether switching from Lite to Pro mode should reset all fields (safer — avoids wrong order submission) or retain them (more convenient). Device-level storage means a user's Lite/Pro preference applies to every account on that device. The performance strategy (partial reload vs. full screen refresh) is not decided. The analytics architecture (GA4 only or GA4 plus Firebase) is not confirmed.

#### What Must Already Exist
- P3 trading screen with full Pro Mode functionality
- Order validation logic and market rules per exchange
- Device-level preference storage

#### What the URS Proposes to Add or Change
- Lite Mode as a user-selectable variant
- Simplified order surface (Limit + eligible Market orders only)
- Mode preference persistence
- Lite vs. Pro usage telemetry

#### What Will Break If We Build From This URS Today
> **"If a user sets Lite Mode, switches to Pro, fills in fields, and switches back to Lite — what do they see?"** — The URS does not answer this. If fields carry over incorrectly, a user in Lite Mode could submit a trade using values from a Pro Mode order they had filled in. This is the highest-risk UX gap.

> **"A user with two accounts on the same device — which preference applies?"** — Device-level storage means both accounts share the same Lite/Pro preference. This creates a confusing experience that is not described or mitigated.

> **"Performance: partial reload vs. full refresh?"** — If the app reloads the entire trading screen on mode switch, it will feel slow. If it reloads selectively, developers need to know which values to refresh and when.

> **"Which logging system tracks Lite vs. Pro usage?"** — Without this confirmed, QA cannot write meaningful analytics tests, and the team cannot measure whether Lite Mode is being used.

#### What Needs to Happen First
1. **Product must decide field reset vs. retention** on mode switch. Default recommendation from grooming: reset for safety. Retain only price and quantity if there is a strong convenience case.
2. **Engineering must assess persistence alternatives** to device-level storage, or document the multi-account UX risk as accepted.
3. **Engineering must finalize the performance strategy** (partial reload vs. full refresh).
4. **Analytics must confirm the logging architecture** (GA4 only or GA4 + Firebase).

#### Engineering Risk in Plain English
The biggest risk in this URS is not the Lite Mode feature itself — it is the mode transition. A user who toggles modes and sees unexpected field values could submit a wrong order. This is not a code defect; it is a UX hazard created by undefined boundary behavior. The fix is a decision, not a code change.

| Dimension | Score | Plain English |
|---|---|---|
| Testability | 4/5 | Core order rules are testable; mode-switch behavior cannot be tested until the decision is made |
| Integration Dependency | 2/5 | Mostly UI and local state; no new backend systems |
| Operational Dependency | 1/5 | No manual operations |
| Regression Risk | 5/5 | Wrong mode-switch behavior causes incorrect trade submissions — a critical business risk |
| Observability Need | 4/5 | Lite vs. Pro event tracking is required to measure adoption and catch mode-switch bugs |

---

### 8. UT Enhancements - Phase 2 2026.pdf

#### Plain-English Summary
This document is a collection of Unit Trust improvement ideas bundled under one cover. Items include fixing a reporting issue, adding a Fund Screener, automating news updates, and hiding minute/hour filters. The document reads more like an email thread of requested changes than a structured specification.

**This is the weakest document in the folder. It cannot be used as a build contract in its current form.**

#### What Must Already Exist
- UT reporting, charting, and news features in POEMS

#### What the URS Proposes to Add or Change
- Fix reporting issue (unspecified)
- Add Fund Screener
- Automate UT news updates
- Hide minute/hour filters
- Possibly other items discovered during work

#### What Will Break If We Build From This URS Today
> **"Which of these items have been decided versus which are still ideas?"** — The document does not separate decided scope from exploratory suggestions. Building from it risks delivering items that are not actually approved.

> **"What is the not-in-scope boundary?"** — Without a clear not-in-scope statement, scope will expand during development. Engineers will be asked to include items that were never in the spec because they were mentioned in passing.

> **"Each item lacks a before/after description"** — "Fix reporting issue" does not say what is currently wrong, what behavior the fix produces, or what success looks like.

#### What Needs to Happen First
1. **Split into individual change requests** — each with a name, a current-state problem statement, a target-state outcome, and acceptance criteria.
2. **Add a not-in-scope statement** — what this Phase 2 does not include.
3. **Assign an owner to each item** — who is the BA for Fund Screener? Who is the technical lead?
4. **Prioritize items** — which ones are must-haves for Phase 2 vs. nice-to-haves?

#### Engineering Risk in Plain English
A document that bundles vague improvement ideas without separation, acceptance criteria, or scope boundaries will produce a chaotic build. Engineers will spend more time negotiating scope than writing code. The fix is not additional writing — it is structural: one item per document, each with a clear problem statement and acceptance criteria.

| Dimension | Score | Plain English |
|---|---|---|
| Testability | 2/5 | Items without acceptance criteria cannot be tested |
| Integration Dependency | 3/5 | Fund Screener and news automation may touch external systems |
| Operational Dependency | 2/5 | Automation reduces ops burden; news accuracy is an ops question |
| Regression Risk | 4/5 | Changes to existing UT reporting risk breaking current users |
| Observability Need | 3/5 | Standard usage analytics; nothing unusual specified |

---

### 9. WM - Accredited Investor Form.pdf

#### Plain-English Summary
This URS covers making the Accredited Investor (AI) declaration form accessible from within the POEMS mobile app (P3), specifically through the Me tab. Currently, clients who want AI status verification must use a different channel. The URS proposes bringing the form into P3 to reduce the effort required to complete AI verification and renewal.

**The key ambiguity:** The form involves a native app shell, an embedded web form (iframe), and a backend criteria engine. The document does not say which team owns which layer.

#### What Must Already Exist
- Accredited Investor business rules and criteria (set by compliance)
- Existing web form for AI declaration
- Reminder/notification system for renewals

#### What the URS Proposes to Add or Change
- P3 Me tab entry point for AI form
- Improved exposure in onboarding and renewal flows
- Joint account handling in the app

#### What Will Break If We Build From This URS Today
> **"Who builds the native shell versus who builds the web form?"** — The iFrame embedding approach is described, but the ownership boundary between P3 native team and the form team is not defined. This will cause duplicate work or gaps.

> **"What backend criteria engine handles the AI status check?"** — The URS references a criteria engine but does not name it or describe the API contract. Engineering cannot connect to a system they cannot identify.

> **"Joint account handling is mentioned but not specified"** — A client with a joint account needs a different form flow. This is referenced but not detailed.

#### What Needs to Happen First
1. **Define the ownership boundary** — Which team owns the native shell? Which team owns the web form? Which team owns the backend criteria engine?
2. **Name the criteria engine** and describe its API contract.
3. **Detail the joint account flow** — who can initiate AI status, what happens for each joint holder?

#### Engineering Risk in Plain English
The business rules for Accredited Investor status are stable and well-understood. The document's primary problem is organizational, not technical: multiple teams are involved and the ownership boundaries are blurred. Closing the boundary question is a project management action, not an engineering investigation.

| Dimension | Score | Plain English |
|---|---|---|
| Testability | 4/5 | Form field validation and criteria engine behavior are testable |
| Integration Dependency | 4/5 | Native shell + iframe + backend criteria engine; ownership across multiple teams |
| Operational Dependency | 2/5 | Compliance owns the criteria; ops manages renewals |
| Regression Risk | 4/5 | Changes to AI form access affect compliance-sensitive clients |
| Observability Need | 3/5 | Standard form analytics; submission rate and completion funnel |

---

### 10. CashCOupon.drawio

#### Plain-English Summary
This is a system flow diagram (draw.io XML) showing how the cash coupon lifecycle moves through multiple systems — from P3 triggering a coupon event, through Global Admin for marketing approval, to GBO for credit, and including Mambu for member notifications. The diagram is the most accurate picture of the end-to-end system flow across the coupon family.

**The gap:** Diagrams alone cannot serve as build contracts. This diagram needs a written companion that names each state, describes each transition, explains what each system does at each step, and defines the failure and recovery paths.

#### What the Diagram Shows
- P3 sends coupon event → Global Admin for marketing approval → GBO for credit → Mambu for member notification
- A queue/listener architecture handles asynchronous processing
- Retry and reconciliation behavior is implied in the flow

#### What Will Break If We Use This Diagram Alone
> **"What does each state transition mean in plain terms?"** — The diagram shows shapes and arrows; it does not explain the business meaning of each state or the conditions under which a transition fires.

> **"What does the failure path look like?"** — A diagram that shows only the happy path creates false confidence. A developer who follows only the arrows will build a system that cannot recover from errors.

> **"Which system owns which transition?"** — The diagram shows cross-system flows but does not assign ownership per step. When something breaks in production, no one knows who to call.

#### What Needs to Happen First
1. **Write a companion narrative** for each state: Pending, Processing, Redeemed, Error, Retry. What does it mean? When does it occur? What must be true to enter it?
2. **Describe the failure and recovery transitions** in plain terms — what causes a transition to Error, and what happens after?
3. **Annotate the diagram with owner labels** — which team owns each step.
4. **Version the diagram** and point to it as the source of truth. Without a version, it will drift from the actual implementation.

#### Engineering Risk in Plain English
This diagram is valuable as an integration map, but it is dangerous as a standalone artifact. Teams that treat diagrams as contracts end up building to the diagram's assumptions rather than to the written specification. The diagram and the written narrative must be maintained together.

| Dimension | Score | Plain English |
|---|---|---|
| Testability | 3/5 | Happy path is visible; failure paths are not |
| Integration Dependency | 5/5 | Crosses P3, Global Admin, GBO, Mambu — four systems |
| Operational Dependency | 3/5 | Failure and recovery behavior not described; ops must guess |
| Regression Risk | 5/5 | Changes to one system affect the whole flow |
| Observability Need | 5/5 | Every state transition and failure must be visible in production |

---

### 11. URS - DDA Linking and DDA Deposit.pdf

#### Plain-English Summary
This URS covers adding Direct Debit Authorisation (DDA) as a deposit method in POEMS. Currently, clients fund their accounts using PayNow or eNETS — both require the client to switch to their banking app. DDA would allow a client to link their bank account once, then deposit money instantly without leaving POEMS — the money moves directly via the DBS bank system.

The URS is structured in two phases. Phase 1 covers P3 for GBO trading accounts (M, C, KC, CC, V). Phase 2 covers Synergy accounts and the MyWealth app.

**The critical gap:** Section 3.7 (Finance Report) is entirely blank. Every payment method in a regulated financial institution needs a reconciliation report for the finance team. This gap cannot be resolved by engineering — it requires a conversation between the business and the finance department.

#### What Must Already Exist
- eGIRO infrastructure for bank account linking (partially related)
- DBS Vendor API integration for GIRO processing
- GBO system for posting credits to client accounts
- RPS (Regular Payment System) job running every 5 minutes
- Push notification infrastructure via poems engine API
- CIS (Central Information System) for account and bank record management

#### What the URS Proposes to Add or Change
- DDA Linking: one-time bank account linkage via DBS iBanking portal
- DDA Deposit: instant deposit via DBS FAST Collection API (SGD only, max $200,000)
- Push notifications at each stage: linking submitted, linking approved/rejected, deposit submitted, deposit received
- De-link flow: client can remove the bank linkage
- Phase 1: P3 GBO accounts. Phase 2: Synergy accounts and MyWealth

#### What Will Break If We Build From This URS Today
> **"Finance will not be able to reconcile DDA transactions"** — The Finance Report requirement (section 3.7) is entirely TBC. Without a defined report format and delivery mechanism, the finance team cannot audit DDA transactions. This is a compliance and audit risk, not an engineering defect.

> **"Phase 2 account eligibility has open questions"** — Advisory accounts (S2, UTW) appear in multiple places with conflicting instructions. One row says the account links to S2; another says it links to UTW. A developer will implement one answer and be told it was wrong.

> **"Non-functional requirements are all blank"** — No performance SLA for the DBS API, no security controls for storing bank account references, no operational runbook for handling DBS async response failures. Building without these means the system will work in testing and behave unpredictably in production under load.

> **"Phase 2 has no delivery sequence"** — SynergyBO and MyWealth are both listed as Phase 2 targets, but which comes first? Engineering cannot plan the sprint backlog without this.

#### What Needs to Happen First
1. **Katherine (Finance) and Alvin must define the Finance Report** — format, frequency, delivery method (email? API? portal?), and who receives it. This is a business conversation, not an engineering task.
2. **Shawn and Jamie must resolve the Advisory account mapping** — which account type links to which DDA account for Synergy accounts.
3. **Non-functional requirements must be added** — performance SLA for DBS API (expected response time, timeout behavior), security controls for bank account data, ops runbook for async failure scenarios.
4. **Phase 2 delivery order must be confirmed** — SynergyBO before MyWealth, or vice versa.

#### Engineering Risk in Plain English
This is the most integration-heavy document in the folder. The chain is: P3 app → DBS iBanking website → P3 webhook → CIS API → GBO API → RPS job → GBO posting. Every link in that chain is a potential failure point. The document describes the happy path well. The failure and reconciliation paths are not described.

| Dimension | Score | Plain English |
|---|---|---|
| Testability | 4/5 | Field rules and status transitions are well-specified; open account questions reduce coverage |
| Integration Dependency | 5/5 | DBS FAST + DBS Vendor + CIS + GBO + RPS + poems engine push notifications + Figma — the longest integration chain in the folder |
| Operational Dependency | 3/5 | Finance reconciliation not defined; DBS async response timing is ops-sensitive |
| Regression Risk | 4/5 | Changes to CIS, GBO, and RPS affect live payment flows for all users |
| Observability Need | 5/5 | Every link in the chain needs monitoring: linking status, DBS response, posting outcome, push delivery |

---

### 12. URS -POEMS Shareholder Meeting P3 URS.pdf

#### Plain-English Summary
This URS covers a new sub-module within the Corporate Actions section of POEMS P3. Clients who hold shares in companies listed on SGX will see upcoming shareholder meetings for securities they own. They can register to attend in person or submit a vote (with or without appointing a proxy). Submitted instructions are sent as a CSV to a designated email address for processing by the company secretary's office.

**What is strong:** The Refinitiv data field mapping table is excellent — it names every field, shows its logic, and gives real examples. This is the clearest data contract in the folder.

**The key risk:** The submission mechanism is email. A client submits their vote by sending an email with a CSV attachment. There is no confirmation of delivery, no retry if the email fails, and no audit trail beyond the sent email. For a regulated securities environment, vote submission is a legally significant action — the absence of delivery confirmation is a real operational risk.

#### What Must Already Exist
- Corporate Actions module in P3
- Refinitiv General_Meetings_Daily data feed (delivered Monday to Friday including public holidays)
- CIS for account holder particulars (name, email, residential address)
- SGX meeting schedule public page

#### What the URS Proposes to Add or Change
- New Shareholder Meeting sub-module in Corporate Actions
- Meeting cards for holdings with upcoming meetings (XSES only)
- Meeting detail page with SGX hyperlink
- Attendance and voting flows: Attend-in-person, Vote Only, proxy appointment
- Share quantity validation (vote with all shares or some shares)
- Submission to proxy@phillip.com.sg via email
- Withdrawal Admin interface for ops review
- View submitted instructions with status badge

#### What Will Break If We Build From This URS Today
> **"A client submits a vote and does not know if it arrived"** — Email has no delivery confirmation. A client who submits a proxy instruction has no way to verify it was received. If the email fails silently, the client believes they have voted when they have not. In a regulated context, this is a legal exposure.

> **"The 72-hour free shares rule is not explained"** — The URS states that only shares held 72 hours before the meeting are eligible for voting, but it does not say which system calculates this or which API provides the data. Engineering cannot implement this without a data source.

> **"The Withdrawal Admin interface may not be built"** — The URS describes it as "if creating a UI in Withdrawal Admin is possible" — this is not a requirement, it is a hope. Ops may be handling submissions manually with no tooling support.

> **"Refinitiv data is trusted without reconciliation"** — What happens if the Refinitiv feed is delayed, contains errors, or goes missing? The URS does not address data quality or fallback behavior.

#### What Needs to Happen First
1. **Replace email-only submission with a delivery-confirmed mechanism** — either an in-app submission status screen, an email read-receipt, or an API acknowledgment. "Sent email" is not the same as "vote received."
2. **Identify the system and API that provides the 72-hour free shares calculation** — this is a compliance-relevant calculation; it must be traceable and auditable.
3. **Confirm the Withdrawal Admin scope** — build the UI or document the manual ops process. Do not leave it as "if possible."
4. **Define Refinitiv data reconciliation** — what happens when the feed is late or contains anomalies?

#### Engineering Risk in Plain English
The URS is well-structured for the user-facing flows — the meeting card display, voting mechanics, and share quantity validation are all clear and testable. The email submission mechanism is the single most significant engineering risk in this document. Vote submission in a regulated securities context carries legal weight; treating it as a simple email is inadequate for production.

| Dimension | Score | Plain English |
|---|---|---|
| Testability | 4/5 | Data mapping table is explicit; Refinitiv field logic is well-specified; vote validation rules are clear |
| Integration Dependency | 3/5 | Refinitiv feed + CIS + SGX hyperlink + email + Withdrawal Admin — moderate surface |
| Operational Dependency | 3/5 | Email delivery is unreliable; 72-hour calculation source unknown; ops review process not confirmed |
| Regression Risk | 3/5 | New sub-module; existing Corporate Actions behavior must not be affected |
| Observability Need | 4/5 | Refinitiv data freshness, submission status, vote accuracy, email delivery all need monitoring |

---

## Cross-Document Landscape

### Documents That Share Systems (Integration Overlaps)

Three or more documents touch the same systems:

| Shared System | Documents That Use It |
|---|---|
| P3 (client app) | Cash Coupon, DDA, Shareholder Meeting, Lite Mode, Smart Portfolio, AI GPT |
| GBO (credits/posting) | Cash Coupon, Amalgamated Trade, DDA |
| CIS (account data) | DDA, Shareholder Meeting, AI GPT |
| Global Admin | Cash Coupon, Amalgamated Trade |
| Mambu (notifications) | Cash Coupon |

**Practical implication:** Changes to GBO or CIS affect multiple features simultaneously. A developer working on Cash Coupon changes needs to know that DDA and Amalgamated Trade also touch GBO. This is not visible in any single URS — it is a cross-document risk that requires a coordinator.

### Documents That Share the Same BA or Owner

| Owner | Documents |
|---|---|
| Steven (BA) | Smart Portfolio Phase 2, Shareholder Meeting |
| Marketing | Amalgamated Trade, Cash Coupon |
| GBO Owner | Cash Coupon, Amalgamated Trade, DDA |
| P3 Team | Lite Mode, Smart Portfolio, Cash Coupon, DDA, AI GPT, Shareholder Meeting |

**Practical implication:** BA bandwidth is a bottleneck. Several high-priority corrections (Smart Portfolio Phase 2 URS update, Cash Coupon lifecycle fix) all require Steven. Planning should sequence these to avoid BA overload.

### Documents That Cannot Be Built Together

| Pair | Why They Conflict |
|---|---|
| Cash Coupon Global Admin + CashCOupon.drawio | The diagram and the text URS describe different lifecycle states. Both must be updated together. |
| Amalgamated Trade + Cash Coupon | Both send to GBO; the batch timing for Amalgamated Trade affects when Cash Coupon credits land. Delivery sequence matters. |
| DDA + Smart Portfolio Phase 2 | Both add new RSP/payment flows via eGIRO; they share the eGIRO infrastructure and the central UI team. |

---

## Recommended Build Order

### Wave 1 — Ready to Start Now (after minor cleanup)
1. **Phillip GPT on POEMS** — fully ready. Can start immediately.
2. **Accredited Investor Form** — needs ownership boundary defined, then can start.
3. **reCAPTCHA replacement** — needs migration contract and Phase 2 scope, then can start.

### Wave 2 — After Specific Gaps Are Closed
4. **Smart Portfolio Phase 2** — after Steven's URS update (redirect contract, failure flow, eGIRO callback).
5. **Shareholder Meeting** — after submission confirmation mechanism is defined.
6. **Lite Mode Trade Ticket** — after the four open decisions are closed (field reset, persistence, performance, analytics).

### Wave 3 — After Business Decisions Land
7. **DDA Linking and DDA Deposit (Phase 1)** — after Finance Report scope is defined and Advisory account mapping is resolved.
8. **Cash Coupon Global Admin** — after the GBO error contract and reconciliation policy are defined.

### Wave 4 — After Marketing Decisions Land
9. **Amalgamated Trade** — after the amalgamated market list and grouping behavior are confirmed by Marketing.

### Not Yet Schedulable
10. **Refer A Friend** — needs baseline/CR separation.
11. **UT Enhancements Phase 2** — needs full decomposition into individual items.
12. **CashCOupon.drawio** — needs written companion narrative (can be done in parallel with Cash Coupon Global Admin work).

---

## Top 10 Action Items Across the Folder

| Priority | Action | Owner | Blocks |
|---|---|---|---|
| P0 | Define Finance Report for DDA (format, delivery, frequency) | Katherine + Alvin (Finance) | DDA Phase 1 |
| P0 | Provide amalgamated market list (which markets are amalgamated) | Marketing | Amalgamated Trade |
| P0 | Fix Cash Coupon lifecycle: Redeemed only after GBO success | BA + GBO Owner | Cash Coupon |
| P0 | Update Smart Portfolio URS: redirect, failure/cancel, eGIRO callback | Steven (BA) | Smart Portfolio Phase 2 |
| P0 | Close Lite Mode 4 decisions: reset, persistence, performance, analytics | Product + Engineering | Lite Mode |
| P1 | Define Vote submission confirmation (replace email-only) | BA + Operations | Shareholder Meeting |
| P1 | Identify 72-hour free shares data source | BA + CIS team | Shareholder Meeting |
| P1 | Resolve Phase 2 Advisory account mapping for DDA | Shawn + Jamie | DDA Phase 2 |
| P1 | Define reCAPTCHA migration contract and rollback procedure | BA + Engineering | reCAPTCHA |
| P1 | Split Refer A Friend into baseline vs. change | BA | Refer A Friend |

---

*Document last updated: 22 June 2026*
*Assessment basis: 12 artifacts (10 PDFs, 1 draw.io, 1 draw.io diagram) + 4 grooming sessions (5 June 2026)*
