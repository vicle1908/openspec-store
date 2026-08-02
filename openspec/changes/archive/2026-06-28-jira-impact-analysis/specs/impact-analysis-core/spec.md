## ADDED Requirements

### Requirement: Feature Map Configuration
The system SHALL resolve a changed file path to one or more `feature.<tag>` tags using a YAML feature map at `tdt-meta/feature-map.yaml`. The file MUST have a top-level `feature_map:` key mapping path prefixes (directories end with `/`) to lists of `[feature_tag, platform]` tags. Tags MUST be dot-separated identifiers (e.g. `feature.auth`); the second element MUST be one of `ios`, `android`, `python`. The file MUST also contain a `base_modules:` list whose entries trigger full-platform escalation.

#### Scenario: Longest-prefix match wins
- **WHEN** the resolver scans `feature_map` entries in document order
- **THEN** the first entry whose path prefix matches the changed file path SHALL be returned

#### Scenario: Base module propagation
- **WHEN** a resolved tag is in `base_modules`
- **THEN** the system SHALL mark all named features on the same platform as at-risk
- **AND** the system SHALL skip the GitNexus blast-radius computation for that change

#### Scenario: Platform tags excluded from at-risk
- **WHEN** base-module escalation enumerates tags to mark as at-risk
- **THEN** platform tags (`ios`, `android`, `python`, `unknown`) SHALL be excluded
- **AND** only tags beginning with `feature.` SHALL appear in `at_risk_modules` and `coverage_gaps`

#### Scenario: Unmapped path
- **WHEN** no prefix matches a changed file path
- **THEN** the resolver SHALL return the fallback tag (default `feature.others`) and mark `matched_entry="<fallback>"`
- **AND** the report SHALL include the path in `unmapped_paths`
- **AND** the report SHALL state "N file(s) have no feature mapping — update feature-map.yaml"

#### Scenario: Loader caches on first load
- **WHEN** the loader is first instantiated
- **THEN** the YAML contents MUST be parsed once and cached
- **AND** the loader MUST reload when the file's mtime changes

### Requirement: Ticket-to-MR Resolution
The system SHALL extract GitLab merge-request references from a Jira ticket's comments and description using two patterns: full URLs (`https://<host>/<group>/<project>/-/merge_requests/<iid>`) and short notation (`!N` with an optional `MR ` prefix). For each extracted reference the system SHALL enrich it via `tdt-core`'s `fetch_mr_metadata` and deduplicate by `(project_path, mr_iid)`.

#### Scenario: Full URL is extracted
- **WHEN** a comment contains `https://git.ecomedic.vn/tdt/pmobile3-ios/-/merge_requests/42`
- **THEN** the resolver SHALL return one `MrReference` with `project_path="tdt/pmobile3-ios"`, `mr_iid=42`, and the absolute `url`

#### Scenario: Short notation is extracted
- **WHEN** a comment contains `MR !23598`
- **THEN** the resolver SHALL return one `MrReference` with `mr_iid=23598`
- **AND** the resolver SHALL enrich it via the GitLab API using the default host placeholder

#### Scenario: Duplicates are removed
- **WHEN** the same `project_path + mr_iid` appears in multiple comments
- **THEN** the resolver SHALL return exactly one `MrReference` per pair

### Requirement: GitLab API authentication and MR fetching
All GitLab API calls SHALL go through `GitlabClientFactory.from_env()` from `tdt-core.clients.gitlab`. Credentials MUST come from `GITLAB_PAT` / `GITLAB_TOKEN` in `~/.tdt/.env`. MR diffs MUST be fetched via the python-gitlab method `mr.changes()`, which returns a dict with `changes: list[FileChange]`. Each `FileChange` MUST include `new_path`, `old_path`, `diff` (unified-diff string), `new_file`, `renamed_file`, and `deleted_file`.

#### Scenario: Merge commit SHA is read
- **WHEN** an MR has `state == "merged"`
- **THEN** the system SHALL use `mr.merge_commit_sha` as the cache key

### Requirement: GitNexus blast-radius invocation
The system SHALL invoke the GitNexus CLI as `node <runner> impact <symbol> --direction upstream --include-tests -r <repo> --summary-only --limit 20 --depth 1` for each extracted symbol. The CLI emits JSON to stdout (no `--json` flag). The system MUST parse `status`, `impactedCount`, `risk`, `byDepth`, `byDepthCounts`, `affected_modules`, and `affected_processes` per the JSON schema. Each invocation MUST time out after 30 seconds; on timeout, the symbol SHALL be treated as `not_found`.

The `--summary-only` flag is MANDATORY for large repositories. Without it, GitNexus enumerates every symbol at each depth level (default limit 100 per depth, `--depth 3`) before returning — on a graph with 75K+ symbols and 10M+ edges (e.g. `poems-mobile3-ios`, `poems-mobile3-android`), the Node.js v8 heap grows unboundedly during BFS traversal, eventually crashing with SIGABRT (exit code 134) before the Python-side 30-second timeout fires. With `--summary-only`, GitNexus returns `byDepthCounts` (counts per depth), `affected_modules`, `affected_processes`, and `risk` — sufficient for at-risk module detection — without the per-symbol enumeration overhead. The `byDepth` field is omitted from the response; `byDepthCounts` (a `Record<number, number>`) MUST be used instead.

The `--limit 20` cap per depth level bounds output size for hub symbols (classes with many callers) even if `--summary-only` is absent or the output is degraded. **`--limit` only caps the returned per-depth list, NOT the BFS edge walk.** A hub symbol with 3K+ direct callers forces GitNexus to walk edges from every depth-1 node regardless of `--limit`, so this cap cannot be relied upon for traversal cost.

The `--depth 1` flag caps the BFS traversal to direct callers only. **This is the most important performance flag.** Going to `--depth 2` on a hub symbol (e.g. `TradeBaseFilterButton` in `poems-mobile3-ios` with 3254 depth-1 callers) routinely exceeds the 30-second Python timeout even with `--limit 5 --summary-only` because the BFS walks millions of edges from every depth-1 node. Depth 1 keeps the traversal bounded by the symbol's out-degree, returning in 4-10 seconds on `poems-mobile3-ios`. Transitive impacts beyond direct callers are not captured by this integration; if transitives are needed, run a downstream / forward BFS query on the depth-1 callers as a separate, second-pass operation.

Note: `--timeout` is **NOT** a valid flag for the GitNexus CLI's `impact` subcommand. The flag exists only on the MCP tool surface (`timeoutMs` parameter), not the CLI. The only wall-clock budget available to the Python wrapper is the Python-side `subprocess.run(timeout=30)`, which SIGKILLs the Node process on expiry.

When `--summary-only` is in effect, the parser SHALL use `byDepthCounts` (per-depth totals) to populate `impacted_count` when `byDepth` is absent from the response.

#### Scenario: Symbol is found
- **WHEN** GitNexus returns `status="found"` with `impactedCount` and `byDepthCounts: {"1": N}` (no `byDepth`)
- **THEN** the system SHALL record `affected_modules`, `risk`, and `impacted_count = N`
- **AND** if `byDepth` is also present in the response, the system SHALL record per-depth symbol lists in addition to `byDepthCounts`

#### Scenario: Symbol is not found
- **WHEN** GitNexus returns `status="not_found"` or the call fails
- **THEN** the system SHALL add the symbol to `symbols_not_indexed`
- **AND** the system SHALL record `risk="UNKNOWN"`

#### Scenario: Staleness warning threshold
- **WHEN** more than 20% of extracted symbols are not found in the GitNexus index
- **THEN** the report SHALL include the warning "GitNexus index may be stale — N symbols not found. Run `gitnexus analyze` to refresh."

### Requirement: Symbol extraction from diff
The system SHALL extract changed symbols from a unified diff using `ast.parse()` for Python files (matching `FunctionDef`, `ClassDef`, `AsyncFunctionDef` whose first line overlaps a changed range) and a regex fallback (`def `, `class `, `async def `, `func `, `struct `, `enum `) for all other languages. When no symbols can be extracted, the file path SHALL be used as the symbol identifier.

#### Scenario: Python symbol is extracted
- **WHEN** a Python file's diff contains `def do_thing():`
- **THEN** `do_thing` SHALL be returned as an extracted symbol

#### Scenario: No symbols extracted
- **WHEN** a diff has no recognizable symbols
- **THEN** the file path SHALL be used as the symbol identifier

### Requirement: Blast-radius result caching
GitNexus results SHALL be cached to a SQLite database at `$TDT_HOME/state/webhook-receiver/webhook-impacts-cache.sqlite`. The cache key SHALL be `sha256(f"{repo}:{commit_sha}:{','.join(sorted(symbols))}".encode())`. Entries SHALL expire after the configured TTL (default 3600 seconds, override via `GITNEXUS_INDEX_CACHE_TTL_SECONDS`).

#### Scenario: Cache hit
- **WHEN** the same `(repo, commit_sha, symbols)` tuple has a stored result within the TTL window
- **THEN** the system SHALL return the stored result and set `cache_hit=True`

#### Scenario: Cache miss
- **WHEN** no stored result exists for the key
- **THEN** the system SHALL invoke GitNexus and store the result before returning

### Requirement: Core/common escalation threshold
When a changed file resolves to a tag in `base_modules`, the system SHALL compute the net line delta (added + removed, excluding whitespace-only lines). If the net delta is more than 3 lines, the system SHALL mark all platform features at-risk and skip GitNexus analysis for that file. If the net delta is 3 or fewer, the file SHALL be treated as a named feature change (GitNexus runs normally).

#### Scenario: Small base-module change
- **WHEN** `feature.common` is in `base_modules` and the net delta is 2 lines
- **THEN** the system SHALL run GitNexus blast-radius analysis

#### Scenario: Large base-module change
- **WHEN** `feature.common` is in `base_modules` and the net delta is 25 lines
- **THEN** the system SHALL mark all platform features at-risk
- **AND** the system SHALL skip GitNexus analysis

### Requirement: Impact report data model
The system SHALL emit an `ImpactReport` Pydantic model with the following fields: `mr_iid: int`, `mr_url: str`, `project_path: str`, `commit_sha: str`, `ticket_key: str | None`, `triggered_by: Literal["webhook", "cli"]`, `changed_files: list[ChangedFile]`, `resolved_features: list[str]`, `at_risk_modules: list[str]`, `test_files_to_run: list[TestFile]`, `coverage_gaps: list[str]`, `unmapped_paths: list[str]`, `analysis_timestamp: datetime`, `analysis_duration_ms: int`, `gitnexus_index_stale: bool = False`, `cache_hits: int = 0`, `cache_misses: int = 0`. Nested `ChangedFile` MUST carry `path`, `feature_tags`, `lines_added`, `lines_removed`, `net_lines`, `symbols_extracted`. Nested `TestFile` MUST carry `path`, `test_type: TestType`, `covers_features: list[str]`, `covers_symbols: list[str]`. `TestType` is an enum with values `unit`, `integration`, `smoke`, `e2e`, `regression`, `unknown`.

#### Scenario: CLI emits report
- **WHEN** the CLI runs `impact ticket <KEY>` against a ticket with a merged MR
- **THEN** the report MUST include the resolved MR's `mr_iid`, `commit_sha`, `resolved_features`, and `at_risk_modules`

#### Scenario: Signed line delta
- **WHEN** a file's diff has `lines_added = A` and `lines_removed = R`
- **THEN** `net_lines` SHALL equal `A - R` (signed), and the base-module escalation threshold SHALL compare against `abs(net_lines)` so pure deletions also escalate

### Requirement: Idempotent Jira comments
Comment identity SHALL be `(mr_iid, ticket_key)`. On re-analysis the system SHALL fetch existing comments, find the comment whose body contains `Impact Analysis — MR !{mr_iid}`, and edit it in place via `issue_edit_comment`. When no existing comment is found, the system SHALL add a new one via `add_comment_adf`. The marker search MUST match both literal em-dash (`—`) and JSON-escaped (`\u2014`) forms to handle upstream SDK PUT round-trips.

#### Scenario: First post creates a comment
- **WHEN** no existing comment matches the marker
- **THEN** the system SHALL add a new ADF comment via `add_comment_adf`

#### Scenario: Re-post edits the existing comment
- **WHEN** a comment with the marker already exists
- **THEN** the system SHALL edit it via `issue_edit_comment`
- **AND** the ticket SHALL NOT gain an additional comment

### Requirement: Test type inference
The system SHALL infer each recommended test's `TestType` using two layers: a feature-bucket table (`FEATURE_TEST_TYPES`) and a path-pattern override. When both layers apply, the system SHALL prefer the more specific path-based inference. GitNexus-discovered test files SHALL be refined by path. When no inference applies, the type SHALL be `UNKNOWN`.

#### Scenario: Feature-bucket inference
- **WHEN** the changed feature is `feature.trade`
- **THEN** the inferred test types SHALL include `integration`, `smoke`, and `e2e` per the table

#### Scenario: Path-based override
- **WHEN** a test file path matches `tests/integration/`
- **THEN** the inferred type SHALL be `integration` regardless of feature bucket

### Requirement: CLI contract
The system SHALL expose three CLI commands under the `impact` subcommand:

- `impact ticket <KEY>` — analyze a Jira ticket and post the impact report.
- `impact mr <PROJECT> <IID>` — analyze a single MR by URL.
- `impact feature <TAG>` — list files / symbols for one feature tag.

The `impact ticket` command MUST fetch comments, extract MR references, fetch diffs, run the analysis pipeline, and either print (with `--dry-run`) or post the report to Jira.

#### Scenario: Dry run prints ADF
- **WHEN** the user runs `impact ticket SR-123 --dry-run`
- **THEN** the system SHALL print the rendered ADF document to stdout
- **AND** it SHALL NOT call `add_comment_adf` or `issue_edit_comment`

#### Scenario: Posting writes a Jira comment
- **WHEN** the user runs `impact ticket SR-123` without `--dry-run`
- **THEN** the system SHALL post the ADF document to ticket `SR-123`

### Requirement: Webhook extension to `POST /gitlab-webhook`
The webhook-receiver SHALL extend the existing `POST /gitlab-webhook` endpoint so that `action == "merge"` (with `state == "merged"`) routes through `handle_merge_request` to a new `run_impact_workflow` DBOS step. The state guard MUST be modified to allow merge hooks through, and the action allowlist MUST include `"merge"`. When `JIRA_IMPACT_WEBHOOK_ENABLED` is false, the workflow MUST NOT be invoked.

#### Scenario: Merge hook triggers impact workflow
- **WHEN** a merge hook arrives with `action == "merge"` and `state == "merged"`
- **THEN** the system SHALL accept the request with HTTP 200
- **AND** the system SHALL fire-and-forget an `asyncio.create_task` running `run_impact_workflow`
- **AND** the system SHALL also dispatch to ai-review per existing behavior

#### Scenario: Disabled flag suppresses impact workflow
- **WHEN** `JIRA_IMPACT_WEBHOOK_ENABLED` is false
- **THEN** the merge hook SHALL be processed by the existing ai-review path only
- **AND** `run_impact_workflow` SHALL NOT be invoked

### Requirement: Webhook idempotency, soft failures, and feature flag
The `run_impact_workflow` step MUST never raise an exception; failures MUST be captured in `ImpactWorkflowResult.skipped_reason` or logged. The system MUST respect the `JIRA_IMPACT_WEBHOOK_ENABLED` env flag (default `false`). When the webhook is disabled, the merge hook is processed as before. When the GitLab API or Jira API fails, the webhook MUST still respond 200 so the GitLab sender does not retry indefinitely.

#### Scenario: GitLab API failure
- **WHEN** `fetch_mr_changes` raises an exception
- **THEN** the workflow SHALL log the failure with `impact_workflow_pipeline_failed`
- **AND** the workflow SHALL return an `ImpactWorkflowResult` with `skipped_reason="pipeline_failed:<ExceptionType>"`
- **AND** the webhook MUST still return HTTP 200

#### Scenario: No matching tickets
- **WHEN** the JQL search returns zero tickets
- **THEN** the workflow SHALL exit cleanly with `posted_comment_ids={}`
- **AND** no Jira write SHALL occur

### Requirement: Jira ADF comment format
The impact comment MUST be a Jira ADF document restricted to the workspace's existing node types: `doc` (root, `version: 1`), `paragraph`, `text` (with optional `marks: [{type: "strong"}]`), and `mention`. Tables, headings, bullet lists, and code blocks MUST NOT be used. Optional sections (e.g. coverage gaps, recommended tests) SHALL be omitted when empty.

#### Scenario: Optional sections are omitted
- **WHEN** `coverage_gaps` is empty
- **THEN** the rendered ADF MUST NOT contain a "Coverage Gaps" section

#### Scenario: Staleness warning is prepended
- **WHEN** `gitnexus_index_stale == True`
- **THEN** the first paragraph of the ADF MUST be the warning text
- **AND** the warning MUST use `marks: [{type: "strong"}]`

#### Scenario: Raw report is persisted
- **WHEN** the report is built
- **THEN** the full JSON MUST be written to `$TDT_HOME/state/webhook-receiver/webhook-impacts/{mr_iid}-{commit_sha}.json`
- **AND** the comment MUST include a "View raw report" link referencing that path

### Requirement: Builder granularity
The ADF builder SHALL expose private helpers `_heading_paragraph(text)`, `_bold_label_paragraph(label, value)`, and `_bullet_paragraph(text)`, mirroring the conventions in `jira_skill/issue/adf.py`. The public `build_impact_adf(report, raw_report_path)` MUST return the full document.

#### Scenario: Public entry point returns a doc
- **WHEN** `build_impact_adf(report, raw_report_path)` is called
- **THEN** the returned dict MUST have `version: 1`, `type: "doc"`, and a non-empty `content` list

### Requirement: GitLab MR Note Posting
The system SHALL post a GitLab MR note containing the full impact analysis rendered as GitLab markdown on every non-update MR event (action ∈ {open, reopen, merge}). The note SHALL be idempotent: on re-run, the existing TDT note SHALL be edited in place rather than appended. The note body prefix SHALL be "⚠️ Impact Analysis — MR !" for idempotency detection. The GitLab posting SHALL be fire-and-forget and SHALL NOT block or delay the webhook response. Failures SHALL be logged but SHALL NOT propagate as errors to the caller.

The Jira comment posting remains merge-only per SPEC-IA-7.

#### Scenario: open event posts GitLab note
- **WHEN** an MR transitions to opened
- **THEN** the system SHALL post the impact analysis as a GitLab MR note
- **AND** the system SHALL NOT post a Jira comment (no merged commit SHA available yet)
- **AND** `triggered_by` SHALL be set to `"webhook-open"`

#### Scenario: reopen event posts GitLab note
- **WHEN** an MR is reopened
- **THEN** the system SHALL post the impact analysis as a GitLab MR note
- **AND** `triggered_by` SHALL be set to `"webhook-reopen"`

#### Scenario: merge event posts both
- **WHEN** an MR is merged
- **THEN** the system SHALL post the impact analysis as a GitLab MR note
- **AND** `triggered_by` SHALL be set to `"webhook-merge"`
- **AND** the system SHALL post an idempotent Jira ADF comment on the matched ticket

#### Scenario: update event is skipped
- **WHEN** `action = "update"`
- **THEN** the system SHALL skip both GitLab and Jira posting entirely
- **AND** the debouncer SHALL coalesce rapid update bursts (only the latest fires)

#### Scenario: idempotency prevents duplicates
- **WHEN** the same MR fires a second time with the same action
- **THEN** the system SHALL edit the existing GitLab MR note in place
- **AND** SHALL edit the existing Jira comment in place (already implemented)

### Requirement: GitLab Markdown Comment Format
The GitLab MR note body MUST be GitLab Flavored Markdown produced by `build_gitlab_note` in `jira_skill.impact.gitlab_note`. The function reads `ImpactReport` pydantic model fields directly and formats them as markdown — it is NOT an ADF-to-markdown converter. The note MUST contain the same information sections as the Jira ADF comment (staleness warning, title, stats, affected features, at-risk modules, changed files, recommended tests, coverage gaps, unmapped paths, raw report link) but rendered as GitLab markdown. The idempotency marker `NOTE_PREFIX = "⚠️ Impact Analysis — MR !"` SHALL NOT be present in the output of `build_gitlab_note`; it is prepended by `post_gitlab_note` before calling `upsert_mr_note`. The title SHALL use `###` heading level and SHALL include the " merged" suffix when `triggered_by == "webhook-merge"`, omitting it for `webhook-open` and `webhook-reopen`.

#### Scenario: Markdown section structure
- **WHEN** the note body is rendered from an `ImpactReport`
- **THEN** the body SHALL contain a `### Impact Analysis — MR !{mr_iid}` title line
- **AND** a stats line `"Analyzed {n} changed files across {m} features in {ms}ms. Cache: {hits} hits / {misses} misses."`
- **AND** an `**Affected Features:**` line listing `resolved_features`
- **AND** an `**At-Risk Modules:**` line listing `at_risk_modules` (or `none`)
- **AND** a `### Changed Files ({n})` section rendering each `ChangedFileModel` as `- \`{path}\` ({feature_tags}, +{lines_added}/-{lines_removed}, symbols: {symbols_extracted})`
- **AND** a `### Recommended Tests ({n})` section rendering each `TestFileModel` as `- \`{path}\` ({test_type.value}) — covers {covers_features}`
- **AND** a `**Coverage Gaps:**` line when `coverage_gaps` is non-empty
- **AND** a `**Unmapped Paths ({n}):**` line when `unmapped_paths` is non-empty
- **AND** a `[View raw impact report](file://{path})` link when `raw_report_path` is provided
- **AND** empty optional sections SHALL be omitted entirely

#### Scenario: Staleness warning is included
- **WHEN** `gitnexus_index_stale == True`
- **THEN** the note SHALL prepend a bold warning: "**⚠️ GitNexus index may be stale** — N symbols not found. Run `gitnexus analyze` to refresh."

### Requirement: Error handling
The system MUST handle GitLab, GitNexus, and Jira API failures per the following rules:
- CLI: emit warning, skip affected MR, continue with others. Exit 0 if at least one MR succeeded.
- Webhook: retry 2x with exponential backoff (1s, 2s); on final failure, write to `~/.tdt/state/webhook-impacts-failed/<mr_iid>.json`.
- GitNexus unavailable: proceed with feature-map only, mark `at_risk_modules` and `test_files_to_run` as empty, and add a warning.
- Jira API failure: log and exit non-zero on the CLI; on the webhook path, retry then write to the failure directory.

#### Scenario: CLI continues past a failing MR
- **WHEN** one MR's GitLab fetch raises
- **THEN** the CLI SHALL log a warning and continue with the remaining MRs
- **AND** the CLI SHALL exit 0 if at least one MR succeeded

#### Scenario: GitNexus unavailable
- **WHEN** the GitNexus subprocess is not found
- **THEN** the report SHALL contain empty `at_risk_modules` and `test_files_to_run`
- **AND** the report SHALL include the "GitNexus unavailable" warning

### Requirement: Environment variables
The system MUST recognize the following environment variables:

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `JIRA_IMPACT_WEBHOOK_ENABLED` | No | `false` | Enable impact analysis on MR merge in webhook-receiver |
|| `GITLAB_IMPACT_NOTE_ENABLED` | No | `false` | Enable GitLab MR note posting on open/reopen/merge events |
| `GITNEXUS_INDEX_CACHE_TTL_SECONDS` | No | `3600` | TTL for GitNexus result cache |
| `JIRA_IMPACT_TICKET_FILTER` | No | `None` | JQL to auto-find related tickets |

#### Scenario: Default flag is false
- **WHEN** `JIRA_IMPACT_WEBHOOK_ENABLED` is not set
- **THEN** the webhook MUST treat impact analysis as disabled

#### Scenario: Cache TTL override
- **WHEN** `GITNEXUS_INDEX_CACHE_TTL_SECONDS` is set to `7200`
- **THEN** the cache SHALL honor the 7200-second TTL