# proposal.md

## Why

Android and iOS code quality scanning currently live in separate, platform-specific implementations:

- **`android-scan-agent`** — daily scan, MR-scoped scan, Google Sheets output, ripgrep-based
- **iOS scan** — manual tooling, rules documented in `poems-mobile3-ios/docs/technical-debt-scan/categories/`

The android-scan-agent is well-designed but tightly coupled to Android conventions (Kotlin/Java paths, Android module tab names, `C*`/`L*`/`P*` rule IDs). Creating a separate iOS agent would duplicate orchestrator, worktree, scanner, and Sheets writer logic while only changing the platform-specific layer.

Additionally, the live rule books already live in the target repos, but in two different places: Android rules are maintained under `poems-mobile3-android/docs/rules/categories/*.md`, while iOS rules live under `poems-mobile3-ios/docs/technical-debt-scan/categories/*.md`. The current android-scan-agent still depends on a compiled `config/rule_patterns.yaml` snapshot, so the unified scanner should read the repo markdown at scan time and fall back to the bundled snapshot only when repo docs are absent.

## What Changes

### Architecture: Core + Platform Plugins

Refactor `android-scan-agent` into a platform-agnostic `code-daily-scan` with the following structure:

```
code-daily-scan/
├── src/code_daily_scan/           # Platform-agnostic core
│   ├── __init__.py
│   ├── cli.py                     # unified CLI: scan --platform android|ios
│   ├── models.py                  # Finding, RulePattern, ScanResult (shared)
│   ├── config.py                  # ~/.tdt/code-daily-scan.yaml loading + legacy config fallback
│   ├── orchestrator.py            # ScanOrchestrator (shared)
│   ├── orchestrator_mr.py         # MrScanOrchestrator (shared, unchanged)
│   ├── worktree.py                # WorktreeManager (shared)
│   ├── phase3.py                  # GitNexus enrichment and post-processing (shared)
│   ├── locks.py                   # lockfile + TTL (shared)
│   ├── retry.py                   # retry/backoff (shared)
│   ├── gitlab_mr.py               # GitLab MR integration (shared)
│   ├── scanners/
│   │   ├── __init__.py
│   │   └── grep_scanner.py        # RipgrepRunner, RulePatternLoader, GrepScanner (shared)
│   └── sheets/
│       ├── __init__.py
│       ├── mapper.py              # SheetMapper, finding_to_sheet_row (shared)
│       ├── writer.py              # tdt-sheets backend (shared)
│       └── sheet_mr.py            # MR tab writing (shared)
├── plugins/
│   ├── __init__.py                # Plugin registry
│   ├── android/
│   │   ├── __init__.py
│   │   ├── plugin.py              # AndroidPlugin implementation
│   │   ├── rules_loader.py        # loads from docs/rules/categories/*.md
│   │   ├── tabs.py                # Android module -> tab resolution
│   │   └── scopes.py              # default scan scopes + coverage levels
│   └── ios/
│       ├── __init__.py
│       ├── plugin.py              # IOSPlugin implementation
│       ├── rules_loader.py        # loads from docs/technical-debt-scan/categories/*.md
│       ├── tabs.py                # iOS feature -> tab resolution
│       └── scopes.py              # default scan scopes + coverage levels
└── config/
    └── rule_patterns.yaml         # fallback snapshot when repo docs are absent
```

### Key Design Decisions

#### 1. Dynamic Rule Loading from Target Repo

Rules are read from the target repo's worktree at scan time, with platform-specific paths:

| Platform | Source path |
|----------|------------|
| Android | `{worktree}/docs/rules/categories/*.md` |
| iOS | `{worktree}/docs/technical-debt-scan/categories/*.md` |

The `rules_loader.py` in each plugin parses these files into `RulePattern` objects. This means:
- Rules update automatically when the repo branch advances — no release needed
- Android and iOS share the same loader contract, but each parses its own markdown dialect and source path
- Fallback to `config/rule_patterns.yaml` if repo docs are missing or incomplete

#### 2. Worktree-Based Scanning

Each scan creates/uses a worktree for the target repo:

```python
# plugin-specific worktree naming
WorktreeManager(repo_path, branch="main", worktree_root=...)
# Android: {parent}/.worktrees/poems-mobile3-android/code-daily-scan-{timestamp}
# iOS:    {parent}/.worktrees/poems-mobile3-ios/code-daily-scan-{timestamp}
```

Worktrees are cleaned up after each scan. This mirrors the android-scan-agent pattern exactly.

#### 3. Separate Spreadsheets per Platform

Spreadsheet IDs are configured in `~/.tdt/code-daily-scan.yaml`:

```yaml
android:
  spreadsheet_id: "1DSaaBD3-..."
ios:
  spreadsheet_id: "1DSaaBD3-..."
```

Each platform writes to its own spreadsheet. Tab structure is platform-specific:
- **Android:** Auth, Home, Trade, WatchList, etc. (existing 15-module split)
- **iOS:** Auth, Home, Trade, Market, Community, Me/Settings, etc. (10 feature-based tabs)

#### 4. Unified CLI

```bash
# Daily scan
code-daily-scan scan --platform android
code-daily-scan scan --platform ios

# MR scan (changed files only)
code-daily-scan scan --platform android --mr-iid 23318
code-daily-scan scan --platform ios --mr-iid 42

# Branch scan (changed files only)
code-daily-scan scan --platform ios \
  --source-branch HuuThanh/Task/EW-Update-PUIComponent \
  --feature "Modules/Profile/Ewallet"

# Branch scan (full package - all files in feature)
code-daily-scan scan --platform ios \
  --source-branch HuuThanh/Task/EW-Update-PUIComponent \
  --feature "Modules/Profile/Ewallet" \
  --scan-full-package

# Health check
code-daily-scan health --platform ios
# Sheet validation
code-daily-scan sheet-setup --platform android
```

MR scans and branch scans are the same scanner pipeline, scoped to changed files, with workspace-relative findings, optional MR comments, and dedicated tabs.

#### 5. Plugin Interface

Each platform implements `PlatformPlugin`:

```python
class PlatformPlugin(Protocol):
    name: str
    supported_extensions: tuple[str, ...]
    default_scopes: list[str]
    module_tab_map: dict[str, str]
    rules_loader_cls: Type[RulesLoader]
    composite_rule_min_matches: dict[str, int]
    cleanup_rule_pairs: dict[str, tuple[str, str]]

    def resolve_tab(self, file_path: str) -> str: ...
    def resolve_scope(self, file_path: str) -> str: ...
```

This allows:
- Scanner core to remain unchanged
- New platforms (Flutter, React Native) to be added by implementing the protocol
- Each plugin to have its own rules, scopes, and tab mapping

#### 6. Rule Format (Unchanged from android-scan-agent)

Rules are markdown documents in the target repos, parsed into the shared `RulePattern` model.

- Android source: `poems-mobile3-android/docs/rules/categories/*.md`
- iOS source: `poems-mobile3-ios/docs/technical-debt-scan/categories/*.md`
- Bundled fallback: `config/rule_patterns.yaml`

The fallback snapshot stays YAML because it is the compiled, release-independent safety net, not the source of truth.

## Capabilities

- **Daily scan:** Full repository scan for all modules
  - `code-daily-scan scan --platform android`
  - `code-daily-scan scan --platform ios`
- **MR-scoped scan:** Scan only files changed in a GitLab MR
  - `code-daily-scan scan --platform android --mr-iid 23318`
  - `code-daily-scan scan --platform ios --mr-iid 42`
- **Branch scan (changed files):** Compare branches and scan only changed files
  - `code-daily-scan scan --platform ios --source-branch feat/xyz --feature "Modules/Profile/Ewallet"`
- **Branch scan (full package):** Scan entire feature package in a branch
  - `code-daily-scan scan --platform ios --source-branch feat/xyz --feature "Modules/Profile/Ewallet" --scan-full-package`
- **Health check:** Verify scaffold health and last run status
  - `code-daily-scan health --platform ios`
- **Sheet validation:** Validate Google Sheets write access
  - `code-daily-scan sheet-setup --platform android`

## Impact

**Scope:** New `code-daily-scan` repo; `android-scan-agent` archived after migration.

### New files

- All files in `src/code_daily_scan/` (core, platform-agnostic)
- `plugins/android/` (Android plugin)
- `plugins/ios/` (iOS plugin)
- `config/rule_patterns.yaml` (fallback defaults)

### Modified files (none during Phase 1)

- `android-scan-agent` remains unchanged until iOS plugin is verified
- Migration: rename `android-scan-agent` → `code-daily-scan`, extract plugin

### Deprecations

- `android-scan-agent` deprecated in favor of `code-daily-scan --platform android`
- `android-scan-agent` scan command maps to `code-daily-scan scan --platform android`

### Dependencies (existing)

- `tdt-core[gitlab]` — GitLab client factory, env loading
- `tdt-sheets` — Google Sheets writer with 3-level auth fallback
- `agent-core` — scheduler integration
- `typer>=0.25.1` — CLI framework

### No impact on

- `ai-review` (shares tdt-core but no code changes)
- `tdt-core` (no new APIs needed)
- `jira-skill`
- Daily Jira reporting workflows
