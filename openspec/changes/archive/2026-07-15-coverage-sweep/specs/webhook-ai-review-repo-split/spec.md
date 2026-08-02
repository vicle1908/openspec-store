## ADDED Requirements

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
