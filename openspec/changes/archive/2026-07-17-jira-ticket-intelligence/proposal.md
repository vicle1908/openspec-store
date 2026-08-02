## Why

Jira analysis logic is already scattered across three repos in incompatible shapes. The same concepts — risk, blocking, churn, completion, freshness, capacity — are computed three times with slightly different heuristics and zero shared contracts. This makes it impossible for one tool to reuse another's analysis, hard to compare outputs across surfaces, and risky to change any signal because the blast radius is implicit.

**Concrete fragmentation found in code:**

| Signal | jira-epic-report | jira-daily-reports | webhook-receiver |
|--------|-----------------|-------------------|-----------------|
| Risk scoring | 9-factor weighted risk with severity levels (analyzers/risk.py) | Not computed | Not computed |
| Blocking | BFS impact radius, DFS chain depth, circular deps (analyzers/blocking.py) | Stale-3-days check (reports/blocked.py) | Not computed |
| Freshness | Not present | Pair-level freshness state + run id (delivery/tdt_sheet.py) | Relevance predicate + debounce (report_freshness.py) |
| Capacity | SprintAllocationAnalyzer, overload detection (analyzers/resource.py, sprint.py) | Person Capacity tab with ownership vs activity (reports/sprint_report_sheet.py) | Not computed |
| Reminders | Not present | Policy YAML, escalation ladder, tagger, suppressor (reminders/) | Real-time transition guard (jira_guard/) |
| Churn/insights | Comment categorization, changelog patterns, risk flags (analyzers/insight.py) | Not present | Not present |
| AI enrichment | AgentAnalyzer spanning codex/claude/kimi/pi (analyzers/agent.py) | Not present | Not present |

Every one of these signals currently lives in one repo. The shared intelligence layer should make them available everywhere without forcing each consumer to re-implement them.

## What Changes

- Define a single canonical ticket-intelligence bundle contract that all ecosystem tools can read.
- Normalize the signals that already exist across repos (risk, blocking, churn, freshness, capacity, completeness, actionability) into one shared shape.
- Add explainable triage suggestions, dependency/relationship signals, and issue-level summaries as new shared capabilities.
- Treat project-level and queue-level summaries as consumer-composed derived views in v1 rather than canonical bundle fields.
- Separate deterministic snapshot-to-bundle analysis from live Jira acquisition so fixtures and contract tests can run without live API access.
- Respect existing Jira access boundaries and allow local consumer policy without mutating source facts.
- Keep the analysis surface deterministic for the baseline path; AI enrichment stays optional.
- Complete consumer cutover onto the shared canonical bundle path while keeping consumer-local rendering and policy outside the shared contract.

## Capabilities

### New Capabilities
- `ticket-intelligence-core`: shared ticket-intelligence analysis bundle contract, signal taxonomy, explainable triage suggestions, dependency/relationship normalization, multi-level summaries, and consumer-local policy guidance.

### Modified Capabilities
- None.

## Normative Spec Location

The shipped, execution-ready canonical contract now lives at:
- `tdt-meta/openspec/specs/ticket-intelligence-core/spec.md`

This change proposal remains the planning and rollout-history surface for the original migration plus the SDK-first RCA/filter/sheets extension work. The permanent spec should be treated as the single source of truth for the shipped v1 contract to avoid drift across scattered spec files.

## Dashboard reuse alignment

- Filter-backed dashboard automation is implemented canonically in `jira_skill.dashboard`.
- Ticket-intelligence runs and dashboard setup should reuse the same resolved filter ID so bundle outputs, Sheets tabs, and dashboard gadgets all represent the same issue scope.
- Dashboard-specific lifecycle rules, validation, and rollback behavior are governed by `tdt-meta/openspec/changes/jira-dashboard-automation/specs/dashboard-automation-core/spec.md`.

## Impact

- `jira-skill`: hosts the new `jira_skill.analysis.*` module tree with bundle models, signal extractors, triage logic, collection/writer helpers, and consumer adapters. The canonical dashboard automation runtime now also lives here under `jira_skill.dashboard`, so downstream repos should reuse its lifecycle operations and bundled layouts instead of maintaining divergent dashboard setup logic.
- `jira-epic-report`: now uses a thin adapter over `analyze_snapshot()` for the shared implemented surfaces while keeping rendering/report composition local.
- `jira-daily-reports`: now emits canonical shared bundle models and keeps reminder/escalation/report-specific policy local.
- `webhook-receiver`: emits canonical freshness/triage bundle structures while retaining ingress ownership and consumer-local guard/freshness dispatch behavior.
- `tdt-core`: unchanged. Auth and transport stay in tdt-core.
- Python SDK flavor: reusable importable modules in `jira_skill.analysis` are the primary migration target; convenience scripts and CLI entrypoints are wrappers over that SDK surface, not a second implementation path.
- Tests: shared fixture set + contract/parity tests prove the same snapshot produces stable bundle outputs across consumers.
