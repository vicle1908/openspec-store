## MODIFIED Requirements

### Requirement: Full local operational readiness is evidence-backed

The canonical local readiness gate SHALL start an isolated production-contract
Compose project, validate its normalized runtime contract, wait for all required
secure healthchecks and one-shot initializers, execute real authenticated HTTP,
Temporal/Nexus, PostgreSQL, Kafka, Redis, OTLP, and provider-sandbox operations,
and run the required negative and fault/recovery cohorts. Canonical operations
SHALL begin at an owning service API or authorized Nexus command and SHALL prove
the resulting domain transaction, outbox, CDC/Kafka record, consumer or
Workflow disposition, provider effect, notification, projection, and correlated
telemetry where applicable. Direct SQL mutation, direct Kafka injection,
health-only probes, and unrelated telemetry samples MUST NOT satisfy this
operation contract. The gate SHALL write a
machine-readable manifest containing source and contract identity, image
identities, declared reductions, security posture, health state, Workflow and
replay results, a causal operation ledger, logical side-effect counts,
connector/task state, topic
metadata, authorization denials, fault/recovery results, redaction result,
failure diagnostics, `run_id`, `compose_project`, and cleanup status. The gate
SHALL bind every artifact to that exact identity, SHALL reject local-fast or
cross-run evidence, and SHALL never select a globally newest artifact as a
substitute for an explicitly named run.

#### Scenario: Full local gate passes
- **WHEN** all required roles converge and the happy-path, compensation, idempotency, authorization, and recovery operation cohorts complete within their thresholds
- **THEN** the gate exits zero, marks the manifest `local-production-contract`, and retains exact run, project, contract, image, reduction, causal-ledger, and operation evidence

#### Scenario: Synthetic probe passes without an owned operation
- **WHEN** a direct outbox insert, direct Kafka record, health request, or uncorrelated telemetry query succeeds but no owning-service operation proves its durable business outcome
- **THEN** the probe is retained only as supplemental diagnostics
- **AND** the canonical readiness gate remains incomplete

#### Scenario: Health-only stack is incomplete
- **WHEN** a required role, security control, initializer, real operation, authorization denial, or recovery cohort is absent or failed
- **THEN** the gate exits non-zero and records the failed role, control, operation, identity, and redacted diagnostics

#### Scenario: Local-fast evidence is supplied
- **WHEN** any required artifact identifies local-fast or an insecure unknown mode
- **THEN** acceptance exits non-zero before evaluating functional outcomes

#### Scenario: Artifact identity collides
- **WHEN** a smoke, Worker, Workflow, provider, security, recovery, or acceptance artifact has a missing or mismatched source revision, contract version, run ID, or project
- **THEN** acceptance exits non-zero and reports the exact identity mismatch
- **AND** no artifact from another run is considered evidence

#### Scenario: Cleanup failure fails closed
- **WHEN** the workload passes but project, volume, network, or ephemeral-secret cleanup returns non-zero
- **THEN** the outer run exits non-zero
- **AND** the retained summary records `cleanup.status=failed` and redacted diagnostics

#### Scenario: Cleanup is scoped
- **WHEN** the operator runs normal shutdown after verification
- **THEN** only the owned isolated project and run-scoped secret material are removed
- **AND** unrelated Compose projects, images, volumes, networks, credentials, and trust roots remain untouched
