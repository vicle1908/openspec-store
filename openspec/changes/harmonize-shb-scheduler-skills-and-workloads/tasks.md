# Tasks

## 1. Skill Harmonization (`shb-agent-skills`)

- [ ] 1.1 Rewrite `skills/scheduler-skill/SKILL.md` to document native `shb-schedule` CLI, `shb-schedule/v1` manifest schema, and `/scheduler/health` endpoints, completely removing `vds-cli` references
- [ ] 1.2 Update `registry.yaml` entry for `scheduler-skill` to reflect native SHB scheduling architecture and capabilities

## 2. Settlement Reconciliation Workflow (`shb-schedule`)

- [ ] 2.1 Implement `src/shb_schedule/workflows/recon.py` defining transaction sourcing (`load_settlement_transactions`) and execution (`execute_settlement_reconciliation`) steps, and `@DBOS.workflow` for `eod_settlement_recon_workflow` backed by `shb_tools.recon.engine.ReconciliationEngine`
- [ ] 2.2 Register `eod-settlement-recon` and callable path in `shb_schedule.manifests.registry.APPROVED_WORKFLOWS`
- [ ] 2.3 Create and install schedule manifest `~/.shb/schedules/eod-settlement-recon.yaml` (`0 23 * * *`)

## 3. Compliance Scanner Workflow (`shb-schedule`)

- [ ] 3.1 Implement `src/shb_schedule/workflows/compliance.py` defining `@DBOS.step` and `@DBOS.workflow` for `nightly_compliance_scan_workflow` backed by `shb_tools.scanner.engine.ComplianceScanner` with dirty-worktree guards
- [ ] 3.2 Register `nightly-compliance-scan` and callable path in `shb_schedule.manifests.registry.APPROVED_WORKFLOWS`
- [ ] 3.3 Create and install schedule manifest `~/.shb/schedules/nightly-compliance-scan.yaml` (`0 1 * * *`)

## 4. Verification and Acceptance

- [ ] 4.1 Author unit tests for reconciliation and compliance workflows in `shb-schedule/tests/`
- [ ] 4.2 Run test suite with `uv run pytest tests/ -q -p no:cacheprovider` and verify 100% pass rate
- [ ] 4.3 Validate all manifests with `uv run shb-schedule validate ~/.shb/schedules`
- [ ] 4.4 Run strict OpenSpec validation with `openspec validate harmonize-shb-scheduler-skills-and-workloads --strict --store openspec-store`
