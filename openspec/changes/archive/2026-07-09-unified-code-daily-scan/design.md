# design.md

## Overview

Refactor `android-scan-agent` into a platform-agnostic `code-daily-scan` with plugin-based architecture. Android and iOS share the core scanning, worktree, and Sheets writing logic; only the platform-specific layer (rules, scopes, tab mapping) differs.

## Architecture

```
code-daily-scan/
├── src/code_daily_scan/           # Platform-agnostic core
│   ├── __init__.py
│   ├── models.py                 # Finding, RulePattern, ScanResult, WorktreeSession
│   ├── config.py                # ~/.tdt/code-daily-scan.yaml loader + legacy fallback
│   ├── plugins.py              # PlatformPlugin protocol + registry
│   ├── orchestrator.py          # ScanOrchestrator
│   ├── orchestrator_mr.py      # MrScanOrchestrator (unchanged from android-scan-agent)
│   ├── worktree.py             # WorktreeManager (from android-scan-agent)
│   ├── phase3.py                # Phase3Processor, GitNexusEnricher, TokenBudget
│   ├── scheduler.py            # Cron scheduling helpers
│   ├── health.py              # Health reporting, monthly cost tracking
│   ├── locks.py               # Lockfile acquisition/release
│   ├── retry.py               # Exponential backoff retry
│   ├── gitlab_mr.py           # GitLab MR integration
│   ├── cli.py                 # Typer CLI with --platform flag
│   ├── scanners/
│   │   ├── __init__.py
│   │   ├── grep_scanner.py   # RipgrepRunner, RulePatternLoader, GrepScanner
│   │   └── grep_rules.py     # Composite/cleanup rule configs (C1/C5/C6, L4/L5)
│   └── sheets/
│       ├── __init__.py
│       ├── mapper.py           # SheetMapper, finding_to_sheet_row
│       ├── writer.py          # tdt-sheets backend (from android-scan-agent)
│       └── sheet_mr.py       # MR tab writing (from android-scan-agent)
├── plugins/
│   ├── __init__.py           # Plugin registry (PLUGINS dict)
│   ├── android/               # Android plugin
│   │   ├── __init__.py
│   │   ├── plugin.py         # AndroidPlugin class
│   │   ├── rules_loader.py   # Loads from docs/rules/categories/*.md
│   │   ├── tabs.py          # 15-module tab mapping
│   │   └── scopes.py        # Default scopes + coverage levels
│   └── ios/                  # iOS plugin
│       ├── __init__.py
│       ├── plugin.py         # IOSPlugin class
│       ├── rules_loader.py   # Parses Markdown rules
│       ├── tabs.py          # Category-based tab mapping
│       └── scopes.py        # Default scopes + coverage levels
├── config/
│   └── rule_patterns.yaml   # Fallback defaults
├── tests/
├── scripts/
│   └── deploy.sh             # Deployment script (follows ai-review pattern)
└── pyproject.toml
```

## Key Design Decisions

### 1. Reuse Existing Core

Modules copied verbatim from `android-scan-agent`:
- `worktree.py`, `phase3.py`, `locks.py`, `retry.py`, `gitlab_mr.py`
- `orchestrator_mr.py`, `sheets/writer.py`, `sheets/sheet_mr.py`

Modules requiring changes:
- `cli.py` — add `--platform` flag, plugin routing
- `orchestrator.py` — accept `PlatformPlugin`, inject scanner_classes
- `config.py` — load from `~/.tdt/code-daily-scan.yaml` (no legacy fallback)
- `plugins.py` — `PlatformPlugin` protocol + registry
- `scanners/grep_scanner.py` — use plugin's `supported_extensions`
- `sheets/mapper.py` — delegate `resolve_tab()` to plugin

### 2. Dynamic Rule Loading from Worktree

Rules are read from the target repo's worktree at scan time:

| Platform | Source path |
|----------|------------|
| Android | `{worktree}/docs/rules/categories/*.md` |
| iOS | `{worktree}/docs/technical-debt-scan/categories/*.md` |

### 3. PlatformPlugin Protocol

```python
class RulesLoader(Protocol):
    supported_extensions: tuple[str, ...]
    def load(self, root: Path) -> list[RulePattern]: ...

class PlatformPlugin(Protocol):
    name: str
    supported_extensions: tuple[str, ...]
    default_scopes: list[str]
    rules_loader_cls: type[RulesLoader]
    scanner_classes: tuple[type[GrepScanner], ...]
    composite_rule_min_matches: dict[str, int]
    cleanup_rule_pairs: dict[str, tuple[str, str]]

    def resolve_tab(self, file_path: str) -> str: ...
    def resolve_scope(self, file_path: str) -> str: ...
    def resolve_finding_tab(self, finding: Finding) -> str: ...
```

### 4. Plugin Registry

```python
PLUGINS: dict[str, PlatformPlugin] = {
    "android": AndroidPlugin(),
    "ios": IOSPlugin(),
}
```

### 5. MR Scan Contract

Preserved intact from android-scan-agent:
- `scan-mr` accepts `--mr-iid`, optional `--project`, `--dry-run`, `--post-comment`
- Project inferred from repo's `origin` remote if omitted
- `MrInfo.tab_name` follows `MR-{project-slug}-{iid}`
- Test paths excluded: `/androidTest/`, `/test/`, `/androidTestUtils/`
- Finding paths are workspace-relative
- MR tab includes diff hunk in `MR Context` column

## Rule Loading Format

### Android Rules (`docs/rules/categories/*.md`)

Rules use Markdown with bullet patterns (no fenced code blocks in patterns):

```markdown
## C1 - ViewPager2 stores fragment instances and reuses stale fragments

- Priority: `P0`
- Category: `Crash`
- Why it matters: Reusing fragment instances...
- Detection patterns:
  - `ArrayList<BaseFragment>`
  - `setListFragment(`
  - `createFragment(position) = mListPagers[position]`
- Recommended solution: Store page metadata only...
```

Parser extracts:
- `rule_id`: `C1` (from `## C1 - Title`)
- `priority`: `P0` (from `- Priority: \`P0\``)
- `category`: `Crash` (from file convention — `crash-runtime.md` → C* → Crash)
- `pattern`: each bullet under `- Detection patterns:` as separate entry
- `title`: text after dash in heading
- `description`: `- Why it matters:` section

### iOS Rules (`docs/technical-debt-scan/categories/*.md`)

Rules use the **same bullet-line convention** as Android rules:

```markdown
## M1 — Strong capture of `self` in long-lived closure

- Priority: `P0`
- Category: `Memory Leak`
- Why it matters: Long-lived closures can keep screens alive indefinitely.
- Detection patterns:
  - `self.` referenced inside an escaping closure without `[weak self]`
  - closures assigned to properties or passed into services
- Recommended solution: Use `[weak self]` and guard/unwarp safely.
```

Parser extracts:
- `rule_id`: `M1` (from `## M1 — Title`)
- `priority`: `P0` (from `- Priority: \`P0\``)
- `category`: `Memory Leak` (from `- Category: \`Memory Leak\``)
- `pattern`: each bullet under `- Detection patterns:` as separate entry
- `title`: text after `## RULE_ID` in heading (em-dash for iOS: `M1 — Title`)
- `description`: `- Why it matters:` section

## Module Responsibilities

### Core Modules (Reused)

| Module | Source | Purpose |
|--------|--------|---------|
| `worktree.py` | android-scan-agent | Git worktree lifecycle |
| `phase3.py` | android-scan-agent | GitNexusEnricher, TokenBudget, Phase3Processor |
| `locks.py` | android-scan-agent | Best-effort lockfile with TTL |
| `retry.py` | android-scan-agent | Exponential backoff retry |
| `gitlab_mr.py` | android-scan-agent | GitLab MR fetch via `GitlabClientFactory` |
| `sheets/writer.py` | android-scan-agent | tdt-sheets backend |
| `sheets/sheet_mr.py` | android-scan-agent | MR tab rendering |
| `orchestrator_mr.py` | android-scan-agent | MR-scoped scan pipeline |

### Plugin Modules (New)

| Module | Platform | Purpose |
|--------|----------|---------|
| `plugins/android/plugin.py` | Android | Platform configuration |
| `plugins/android/rules_loader.py` | Android | Parse `docs/rules/categories/*.md` |
| `plugins/android/tabs.py` | Android | Feature + infrastructure tab mapping |
| `plugins/android/scopes.py` | Android | Default scopes + coverage |
| `plugins/ios/plugin.py` | iOS | Platform configuration |
| `plugins/ios/rules_loader.py` | iOS | Parse Markdown rules |
| `plugins/ios/tabs.py` | iOS | Feature-based tab mapping |
| `plugins/ios/scopes.py` | iOS | Default scopes + coverage |

## Sheets Output

### Android Tab Structure (21 tabs)

Summary | Auth | Home | WatchList | Market | Trade | Community | Me/Settings | Deposit/Withdraw | Form | Others | Common | Adapter | Ui | CounterDetail | Network | Extensions | Utils | Viewmodels | Dashboard | Infrastructure | Local | App

Path-based tab resolution: file path → feature or module → tab name.

### iOS Tab Structure (10 feature tabs + Summary)

Summary | Auth | Home | WatchList | Market | Trade | Community | Me/Settings | Deposit/Withdraw | Form | Others

Feature-based tab resolution: `finding.feature` → tab via `FEATURE_TAB_MAP`.
This is consistent with Android and enables cross-platform feature comparison.

### Column Format (16 columns)

Rule ID | Related Rules | Title | Priority | Category | File Path | Symbol | Issue | Recommended Solution | Solution Review | Impact | Man Day | Status | Jira Ticket | Target Fix | MR Context

## CLI Commands

### Unified `scan` Command

The unified `scan` command supports three modes based on provided options:

#### Daily Scan (no options)
Full repository scan for all modules. Runs on schedule via cron.
```bash
code-daily-scan scan --platform android
code-daily-scan scan --platform ios
```

#### MR Scan (`--mr-iid`)
Scans only files changed in a GitLab Merge Request.
```bash
code-daily-scan scan --platform ios --mr-iid 42 --post-comment
```

#### Branch Scan (`--source-branch`)
Compares source branch against target branch (default: `main`). Uses git worktree.

Changed files only:
```bash
code-daily-scan scan --platform ios \
  --source-branch HuuThanh/Task/EW-Update-PUIComponent \
  --feature "Modules/Profile/Ewallet"
```

Full package (`--scan-full-package`):
```bash
# iOS
code-daily-scan scan --platform ios \
  --source-branch HuuThanh/Task/EW-Update-PUIComponent \
  --feature "Modules/Profile/Ewallet" \
  --scan-full-package

# Android
code-daily-scan scan --platform android \
  --source-branch modules/ewallet/develop_newdesignsystem \
  --feature "com.tdt.pmobile3.ewallet" \
  --scan-full-package
```

### Legacy Commands (Deprecated)

| Command | Replacement |
|---------|--------------|
| `scan-mr` | `scan --mr-iid` |
| `scan-branch` | `scan --source-branch` |

### Mode Comparison

| Mode | Trigger | Files Scanned | Tab Pattern |
|------|---------|---------------|-------------|
| Daily | No trigger | All | Feature-based (see [Tab Routing Contract](#tab-routing-contract) below) |
| MR | `--mr-iid` | Changed in MR | `MR-{project-slug}-{iid}` |
| Branch | `--source-branch` | Changed files | `BRANCH-{branch-slug}` (deterministic — see *Branch-scan tab naming* below) |
| Full Package | `--scan-full-package` | All in feature | `BRANCH-{branch-slug}` or `BRANCH-{branch-slug}-{feature-slug}` if `--feature` given |

The branch-scan tab name is **deterministic and stable across runs** — the
first run creates the tab, every subsequent run reuses it. The exact
slug rules and idempotence contract are specified in
[`specs/code-daily-scan-core/spec.md`](../specs/code-daily-scan-core/spec.md)
under the *Branch-Scan Tab Name Is Deterministic And Reusable*
requirement. In summary:

* `{branch-slug}` is the result of
  `re.sub(r"[^A-Za-z0-9._-]+", "-", source_branch).strip("-_")`. Dots,
  underscores and existing dashes survive so semver branches and
  Jira-suffixed branch names round-trip readably.
* `{feature-slug}` is the TitleCase concat of the meaningful segments
  of the feature string, with Android package markers (`com`, `tdt`,
  `pmobile3`, `app` …) and iOS module markers (`modules`, `feature`)
  dropped. iOS slash form, iOS bare form, Android dot form and Android
  slash form all collapse to the same canonical slug.
* No `--feature`: `BRANCH-{branch-slug}`. With `--feature`:
  `BRANCH-{branch-slug}-{feature-slug}`.

## Config Schema

```yaml
# ~/.tdt/code-daily-scan.yaml
android:
  spreadsheet_id: "1DSaaBD3-..."
  repo_path: "~/Developer/tdt/poems-mobile3-android"
ios:
  spreadsheet_id: "1DSaaBD3-..."
  repo_path: "~/Developer/tdt/poems-mobile3-ios"
defaults:
  cron: "0 7 * * *"
  timezone: "Asia/Ho_Chi_Minh"
```

Config precedence:
1. CLI flags
2. Env vars (`ANDROID_SCAN_SPREADSHEET_ID`, `IOS_SCAN_SPREADSHEET_ID`)
3. Config file (`~/.tdt/code-daily-scan.yaml`)
4. Defaults

> **Note (2026-06-14):** The previous "Legacy fallback
> (`~/.tdt/config.yaml` `android_scan:` section) — removed after 30-day
> migration" tier has been removed from the runtime path. Operators
> with a pre-existing `android_scan` block MUST run
> `code-daily-scan migrate-config` once to import it into the new
> file. See `tasks.md` → Phase 10.

## Testing Strategy

### Unit Tests
- `test_grep_scanner.py` — ripgrep parsing, composite rules, cleanup rules
- `test_android_plugin.py` — rules_loader (bullet pattern parsing), tab resolution
- `test_ios_plugin.py` — markdown parsing (bullet patterns), tab resolution
- `test_orchestrator.py` — plugin injection, scanner list

### Integration Tests
- `scan --platform android --dry-run`
- `scan --platform ios --dry-run`
- `scan-mr --platform ios --mr-iid N`

### Mock Tests
- `GrepScanner` with mocked `RipgrepRunner`
- `GitNexusEnricher` with mocked subprocess

## Deployment

Follows ai-review pattern with `scripts/deploy.sh`:
1. Copy source to `deployments/code-daily-scan/app/`
2. Copy path dependencies (tdt-core, tdt-sheets)
3. Verify snapshot
4. Run `uv sync`
5. Generate LaunchAgent plist
6. Restart service
7. Health check

## Rollout Plan

| Phase | Description |
|-------|-------------|
| Phase 0 | Extract core to `code-daily-scan`, add Android plugin |
| Phase 1 | Add iOS plugin, verify iOS scan output |
| Phase 2 | Deprecate `android-scan-agent`, add warning |
| Phase 3 | Archive `android-scan-agent` after 30-day migration |

## Migration from android-scan-agent

```bash
# Before
android-scan-agent scan

# After
code-daily-scan scan --platform android
```

Config: `~/.tdt/config.yaml` `android_scan:` → `~/.tdt/code-daily-scan.yaml` `android:`
