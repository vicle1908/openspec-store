# webhook-public-ingress-failover Specification

## Purpose
TBD - created by archiving change coverage-sweep. Update Purpose after archive.
## Requirements
### Requirement: The primary public ingress URL MUST be a Tailscale Funnel endpoint

The primary URL SHALL be `https://les-mac-mini.tailc6b508.ts.net/gitlab-webhook`, served by
Tailscale Funnel in front of the local `webhook-receiver` on `127.0.0.1:8080`.

#### Scenario: Primary URL is the default state on a fresh install

- **WHEN** `~/.tdt/state/webhook-primary.state` does not exist
- **THEN** the receiver SHALL treat the Tailscale URL as primary
- **AND** the dashboard SHALL render the Tailscale URL in its header line.

#### Scenario: Primary URL receives traffic with no special headers

- **WHEN** GitLab delivers a webhook to the Tailscale URL
- **THEN** the receiver SHALL NOT require the `X-TDT-Secondary` header
- **AND** it SHALL log `ingress=primary` on the request.

### Requirement: A hot-spare public URL MUST be served by a running ngrok agent

The ngrok agent SHALL be installed and running on the local machine with a stable free-tier
hostname, exposing `http://127.0.0.1:8080` to the public internet. The hostname SHALL be
recorded in `~/.tdt/state/webhook-secondary.url`.

#### Scenario: Secondary URL serves a healthy receiver locally

- **WHEN** the operator runs `curl -sS https://<ngrok-hostname>/health`
- **THEN** the response SHALL be HTTP 200 with `{"status":"healthy",...}` within 1000ms.

#### Scenario: Secondary URL is not enabled by default

- **WHEN** `~/.tdt/state/webhook-primary.state` contains `tailscale`
- **THEN** the receiver SHALL NOT expect deliveries from the secondary URL
- **AND** the dashboard SHALL report the secondary URL as `standby`.

### Requirement: The on-disk state file MUST select which URL is currently primary

`~/.tdt/state/webhook-primary.state` SHALL contain a single token: either `tailscale` or
`ngrok`. The receiver SHALL read this file on startup and refresh every 30 seconds.

#### Scenario: Flipping to ngrok as primary

- **WHEN** the operator writes `ngrok` to `~/.tdt/state/webhook-primary.state`
- **THEN** within 30 seconds the dashboard SHALL render the ngrok URL as primary
- **AND** within 60 seconds the self-test loop SHALL target the ngrok URL.

#### Scenario: Flipping back to Tailscale

- **WHEN** the operator writes `tailscale` to `~/.tdt/state/webhook-primary.state`
- **THEN** within 30 seconds the dashboard SHALL restore the Tailscale URL as primary
- **AND** the secondary URL SHALL return to `standby` status.

### Requirement: Secondary-URL deliveries MUST carry the X-TDT-Secondary handshake header

The project webhook configuration for the secondary URL MUST send `X-TDT-Secondary: 1`
on every request. The receiver MUST treat the presence of this header as a signal that
the delivery came from the secondary ingress.

The receiver MUST log the ingress source (`ingress=primary` or `ingress=secondary`)
on every `/gitlab-webhook` delivery so the dashboard, incident-report skill, and
self-test observations can distinguish the two paths. The header is **observability
metadata only** — it does not grant dedupe bypass (see the
`webhook-ai-review-repo-split` spec, which requires dedupe on every `Merge Request
Hook` delivery regardless of ingress).

> **Operational note — both hooks always fire.** GitLab does not conditionalize a
> project webhook on an external file or signal, so once the primary hook (id 32 on
> project 231, 33 on 232) and the secondary hook (id 42 on 231, 43 on 232) are
> installed, every MR event reaches the receiver through **both** ingresses. The
> `~/.tdt/state/webhook-primary.state` file is an operator-facing indicator that
> changes how the receiver renders `/health/ingress` and how the self-test loop
> targets the public edge; it does **not** toggle the GitLab hooks. Idempotency is
> therefore the receiver's sole defense against duplicate dispatches — the dedupe
> key (`project_id`, `MR IID`, `event_type`) MUST be applied uniformly.

#### Scenario: Receiver identifies a secondary delivery

- **WHEN** a request arrives at `/gitlab-webhook` with `X-TDT-Secondary: 1`
- **THEN** the receiver SHALL log `ingress=secondary`
- **AND** it SHALL apply the dedupe check (NOT skip it — see operational note)
- **AND** it SHALL tag the agentmemory observation with `ingress=secondary`.

#### Scenario: Missing handshake header on a secondary path is treated as primary

- **WHEN** a request arrives at `/gitlab-webhook` with no `X-TDT-Secondary` header
- **THEN** the receiver SHALL treat it as a primary delivery
- **AND** it SHALL apply the dedupe check.

#### Scenario: Concurrent primary + secondary deliveries for the same event dedupe to one dispatch

- **WHEN** the receiver receives the same `Merge Request Hook` payload within the
  10-minute dedupe TTL — once via the primary ingress and once via the secondary
  ingress (separated by ≤ 1 second, as observed in production)
- **THEN** the first delivery SHALL be a dedupe miss and SHALL dispatch
- **AND** the second delivery SHALL be a dedupe hit and SHALL return
  HTTP 200 with `{"status": "duplicate", ...}` without dispatching
- **AND** the receiver SHALL NOT post more than one Jira impact comment for the
  underlying MR (verified by `impact_comment_posted` log count).

