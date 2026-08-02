# webhook-incident-report Specification

## Purpose

Define the contract for the `incident-report` skill: a reproducible 1-page postmortem
generator that takes a time window and a project ID and emits a markdown report from the
dashboard data plus funnel/ngrok logs.

## Requirements

## ADDED Requirements

### Requirement: The skill MUST be invocable from the agent's chat UI

The `incident-report` skill SHALL live at
`~/.agents/skills/incident-report/SKILL.md` and be discoverable via the standard skill
flow.

#### Scenario: Operator invokes the skill by name

- **WHEN** the operator says "incident report for project 231, last 2 hours"
- **THEN** the agent SHALL invoke the `incident-report` skill
- **AND** the skill SHALL produce a markdown report.

### Requirement: The report MUST include a timeline of failures

The skill SHALL read self-test observations from
`~/.tdt/state/webhook-selftest-observations.jsonl` and DLQ events from
`~/.tdt/state/webhook-deadletter/` (one file per failed delivery, JSON
containing the original payload + handoff_id + reason), filter to the
requested window, sort them chronologically, and emit them as a timeline
section.

#### Scenario: Window with multiple failures

- **WHEN** the operator requests a 2-hour window that contains 6 self-test `down`
  observations and 2 DLQ events
- **THEN** the report SHALL list all 8 events with timestamps and reasons in
  chronological order.

### Requirement: The report MUST list affected MRs

The skill SHALL cross-reference the DLQ events and hook events with the GitLab MRs they
referenced and emit a table of MR IID, last-known status, and whether the review ran.

#### Scenario: MR with successful review during the window

- **WHEN** an MR was opened during the window and a successful review ran
- **THEN** the table SHALL show `MR IID: <n> | reviewed: yes | notes posted: <count>`.

#### Scenario: MR with no review during the window

- **WHEN** an MR was opened during the window but no review ran
- **THEN** the table SHALL show `MR IID: <n> | reviewed: NO (lost) | notes posted: 0`
  with a `⚠️ LOST` tag.

### Requirement: The report MUST recommend follow-up actions

The report SHALL end with a `## Recommended Follow-ups` section containing 1-3 actionable
items derived from the data (e.g., "rotate state file to ngrok", "replay 2 DLQ files",
"open Jira ticket for review gap").

#### Scenario: Follow-ups derived from state file value

- **WHEN** the state file is `tailscale` and the self-test has been down for >15min
- **THEN** the follow-ups SHALL include
  `1. Flip ~/.tdt/state/webhook-primary.state to ngrok`.

#### Scenario: Follow-ups derived from DLQ contents

- **WHEN** the DLQ directory has 5+ files at the end of the window
- **THEN** the follow-ups SHALL include
  `2. Replay DLQ files: tdt-tools/replay-dlq.py --all`.
