# TDT Home Service Inventory

## Consumers Reading ~/.tdt

| Repository | Entry Point | Reads |
|------------|-------------|-------|
| agent-core | `agent_core/` | `.env`, `config.yaml` |
| agent-docs-sync | `agent_docs_sync/` | `.env` |
| agent-harness | `agent_harness/` | `.env` |
| ai-harness-skills | `ai_harness_skills/` | `.env` |
| ai-review | `ai_review/` | `.env` |
| browser-cli | `browser_cli/` | `.env` |
| code-daily-scan | `code_daily_scan/` | `.env` |
| jira-daily-reports | `jira_daily_reports/` | `.env` |
| jira-epic-report | `jira_epic_report/` | `.env` |
| jira-kanban-from-spreadsheet | `jira_kanban_from_spreadsheet/` | `.env` |
| jira-skill | `jira_skill/` | `.env` |
| ops-automation-suite | `ops_automation_suite/` | `.env` |
| tdt-core | `tdt_core/` | `.env`, `config.yaml`, `config.toml` |
| tdt-observability | `tdt_observability/` | `.env` |
| tdt-sheets | `tdt_sheets/` | `.env` |
| webhook-receiver | `webhook_receiver/` | `.env` |

## Writers to ~/.tdt

- `tdt-core` CLI (`tdt config doctor`, `tdt config create-manifest`)
- `tdt-core` env loader (`load_tdt_env()` writes to `os.environ` only)

## Scheduled Services

- No persistent TDT services are currently running
- Scheduler config lives in `~/.tdt/config.yaml`

## Deployment Surfaces

- All consumers run as local Python processes (no Docker/K8s)
- GDrive sync via `rclone bisync` (excludes `~/.tdt`)
