# agent-core-quality-gate Specification

## Purpose

Establish enforceable quality gates for all TDT Python agent-core repositories. Defines minimum test coverage, type-checking requirements, lint standards, file size boundaries, environment health, and SDK discipline that MUST pass before any code is committed.
## Requirements
### Requirement: Workspace repo inventory and scope

The quality gate SHALL apply to a fixed inventory of Python repositories under `/Users/lekhanhvinh/Developer/tdt/`. Each repo SHALL declare its package layout (the `--cov=` target) so coverage, mypy, and lint checks all use the same root.

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
- **THEN** it SHALL be added to the inventory in this spec before the next quality-gate audit
- **AND** the inventory table SHALL list its declared package root
- **AND** PRs that introduce new repos SHALL update this scenario in the same change

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

### Requirement: Working build environment prerequisite

Every repo in the inventory SHALL have a working `uv`-managed virtual environment that can execute `pytest`, `mypy`, and `ruff` from the repo root. CI SHALL fail closed when the environment is broken; a missing or stale `.venv` SHALL NOT be silently treated as "0 errors" or "0 failures".

#### Scenario: Stale venv detected

- **WHEN** `uv run pytest` or `uv run mypy` exits with `cannot execute: No such file or directory` or similar venv resolution errors
- **THEN** the quality gate runner SHALL classify the repo as `BROKEN_ENV`
- **AND** the failure SHALL be reported separately from `FAIL` (test/coverage/type failures)
- **AND** the runner SHALL NOT report the repo as `PASS`

#### Scenario: ops-automation-suite venv rebuild

- **WHEN** `ops-automation-suite/.venv` is broken or points at a stale path
- **THEN** `uv sync --reinstall` SHALL be run from the repo root to rebuild the venv
- **AND** the rebuild SHALL be re-verified by running `uv run mypy src/ops_automation` and `uv run pytest -q`
- **AND** the repo SHALL only be re-classified after both commands return real exit codes

### Requirement: Minimum test coverage of 80%

All Python repositories SHALL maintain at least 80% test coverage as measured by `pytest-cov`. Coverage SHALL be enforced per-repo in CI and SHALL NOT be lowered by any PR.

#### Scenario: Coverage gate enforced in CI

- **WHEN** CI runs `uv run pytest --cov=<package>`
- **THEN** the command exits 0 only if total coverage >= 80%
- **AND** the `--cov-fail-under=80` flag is set in each repo's CI pipeline

#### Scenario: Coverage gap tracked

- **WHEN** coverage drops below 80%
- **THEN** the CI pipeline fails
- **AND** a `term-missing` report identifies uncovered lines

#### Scenario: Per-module coverage minimums

- **WHEN** evaluating coverage for a specific module
- **THEN** no module SHALL have 0% coverage
- **AND** modules below 50% coverage SHALL be flagged as technical debt in the repo README

#### Scenario: Module-level coverage enforcement in CI

- **WHEN** a new module is added to a repo (e.g., `src/kbs/backup/`)
- **THEN** the CI pipeline SHALL check per-module coverage thresholds
- **AND** modules with 0% coverage SHALL block merge
- **AND** the `--cov-fail-under` flag SHALL apply per-directory, not just globally
- **AND** modules below 50% SHALL generate a technical debt entry in the repo README automatically

#### Scenario: Zero-coverage module detection

- **WHEN** `pytest --cov` reports any source file at 0% coverage
- **THEN** the CI pipeline SHALL fail with a descriptive message listing the uncovered files
- **AND** the failure message SHALL include the line count of uncovered code for triage priority
- **Example**: `src/kbs/backup/` (6 files, ~700 lines, 0% coverage) → BLOCK

#### Scenario: Coverage regression triggers a triage task

- **WHEN** a repo's overall coverage falls by more than 3 percentage points from one audit to the next
- **THEN** the regression SHALL be tracked as a P1 task in `tasks.md`
- **AND** the triage SHALL identify the commit range responsible
- **AND** new modules added in that range SHALL be inspected for missing tests
- **Example**: `jira-daily-reports` 74% → 56% (-18pts) after `sprint_report_sheet.py` was added → P1

### Requirement: Zero mypy errors in strict mode

All Python repositories SHALL pass `uv run mypy <package>` with zero errors. The `strict = true` flag SHALL be set in `pyproject.toml` for each repo.

#### Scenario: Type check passes

- **WHEN** running `uv run mypy <package>`
- **THEN** exit code is 0
- **AND** no errors are reported

#### Scenario: Any returns from SDK are narrowed

- **WHEN** a third-party SDK returns `Any`
- **THEN** the wrapper code SHALL use `typing.cast()` or TypedDict to narrow the type
- **AND** mypy SHALL NOT report `no-any-return`

#### Scenario: Gradual strictness increase

- **WHEN** a repo has existing `disable_error_code` entries
- **THEN** each release SHALL remove at least one suppressed error code
- **AND** the `disable_error_code` list SHALL shrink over time

### Requirement: Zero failing tests

All test suites SHALL pass with zero failures before any commit to shared branches.

#### Scenario: Rich ANSI codes stripped in CLI test assertions

- **WHEN** a test asserts on CLI help text that Rich may wrap in ANSI codes
- **THEN** the test SHALL strip ANSI codes using `re.sub(r'\x1b\[[0-9;]*m', '', output)` before assertion
- **AND** the assertion SHALL pass regardless of Rich colorization state

#### Scenario: Test failures block PR

- **WHEN** `uv run pytest` reports any failures
- **THEN** the PR SHALL NOT be merged
- **AND** the failures SHALL be fixed before re-requesting review

#### Scenario: Test regression triggers triage

- **WHEN** a previously green repo grows new failing tests between audits
- **THEN** the regression SHALL be filed as a P1 task identifying the failing modules
- **AND** the audit log SHALL preserve the prior pass/fail count for diff
- **Example**: `jira-daily-reports` 5 fails → 22 fails after `sprint_report_sheet.py` landed → P1

### Requirement: File size boundaries

No single Python source file SHALL exceed 800 lines. Files exceeding 400 lines SHALL be flagged for review and SHALL include a comment justifying the size.

#### Scenario: Monolith file extraction

- **WHEN** a file exceeds 400 lines
- **THEN** it SHALL be considered for splitting into focused modules
- **AND** the split SHALL preserve all existing public APIs

#### Scenario: PatchedJira extraction (completed)

- **WHEN** `src/tdt_core/clients/jira.py` is below 400 lines
- **THEN** the extraction is considered complete
- **AND** `from tdt_core.clients.jira import PatchedJira` continues to work
- **NOTE**: As of 2026-05-31, jira.py is 315 lines. The single-file design was kept rather than a multi-mixin split, and that is acceptable since the file is now under the flag threshold.

#### Scenario: Epic report CLI extraction

- **WHEN** `epic_report/cli.py` exceeds 800 lines (validated at 1428 lines)
- **THEN** command logic SHALL be extracted to `commands/epic.py`, `commands/sprint.py`, `commands/compare.py`
- **AND** `cli.py` SHALL retain only entry point and config callback
- **AND** all subcommands SHALL function identically

#### Scenario: Sprint report sheet extraction

- **WHEN** `jira-daily-reports/src/jira_daily_reports/reports/sprint_report_sheet.py` exceeds 800 lines (validated at 1255 lines)
- **THEN** it SHALL be split into focused modules under `reports/sprint/` (e.g. `aggregation.py`, `verdicts.py`, `rendering.py`)
- **AND** the split SHALL preserve the public `run()` entry point used by `cli.py`
- **AND** the 22 failing tests SHALL be triaged and fixed as part of this work

#### Scenario: jira-skill field config extraction

- **WHEN** `jira-skill/src/jira_skill/field_config.py` is at or above 768 lines (currently 768)
- **THEN** it SHALL be split before crossing 800 lines
- **AND** the split SHALL keep the public field-config API stable for downstream callers

#### Scenario: Kanban CLI extraction

- **WHEN** `jira-kanban-from-spreadsheet/src/kbs/cli.py` exceeds 400 lines (validated at 732 lines)
- **THEN** subcommands SHALL be extracted to `src/kbs/commands/` (one module per Click subcommand)
- **AND** the entry point SHALL stay in `cli.py` (target ~300 lines)

### Requirement: File size thresholds aligned across ecosystem

The file size threshold SHALL be 800 lines maximum, with review flagging at 400 lines. This supersedes any conflicting thresholds in `ccg/verify-quality` (500 lines) or other quality tools. All quality gate tools SHALL use these values.

#### Scenario: verify-quality threshold alignment

- **WHEN** `ccg/verify-quality` skill is invoked
- **THEN** it SHALL use 800 lines as the hard maximum (not 500)
- **AND** it SHALL flag files at 400 lines for review (not 500)
- **AND** the skill documentation SHALL reference this spec as the authoritative source

### Requirement: No unused dependencies

All dependencies declared in `[project]` SHALL be imported and used in source code. All dependencies imported in source SHALL be declared in `[project]` or `[dependency-groups]`.

#### Scenario: Unused dependency detection

- **WHEN** a dependency is declared but never imported
- **THEN** it SHALL be removed from `pyproject.toml`
- **AND** `uv lock` SHALL be re-run to update the lockfile

#### Scenario: tenacity removal (webhook-receiver)

- **WHEN** `tenacity` is found in webhook-receiver `pyproject.toml`
- **THEN** it SHALL be removed (declared but not imported in any source file)
- **AND** `uv lock --check` SHALL still pass

### Requirement: Canonical SDK client usage

All Jira and GitLab API access SHALL route through `tdt_core.clients` factories. No downstream code SHALL instantiate `atlassian.Jira` or `gitlab.Gitlab` directly.

#### Scenario: Jira access through PatchedJira

- **WHEN** code needs to call Jira APIs
- **THEN** it SHALL import from `tdt_core.clients.jira`
- **AND** it SHALL NOT instantiate `atlassian.Jira` directly
- **AND** it SHALL NOT call `jira.post("rest/api/3/...")` from outside `PatchedJira`

#### Scenario: GitLab access through factory

- **WHEN** code needs to call GitLab APIs
- **THEN** it SHALL use `GitlabClientFactory.from_env().create_client()`
- **AND** it SHALL NOT instantiate `gitlab.Gitlab` directly
- **AND** it SHALL call `.auth()` before `.user`

#### Scenario: No shelling out to CLI tools from Python

- **WHEN** code needs Jira or GitLab operations
- **THEN** it SHALL NOT shell out to `acli` or `glab`
- **AND** it SHALL use the factory methods from `tdt_core`

### Requirement: No hardcoded secrets

No API keys, passwords, tokens, credentials, or credential-equivalent values SHALL appear in any tracked artifact in `agent-core`, `agent-docs-sync`, or `agent-harness`. Runtime secrets SHALL be loaded from `~/.tdt/.env` through the centralized TDT environment boundary, and CI SHALL scan tracked files and relevant repository history independently of local hooks.

#### Scenario: Credential loading

- **WHEN** code needs credentials
- **THEN** it SHALL use `tdt_core.env.load_tdt_env()` and environment lookup
- **AND** it SHALL NOT read credentials from committed literals, examples, fixtures, generated configuration, or hardcoded secret paths

#### Scenario: Tracked artifact contains a credential
- **WHEN** a tracked Python, YAML, TOML, JSON, Markdown, fixture, lock, or generated configuration artifact contains a credential-like value
- **THEN** the repository CI secret gate SHALL fail before merge
- **AND** diagnostic output SHALL redact the detected value while identifying the affected path and rule

#### Scenario: Local hook is absent or bypassed
- **WHEN** a commit reaches CI without running the repository pre-commit hook
- **THEN** the independent CI secret scan SHALL still inspect the required tracked-file and commit range
- **AND** a detected secret SHALL block the change

#### Scenario: Secret exception is required
- **WHEN** a deterministic non-secret fixture triggers a false positive
- **THEN** an exception SHALL be scoped to the smallest stable fingerprint or fixture path with a documented rationale and owner
- **AND** a broad repository, file-type, or rule-family exclusion SHALL NOT be accepted

#### Scenario: Exposed credential is contained
- **WHEN** a credential is found in tracked history
- **THEN** it SHALL be revoked or rotated unless an owner-approved local-only exception proves there are no remotes, remote-tracking references, tags, secondary worktrees, exported clones, bundles, backups, or external distributions
- **AND** a local-only exception SHALL require complete history sanitation, object pruning, duplicate removal, and redacted evidence
- **AND** discovery of any external copy SHALL invalidate the exception and require immediate rotation

#### Scenario: Retained local key is centralized and history is sanitized
- **WHEN** the owner approves retaining a credential under the local-only exception
- **THEN** the credential SHALL exist only in `$TDT_HOME/.env` with mode `0600`
- **AND** local Git refs, reflogs, and reachable/unreachable objects SHALL not contain the credential or original exposure commit
- **AND** `~/.agentmemory/.env` and other runtime files SHALL not duplicate the credential
- **AND** AgentMemory SHALL receive the centralized value through its sourced LaunchAgent environment
- **AND** `$TDT_HOME/state/agent-docs-sync/security/local-history-sanitization.json` SHALL have parent mode `0700`, file mode `0600`, and contain only redacted scope, rewrite, scan, duplicate-removal, runtime-verification, operator, and UTC timestamp results

#### Scenario: Secret detection in CI

- **WHEN** a commit contains a hardcoded secret
- **THEN** the pre-commit `gitleaks` hook SHALL block the commit

### Requirement: ECC/CCG skill consolidation

Each capability domain SHALL have exactly one source of truth across the ECC plugin, CCG quality gates, and built-in skills. Duplicates SHALL be deprecated with forward references.

#### Scenario: Security review single source

- **WHEN** a security review is needed
- **THEN** the `security-review` built-in skill SHALL be the primary entry point
- **AND** ECC `security-review` and CCG `verify-security` SHALL forward to it

#### Scenario: Verification pipeline single source

- **WHEN** pre-commit verification is needed for a Python repo
- **THEN** `uv run pytest --cov --cov-fail-under=80`, `uv run mypy <package>`, and `uv run ruff check <package>` SHALL be the execution engine
- **AND** ECC `verification-loop` SHALL orchestrate these Python-native tools
- **AND** built-in `verification-before-completion` SHALL delegate to the verification-loop orchestrator
- **AND** CCG Node.js scanners SHALL NOT be used for Python repos (they are reserved for JS/TS repos)

#### Scenario: Multi-agent orchestration single source

- **WHEN** multi-agent coordination is needed
- **THEN** built-in TeamCreate SHALL be the execution mechanism
- **AND** CCG ant-colony protocol SHALL define the role system
- **AND** ECC `agentic-os` SHALL define the persistence model
- **AND** each SHALL reference the others, not duplicate functionality

### Requirement: CI workflow includes secret scanning

Every repository in the three-repository verification set (`agent-core`,
`agent-docs-sync`, `agent-harness`) SHALL have a `.github/workflows/ci.yml`
that includes gitleaks secret scanning with `fetch-depth: 0` and the pinned
gitleaks image version. This requirement operationalizes the existing
"No hardcoded secrets" requirement with a specific CI mechanism.

#### Scenario: CI workflow exists with gitleaks config
- **WHEN** `test_secret_scanning_policy.py` reads `.github/workflows/ci.yml`
- **THEN** the file SHALL contain `fetch-depth: 0`
- **AND** the file SHALL reference the pinned gitleaks image (`docker://ghcr.io/gitleaks/gitleaks:v8.30.1`)
- **AND** the file SHALL contain `git --redact=100 --no-banner --verbose .`
- **AND** the test SHALL pass

#### Scenario: CI workflow passes actionlint validation
- **WHEN** `actionlint .github/workflows/ci.yml` is run in any of the three repositories
- **THEN** the command SHALL exit with code 0

#### Scenario: CI secret scan does not produce false positives
- **WHEN** the gitleaks CI workflow runs against the full git history
- **THEN** the scan SHALL complete with zero findings
- **AND** any deterministic non-secret findings SHALL be resolved through
  exact-fingerprint `.gitleaksignore` entries per the existing exception policy

