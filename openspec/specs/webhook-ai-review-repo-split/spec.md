# webhook-ai-review-repo-split Specification

## Purpose

Define the repository and runtime ownership boundary between `webhook-receiver`
and `ai-review` in the canonical workspace. This specification is the source of
truth for split-service responsibilities and handoff contracts.
## Requirements
### Requirement: Ingress ownership SHALL remain in webhook-receiver

`webhook-receiver` SHALL own webhook ingress, token validation, async handoff
dispatch, and Jira guard routes.

#### Scenario: GitLab webhook handled at ingress

- **WHEN** GitLab sends `POST /gitlab-webhook`
- **THEN** `webhook_receiver.api.app` SHALL validate `X-Gitlab-Token`
- **AND** it SHALL return acceptance/rejection responses from ingress
- **AND** it SHALL NOT run reviewer orchestration inline.

#### Scenario: Jira guard stays ingress-owned

- **WHEN** Jira transition events arrive
- **THEN** routes under `/webhooks/jira/*` SHALL be served by webhook-receiver
- **AND** guard policy evaluation SHALL remain in `webhook_receiver/jira_guard`.

### Requirement: Review-domain ownership SHALL remain in ai-review

`ai-review` SHALL own authenticated review intake, idempotency, reviewer
execution, review synthesis, and GitLab note publication.

#### Scenario: Authenticated intake endpoint

- **WHEN** ingress forwards review work to `POST /reviews/gitlab-mr`
- **THEN** `ai_review.api.app` SHALL require dispatch secret authentication
- **AND** it SHALL reserve idempotency and enqueue orchestration.

#### Scenario: Publication performed by ai-review

- **WHEN** findings are ready for publication
- **THEN** `ai-review` SHALL post or update the managed MR note marker
  `<!-- mr-auto-review -->`
- **AND** webhook-receiver SHALL NOT publish managed review notes directly.

### Requirement: Inter-service handoff SHALL be local, authenticated, and traceable

Handoff from ingress to review service SHALL use loopback HTTP with dispatch
secret and correlation identifiers.

#### Scenario: Correlated local dispatch

- **WHEN** ingress dispatches eligible MR actions
- **THEN** it SHALL call `http://127.0.0.1:${AI_REVIEW_PORT:-8090}/reviews/gitlab-mr`
- **AND** it SHALL include `X-AI-Review-Dispatch-Secret`, `X-Handoff-Id`, and
  `X-Trace-Id` headers
- **AND** payload SHALL include project path/ID, MR IID, action, and commit SHA.

### Requirement: Deployments SHALL remain split and workspace-local

Each service SHALL deploy from its own source repo into its own workspace-local
runtime tree under `$HOME/Developer/tdt/deployments/`.

#### Scenario: Separate deploy entrypoints

- **WHEN** operators deploy services
- **THEN** they SHALL run `webhook-receiver/scripts/deploy.sh` for ingress
- **AND** they SHALL run `ai-review/scripts/deploy.sh` for review service
- **AND** both deploy scripts SHALL reject legacy cloud source/runtime paths.

#### Scenario: Provenance artifacts per service

- **WHEN** deployment completes
- **THEN** each service SHALL write `state/deployment-manifest.json`
- **AND** each service SHALL write source/runtime snapshot hashes under its own
  deployment `state/` directory.

### Requirement: Documentation references SHALL resolve to live split contracts

Docs in `webhook-receiver` and workspace metadata SHALL reference existing,
current split-service runbook/spec paths.

#### Scenario: Canonical split references

- **WHEN** readers follow runbook/spec links from repo docs
- **THEN** links to `openspec/specs/ai-review-deployment-state/spec.md`,
  `openspec/specs/webhook-ai-review-repo-split/spec.md`, and
  `docs/workflows/webhook-ai-review-dual-service-runbook.md` SHALL resolve.

### Requirement: Generated runtime trees SHALL be treated as artifacts

Files under `deployments/*/app/` SHALL be treated as generated runtime outputs,
not source-of-truth code.

#### Scenario: Source-first editing policy

- **WHEN** an operator needs to change behavior
- **THEN** changes SHALL be made in source repos (`webhook-receiver` or
  `ai-review`) and redeployed
- **AND** generated files under `deployments/*/app/` SHALL NOT be edited
  directly.

### Requirement: Dispatched MR actions MUST be idempotent end-to-end

`webhook-receiver` SHALL deduplicate inbound GitLab webhook deliveries by
`(project_id, MR IID, event_type)` with a 10-minute TTL before dispatching to
`ai-review`, so a flapping DERP edge that retries the same event twice does not cause
two review runs. The dedupe check applies to **every** `Merge Request Hook` delivery
regardless of the ingress it arrived on (primary or `X-TDT-Secondary: 1`); see the
`webhook-public-ingress-failover` spec for why both ingresses always fire in
production.

#### Scenario: Dedupe hit on a duplicate delivery

- **WHEN** the receiver receives a delivery for `(project_id=231, mr_iid=42,
  event_type=merge_request)` within 10 minutes of a previous delivery with the same
  key
- **THEN** it SHALL return HTTP 200 to GitLab
- **AND** it SHALL NOT dispatch to `ai-review`
- **AND** it SHALL log `dedupe=hit`.

#### Scenario: Dedupe miss on a new event

- **WHEN** the receiver receives a delivery for `(project_id=231, mr_iid=42,
  event_type=note)` more than 10 minutes after the last merge_request delivery
- **THEN** it SHALL treat it as a new event and dispatch to `ai-review`.

#### Scenario: Dedupe applies to the secondary ingress

- **WHEN** the receiver receives two deliveries for `(project_id=231, mr_iid=42,
  event_type=merge_request)` within 10 minutes, the first without
  `X-TDT-Secondary: 1` (primary) and the second with `X-TDT-Secondary: 1`
  (secondary)
- **THEN** the primary delivery SHALL dispatch
- **AND** the secondary delivery SHALL return HTTP 200 with
  `{"status": "duplicate", ...}` without dispatching
- **AND** the secondary delivery SHALL be logged with `ingress=secondary,
  dedupe=hit`.

### Requirement: Downstream `ai-review` dispatch MUST be bounded by a 30-second timeout

The dispatch call from `webhook-receiver` to `ai-review` SHALL be bounded by
`AI_REVIEW_DOWNSTREAM_TIMEOUT_SECONDS` (default 30). A timeout SHALL be counted as a
dispatch failure and SHALL surface in the DLQ trigger logic.

#### Scenario: Dispatch times out

- **WHEN** the `ai-review` call does not respond within 30 seconds
- **THEN** the receiver SHALL cancel the request
- **AND** it SHALL record the failure with reason `timeout`
- **AND** it SHALL return HTTP 200 to GitLab (so GitLab does not retry).

#### Scenario: Dispatch completes in time

- **WHEN** the `ai-review` call responds within 30 seconds with HTTP 2xx
- **THEN** the receiver SHALL treat it as success and return HTTP 200 to GitLab.

