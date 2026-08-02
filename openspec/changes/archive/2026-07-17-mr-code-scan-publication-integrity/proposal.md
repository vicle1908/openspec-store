# MR Code Scan Publication Integrity Proposal

## Why

MR !23843 demonstrated that exact-head-SHA scanning is necessary but insufficient for a trustworthy MR review. The scanner covered the GitLab diff version active at execution time, yet its dedicated comment published 40 whole-file findings that the final hunk-aware summary reduced to zero, and the comment became stale when the target branch advanced and GitLab recomputed the MR from 30 files to one.

The same audit found one concrete Android detector gap: receiver registration state can be marked successful when nullable registration input prevents the call, while unregistration failures can be silently discarded. Specifying both corrections together closes the observed publication-integrity failure and adds focused detection for the change pattern the review missed.

## What Changes

- Capture an authoritative MR diff snapshot containing project, MR IID, head SHA, base SHA, GitLab diff-version ID, changed files, and changed-line ranges.
- Keep exact-head-SHA worktrees as the source of file content while using the GitLab diff snapshot as the source of MR scope identity.
- Apply one shared changed-hunk relevance gate before findings reach either the dedicated `<!-- code-scan-review -->` comment or the aggregate `<!-- mr-auto-review -->` summary.
- Prevent dedicated comments from publishing findings on unchanged files or unchanged lines as MR-introduced issues.
- Include the reviewed head SHA, base SHA, and diff-version ID in structured execution evidence and posted review notes.
- Detect target-branch advancement through a changed GitLab diff-version ID and update the existing code-scan note to a stale/pending state or re-run before presenting findings as current.
- Add Android receiver-state detection for registration flags mutated outside a successful nullable registration path and for unregister failures discarded while state is cleared.
- Add regression and live-MR verification using the two observed MR !23843 diff versions (`644133` with 30 files and `644137` with one file).

## Capabilities

### New Capabilities

- `android-receiver-state-detection`: Detect registration-state bookkeeping that can diverge from actual dynamic `BroadcastReceiver` registration while preserving valid `onStart`/`onStop` lifecycle pairing.

### Modified Capabilities

- `mr-code-scan-reviewer`: Make MR scope reproducible by diff version, share hunk relevance across all publication paths, and invalidate or refresh stale results after target-branch advancement.

## Impact

- `ai-review/src/ai_review/review_flow/context.py`: authoritative diff snapshot resolution and identity propagation.
- `ai-review/src/ai_review/prompts/builder.py` and review metadata models: base SHA, diff-version ID, and changed-line ranges.
- `ai-review/src/ai_review/review_flow/orchestrator.py`: one shared relevance gate and consistent finding counts.
- `ai-review/src/ai_review/reviewers/code_scan_reviewer.py`: publish only relevance-filtered findings and include diff identity.
- `ai-review` GitLab intake/posting integration: detect changed diff versions and update or re-run idempotent notes.
- `code-daily-scan` Android rules/post-filters: receiver-state invariant detection.
- Tests in `ai-review` and `code-daily-scan`, plus operational verification against a real GitLab MR.
- No external dependencies and no database migration.

## Non-Goals

- Do not treat valid `onStart` registration paired with `onStop` unregistration as a defect.
- Do not flag a non-null receiver declared as an object expression as a nullability risk.
- Do not claim that a thrown registration call executes subsequent state mutation.
- Do not redesign every Android lifecycle rule or re-prioritize all existing findings.
- Do not replace exact-SHA worktrees with API-only source retrieval.
- Do not auto-approve, merge, or resolve GitLab discussions.
