# design.md

## Context

`code-daily-scan` runs daily across the entire `poems-mobile3-android` codebase, grouping findings into module tabs (Auth, Home, Trade, etc.) in a Google Sheet. It uses `GrepScanner` backed by markdown rule files to surface code quality issues.

When a developer opens an MR, two things are missing:

1. **Scoped signal**: A quick code-quality scan on just the changed files, not the whole repo
2. **MR-native output**: Findings written to a per-MR sheet tab, not buried in daily scan tabs

Separately, `ai-review` already handles LLM-powered MR reviews and uses `python-gitlab` via `GitlabClientFactory.from_env()` to fetch MR diffs. This change reuses that same factory and the `merge_request.changes()` API, but redirects output to a spreadsheet tab instead of an LLM prompt.

## Goals / Non-Goals

### Goals
- Add `scan-mr` and `scan-branch` commands to `code-daily-scan` CLI
- Scope scans to MR/branch-changed files only
- Support `--feature` filter to scan specific packages (e.g., `com/tdt/pmobile3/ewallet`)
- Write findings to a per-MR/branch spreadsheet tab
- Use git worktree to checkout the correct branch for scanning
- Optionally post a minimal GitLab MR comment (opt-in flag)
- Reuse existing scanner classes without modification
- Use `GitlabClientFactory.from_env()` (python-gitlab) for all GitLab API calls
- Write file paths as workspace-relative

### Non-Goals
- Duplicate scanner logic — reuse existing scanner classes
- Full LLM review — that's `ai-review`'s domain
- Automatic tab cleanup on MR close/merge
- Cross-MR aggregation dashboard
- Modify `ai-review` code

## Decisions

### Decision 1: How to get MR-changed file list

**Option A: GitLab API `merge_request.changes()`** (via `python-gitlab`)
- Fetches full diff content per file
- Works without local repo checkout
- Requires `GITLAB_PAT` (already available via `GitlabClientFactory`)
- Returns `{"changes": [{"diff": "...", "new_path": "...", "old_path": "..."}]}`

**Option B: Local `git diff --name-only` in checked-out repo**
- Fast, no network call
- Requires local repo at correct ref
- Fails if branches aren't fetched

**Option C: `glab mr view {iid} --output json` + local git**
- Uses `glab` CLI which is already in environment
- Mixed network + local approach

**Decision: Option A (GitLab API)** — same pattern as `ai-review`. Works without requiring the local repo to have all branches fetched. The diff content is not needed immediately (scanners read files from disk), only the file path list.

**Rationale:** `ai-review/review_flow/context.py:_load_gitlab_compare()` already uses `merge_request.changes()`. This is the established pattern.

```python
# code_daily_scan/gitlab_mr.py
from tdt_core.clients.gitlab import GitlabClientFactory

client = GitlabClientFactory.from_env().create_client()
client.auth()
project = client.projects.get(project_id)  # numeric ID or path-encoded
mr = project.mergerequests.get(mr_iid)
changes_response = mr.changes()
changed_files = [item["new_path"] for item in changes_response["changes"]]
```

### Decision 2: How to scope scanner to changed files only

**Option A: Subclass `GrepScanner` with path filter**
- Adds `file_filter: Callable[[Path], bool]` to `GrepScanner.scan()`
- Requires modifying scanner interface

**Option B: Wrap `GrepScanner.scan()` with path filter**
- Pass `file_filter` to `GrepScanner.__init__`
- Scanner checks filter before yielding findings
- Minimal interface change

**Option C: Filter findings after scan**
- Scan entire repo, filter findings by `finding.file_path` against changed file set
- Wasteful: scans whole repo, then discards most findings

**Decision: Option B — pass `changed_files: set[str]` to `GrepScanner.__init__`**

The `GrepScanner` already walks the repo tree with `git ls-files`. We intercept the path check: if `changed_files` is set, only yield files in that set.

```python
class GrepScanner:
    def __init__(
        self,
        patterns_path: Path | None = None,
        *,
        changed_files: set[str] | None = None,  # NEW: scope to MR changed files
    ) -> None:
        ...
        self._changed_files = changed_files

    def _file_in_scope(self, path: Path) -> bool:
        if self._changed_files is None:
            return True
        # Normalize to workspace-relative path
        rel = path.relative_to(self._repo_root).as_posix()
        return rel in self._changed_files
```

`MrScanOrchestrator` populates `changed_files` from the GitLab API response.

### Decision 3: How to write findings to the MR tab

**Option A: Reuse `write_scan_findings()` with different `module_tab_map`**
- Pass `{"mr": "MR-23318"}` as `module_tab_map`
- All findings land in one tab named `MR-23318`
- `include_summary=False` (no module-level breakdown needed for MR-scoped scan)

**Option B: New `write_mr_findings()` function in `sheet_mr.py`**
- Dedicated MR tab builder with summary row, MR Context column, priority-sorted findings
- Simpler, single-purpose, avoids polluting the daily scan writer
- Uses `tdt-sheets` `ensure_sheet()` + `batch_clear()` + `batch_write()` for robust tab lifecycle

**Decision: Option B — dedicated `write_mr_findings()` in `sheet_mr.py`**

The MR tab needs different structure from daily tabs (summary row, MR Context, different sorting). A dedicated module is cleaner and avoids coupling between the two output modes. The daily `write_scan_findings()` is unchanged.

```python
# code_daily_scan/sheets/sheet_mr.py
from code_daily_scan.sheets.sheet_writer import write_scan_findings

module_tab_map = {"mr": f"MR-{mr_iid}"}
result = write_scan_findings(
    findings=findings,
    spreadsheet_id=spreadsheet_id,
    module_tab_map=module_tab_map,
    dry_run=dry_run,
    selected_tab=f"MR-{mr_iid}",
    include_summary=False,
)
```

The `SheetMapper` routes all findings to `MR-{IID}` because no file matches the daily module patterns — and even if they do, `selected_tab` overrides to write only to that tab.

### Decision 4: Tab lifecycle

**MR tabs are ephemeral but not auto-cleaned.**

- **Create:** If `MR-{IID}` tab doesn't exist, `tdt-sheets` `batch_write` creates it implicitly (Google Sheets API behavior)
- **Overwrite:** Each `scan-mr` run clears and rewrites the tab — idempotent
- **Cleanup:** No automatic removal on MR close/merge. A separate maintenance command (`scan-mr --cleanup-stale`) can be added later

### Decision 5: MR comment posting (opt-in `--post-comment`)

**Pattern: reuse `GitLabReviewPoster` from `ai-review/gitlab/review_posting.py`**

The `ai-review` poster uses a marker comment (`<!-- mr-auto-review -->`) to find and update its own comments. For `scan-mr`, we use a distinct marker: `<!-- android-scan-mr -->`.

```python
from ai_review.gitlab.review_posting import GitLabReviewPoster

poster = GitLabReviewPoster(project=project_id)
poster.post_or_update(
    mr_iid=mr_iid,
    body=f"Android Scan findings written to sheet: [{count} finding(s)]",
    marker="<!-- android-scan-mr -->",
)
```

**Design note:** `GitLabReviewPoster` is imported from `ai-review`, not copied. Both repos declare `tdt-core[gitlab]` so `python-gitlab` is available. The `ai-review` package is a sibling in the workspace.

If `ai-review` is not installed in the `code-daily-scan` venv, the `--post-comment` feature degrades gracefully with a warning log — it does not fail the whole command.

### Decision 6: Path format — workspace-relative

All `file_path` values in `Finding` are written as **relative to the workspace root** (`poems-mobile3-android/`), not absolute paths.

Example:
```
app/src/main/java/com/tdt/pmobile3/trade/TradeViewModel.kt
```

The `GrepScanner` already stores paths relative to `self._repo_root` (set in `__init__`). No change needed.

### Decision 7: Sheet schema — 16 columns + `MR Context`

The existing 16-column schema is preserved exactly. A 17th column **`MR Context`** is appended, storing the diff snippet that triggered the finding.

```python
# code_daily_scan/sheets/sheet.py
SHEET_COLUMNS: tuple[str, ...] = (
    "Rule ID",
    ...
    "Target Fix in Version",
    "MR Context",  # NEW
)
```

For daily scans (non-MR), `MR Context` column is empty — `Finding` model has no `mr_context` field.

## Data Flow

```
scan-mr --mr-iid 23318 [--post-comment]
│
├─ gitlab_mr.fetch_mr_info(iid, project)
│   └─ GitlabClientFactory.from_env().create_client()
│       └─ project.mergerequests.get(iid).changes()
│           → changed_files: set[str]
│           → mr_info: {title, author, source_branch, target_branch}
│
├─ MrScanOrchestrator(repo_path, changed_files).run()
│   ├─ GrepScanner(patterns_path, changed_files=changed_files).scan()
│   ├─ LifecycleScanner(patterns_path).scan()         ← unchanged (already scoped)
│   ├─ PerformanceScanner(patterns_path).scan()         ← unchanged
│   ├─ ArchitectureScanner(patterns_path).scan()       ← unchanged
│   ├─ SecurityScanner(patterns_path).scan()          ← unchanged
│   └─ Phase3Processor.process(findings, ...)
│       → ScanResult(findings, mr_context={...})
│
├─ sheet_mr.write_mr_findings(result, mr_info)
│   ├─ build_mr_rows(findings)  ← finding_to_sheet_row() + MR Context
│   ├─ ensure_tab_exists(spreadsheet_id, f"MR-{iid}")
│   └─ batch_clear_and_update(tab, rows)
│       → "MR-23318" tab written
│
└─ (optional) GitLabReviewPoster(project).post_or_update(mr_iid, ...)
    → MR comment: "Android Scan: 12 findings → MR-23318 tab"
```

## Risks / Trade-offs

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| MR tab name collision (same IID across projects) | Low | Findings written to wrong tab | Include project slug in tab name: `MR-{project}-{iid}` |
| `ai-review` not installed in `code-daily-scan` venv | Medium | `--post-comment` silently degraded | Log warning, don't fail command |
| Local repo not checked out | N/A | Doesn't matter — GitLab API used for diffs, worktree for scan | Worktree auto-creates detached checkout |
| Large MR (hundreds of files) | Medium | Scan time grows linearly | GrepScanner is fast; add `--max-files` guard if needed |
| Worktree branch not in local repo | Medium | `git worktree add` may fail | `--source-branch` must exist on remote |
| Feature filter matches no files | Low | 0 findings, empty tab written | Tab still created for visibility |
| Tab name too long for Google Sheets | Low | Sheet write fails | Feature filter reduces branch name; use `--dry-run` to check |

## Migration Plan

### Phase 1: Core scaffolding
1. Create `code_daily_scan/gitlab_mr.py` — `fetch_mr_changed_files()` and `fetch_mr_info()`
2. Create `code_daily_scan/orchestrator_mr.py` — `MrScanOrchestrator` with worktree support
3. Modify `GrepScanner` to accept optional `changed_files: set[str]`
4. Modify `sheet_mr.py` — accepts both `MrInfo` and `BranchInfo` via Union type

### Phase 2: Branch scan
5. Create `code_daily_scan/gitlab_branch.py` — `fetch_branch_info()` using `repository_compare` API
6. Modify `MrScanOrchestrator` to accept `source_branch` parameter for worktree checkout
7. Add `--feature` parameter for package filtering

### Phase 3: CLI
8. Modify `cli.py` — add `scan-branch` command, `--feature` option to both commands
9. Test worktree creation and cleanup

### Phase 4: MR comment (optional)
10. Add `--post-comment` flag to `scan-mr` command
11. Import and use `GitLabReviewPoster` from `ai-review` with graceful fallback

### Phase 5: Testing
12. Add unit tests for `gitlab_mr.py` and `gitlab_branch.py`
13. Add integration tests for `MrScanOrchestrator` with known MR/branch
14. Verify `--dry-run` output matches sheet output

## Open Questions

| # | Question | Decision | Rationale |
|---|---|---|---|
| OQ1 | Include summary row in MR tab? | **Yes** — priority counts (P0/P1/P2/P3) + total at top | Quick signal without opening the sheet; mirrors daily scan summary pattern |
| OQ2 | Project slug in tab name? | **Yes** — `MR-{slug}-{iid}` | Same IID can exist across GitLab projects; slugify project path: `poems-team/poems-mobile3-android` → `MR-poems-team-poems-mobile3-android-23318` |
| OQ3 | Project infer from repo or explicit arg? | **Infer from `git remote get-url origin`** | Avoids requiring user to know numeric project ID; API resolves path to numeric ID |
| OQ4 | `--max-files` guard for large MRs? | **Skip in v1** | ripgrep handles 100s of files fast; add only if production MRs hit performance issues |

## Resolved design decisions for development readiness

### R1: GrepScanner file scoping — post-filter approach

The `GrepScanner.scan()` method runs `RipgrepRunner.search()` which executes `rg --vimgrep` recursively over the repo root. Modifying `RipgrepRunner` to accept a file list would change its interface for all callers. Instead:

**Decision: Post-filter findings in `MrScanOrchestrator`**

`GrepScanner` gets a new `changed_files: set[str] | None = None` constructor parameter. The `MrScanOrchestrator` passes the set of workspace-relative file paths. The `scan()` method wraps the runner result:

```python
# GrepScanner.__init__
def __init__(
    self,
    patterns_path: Path | None = None,
    *,
    loader: RulePatternLoader | None = None,
    rg_runner: RipgrepRunner | None = None,
    changed_files: set[str] | None = None,  # NEW
) -> None:
    ...
    self.changed_files = changed_files

# GrepScanner.scan()
def scan(self, root: Path) -> list[Finding]:
    findings = super().scan(root)
    if self.changed_files is not None:
        findings = [f for f in findings if self._workspace_rel_path(f.file_path, root) in self.changed_files]
    return findings

def _workspace_rel_path(self, abs_path: str, root: Path) -> str:
    return str(Path(abs_path).relative_to(root.resolve()))
```

`MrScanOrchestrator` normalizes GitLab API paths to workspace-relative before passing to scanner.

### R2: Path format — workspace-relative

`GrepScanner._match_to_finding()` currently stores `file_path` as absolute (`Path(match.file_path).resolve()`). This must change to workspace-relative for MR tab compatibility.

```python
# Changed: GrepScanner._match_to_finding()
repo_root = getattr(self, '_repo_root', None) or root
if repo_root:
    file_path = str(Path(match.file_path).relative_to(repo_root.resolve()))
else:
    file_path = match.file_path
```

`MrScanOrchestrator` sets `self._repo_root = repo_path` on the scanner instances so all paths are workspace-relative.

### R3: MR Context population

`gitlab_mr.py` fetches `mr.changes()` and stores the raw diff entries as `ReviewDiff` dataclasses in `MrInfo.diffs`. `sheet_mr.build_mr_tab_rows()` calls `_build_mr_context()` to match each finding's workspace-relative `file_path` to the corresponding diff:

```python
def _build_mr_context(file_path: str, diffs: list[ReviewDiff]) -> str:
    for diff in diffs:
        path = diff.new_path or diff.old_path or ""
        if path == file_path:
            lines = diff.diff.splitlines()
            if len(lines) > 12:
                lines = [*lines[:12], "... (truncated)"]
            return "\n".join(lines)
    return ""
```

Note: GitLab withholds text diffs for MRs with many changed files (813 in MR !23318 → only 46 files have diff content, zero Kotlin files). MR Context will be empty for most findings in large release merges. This is GitLab API behavior, not a scanner bug.

If diff is unavailable (GitLab returns `None` for large MRs; GitLab withholds text diffs for MRs exceeding ~50 changed files due to internal size limits), the column is empty — not a fatal error. The scanner always runs regardless of diff availability. See R3 in implementation for `_build_mr_context()` details.

### R4: `ai-review` availability for `--post-comment`

`GitLabReviewPoster` is imported at call time inside a try/except:

```python
try:
    from ai_review.gitlab.review_posting import GitLabReviewPoster
    poster = GitLabReviewPoster(project=str(project_id))
    poster.post_or_update(mr_iid, body, marker="<!-- android-scan-mr -->")
except ImportError:
    logger.warning("ai-review not installed, skipping MR comment")
```

Both repos declare `tdt-core[gitlab]`, so `python-gitlab` is always available. Only the `ai-review` import is conditional.

### R5: Project inference from git remote

```python
def infer_project_from_git_remote(repo_path: Path) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo_path), "remote", "get-url", "origin"],
        capture_output=True, text=True, check=True,
    )
    url = result.stdout.strip()
    # git@git.ecomedic.vn:poems-team/poems-mobile3-android.git
    # → poems-team/poems-mobile3-android
    project_path = url.removeprefix("git@git.ecomedic.vn:")
    if "://" in project_path:
        project_path = project_path.split("/", 3)[-1]
    project_path = project_path.removesuffix(".git")
    return project_path
```

The GitLab API resolves this path-encoded string to a numeric project ID automatically when passed to `client.projects.get("poems-team/poems-mobile3-android")`.

## Pattern Quality Notes (Production Experience)

### Round 1 findings on MR !23318

Initial scan of MR !23318 (813 files, 594 findings) revealed these high-noise rules:

| Rule | Initial Count | Issue |
|------|-------------|-------|
| L3 `companion object` | 130 | 98% false positive — fires on idiomatic static constants, not context leaks |
| C8 `\.resources` | 66 | 95% false positive — fires on `root.resources` in adapter `getView()` (safe) |
| L2 `context as Activity` | 86 | 84 are ViewHolder layout inflation (safe), 2 are genuine leaks |
| P2 `observe + call` | 68 | Fires on `updateUIFromData()`, image loading, UI calls (not network) |
| P5 `notifyDataSetChanged` | 115 | Correct signal but no DiffUtil detection |

### Implemented fixes

#### Architecture: Post-filter pipeline

A `_apply_post_filters()` step was added to `GrepScanner.scan()`. Post-filters work on findings grouped by `(rule_id, file_path)` and can read file content via `absolute_file_path` (stored in `Finding`). This cleanly separates "what regex found" from "should we suppress it based on semantic context."

```python
_RULE_POST_FILTERS: dict[str, Callable[[list[Finding]], list[Finding]]] = {
    "L2": _suppress_viewholder_context,     # suppress if onCreateViewHolder + layoutInflater
    "L6": _suppress_l6_activity_observe,   # suppress observe(this) in Activity (not Fragment)
    "P5": _suppress_diffing_p5,            # suppress if file has areContentsTheSame
}
```

#### Pattern removals

| Rule | Removed Pattern | Reason |
|------|--------------|--------|
| **L3** | `companion object` | Identiomatic Kotlin for static constants. Structurally impossible to distinguish from context leaks with regex alone. Now only fires on `lateinit var ctx: Context` |
| **C8** | `\.resources` | Fires on safe `root.resources.getDimension()` calls in adapter `getView()`. Removed entirely; `requireContext()` and `requireActivity()` patterns remain |
| **C9** | `\bdata\.[^!]+` | Fired on ALL `data.property` access. Narrowed to force-unwrap only (`!!`, `\.data!!`) |

#### Pattern refinements

| Rule | Change | Reason |
|------|--------|--------|
| **L2** post-filter | Suppress if file has `onCreateViewHolder` AND snippet contains `layoutInflater` / `LayoutInflater.from` | ViewHolder inflation with `(parent.context as Activity)` is correct Android Kotlin |
| **L3** | Keep `lateinit var ctx: Context` only | Actual context leak, never idiomatic |
| **P2** patterns 1-2 | `observe() + .api/.repository/.service/.client.` and `observe() + fetch/request/reload/refresh()` | Catches genuine observe-then-network-call anti-pattern |
| **P5** | Removed `areContentsTheSame` / `setHasStableIds` from regex; added post-filter for files containing `areContentsTheSame` | Cleaner signal; DiffUtil files suppressed entirely |
| **L6** post-filter | Suppress `observe(this)` in Activity classes | Valid in Activities; only Fragments need `viewLifecycleOwner` |
| **C4** | Narrowed `\[0-9\]` to require it be at end of statement | Eliminates `FloatArray[0]` and similar legitimate array accesses |

#### New `Finding` field

`absolute_file_path: str` was added to the `Finding` dataclass. Post-filters need absolute paths to read file content; `file_path` is workspace-relative and can't be read when cwd differs from scan root.

### Results: MR !23318 after enhancements

| Metric | Baseline | Enhanced | Change |
|--------|---------|----------|--------|
| **Total findings** | 594 | **282** | **−53%** |
| P0 Crash | 146 | **81** | −45% |
| P1 Leak/Perf | 424 | **195** | −54% |
| P2 Architecture | 24 | **6** | −75% |

Key reductions:
- **L3**: 130 → 3 (98% reduction, `companion object` pattern removed)
- **C8**: 66 → 20 (70% reduction, `\.resources` pattern removed)
- **L2**: 86 → 10 (88% reduction, ViewHolder post-filter)
- **P2**: 68 → ~15 (pattern refinement)
- **C4**: 25 → 20 (20% reduction, end-of-statement narrowing)

### Remaining known limitations

These rules are structurally hard to fix with regex alone and require deeper analysis (AST/type-aware tools):

- **P5** (`notifyDataSetChanged`): List size matters — 5-item menus are fine, 500-item lists are not. Post-filter can't know list size.
- **C5** (`observe + show`): Pattern fires on user-initiated dialog calls; can't distinguish from state-loss crashes without control-flow analysis.
- **C9** (`!!`): Sometimes intentional (validated backend contract), sometimes crash risk. Can't distinguish without value-flow analysis.

For these rules, the findings are **correct signal but require triage** — not false positives. The triage burden is reduced (282 vs 594), but not eliminated.

### Test coverage

Post-filter logic is unit-tested with synthetic fixture files and real ripgrep subprocess. 135 tests pass including 7 new post-filter tests covering L2 (2 variants), L6 (2), L3 (2), P5 (2).

### Future improvements (not implemented)

- **C4 post-filter**: Add guard detection (`list.size > n`, `isNotEmpty`, `indices`) to suppress findings when index access is within bounds check
- **C5 post-filter**: Distinguish `observe()` callback (unsafe) from dialog method call (safe) using class hierarchy analysis
- **AST-based scanner**: Replace regex patterns with a Kotlin AST analyzer for L2/L3/C5/C9 rules — the structural patterns exist but require parse-level analysis
- **DiffUtil detection**: Expand P5 suppression to files using `DiffUtil.ItemCallback` with `areContentsTheSame` — currently only `areContentsTheSame` in file body is detected
