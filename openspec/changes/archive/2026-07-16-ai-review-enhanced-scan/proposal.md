# ai-review-enhanced-scan Proposal

## Why

The ai-review pipeline now integrates `code-daily-scan`, but MR 23833 exposed that the integration can publish "No code scan issues found" without proving it scanned the reviewed commit or evaluated eligible files and rules. The existing capability must be hardened so clean results are evidence-based and operationally auditable.

## What Changes

- **Existing integration baseline**: Preserve the deployed `CodeScanReviewer`, parallel execution, dedicated comment marker, configuration toggle, and independent failure handling
- **Compatibility-preserving report extension**: Keep `MrScanOrchestrator.run()` returning `(findings, report)` and enrich the existing report dictionary so standalone MR and branch CLI callers remain compatible
- **Exact revision scanning**: Propagate the prepared worktree path and reviewed commit SHA into the code-scan context, and reject a scan when the checkout cannot be proven to match that SHA
- **Evidence-bearing outcomes**: Distinguish a verified clean scan from no eligible files, no loaded rules, missing files, and degraded post-processing
- **Operational observability**: Log requested, eligible, existing, and scanned file counts together with loaded-rule counts and skip reasons

## Capabilities

### New Capabilities

- `mr-code-scan-reviewer`: Integrate code-daily-scan as a reviewer in the ai-review MR pipeline with:
  - Parallel execution with LLM reviewers
  - Independent GitLab MR comment posting
  - Configurable enable/disable via `enable_code_scan` flag
  - Graceful error handling with error comment posting
  - Marker-based upsert semantics using the dedicated `<!-- code-scan-review -->` marker
  - Exact-SHA worktree verification before scanning
  - Scan execution evidence and explicit clean, skipped, degraded, and failed outcomes

### Modified Capabilities

- (none)

## Impact

- **Code**: `ai-review` repo — reviewer context propagation, revision verification, result classification, logging, and tests
- **Code**: `code-daily-scan` repo — structured MR scan execution report with file eligibility, existence, rule-loading, and degradation evidence
- **Configuration**: `~/.tdt/.env` or repo config for `enable_code_scan` flag
- **Runtime packaging**: `ai-review/scripts/deploy.sh` embeds a non-editable copy of `code-daily-scan`; the Docker scheduler uses a separate editable install over read-only source bind mounts
- **Deployment**: The launchd runtime must be redeployed from `ai-review`, and the scheduler must be rebuilt/restarted separately to keep the standalone scan runtime consistent
- **GitLab**: Existing dedicated code-scan comment is updated with evidence-based outcomes

## Non-Goals

- This does NOT change the detection semantics of individual code-daily-scan rules
- This does NOT change how LLM reviewers are invoked or configured
- This does NOT add new markers or alter existing comment marker conventions
