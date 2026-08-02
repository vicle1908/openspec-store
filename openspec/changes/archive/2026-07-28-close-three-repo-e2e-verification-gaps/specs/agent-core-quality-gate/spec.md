## MODIFIED Requirements

### Requirement: Workspace repo inventory and scope

The quality gate SHALL apply to a fixed inventory of Python repositories under
`/Users/lekhanhvinh/Developer/tdt/`. Each repo SHALL declare its package layout
(the `--cov=` target) so coverage, mypy, and lint checks all use the same root.

The inventory in scope:

| Repo | Package | Why in scope |
|---|---|---|
| `tdt-core` | `src` | foundational Jira/GitLab SDK |
| `webhook-receiver` | `src` | webhook ingress |
| `jira-daily-reports` | `src` | reporting CLI |
| `jira-epic-report` | `epic_report` (flat) | epic/sprint reporting CLI |
| `jira-skill` | `src/jira_skill` | jira automation server |
| `jira-kanban-from-spreadsheet` | `src/kbs` | sprint→Kanban CLI |
| `agent-core` | `src/agent_core` | agent runtime |
| `agent-docs-sync` | `src/agent_docs_sync` | documentation synchronization consumer |
| `agent-harness` | `src/agent_harness` | gated planning workflow consumer |
| `ai-review` | `src/ai_review` | code review automation |
| `browser-cli` | `src/browser_cli` | playwright CLI |
| `ops-automation-suite` | `src/ops_automation` | ops orchestrator |

#### Scenario: Repo declares its package root

- **WHEN** a repo runs CI or local quality gates
- **THEN** it SHALL pass `--cov=<package>` matching the inventory above
- **AND** mypy SHALL be invoked as `uv run mypy <package>`
- **AND** ruff SHALL target the same package root

#### Scenario: Three-repository verification scope

- **WHEN** `agent-core`, `agent-docs-sync`, and `agent-harness` are verified as
  one framework-compatible set
- **THEN** all three SHALL enforce the shared 80% coverage minimum and strict
  typing/lint gates
- **AND** a green combined result SHALL not conceal a below-threshold repo

#### Scenario: New repo joins the workspace

- **WHEN** a Python repo is added to `/Users/lekhanhvinh/Developer/tdt/`
- **THEN** it SHALL be added to the inventory in this spec before the next
  quality-gate audit
- **AND** the inventory table SHALL list its declared package root
- **AND** PRs that introduce new repos SHALL update this scenario in the same
  change

## ADDED Requirements

### Requirement: Source security and generated-artifact gate

Each repository in the three-repository verification set (`agent-core`,
`agent-docs-sync`, and `agent-harness`) SHALL run deterministic source security
rules over production code and SHALL reject generated Python cache artifacts
from source control. Test-only assertion rules MAY be excluded through
documented per-file configuration. Extending this gate to the broader workspace
inventory requires a separate change.

#### Scenario: Production security lint

- **WHEN** CI verifies one of the three repositories in this change
- **THEN** production source SHALL be checked with the repository's Ruff rules
  including the applicable security rule set
- **AND** hardcoded credentials, unsafe process execution, and prohibited raw
  Jira/GitLab clients SHALL fail the gate

#### Scenario: Generated Python cache is tracked

- **WHEN** `git ls-files` contains `.pyc` or `__pycache__` paths
- **THEN** the quality gate SHALL fail with the tracked paths
