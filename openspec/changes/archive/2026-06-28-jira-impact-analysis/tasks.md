# Jira Impact Analysis — Tasks

## Phase 0: Foundation (Pre-requisites)

### Task 0.1 — Add `get_mr_diff()` and `get_mr_metadata()` to tdt-core
- [x] 
**Owner**: tdt-core
**Estimated**: 1h
**Target**: `tdt-core/src/tdt_core/clients/gitlab.py`

Add two helper methods to `GitlabClientFactory` (or directly to a module-level helper):

```python
def get_mr_changes(self, project_path: str, mr_iid: int) -> dict[str, Any]:
    """Fetch MR changes via python-gitlab's mr.changes().

    Returns the dict from GET /projects/:id/merge_requests/:iid/changes.
    Keys include: id, iid, sha, merge_commit_sha, squash_commit_sha, merged_at, changes[].
    Each change entry has: old_path, new_path, diff, new_file, renamed_file, deleted_file.
    """
    gl = self.create_client()
    project = gl.projects.get(project_path)
    mr = project.mergerequests.get(mr_iid)
    return mr.changes()  # dict; diffs in response["changes"]
```

Also add:

```python
def get_mr_metadata(self, project_path: str, mr_iid: int) -> dict[str, Any]:
    """Fetch MR state and merge commit SHA. Returns {state, merged_at, merge_commit_sha, sha, squash_commit_sha}."""
    gl = self.create_client()
    project = gl.projects.get(project_path)
    mr = project.mergerequests.get(mr_iid)
    return {
        "state": mr.state,
        "merged_at": mr.merged_at,
        "merge_commit_sha": mr.merge_commit_sha,
        "squash_commit_sha": getattr(mr, "squash_commit_sha", None),
        "sha": mr.sha,
    }
```

**Why this ships first**: both `jira-skill` CLI and `webhook-receiver` need MR diff fetching. The python-gitlab pattern matches what `ai-review/src/ai_review/review_flow/context.py:391-413` and `code-daily-scan/src/code_daily_scan/gitlab_mr.py:113-124` already use. One implementation in tdt-core avoids duplication.

**Verification**:
```bash
cd tdt-core && uv run python -c "
from tdt_core.clients.gitlab import GitlabClientFactory
f = GitlabClientFactory.from_env()
changes = f.get_mr_changes('tdt/pmobile3-ios', 1)
print(len(changes['changes']), 'files changed')
meta = f.get_mr_metadata('tdt/pmobile3-ios', 1)
print('state:', meta['state'], 'sha:', meta['merge_commit_sha'])
"
```

---

### Task 0.2 — Create `feature-map.yaml`
- [x] 
**Owner**: team
**Estimated**: 1–2h
**Target**: `tdt-meta/feature-map.yaml`

Populate from the existing `code-daily-scan` feature taxonomy (11 features). Validate coverage against the actual directory trees:

```bash
# iOS modules
ls ~/Developer/tdt/poems-mobile3-ios/Pmobile3/Modules/
# Android screens
ls ~/Developer/tdt/poems-mobile3-android/app/src/main/java/com/tdt/pmobile3/ui/screens/
# Python packages
ls ~/Developer/tdt/jira-skill/src/jira_skill/
ls ~/Developer/tdt/webhook-receiver/src/webhook_receiver/
```

Verify every major directory has an entry. Leave `unmapped_paths` for discoveries after the tool ships.

**Verification**:
```bash
python -c "
import yaml
with open('tdt-meta/feature-map.yaml') as f:
    data = yaml.safe_load(f)
print(len(data['feature_map']), 'entries')
print('base_modules:', data.get('base_modules', []))
"
```

---

## Phase 1: SDK Core (`jira-skill/impact/`)

### Task 1.1 — Implement `feature_map.py`
- [x] 
**Owner**: jira-skill
**Estimated**: 1–2h
**Target**: `jira-skill/src/jira_skill/impact/feature_map.py`

Implement `class FeatureMap` (SPEC-IA-1.5):
- Loads `tdt-meta/feature-map.yaml` via `get_path_env("TDT_META_PATH", Path.home()/"Developer/tdt/tdt-meta")`
- Singleton pattern: module-level `_instance` with mtime-check reload
- `resolve(path) -> list[str]`: longest-prefix match in document order
- `get_all_features_for_platform(platform) -> list[str]`
- Fallback: if YAML file not found, raise `FileNotFoundError` with a helpful message pointing to Task 0.2

Unit tests: cover longest-prefix, base module propagation, unmapped fallback, platform filter.

**Verification**:
```bash
cd jira-skill && uv run pytest tests/impact/test_feature_map.py -v
```

---

### Task 1.2 — Implement `ticket_mr_resolver.py`
- [x] 
**Owner**: jira-skill
**Estimated**: 2–3h
**Target**: `jira-skill/src/jira_skill/impact/ticket_mr_resolver.py`

Implement (SPEC-IA-2):
- `MR_URL_PATTERNS`: compile regexes aligned with `gitlab/branch_linking.py` patterns
- `extract_mr_urls(comment_body) -> list[MrReference]`
- `fetch_ticket_mrs(ticket_key) -> list[MrReference]`: fetch comments + extract + enrich via `tdt-core`'s `get_mr_metadata()`
- `fetch_mr_diff(project_path, mr_iid)`: delegate to `tdt-core`'s `get_mr_diff()`
- `class MrReference` dataclass (SPEC-IA-2.2)

Integration test: real ticket with known MR references. Use `respx` or `aioresponses` to mock GitLab API responses.

**Verification**:
```bash
cd jira-skill && uv run pytest tests/impact/test_ticket_mr_resolver.py -v
# Manual smoke:
uv run python -c "from jira_skill.impact import fetch_ticket_mrs; print(fetch_ticket_mrs('SR-3588'))"
```

---

### Task 1.3 — Implement `gitnexus_impact.py`
- [x] 
**Owner**: jira-skill
**Estimated**: 2–3h
**Target**: `jira-skill/src/jira_skill/impact/gitnexus_impact.py`

Implement (SPEC-IA-3):
- `def extract_symbols_from_diff(diff: str, filename: str) -> list[str]`: AST + regex fallback. Parses the unified diff from `mr.changes()` entries' `diff` field.
- `def run_gitnexus_impact(symbols: list[str], repo: str, commit_sha: str) -> list[BlastRadiusResult]`: subprocess call via `node .gitnexus/run.cjs impact {symbol} --direction upstream --include-tests -r {repo}`, parses JSON from stdout (always JSON, no flag). Check cache first.
- `def aggregate_blast_radius(results: list[BlastRadiusResult]) -> BlastRadiusResult`: merge `byDepth`, `affected_modules`, `risk` across symbols
- `def check_staleness(symbols: list[str], results: list[BlastRadiusResult]) -> bool`: >20% missing → stale
- Cache layer: `~/.tdt/state/webhook-impacts-cache.sqlite`, key `sha256(repo:commit_sha:sorted_symbols)`, TTL 3600s

**GitNexus JSON parsing rules:**
1. `status` field: `found` / `not_found` / `ambiguous` / `error`
2. `risk` field: `LOW` | `MEDIUM` | `HIGH` | `CRITICAL` | `UNKNOWN`
3. `byDepth` keys are strings (`"1"`, `"2"`)
4. Test files detected from `filePath` matching `test`, `tests`, `_test.`
5. On `not_found` or `error` status: add symbol to `symbols_not_indexed`
6. On `ambiguous`: use `maxImpactedCount` / `maxRisk` from `candidates[]`

**Timeout**: 30 seconds per subprocess call. On timeout, treat as not indexed.

**Verification**:
```bash
cd jira-skill && uv run pytest tests/impact/test_gitnexus_impact.py -v
# Manual smoke (real call):
node ~/.gitnexus/run.cjs impact analyze_snapshot --direction upstream --include-tests -r jira-skill 2>&1 | head -20
```

---

### Task 1.4 — Implement `coverage_analyzer.py`
- [x] 
**Owner**: jira-skill
**Estimated**: 1–2h
**Target**: `jira-skill/src/jira_skill/impact/coverage_analyzer.py`

Implement (SPEC-IA-1, IA-3, IA-4):
- `def analyze_diff(diff: list[dict], repo: str, commit_sha: str, feature_map: FeatureMap) -> CoverageResult`: orchestrates symbol extraction + feature resolution + GitNexus + threshold check
- Threshold check: for each `feature.common` file, compute net line delta; skip GitNexus if > 3 net lines
- `def detect_coverage_gaps(resolved_features, test_files) -> list[str]`
- `class CoverageResult` dataclass: `changed_files`, `resolved_features`, `at_risk_modules`, `test_files`, `coverage_gaps`, `unmapped_paths`, `cache_stats`

Unit tests: coverage gap detection, core/common threshold, empty diff, unmapped files.

**Verification**:
```bash
cd jira-skill && uv run pytest tests/impact/test_coverage_analyzer.py -v
```

---

## Phase 2: Report & CLI

### Task 2.1 — Implement `impact_report.py`
- [x] 
**Owner**: jira-skill
**Estimated**: 2h
**Target**: `jira-skill/src/jira_skill/impact/impact_report.py`

Implement (SPEC-IA-4, IA-8):
- `class ImpactReport` Pydantic model with `ChangedFile`, `TestFile`, `TestType` (SPEC-IA-4)
- `def build_impact_adf(report: ImpactReport, raw_report_path: Path) -> dict`: builds Jira ADF doc using **only** paragraph, text, strong marks — NO tables, headings, or bullet lists (workspace has no patterns for these)
- Helper functions:
  - `_heading_paragraph(text)` — paragraph with bold title
  - `_bold_label_paragraph(label, value)` — paragraph with "Label: value" rendering
  - `_bullet_paragraph(text)` — paragraph starting with "  • " (emulating bullets via indentation)
- `def post_to_jira(report: ImpactReport, ticket_key: str)`: uses `PatchedJira.add_comment_adf()` for new comments; checks existing comments for idempotent update via `edit_comment()`
- `def write_raw_report(report: ImpactReport, state_dir: Path) -> Path`: writes JSON to `~/.tdt/state/webhook-impacts/{mr_iid}-{commit_sha}.json`
- Idempotency: scan existing comments for `Impact Analysis — MR !{mr_iid}`, update if found

**Constraint**: NO table nodes, NO heading nodes, NO bulletList nodes. Only `paragraph`, `text`, `strong` marks. This matches the existing ADF surface in `jira_skill/issue/adf.py`.

**Verification**:
```bash
cd jira-skill && uv run pytest tests/impact/test_impact_report.py -v
# Manual: print the ADF doc
uv run python -c "
from jira_skill.impact.impact_report import build_impact_adf
import json
report = ...  # build a sample ImpactReport
adf = build_impact_adf(report, Path('/tmp/sample.json'))
print(json.dumps(adf, indent=2))
"
```

---

### Task 2.2 — Implement `regression_planner.py`
- [x] 
**Owner**: jira-skill
**Estimated**: 1–2h
**Target**: `jira-skill/src/jira_skill/impact/regression_planner.py`

Implement (SPEC-IA-5):
- `def infer_test_type(feature_tags: list[str]) -> list[TestType]`: feature-bucket lookup
- `def refine_test_type(test_file: TestFile, inferred: list[TestType]) -> list[TestType]`: path-based refinement
- `def rank_test_files(tests: list[TestFile], priority_features: list[str]) -> list[TestFile]`: sort by feature overlap
- `def format_recommendation(report: ImpactReport) -> str`: human-readable summary

Unit tests covering all inference rules and priority ranking.

**Verification**:
```bash
cd jira-skill && uv run pytest tests/impact/test_regression_planner.py -v
```

---

### Task 2.3 — Implement CLI commands
- [x] 
**Owner**: jira-skill
**Estimated**: 2–3h
**Target**: `jira-skill/src/jira_skill/impact/cli.py` + update `jira-skill/src/jira_skill/cli.py`

Implement (SPEC-IA-6):
- Add `impact_app = typer.Typer(name="impact", help="Impact analysis commands")` subapp
- Register: `app.add_typer(impact_app, name="impact")`
- Commands: `impact-ticket`, `impact-mr`, `impact-feature`
- Output: JSON to stdout via `rich.json` or `json.dumps`
- Load env: `load_tdt_env()` at top of each command

**Verification**:
```bash
cd jira-skill
uv run python -m jira_skill impact-ticket SR-3588 2>&1 | head -30
uv run python -m jira_skill impact-feature feature.auth --platform ios --list-tests
```

---

## Phase 3: Webhook Integration

### Task 3.1 — Two-line change in `handle_merge_request`
- [x]
**Owner**: webhook-receiver
**Estimated**: 30 min (vs 2–3h)
**Target**: `webhook-receiver/src/webhook_receiver/api/app.py`

The change is **minimal and surgical**:

```python
# Line 238-243 currently:
if state in ("merged", "closed"):
    logger.info("mr_skipped", mr_iid=mr_iid, state=state, handoff_id=handoff_id)
    return
if action not in ("open", "update", "reopen"):
    logger.info("mr_skipped", mr_iid=mr_iid, action=action, handoff_id=handoff_id)
    return
```

Replace with logic that allows `action == "merge"` through the state guard:

```python
if action != "merge" and state in ("merged", "closed"):
    logger.info("mr_skipped", mr_iid=mr_iid, state=state, handoff_id=handoff_id)
    return
if action not in ("open", "update", "reopen", "merge"):
    logger.info("mr_skipped", mr_iid=mr_iid, action=action, handoff_id=handoff_id)
    return
```

After `commit_sha` is validated (line ~250), add the impact dispatch branch:

```python
if action == "merge" and settings.jira_impact_webhook_enabled:
    asyncio.create_task(
        _run_impact_dispatch(payload, settings, handoff_id, trace_id)
    )
```

Then implement `_run_impact_dispatch` in the same file (or import from a new `impact.py` module — see Task 3.2). All existing dedupe, debouncer, DLQ, and DBOS step infrastructure is reused unchanged.

**Verification**:
```bash
# Send a mock merge hook
curl -X POST http://localhost:8080/gitlab-webhook \
  -H "X-Gitlab-Token: $GITLAB_WEBHOOK_SECRET" \
  -H "X-Gitlab-Event: Merge Request Hook" \
  -H "Content-Type: application/json" \
  -d '{
    "object_attributes": {"iid": 42, "action": "merge", "state": "merged", "last_commit": {"id": "abc123"}},
    "project": {"path_with_namespace": "tdt/jira-skill"}
  }'
# Expected: 202 Accepted; if jira_impact_webhook_enabled=true, _run_impact_dispatch fires
```

**Test the gate**:
```bash
# With JIRA_IMPACT_WEBHOOK_ENABLED=false → impact is not dispatched
# With JIRA_IMPACT_WEBHOOK_ENABLED=true → impact fires, Jira comment posted
```

---

### Task 3.2 — Implement `run_impact_workflow` DBOS step
- [x]
**Owner**: webhook-receiver
**Estimated**: 2–3h
**Target**: `webhook-receiver/src/webhook_receiver/impact.py`

Implement the DBOS step:
```python
@dbos.step()
def run_impact_workflow(payload: dict, settings: Any) -> ImpactReport:
    project_path = payload["project"]["path_with_namespace"]
    mr_iid = payload["object_attributes"]["iid"]
    merge_sha = payload["object_attributes"].get("last_commit", {}).get("id")

    diff = get_mr_diff(project_path, mr_iid)
    fm = FeatureMap()
    result = coverage_analyzer.analyze_diff(diff, project_path, merge_sha, fm)
    report = build_impact_report(result, mr_iid, project_path, merge_sha, triggered_by="webhook")
    return report
```

Then in the handler: call `run_impact_workflow(payload, settings)`, then `_post_impact_to_jira(report, settings)`.

**Verification**:
```bash
# Trigger via webhook, check Jira comment appears
curl -X POST http://localhost:8080/gitlab-webhook ... && sleep 10
# Check webhook-receiver logs for "impact_analysis_complete"
```

---

## Phase 4: code-daily-scan Integration

### Task 4.1 — Refactor `feature_resolver.py` to read `feature-map.yaml`
- [x]
**Owner**: code-daily-scan
**Estimated**: 2h
**Target**: `code-daily-scan/feature_resolver.py`

Refactor to:
1. On init, try to load `tdt-meta/feature-map.yaml`
2. If found: build internal rule list from YAML entries (preserving order)
3. If not found: fall back to embedded `FEATURE_RULES`, `ANDROID_ONLY_RULES`, `IOS_ONLY_RULES` (backward compat)
4. `resolve_feature()` and `resolve_feature_with_confidence()` use the same loaded rule list

Run existing tests to verify no regression.

**Verification**:
```bash
cd code-daily-scan && uv run pytest tests/test_feature_resolver.py -v
```

---

## Phase 5: Integration & Polish

### Task 5.0 — Harden GitNexus blast-radius for large repos
- [x] 
**Owner**: jira-skill
**Estimated**: 1h
**Target**: `jira-skill/src/jira_skill/impact/gitnexus_impact.py`

Update `_invoke_gitnexus` to pass the performance-critical flags discovered from GitNexus v1.6.8 source analysis:

1. **Add `--summary-only`** to the base command (always — we only need counts + risk, not per-symbol lists):
   ```python
   cmd = [
       "node", str(runner_path), "impact", symbol,
       "--direction", direction,
       "--include-tests",
       "-r", repo,
       "--summary-only",   # MANDATORY: omits byDepth, returns byDepthCounts instead
       "--limit", "20",    # cap per-depth symbols (default 100 is too large on big graphs)
       "--depth", "1",     # MANDATORY: cap BFS to direct callers; depth-2 fans out millions of edges
   ]
   ```
   **Do NOT add `--timeout`** — it is not a valid CLI flag (only available on the MCP tool surface). Use the Python-side `subprocess.run(timeout=30)` budget instead.

2. **Update `_parse_response`** to handle `byDepthCounts` when `byDepth` is absent (summary-only mode):
   ```python
   by_depth = raw.get("byDepth") or {}
   by_depth_counts = raw.get("byDepthCounts") or {}
   # When byDepth is absent, sum byDepthCounts as impacted_count fallback
   if not by_depth and by_depth_counts:
       impacted = sum(v for k, v in by_depth_counts.items()
                      if isinstance(v, (int, float)))
   ```

3. **Update `_do_invoke` docstring** to document the flags and the SIGABRT risk on large repos.

**Why `--summary-only` is mandatory**: On `poems-mobile3-ios` (75K symbols, 10M edges), the Node.js v8 heap grows unboundedly during BFS traversal, eventually crashing with SIGABRT (exit code 134) before the Python-side 30-second timeout can fire. `--summary-only` returns `byDepthCounts` (per-depth totals) + `affected_modules` + `risk` — sufficient for the at-risk module use case — without per-symbol enumeration overhead.

**Why `--depth 1` (most important)**: `--limit` only caps the *returned* per-depth list, NOT the BFS edge walk. A hub symbol with 3K+ depth-1 callers forces GitNexus to walk edges from every depth-1 node regardless of `--limit`. At `--depth 2` the BFS walks millions of edges (verified: `TradeBaseFilterButton` in `poems-mobile3-ios` exceeds 30s timeout even with `--limit 5`). `--depth 1` bounds traversal by the symbol's out-degree, returning in 4-10s on `poems-mobile3-ios`.

**Why NOT `--timeout`**: `--timeout` is **not** a valid flag on the GitNexus CLI's `impact` subcommand. It exists only on the MCP tool surface (`timeoutMs` parameter). Passing it to the CLI causes `error: unknown option '--timeout'` (exit code 1, JSON error before any work). The only wall-clock budget available to the Python wrapper is the Python-side `subprocess.run(timeout=30)`.

**Why `--limit 20`**: Bounds output size for hub symbols even if `--summary-only` is absent or the response is degraded. Default 100 is too permissive on large graphs.

**Verification**:
```bash
cd jira-skill && uv run pytest tests/impact/test_gitnexus_impact.py -v
# Manual smoke (poems-mobile3-ios — depth 2 hangs even with --summary-only):
cd /Users/lekhanhvinh/Developer/tdt/poems-mobile3-ios && time node ~/.npm-global/lib/node_modules/gitnexus/dist/cli/index.js impact TradeBaseFilterButton --direction upstream --include-tests -r poems-mobile3-ios --summary-only --limit 20 --depth 1 2>&1 | head -15
# Should return JSON in 4-10s with impactedCount + byDepthCounts.
```

---

### Task 5.1 — Integration tests
- [x]
**Owner**: jira-skill + webhook-receiver
**Estimated**: 2–3h
**Target**: `tests/impact/test_full_pipeline.py`, `webhook-receiver/tests/test_impact_workflow.py`

- CLI: ticket key → comments → MR URLs → diff → feature map → GitNexus → report JSON
- Webhook: mock merge hook payload → 202 → DBOS step → Jira comment posted
- Idempotency: same MR analyzed twice → one Jira comment (updated)
- Cache: second analysis hits cache (check `cache_hits` in report)

**Verification**:
```bash
cd jira-skill && uv run pytest tests/impact/test_full_pipeline.py -v
cd webhook-receiver && uv run pytest tests/test_impact_workflow.py -v
```

---

### Task 5.2 — Lint, typecheck, ruff
- [x]
**Owner**: all
**Estimated**: 1h
**Target**: all modified files

```bash
cd jira-skill && uv run ruff check src/jira_skill/impact/ && uv run mypy src/jira_skill/impact/
cd webhook-receiver && uv run ruff check src/webhook_receiver/impact.py src/webhook_receiver/api/app.py
cd tdt-core && uv run ruff check src/tdt_core/clients/gitlab.py
```

---

### Task 5.3 — End-to-end verification
- [x]
**Owner**: team
**Estimated**: 1–2h

1. `JIRA_IMPACT_WEBHOOK_ENABLED=false` (webhook off, CLI only first)
2. Run `jira-skill impact-ticket <real-ticket>` against a real Jira ticket
3. Verify: Jira comment appears with correct features, test files, staleness warning
4. Enable webhook: `JIRA_IMPACT_WEBHOOK_ENABLED=true`
5. Merge a test MR
6. Verify: Jira comment on linked ticket within 30s

---

## Dependencies

```
Task 0.1 (tdt-core get_mr_diff) ──────────────────────┐
                                                       ├── Task 1.2 (ticket_mr_resolver) ──┐
Task 0.2 (feature-map.yaml) ──── Task 1.1 (feature_map) ─┤
                                                       ├── Task 1.4 (coverage_analyzer) ───┤
                                                       └── Task 3.2 (webhook workflow) ─────┘
Task 1.3 (gitnexus_impact) ───────────────────────────┼── Task 1.4 ────────────────────────┤
Task 5.0 (GitNexus perf fix) ─────────────────────────┴── Task 2.1 (impact_report) ──────────┤
Task 2.2 (regression_planner) ─────────────────────────────────────────────────────────────────┤
Task 2.3 (CLI) ─────────────────────────────────────────────────────────────────────────────┤
Task 3.1 (webhook handler ext) ─── Task 3.2 (DBOS workflow) ──────────────────────────────────┤
Task 4.1 (code-daily-scan integration) ─────────────────────────────────────────────────────┤
Task 5.1 (integration tests) ─── Task 5.2 (lint/typecheck) ─── Task 5.3 (e2e verification)
```
