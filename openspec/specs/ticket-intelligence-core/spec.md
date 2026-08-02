# ticket-intelligence-core Specification

## Purpose
Define the canonical shared Jira ticket intelligence contract for the TDT ecosystem. This specification is the long-lived source of truth for the shipped v1 bundle contract implemented in `jira-skill` and consumed by `jira-epic-report`, `jira-daily-reports`, and `webhook-receiver`.

## Requirements

### Requirement: Produce a reusable ticket intelligence bundle
The system SHALL produce a reusable ticket intelligence bundle for Jira issues that multiple ecosystem tools can consume without changing analysis semantics.

#### Scenario: Bundle contract is validated and serializable
- **WHEN** the shared bundle crosses a repo boundary or is persisted as a fixture artifact
- **THEN** it SHALL be represented by versioned Pydantic models that validate structure and support deterministic serialization

#### Scenario: Multiple consumers read the same bundle
- **WHEN** `jira-epic-report`, `jira-daily-reports`, or `webhook-receiver` requests analysis for the same Jira snapshot
- **THEN** the system SHALL produce the same canonical bundle for that snapshot
- **AND** each consumer SHALL be able to read the bundle without needing repo-specific analysis logic

#### Scenario: The bundle is versioned
- **WHEN** the intelligence contract changes
- **THEN** the system SHALL expose a versioned bundle shape so consumers can detect compatible versus breaking changes

#### Scenario: Evidence is attached
- **WHEN** a normalized signal is emitted in the bundle
- **THEN** the bundle SHALL carry evidence references or summaries that explain the signal source

### Requirement: Normalize existing signals into the shared contract
The system SHALL normalize the existing ecosystem signals into the shared bundle and preserve the strongest existing heuristics rather than reimplementing them from scratch.

#### Scenario: Risk signals are normalized
- **WHEN** `jira-epic-report` produces weighted risk and severity data
- **THEN** the shared bundle SHALL expose those values as normalized risk fields

#### Scenario: Blocking signals are normalized
- **WHEN** `jira-epic-report` produces impact radius, chain depth, or circular dependency findings
- **THEN** the shared bundle SHALL expose those values as normalized blocking fields

#### Scenario: Freshness signals are normalized
- **WHEN** `webhook-receiver` or `jira-daily-reports` computes freshness source, run id, refreshed timestamps, or other portable freshness facts
- **THEN** the shared bundle SHALL expose those portable freshness facts in a canonical shape
- **AND** pair-state tracking, debounce windows, in-flight state, and dispatch mechanics SHALL remain consumer-local

#### Scenario: Completeness gaps are normalized
- **WHEN** `jira-daily-reports` or `jira-epic-report` identifies missing metadata
- **THEN** the shared bundle SHALL expose those gaps explicitly

#### Scenario: Capacity signals are normalized
- **WHEN** `jira-epic-report` or `jira-daily-reports` detects overload, work distribution, or person capacity pressure
- **THEN** the shared bundle SHALL expose those values in a canonical capacity model

#### Scenario: Churn and insight signals are normalized
- **WHEN** changelog or comment analysis detects churn, reopen loops, or risk flags
- **THEN** the shared bundle SHALL expose those findings in a canonical insight model

#### Scenario: Existing heuristics remain the source of truth
- **WHEN** a signal already exists in one or more consumers
- **THEN** the system SHALL wrap or normalize the existing detection logic rather than inventing a second competing heuristic

### Requirement: Generate explainable triage suggestions
The system SHALL emit explainable triage suggestions that identify what action is recommended, why it is recommended, and what evidence supports it.

#### Scenario: Suggestion is actionable
- **WHEN** one or more bundle signals triggers a recommendation
- **THEN** the bundle SHALL include a named action, a reason, and the evidence that drove it

#### Scenario: Suggestion can be dismissed or overridden
- **WHEN** a consumer chooses not to apply a recommendation
- **THEN** the system SHALL allow that suggestion to be dismissed or overridden without corrupting future analysis

#### Scenario: Suggestion evidence is visible
- **WHEN** a suggestion is rendered in any consumer
- **THEN** the system SHALL expose the supporting evidence so users can verify the recommendation

### Requirement: Support consumer-specific triage policies
The system SHALL allow consumers to provide local policy guidance that influences prioritization without changing the canonical analysis contract.

#### Scenario: Reminder escalation remains consumer-local in v1
- **WHEN** `jira-daily-reports` or `webhook-receiver` applies reminder ladders, suppression, or transition-specific escalation rules
- **THEN** those rules SHALL remain outside the canonical shared signal taxonomy in v1 and SHALL consume the bundle as local policy input

#### Scenario: Consumer guidance changes priority
- **WHEN** a consumer applies local guidance for labels, teams, thresholds, or refresh rules
- **THEN** the system SHALL adjust prioritization while preserving the same underlying signal bundle

#### Scenario: Policy does not change raw facts
- **WHEN** local guidance is applied
- **THEN** the system SHALL NOT rewrite the underlying Jira facts or evidence

### Requirement: Respect issue visibility and access boundaries
The system SHALL only analyze and expose Jira data that the authenticated consumer is allowed to access.

#### Scenario: Restricted issue is hidden
- **WHEN** Jira denies access to an issue or field
- **THEN** the bundle SHALL mark that data as unavailable instead of leaking restricted content

#### Scenario: Consumer scope is narrower than the snapshot
- **WHEN** a consumer requests a snapshot that includes issues outside its access scope
- **THEN** the system SHALL omit or redact inaccessible issue details while preserving the rest of the bundle

### Requirement: Infer RCA, prevention, severity, and fix-state context from ticket evidence plus structured SCM intelligence
The system SHALL support ticket intelligence that combines Jira ticket evidence with optional structured SCM intelligence evidence. Ticket evidence SHALL remain the deterministic baseline. Structured SCM intelligence MAY strengthen or clarify RCA, prevention guidance, fix status, and severity when available. Local worktree hints SHALL be treated as lightweight augmentation unless stronger SCM intelligence is present. Optional semantic or LLM-assisted analysis MAY exist as additive enrichment, but SHALL NOT be required for the deterministic core contract. When multiple issues are emitted together, the per-issue output SHALL support stable ordering by a composite severity assessment derived from normalized risk, blocking, completeness, and available evidence layers.

#### Scenario: Ticket-only inference is available
- **WHEN** analysis only has Jira snapshot content such as summary, description, comments, changelog, links, and status
- **THEN** the system SHALL be allowed to infer RCA, prevention guidance, fix status, and risk severity from that ticket evidence alone
- **AND** any resulting analysis SHALL remain clearly evidence-backed rather than presented as code-verified truth

#### Scenario: Structured SCM intelligence evidence is available
- **WHEN** analysis is provided structured SCM intelligence such as branch role, merge request state, source/target branch, pipeline status, commit recency, or equivalent traceable SCM metadata
- **THEN** the system SHALL incorporate that evidence into RCA, prevention, severity, and fix-status evaluation
- **AND** the resulting bundle SHALL preserve traceable evidence showing which conclusions were grounded in ticket evidence versus SCM intelligence evidence

#### Scenario: Lightweight worktree evidence is available without SCM truth
- **WHEN** analysis only has lightweight local worktree hints such as worktree commit-message matches, diff-string matches, branch-local grep hits, checked-out branch names, or code-extracted ticket references
- **THEN** the system SHALL treat that material as heuristic augmentation rather than authoritative branch or fix-state truth
- **AND** the resulting bundle SHALL preserve that the evidence came from local worktree heuristics rather than live merge-request or pipeline state

#### Scenario: Active testing branch is distinguished from historical fix evidence
- **WHEN** branch-related evidence is emitted in the bundle
- **THEN** the contract SHALL allow the system to distinguish active testing branch context from historical fix branch context, merged-fix references, and unknown branch state
- **AND** the system SHALL NOT imply that a checked-out local branch alone proves current review state, merge state, or verified fix state

#### Scenario: Strong fix-state claims require stronger evidence
- **WHEN** the system emits a strong fix-state conclusion such as merged, verified, or actively under review
- **THEN** that conclusion SHALL require stronger evidence classes such as QA verification, merge-request state, pipeline state, or equivalent explicit traceable evidence
- **AND** commit presence alone SHALL NOT be treated as equivalent to a confirmed merged or verified fix

#### Scenario: True severity is strengthened by SCM intelligence
- **WHEN** structured SCM intelligence indicates broader blast radius, critical path impact, risky call sites, or fix incompleteness not visible from ticket text alone
- **THEN** the system SHALL allow the normalized severity assessment to reflect that stronger evidence
- **AND** the evidence trail SHALL identify the SCM intelligence inputs that changed the assessed severity

#### Scenario: Bundle output is stably ordered by composite severity
- **WHEN** multiple issues are emitted in a bundle or written to Sheets
- **THEN** the system SHALL support a deterministic descending order based on a composite per-issue severity score
- **AND** that score SHALL be allowed to combine normalized risk, blocking pressure, completeness gaps, RCA confidence, fix-status context, and available evidence layers
- **AND** the emitted output MAY also include a human-readable severity rank label for auditability

#### Scenario: Prevention guidance is code-aware
- **WHEN** SCM intelligence or worktree evidence is available for the affected implementation context
- **THEN** prevention guidance SHALL be allowed to reference concrete safeguards suggested by that evidence such as missing tests, missing guards, weak validation, or absent monitoring
- **AND** the resulting prevention output SHALL remain additive and evidence-backed

#### Scenario: Evidence classes are layered explicitly
- **WHEN** the bundle records ticket intelligence evidence
- **THEN** the contract SHALL allow at least three distinct evidence layers: deterministic ticket evidence, structured SCM intelligence evidence, and optional semantic enrichment
- **AND** optional semantic enrichment SHALL remain additive and SHALL NOT be required for deterministic bundle production

#### Scenario: FixStatus evidence chain is priority-ordered
- **WHEN** the system detects fix status for a Jira issue
- **THEN** evidence SHALL be evaluated in this priority order (strongest first):
  1. **SCM GitLab** — structured MR state from the GitLab API (`merged` → FIXED, `opened` → IN_REVIEW, `closed/canceled/locked` → UNFIXED).
  2. **QA comments** — human verification text extracted from Jira comment bodies. Comment bodies are stored as ADF (Atlassian Document Format) in the Jira Cloud v3 API; the system SHALL normalize ADF to plain text before pattern matching.
  3. **MR text references** — plain-text strings referencing MRs/PRs found in comment text (e.g. `MR !42`, `merge_requests/123`). Strings prefixed with `"branch "` (worktree branch evidence) SHALL be excluded from this step and routed back to step 5. Bare MR URLs default to FIXED; phrase references without explicit state keywords default to IN_REVIEW.
  4. **Jira status** — canonical status-to-fix-status mapping. Multi-word phrases are checked first (`in progress` → IN_PROGRESS, `in review` → IN_REVIEW, `in test` → IN_REVIEW). Single-word tokenization prevents `"done"` matching `"Undone"`.
  5. **Worktree git evidence** — presence of git commits referencing the issue key. Any non-zero commit count in any worktree → IN_PROGRESS.

#### Scenario: RCA taxonomy has 8 ordered categories with 4P lens (v2.0)
- **WHEN** the system infers root cause category from ticket evidence
- **THEN** it SHALL match against the following priority-ordered taxonomy and return the first match:
  1. **Crash / ANR / Force Close** (4P: Plant) — app crash, force close, ANR, fatal exception, thread not responding.
  2. **UI Layout / Visual Defect** (4P: Plant) — overlap, cut-off, truncated, misaligned, spacing, positioning, color, icon placement, partial display, hidden/obscured elements.
  3. **Wrong Data / Incorrect Value** (4P: Plant) — wrong amount, wrong format, data not updating, stale cache, truncated data value, platform discrepancy.
  4. **Text / Font Display** (4P: Plant) — font size, text size, system font scaling, Dynamic Type, display text too large/small/missing.
  5. **Feature Not Working / Missing** (4P: Procedures) — feature broken, missing, regression, notification not received, loading stuck, blank content, button has no effect.
  6. **3rd Party Issue (WebView, API, SDK)** (4P: Policies) — login fail, auth error, 401/403, token expired, session timeout, network error, timeout, offline, API 500/502/503, sync fail, WebView blank, SDK crash, IdP unreachable, vendor outage.
  7. **Performance / Slow Loading** (4P: Plant) — slow, lag, freeze, hang, jank, memory leak, high CPU.
  99. **Other / Unclassified** (4P: none) — sentinel returned when non-empty content matches no pattern.
- **AND** a "hidden and cannot" (data hidden and not scrollable) or "disabled" pattern SHALL match `UI Layout / Visual Defect` (category 2) rather than `Feature Not Working / Missing` (category 5), because the element is present but not accessible — not absent.
- **AND** "disabled button" and "bold text display" patterns SHALL match `UI Layout / Visual Defect` (category 2) rather than `Feature Not Working` (category 5).
- **AND** "bold" text display (value displayed in bold instead of normal weight) SHALL match `UI Layout / Visual Defect` (category 2) as a text rendering defect.
- **AND** "filter is not reset" patterns SHALL match `Feature Not Working / Missing` (category 5) rather than `Other / Unclassified`.
- **AND** `rca_component` weight in the composite severity score SHALL use confidence 0.7 for category 1, 0.6 for categories 2–5, 0.5 for category 6, 0.4 for category 7, 0.0 for the unclassified sentinel.
- **AND** each category SHALL carry prevention_actions appropriate to its class (crash guards, layout tests, data validation, font/accessibility tests, feature flag tests, vendor escalation, performance profiling).

#### Scenario: RCA category carries a 4P lens label (RCA-8)
- **WHEN** the system infers the primary root cause category
- **THEN** it SHALL attach a 4P lens tag from the Xurrent 4P root cause framework — exactly one of `People | Procedures | Policies | Plant` — to every taxonomy category
- **AND** `bundle.root_cause.four_p_lens` SHALL carry that tag
- **AND** the unclassified sentinel SHALL have `four_p_lens = null` (no lens)
- **AND** the lens mapping SHALL be:
  - Crash / ANR / Force Close → Plant
  - UI Layout / Visual Defect → Plant
  - Wrong Data / Incorrect Value → Plant
  - Text / Font Display → Plant
  - Feature Not Working / Missing → Procedures
  - 3rd Party Issue (WebView, API, SDK) → Policies
  - Performance / Slow Loading → Plant
- **AND** the lens SHALL render in the Classification tab's `RCA 4P Lens` column (position 26).

#### Scenario: Multi-cause surfacing via secondary_categories (RCA-8)
- **WHEN** the ticket content matches N distinct RCA taxonomy categories beyond the primary
- **THEN** `bundle.root_cause.secondary_categories` SHALL list those additional categories
- **AND** the list SHALL be sorted by priority ascending (lowest priority number = most severe first)
- **AND** the list SHALL be deduplicated
- **AND** the list SHALL be capped at 3 entries to keep sheet cells readable
- **AND** the list SHALL be empty for single-cause tickets and for the unclassified sentinel
- **AND** the joined string (`" | "` separator) SHALL render in the Classification tab's `Secondary RCA` column (position 27)
- **AND** this addresses the Xurrent 4P antipattern of "stopping at the first cause" — analysts see all contributing causes, not just the winner-takes-all primary.

#### Scenario: Composite severity score is a deterministic weighted sum
- **WHEN** the system computes the composite severity score for ordering and ranking
- **THEN** it SHALL compute a deterministic 0.0–1.0 score using:
  - `risk_component × 0.40` — from CompletenessSignal missing-fields weight: `min(sum(weights) / 15, 1.0)`, where MISSING_INFO=2, UNASSIGNED=3/5, BLOCKED_TASK=5, CODE_INCOMPLETE_FIX=4, NO_SPRINT_ALLOCATION=3.
  - `blocking_component × 0.20` — from DependencySignal: `blocked_by_keys` (+0.2), impact radius (+0.15 each, cap 0.4), chain depth (+0.1 each, cap 0.25), circular (+0.15), capped at 1.0.
  - `code_component × 0.20` — from `_code_evidence_score()`: base 0.2 for any worktree/branch hint, +0.15 for `"commits mention"`, +0.1 for `"branch "`, +0.35 for security/payment keywords, +0.2 for TODO/FIXME, cap 1.0.
  - `completeness_component × 0.10` — `min(len(missing_fields) / 7, 1.0)`, tracking: assignee, description, story_points, due_date, labels, priority, epic_link.
  - `rca_component × 0.05` — RootCauseSignal.confidence: 0.7 for priority 1 (Crash), 0.6 for priorities 2–5 (UI Layout, Wrong Data, Text/Font, Feature Not Working), 0.5 for priority 6 (3rd Party), 0.4 for priority 7 (Performance), 0.0 for the unclassified sentinel.
  - `fix_status_rank × 0.05` — VERIFIED=1.0, FIXED=0.85, IN_REVIEW=0.65, IN_PROGRESS=0.45, UNKNOWN=0.2, UNFIXED=0.0.
- **AND** severity rank labels SHALL use these calibrated thresholds (2026-06-22): P0 ≥ 0.75, P1 ≥ 0.55, P2 ≥ 0.30, P3 < 0.30.
- **NOTE:** The formula reserves 0.4 + 0.2 = 0.6 for blocking signals. For bug-triage filters without issuelinks (typical), the achievable range without blocking is 0.0–0.58. P0 requires blocking signals; most bugs score P1.


### Requirement: Capture feedback on analysis usefulness
The system SHALL allow consumers to record feedback on whether a recommendation was useful, accepted, dismissed, or overridden.

#### Scenario: Recommendation is accepted
- **WHEN** a consumer accepts a recommendation
- **THEN** the system SHALL be able to record that outcome for later analysis and tuning

#### Scenario: Recommendation is dismissed
- **WHEN** a consumer dismisses a recommendation
- **THEN** the system SHALL record that outcome without changing the original analysis evidence

### Requirement: Surface dependency and relationship signals
The system SHALL detect and normalize Jira dependency relationships such as blocked-by, blocks, related, and duplicate-style links when those relationships are available.

#### Scenario: Blocked work is detected
- **WHEN** an issue participates in a blocking relationship
- **THEN** the bundle SHALL surface that dependency as a first-class signal for triage and prioritization

#### Scenario: Related work is detected
- **WHEN** an issue is linked to another issue in a non-blocking relationship
- **THEN** the bundle SHALL include the relationship so downstream consumers can cluster or navigate related work

### Requirement: Use shared Jira authentication and API v3 data access
The system SHALL obtain Jira data through the shared `tdt_core.clients` Jira factory and SHALL use Jira Cloud API v3-compatible access paths for issue, changelog, worklog, and link data.

#### Scenario: Credentials are available
- **WHEN** `~/.tdt/.env` provides Jira credentials
- **THEN** the analysis layer SHALL load Jira access through `JiraClientFactory.from_env()` rather than raw SDK construction

#### Scenario: Credentials are missing
- **WHEN** Jira credentials are absent or invalid
- **THEN** the analysis layer SHALL fail fast with an actionable configuration error

#### Scenario: Worklog data is needed
- **WHEN** a signal requires worklog data
- **THEN** the analysis layer SHALL fetch issue worklogs through the Jira API path that supports pagination and partial-data detection

#### Scenario: Changelog data is needed
- **WHEN** a signal requires change history
- **THEN** the analysis layer SHALL fetch issue changelog data through the Jira API v3-compatible path

### Requirement: Handle partial Jira data gracefully
The system SHALL continue producing the analysis bundle when Jira returns partial data, and SHALL mark unavailable fields explicitly rather than failing the entire analysis.

#### Scenario: Worklogs are paginated or partial
- **WHEN** Jira returns partial worklog data for an issue
- **THEN** the bundle SHALL still be produced and SHALL indicate any unavailable or incomplete fields

#### Scenario: A single issue is malformed
- **WHEN** one issue in a batch has malformed links or missing fields
- **THEN** the system SHALL continue analyzing the rest of the snapshot and SHALL record the issue-level problem in the bundle

#### Scenario: A field is inaccessible
- **WHEN** Jira redacts a field or the caller lacks permission to read it
- **THEN** the bundle SHALL mark the field as unavailable or redacted instead of silently omitting it

### Requirement: Be reusable across ecosystem consumers
The system SHALL allow at least `jira-epic-report`, `jira-daily-reports`, and `webhook-receiver` to consume the same analysis contract without duplicating the core signal extraction logic.

#### Scenario: Shared analysis runs from snapshot input
- **WHEN** a consumer or test provides a Jira snapshot input to the analysis layer
- **THEN** the system SHALL produce the same canonical bundle without requiring live Jira API access during bundle construction

#### Scenario: A consumer adapts the bundle
- **WHEN** a consumer needs a report, reminder, or webhook decision
- **THEN** it SHALL adapt the shared ticket intelligence bundle instead of re-implementing the same core signals locally

#### Scenario: Consumer behavior stays local
- **WHEN** a consumer renders or acts on the bundle
- **THEN** presentation, prioritization thresholds, escalation ladders, and actioning logic SHALL remain in that consumer while the analysis contract stays shared
