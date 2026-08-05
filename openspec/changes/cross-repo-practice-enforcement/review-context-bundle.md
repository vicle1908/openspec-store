# Review Context Bundle: Cross-Repo Practice Enforcement

## Workspace Overview

- **16 Python repos** at ~/Developer/
- **1 Go repo**: go-microservices (not in scope)
- **1 Node repo**: mcp-router (not in scope)
- **Shared store**: ~/Developer/openspec-store/
- **All Python repos use**: uv (pyproject.toml + uv.lock), hatchling build backend
- **All target Python**: >=3.14,<3.15 (except ai-harness-skills: >=3.14)

## Tool Version Matrix

| Repo | ruff | mypy | pytest |
|------|------|------|--------|
| agent-core | 0.15.0 | 2.1.0 | 9.0.0 |
| agent-docs-sync | 0.5.0 | 1.11 | 8.3.0 |
| agent-harness | 0.15.0 | 2.1.0 | 9.0.0 |
| ai-harness-skills | 0.16.0 | 2.3.0 | 9.1.1 |
| ai-review | 0.15.0 | 2.1.0 | 9.0.0 |
| browser-cli | 0.15.0 | 2.1.0 | 9.0.0 |
| code-daily-scan | 0.15.0 | 1.10.0 | 8.3.0 |
| jira-daily-reports | 0.15.0 | 1.10.0 | 8.3.0 |
| jira-epic-report | 0.8.4 | 1.14.0 | 8.3.4 |
| jira-kanban-from-spreadsheet | 0.15.0 | 1.14.0 | 8.3.0 |
| jira-skill | 0.15.0 | 1.10.0 | 8.3.0 |
| ops-automation-suite | 0.15.0 | 2.1.0 | 9.0.0 |
| tdt-core | 0.15.0 | 1.14.0 | 8.3.0 |
| tdt-observability | 0.15.0 | 1.14.0 | 9.0.0 |
| tdt-sheets | 0.15.0 | 2.1.0 | 9.0.0 |
| webhook-receiver | 0.15.0 | 2.1.0 | 9.0.0 |

## Ruff Config Matrix

- **agent-core**: select=EMPTY ignore=['E501', 'B008']
- **agent-docs-sync**: select=['E', 'F', 'W', 'I', 'N', 'UP', 'S', 'B', 'A', 'COM', 'C4', 'DTZ', 'ISC', 'ICN', 'PIE', 'PT', 'RSE', 'RET', 'SLF', 'SIM', 'TID', 'TCH', 'ARG', 'PTH', 'ERA'] ignore=['COM812']
- **agent-harness**: select=['E', 'W', 'F', 'I', 'N', 'UP', 'B', 'A', 'C4', 'SIM', 'TCH', 'RUF', 'TC', 'S'] ignore=['E501', 'B008', 'TC001', 'TC003', 'UP042', 'SIM114']
- **ai-harness-skills**: select=['E', 'F', 'I', 'B', 'UP', 'SIM', 'RUF'] ignore=EMPTY
- **ai-review**: select=['E', 'W', 'F', 'I', 'N', 'UP', 'B', 'A', 'C4', 'SIM', 'TCH', 'RUF'] ignore=['E501', 'B008']
- **browser-cli**: select=['E', 'W', 'F', 'I', 'N', 'B', 'C4', 'UP'] ignore=['E501']
- **code-daily-scan**: select=['E', 'W', 'F', 'I', 'N', 'UP', 'B', 'A', 'C4', 'SIM', 'TCH', 'RUF'] ignore=['E501', 'B008', 'SIM105', 'RUF012', 'UP007', 'UP042']
- **jira-daily-reports**: select=['E', 'W', 'F', 'I', 'N', 'UP', 'B', 'A', 'C4', 'SIM', 'TCH', 'RUF'] ignore=['E501', 'SIM108', 'SIM102', 'SIM105', 'SIM110', 'A001', 'RUF001', 'RUF012', 'RUF013', 'B008']
- **jira-epic-report**: select=['E', 'W', 'F', 'I', 'N', 'UP', 'B', 'A', 'C4', 'SIM', 'TCH', 'RUF'] ignore=['E501']
- **jira-kanban-from-spreadsheet**: select=['E', 'W', 'F', 'I', 'N', 'UP', 'B', 'A', 'C4', 'SIM', 'TCH', 'RUF'] ignore=['E501', 'SIM108']
- **jira-skill**: select=['E', 'W', 'F', 'I', 'N', 'UP', 'B', 'A', 'C4', 'SIM', 'TCH', 'RUF'] ignore=['E501', 'SIM108', 'SIM102', 'SIM103', 'SIM105', 'SIM110', 'A001', 'A004', 'RUF001', 'RUF012', 'RUF013']
- **ops-automation-suite**: select=['E', 'W', 'F', 'I', 'N', 'UP', 'B', 'A', 'C4', 'SIM', 'TCH', 'RUF'] ignore=EMPTY
- **tdt-core**: select=['E', 'W', 'F', 'I', 'N', 'UP', 'B', 'A', 'C4', 'SIM', 'TCH', 'RUF'] ignore=['E501', 'SIM108']
- **tdt-observability**: select=['E', 'F', 'I', 'N', 'W', 'UP', 'B', 'C4', 'SIM'] ignore=['E501']
- **tdt-sheets**: select=EMPTY ignore=EMPTY
- **webhook-receiver**: select=['E', 'W', 'F', 'I', 'N', 'UP', 'B', 'A', 'C4', 'SIM', 'TCH', 'RUF'] ignore=['E501', 'B008', 'UP035']

## Pre-Commit Status

- **agent-core**: gitleaks=True ruff=True ruff-format=True mypy=True pytest=True shellcheck=False hooks=['gitleaks', 'ruff-check', 'ruff-format', 'mypy', 'pytest']
- **agent-docs-sync**: gitleaks=True ruff=True ruff-format=True mypy=True pytest=True shellcheck=False hooks=['gitleaks', 'ruff-check', 'ruff-format', 'mypy', 'pytest']
- **agent-harness**: gitleaks=True ruff=True ruff-format=True mypy=True pytest=True shellcheck=False hooks=['gitleaks', 'ruff-check', 'ruff-format', 'mypy', 'pytest']
- **ai-harness-skills**: NO .pre-commit-config.yaml
- **ai-review**: gitleaks=True ruff=True ruff-format=True mypy=False pytest=False shellcheck=False hooks=['gitleaks', 'ruff', 'ruff-format', 'trailing-whitespace', 'end-of-file-fixer', 'check-yaml', 'check-toml', 'check-added-large-files', 'check-merge-conflict', 'detect-private-key', 'debug-statements']
- **browser-cli**: gitleaks=True ruff=True ruff-format=True mypy=False pytest=False shellcheck=True hooks=['gitleaks', 'shellcheck', 'shfmt', 'ruff', 'ruff-format', 'actionlint']
- **code-daily-scan**: NO .pre-commit-config.yaml
- **jira-daily-reports**: gitleaks=True ruff=True ruff-format=True mypy=False pytest=False shellcheck=True hooks=['gitleaks', 'shellcheck', 'shfmt', 'ruff', 'ruff-format', 'actionlint']
- **jira-epic-report**: gitleaks=True ruff=True ruff-format=True mypy=False pytest=False shellcheck=True hooks=['gitleaks', 'shellcheck', 'shfmt', 'ruff', 'ruff-format', 'actionlint']
- **jira-kanban-from-spreadsheet**: gitleaks=True ruff=True ruff-format=True mypy=False pytest=False shellcheck=True hooks=['gitleaks', 'shellcheck', 'shfmt', 'ruff', 'ruff-format', 'actionlint']
- **jira-skill**: gitleaks=True ruff=True ruff-format=True mypy=False pytest=False shellcheck=True hooks=['gitleaks', 'shellcheck', 'shfmt', 'ruff', 'ruff-format', 'actionlint']
- **ops-automation-suite**: gitleaks=True ruff=True ruff-format=True mypy=False pytest=False shellcheck=True hooks=['gitleaks', 'shellcheck', 'shfmt', 'ruff', 'ruff-format', 'actionlint']
- **tdt-core**: gitleaks=True ruff=True ruff-format=True mypy=False pytest=False shellcheck=False hooks=['gitleaks', 'ruff', 'ruff-format', 'trailing-whitespace', 'end-of-file-fixer', 'check-yaml', 'check-toml', 'check-added-large-files', 'check-merge-conflict', 'detect-private-key', 'debug-statements']
- **tdt-observability**: NO .pre-commit-config.yaml
- **tdt-sheets**: NO .pre-commit-config.yaml
- **webhook-receiver**: gitleaks=True ruff=True ruff-format=True mypy=False pytest=False shellcheck=False hooks=['gitleaks', 'ruff', 'ruff-format', 'trailing-whitespace', 'end-of-file-fixer', 'check-yaml', 'check-toml', 'check-added-large-files', 'check-merge-conflict', 'detect-private-key', 'debug-statements']

## Cross-Repo Dependency Graph

- **agent-core** consumes: tdt-core = { path = "../tdt-core", editable = true }
- **agent-docs-sync** consumes: agent-core = { path = "../agent-core", editable = true }, tdt-core = { path = "../tdt-core", editable = true }
- **agent-harness** consumes: agent-core = { path = "../agent-core", editable = true }, tdt-core = { path = "../tdt-core", editable = true }
- **ai-review** consumes: tdt-core = { path = "../tdt-core", editable = true }, code-daily-scan = { path = "../code-daily-scan", editable = true }
- **code-daily-scan** consumes: agent-core = { path = "../agent-core", editable = true }, tdt-core = { path = "../tdt-core", editable = true }, tdt-sheets = { path = "../tdt-sheets", editable = true }
- **jira-daily-reports** consumes: tdt-core = { path = "../tdt-core", editable = true }, tdt-sheets = { path = "../tdt-sheets", editable = true }, jira-skill = { path = "../jira-skill", editable = true }
- **jira-epic-report** consumes: tdt-core = { path = "../tdt-core", editable = true }, tdt-sheets = { path = "../tdt-sheets", editable = true }, jira-skill = { path = "../jira-skill", editable = true }
- **jira-kanban-from-spreadsheet** consumes: tdt-core = { path = "../tdt-core", editable = true }, tdt-sheets = { path = "../tdt-sheets", editable = true }
- **jira-skill** consumes: tdt-core = { path = "../tdt-core", editable = true }, tdt-sheets = { path = "../tdt-sheets", editable = true }
- **tdt-observability** consumes: tdt-core = { path = "../tdt-core", editable = true }
- **tdt-sheets** consumes: tdt-core = { path = "../tdt-core", editable = true }
- **webhook-receiver** consumes: tdt-core = { path = "../tdt-core", editable = true }, jira-daily-reports = { path = "../jira-daily-reports", editable = true }, jira-skill = { path = "../jira-skill", editable = true }

## Test Counts (from AGENTS.md)

- agent-core: 69 tests
- agent-docs-sync: 38 tests
- agent-harness: 33 tests
- ai-harness-skills: 34 tests
- ai-review: 19 tests
- browser-cli: 10 tests
- code-daily-scan: 35 tests
- jira-daily-reports: 70 tests
- jira-epic-report: 45 tests
- jira-kanban-from-spreadsheet: 16 tests
- jira-skill: 90 tests
- ops-automation-suite: 4 tests
- tdt-core: 20 tests
- tdt-observability: 7 tests
- tdt-sheets: 11 tests
- webhook-receiver: 6 tests
- **Total: 507 tests**