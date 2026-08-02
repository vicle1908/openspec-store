# MR Code Scan Publication Integrity Design

## Context

The `ai-review` MR pipeline currently resolves MR scope through `_load_local_diffs` against the prepared worktree and uses `ReviewContextResolver._local_diff_looks_stale` to decide whether to fall back to GitLab compare. In MR `!23843` the local diff agreed with the first GitLab diff version (`644133`, 30 files) at scan time, so the scanner covered the authoritative scope at that moment. After scan completion, MR `!23844` merged `main` into `feature/develop_fix_bugs`, GitLab produced diff version `644137`, and MR `!23843` collapsed to one file. The dedicated `<!-- code-scan-review -->` note was not refreshed and contradicted the final summary `Findings: 0`.

A separate audit of the same commit found a focused Android detector gap: the new `registerOrderAlertBondsReceiver()` helper sets a registration flag even when a nullable `IntentFilter` short-circuits the actual registration call, and `unregisterOrderAlertBondsReceiver()` swallows every exception while clearing the flag. The dedup path on the scanner (`codescan_finding_suppressed` at line 114498 of `ai-review.stdout.log`) silently dropped every L5/LifecycleState candidate on that MR.

The audit validated that `onStart`/`onStop` pairing is correct, that a thrown `registerReceiver` cannot execute the subsequent flag assignment, and that the receiver object is non-null by construction. Those claims are explicitly excluded from this design.

## Goals / Non-Goals

### Goals

- Give every published review note a reproducible MR identity that includes project, MR IID, head SHA, base SHA, and GitLab diff-version ID.
- Apply one shared changed-hunk relevance gate so the dedicated note and the aggregate summary agree.
- Detect when the MR diff version has changed since the last scan and either refresh or invalidate the existing notes.
- Detect Android `BroadcastReceiver` registration-state bookkeeping that can diverge from actual registration.
- Preserve the existing exact-head-SHA worktree contract for source retrieval.

### Non-Goals

- Do not treat valid `onStart` register / `onStop` unregister as a defect.
- Do not flag a non-null receiver declared as an object expression as a nullability risk.
- Do not assert that a thrown `registerReceiver` call still mutates subsequent state.
- Do not redesign all Android lifecycle rules or change detector priority mappings.
- Do not replace exact-SHA worktrees with API-only source retrieval.
- Do not auto-approve, merge, or resolve GitLab discussions.

## Decisions

### D-1. Authoritative diff snapshot

Extend the existing `ReviewContext` rather than introduce a second context pipeline:

- Add a `MrDiffSnapshot` field containing project ID, MR IID, target branch, source branch, head SHA, base SHA, GitLab diff-version ID, and ordered `MrDiffFile` entries with `old_path`, `new_path`, and added/changed line ranges.
- Resolve the snapshot through the existing `GitlabClientFactory` client. Use the GitLab v4 merge-request versions/diffs APIs for scope identity and line ranges; retain the prepared exact-SHA worktree for file bytes and scanner execution.
- Keep `ReviewDiff` as the prompt/validator compatibility type, deriving it from the snapshot response rather than replacing it in one step.
- Reconciliation rule: if the prepared worktree HEAD does not equal `snapshot.head_sha`, return `ReviewContext.degraded_reason="head_sha_drift"` and do not scan.
- Preserve the current local Git resolution only as a file-content/diff-text fallback when GitLab line-range data is unavailable; it MUST NOT override the snapshot's MR identity.

Alternative considered: pure GitLab API for all diff content. Rejected because file bytes remain cheaper from the local worktree for the 30-file to 1000-file MR range, and the scanner already requires an exact-SHA checkout.

### D-2. Shared changed-hunk relevance gate

Extract the existing `EnhancedValidationContext` file/line relevance decision into a reusable result object consumed by both paths:

- Input: parsed code-scan findings, `ReviewDiff` values derived from the snapshot, and the snapshot identity.
- Output: filtered findings plus counters distinguishing `line_not_in_diff`, `file_not_in_diff`, generic suppression, and detector suppression.
- Apply the helper to code-scan findings before `CodeScanReviewer._post_comment`, then pass the same filtered code-scan findings into aggregate orchestration. The aggregate validator remains responsible for LLM findings and other calibration rules.
- The dedicated note and aggregate summary therefore share the exact same code-scan list without duplicating the entire aggregate validation pipeline.

Alternative considered: keep per-publisher filtering. Rejected because it produced the 40-vs-0 contradiction observed on `!23843`.

### D-3. Note identity and refresh policy

The dedicated `<!-- code-scan-review -->` note and the `<!-- mr-auto-review -->` note MUST each include the reviewed `head_sha`, `base_sha`, and `diff_version_id`. The intake step performs a precondition check:

- Fetch the latest GitLab diff-version ID for the MR.
- If the existing dedicated note's `diff_version_id` differs, treat the prior note as stale and either:
  - replace the existing note via `GitLabReviewPoster.post_or_update()` once a fresh scan completes, OR
  - post a short stale marker comment that says the prior note is no longer authoritative for the current diff and that a new scan is pending.

The aggregate summary follows the same identity contract.

Alternative considered: delete stale notes on every intake. Rejected because it could erase an MR-introduced reviewer contribution if the new scan fails to run.

### D-4. Existing capability preservation

The current capability's `ENABLE_CODE_SCAN` flag, marker conventions, two-tier env fallback, parallel orchestrator execution, exact-SHA worktree propagation, and structured `codescan_execution_summary` event remain unchanged. The new behavior is layered on top.

### D-5. Android receiver-state detection

Extend the canonical Android `memory-lifecycle.md` source and the existing Android `L5` scanner pipeline rather than inventing an unrecognised category file:

- Add explicit rule IDs `L-RX-001` and `L-RX-002` to the canonical Android Markdown rule source, with parser-compatible headings and patterns.
- Extend the Android loader category map only if the canonical source requires a new lifecycle file; otherwise keep the rules in `memory-lifecycle.md` so `Memory Leak` continues to load them.
- Add context-aware Android post-filter/detector support in `plugins/android/post_filters.py`, `plugin.py`, and the scanner hook that has access to the full file content and raw matches. A post-filter MUST be able to emit a finding for an invariant that raw grep cannot express; it MUST NOT be implemented as a suppression-only function that has no raw `L-RX` match.
- `L-RX-001` detects a Boolean registration flag assigned `true` outside a safe-call or null-check block that wraps the matching `registerReceiver` / `ContextCompat.registerReceiver` call.
- `L-RX-002` detects a `runCatching { unregisterReceiver(...) }` or `try { unregisterReceiver(...) } catch (_) {}` block that then clears the registration flag.
- The detector MUST NOT flag the legitimate `onStart`/`onStop` pairing, a non-null receiver object expression, or a thrown registration call's unreachable following assignment.
- Findings SHALL use the existing `Finding` model and `FindingParser` output path, with priority mapped through the existing `PRIORITY_SEVERITY_MAP` rather than introducing a new severity type.

Alternative considered: inline rule refactor across all Android lifecycle detectors. Rejected because the audit only validated this specific invariant and broader refactoring was outside the change's evidence base.

### D-6. Validation against MR !23843

Live validation SHALL exercise both observed diff versions:

- Diff version `644133`: scanner SHALL publish zero findings on files outside the 30-file snapshot and SHALL identify the receiver-state invariant on the added helper.
- Diff version `644137`: scanner SHALL publish zero whole-file findings and SHALL identify the receiver-state invariant on the added helper.
- A precondition check SHALL mark the earlier dedicated note stale when GitLab presents diff version `644137`.


### D-7. Diff-version cache

Cache the resolved GitLab diff-version ID per MR handoff for 60 seconds to avoid
burst rate-limiting on the versions endpoint. The cache key is `(project_id, mr_iid)`
and the value is the latest `diff_version_id`. On retrigger within the TTL window
the cached value is reused; after TTL the versions API is called again. The cache is
an in-memory dict on the `ReviewContextResolver` instance (no persistent state).

### D-8. Orchestrator code-scan validation replacement

The shared relevance gate (D-2) replaces the orchestrator's existing per-finding
`EnhancedValidationContext.validate()` call for code-scan findings (currently at
orchestrator.py ~line 675). After D-2, code-scan findings that reach the orchestrator
have already passed the shared gate. The orchestrator MUST NOT re-validate code-scan
findings through `EnhancedValidationContext`; it MAY still validate LLM reviewer
findings through the existing path. This avoids double-filtering and ensures the
dedicated note and aggregate summary see the same set.

## Risks / Trade-offs

- [Risk] GitLab diff-version endpoint may rate-limit on bursts → Mitigation: cache diff-version ID per MR handoff for 60 seconds and reuse it on the first recheck.
- [Risk] Worktree refresh after target advancement can race with reviewer publication → Mitigation: gate publication behind a single diff-version compare and refuse to publish if the version changes between resolve and post.
- [Risk] Receiver-state detector may misfire on patterns where the boolean is intentionally decoupled → Mitigation: scope the detector to files that contain a `registerReceiver`/`ContextCompat.registerReceiver` call and a paired `unregisterReceiver` call within the same compilation unit.
- [Risk] Note refresh policy can erase prior review context if the new scan fails → Mitigation: keep the existing note until a fresh scan completes successfully; never delete on intake alone.
- [Risk] Migrating existing MRs mid-review could double-post notes → Mitigation: apply the new note identity check on the next intake and only reformat existing notes on first re-run.

## Migration Plan

- Phase 1 (ai-review): add `MrDiffSnapshot` data model and resolve it once per intake; keep current publication path but include the new identity fields.
- Phase 2 (ai-review): route the dedicated note and the summary note through one relevance gate that uses the snapshot.
- Phase 3 (ai-review): add the precondition diff-version compare and stale-note handling.
- Phase 4 (code-daily-scan): add the Android `L-RX` detector category and post-filter wiring.
- Phase 5 (ai-review and code-daily-scan): regression tests plus live validation on MR `!23843` (both diff versions) and one new MR.
- Rollback: redeploy prior known-good ai-review and scanner source revisions, then rebuild/restart the scheduler; verify both runtime module paths and health checks after rollback.

## Open Questions (Resolved)

- **Precondition compare action scope:** The stale-note compare fires on every intake (`open`, `reopen`, AND `update`). GitLab recomputes diff versions on any push regardless of action type, so scoping to only open/reopen would miss staleness on update events.
- **L-RX severity:** Reuse `critical` to align with the existing `PRIORITY_SEVERITY_MAP` in code-scan-reviewer. No new severity bucket.
