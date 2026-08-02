# gitlab-hook-health-dashboard Specification

## Purpose

Define the contract for the GitLab hook health dashboard: a one-screen summary of recent
webhook delivery health per project, designed to be readable in 10 seconds during an
incident.

## Requirements

## ADDED Requirements

### Requirement: The dashboard MUST summarize the last 24 hours of deliveries per project

`tdt-tools/gitlab-hook-dashboard.py` SHALL query `glab api projects/<id>/hooks/<id>/events`
for each configured project and classify the events by HTTP status.

#### Scenario: Healthy dashboard output

- **WHEN** the operator runs the dashboard script with no arguments
- **THEN** the output SHALL be a markdown table with one row per project+hook
- **AND** each row SHALL include: project name, hook URL (truncated), total events in
  the last 24h, count by status (200, 4xx, 5xx, internal error), and the timestamp of
  the most recent event.

#### Scenario: Project with no recent events

- **WHEN** a project has zero events in the last 24h
- **THEN** the row SHALL show `events=0` and a warning icon (e.g., ⚠️) to indicate
  silent drop.

### Requirement: The dashboard MUST read the current primary URL from the state file

The dashboard's header line SHALL show the value of
`~/.tdt/state/webhook-primary.state` and the corresponding public URL.

#### Scenario: State file shows tailscale as primary

- **WHEN** the state file contains `tailscale`
- **THEN** the header SHALL read
  `Primary: tailscale (https://les-mac-mini.tailc6b508.ts.net)`.

#### Scenario: State file shows ngrok as primary

- **WHEN** the state file contains `ngrok`
- **THEN** the header SHALL read
  `Primary: ngrok (https://<hostname-from-secondary.url>)`.

### Requirement: The dashboard MUST include the latest self-test observation

The dashboard SHALL query agentmemory for the most recent self-test observation of kind
`selftest` and display it as a one-line footer.

#### Scenario: Latest self-test was ok

- **WHEN** the most recent self-test observation is `{status: "ok", latency_ms: 28}`
- **THEN** the footer SHALL read
  `Self-test: ok @ <iso> (28ms)`.

#### Scenario: Latest self-test was down

- **WHEN** the most recent self-test observation is `{status: "down", error: "timeout"}`
- **THEN** the footer SHALL read
  `Self-test: DOWN @ <iso> — timeout` in red ANSI color.
