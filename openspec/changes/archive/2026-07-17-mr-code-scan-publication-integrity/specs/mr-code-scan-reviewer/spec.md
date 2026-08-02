# MR Code Scan Reviewer Delta Specification

## ADDED Requirements

### Requirement: MR review SHALL resolve an authoritative diff snapshot

The MR review SHALL resolve, once per intake, an MR diff snapshot carrying project, MR IID, target branch, source branch, head SHA, base SHA, GitLab diff-version ID, changed file list, and per-file added or changed line ranges. The snapshot SHALL be derived from GitLab as the identity authority and from the prepared worktree as the file-content authority.

#### Scenario: Snapshot identity is available

- **WHEN** an intake is accepted
- **THEN** the review SHALL resolve an `MrDiffSnapshot` carrying project, MR IID, head SHA, base SHA, GitLab diff-version ID, changed files, and per-file changed-line ranges
- **AND** the snapshot identity SHALL be propagated through `ReviewContext` metadata, prompt metadata, and the code-scan metadata sidecar

#### Scenario: Head SHA drift degrades the review

- **WHEN** the prepared worktree HEAD differs from the snapshot head SHA
- **THEN** the review SHALL NOT scan the worktree as authoritative
- **AND** the review SHALL return a degraded result with reason `head_sha_drift`

### Requirement: MR reviews SHALL apply a shared changed-hunk relevance gate

Findings published from any review path SHALL pass through one shared gate that compares each finding's file path and line number against the MR diff snapshot's changed-line ranges. Findings on files or lines outside the snapshot SHALL be dropped with reason `line_not_in_diff`.

#### Scenario: Finding targets an unchanged line

- **WHEN** a finding reports `file_path` in the snapshot but `line` outside every added or changed range for that file
- **THEN** the finding SHALL be dropped from both the dedicated `<!-- code-scan-review -->` note and the aggregate `<!-- mr-auto-review -->` summary

#### Scenario: Finding targets an unchanged file

- **WHEN** a finding reports a `file_path` that is not in the snapshot's changed file list
- **THEN** the finding SHALL be dropped with reason `line_not_in_diff`

### Requirement: Posted review notes SHALL expose MR identity

Every `<!-- code-scan-review -->` note and every `<!-- mr-auto-review -->` note SHALL include the reviewed head SHA, base SHA, and GitLab diff-version ID in a stable, machine-readable footer.

#### Scenario: Dedicated note carries diff identity

- **WHEN** the code-scan reviewer publishes its dedicated note
- **THEN** the note body SHALL end with a footer line containing `head_sha=<sha>`, `base_sha=<sha>`, and `diff_version_id=<id>`
- **AND** the footer SHALL be present on both initial posts and updates

#### Scenario: Summary note carries diff identity

- **WHEN** the orchestrator publishes the aggregate summary note
- **THEN** the note body SHALL include `Reviewed head SHA`, `Base SHA`, and `Diff version ID` fields
- **AND** the published SHA SHALL match the snapshot identity

### Requirement: Stale notes SHALL be marked when MR diff version changes

The intake step SHALL compare the existing dedicated `<!-- code-scan-review -->` note's diff-version ID against the current GitLab diff-version ID. When they differ, the prior note SHALL be marked stale rather than left to contradict newer findings.

#### Scenario: Prior note is stale on new intake

- **WHEN** an intake is accepted for an MR
- **AND** the existing dedicated note's `diff_version_id` differs from the current GitLab diff-version ID
- **THEN** the prior note SHALL either be replaced by a fresh scan via `GitLabReviewPoster.post_or_update()` or SHALL be flagged with a short stale-marker comment
- **AND** no MR-introduced reviewer contribution SHALL be lost when the fresh scan fails or is skipped

#### Scenario: Diff version unchanged on retake

- **WHEN** an intake is accepted for an MR
- **AND** the existing dedicated note's `diff_version_id` equals the current GitLab diff-version ID
- **THEN** the prior note SHALL be reused via `GitLabReviewPoster.post_or_update()` rather than duplicated

### Requirement: CodeScanReviewer SHALL publish only relevance-filtered findings

The `CodeScanReviewer` SHALL publish its dedicated `<!-- code-scan-review -->` note using the MR diff snapshot's changed-line ranges and SHALL NOT publish findings outside those ranges as MR-introduced issues.

#### Scenario: All scanner findings fall in changed hunks

- **WHEN** all scanner findings report files and lines covered by the snapshot's changed-line ranges
- **THEN** the dedicated note SHALL list every finding in the existing FindingParser markdown format
- **AND** the aggregate summary SHALL present the same count of contributing findings

#### Scenario: Some scanner findings fall outside changed hunks

- **WHEN** at least one scanner finding reports a file or line outside the snapshot's changed-line ranges
- **THEN** the dedicated note SHALL list only the in-hunk findings
- **AND** the aggregate summary SHALL present the same count of contributing findings
- **AND** the `codescan_execution_summary` event SHALL distinguish `hunk_filtered` from `suppressed` in the skip-reason counters
