# harness-workflow-architecture Specification

## Purpose
Defines the complete 12-stage workflow architecture for processing tickets end-to-end in large-scale SaaS microservices.
## Requirements
### Requirement: 12-stage workflow definition

The workflow SHALL consist of 12 stages organized into 5 phases: Discovery, Design, Planning, Implementation, and Verification.

#### Scenario: Stage execution order

- **WHEN** a ticket enters the workflow
- **THEN** stages SHALL execute in the defined order: Intake → Clarify → Spec → Impact → Design → API Contract → Impl Plan → Coding Tasks → Coding → Test Cases → Test Plan → Verification
- **AND** each stage SHALL complete before the next begins

#### Scenario: Stage type classification

- **WHEN** a stage is defined
- **THEN** it SHALL be classified as either deterministic or model-backed
- **AND** model-backed stages SHALL use LLM agents for execution
- **AND** deterministic stages SHALL use fixed logic

### Requirement: Human approval points

The workflow SHALL include human approval gates at stages 2, 3, 5, 6, 9, and 12.

#### Scenario: Approval required

- **WHEN** a stage with human approval completes
- **THEN** the workflow SHALL interrupt and wait for human decision
- **AND** approval SHALL be recorded in the gate decision store
- **AND** rejection SHALL trigger rollback to the previous stage

#### Scenario: Auto-pass stages

- **WHEN** a stage without human approval completes
- **THEN** the workflow SHALL proceed automatically to the next stage

### Requirement: Artifact traceability

Every artifact SHALL be linked through a traceability chain from requirement to verification.

#### Scenario: Artifact creation

- **WHEN** a stage produces an artifact
- **THEN** it SHALL be stored as an atomic envelope with SHA-256 digest
- **AND** the envelope SHALL reference the previous stage's artifact
- **AND** the traceability chain SHALL be verifiable

#### Scenario: Artifact verification

- **WHEN** an artifact is loaded from storage
- **THEN** its SHA-256 digest SHALL be verified
- **AND** mismatch SHALL reject the artifact

