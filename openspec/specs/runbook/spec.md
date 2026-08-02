## Purpose

This specification defines requirements for Runbook.

## Requirements

### Requirement: Initial Setup Runbook

The harness SHALL provide a step-by-step setup guide for new deployments.

#### Scenario: First-time setup
- **WHEN** a user sets up the harness for the first time
- **THEN** the runbook SHALL include:
  1. Clone agent-harness repo
  2. Run `uv sync` to install dependencies
  3. Copy `config.yaml.example` to `~/.tdt/harness/config.yaml`
  4. Configure workspace repos in `~/.tdt/harness/workspace.yaml`
  5. Verify tool availability: `harness doctor`
  6. Index target services: `harness index --all`
  7. Run smoke test: `harness run TEST-001 --dry-run`

#### Scenario: Tool installation
- **WHEN** a required tool is missing
- **THEN** the runbook SHALL provide installation instructions:
  - GitNexus: `npm i -g gitnexus`
  - Graphify: `pip install graphify`
  - OpenSpec: `npm i -g openspec`

### Requirement: Index Management Runbook

The harness SHALL provide guidance for managing GitNexus and Graphify indexes.

#### Scenario: Index a new service
- **WHEN** a new service is added to the workspace
- **THEN** the runbook SHALL include:
  1. Add repo to `~/.tdt/harness/workspace.yaml`
  2. Run `cd <repo> && npx gitnexus analyze --force`
  3. Run `cd <repo> && graphify build`
  4. Verify: `harness index --status <repo>`

#### Scenario: Refresh stale index
- **WHEN** an index is stale (last commit differs from HEAD)
- **THEN** the runbook SHALL include:
  1. Check staleness: `harness index --stale`
  2. Re-index: `harness index --refresh <repo>`
  3. Verify: `harness index --status <repo>`

### Requirement: Troubleshooting Runbook

The harness SHALL provide troubleshooting guidance for common issues.

#### Scenario: Workflow fails at a stage
- **WHEN** a workflow fails
- **THEN** the runbook SHALL include:
  1. Check logs: `harness status <ticket_id> --verbose`
  2. Check trace: `harness report <ticket_id>`
  3. Check tool availability: `harness doctor`
  4. Check config: `harness config --validate`

#### Scenario: Gate approval timeout
- **WHEN** a gate times out
- **THEN** the runbook SHALL include:
  1. Check pending gates: `harness status <ticket_id>`
  2. Approve manually: `harness approve <ticket_id> <stage>`
  3. Or reject and backtrack: `harness reject <ticket_id> <stage> "timeout"`

#### Scenario: Tool circuit breaker open
- **WHEN** a tool's circuit breaker is open
- **THEN** the runbook SHALL include:
  1. Check tool status: `harness doctor --tools`
  2. Wait for recovery timeout
  3. Or manually reset: `harness doctor --reset-circuit <tool_name>`

### Requirement: Monitoring Runbook

The harness SHALL provide guidance for monitoring workflow health.

#### Scenario: Check workflow status
- **WHEN** monitoring active workflows
- **THEN** the runbook SHALL include:
  1. List active: `harness status --active`
  2. Check specific: `harness status <ticket_id>`
  3. View metrics: Langfuse dashboard at `http://localhost:3000`

#### Scenario: Check system health
- **WHEN** monitoring system health
- **THEN** the runbook SHALL include:
  1. Tool health: `harness doctor --tools`
  2. Memory health: `harness doctor --memory`
  3. Config health: `harness config --validate`

### Requirement: Backup and Recovery Runbook

The harness SHALL provide guidance for backup and recovery.

#### Scenario: Backup workflow state
- **WHEN** backing up workflow state
- **THEN** the runbook SHALL include:
  1. Backup scratch: `cp -r ~/.tdt/agent-harness/scratch/ /backup/`
  2. Backup Postgres: `pg_dump agent_harness > backup.sql`

#### Scenario: Recover from crash
- **WHEN** recovering from a crash
- **THEN** the runbook SHALL include:
  1. Check checkpoints: `harness status <ticket_id> --checkpoints`
  2. Resume from last checkpoint: `harness resume <ticket_id>`
  3. Or restart: `harness run <ticket_id> --resume`
