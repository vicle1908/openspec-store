# temporal-server-migration

## Purpose

Migrate from deprecated temporalio/auto-setup to temporalio/server with fresh start (no data migration). Uses temporalio/admin-tools for database schema setup.

## Requirements

### Requirement: TSM-001: Fresh Start

The system SHALL delete all old workflow data and start fresh with temporalio/server.

#### Scenario: Fresh Start
Given temporalio/auto-setup running with old data
When fresh start is initiated
Then it shall stop auto-setup container
And it shall delete all old data volumes
And it shall start temporalio/server container
And it shall initialize fresh workflow environment

### Requirement: TSM-002: Admin Tools Setup

The system SHALL use temporalio/admin-tools to set up the database schema before starting temporalio/server.

#### Scenario: Schema Setup
Given PostgreSQL 18.6 running fresh
When temporalio/admin-tools runs
Then it shall create temporal database
And it shall create temporal_visibility database
And it shall run schema migrations
And it shall verify schema version

#### Scenario: Admin Tools Environment
Given temporalio/admin-tools container
When configured
Then it shall have access to PostgreSQL
And it shall have access to Elasticsearch (if used)
And it shall run setup-postgres.sh script

### Requirement: TSM-003: Service Verification

The system SHALL verify all services can connect to temporalio/server after fresh start.

#### Scenario: Verify Services
Given temporalio/server running fresh
When all services are started
Then they shall connect successfully
And all workflows shall execute correctly
And database shall be initialized by services

### Requirement: TSM-004: Rollback Capability

The system SHALL support rollback to temporalio/auto-setup if fresh start fails.

#### Scenario: Rollback
Given temporalio/server fresh start failed
When rollback is initiated
Then it shall restore temporalio/auto-setup container
And it shall verify all workflows work
And it shall restore from backup if available
