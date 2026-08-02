# ai-review-enhanced-scan Design

## Context

The ai-review pipeline already runs `CodeScanReviewer` alongside optional LLM reviewers in a `ThreadPoolExecutor`. The code-scan reviewer reads a JSON sidecar, invokes `code-daily-scan` in-process, and upserts a dedicated `<!-- code-scan-review -->` comment.

The current sidecar omits `commit_sha`, and `CodeScanReviewer` permits fallback to the long-lived repository checkout. It also discards the report returned by `MrScanOrchestrator.run()`, so an empty findings list is treated as clean without evidence that eligible files or rules were evaluated. The reused worktree session sets `gitnexus_index_fresh=None`, which Phase 3 explicitly reports as degraded.

This design hardens the existing integration while preserving its public reviewer and scanner return contracts.

## Goals / Non-Goals

**Goals:**

- Preserve the existing reviewer integration, concurrency, configuration, and marker-based comment behavior
- Prove the scan checkout matches the reviewed commit before evaluating code
- Extend the existing scanner report dictionary with execution evidence without changing its two-tuple return shape
- Separate detector completeness from Phase 3 post-processing health in outcome evidence
- Make clean, findings, skipped, degraded, and failed outcomes operationally distinguishable
- Define the actual launchd and scheduler rollout paths and runtime provenance checks

**Non-Goals:**

- Changing individual code-daily-scan rule detection semantics
- Changing LLM reviewer invocation or configuration
- Creating new comment markers (reuse existing `GitLabReviewPoster` pattern)
- Modifying the webhook-receiver pipeline
- Replacing the `FindingParser` with a custom parser

## Decisions

### Decision 1: Extend `BaseReviewer` (not `CommandReviewer`)

**Chosen approach:** `CodeScanReviewer(BaseReviewer)` — implements `check_availability()` and `run()` directly.

**Rationale:** `MrScanOrchestrator` is a Python class, not a CLI binary. `CommandReviewer` assumes `subprocess.run()` with `shutil.which()` for availability checks. Direct `BaseReviewer` implementation gives full control over execution and error handling.

**Alternative considered:** Wrap `MrScanOrchestrator` in a subprocess call to the `code-daily-scan` CLI. Rejected because it adds process overhead and complicates error handling.

### Decision 2: Platform detection from project ID

**Chosen approach:** Derive platform from `Settings.local_repo_paths` project ID mapping:

- Project ID 231 → "ios" (poems-mobile3-ios)
- Project ID 232 → "android" (poems-mobile3-android)

**Rationale:** The review context includes `project_id`, which maps directly to the platform. No additional config needed.

**Alternative considered:** Detect from repo path. Rejected because `ReviewContext` doesn't always include the full repo path.

### Decision 3: Dedicated `<!-- code-scan-review -->` marker

**Chosen approach:** Post scan findings to a separate comment with marker `<!-- code-scan-review -->`.

**Rationale:** Keeps scan findings visually distinct from LLM reviews. Allows developers to read findings separately. Maintains separation of concerns.

**Alternative considered:** Include scan findings in the same `<!-- mr-auto-review -->` comment. Rejected because:

1. Scan findings are structured (rule, file, line) while LLM findings are natural language
2. The finding parser would need to distinguish between reviewer sources
3. Separate markers allow independent updates

### Decision 4: Two-tier env var config with legacy fallback

**Chosen approach:** `Settings.enable_codescan` loaded via:

```python
enable_codescan=get_bool_env(
    "AI_REVIEW_ENABLE_CODESCAN",
    get_bool_env("ENABLE_CODE_SCAN", True)
)
```

**Rationale:** Matches the existing pattern for all other reviewer enable flags (lines 71-76 of settings.py). The `AI_REVIEW_*` prefix takes priority; legacy `ENABLE_*` is fallback.

### Decision 5: Graceful error handling with FAILED status

**Chosen approach:** Wrap `MrScanOrchestrator.run()` in try/except. Return `ReviewResult(status=FAILED, error=str(exc))` for any exception.

**Rationale:** Matches `CommandReviewer` error handling pattern. The orchestrator catches executor exceptions and creates `ReviewerExecution` entries. Error is logged but doesn't prevent other reviewers from completing.

### Decision 6: Findings serialized to markdown list format

**Chosen approach:** Serialize each `Finding` as:

```text
- [{severity}] {file_path}:{line} - {message}
```

**Rationale:** Compatible with `FindingParser.MARKDOWN_PATTERN`. Severity mapping: P0/P1 → critical, P2 → high, P3 → medium, informational → suggestion.

## Architecture

### File Structure

```text
ai-review/src/ai_review/
├── reviewers/
│   ├── __init__.py              # Export CodeScanReviewer
│   ├── base.py                  # BaseReviewer, ReviewResult, ReviewStatus, ReviewMode
│   ├── command.py               # CommandReviewer (LLM reviewers)
│   ├── kimi_reviewer.py
│   ├── claude_reviewer.py
│   ├── codex_reviewer.py
│   ├── pi_reviewer.py
│   └── code_scan_reviewer.py    # NEW
├── review_flow/
│   ├── orchestrator.py          # ReviewOrchestrator._build_reviewers()
│   └── context.py               # ReviewContext
├── gitlab/
│   └── review_posting.py        # GitLabReviewPoster
└── config/
    └── settings.py              # Settings.enable_codescan, get_enabled_clis()
```

### CodeScanReviewer Interface

```python
# reviewers/code_scan_reviewer.py
from pathlib import Path
from ai_review.reviewers.base import BaseReviewer, ReviewResult, ReviewStatus, ReviewMode

class CodeScanReviewer(BaseReviewer):
    name: str = "codescan"
    
    def __init__(
        self,
        *,
        repo_path: Path,
        platform: str,
        patterns_path: Path | None = None,
        timeout_seconds: int = 120,
    ):
        ...
    
    def check_availability(self) -> bool:
        # Check code-daily-scan package is importable
        try:
            from code_daily_scan.orchestrator_mr import MrScanOrchestrator
            return True
        except ImportError:
            return False
    
    def run(
        self,
        prompt_file: Path,
        mode: ReviewMode,
        cwd: Path | None = None,
    ) -> ReviewResult:
        # prompt_file contains MR context (project, mr_iid, changed_files, etc.)
        # Returns ReviewResult with serialized findings or error
```

### Orchestrator Integration

```python
# review_flow/orchestrator.py
def _build_reviewers(self, settings: Settings) -> dict[str, BaseReviewer]:
    reviewers: dict[str, BaseReviewer] = {}
    # ... existing reviewers ...
    if settings.enable_codescan:
        repo_path = self._get_repo_path(payload.project_id)  # from local_repo_paths
        platform = self._get_platform(payload.project_id)
        reviewers["codescan"] = CodeScanReviewer(
            repo_path=repo_path,
            platform=platform,
        )
    return reviewers
```

### Finding Serialization

```python
def _serialize_finding(finding: Finding) -> str:
    severity_map = {"P0": "critical", "P1": "critical", "P2": "high", "P3": "medium"}
    severity = severity_map.get(finding.priority, "suggestion")
    file_path = finding.file_path.replace("\\", "/")  # Normalize path separators
    return f"- [{severity}] {file_path}:{finding.line} - {finding.message}"
```

### Decision 7: Reuse only the prepared exact-SHA checkout

**Chosen approach:** `PromptBuilder` propagates both `worktree_path` and `commit_sha` from `ReviewContext.to_prompt_metadata()` into the code-scan metadata sidecar. `CodeScanReviewer` scans that checkout and verifies its `HEAD` equals the reviewed SHA before invoking `MrScanOrchestrator`.

**Rationale:** `ReviewContextResolver` already prepares and validates a commit-aware worktree. The current metadata sidecar drops `worktree_path` and `commit_sha`, causing `CodeScanReviewer` to fall back to the long-lived repository checkout while bypassing `MrScanOrchestrator` worktree creation. Preserving the prepared checkout removes this context-loss defect without creating another worktree.

**Alternative considered:** Let `MrScanOrchestrator` create a second worktree from `source_branch`. Rejected because branch heads can move after webhook intake and duplicate worktree lifecycle increases latency and failure modes.

### Decision 8: Return structured scan execution evidence

**Chosen approach:** Enrich the existing MR scan report dictionary with a namespaced execution-evidence section containing requested files, extension-eligible files, files present in the checkout, loaded rule count by category, scanned file count, skipped-file reasons, pre-Phase-3 finding count, post-Phase-3 finding count, and degradation reasons.

**Rationale:** An empty `findings` list currently represents multiple states: no rule matched, no eligible files, missing files, or no rules loaded. The reviewer cannot publish an accurate user-facing outcome without evidence that meaningful work occurred.

**Alternative considered:** Infer scan health from duration or MR changed-file count. Rejected because runtime varies with rule and repository caches, and changed files can include intentionally unsupported assets such as JSON.

### Decision 9: Classify clean, findings, skipped, degraded, and failed outcomes

**Chosen approach:** Publish "No code scan issues found" only when the reviewed SHA is verified, at least one eligible existing file was scanned, at least one rule loaded, and neither detector execution nor Phase 3 is degraded. Use an informational skipped result for no changed files or no eligible files, a degraded result for partial detector execution or unavailable Phase 3 context, and a failed result for revision mismatch or zero loaded rules. A degraded result MAY preserve and publish findings, but SHALL identify which stage degraded.

**Rationale:** Phase 3 currently treats `gitnexus_index_fresh=None` as unavailable. Keeping detector evidence and post-processing health as separate report sections makes that limitation visible without discarding valid pattern findings or mislabeling an unverified zero as clean.

### Decision 10: Preserve scanner API compatibility

**Chosen approach:** `MrScanOrchestrator.run()` continues to return exactly `(findings, report)`. New execution evidence is namespaced inside the existing report dictionary; existing Phase 3 keys remain available during migration.

**Rationale:** GitNexus identifies four direct CLI callers and five affected execution flows, with CRITICAL blast radius for changing the method contract. Extending the dictionary preserves tuple unpacking and allows callers to adopt evidence incrementally.

### Decision 11: Deploy the two runtime copies explicitly

**Chosen approach:** Run the ai-review deployment script to copy both repositories into the launchd runtime and install them non-editably. Independently rebuild/restart the scheduler service, whose editable package reads bind-mounted `code-daily-scan/src`. Verify module provenance from each runtime after rollout.

**Rationale:** `code-daily-scan/scripts/deploy.sh` writes to `~/deployments/code-daily-scan/app`, which is not consumed by either MR review or the Docker scheduler. Treating that script as the rollout path would leave the active runtimes stale.

## Risks / Trade-offs

| Risk | Mitigation |
| --- | --- |
| Scan adds latency to overall review | Runs in parallel with LLM reviewers via ThreadPoolExecutor |
| code-daily-scan not installed in ai-review venv | Add as dependency in pyproject.toml |
| Worktree ownership becomes ambiguous | Reuse only the checkout prepared by `ReviewContextResolver` and verify its SHA before scanning |
| Duplicate findings (scan + LLM) | Acceptable — different perspectives are complementary |
| `ReviewContext` missing required fields | Fail the code-scan reviewer explicitly; do not publish a clean result |
| Existing callers expect a two-tuple from `MrScanOrchestrator.run()` | Preserve the two-tuple and existing Phase 3 keys; add namespaced execution evidence to the report dictionary |
| Platform extensions intentionally exclude assets such as JSON | Report them as ineligible rather than silently counting them as scanned |
| Reused ai-review worktree has unknown GitNexus freshness | Record detector and Phase 3 status separately; do not emit the exact clean phrase while Phase 3 is degraded |
| Source tests pass but deployed copy is stale | Verify imported module paths and source/runtime snapshots from the launchd venv and scheduler container |
| Standalone deploy script targets an unused runtime | Deploy MR review through `ai-review/scripts/deploy.sh`; rebuild/restart the scheduler separately |
| Finding parser misses structured output | Verify format matches `MARKDOWN_PATTERN` exactly |

## Open Questions (Resolved)

| Question | Resolution |
| --- | --- |
| Comment marker | `<!-- code-scan-review -->` for scan findings |
| Error comment | Yes — error is logged and returned as FAILED status |
| Config location | `~/.tdt/.env` via `ENABLE_CODE_SCAN` or `AI_REVIEW_ENABLE_CODESCAN` |
| Base class | `BaseReviewer` (not `CommandReviewer`) |
| Platform detection | From project ID via `local_repo_paths` mapping |
| Finding format | Markdown list compatible with `FindingParser` |
