# Jira Impact Analysis — QA Regression Coverage

## Why

When code lands in a repo, QA and Dev teams need to answer: **what must I test?** Today this is tribal knowledge — the developer who merged the MR knows the scope, but there's no structured, repeatable path from "this code changed" to "here are the test cases you need to run." We want to close that gap.

A developer merges an MR, or a QA engineer opens a ticket, and within seconds gets a structured test coverage recommendation that covers:
- Which **features** are affected (derived from directory/module mapping, aligned with the existing `code-daily-scan` feature taxonomy)
- Which **other modules** are at risk (via GitNexus blast-radius)
- Which **test files** cover the affected code (via GitNexus test-caller edges)
- What **test types** are appropriate (unit, integration, smoke, regression)

This prevents regressions from slipping through, ensures feature test coverage is consistent across the team, and creates an auditable link from code change to test coverage.

## What Changes

### Entry Point A — GitLab MR Merge Webhook

When a GitLab MR is merged, the existing `/gitlab-webhook` handler in `webhook-receiver` already receives the event. We extend the `action` filter to also handle `action: merge`:

1. When `object_attributes.action == "merge"`, run the impact analysis pipeline (instead of skipping, as today)
2. Extract the merged MR's **diff** (changed files + line ranges) via GitLab API
3. Resolve each changed file to its **feature** via `feature-map.yaml` (longest-prefix match)
4. Run **GitNexus impact analysis** on changed symbols to find downstream callers and test files
5. Emit a structured `ImpactReport`
6. **Post to Jira** ticket comment via `add_comment_adf()`

This runs via the existing DBOS debouncer pattern — the merge hook fires, the debouncer gates duplicate rapid-fire events, and `handle_merge_request` dispatches to a DBOS step that runs the analysis.

### Entry Point B — On-demand CLI

```bash
cd jira-skill && uv run python -m jira_skill impact-ticket SR-3588
```

The CLI:
1. Reads the Jira ticket's **comments** to extract all referenced GitLab MR URLs
2. Fetches each MR's diff via GitLab API
3. Applies the same feature-mapping + GitNexus analysis pipeline
4. Outputs a structured report (JSON to stdout)

## Alignment with Existing Systems

### Feature Taxonomy

The system reuses the **11-feature taxonomy** already defined in `code-daily-scan/feature_resolver.py`:

```
Deposit/Withdraw, Trade, Auth, Home, WatchList, Form, Market, Community,
Me/Settings, Common, Others (fallback)
```

`code-daily-scan` uses an ordered Python rule-list (`FEATURE_RULES`) with platform-aware sub-rules (`ANDROID_ONLY_RULES`, `IOS_ONLY_RULES`). This change introduces `tdt-meta/feature-map.yaml` as the **canonical source of truth** that both `code-daily-scan` and `jira-impact` read at runtime — replacing the hardcoded rule list with a git-tracked YAML file. `feature_resolver.py` retains its embedded defaults as a fallback for backward compatibility.

### GitLab Integration

`jira-skill` already has a mature `gitlab/` subpackage (`gitlab/models.py`, `gitlab/mr_sync.py`, `gitlab/webhook_handler.py`) built on `python-gitlab`. This change extends it with:
- MR diff fetching (`GET /projects/{id}/merge_requests/{iid}/diffs`)
- Merge-commit SHA extraction

### Jira Integration

`jira-skill` already has `issue/comments.py` for comment fetching and `PatchedJira.add_comment_adf()` for ADF comment posting. The new `ticket_mr_resolver.py` extends these patterns.

## Feature Map (Directory Convention)

The `feature-map.yaml` lives in `tdt-meta/`. It maps directory prefixes (or substring patterns) to feature names. The schema supports two entry types:

```yaml
feature_map:
  # Longest-prefix entries — first match wins. Path is a directory prefix.
  - path: "Pmobile3/Modules/Auth/"
    tags: [feature.auth, ios]
  - path: "Pmobile3/Modules/Trade/"
    tags: [feature.trade, ios]
  - path: "com/tdt/pmobile3/ui/screens/trade/"
    tags: [feature.trade, android]
  - path: "Pmobile3/Core/"
    tags: [feature.common, ios]
  - path: "com/tdt/pmobile3/common/"
    tags: [feature.common, android]

  # Substring entries (mirrors FEATURE_RULES in code-daily-scan).
  # Used when feature identity comes from a token in the path rather than a directory.
  - pattern: "deposit|withdraw|funding|ewallet|digitalasset"
    tags: [feature.deposit-withdraw]
  - pattern: "auth|login|biometric|mfa|otp|password"
    tags: [feature.auth]
  - pattern: "trade|orderview|positionview"
    tags: [feature.trade]
  - pattern: "market|quotes|stock|counter|globalsearch"
    tags: [feature.market]
  - pattern: "watchlist"
    tags: [feature.watchlist]
  - pattern: "home/|dashboard/|tabbar"
    tags: [feature.home]
  - pattern: "profile|setting|notification|accountdetail"
    tags: [feature.me-settings]
  - pattern: "community|discover|promo|news/"
    tags: [feature.community]
  - pattern: "form|cdp|chatgpt|smartpark|egiro"
    tags: [feature.form]
  - pattern: "ui/common|extensions/|network/|adapter/|model/|res/"
    platform: android
    tags: [feature.common, android]
  - pattern: "modules/common|core/|services/|common/|app/|model/"
    platform: ios
    tags: [feature.common, ios]

base_modules:
  - feature.common

fallback:
  tag: feature.others
```

The schema supports two entry types: `path` (longest-prefix directory match) and `pattern` (substring match against the normalized path). The `pattern` form mirrors the existing `FEATURE_RULES` from `code-daily-scan/feature_resolver.py`. The `platform` filter is optional — when set, the entry only applies to paths whose `_normalize_path()` indicates that platform.

**Impact rules:**
- `feature.common` changes (with net line delta > 3) trigger **all features** on the affected platform
- Named feature changes trigger GitNexus blast-radius analysis
- Unmapped paths → `feature.others` (per the `fallback` config) with a warning to update `feature-map.yaml`

## Capabilities

### New Capabilities

- `jira-impact-analysis-sdk`: SDK package at `jira-skill/src/jira_skill/impact/`:
  - `feature_map.py` — YAML loader (reads `tdt-meta/feature-map.yaml`), longest-prefix resolver, base-module propagation
  - `ticket_mr_resolver.py` — Jira comment parser (reuses `issue/comments.py` patterns), MR URL regex extraction, MR diff fetcher
  - `gitnexus_impact.py` — subprocess-based GitNexus wrapper: symbol extraction, `gitnexus impact` call, result parsing, SQLite cache
  - `coverage_analyzer.py` — orchestrator: diff → feature → GitNexus → test mapping
  - `impact_report.py` — `ImpactReport` Pydantic model, Jira ADF comment builder
  - `regression_planner.py` — test-type inference from feature bucket + test-file path heuristics

- `jira-impact-webhook-extension`: extend the existing `/gitlab-webhook` handler in `webhook-receiver` to handle `action: merge` — adds impact analysis to the existing MR debouncer/DBOS pipeline

- `feature-map-yaml`: canonical configuration at `tdt-meta/feature-map.yaml` — shared between `code-daily-scan` (read) and `jira-impact` (read)

- `tdt-core-gitlab-mr-diff`: add `get_mr_diff(project_path, mr_iid)` helper to `tdt-core` (thin wrapper over `python-gitlab`) so both `jira-skill` and `webhook-receiver` use the same API

### Modified Capabilities

- `webhook-gitlab-mr-hook`: extend `handle_merge_request` to also dispatch impact analysis when `action == "merge"` — currently only `open`, `update`, `reopen` trigger ai-review dispatch
- `code-daily-scan-feature-resolver`: `feature_resolver.py` reads `feature-map.yaml` at runtime instead of using the hardcoded `FEATURE_RULES` list; YAML becomes the source of truth

## Impact

### Code

- `tdt-meta/feature-map.yaml` — new: canonical feature-to-directory mapping
- `jira-skill/src/jira_skill/impact/` (new package, ~1000 lines):
  - `__init__.py` (~20 lines)
  - `feature_map.py` (~120 lines)
  - `ticket_mr_resolver.py` (~150 lines)
  - `gitnexus_impact.py` (~180 lines)
  - `coverage_analyzer.py` (~200 lines)
  - `impact_report.py` (~200 lines)
  - `regression_planner.py` (~120 lines)
  - `cli.py` (~100 lines)
- `webhook-receiver/src/webhook_receiver/api/app.py` — extend `handle_merge_request` with `action == "merge"` branch
- `tdt-core/src/tdt_core/clients/gitlab.py` — add `get_mr_diff(project_path, mr_iid)` helper
- `code-daily-scan/feature_resolver.py` — refactor to read `feature-map.yaml` instead of hardcoded rules (backward-compat: fall back to rules if YAML missing)

### Configuration

- `feature-map.yaml` lives in `tdt-meta/` — git-tracked, updated when new features/dirs are added
- Webhook env: `JIRA_IMPACT_WEBHOOK_ENABLED=true|false` (default `false`)
- CLI env: reuses `JIRA_*`, `GITLAB_*`, `GITLAB_PAT` from `~/.tdt/.env`

### Non-Goals

- This is NOT a test case management system — we recommend, not track
- We do NOT auto-run tests; we emit recommendations for human execution
- We do NOT change GitLab/Jira configurations programmatically
- We do NOT infer features from commit messages (explicit YAML mapping only)
- No changes to iOS/Android native build tooling
- Slack integration is out of scope for v1
