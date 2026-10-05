# Spec Delta: shb-schedule-engine

## ADDED Requirements

### Requirement: Banking Core Workload Bindings
The `shb-schedule` package SHALL provide durable workflow implementations and approved registry allowlist mappings for secondary core banking operational workloads, specifically end-of-day settlement reconciliation (`eod_settlement_recon_workflow`) and automated PCI-DSS compliance scanning (`nightly_compliance_scan_workflow`).

#### Scenario: Scheduled settlement reconciliation execution
- **WHEN** the `daily-eod-settlement-recon` schedule is triggered by cron (23:00 HCM) or on-demand
- **THEN** it executes `eod_settlement_recon_workflow`, sources internal and clearing transactions via `load_settlement_transactions`, and reconciles ledgers via `shb_tools.recon.engine.ReconciliationEngine`
- **AND** records matched transactions, discrepancies, and orphan counts in DBOS execution history

#### Scenario: Scheduled compliance scan execution
- **WHEN** the `daily-nightly-compliance-scan` schedule is triggered by cron (01:00 HCM) or on-demand
- **THEN** it executes `nightly_compliance_scan_workflow` delegating to `shb_tools.scanner.engine.ComplianceScanner`
- **AND** skips repositories with uncommitted changes while reporting scan violations in structured workflow telemetry
