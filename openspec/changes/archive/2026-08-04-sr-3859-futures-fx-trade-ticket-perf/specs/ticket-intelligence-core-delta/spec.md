# Delta Spec: ticket-intelligence-core — Add `performance_live_data_loop` RCA sub-tag

## Change Rationale

SR-3859 (Futures/FX order lag/hot device) is the fourth occurrence of the `MutableLiveData`/`@Published` self-reinforcing observer loop class of performance bug (SR-3323, SR-3223, SR-3319, SR-3859). The existing `ticket-intelligence-core` spec defines `RootCauseCategory.performance` but does not distinguish between sub-classes. Adding a `performance_live_data_loop` sub-tag allows future tickets in this class to be automatically cross-referenced to SR-3859 and surfaced to reviewers at PR time.

## MODIFIED Requirements

### Requirement: Infer RCA, prevention, severity, and fix-state context from ticket evidence plus structured SCM intelligence

The system MUST set `RootCauseBundle.root_cause.sub_tag = "performance_live_data_loop"` whenever the inference logic matches the SR-3859 signal pattern. The matching criteria are in the Scenario below.

The existing requirement is unchanged. The following scenario is **added**:

#### Scenario: `performance_live_data_loop` sub-tag inferred from MutableLiveData / objectWillChange symbol match

- **WHEN** the jira-skill bundle analyzer processes a Jira ticket where:
  - `category == performance` (from keyword signal or explicit label)
  - AND investigation matches `MutableLiveData` (Android) or `objectWillChange` (iOS) in the referenced code path
  - AND the ticket summary or description contains `laggy`, `hang`, `hot device`, `slow`, or `performance`
- **THEN** the resulting `RootCauseBundle.root_cause.sub_tag` SHALL be set to `performance_live_data_loop`
- **AND** the `RootCauseBundle.related_issues` SHALL include a cross-reference to SR-3859
- **AND** the `RootCauseBundle.recommendations` SHALL include the prevention actions from `trade-ticket-pmp-anti-regression` spec

#### Scenario: Symbol match without performance keyword does not trigger sub-tag

- **WHEN** investigation matches `MutableLiveData` but the ticket summary does NOT contain a performance signal
- **THEN** `sub_tag` SHALL remain `None` (the root `performance` category is still applied if other signals exist)
