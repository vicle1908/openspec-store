# Jira Impact Analysis — Design

## Context

The TDT ecosystem ships code through GitLab MRs across 6+ repositories (iOS, Android, tdt-core, webhook-receiver, ai-review, jira-skill). When an MR is merged, the team needs a reliable, repeatable answer to: **what must QA and Dev test?**

Three things exist in the ecosystem today that we build on:

1. **`code-daily-scan/feature_resolver.py`** — a working 11-feature path-to-feature mapper with platform-aware rules and confidence scoring. The feature taxonomy (`Auth`, `Trade`, `Home`, `Market`, `WatchList`, `Community`, `Me/Settings`, `Form`, `Deposit/Withdraw`, `Common`, `Others`) is established and understood by the team.

2. **`webhook-receiver`** — a Go/FastAPI service that already owns GitLab webhook ingestion, DBOS debouncing, httpx dispatch, and Jira interaction. The `/gitlab-webhook` handler already receives `Merge Request Hook` events, runs them through a 60s debouncer, and dispatches to `ai-review`.

3. **`jira-skill`** — a mature Python SDK with `PatchedJira`, `GitlabClientFactory`, rich CLI (Typer), and existing `gitlab/` subpackage for MR modeling.

This change does not create new infrastructure. It extends what exists.

## Goals / Non-Goals

**Goals:**

- On MR merge: emit an `ImpactReport` that maps changed files to features, identifies at-risk modules via GitNexus blast-radius, and recommends specific test files and test types.
- On demand (CLI): given a Jira ticket key, extract its MR references, run the same analysis, and output a structured report.
- Produce Jira ADF comments from the report.
- Define a `feature-map.yaml` that aligns with the existing `code-daily-scan` feature taxonomy and serves as the shared source of truth for both tools.

**Non-Goals:**

- Auto-run tests or create test cases programmatically.
- Replace GitLab/Jira configurations or manage test management systems.
- Infer features from commit messages (explicit YAML mapping only).
- Platform-level cascade: each MR's impact analysis stays within its own repo/platform. Defer full cross-repo cascade to v2.
- No changes to iOS/Android native build tooling.
- Slack integration is out of scope for v1.

## Decisions

### D1. `feature-map.yaml` as shared source of truth, aligned with `code-daily-scan`

- **Decision**: `tdt-meta/feature-map.yaml` defines the canonical directory-to-feature mapping. Both `code-daily-scan` (read) and `jira-impact` (read) load this file at startup. The existing `FEATURE_RULES`, `ANDROID_ONLY_RULES`, and `IOS_ONLY_RULES` in `code-daily-scan/feature_resolver.py` are replaced by a YAML loader that reads `feature-map.yaml` on initialization, with a fallback to embedded defaults for backward compatibility if the YAML is absent.
- **Why**: The `code-daily-scan` feature taxonomy (11 features) is already established. Reusing it means QA and developers get consistent feature labels across both tools. A YAML file is human-editable, git-tracked, and diff-friendly — no code change needed to add a new feature.
- **Schema**: each entry maps a path prefix (string, with trailing `/` for directories) to a list of `[feature_tag, platform]` tags. Entries are processed in order; first match wins (longest-prefix rule).
- **Why not extend `feature_resolver.py`**: Python rule-lists are not friendly for non-developers. YAML is readable by product managers and QA leads who maintain the feature taxonomy.
- **Alternatives considered**:
  - Keep `FEATURE_RULES` as-is, copy the taxonomy to `feature-map.yaml` — rejected: two sources of truth diverge over time.
  - Add a `feature_resolver` subpackage to `tdt-core` — rejected: both consumers (`code-daily-scan`, `jira-impact`) are standalone tools, not library imports.

### D2. Ticket → MR resolution via Jira comment parsing, GitLab API for diff

- **Decision**: The CLI resolver fetches all comments on a ticket via `PatchedJira` (using the existing `issue/comments.py` patterns), extracts GitLab MR URLs with regex, deduplicates by `(project_path, MR_IID)`, and fetches MR metadata via `tdt-core`'s `GitlabClientFactory`. The webhook path bypasses this since the MR URL is in the GitLab payload.
- **Why**: Jira comments are the team's de-facto MR tracker. The existing `gitlab/mr_sync.py` and `gitlab/branch_linking.py` use the same URL extraction patterns. Reusing them keeps consistency.
- **MR diff fetching**: use the new `tdt-core` helper `get_mr_diff(project_path, mr_iid)` (see D5) which wraps `python-gitlab`'s `mr.diffs.list()`. For the webhook path, the merge-commit SHA is already in the webhook payload (`object_attributes.last_commit.id`).
- **Regex patterns handled** (same as `gitlab/branch_linking.py`):
  - Full URL: `https://git.ecomedic.vn/<group>/<project>/-/merge_requests/<iid>`
  - Short: `!<iid>`
  - Inline: `MR !<iid>`, `mr !<iid>`

### D3. GitNexus via subprocess, not MCP tools or tdt-core wrapper

- **Decision**: GitNexus has no Python wrapper in `tdt-core` and no published Python SDK. The `gitnexus impact` command is invoked via `subprocess.run()` from the Python process. The command is:
  ```bash
  node <runner> impact {symbol} --direction upstream --include-tests -r {repo} --summary-only --limit 20 --depth 1
  ```
  Output is parsed from the stdout JSON. The working directory is the repo root (e.g. `~/Developer/tdt/poems-mobile3-ios`).
- **Why `--summary-only` is mandatory**: The default traversal enumerates up to 100 symbols per depth level across 3 depths. On `poems-mobile3-ios` (75K+ symbols, 10M+ edges), this causes the Node.js v8 heap to grow unboundedly over minutes, eventually crashing with SIGABRT before the 30-second Python timeout can fire. `--summary-only` returns only `byDepthCounts` (per-depth totals), `affected_modules`, and `risk` — sufficient signal for the at-risk module use case — without the per-symbol enumeration overhead.
- **Why `--limit 20`**: Bounds output size for hub symbols (classes with many callers) even if `--summary-only` is absent or the response is degraded. Default 100 is too permissive on large graphs. Note: `--limit` only caps the *returned* per-depth list — it does NOT bound BFS traversal cost.
- **Why `--depth 1`**: Caps BFS traversal to direct callers only. **This is the most important performance flag.** Going to `--depth 2` on a hub symbol with 3K+ depth-1 callers (e.g. `TradeBaseFilterButton` in `poems-mobile3-ios`) routinely exceeds the 30-second Python timeout even with `--limit 5 --summary-only`, because the BFS still walks edges from every depth-1 node. Depth 1 bounds traversal by the symbol's out-degree (typically tens of edges). Empirically returns in 4-10s on `poems-mobile3-ios`. Transitive impacts beyond direct callers require a separate, second-pass forward BFS on the depth-1 callers.
- **Why NOT `--timeout`**: `--timeout` is **not** a valid flag on the GitNexus CLI's `impact` subcommand. It exists only on the MCP tool surface (`timeoutMs` parameter). Passing it to the CLI causes `error: unknown option '--timeout'` (exit code 1, JSON error before any work). The only wall-clock budget available to the Python wrapper is the Python-side `subprocess.run(timeout=30)`.
- **Why subprocess over MCP**: MCP tools require an MCP server and client setup. `subprocess.run()` is synchronous, stateless, and requires no additional infrastructure. GitNexus is a CLI tool already on the PATH.
- **Why not wait for a tdt-core wrapper**: Building a tdt-core wrapper before shipping the feature creates a blocking dependency. The subprocess call is stable and already used by the GitNexus CLI documentation.
- **Symbol extraction strategy**:
  1. Parse the diff with `git diff --no-color <base>...<head>` to get added/changed lines per file.
  2. For Python: `ast.parse()` to extract `FunctionDef`/`ClassDef` nodes whose first line falls in a changed range.
  3. Fallback (all languages): regex on `def `, `class `, `async def `, `func `, `class `, `struct `, `enum ` in changed lines.
  4. If extraction fails, use the file path as the symbol identifier.
- **Result parsing**: GitNexus outputs JSON to stdout. Parse `upstream_callers`, `test_files`, `modules` from the result.
- **Alternatives considered**:
  - GitNexus MCP tools — rejected: requires MCP server setup, adds infrastructure complexity.
  - LLM symbol extraction — rejected: non-deterministic, expensive, slow.
  - Full file-path as symbol — rejected: loses call-graph granularity; too noisy for blast-radius.

### D4. Platform-level cascade for common; per-symbol GitNexus for named features

- **Decision**: When a changed file maps to `feature.common`, the system marks all features on the same platform as at-risk and skips per-symbol GitNexus analysis. When a changed file maps to a named feature, run GitNexus impact for extracted symbols.
- **Threshold for common escalation**: net line delta (added + removed, excluding whitespace-only lines) <= 3 skips the full sweep. This filters trivial formatting diffs while capturing logic changes.
- **Why not cross-repo scan for common**: iOS and Android have separate `common/` directories. Without a shared library lock-file, a common change in iOS is not automatically correlated with the same logical change in Android.

### D5. Extend existing `/gitlab-webhook` with a single-line change

- **Decision**: The existing `POST /gitlab-webhook` handler in `webhook-receiver` is extended with `action == "merge"` routing. The implementation is a **two-line change**:
  1. `app.py:238` — bypass the `state in ("merged", "closed")` early-return when `action == "merge"`.
  2. `app.py:241` — add `"merge"` to the action allowlist tuple.

  Then add a new branch in `handle_merge_request`:
  ```python
  if action == "merge" and settings.jira_impact_webhook_enabled:
      await _run_impact_dispatch(payload, settings, handoff_id, trace_id)
  ```

- **Why so minimal**: The existing code already routes Merge Request Hooks through `handle_merge_request`. The handler already has token validation, dedupe (lines 800-820), DBOS debouncer registration (lines 500-520), DBOS step wiring via `_dispatch_mr_workflow`, and DLQ on failure. Adding `"merge"` to the allowlist is the entire routing change.
- **State guard bypass**: the existing code at `app.py:238` returns early if `state in ("merged", "closed")`. For `action == "merge"`, `state` will be `"merged"`. The fix moves the state guard to fire only when `action != "merge"`, or guards by `action` first then `state`.
- **DBOS debouncer behavior**: The existing 60-second debouncer uses `f"mr-{mr_iid}"` as the key. A rapid `open → update → merge` sequence is debounced to one dispatch. This is correct — we only want the final merge state.
- **Why no separate endpoint**: A separate `/gitlab-webhook/merge` route adds another public surface, another token check, and diverges from the established pattern. Action-based routing inside the existing handler is the cleaner path.
- **Failure handling**: `handle_merge_request`'s existing failure tracking (failure counter, DLQ on 2 consecutive failures) covers the impact dispatch path automatically since `_run_impact_dispatch` is called inside the same function.

### D6. Jira ADF comment as the sole output channel

- **Decision**: The `ImpactReport` is written as a Jira ADF comment on the linked ticket. There is no Slack integration in v1.
- **Why Jira comment**: QA already lives in Jira. Posting to the ticket creates a permanent, searchable record.
- **Jira ADF structure**:
  ```
  h3: Impact Analysis — MR !{iid} merged
  paragraph: Analysis of {n} changed files across {m} features. Generated at {timestamp}.
  h4: Affected Features
  bulletList: feature.auth, feature.trade, ...
  h4: Changed Files
  table: path | feature | lines | symbols
  h4: Recommended Tests
  table: test_file | test_type | covers
  ```

### D7. Feature module in `jira-skill`, workflow in `webhook-receiver`

- **Decision**: The SDK lives at `jira-skill/src/jira_skill/impact/` (new package). The webhook workflow logic lives at `webhook-receiver/src/webhook_receiver/impact.py`. The SDK is imported by the webhook workflow — the webhook does not duplicate the analysis logic.
- **Why `jira-skill` for SDK**: `jira-skill` already owns all Jira-facing CLI and SDK work. `jira-skill` already has `GitlabClientFactory`, `PatchedJira`, `load_tdt_env()`, and Typer CLI scaffolding.
- **Why not `tdt-core`**: `tdt-core` is the foundation shared across all repos. Feature-map YAML loading, Jira comment parsing, and test-type inference are `jira-skill`-specific concerns.
- **Existing patterns reused**:
  - `jira_skill.gitlab.config` — GitlabClientFactory from `tdt_core.clients.gitlab`
  - `jira_skill.issue.comments` — comment fetching patterns
  - `jira_skill.config` — JiraClientFactory from `tdt_core.clients.jira`
  - `webhook_receiver.paths.TDT_STATE_DIR` — canonical state directory

## Data Flow

```
WEBHOOK PATH:
GitLab ──[Merge Request Hook, action=merge]──► /gitlab-webhook
                                                     │
                                                     ▼
                                              Token validated
                                                     │
                                                     ▼
                                              DBOS debouncer (60s)
                                                     │
                                                     ▼
                                       handle_merge_request(action=merge)
                                                     │
                                    ┌─────────────────┼─────────────────┐
                                    ▼                 ▼                 ▼
                            ai-review          impact (SDK)        (existing
                            dispatch           import               skip for
                            (unchanged)        from                 non-merge
                                                  jira_skill.        actions)
                                                  impact
                                                     │
                                                     ▼
                                          Fetch MR diff (GitLab API)
                                          feature-map.yaml lookup
                                          GitNexus impact (subprocess)
                                          Build ImpactReport
                                                     │
                                                     ▼
                                          Jira ADF comment posted
                                          (add_comment_adf)


CLI PATH:
jira-skill impact-ticket SR-3588
    │
    ▼
Fetch ticket comments (PatchedJira)
    │
    ▼
Extract MR URLs (regex)
    │
    ▼
Fetch MR diffs (GitLab API)
    │
    ▼
feature-map.yaml + GitNexus pipeline
    │
    ▼
Print ImpactReport (JSON)
```

## Module Layout

```
tdt-meta/
└── feature-map.yaml                  # NEW: shared feature-to-directory mapping

tdt-core/src/tdt_core/clients/
└── gitlab.py                        # MODIFIED: add get_mr_diff() helper

jira-skill/src/jira_skill/
└── impact/                          # NEW package (~1000 lines)
    ├── __init__.py                  # Public exports
    ├── feature_map.py               # YAML loader, longest-prefix resolver
    ├── ticket_mr_resolver.py        # Comment parser, MR URL extractor, diff fetcher
    ├── gitnexus_impact.py           # Subprocess wrapper, symbol extraction, cache
    ├── coverage_analyzer.py          # Orchestrator: diff → feature → GitNexus → tests
    ├── impact_report.py             # ImpactReport Pydantic model, ADF builder
    ├── regression_planner.py         # Test-type inference, file ranking
    └── cli.py                       # impact-ticket, impact-mr, impact-feature

webhook-receiver/src/webhook_receiver/
├── impact.py                        # NEW: impact analysis DBOS workflow
└── api/app.py                       # MODIFIED: extend handle_merge_request

code-daily-scan/
└── feature_resolver.py              # MODIFIED: load feature-map.yaml at startup
                                      (fallback to embedded defaults if absent)
```

## Risks / Trade-offs

- **[Feature-map drift]**: If a new directory is not in `feature-map.yaml`, it silently falls to `feature.others`. The report's `unmapped_paths` list surfaces new directories so the team can update the YAML.
- **[GitNexus index staleness]**: GitNexus re-indexes on-demand; renamed symbols won't be found. Warn if >20% of symbols are missing.
- **[Jira comment explosion]**: Many MR merges on one ticket accumulate comments. The comment is idempotent by MR IID — re-analysis updates the existing comment.
- **[GitNexus v8 SIGABRT on large repos]**: On `poems-mobile3-ios` (75K symbols, 10M edges), the Node.js process grows its v8 heap unboundedly during BFS traversal, eventually crashing with SIGABRT before the Python-side 30-second timeout fires. The `--summary-only --limit 20 --depth 1` flags mitigate this. **`--depth 1` is the dominant mitigation** — at `--depth 2` the BFS walks millions of edges from every depth-1 caller regardless of `--limit`. Monitor stderr for exit code 134 (SIGABRT) and for `error: unknown option` errors (suggests a flag we prescribed doesn't exist on the installed CLI version). If the crash recurs, skip GitNexus for these repos and rely solely on base-module escalation.
- **[GitNexus subprocess overhead]**: Each symbol triggers a subprocess call. For MRs with 20+ changed symbols, this could be slow. The GitNexus cache (SQLite, TTL 1h) mitigates repeated calls on the same symbols.
- **[Debouncer merging open+merge actions]**: A rapid `open → update → merge` sequence within 60s is debounced to one dispatch. This is correct for impact analysis (we only want the final merged state), but means the `open` action does not trigger ai-review if `merge` arrives within 60s. This is acceptable because the ai-review trigger on `open` is a best-effort review, not a requirement.
- **[No `tdt-core` GitNexus wrapper]**: The subprocess call is stable but not formally typed. If GitNexus CLI output format changes, the parser breaks. Watch for GitNexus CLI updates.

## Migration Plan

1. **Add `get_mr_diff()` to tdt-core**: thin wrapper over `python-gitlab`. Ships first so both CLI and webhook can use it.
2. **Create `feature-map.yaml`**: populate from the existing `code-daily-scan` taxonomy. Validate that all 11 features are covered.
3. **Refactor `code-daily-scan/feature_resolver.py`**: load YAML at startup, fall back to embedded defaults for backward compat. Run existing tests.
4. **Ship the SDK** (`jira-skill/impact/`): implement `feature_map.py`, `ticket_mr_resolver.py`, `gitnexus_impact.py`, `coverage_analyzer.py`, `impact_report.py`. Add unit tests. CLI is independently usable.
5. **Wire up webhook**: extend `handle_merge_request` with `action == "merge"` branch. Feature-gated with `JIRA_IMPACT_WEBHOOK_ENABLED=false` (default off).
6. **Deploy to dev**: CLI first, then webhook enabled in dev, then production.

**Rollback**: Set `JIRA_IMPACT_WEBHOOK_ENABLED=false`. The SDK and CLI continue independently. No data destroyed.

## Subsequent Changes

### 2026-06-27 — Impact Analysis Hardening

Four correctness fixes derived from live evaluation against MR 23433 (`pspl/poems-mobile3-android`):

1. **Case-insensitive `coverage_gaps` substring match** — Android modules use camelcase source but lowercase directory paths (`corporateaction/`), so a literal `module in file_path` check produced false-positive coverage gaps. Now uses `module.lower() in file_path.lower()`.
2. **Real `duration_ms` capture** — `_run_pipeline` in `webhook-receiver/impact.py` was hardcoding `duration_ms=0`. Now wraps `analyze_diff(...)` in `time.monotonic()` and threads the result through `build_impact_report(..., duration_ms=...)`.
3. **Drop path-as-symbol fallback** — `extract_symbols_from_diff` returned `[filename]` when no symbols were extracted, polluting `at_risk_modules` for config/doc files. Now returns `[]`; the staleness threshold handles the empty input gracefully.
4. **Extend `_SYMBOL_REGEX` to Kotlin/Swift keywords** — Added `fun `, `internal fun`, `protected fun`, `object ` (Kotlin) and `extension `, `protocol ` (Swift) to keep line-level regex in sync with `_HUNK_CONTEXT_PATTERN`.

Spec: `openspec/changes/impact-analysis-hardening/`.
