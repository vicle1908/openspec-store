# rca-detection-fix Specification

## ADDED Requirements

### Requirement: MR reference detection returns FIXED for merged MRs and IN_REVIEW for open MRs
The `detect_fix_status()` function SHALL determine fix status from MR references using explicit state keyword matching, not substring containment checks.

#### Scenario: MR reference containing "merged" keyword returns FIXED
- **WHEN** `detect_fix_status()` receives `mr_references=["MR !123 merged into develop"]`
- **THEN** it SHALL return `FixStatus.FIXED` with `evidence_sources` containing `"mr_reference"`
- **AND** `mr_reference` SHALL be `"MR !123 merged into develop"`

#### Scenario: MR reference containing "canceled" or "closed" returns UNFIXED
- **WHEN** `detect_fix_status()` receives `mr_references=["MR !456 closed without merging"]`
- **THEN** it SHALL return `FixStatus.UNFIXED` with `evidence_sources` containing `"mr_reference"`

#### Scenario: MR reference containing "opened" returns IN_REVIEW
- **WHEN** `detect_fix_status()` receives `mr_references=["MR !789 opened for review"]`
- **THEN** it SHALL return `FixStatus.IN_REVIEW` with `evidence_sources` containing `"mr_reference"`

#### Scenario: MR reference with URL containing merged MR returns FIXED
- **WHEN** `detect_fix_status()` receives `mr_references=["https://gitlab.example.com/mr/42"]` where that MR is merged
- **THEN** it SHALL return `FixStatus.FIXED` (URL matched by existing `https?://.*merge_requests/\d+` pattern)

#### Scenario: MR reference keyword matching uses explicit state keywords
- **WHEN** `detect_fix_status()` receives `mr_references=["MR !123 under review"]`
- **THEN** it SHALL NOT use substring `"review" in ref` to decide fix status
- **AND** it SHALL check for explicit `merged`/`canceled`/`closed`/`opened` keywords

### Requirement: MR reference parameter is preserved through all return paths in detect_fix_status
The `mr_references` function parameter SHALL be captured into a local variable before any early-return block, and that local value SHALL be used in every `FixStatusSignal` return.

#### Scenario: MR reference preserved when QA comment keyword matches first
- **WHEN** `detect_fix_status()` is called with `comments=["QA verified: fixed"]` and `mr_references=["MR !42 merged"]`
- **THEN** the returned `FixStatusSignal` SHALL have `mr_reference="MR !42 merged"`, not `None`

#### Scenario: MR reference preserved when SCM evidence is present
- **WHEN** `detect_fix_status()` is called with `scm_evidence=IssueScmEvidence(...)` (with `merged` state) and `mr_references=["MR !99"]`
- **THEN** the returned `FixStatusSignal` SHALL have `mr_reference` set from the SCM evidence URL or branch name, not `None`

### Requirement: detect_fix_status uses canonical status_mapping as the authoritative Jira-status resolver
The `detect_fix_status()` function SHALL use the canonical `status_mapping` dictionary as the primary and only authoritative path for mapping Jira status strings to `FixStatus` values.

#### Scenario: Standard Done/Resolved/Closed statuses resolve to FIXED
- **WHEN** `jira_status` is `"Done"`, `"Resolved"`, or `"Closed"` (case-insensitive)
- **THEN** the function SHALL return `FixStatus.FIXED`

#### Scenario: In-progress statuses resolve correctly
- **WHEN** `jira_status` is `"In Progress"` or `"SIT"`
- **THEN** the function SHALL return `FixStatus.IN_PROGRESS`
- **WHEN** `jira_status` is `"In Review"` or `"In Test"`
- **THEN** the function SHALL return `FixStatus.IN_REVIEW`

#### Scenario: Open/unknown statuses return None
- **WHEN** `jira_status` is `"Open"`, `"To Do"`, or `"Backlog"` and no other evidence is present
- **THEN** the function SHALL return `None`

#### Scenario: Custom Jira status names do not trigger keyword-based fix status
- **WHEN** `jira_status` is a custom status like `"Fixed Scope"` or `"Done (Verified)"`
- **THEN** the function SHALL NOT match keyword patterns from `FIX_KEYWORDS` against the raw Jira status string
- **AND** if no `status_mapping` key matches, the function SHALL fall through to the next evidence block or return `None`

#### Scenario: Status keyword matching against Jira status is removed
- **WHEN** the Jira status block in `detect_fix_status()` is reached
- **THEN** it SHALL use only `status_mapping` for resolution, not `FIX_KEYWORDS` keyword iteration

### Requirement: Fix status signal selection ranks UNKNOWN above UNFIXED
The `_select_primary_fix_status_signal()` function SHALL rank `UNKNOWN` status above `UNFIXED` when selecting the primary fix status signal.

#### Scenario: UNKNOWN and UNFIXED coexist, UNKNOWN selected
- **WHEN** signals with statuses `[UNKNOWN, UNFIXED]` are passed to `_select_primary_fix_status_signal()`
- **THEN** it SHALL return the `UNKNOWN` signal

### Requirement: analyzer.py uses valid Python 3 exception syntax
The `analyzer.py` module SHALL use parenthesized tuple syntax for `except` clauses.

#### Scenario: analyzer imports without SyntaxError in Python 3.14
- **WHEN** `jira_skill.analysis.analyzer` is imported
- **THEN** no `SyntaxError` SHALL be raised

### Requirement: MergeRequestState includes CANCELED state
The `MergeRequestState` enum SHALL include a `CANCELED` value to handle GitLab MRs closed without merging.

#### Scenario: CANCELED MR state resolves without error
- **WHEN** GitLab returns `"state": "canceled"` for a merge request
- **THEN** `MergeRequestState("canceled")` SHALL return `MergeRequestState.CANCELED`

#### Scenario: detect_fix_status handles CANCELED MR state as UNFIXED
- **WHEN** `scm_evidence.strongest_item()` returns an item with `merge_request_state=CANCELED`
- **THEN** `detect_fix_status()` SHALL return `FixStatus.UNFIXED`

### Requirement: IssueSummary.fix_status is a string and TicketIntelligenceBundle.fix_status is a FixStatusSignal
The `fix_status` field SHALL maintain its current type in each model. `IssueSummary.fix_status` SHALL serialize to a `str | None` (the `.value` of the status enum). `TicketIntelligenceBundle.fix_status` SHALL be `FixStatusSignal | None`.

#### Scenario: Bundle-level fix_status preserves full signal
- **WHEN** a `TicketIntelligenceBundle` is serialized to JSON
- **THEN** `fix_status` SHALL be an object with fields `status`, `evidence_sources`, `worktree_commits`, `qa_comment`, `mr_reference`, `jira_status`

#### Scenario: IssueSummary fix_status is a string value
- **WHEN** an `IssueSummary` is serialized
- **THEN** `fix_status` SHALL be a string like `"fixed"`, `"in_review"`, or `null`

### Requirement: Fix status evidence priority: SCM > QA comments > MR references > Jira status > worktree
The evidence sources in `detect_fix_status()` SHALL have an explicit, documented priority order. Stronger evidence (structured SCM state) overrides weaker evidence (Jira status string).

The priority chain (strongest to weakest):
1. **SCM GitLab** — structured MR state from GitLab API (highest confidence)
2. **QA comments** — human-verified free-text status claims
3. **MR references** — text strings referencing MRs/PRs (medium-weak; can be imprecise)
4. **Jira status** — canonical status_mapping resolution (authoritative but can be stale)
5. **Worktree commits** — presence of git commits (weakest; means IN_PROGRESS)

#### Scenario: SCM merged evidence overrides QA comment indicating IN_REVIEW
- **WHEN** `scm_evidence` has `MERGED` state AND `comments` contain `"under review"`
- **THEN** the function SHALL return `FixStatus.FIXED` (SCM truth wins over QA comment)

#### Scenario: QA comment overrides Jira status
- **WHEN** `comments` contain `"verified fixed"` AND `jira_status="In Progress"`
- **THEN** the function SHALL return `FixStatus.VERIFIED` (QA comment wins over stale Jira status)

#### Scenario: Worktree commits are the weakest evidence source
- **WHEN** only `worktree_commits` (with no SCM evidence, no comments, no MR references) is available
- **THEN** the function SHALL return `FixStatus.IN_PROGRESS`

### Requirement: strongest_item prefers MR state over raw confidence
The `strongest_item()` method in `IssueScmEvidence` SHALL use MR state as a primary sort criterion, not just confidence.

#### Scenario: MERGED MR with lower confidence beats UNKNOWN MR with higher confidence
- **WHEN** `items` contains `[{confidence: 0.9, state: UNKNOWN}, {confidence: 0.6, state: MERGED}]`
- **THEN** `strongest_item()` SHALL return the `MERGED` item

#### Scenario: OPENED MR with lower confidence beats UNKNOWN MR with higher confidence
- **WHEN** `items` contains `[{confidence: 0.9, state: UNKNOWN}, {confidence: 0.7, state: OPENED}]`
- **THEN** `strongest_item()` SHALL return the `OPENED` item

### Requirement: detect_fix_status returns UNFIXED for CLOSED, CANCELED, and LOCKED MR states (non-merged terminal states)
The `detect_fix_status()` function SHALL handle `MergeRequestState.CLOSED`, `MergeRequestState.CANCELED`, and `MergeRequestState.LOCKED` as `UNFIXED`. These are GitLab terminal non-merged states.

#### Scenario: Closed MR without merge returns UNFIXED
- **WHEN** `strongest_item().merge_request_state == MergeRequestState.CLOSED`
- **THEN** `detect_fix_status()` SHALL return `FixStatus.UNFIXED`

#### Scenario: Canceled MR returns UNFIXED
- **WHEN** `strongest_item().merge_request_state == MergeRequestState.CANCELED`
- **THEN** `detect_fix_status()` SHALL return `FixStatus.UNFIXED`

#### Scenario: Locked MR returns UNFIXED
- **WHEN** `strongest_item().merge_request_state == MergeRequestState.LOCKED`
- **THEN** `detect_fix_status()` SHALL return `FixStatus.UNFIXED`
