# Spec: Jira MR-Only Comments Integration

## FR-1: MR Events Post Comments to Jira

**Priority:** Critical  
**When:** MR created, updated, merged, or closed  
**Then:** A structured comment appears on the linked Jira issue(s)  
**Comment format:** Includes MR title, MR URL, action (created/merged/etc.), and author

### Scenario: MR created triggers Jira comment

**Given** an MR is created with title `SR-123: Add feature` on project 231 or 232  
**When** the MR enters `opened` state  
**Then** a comment is posted to Jira issue SR-123 with MR details

### Scenario: MR merged triggers Jira comment

**Given** an MR linked to Jira issue STABI-559  
**When** the MR is merged  
**Then** a comment is posted to STABI-559 indicating the merge action and author

## FR-2: Non-MR Events Do NOT Post to Jira

**Priority:** Critical  
**When:** Push, commit, pipeline, tag push, job, wiki, note, or issue event fires  
**Then:** No comment is created on any Jira issue  
**Exception:** Smart commits in commit messages using `#comment`, `#time`, `#close` syntax still work (handled by Jira's DVCS connector, not the integration webhook)

### Scenario: Individual push does NOT trigger Jira comment

**Given** a developer pushes commits referencing `SR-456` to a feature branch  
**When** the push event fires  
**Then** no comment is created on SR-456 in Jira

### Scenario: Pipeline completion does NOT trigger Jira comment

**Given** a pipeline runs for a branch containing `AM-789` in commit messages  
**When** the pipeline succeeds or fails  
**Then** no comment is created on AM-789 in Jira

### Scenario: Smart commits still function

**Given** a commit message contains `SR-456 #comment Fixed the login bug`  
**When** the commit is pushed  
**Then** the smart commit comment appears on SR-456 via Jira DVCS (independent of integration webhook)

## FR-3: MR-to-Jira Auto-Linking

**Priority:** Critical  
**When:** MR title, description, or branch name contains a Jira issue key matching configured project keys  
**Then:** The MR appears in the Jira issue's Development Panel  
**Configured keys:** PUB, AM, AU, COM, FUN, PWM, RMD, SR, STABI, TJ, P3AP  
**Issue key regex:** `[A-Z]+-\d+` (GitLab default)

### Scenario: MR title with issue key links automatically

**Given** an MR with title `PUB-100: Update dashboard`  
**When** the MR is created  
**Then** the MR appears in the Development Panel of PUB-100 in Jira

### Scenario: Branch name with issue key links automatically

**Given** a branch named `feature/SR-200-login-fix`  
**When** an MR is created from this branch  
**Then** the MR links to SR-200 regardless of title content

### Scenario: Multiple issue keys in MR title link all

**Given** an MR title `SR-300, STABI-100: Shared auth fix`  
**When** the MR is created  
**Then** the MR appears in Development Panels for both SR-300 and STABI-100

## FR-4: Integration Configuration Consistency

**Priority:** High  
**When:** Both projects checked via `glab api projects/{id}/integrations/jira`  
**Then:** Both return identical event configs

| Event Flag | Value |
|------------|-------|
| `merge_requests_events` | `true` |
| `comment_on_event_enabled` | `true` |
| All other `*_events` flags | `false` |
| `jira_issue_transition_id` | `""` (empty) |
| `project_keys` | `["PUB","AM","AU","COM","FUN","PWM","RMD","SR","STABI","TJ","P3AP"]` |

### Scenario: Both projects have identical config

**Given** both project 231 and 232 have been updated  
**When** their integration configs are compared  
**Then** all event flags, project_keys, and URL values are identical

## FR-5: No Auto-Transitions on MR Actions

**Priority:** Medium  
**When:** MR is merged or closed  
**Then:** Jira issue status is NOT automatically changed (jira_issue_transition_id remains empty)  
**Rationale:** Prevents accidental status changes from CI-only MRs

## NFR-1: Zero Downtime

The integration update via GitLab API is applied atomically. No service interruption.

## NFR-2: Reversible

All changes can be reverted via the same API endpoint. Current config is saved before modification.

## Dependencies

- GitLab Jira Integration (built-in, already active on both projects)
- `glab` CLI v1.94.0+ authenticated to `git.ecomedic.vn`
- Jira account `lekhanhvinh@phillip.com.sg` with access to all 11 project keys
