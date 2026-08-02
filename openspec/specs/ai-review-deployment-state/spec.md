# ai-review-deployment-state Specification

## Purpose

Define the live operational contract for the split AI review architecture in the
canonical workspace: `webhook-receiver` owns ingress and Jira guard routing,
while `ai-review` owns review intake, orchestration, and GitLab publication.
This specification is the source of truth for what "AI review is correctly
deployed" means.

Historical completion reports under
`openspec/changes/archive/agent-completion-reports/` are retained for provenance
only and SHALL NOT be treated as live deployment contracts.

## Requirements

### Requirement: AI review runtime SHALL be split into two launchd-managed services

Production runtime SHALL use two independent launchd services:
`com.tdt.webhook-receiver` on `127.0.0.1:8080` and `com.tdt.ai-review` on
`127.0.0.1:8090`. PM2 and `python -m uvicorn` launch patterns are prohibited.

#### Scenario: Both split services are running

- **WHEN** the system is in steady state
- **THEN** `launchctl print gui/$(id -u)/com.tdt.webhook-receiver` SHALL show `state = running` with a numeric PID
- **AND** `launchctl print gui/$(id -u)/com.tdt.ai-review` SHALL show `state = running` with a numeric PID
- **AND** exactly one process SHALL listen on TCP `127.0.0.1:8080`
- **AND** exactly one process SHALL listen on TCP `127.0.0.1:8090`

#### Scenario: Launchers execute runtime venv uvicorn directly

- **WHEN** deployment launchers are inspected
- **THEN** `deployments/webhook-receiver/bin/webhook-receiver-launcher.sh` SHALL `exec` `deployments/webhook-receiver/app/.venv/bin/uvicorn webhook_receiver.api.app:app`
- **AND** `deployments/ai-review/bin/ai-review-launcher.sh` SHALL `exec` `deployments/ai-review/app/.venv/bin/uvicorn ai_review.api.app:app`
- **AND** neither launcher SHALL rely on `source .venv/bin/activate`, `PYTHONHOME`, PM2, or `python -m uvicorn`

### Requirement: Split runtime ownership SHALL follow service boundaries

`webhook-receiver` SHALL own public webhook ingress and Jira transition guard
routes, while `ai-review` SHALL own review intake (`/reviews/gitlab-mr`),
idempotency, reviewer orchestration, and GitLab note publication.

#### Scenario: Webhook-receiver stays ingress-focused

- **WHEN** the ingress app module `webhook_receiver.api.app` handles MR events
- **THEN** it SHALL validate the GitLab webhook token and schedule asynchronous handoff work
- **AND** it SHALL NOT execute reviewer orchestration directly in-process

#### Scenario: Ai-review owns orchestration and publication

- **WHEN** `ai_review.api.app` accepts an intake request
- **THEN** it SHALL validate dispatch auth, apply idempotency reservation, and enqueue orchestration via `ReviewOrchestrator`
- **AND** GitLab review note create/update behavior SHALL occur from `ai-review` code paths

### Requirement: Diff grounding SHALL prefer local git with explicit degraded fallback reasons

`ai-review` SHALL prefer workspace-local git/worktree diffs and degrade to GitLab
compare with machine-readable metadata when source refs cannot be resolved.

#### Scenario: Missing source refs degrade with explicit reason and compare fallback

- **WHEN** worktree preparation cannot resolve source refs for the incoming MR
  (for example stale or deleted source branch refs)
- **THEN** review context metadata SHALL set `degraded_step` to `worktree_prepare`
- **AND** `degraded_reason` SHALL start with `source_ref_missing:`
- **AND** `diff_source` SHALL switch to `gitlab_compare` when compare payload is available
- **AND** orchestration SHALL continue instead of failing intake.

### Requirement: GitLab webhook ingress SHALL validate auth and return fast acceptance

`POST /gitlab-webhook` in `webhook-receiver` SHALL authenticate using
`X-Gitlab-Token` against `GITLAB_WEBHOOK_SECRET`/`WEBHOOK_SECRET`, return fast
acceptance for valid events, and reject invalid auth without scheduling work.

#### Scenario: Valid Merge Request hook is accepted

- **WHEN** GitLab posts `X-Gitlab-Event: Merge Request Hook` and a valid `X-Gitlab-Token`
- **THEN** ingress SHALL respond with HTTP `200`
- **AND** the response body SHALL include `status: "accepted"`, `handoff_id`, and `trace_id`
- **AND** MR processing SHALL be scheduled asynchronously so response flush is not blocked by review execution

#### Scenario: Invalid token is rejected

- **WHEN** the incoming `X-Gitlab-Token` does not match configured webhook secret
- **THEN** ingress SHALL return HTTP `401`
- **AND** no review handoff SHALL be scheduled

### Requirement: Webhook-to-ai-review handoff SHALL use authenticated local intake

For eligible MR actions, webhook ingress SHALL dispatch to
`POST http://127.0.0.1:${AI_REVIEW_PORT:-8090}/reviews/gitlab-mr` with
`X-AI-Review-Dispatch-Secret`, `X-Handoff-Id`, and `X-Trace-Id` headers plus
normalized MR metadata payload.

#### Scenario: Eligible MR actions dispatch handoff

- **WHEN** MR action is `open`, `update`, or `reopen` and `last_commit.id` is present
- **THEN** webhook ingress SHALL POST a handoff payload containing `project.id`, `project.path_with_namespace`, `merge_request.iid`, `merge_request.commit_sha`, branches, and action metadata
- **AND** dispatch secret header SHALL be sourced from `AI_REVIEW_DISPATCH_SECRET`

#### Scenario: Ineligible events are skipped without dispatch

- **WHEN** MR state is `merged`/`closed`, action is outside supported set, or commit SHA is missing
- **THEN** ingress SHALL skip handoff dispatch
- **AND** it SHALL return normal webhook acceptance behavior without enqueuing review orchestration

### Requirement: Ai-review intake SHALL enforce dispatch auth and idempotency

`POST /reviews/gitlab-mr` in `ai-review` SHALL require a valid dispatch secret
(`X-AI-Review-Dispatch-Secret`) and SHALL reserve idempotency by logical key so
duplicates do not enqueue duplicate runs.

#### Scenario: Missing or invalid dispatch secret is rejected

- **WHEN** dispatch secret header is missing
- **THEN** intake SHALL return HTTP `401`
- **AND** orchestration SHALL NOT be enqueued
- **AND** **WHEN** dispatch secret is present but mismatched
- **THEN** intake SHALL return HTTP `403`

#### Scenario: Duplicate requests are acknowledged without duplicate enqueue

- **WHEN** two intake calls share the same logical key (`project`, `mr_iid`, `action`, `commit_sha`)
- **THEN** the first call SHALL return `status: "accepted"` with `duplicate: false`
- **AND** later calls within TTL SHALL return `status: "duplicate"` with `duplicate: true`
- **AND** only the first accepted call SHALL enqueue `ReviewOrchestrator`

### Requirement: Reviewer orchestration SHALL run in ai-review with oversize controls

`ai-review` SHALL build reviewer set from enable flags, run selected reviewers,
and apply prompt-size policy from
`AI_REVIEW_PROMPT_OVERSIZE_THRESHOLD_BYTES`/`PROMPT_OVERSIZE_THRESHOLD_BYTES`.

#### Scenario: Reviewer set follows enable flags

- **WHEN** reviewer toggles are enabled for `kimi`, `claude`, `codex`, `pi`, `codescan`
- **THEN** `ReviewOrchestrator` SHALL construct reviewer instances for each enabled CLI
- **AND** disabled CLIs SHALL be excluded from the run plan

#### Scenario: Oversized prompts use compact mode across selected reviewers

- **WHEN** largest prompt exceeds the configured oversize threshold and threshold is greater than `0`
- **THEN** reviewer plans SHALL start with compact prompt mode for selected reviewers
- **AND** fallback prompt mode SHALL be applied per reviewer plan when configured
- **AND** **WHEN** threshold is `0`
- **THEN** size-based compact-mode forcing SHALL be disabled

### Requirement: Review publication SHALL preserve marker-based update semantics

Published MR notes from `ai-review` SHALL use marker-based upsert semantics so
new findings update the existing automation note instead of creating unlimited
duplicates.

#### Scenario: Marker-based post-or-update is applied

- **WHEN** orchestration generates summary lines for a merge request
- **THEN** `GitLabReviewPoster.post_or_update` SHALL post or update using marker `<!-- mr-auto-review -->`
- **AND** publication status SHALL be logged with handoff context

### Requirement: Health contracts SHALL expose split-service readiness

Both services SHALL expose health endpoints with service-specific checks and the
ingress health response SHALL include ai-review reachability status.

#### Scenario: Webhook-receiver health includes ai-review dispatch probe

- **WHEN** `GET /health` is called on webhook-receiver
- **THEN** the response SHALL include top-level `status` and `checks`
- **AND** it SHALL include `ai_review_dispatch` with probe URL, reachability flag, and status code

#### Scenario: Ai-review health includes reviewer and dependency checks

- **WHEN** `GET /health` is called on ai-review
- **THEN** the response SHALL include `service: "ai-review"`, `version`, and overall `status`
- **AND** checks SHALL include `omniroute_proxy`, `kimi_cli`, `circuit_breaker`, `sessions`, `reviewer_enablement`, `reviewer_probes`, and `codescan`

### Requirement: Deployment verification SHALL enforce split runtime provenance

Each service deploy script SHALL verify lock alignment, runtime copy integrity,
launchd process state, single-port listener, and `/health` before declaring
success. Generated runtime files under `deployments/*/app` SHALL be treated as
artifact outputs, not manual edit targets.

#### Scenario: Deploy script enforces lock and runtime checks

- **WHEN** `webhook-receiver/scripts/deploy.sh` or `ai-review/scripts/deploy.sh` runs
- **THEN** source repos SHALL pass `uv lock --check` before runtime install
- **AND** runtime install SHALL use `uv sync --frozen --no-dev --no-editable --compile-bytecode`
- **AND** deploy SHALL fail non-zero if launchd, listener uniqueness, or `/health` verification fails

#### Scenario: Deployment manifests capture rollout provenance

- **WHEN** deployment completes successfully
- **THEN** each service SHALL write `deployment-manifest.json` and snapshot hashes under `deployments/<service>/state/`
- **AND** those manifests SHALL be the rollout provenance record for operational audits

### Requirement: Historical planning artifacts SHALL remain read-only archive

Completed planning artifacts SHALL remain under
`openspec/changes/archive/agent-completion-reports/` as immutable historical
references and SHALL NOT be edited to represent current runtime state.

#### Scenario: Live state comes from spec and service health

- **WHEN** operators verify current AI review behavior
- **THEN** this live spec and current `/health` outputs SHALL be treated as source of truth
- **AND** archived completion reports SHALL remain unchanged

### Requirement: New service behavior changes SHALL be tracked as OpenSpec changes

Any future behavior change SHALL be tracked in
`openspec/changes/<change-name>/` with proposal, design, specs, and tasks when
it touches webhook ingress, Jira guard, ai-review intake, orchestration,
publication, or deployment contracts.

#### Scenario: Change request is tracked outside live spec folder

- **WHEN** a new feature or contract update is proposed
- **THEN** authors SHALL create a dedicated `openspec/changes/<change-name>/` folder
- **AND** they SHALL not place active change artifacts inside `openspec/specs/ai-review-deployment-state/`
