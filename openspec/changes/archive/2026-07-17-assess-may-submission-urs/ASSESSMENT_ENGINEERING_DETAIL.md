# May Submission URS Assessment — Detailed Engineering Addendum

This addendum deepens the core assessment with engineering-oriented dimensions that are useful during planning, estimation, and handoff:

- **Testability** — how directly the doc can be translated into verifiable test cases
- **Integration Dependency** — how much the feature depends on cross-system contracts
- **Operational Dependency** — how much manual teams / operational procedures influence correctness
- **Regression Risk** — how likely a change is to break an existing current-state feature
- **Observability Need** — how strongly the feature needs logs, metrics, alerts, reconciliation, or audit trails

## Rating Scale

| Score | Meaning |
|---|---|
| 5 | Very high |
| 4 | High |
| 3 | Medium |
| 2 | Low |
| 1 | Very low |

## Dimension definitions

### Testability
- **5**: clear AC and directly testable rules
- **3**: partially testable, some inferred behavior
- **1**: hard to derive stable test cases from the doc

### Integration Dependency
- **5**: depends on several external systems or cross-team contracts
- **3**: moderate dependency, some system boundaries matter
- **1**: mostly local / self-contained capability

### Operational Dependency
- **5**: correctness depends heavily on manual ops / business handling / approvals / runbooks
- **3**: some business operations involved but not central
- **1**: almost entirely system-driven

### Regression Risk
- **5**: likely to destabilize important current-state behavior if changed badly
- **3**: targeted regression risk, manageable with focused testing
- **1**: low risk to existing baseline

### Observability Need
- **5**: requires strong runtime monitoring, audit trail, reconciliation, or alerts
- **3**: moderate logging / analytics sufficient
- **1**: minimal observability need beyond normal UX/product analytics

---

## Per-File Detailed Engineering Assessment

### Gami - Amalgamated Trade.pdf

| Dimension | Score | Rationale |
|---|---|---|
| Testability | 2 | Amalgamated-market list and grouping criteria still open after grooming. |
| Integration Dependency | 5 | Real-time → end-of-day scheduler adds new integration. |
| Operational Dependency | 4 | Marketing-driven market/grouping rules. |
| Regression Risk | 4 | Real-time → batch migration changes downstream timing. |
| Observability Need | 5 | Batch outcomes, FIFO trace, per-counter application required. |

**Detailed assessment**
- Main weakness is not business intent but incomplete edge-case contract and the unconfirmed amalgamation list.
- Grooming confirmed batch + amalgamation architecture; remaining blocker is the canonical amalgamated-market list and grouping behavior from Marketing.

**Engineering implication**
- Requires explicit scenario matrix for cutoff timing, partial-settlement, and counter-level application before implementation sizing is trustworthy.

---

### Gami - Cash Coupon Global Admin.pdf

| Dimension | Score | Rationale |
|---|---|---|
| Testability | 2 | State conflict prevents stable expected outcomes. |
| Integration Dependency | 5 | P3, Global Admin, and GBO contracts all matter. |
| Operational Dependency | 5 | Marketing approval/rejection and GBO error handling are core to the workflow. |
| Regression Risk | 5 | Incorrect state modeling can corrupt both user-facing and operational flows. |
| Observability Need | 5 | Approval states, rejection path, and GBO errors all require strong auditability. |

**Detailed assessment**
- This is one of the riskiest documents in the set because system states and operational process are tightly coupled.
- It is not enough to document UI or API behavior; the lifecycle itself must be contractually correct.
- A wrong interpretation here would likely produce silent operational breakage, not just visible UI bugs.

**Engineering implication**
- Must define state transition table and operational notification contract before design or estimation.

---

### ITSR 330853 Refer A Friend URS Revised 1.1.pdf

| Dimension | Score | Rationale |
|---|---|---|
| Testability | 3 | Many enhancements are testable, but mixed baseline/target scope blurs expected behavior. |
| Integration Dependency | 3 | Depends on downstream qualification and reward attribution flows. |
| Operational Dependency | 2 | Mostly product/system behavior; less manual operational handling than coupon docs. |
| Regression Risk | 4 | Existing referral flows could regress if baseline vs delta is misunderstood. |
| Observability Need | 3 | Progress tracking, notifications, and reward flow need product analytics and flow monitoring. |

**Detailed assessment**
- The document is conceptually rich but contractually noisy.
- The main risk is shipping the wrong delta rather than failing to understand the domain.
- Once baseline-vs-CR separation is done, testability improves materially.

**Engineering implication**
- Separate regression suite for baseline RAF flow and delta suite for each CR enhancement.

---

### ITSR 369004 SMART Portfolio Phase 2.pdf

| Dimension | Score | Rationale |
|---|---|---|
| Testability | 4 | Field rules precise; redirect/cancel flows not yet testable. |
| Integration Dependency | 4 | PayNow, eGIRO, internal transfer, central UI callback. |
| Operational Dependency | 3 | RSP execution on 7th; suspension follow-up. |
| Regression Risk | 4 | Lump-sum flow must remain unchanged. |
| Observability Need | 4 | RSP state transitions, payment return, suspension events required. |

**Detailed assessment**
- One of the cleanest engineering handoff documents in the set.
- Grooming clarified RSP scope (monthly only, 7th execution, suspend-not-terminate) but surfaced new contract gaps: payment redirect, eGIRO return, failure/cancel flows.

**Engineering implication**
- Good candidate for direct implementation only after Steven's URS update adds the missing flow contracts.

---

### ITSR [369574] RECAPTCHA TO REPLACE GEETESTv1.0.pdf

| Dimension | Score | Rationale |
|---|---|---|
| Testability | 4 | Phases and target controls are clear, though admin portal scope needs clarification. |
| Integration Dependency | 4 | Involves auth/OTP flows, protection controls, and potentially admin portal behavior. |
| Operational Dependency | 2 | Less manual operations, more runtime safety/policy behavior. |
| Regression Risk | 5 | Replacement of a current security control can break login/OTP flows or weaken defenses. |
| Observability Need | 5 | Security rollout requires monitoring, fallback, abuse detection, and comparative metrics. |

**Detailed assessment**
- Engineering risk is concentrated in migration safety, not in feature understanding.
- This doc should be treated like a production control-plane change, not a simple UI enhancement.

**Engineering implication**
- Must include rollout telemetry, fallback trigger, and attack/abuse monitoring requirements in implementation plan.

---

### Phillip GPT on POEMS v1.0.pdf

| Dimension | Score | Rationale |
|---|---|---|
| Testability | 4 | Many parameter-passing, UX, disclaimer, and gating rules are testable. |
| Integration Dependency | 4 | Depends on platform screens, iframe embedding, context data, flags, and model source logic. |
| Operational Dependency | 3 | Compliance and content governance matter, but runtime flow is mostly system-driven. |
| Regression Risk | 3 | Can affect existing platform surfaces, but feature flags reduce blast radius. |
| Observability Need | 4 | Needs analytics, disclaimer tracking, flag observability, and safety-related runtime monitoring. |

**Detailed assessment**
- This is one of the strongest docs because it gives engineering enough product and UX specificity to move forward.
- The remaining concern is governance separation, not core implementation ambiguity.

**Engineering implication**
- Good candidate for phased delivery if compliance rules and feature flag strategy are handled explicitly.

---

### URS_P3_Stock Trade ticket - Lite mode.pdf

| Dimension | Score | Rationale |
|---|---|---|
| Testability | 4 | Order/market rules are explicit; mode-switch behavior not yet testable. |
| Integration Dependency | 2 | Mostly UI/state-layer change over an existing trading core. |
| Operational Dependency | 1 | Minimal manual ops involvement. |
| Regression Risk | 5 | Incorrect submission risk explicitly flagged after grooming. |
| Observability Need | 4 | Light vs Pro event tracking on Review Order required. |

**Detailed assessment**
- Strong, bounded feature variant spec.
- Biggest risk is not misunderstanding the Lite mode itself but breaking the existing Pro behavior or state transfer logic.
- Grooming downgraded the doc from `5/5` to `4/5` because four decisions remain open: field reset, persistence, performance, analytics.

**Engineering implication**
- Shared validation core plus strong mode-transition testing should be central to implementation design.
- Lock the four open decisions before estimation.

---

### UT Enhancements - Phase 2 2026.pdf

| Dimension | Score | Rationale |
|---|---|---|
| Testability | 2 | Too many bundled items with uneven specificity; hard to derive stable test suite. |
| Integration Dependency | 3 | Depends on several existing UT-related systems/flows but not all equally. |
| Operational Dependency | 2 | Mostly product/system changes, though some reporting/news processes may involve ops context. |
| Regression Risk | 4 | Existing UT features may regress because multiple unrelated changes are bundled together. |
| Observability Need | 3 | Moderate telemetry/logging required, especially for reporting/news automation. |

**Detailed assessment**
- The weakest area is bundling, not necessarily domain uncertainty.
- By grouping unrelated enhancements in one loose contract, the doc becomes difficult to estimate, test, and phase safely.

**Engineering implication**
- Split by enhancement before estimation; otherwise risk and effort will be mispriced.

---

### WM - Accredited Investor Form.pdf

| Dimension | Score | Rationale |
|---|---|---|
| Testability | 4 | Business rules are stable and target entry-surface changes are testable. |
| Integration Dependency | 4 | Native shell, web/iframe form, backend criteria, and notification channels all matter. |
| Operational Dependency | 2 | Most logic is system-driven; low manual operational branching. |
| Regression Risk | 4 | Existing access path and user renewal experience can regress during channel migration. |
| Observability Need | 3 | Renewal reminders, submission success, and channel usage should be monitored. |

**Detailed assessment**
- Strong domain rules, moderate implementation dependency complexity.
- Main ambiguity is channel ownership, not eligibility logic.

**Engineering implication**
- Resolve shell-vs-form ownership first, then implementation/test planning becomes straightforward.

---

### CashCOupon.drawio

| Dimension | Score | Rationale |
|---|---|---|
| Testability | 3 | Good for flow validation, weaker as standalone acceptance contract. |
| Integration Dependency | 5 | Pure cross-system interaction artifact across multiple services. |
| Operational Dependency | 3 | Retry/reconciliation behaviors imply operational awareness and follow-up. |
| Regression Risk | 5 | If used as target truth without alignment, it can drive incorrect integration changes. |
| Observability Need | 5 | Queue processing, scheduled scans, retries, and status reconciliation need strong runtime visibility. |

**Detailed assessment**
- This is a high-value integration artifact but not sufficient as a standalone spec.
- Its risk lies in being almost-canonical: teams may trust it too much unless it is reconciled with textual URS sources and actual current implementation.

**Engineering implication**
- Use as reconciliation diagram, not sole contract source.

---

## Cross-File Engineering Conclusions

### Highest testability
- `ITSR 369004 SMART Portfolio Phase 2.pdf`
- `URS_P3_Stock Trade ticket - Lite mode.pdf`
- `Phillip GPT on POEMS v1.0.pdf`

### Highest integration dependency
- `Gami - Cash Coupon Global Admin.pdf`
- `CashCOupon.drawio`
- `Gami - Amalgamated Trade.pdf`
- `WM - Accredited Investor Form.pdf`
- `ITSR [369574] RECAPTCHA TO REPLACE GEETESTv1.0.pdf`

### Highest operational dependency
- `Gami - Cash Coupon Global Admin.pdf`
- `Gami - Amalgamated Trade.pdf`
- `CashCOupon.drawio`

### Highest regression risk
- `Gami - Cash Coupon Global Admin.pdf`
- `ITSR [369574] RECAPTCHA TO REPLACE GEETESTv1.0.pdf`
- `CashCOupon.drawio`
- `Gami - Amalgamated Trade.pdf`
- `ITSR 330853 Refer A Friend URS Revised 1.1.pdf`
- `UT Enhancements - Phase 2 2026.pdf`
- `WM - Accredited Investor Form.pdf`

### Highest observability need
- `Gami - Cash Coupon Global Admin.pdf`
- `ITSR [369574] RECAPTCHA TO REPLACE GEETESTv1.0.pdf`
- `CashCOupon.drawio`
- `Gami - Amalgamated Trade.pdf`

---

## Final Detailed Verdict

The strongest improvement to the assessment is not changing which docs are good or weak — it is clarifying **why** they are good or weak from an engineering perspective.

- Some docs are weak because they are **ambiguous**.
- Some are weak because they are **integration-heavy and operationally coupled**.
- Some are strong because they are **directly testable even if not perfectly polished**.
- Some are risky because they modify **important current-state flows** and therefore demand explicit regression and observability planning.

This engineering detail layer should be used together with the readiness, feature-delta, and remediation outputs to drive planning, estimation, and BA cleanup.
