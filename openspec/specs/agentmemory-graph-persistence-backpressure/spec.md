# agentmemory-graph-persistence-backpressure Specification

## Purpose
Bound graph extraction persistence so iii state writes remain recoverable under backlog pressure while observation capture, summarization, consolidation, and session completion continue independently.

## Requirements

### Requirement: Graph extraction SHALL apply bounded backpressure

The installed runtime SHALL use graph extraction with awareness of persistence timeouts. Graph extraction SHALL be controlled by the `GRAPH_EXTRACTION_ENABLED` flag. When enabled, heuristic extraction always runs; LLM extraction runs only when the flag is true. Persistence timeouts from `state::set` are non-fatal and shall be monitored. The operator may disable graph extraction by setting `GRAPH_EXTRACTION_ENABLED=false` if persistence timeouts become problematic.

#### Scenario: Large session is graph-extracted

- **WHEN** a completed session contains more observations than the configured graph batch size
- **THEN** graph extraction SHALL split the work into bounded batches
- **AND** concurrent graph persistence SHALL remain within the configured limit
- **AND** session completion SHALL not wait for the entire graph backlog to drain

#### Scenario: Graph backlog exceeds capacity

- **WHEN** pending graph work exceeds the configured queue capacity
- **THEN** new graph work SHALL be deferred, coalesced, or rejected with an explicit diagnostic
- **AND** observation capture SHALL continue
- **AND** the runtime SHALL not create unbounded in-memory work.

### Requirement: Graph persistence failure SHALL be isolated

A graph persistence timeout or state-store failure MUST be recorded with bounded retry/defer behavior and MUST NOT block observation capture, summarization, consolidation, or session-end acknowledgement.

#### Scenario: State write times out

- **WHEN** a graph node or edge write exceeds the iii invocation deadline
- **THEN** the graph batch SHALL be marked failed or deferred
- **AND** the failure SHALL include batch and latency diagnostics without memory payloads or credentials
- **AND** session-end processing SHALL remain successful.

#### Scenario: Graph persistence recovers

- **WHEN** a deferred graph batch is retried after the state store becomes healthy
- **THEN** the batch SHALL complete without duplicating graph nodes or edges
- **AND** the retry count and recovery latency SHALL be observable.

### Requirement: Graph runtime diagnostics SHALL be safe and actionable

The runtime SHALL expose or log bounded graph queue depth, batch count, timeout count, retry/defer count, and last recovery status without emitting credentials, transcript contents, or raw memory payloads.

#### Scenario: Operator checks graph health

- **WHEN** an operator reviews graph persistence diagnostics
- **THEN** they SHALL be able to distinguish provider failure, state-store timeout, queue saturation, and successful recovery
- **AND** diagnostic output SHALL not contain secrets or observation bodies.

### Requirement: Graph persistence SHALL support backup-first rollout and rollback

Graph persistence runtime settings SHALL be backed up before modification and SHALL be restorable without migrating or rewriting the persistent state database.

#### Scenario: Configuration rollout fails

- **WHEN** graph persistence configuration causes startup failure or health degradation
- **THEN** the operator SHALL be able to restore the prior configuration and restart the launchd-managed service
- **AND** observation capture and session-end health SHALL be re-verified after rollback.
