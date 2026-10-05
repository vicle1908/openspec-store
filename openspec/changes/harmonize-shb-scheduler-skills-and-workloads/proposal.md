# Proposal

## Why

The Saigon - Hanoi Bank (SHB) agent ecosystem recently established `shb-schedule` as its canonical, durable task scheduler. However, operational discovery identified two integration anomalies:
1. `shb-agent-skills` contains a legacy `scheduler-skill` inherited from an external organization (VDS) referencing `vds-cli`, `VDS_SCHEDULER_ENABLED`, and Celery Beat migration, causing autonomous agents to invoke non-existent tools when attempting to interact with the scheduler.
2. Recurring banking operations—specifically end-of-day settlement reconciliation (`shb-recon`) and PCI-DSS compliance audits (`shb-compliance-scan`) in `shb-tools`—lack declarative schedule manifests and approved workflow bindings in `shb-schedule`, risking scattered manual script invocations.

Harmonizing `scheduler-skill` to native `shb-schedule` standards and onboarding these secondary workloads completes ecosystem consolidation under a unified, clean-break scheduling backbone.

## What Changes

- **Rewrite `scheduler-skill` in `shb-agent-skills`**: Modernize `skills/scheduler-skill/SKILL.md` and `registry.yaml` to document native `shb-schedule` CLI tools (`validate`, `list`, `run-now`, `reload`, `service`), `shb-schedule/v1` manifest specifications, and `/scheduler/health` endpoints, completely eliminating alien `vds-cli` references.
- **Onboard EOD Settlement Reconciliation Workflow**: Export and allowlist `eod_settlement_recon_workflow` in `shb-schedule`, backed by `shb_tools.recon.engine.ReconciliationEngine`, and ship declarative schedule manifest `eod-settlement-recon.yaml` (executing daily at 23:00 HCM).
- **Onboard Nightly Compliance Scan Workflow**: Export and allowlist `nightly_compliance_scan_workflow` in `shb-schedule`, backed by `shb_tools.compliance.scanner.ComplianceScanner`, and ship declarative schedule manifest `nightly-compliance-scan.yaml` (executing daily at 01:00 HCM) with dirty worktree protection.
- **Update Workflow Registry Allowlist**: Register new callable paths in `shb_schedule.manifests.registry.APPROVED_WORKFLOWS`.

## Capabilities

### Modified Capabilities

- `shb-agent-skills`: Updates the canonical skills catalog to provide native `shb-schedule` operational skills and commands, replacing legacy foreign scheduler artifacts.
- `shb-schedule-engine`: Expands the standardized scheduling engine with secondary banking workload bindings for settlement reconciliation and PCI-DSS compliance scanning.

## Impact

- Autonomous coding agents in the SHB ecosystem can reliably operate `shb-schedule` using verified native commands.
- Routine EOD banking reconciliation and compliance scans are scheduled durably with crash resilience and execution audit logs in `~/.shb/scheduler.db`.
- Zero disruption to existing ReAct agent loops or banking client factories.

## Non-Goals

- Modifying the underlying algorithms in `shb_tools.recon` or `shb_tools.compliance`.
- Re-introducing multi-writer microservice schedule mutation (all schedules remain file-declared under `~/.shb/schedules/`).
- Auto-remediating PCI-DSS violations during unattended runs (violations are strictly audited and logged).
