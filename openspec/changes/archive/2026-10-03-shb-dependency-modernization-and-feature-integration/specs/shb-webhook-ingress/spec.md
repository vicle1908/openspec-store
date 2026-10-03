# shb-webhook-ingress Specification Delta

## MODIFIED Requirements

### Requirement: Event Webhook Ingress and Dead Letter Queue
The `shb-webhook-receiver` service SHALL ingest HTTP webhook events from GitLab and Jira using FastAPI `>=0.142.2` with async lifespan context management, validating HMAC signatures and routing failed event deliveries to an inspectable Dead Letter Queue (DLQ).

#### Scenario: Webhook event receipt and dispatch
- **WHEN** a valid GitLab pipeline or MR event webhook is received
- **THEN** the ingress service validates the payload signature and queues the event for downstream agent processing

#### Scenario: Modern lifespan lifecycle initialization
- **WHEN** the webhook receiver application starts and stops
- **THEN** FastAPI and Uvicorn SHALL initialize and cleanly dispose of database connection pools and background workers via the `@asynccontextmanager` lifespan handler

#### Scenario: Dead Letter Queue replay
- **WHEN** an operator invokes the replay DLQ command via `replay-dlq`
- **THEN** previously failed webhook payloads are re-evaluated and dispatched to target handlers
