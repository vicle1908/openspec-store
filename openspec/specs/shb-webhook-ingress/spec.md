# shb-webhook-ingress Specification

## Purpose
Provides event-driven webhook ingress, incident dispatching, and Jira project delivery tracking for Saigon - Hanoi Bank (SHB) software engineering.

## Requirements

### Requirement: Event Webhook Ingress and Dead Letter Queue
The `shb-webhook-receiver` service SHALL ingest HTTP webhook events from GitLab and Jira, validating HMAC signatures and routing failed event deliveries to an inspectable Dead Letter Queue (DLQ).

#### Scenario: Webhook event receipt and dispatch
- **WHEN** a valid GitLab pipeline or MR event webhook is received
- **THEN** the ingress service validates the payload signature and queues the event for downstream agent processing

#### Scenario: Dead Letter Queue replay
- **WHEN** an operator invokes the replay DLQ command via `replay-dlq`
- **THEN** previously failed webhook payloads are re-evaluated and dispatched to target handlers

### Requirement: Jira Project Delivery and Progress Reporting
The `shb-jira-tools` system SHALL provide interfaces for executing JQL queries, creating ADF formatted comments, and calculating sprint and epic progress metrics for SHB teams.

#### Scenario: Epic delivery progress report
- **WHEN** an engineer executes `shb-jira epic-report --epic-key <key>`
- **THEN** the tool fetches all linked child issues, computes completed versus remaining story points, and prints an executive progress breakdown

### Requirement: Command-Line Interface Entrypoints
The packages SHALL expose executable CLI entrypoints `shb-webhook-receiver`, `replay-dlq`, and `shb-jira` for operational monitoring and reporting.

#### Scenario: Command-line healthcheck execution
- **WHEN** an operator executes `shb-webhook-receiver --help` or `shb-jira --help`
- **THEN** the CLI outputs available commands and flags with exit code 0
