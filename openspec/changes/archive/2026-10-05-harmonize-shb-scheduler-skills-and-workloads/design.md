# Design

## Context

The SHB scheduler infrastructure (`shb-schedule`) is established, strictly validated, and verified on DBOS Transact 3.2.0 with SQLite WAL persistence. The flagship documentation sync workflow (`daily-shb-docs-sync`) is running. However, agents operating in `shb-agent-skills` encounter an alien VDS `scheduler-skill` referencing non-existent `vds-cli` tools. Concurrently, `shb-tools` contains two operational engines (`ReconciliationEngine` and `ComplianceScanner`) that run only via ad-hoc CLI calls rather than managed recurring manifests.

## Goals / Non-Goals

**Goals:**
- Replace `skills/scheduler-skill/SKILL.md` in `shb-agent-skills` with an authoritative guide for `shb-schedule`.
- Implement `@DBOS.workflow` and `@DBOS.step` definitions for settlement reconciliation and compliance scanning.
- Add allowlist entries in `shb_schedule.manifests.registry.APPROVED_WORKFLOWS`.
- Create declarative manifests: `eod-settlement-recon.yaml` (23:00 HCM) and `nightly-compliance-scan.yaml` (01:00 HCM).
- Verify dirty worktree protection on the compliance scan workflow.

**Non-Goals:**
- Altering core banking reconciliation rules or PCI-DSS regex patterns.
- Modifying `shb-tools` CLI interfaces.
- Supporting distributed multi-worker execution beyond local single-owner SQLite WAL and PostgreSQL.

## Decisions

### 1. Skill Rewriting Architecture (`shb-agent-skills`)
- Rewrite `skills/scheduler-skill/SKILL.md` with standard YAML frontmatter:
  ```yaml
  name: scheduler-skill
  description: Operate the SHB ecosystem task scheduler (shb-schedule) for cron and interval workflows.
  compatibility: Python 3.14+, DBOS Transact 3.x, shb-schedule
  allowed-tools: bash read write edit grep ast_grep
  ```
- Document core operational verbs:
  - `uv run shb-schedule validate ~/.shb/schedules`
  - `uv run shb-schedule list --dir ~/.shb/schedules`
  - `uv run shb-schedule run-now <job-name>`
  - `uv run shb-schedule reload`
  - `curl -s http://127.0.0.1:9110/scheduler/health`
  - `curl -s http://127.0.0.1:9110/scheduler/schedules`
- Update `shb-agent-skills/registry.yaml` metadata.

### 2. Settlement Reconciliation Workflow (`shb_schedule.workflows.recon`)
- `@DBOS.step`: `load_settlement_transactions(date_str: str, context: dict[str, Any] | None = None) -> dict[str, Any]`
  Sources `internal_transactions` and `clearing_transactions` from manifest context, local settlement ledger JSON (`~/.shb/settlement/{date}.json`), or default banking sample fixtures.
- `@DBOS.step`: `execute_settlement_reconciliation(internal_transactions: list[dict[str, Any]], clearing_transactions: list[dict[str, Any]], reconciliation_date: str) -> dict[str, Any]`
  Invokes `ReconciliationEngine().reconcile()` and returns a JSON-serializable dictionary of matched, discrepancy, and orphan tallies.
- `@DBOS.workflow`: `eod_settlement_recon_workflow(*args: Any, reconciliation_date: str | None = None, **kwargs: Any) -> dict[str, Any]`
  Resolves the target date, orchestrates the loading and reconciliation steps, and records audit telemetry in DBOS execution history.
### 3. Compliance Scanner Workflow (`shb_schedule.workflows.compliance`)
- `@DBOS.step`: `git_check_dirty_tree(repo_dir: Path) -> dict[str, Any]` (reuses existing step).
- `@DBOS.step`: `execute_repo_compliance_scan(repo_dir: Path) -> ComplianceReport`
  Executes `ComplianceScanner().scan_directory()` on target, returning violation summaries.
- `@DBOS.workflow`: `nightly_compliance_scan_workflow(*args: Any, **kwargs: Any) -> dict[str, Any]`
  Iterates across configured SHB child repositories, skipping dirty repositories to prevent evaluating in-progress edits, and aggregating violation summaries.

### 4. Manifest Definitions
- `~/.shb/schedules/eod-settlement-recon.yaml`:
  `cron: "0 23 * * *"`, `timezone: "Asia/Ho_Chi_Minh"`, `queue: "recon-queue"`, `workflow: "eod-settlement-recon"`.
- `~/.shb/schedules/nightly-compliance-scan.yaml`:
  `cron: "0 1 * * *"`, `timezone: "Asia/Ho_Chi_Minh"`, `queue: "audit-queue"`, `workflow: "nightly-compliance-scan"`.

## Risks / Trade-offs

- **Worktree Evaluation During Compliance Scans**: Like docs-sync, compliance scanning requires repository files. Running on dirty repositories could raise false alerts for in-progress developer edits. Skipping dirty worktrees prevents false-positive alerts while ensuring clean repositories are regularly scanned.
- **Queue Separation**: Distinct queues (`recon-queue`, `audit-queue`, `sync-queue`) isolate concurrency so long-running compliance scans do not starve settlement audits.
