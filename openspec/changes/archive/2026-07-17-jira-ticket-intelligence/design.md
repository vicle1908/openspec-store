## Context

The current ecosystem already has rich Jira intelligence, but it is spread across separate repos and optimized for different surfaces. The shared capability should make those signals reusable without forcing a redesign of the existing products.

**Normative note:** the shipped v1 canonical contract now lives in `tdt-meta/openspec/specs/ticket-intelligence-core/spec.md`. This design document remains valuable as migration/design history plus extension planning, but it should not be treated as the primary source of truth for already-shipped v1 requirements.

### Current state by repository

#### `jira-epic-report`
- RiskAnalyzer: weighted, severity-scored risk factors
- BlockingAnalyzer: BFS impact radius, DFS chain depth, circular dependencies
- ResourceAnalyzer + SprintAnalyzer: overload, allocation, capacity, cross-project risk
- TimelineAnalyzer + ProgressTracker + StatusAggregator: completion, velocity, progress snapshots
- InsightAnalyzer: comment categorization, changelog pattern extraction, linked work, risk flags
- EscalationDetector: stale-item escalation and blocker-chain recommendations
- AgentAnalyzer: optional AI deep analysis and multi-agent synthesis

#### `jira-daily-reports`
- Standup/blocked/missing-info/velocity/platform/priority/sprint-health/code-review/WIP/WIP-age/cycle-time report surfaces
- Sprint-sheet synthesis with direct-link expansion and person-capacity output
- Freshness persistence (run id + source + timestamp) and pair-level freshness checks
- Reminder policies, escalation ladders, suppression, role resolution, and audit logging

#### `webhook-receiver`
- Transition guard and policy enforcement
- Freshness dispatch with debounce and in-flight protection
- Health exposure for guard and freshness state
- Relevance predicate for Jira changes that can affect refresh behavior

#### `jira-skill`
- JQL, issue, board, sprint, link, comment, and GitLab primitives
- Existing natural home for shared Jira-domain analysis primitives

### Design intent

The spec should capture three layers:

1. **Normalized existing signals** — what already exists in one repo and must become reusable.
2. **New shared capabilities** — explainable triage, multi-level summaries, local policy overlays, feedback capture, access-aware redaction.
3. **Consumer adapters** — thin integrations in each repo that initially preserved behavior during migration and now serve as canonical-only consumers of the shared bundle.

## Goals / Non-Goals

**Goals:**

- Make existing Jira intelligence reusable across the ecosystem.
- Keep signal extraction deterministic and testable.
- Complete consumer cutover onto the shared bundle path.
- Add explainable triage and shared summaries that no repo currently provides in a canonical way.
- Keep `tdt-core` infra-only and keep execution boundaries intact.

**Non-Goals:**

- Replace every analyzer immediately.
- Move webhook ingress, scheduling, or auth responsibilities into the analysis core.
- Build a new external service/database.
- Make AI mandatory for the baseline bundle.

## Decisions

### 1. Shared core lives in `jira-skill`
- Rationale: this is Jira-domain logic, not infra.
- Alternative rejected: `tdt-core` (too low-level).

### 2. Bundle-first contract
- Rationale: one versioned bundle can drive CLI reports, dashboards, reminders, and webhooks.
- The bundle should contain:
  - `meta` (version, source repo, timestamp, snapshot id)
  - `issue` or `scope` identity
  - `signals` (risk, blocking, freshness, capacity, completeness, insight, dependency)
  - `recommendations` (action, reason, evidence)
  - `summary` (human-readable issue-level narrative)
  - `policy` (consumer-local guidance metadata)
  - `access` (redacted/unavailable markers)
- Project and queue summaries should be derived by consumer adapters in v1, not canonical bundle fields.
- Alternative rejected: many per-repo dict shapes.

### 3. Normalize, then enrich
- Rationale: current signals already exist, so the migration should start by mapping them.
- Enrichment is optional and layered; it should not replace deterministic signals.
- The shared core should be library-first and operate on snapshot input models so analysis can be replayed in tests and fixtures without live Jira access.
- Alternative rejected: agent-first generation.

### 4. Keep consumer policy local
- Rationale: epic dashboards, daily reports, and webhook guards have different operating thresholds.
- The shared core should not hard-code consumer thresholds.

### 5. Contract tests are mandatory
- Rationale: the biggest risk is silent drift between shared bundle and old repo outputs.
- Tests should compare the same Jira snapshot across:
  - current repo-local output
  - shared bundle output
  - consumer adapter output
- Shared fixtures should be captured as snapshot inputs plus expected bundle output so deterministic analysis can be tested independently from live Jira reads.

### 6. Use API v3-compatible Jira reads and preserve access boundaries
- Rationale: the shared layer will fetch issue, changelog, worklog, and issue-link data.
- It must surface unavailable/redacted state rather than assuming full visibility.

## Risks / Trade-offs

- [Risk] Normalization may flatten nuanced repo-local heuristics → Mitigation: preserve evidence, scores, and extension fields.
- [Risk] Contract drift between bundle and consumer adapters → Mitigation: snapshot-based contract tests.
- [Risk] Partial Jira data may produce incomplete bundles → Mitigation: explicit unavailable/redacted markers.
- [Risk] AI enrichment could tempt consumers to bypass deterministic signals → Mitigation: keep AI in an optional enrichment namespace.
- [Risk] Rollout complexity across 3 repos → Mitigation: phase the adapters one repo at a time.

## Migration Plan

Historical migration summary for the shipped v1 contract:

1. Add `jira_skill.analysis` and define the canonical bundle model.
2. Map the existing analyzers into the bundle taxonomy.
3. Add consumer adapters in `jira-epic-report`, `jira-daily-reports`, and `webhook-receiver`.
4. Create shared fixtures from representative Jira snapshots.
5. Add contract tests that compare old and new output.
6. Cut over each consumer to the canonical shared path.
7. Remove rollout-era flags, stub bundles, and legacy adapter-only fallback behavior.
8. Complete shared freshness/capacity semantics needed by `jira-daily-reports` so that its adapter can safely collapse to the same thin-wrapper canonical pattern as `jira-epic-report`.

Post-cutover target state:
- consumer repos require `jira-skill`
- adapters expose canonical-only behavior
- rollback relies on code changes/reverts rather than runtime flags
- `jira-daily-reports` no longer reconstructs shared semantics locally

## Open Questions

None remaining. All questions resolved in the sections below.

## Resolved design decisions for development readiness

### Bundle contract structure (ADDED 2026-06-04, UPDATED 2026-06-05)
The top-level bundle model SHALL be defined in `jira_skill.analysis.bundle` as:

```python
class TicketIntelligenceBundle(BaseModel):
    """Canonical ticket intelligence bundle for cross-repo consumption."""

    meta: BundleMeta
    scope: BundleScopeSummary
    issue_identities: list[BundleIssueIdentity]
    risk: RiskSignal | None
    blocking: BlockingSignal | None
    freshness: FreshnessSignal | None
    completeness: CompletenessSignal | None
    capacity: CapacitySignal | None
    churn_insight: InsightSignal | None
    dependency: DependencySignal | None
    recommendations: list[Recommendation]
    summary: BundleSummary
    policy: BundlePolicy
    access: ScopeAccessReport
    enrichment: EnrichmentData | None = None
```

Rationale: the implemented contract is scope-based and promotes one canonical signal per family at the top level, while preserving issue-level detail through `issue_identities` and `summary.issue_summaries`.

### Evidence requirements (ADDED 2026-06-04)
Evidence for explainable recommendations MUST include:
- Signal type + value (e.g., `risk.severity = "high"`)
- Source field(s) (e.g., `issue.fields.priority`, `changelog[0]`)
- Threshold crossed (e.g., `stale_days = 5 > threshold = 3`)

Optional but recommended:
- Link to Jira issue/comment
- Timestamp of source data

### Multi-level summary strategy (ADDED 2026-06-04, UPDATED 2026-06-06)
- **Issue-level**: Canonical in bundle (single issue narrative)
- **Project/epic-level**: Consumer-composed derived views in v1
- **Queue-level**: Consumer-composed derived views in v1

Aggregation remains intentionally deferred from the canonical shared package in v1.
Consumer adapters MAY derive project/epic/queue summaries from `scope`, `issue_identities`,
and `summary.issue_summaries`, but `jira_skill.analysis.aggregation` is not part of the
implemented contract.

Rationale: the shipped contract is scope-based and deterministic. Consumer-composed
aggregation avoids freezing presentation-specific rollups into the canonical bundle before
multiple consumers converge on a stable shared abstraction.

### Adapter pattern (ADDED 2026-06-04, UPDATED POST-CUTOVER)
Consumer adapters SHALL follow this structure whenever the shared analyzer fully models the needed semantics:

```python
from jira_skill.analysis import SnapshotScope, TicketIntelligenceBundle
from jira_skill.analysis.analyzer import analyze_snapshot

class EpicReportAdapter:
    def __init__(self, epic_key: str = ""):
        self.epic_key = epic_key

    def to_bundle(self, snapshot: SnapshotScope) -> TicketIntelligenceBundle:
        return analyze_snapshot(snapshot, source="jira-epic-report")
```

Current exception / clarification:
- `jira-daily-reports` freshness/capacity semantics have already been promoted into `jira-skill`, so its adapter can stay thin.
- `jira-epic-report` is thin for all implemented shared surfaces including risk normalization.
- Canonical shared `RiskSignal` extraction has been implemented in `jira-skill.analysis.analyzer` with fixture-backed verification and normative heuristic mapping from the legacy `RiskAnalyzer`.

Rationale: the intended end state is thin canonical adapters. Both freshness/capacity and risk normalization are now shipped.

### Fixture coverage matrix (ADDED 2026-06-04)
Shared fixtures SHALL cover these scenarios (minimum 8 snapshots).

**Verified analyzer output (2026-06-07).** The values below are the *actual*
`analyze_snapshot()` outputs, confirmed by the contract suite. They supersede the
earlier aspirational matrix, which never matched reality: a verification pass found
the 8 fixtures had been authored in a legacy schema (`assignee_display_name`,
`project`, `inward_issue_key`/`outward_issue_key`) that the canonical
`SnapshotIssue`/`SnapshotIssueLink` models silently dropped. Every fixture therefore
collapsed to one identical degenerate bundle, and the contract tests — whose expected
bundles were regenerated from that degenerate output — were tautological. The fixtures
were converted to the canonical schema, the collector link-direction bug and the dead
circular-detection code were fixed, and non-tautological matrix assertions were added.

| Fixture ID | Risk | Blocking | Freshness | Capacity | Completeness | Notes |
|------------|------|----------|-----------|----------|--------------|-------|
| happy-path | LOW | none | FRESH | n/a | PARTIAL | Baseline; no blockers |
| critical-risk | CRITICAL | DIRECT | n/a | n/a | SPARSE | Many risk factors near cut-off |
| circular-deps | MEDIUM | CIRCULAR | n/a | n/a | PARTIAL | Real 3-issue blocking loop |
| stale-blocked | MEDIUM | DIRECT | STALE | n/a | PARTIAL | Stale + blocked |
| overloaded-assignee | MEDIUM | none | n/a | OVERLOADED | PARTIAL | WIP over threshold |
| missing-metadata | MEDIUM | none | n/a | n/a | SPARSE | Missing assignee/description/points |
| epic-rollup | LOW | none | n/a | n/a | PARTIAL | 11 child issues |
| cross-project-blocker | MEDIUM | DIRECT | n/a | n/a | PARTIAL | Blocker in a different project |

`n/a` means the signal is intentionally absent (`None`) for that fixture. Freshness and
capacity are pass-through signals: they are only populated when the snapshot carries the
corresponding `raw_fields` hints (`freshness_state`/`stale_days`, `wip_count`/`capacity_state`),
so fixtures that do not encode those hints produce no freshness/capacity signal.

Fixtures SHALL be stored in `jira-skill/tests/fixtures/snapshots/` as JSON files with paired expected bundle outputs.

### Legacy risk heuristics preserved in the shipped shared contract (ADDED 2026-06-05, UPDATED 2026-06-06)
Canonical `RiskSignal` extraction is implemented in `jira-skill.analysis.analyzer`. Its acceptance contract is derived from `jira-epic-report/epic_report/analyzers/risk.py` and preserves these v1 heuristics:

- `UNASSIGNED_TASK` / `UNASSIGNED_NEAR_DEADLINE`
  - Trigger when work is unassigned.
  - Elevate severity when close to cut-off (`risk_cutoff_buffer`, default 7 days).
- `PLANNING_INCOMPLETE`
  - Trigger when an epic is `In Progress` while child tasks remain in `Draft`.
- `TIMELINE_AT_RISK`
  - Trigger from completion percentage + days to cut-off.
- `MISSING_INFO`
  - Trigger when description / design / requirement links are missing on the epic-level source model.
- `BLOCKED_TASK`
  - Trigger when a task has blockers.
- `RESOURCE_OVERLOAD`
  - Trigger when active work for one assignee exceeds threshold.
- `NO_SPRINT_ALLOCATION`
  - Trigger when work is not assigned to any sprint.
- `CROSS_PROJECT_CONFLICT`
  - Trigger when one assignee is spread across multiple projects.

For the canonical shared bundle in `jira-skill`, parity does NOT require reproducing the old `Risk` object list 1:1. Instead, v1 shared parity SHALL mean:
- top-level `bundle.risk` exists when one or more legacy risk heuristics would have fired,
- `bundle.risk.severity` matches the aggregate severity band implied by the weighted legacy score,
- `bundle.risk.factors` preserves the normalized triggered heuristic names,
- `bundle.risk.evidence` points to the concrete snapshot fields or linked issues that caused those factors.

Recommended score mapping for shared v1 implementation:
- Use a normalized 0.0-1.0 composite score derived from the triggered weighted factors.
- Preserve legacy severity thresholds semantically: `critical` for highest weighted aggregate, then `high`, `medium`, `low`.
- Keep consumer-local PM policy, escalation phrasing, and presentation-specific recommendation text outside the shared risk signal.

### Rollout history and current parity definition (ADDED 2026-06-04, UPDATED 2026-06-06)
"Parity" means:
- For deterministic implemented signals (blocking, freshness, capacity): exact numerical or categorical match within documented tolerance.
- For shared risk parity: severity-band and triggered-factor parity against the legacy `RiskAnalyzer`, not a byte-for-byte reproduction of legacy presentation objects.
- For recommendations: same action type, similar evidence.
- For summaries: semantic equivalence (not line-by-line).

The staged rollout is complete for the shipped v1 canonical bundle path:
1. `jira-epic-report` uses a thin canonical adapter over `analyze_snapshot()`.
2. `jira-daily-reports` emits canonical shared bundle models and keeps consumer-local policy outside the contract.
3. `webhook-receiver` emits canonical freshness/triage bundle structures and keeps ingress/dispatch policy local.

Historical rollout sequencing and rollback flags are retained only as migration history and are no longer normative for current implementations.

### AI enrichment namespace (ADDED 2026-06-04)
Optional AI enrichment SHALL be isolated in `bundle.enrichment`:

```python
class EnrichmentData(BaseModel):
    """Optional AI/agent-generated insights."""
    
    agent_summary: str | None  # Deep analysis narrative
    sentiment_score: float | None  # Comment sentiment
    complexity_estimate: str | None  # AI-estimated complexity
    similar_issues: list[str]  # ML-based similarity
    
    # Metadata
    enrichment_source: str  # "codex", "claude", "kimi", "pi"
    enrichment_timestamp: datetime
    enrichment_version: str
```

Consumers SHALL NOT depend on enrichment fields for deterministic behavior. Enrichment MAY be disabled globally via config.

## Resolved design decisions for development readiness

### Bundle model strategy
- The shared bundle SHALL use Pydantic models as the canonical external contract in `jira_skill.analysis`.
- Rationale: `jira-epic-report` already uses Pydantic heavily for its primary report and work-item models, while `jira-daily-reports` reminder policies also use Pydantic. Choosing Pydantic for the bundle minimizes adapter friction for the richest first consumer and gives versioned serialization, validation, and schema clarity at repo boundaries.
- Constraint: internal helper structures MAY still use dataclasses where convenient, but any cross-repo bundle, snapshot input, signal payload, recommendation payload, or redaction marker SHALL be expressed as Pydantic models.

### Reminder readiness scope
- Reminder-readiness SHALL remain a `jira-daily-reports` extension in v1, not a canonical shared signal.
- Rationale: current reminder behavior depends on project-local policy YAML, escalation ladders, suppression state, and transition-specific handling that are operational rather than domain-universal.

### Freshness scope
- The canonical bundle SHALL include portable freshness facts only: source, run id, refreshed timestamp, and availability markers.
- Debounce windows, in-flight state, scheduler integration, and dispatch mechanics SHALL remain consumer-local.

### Webhook receiver coupling strategy
- `webhook-receiver` MAY continue importing reminder policy primitives from `jira-daily-reports` during the migration.
- The first development milestone is bundle parity, not immediate dependency untangling. Direct coupling should be reduced only after shared bundle-driven behavior is proven equivalent.

- `jira-epic-report`'s `AgentAnalyzer` is confirmed to be optional AI CLI enrichment (`codex`/`claude`/`kimi`/`pi`) and should remain outside the deterministic baseline bundle.
- `jira-skill` currently mixes dataclass-heavy domain models with some Pydantic config models. The bundle contract must pick an explicit boundary strategy instead of inheriting this ambiguity implicitly.
- `webhook-receiver` currently imports reminder policy/escalation primitives directly from `jira-daily-reports`, which increases the value of extracting a reusable shared analysis layer into `jira-skill`.
- Stale-item semantics are not identical today: `jira-epic-report` escalates items stale for more than 60 days, while `jira-daily-reports` has separate 3-day blocked reporting, 3/7-day WIP-age flags, and reminder escalation ladders. These thresholds should stay consumer-local in v1.

---

## Section 5: RCA + Prevention + Reusable Pipeline (ADDED 2026-06-06)

### Design decisions for RCA signal extraction

#### 1. RCA patterns are priority-ordered (not dictionary)
Priority ensures the most specific/critical patterns match first:
1. Crash / freeze / ANR (most specific, first priority)
2. Wrong financial data submitted
3. API error response missing field → silent handler exit
4. BottomSheet keyboard obscures input (adjustPan missing)
5. BottomSheet dismiss blocked
6. PMP/Greeks price updates but color doesn't change
7. Negative number input blocked
... descending to generic UI/UX polish (catch-all, lowest priority)

This prevents over-matching (e.g., "Platform parity" was matching 96.5% before refinement, now ~16%).

#### 2. Prevention map is 1:1 with RCA categories
Each RCA category has exactly 1-3 concrete prevention actions.
Rationale: prevention is attached to the RCA, not per-ticket.

#### 3. FixStatus determined from content + metadata (not Jira status)
Detection order in the current implementation: QA keywords → MR references → Jira status mapping → worktree commit evidence → no signal returned.
This is the implementation-backed baseline; any future "developer keywords" or explicit `NOT_STARTED` semantics should be specified only when added to code.

#### 4. Composite severity score formula and rank thresholds
The composite score is a weighted linear combination implemented in `analyzer._compute_composite_severity_score()`:
```
total = risk_component     * 0.40   # from CompletenessSignal missing-fields weight
      + blocking_component * 0.20   # from DependencySignal: blocked_by, impact_radius, chain_depth, circular
      + code_component     * 0.20   # from _code_evidence_score(): commit presence + "commits mention" + "branch "
      + completeness      * 0.10   # 7 tracked fields (assignee, description, story_points, due_date, labels, priority, epic_link)
      + rca_component     * 0.05   # from RootCauseSignal.confidence: 0.3–0.7 depending on category priority
      + fix_status_rank() * 0.05   # VERIFIED=1.0, FIXED=0.85, IN_REVIEW=0.65, IN_PROGRESS=0.45, UNKNOWN=0.2, UNFIXED=0.0
```
Score is rounded to 4 decimal places, capped at 1.0.

**Severity rank thresholds** (implemented in `_severity_rank_label()`):
- **P0** ≥ 0.75 — Requires blocking signal (blocking_component ≥ ~0.75) AND at least one of: verified fix + SCM evidence + high RCA confidence. In practice, issues with circular/chained blocking links or blocked-by chains.
- **P1** ≥ 0.55 — Achievable without blocking: a critical-risk issue with verified fix + high-RCA confidence + multiple completeness gaps + SCM/worktree evidence reaches ~0.58.
- **P2** ≥ 0.30 — Baseline triage priority for any issue with a risk signal or completeness gap.
- **P3** < 0.30 — Low priority; well-documented, verified-fix, no blocking.

Key calibration facts:
- `blocking_component` is 0 for all 752 mainflow bugs (no issuelinks in the filter JQL).
- Theoretical max without blocking: 0.4 (risk) + 0.2 (code max) + 0.1 (completeness max) + 0.035 (rca) + 0.05 (fix) = 0.785 → P0 achievable only with blocking signals.
- Typical bug (critical risk, missing 5/7 fields, verified fix, RCA confidence 0.7): score ≈ 0.6696 → P1.

The thresholds were rebalanced on 2026-06-22 (D-iteration) to match the achievable formula range.

### Design decisions for reusable pipeline

#### 4. FilterSnapshotCollector produces SnapshotScope
Takes filter ID or JQL, produces `SnapshotScope` with enriched `SnapshotIssue` entries.
Current implementation already exists in the SDK as `jira_skill.analysis.collector.FilterSnapshotCollector`.
It resolves saved-filter JQL, paginates Jira results, enriches issues with comments/worklogs/changelog/links, and optionally attaches worktree commit evidence.

#### 5. Filter registry remains SDK-first
The current implementation surface uses `jira_skill.analysis.filter_registry` and exports `FilterRegistryReader` from the package root.
This registry layer decouples "what filters should run" from CLI or script orchestration.
The naming in specs should follow the implemented module path first, even if a future rename to `registry.py` is still considered.

#### 6. Continuous mode is orchestration, not signal extraction
`--continuous` / `--incremental` behavior belongs to the SDK/CLI orchestration layer around collection and writing.
It must not leak into the deterministic snapshot-to-bundle analysis contract.

#### 7. SheetsWriter exists but is not yet contract-aligned
The implemented writer module is `jira_skill.analysis.sheets_writer.SheetsWriter`.
However, the current code still assumes issue-summary and metadata fields that do not match the canonical analyzer/bundle output shape.
Section 5 execution should therefore treat SheetsWriter as an existing module that still needs contract-alignment work, not as finished integration.

#### 8. CLI and scripts are wrappers over the SDK
Single-command orchestration such as `uv run jira-skill analyze-filter --filter 15269` is desirable, but the migration target is still the importable SDK path:
collector/filter-registry → `analyze_snapshot()` → `SheetsWriter`.
Legacy or convenience scripts should be treated as wrappers over those SDK modules, not as parallel business logic surfaces.

#### 9. Execution-ready acceptance boundary
Section 5 should be considered execution-ready when it is read as:
- extractor reuse and script-to-SDK alignment are the first implementation slice
- `project.py` is the only clearly missing extractor module called out by current code review
- current analyzer output is respected as-is unless the bundle contract is intentionally expanded
- unimplemented conveniences (embedded issue-summary RCA structures) are excluded from baseline acceptance
