# temporal-upgrade

## Purpose

Upgrade Temporal server from v1.29.7 to v1.31.2 to gain Worker Versioning v2 GA, security fixes, and new features.

## Current State

- Temporal server: v1.29.7
- Temporal SDK: v1.46.0
- Worker Versioning: v1 (deprecated)
- Security: CVE-2026-5724 not addressed

## Dependencies

- Temporal server v1.31.2 (Docker image)
- Temporal SDK v1.46.0+ (Go module)

## Requirements

### Requirement: TU-001: Temporal Server Upgrade

The Temporal server SHALL be upgraded from v1.29.7 to v1.31.2. The upgrade SHALL be performed with zero downtime for running workflows.

#### Scenario: Server Upgrade
Given a running Temporal server at v1.29.7
When the server is upgraded to v1.31.2
Then existing workflows shall continue executing
And new workflows shall use Worker Versioning v2

#### Scenario: Backward Compatibility
Given workflows running on v1.29.7
When the server is upgraded to v1.31.2
Then all running workflows shall complete successfully
And no data loss shall occur

### Requirement: TU-002: Worker Versioning v2 GA

Worker Versioning v2 SHALL be enabled by default. The deployment APIs SHALL be fully general availability.

#### Scenario: Worker Versioning v2
Given a worker with Worker Versioning v2
When the worker registers workflows and activities
Then the deployment version shall be tracked
And workflow history shall include principal attribution

#### Scenario: Deployment API
Given a deployment with multiple versions
When a new version is deployed
Then the deployment API shall manage version routing
And traffic shall be gradually shifted to the new version

### Requirement: TU-003: Security Fix

The CVE-2026-5724 security fix SHALL be applied. Systems using authorization + replication SHALL set `system.disableStreamingAuthorizer` to `true`.

#### Scenario: CVE Mitigation
Given a Temporal server with authorization + replication
When v1.31.2 is deployed
Then `system.disableStreamingAuthorizer` shall be set to `true`
And the replication streaming endpoint shall be secured

#### Scenario: No Authorization
Given a Temporal server without authorization
When v1.31.2 is deployed
Then the security fix shall be applied automatically
And no configuration changes are required

### Requirement: TU-004: Serverless Workers Support

Serverless workers SHALL be supported as a pre-release feature. Workers SHALL be able to run on serverless platforms (AWS Lambda, etc.).

#### Scenario: Serverless Worker
Given a workflow that can run on serverless
When the worker is configured for serverless
Then it shall support automatic invocation
And it shall support scale-to-zero

### Requirement: TU-005: Principal Attribution

Workflow history events SHALL include a server-computed, immutable principal attribution field. This field SHALL provide trustworthy "who did this?" attribution.

#### Scenario: Principal Attribution
Given a workflow execution
When history events are recorded
Then each event SHALL include a principal attribution field
And the field shall be immutable and server-computed

### Requirement: TU-006: Cloud IAM Auth for SQL

The Temporal server SHALL support IAM-based authentication for cloud-managed databases (AWS RDS, GCP Cloud SQL).

#### Scenario: Cloud IAM Auth
Given a Temporal server connected to a cloud-managed database
When `passwordCommand` is configured
Then IAM-based authentication shall be used
And credentials shall be managed by the cloud provider

### Requirement: TU-007: Nexus Overhaul

Nexus SHALL be enabled by default with improved error handling and caller timeout support.

#### Scenario: Nexus Enabled
Given a Temporal server at v1.31.2
When Nexus is configured
Then it shall be enabled by default
And error handling shall be improved

#### Scenario: Caller Timeout
Given a Nexus caller with a timeout
When the timeout expires
Then the caller shall receive a timeout error
And the operation shall be cleaned up

### Requirement: TU-008: CHASM Framework

CHASM SHALL be enabled by default with separate `businessID` spaces for different archetypes.

#### Scenario: CHASM Enabled
Given a Temporal server at v1.31.2
When CHASM is configured
Then it shall be enabled by default
And different archetypes shall have separate businessID spaces

### Requirement: TU-009: Standalone Activities

Activities SHALL be able to run independently of workflows. This feature SHALL be gated behind a dynamic config flag.

#### Scenario: Standalone Activity
Given a workflow with standalone activities
When the dynamic config flag is enabled
Then activities shall run independently
And they shall not require a parent workflow

### Requirement: TU-010: Upgrade Validation

The upgrade SHALL be validated through:
1. Unit tests passing
2. Integration tests passing
3. Workflow execution tests passing
4. Security vulnerability scan passing

#### Scenario: Validation
Given the upgraded Temporal server
When validation tests are run
Then all unit tests shall pass
And all integration tests shall pass
And no security vulnerabilities shall be detected
