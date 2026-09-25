# Python Services Delta Reconciliation Audit

## Overview
All 16 Python services in `tdt/tdt-python-source-package/` on Google Drive were audited against the active local workspace checkouts under `~/Developer/`.

## Reconciliation Matrix

| Repository | Local Path | Local Exists | Active VCS | Resolution |
| :--- | :--- | :--- | :--- | :--- |
| `agent-core` | `/Users/androidteam/Developer/agent-core` | True | Git (main) | Preserved local as authoritative; zero remote overwrites |
| `agent-docs-sync` | `/Users/androidteam/Developer/agent-docs-sync` | True | Git (main) | Preserved local as authoritative; zero remote overwrites |
| `agent-harness` | `/Users/androidteam/Developer/agent-harness` | True | Git (main) | Preserved local as authoritative; zero remote overwrites |
| `ai-harness-skills` | `/Users/androidteam/Developer/ai-harness-skills` | True | Git (main) | Preserved local as authoritative; zero remote overwrites |
| `ai-review` | `/Users/androidteam/Developer/ai-review` | True | Git (main) | Preserved local as authoritative; zero remote overwrites |
| `browser-cli` | `/Users/androidteam/Developer/browser-cli` | True | Git (main) | Preserved local as authoritative; zero remote overwrites |
| `code-daily-scan` | `/Users/androidteam/Developer/code-daily-scan` | True | Git (main) | Preserved local as authoritative; zero remote overwrites |
| `jira-daily-reports` | `/Users/androidteam/Developer/jira-daily-reports` | True | Git (main) | Preserved local as authoritative; zero remote overwrites |
| `jira-epic-report` | `/Users/androidteam/Developer/jira-epic-report` | True | Git (main) | Preserved local as authoritative; zero remote overwrites |
| `jira-kanban-from-spreadsheet` | `/Users/androidteam/Developer/jira-kanban-from-spreadsheet` | True | Git (main) | Preserved local as authoritative; zero remote overwrites |
| `jira-skill` | `/Users/androidteam/Developer/jira-skill` | True | Git (main) | Preserved local as authoritative; zero remote overwrites |
| `ops-automation-suite` | `/Users/androidteam/Developer/ops-automation-suite` | True | Git (main) | Preserved local as authoritative; zero remote overwrites |
| `tdt-core` | `/Users/androidteam/Developer/tdt-core` | True | Git (main) | Preserved local as authoritative; zero remote overwrites |
| `tdt-observability` | `/Users/androidteam/Developer/tdt-observability` | True | Git (main) | Preserved local as authoritative; zero remote overwrites |
| `tdt-sheets` | `/Users/androidteam/Developer/tdt-sheets` | True | Git (main) | Preserved local as authoritative; zero remote overwrites |
| `webhook-receiver` | `/Users/androidteam/Developer/webhook-receiver` | True | Git (main) | Preserved local as authoritative; zero remote overwrites |

## Verification Findings
1. 100% of the 16 Python repositories are present in `~/Developer/`, indexed in GitNexus, and managed via `uv`.
2. Per the OpenSpec normative requirement (`Requirement: Python Services SHALL Enforce Local Workspace Authority`), local repositories are protected from blind overwrites by stale cloud snapshots.
3. Cold Git bundles (`tdt/git-bundles/`) and bare remotes (`tdt/git-remotes/`) remain safely archived in Google Drive as immutable cold backups.
