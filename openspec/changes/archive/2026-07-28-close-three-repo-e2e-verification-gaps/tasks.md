## 1. Freeze baseline and high-risk contracts

- [x] 1.1 In `tdt-meta`, record the pre-implementation source identity for
  `agent-core`, `agent-docs-sync`, and `agent-harness`: HEAD, tracked diff hash,
  sorted untracked paths, frozen framework versions, test counts, coverage, and
  the 2026-07-28 E2E failures. Preserve all pre-existing dirty files.
- [x] 1.2 Before editing harness symbols, require current GitNexus indexes in
  all three repos, then rerun impact for `build_graph`, `WorkflowRunner`,
  `GateConfig`, and CLI `run`; obtain explicit confirmation for the
  HIGH/CRITICAL scope and attach the affected process list (fresh baseline:
  `build_graph` affects 8 symbols and 9 processes) to implementation evidence.
- [x] 1.3 In `agent-harness/tests/`, add characterization tests for current
  graph topology, gate request identity, authorized resume, rejection routing,
  checkpoint version rejection, and same-process non-durable behavior. Extend
  rather than overwrite the existing untracked verification tests.
- [x] 1.4 In `agent-core/tests/skill_system/` and `agent-docs-sync/tests/`, add
  failing fixtures that reproduce aliased skill roots/catalog Markdown noise,
  test-source discovery, ambiguous audit compliance, and tracked-cache
  contamination before implementation begins.

## 2. Repair the harness CLI lifecycle

- [x] 2.1 In `agent-harness/src/agent_harness/cli.py` (or a focused CLI support
  module), implement one configuration resolver used by `run`, `status`,
  `report`, `approve`, and `reject`; add the same `--config` override to every
  lifecycle command while retaining `$TDT_HOME` defaults.
- [x] 2.2 Add lifecycle preflight that rejects empty approvers for protected
  runs and rejects non-durable persistence or a missing `TDT_POSTGRES_URL` for
  `run`, `status`, `report`, `approve`, and `reject` before graph compilation or
  checkpoint access. Keep the programmatic same-process non-durable runner
  contract intact.
- [x] 2.3 Add a typed CLI error model and centralized text/JSON rendering for
  configuration, unknown-run, backend mismatch, checkpoint version,
  authorization, expiry, replay, and decision identity failures. Verify JSON
  stdout contains exactly one document and operational logs use stderr. Missing
  runs SHALL use stable code `run_not_found` without printing backend URLs or
  credentials.
- [x] 2.4 Update `agent-harness` status/report/gate commands to reopen the same
  configured Postgres checkpointer and `thread_id` without creating fallback
  in-memory state or a new checkpoint for unknown runs.
- [x] 2.5 Add separate-operating-system-process CLI tests covering default
  fail-fast behavior, explicit config parity, unknown runs, human-readable
  remediation, JSON error stability, and preservation of completed stages
  after process termination and restart, using the selected real-backend test
  fixture rather than an in-memory fallback.
- [x] 2.6 Correct `agent-harness/README.md` and `docs/configuration.md`,
  `docs/workflow.md`, and `docs/operations.md` so quick starts include durable
  Postgres plus approver setup and use the implemented `--decision-id`,
  `--config`, approve, reject, status, and report syntax.

## 3. Prove durable restart behavior with real PostgreSQL

- [x] 3.1 After explicit database-test approval, inspect and preserve the
  existing untracked `agent-core/docker-entrypoint-initdb.d/20-create-harness-db.sql`
  and `agent-harness/tests/test_postgres_integration.py`; add
  `testcontainers[postgres]` as a test-only dependency through `uv`, and extend
  the files only where needed to provision an isolated disposable test database
  through the shared checkpointer setup contract.
- [x] 3.2 Add a real-PostgreSQL subprocess test for
  `run -> process restart -> status -> approve -> next gate -> reject/backtrack
  -> report/history`, asserting the same run/thread/native interrupt and no
  rerun of completed artifact stages. Use one explicit `TDT_POSTGRES_TEST_URL`
  when supplied, otherwise a pinned Testcontainers `postgres:18.4-trixie`
  backend, and pass its driverless DSN to every subprocess. Record
  `langgraph==1.2.9` and `langgraph-checkpoint-postgres==3.1.0` as the baseline
  and assert the public async saver setup completes before graph compilation.
- [x] 3.3 Add real-backend negative tests for unknown run, wrong thread,
  mismatched stage/digest/interrupt, unauthorized actor, expired decision, and
  replay; hash the checkpoint state before/after each rejection to prove no
  mutation.
- [x] 3.4 Add bounded PostgreSQL readiness probing, isolated database/schema
  naming, deterministic cleanup, and CI configuration that supplies
  `TDT_POSTGRES_TEST_URL` without committing credentials. Prefer the explicit
  DSN; otherwise start the pinned Testcontainers backend with Docker-daemon
  access, use context-managed cleanup, and record the backend identity. The
  test SHALL fail rather than downgrade to in-memory when neither provider is
  available.
- [x] 3.5 Run the PostgreSQL suite twice from fresh processes to prove setup is
  idempotent, using fresh disposable containers or isolated external fixtures,
  and capture commands, image/backend version, readiness, cleanup result, and
  timing in implementation evidence.

## 4. Make agent-core skill diagnostics actionable

- [x] 4.1 In `agent-core/src/agent_core/skill_system/`, implement a shared skill
  candidate enumerator for the loader and doctor: canonicalize resolved paths,
  accept `<skill>/SKILL.md`, retain frontmatter-bearing flat Markdown support,
  and ignore catalog/reference Markdown without skill frontmatter.
- [x] 4.2 Update `SkillLoader` shadow handling so two aliases to one canonical
  file are loaded once without warning, while distinct canonical files with the
  same skill name retain first-directory-wins and one structured shadow issue.
- [x] 4.3 Update `diagnose_profile()` so explicitly included missing,
  malformed, scope-excluded, or unloadable skills are structured errors and
  cause a non-zero doctor exit; ordinary inactive malformed candidates remain
  actionable warnings.
- [x] 4.4 Isolate `agent-core skills doctor --json` stdout from structlog output
  and verify it emits exactly one object with `errors`, `warnings`, and `info`.
- [x] 4.5 Add loader/doctor tests for symlink aliases, distinct shadow sources,
  catalog docs, flat legacy skills, malformed explicit includes, profile scope,
  conflicts, missing directories, JSON parsing, and exit status.
- [x] 4.6 Run doctor against the configured `android-scanner` profile and record
  logical (de-duplicated) diagnostics. Do not modify developer credentials or
  silently rewrite `~/.tdt/config.yaml`; unresolved profile-specific issues
  SHALL remain explicit evidence.

## 5. Tighten docs-sync boundaries and audit semantics

- [x] 5.1 In `agent-docs-sync`, centralize production-source path policy and
  apply it to discovery, scanner, classifier, canonical pipeline, and audit.
  Default exclusions SHALL cover tests, generated sources, `.venv`, caches,
  bytecode, coverage/build output, and repository metadata; internal production
  modules SHALL remain visible in scan evidence.
- [x] 5.2 Build deterministic actionable-public-surface provenance from package
  exports, configured console scripts/CLI entrypoints, deployment/config
  artifacts, and explicit mappings. Treat other internal production findings
  as informational, and add explicit include controls for test/internal audits
  with the effective boundary recorded.
- [x] 5.3 Replace ambiguous audit result semantics with
  `execution_succeeded`, `documentation_compliant`, stable finding counts, and
  boundary metadata. Retain `validation_passed` for exactly one compatibility
  release as a deprecated alias of `documentation_compliant`, never of
  `execution_succeeded`.
- [x] 5.4 Add `docs-sync audit --strict` with deterministic non-zero exit status
  for actionable gaps, broken local links, or Diataxis violations; preserve
  informational zero-exit audit behavior outside strict mode.
- [x] 5.5 Remove all 17 tracked `.pyc`/`__pycache__` artifacts discovered by
  the TDD repository-hygiene fixture (including the two rewritten during the
  baseline verification), verify ignore rules cover Python caches, and retain
  the test/CI assertion that `git ls-files` contains no `.pyc` or
  `__pycache__` paths.
- [x] 5.6 Add deterministic CLI and pipeline tests for default/expanded
  discovery, strict/informational audit, JSON compatibility fields, cache
  exclusion, local-link validation, and fixture-repository parity.
- [x] 5.7 Update `agent-docs-sync/README.md` and CLI/configuration documentation
  with production scan boundaries, strict audit semantics, exit codes, and the
  deprecated field migration.

## 6. Enforce coverage, security, and repository hygiene

- [x] 6.1 Update repository quality configuration/CI so `agent-core`,
  `agent-docs-sync`, and `agent-harness` run package-correct Ruff, formatting,
  strict mypy, pytest-cov with `--cov-fail-under=80`, term-missing output, and a
  zero-coverage source-module check.
- [x] 6.2 Raise `agent-core` coverage from the verified 77% baseline to at least
  80% with behavior tests for MCP/tool preparation, streaming approval, CLI
  evaluation, scheduler setup, tracing, memory/checkpointer, and optional
  integration boundaries. Every current 0% source module SHALL gain behavior
  coverage or be removed from the production package; do not increase omit
  lists to meet the threshold.
- [x] 6.3 Raise `agent-docs-sync` coverage from the verified 63% baseline to at
  least 80% with behavior tests for discovery pipeline, canonical/full DAG
  branches, state persistence, gateway errors, observability hooks/scorers, and
  strict audit. Every current 0% source module SHALL gain behavior coverage or
  be removed from the production package.
- [x] 6.4 Keep `agent-harness` coverage at or above its verified 84% baseline
  while adding the CLI and real-durability tests; any regression below 84% must
  be explained and SHALL still remain above the 80% hard gate.
- [x] 6.5 Enable applicable Ruff security rules over production source in all
  three repos with documented test-only exclusions. Add deterministic checks
  for hardcoded credentials, unsafe process execution, prohibited raw
  Jira/GitLab clients, and tracked Python caches without adding a runtime
  dependency.

## 7. Cross-repository verification and evidence

- [x] 7.1 In each repository run `uv sync --frozen`, package-targeted
  `uv run ruff check`, `uv run ruff format --check`, strict mypy, and the full
  coverage suite. Record exact commands, versions, pass/fail/skip counts, and
  total/module coverage.
- [x] 7.2 Run process-level feature smoke tests for agent-core config, health
  classification, skills doctor/list, and generated-agent scaffold plus its
  smoke test.
- [x] 7.3 Run docs-sync check, production/expanded discover, informational and
  strict audit, local validation, and canonical fixture pipeline. Any
  write-capable generation test SHALL remain confined to a disposable fixture.
- [x] 7.4 Run harness default preflight and durable
  run/status/approve/reject/report using separate operating-system processes,
  plus JSON/text negative paths and rollback/backtrack behavior against the
  selected Testcontainers or explicitly supplied disposable PostgreSQL backend.
- [x] 7.5 Run strict validation for this change and all five affected canonical
  capabilities, confirm each GitNexus index matches the verified commit, then
  run `detect-changes --scope compare --base-ref main` separately in each
  target repo. Investigate every unexpected symbol or execution flow before
  completion.
- [x] 7.6 Create `implementation-evidence.md` in this change containing the
  three-repository source identity, verification matrix, Postgres fixture
  evidence, exact framework version tuple, coverage/security results, remaining
  environmental limitations, and links to logs without credentials.
- [x] 7.7 Exercise rollback in disposable workspaces: restore the prior CLI
  composition while preserving fail-closed graph behavior, restore the docs
  compatibility alias behavior, and restore diagnostic presentation without
  changing loader precedence. Record successful rollback and re-apply results.
- [x] 7.8 Confirm final `git status` in every repo contains only intended change
  files plus the exact pre-existing user changes; no test-generated bytecode,
  coverage, database, or temporary artifacts may remain.
