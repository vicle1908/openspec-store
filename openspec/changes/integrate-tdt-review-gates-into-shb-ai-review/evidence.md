# Implementation & Verification Evidence

## Scope & Target Root
- **Change**: `integrate-tdt-review-gates-into-shb-ai-review`
- **Target Repository**: `/Users/androidteam/Developer/shb/shb-ai-review`
- **Git Baseline**: `9d75c40d740f023986ae33c373881d1cb0211ea3`
- **Execution Mode**: Local Python 3.14+ runtime via `uv`. Zero live GitLab network publishing (safe isolated local loopback HTTP fixture).
- **Scope Extension**: User-authorized extension implementing both opt-in AI review provider dispatch via Pydantic AI v2 (`--ai`) and changed-line (patch) test coverage gating (`mr-coverage diff`) alongside review-state audit (`mr-coverage scan`).

## Architectural Gates & Substantive Hardening

1. **Configured AI Review Provider & Strict Prompt Isolation (`shb_review/ai/reviewer.py`)**:
   - `AiReviewer` using Pydantic AI v2 with structured output (`AiReviewResponseSchema`).
   - Strict untrusted code boundary: system prompt explicitly mandates all diff and source code is untrusted data; the model must never obey instructions or commands within comments or code.
   - Tool execution completely disabled (`tools=[]`): operates as a pure structured-output transformer.
   - Outbound credential redaction: regex-based scrub of private keys, passwords, API keys, bearer tokens, and PANs before transmission to AI models, while preserving line numbers and code structure for deterministic local detections.
   - Credentials from environment only (`SHB_REVIEW_AI_KEY`, `SHB_MODEL_GATEWAY_KEY`, `SHB_MODEL_GATEWAY_URL`); zero token leakage in error messages or logs.
   - Fail-closed contract: unconfigured or failed AI calls raise `AiReviewError` with non-zero exit code (no false approval).

2. **Diff Hunk Gate Hardening (`shb_review/validation/hunk_gate.py`)**:
   - Exact canonical repository path matching without improper git prefix stripping (`_raw_canonical_path` and `_normalize_repo_path`).
   - Resolves paths with traversal safely without escaping repository root boundary.
   - Preserves distinct files sharing the same basename across directories (`src/auth/service.py` vs `src/billing/service.py`).
   - Side-aware diff line filtering: findings with `side="new"` strictly check modified ranges in the new revision and cannot falsely match old deleted lines; findings with `side="old"` check `deleted_lines`.
   - Unified diff parser returning `(changed_ranges, deleted_lines, is_binary, is_truncated)` with fail-closed behavior on binary, truncated, or malformed diffs.

3. **Discussion Deduplication & Resolution Safety (`shb_review/validation/deduplicator.py`)**:
   - Stable SHA-256 fingerprinting over `(canonical_path, rule_id, normalized_message)`.
   - Embedded comment marker `<!-- shb-ai-review:fingerprint=<sha256> -->`.
   - Severity ranking preserving `FindingSeverity` enum (`BLOCKER` > `CRITICAL` > `MAJOR` > `MINOR` > `INFO`).
   - Comment capping (default 15) routing excess findings to summary note.
   - Fail-closed resolution gates: threads are NEVER auto-resolved if:
     1. The review failed (`review_success=False`)
     2. The review was partial or diff truncated (`is_partial=True`)
     3. Findings were capped / overflow exists (`is_capped=True`)
     4. The discussion's target file was unchanged in the current revision (`disc.file_path not in modified_files`)
     5. The thread contains user comments or replies (`has_user_comments=True` or `notes_count > 1`)

4. **Isolated Git Worktree Lifecycle (`shb_review/worktree/manager.py`)**:
   - Git ref validation (`_validate_git_ref`) rejecting malicious branch references, path traversal (`..`), and command injection characters.
   - All checkouts detached at pinned immutable commit SHAs with `--` boundary flags.
   - Safe stale worktree pruning inspecting `git worktree list --porcelain` and pruning only owned directories inside `self.base_dir` without ever calling global `git worktree prune`.
   - Guaranteed cleanup context managers (`managed_worktree`).

5. **GitLab MR Client & Discussion Publisher (`shb_review/gitlab/client.py`, `shb_review/gitlab/posting.py`)**:
   - Immutable `DiffRefs` (`@dataclass(slots=True, frozen=True)`).
   - Evaluated snapshot reuse: `publish_review` directly reuses the evaluated `MRDetails` snapshot, preventing race condition mismatches from redundant fetches.
   - Per-action head SHA race detection: checks `check_head_sha_race` prior to inline discussions, prior to summary note update, and prior to thread resolutions.
   - Author ownership enforcement: verifies bot ownership of existing summary notes before updating, preventing accidental overwriting of user notes.
   - Failure API status: publication errors abort mutations and set verdict to `REJECTED`, guaranteeing non-zero CLI exit code (no false approval).

6. **MR Review Coverage Scanner & Patch Test Coverage (`shb_review/coverage/`)**:
   - `mr-coverage scan`: Evaluates MR review state snapshots detecting missing, stale, or failed reviews with fail-closed schema validation (exit 0 clean, exit 1 gaps, exit 2 malformed).
   - `mr-coverage diff`: Evaluates changed-line test coverage from git diffs against Cobertura XML reports via `shb_review.coverage.patch.calculate_patch_coverage`:
     - Exact canonical repo-relative path resolution against XML classes.
     - Strict full immutable 40/64 hex SHA provenance verification.
     - Language-agnostic with fail-closed missing source detection (`MissingSourceReportError`).
     - Bounded file read with UTF-8 verification and strict DTD/entity injection rejection.
     - Exit code conventions: 0 (passed / no executable changes), 1 (coverage deficit), 2 (fail-closed measurement error).

7. **CLI Integration (`shb_review/cli.py`)**:
   - `shb-ai-review scan --repo <path>`: Local repository scanner with source allowlist and ignore filters.
   - `shb-ai-review review-mr`: Added `--ai` flag for opt-in AI review execution.
   - `shb-ai-review list-reviewers`: Accurate listing of supported review engines (`static-compliance`, `pydantic-ai`).
   - `shb-ai-review doctor`: Diagnostics including AI provider configuration status.

## Verification Checksums & Metadata (Value-Blind)
- `src/shb_review/models.py`: 44 lines, Pydantic v2 models with `side` and `source` fields.
- `src/shb_review/validation/hunk_gate.py`: Hardened path normalization and side-aware filtering.
- `src/shb_review/validation/deduplicator.py`: Hardened thread resolution gating with unchanged file protection.
- `src/shb_review/worktree/manager.py`: Git ref injection validation and safe stale pruning.
- `src/shb_review/gitlab/client.py`: Immutable diff_refs and bot author verification.
- `src/shb_review/gitlab/posting.py`: Snapshot reuse, per-action race checks, and author ownership.
- `src/shb_review/ai/reviewer.py`: Pydantic AI v2 reviewer with tools disabled and outbound credential redaction.
- `src/shb_review/coverage/scanner.py`: Review-state audit scanner.
- `src/shb_review/coverage/patch.py`: Changed-line patch test coverage calculator.
- `src/shb_review/coverage/cli.py`: Typer CLI exposing `scan`, `diff`, `status`, and `health`.
- `src/shb_review/cli.py`: CLI exposing `scan`, `review-mr`, `list-reviewers`, and `doctor`.
