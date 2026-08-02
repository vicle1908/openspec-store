# webhook-receiver-dlq Specification

## Purpose

Define the dead-letter sink contract for `webhook-receiver`: when the downstream
`ai-review` call fails twice in a row for the same `(project_id, MR IID, event_type)`,
the original payload is preserved to disk so it can be replayed.

## Requirements

## ADDED Requirements

### Requirement: Two consecutive downstream failures MUST write the payload to the DLQ

The DLQ writer MUST be invoked when `webhook-receiver` calls `ai-review` and the response
is non-2xx (or the call times out), and the same `(project_id, MR IID, event_type)` has
also failed on the immediately preceding delivery within 10 minutes. The first failure
MUST NOT trigger a DLQ write; only the second consecutive failure MUST write the
payload to `~/.tdt/state/webhook-deadletter/<UTC-timestamp>.json`.

#### Scenario: First failure is not DLQ'd

- **WHEN** the receiver dispatches to `ai-review` and gets HTTP 503
- **THEN** the failure SHALL be recorded in memory only
- **AND** no file SHALL be written to the DLQ directory.

#### Scenario: Second consecutive failure DLQs the payload

- **WHEN** the same `(project_id, MR IID, event_type)` delivery fails again within
  10 minutes of the first failure
- **THEN** the second failure SHALL write
  `~/.tdt/state/webhook-deadletter/<ISO-timestamp>.json`
- **AND** the file SHALL contain the original GitLab payload, the `X-Handoff-Id`,
  and the failure reason
- **AND** the receiver SHALL emit a `dlq.received` event to agentmemory with the
  file path.

#### Scenario: Successful dispatch between two failures resets the failure counter

- **WHEN** a delivery for the same `(project_id, MR IID, event_type)` succeeds
- **THEN** the failure counter SHALL be reset to zero
- **AND** the next failure SHALL be treated as a first failure (no DLQ write).

### Requirement: The DLQ directory MUST be capped at 10,000 files

A daily reaper LaunchAgent SHALL enforce a 10,000-file cap on
`~/.tdt/state/webhook-deadletter/` by deleting the oldest files first.

#### Scenario: Cap enforcement on a healthy cap

- **WHEN** the DLQ directory contains 9,999 files and a new file is written
- **THEN** the reaper SHALL take no action (under cap).

#### Scenario: Cap enforcement on an over-cap condition

- **WHEN** the DLQ directory contains 10,500 files
- **THEN** the reaper SHALL delete the 500 oldest files based on filename timestamp
- **AND** the reaper SHALL log the deletion count to syslog.

### Requirement: DLQ files MUST be replayable via a documented CLI

A `tdt-tools/replay-dlq.py` script MUST accept a DLQ file path and re-POST the original
payload to the local `/gitlab-webhook` route with the original headers.

#### Scenario: Replay of a single DLQ file

- **WHEN** the operator runs `tdt-tools/replay-dlq.py ~/.tdt/state/webhook-deadletter/2026-06-15T11-00-00Z.json`
- **THEN** the script SHALL read the file
- **AND** it SHALL POST the original payload to `http://127.0.0.1:8080/gitlab-webhook`
- **AND** it SHALL print the resulting HTTP status code.

#### Scenario: Replay of a corrupt DLQ file

- **WHEN** the operator runs the replay script on a file that is not valid JSON
- **THEN** the script SHALL exit non-zero with a clear error message
- **AND** it SHALL NOT POST anything to the receiver.
