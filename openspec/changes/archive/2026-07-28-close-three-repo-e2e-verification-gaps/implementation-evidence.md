# Implementation Evidence

## Pre-implementation baseline — 2026-07-28

This baseline was captured before implementation edits. Worktrees were dirty;
the hashes and inventories below are therefore part of the verified source
identity and MUST be preserved when evaluating later diffs.

### Source identity

| Repository | HEAD | Tracked binary diff SHA-256 | Tracked dirty paths | Untracked paths |
|---|---|---|---|---|
| `agent-core` | `3aff416eca0801ea3a1804892bc5700aac71ebf5` | `04cc99ddb2107c0ac90ae0296cc7cb18794923259b67386abaad64c9d8a1e43d` | `AGENTS.md`; `tests/test_dependency_baseline.py`; `tests/test_docker_local_dev.py` | `docker-entrypoint-initdb.d/20-create-harness-db.sql` |
| `agent-docs-sync` | `47e37e9a7c055e4db82e391b956a14f6d651d1b1` | `4b0cef0d2c13f4d69e083b82ec936b747de3254882110806d7b6ebbd9bca2ed1` | `AGENTS.md`; `CLAUDE.md`; `src/agent_docs_sync/__pycache__/cli.cpython-314.pyc`; `src/agent_docs_sync/workflows/__pycache__/__init__.cpython-314.pyc`; `tests/test_dependency_baseline.py` | none |
| `agent-harness` | `7cb90e66cb8886401b2f0875927a87b06a1d9c23` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | none | `tests/test_dependency_baseline.py`; `tests/test_postgres_integration.py` |

The `AGENTS.md` / `CLAUDE.md` changes above are refreshed GitNexus generated
counts. The two docs-sync bytecode changes were produced by the verification
CLI imports and are cleanup targets in task 5.5. All other listed files
predated implementation and are user-owned.

### Code-intelligence identity

All three GitNexus indexes were rebuilt and confirmed current at their listed
HEAD commits on 2026-07-28 before fresh impact analysis.

### Frozen framework tuple

Captured through `importlib.metadata` in the frozen `agent-core` environment:

- `langgraph==1.2.9`
- `langgraph-checkpoint-postgres==3.1.0`
- `pydantic-ai==2.18.0`
- `pydantic-ai-harness==0.11.0`

### Baseline quality matrix

Commands used in each repository:

```text
uv sync --frozen
uv run ruff check src tests
uv run ruff format --check src tests
uv run mypy <package> --strict
uv run pytest tests/ --cov=<package> --cov-report=term --cov-report=json:<path>
```

| Repository | Frozen sync | Ruff | Format | Strict mypy | Tests | Coverage |
|---|---:|---:|---:|---:|---:|---:|
| `agent-core` | pass | pass | pass | 93 source files, pass | 535 passed | 77% |
| `agent-docs-sync` | pass | pass | pass | 44 source files, pass | 166 passed | 63% |
| `agent-harness` | pass | pass | pass | 41 source files, pass | 195 passed, 1 PostgreSQL test skipped | 84% |

Total executable suite result: **896 passed, 1 skipped**.

### Reproduced end-to-end gaps

1. `agent-harness run --ticket TDT-E2E --repo agent-harness --json` with
   defaults failed before intake with `ValueError: Protected gate stages require
   a non-empty approver allowlist` and a Rich traceback.
2. With an explicit approver, the first harness process reached
   `status=running`, `current_stage=spec`; a second process running `status`
   failed with `KeyError: Unknown workflow run`, proving in-memory state loss.
3. `agent-core health --detail --json` returned degraded because gateway and
   PostgreSQL were intentionally unconfigured.
4. `agent-core skills doctor` emitted 18 invalid-file and 125 shadow-warning
   occurrences; the repo and global skill roots resolve to the same physical
   files, so the shadow volume is alias noise.
5. `docs-sync audit --repo . --output json` completed but reported 82 gaps and
   8 Diataxis violations while `validation_passed=true`, conflating execution
   and compliance.
6. Importing docs-sync CLI modules rewrote two tracked `.pyc` files.
7. No Bandit executable was installed; targeted scans found no real embedded
   credentials, raw Jira/GitLab clients, or unsafe execution candidates.

## Impact evidence

Fresh GitNexus indexes were used for all results:

| Symbol | Risk | Impact |
|---|---|---|
| `agent_harness.workflow.graph.build_graph` | **CRITICAL** | 8 upstream symbols, 1 direct caller, 9 affected processes, 2 modules |
| `agent_harness.cli.run` | **HIGH** | 4 direct upstream CLI lifecycle functions and 4 affected processes |
| `agent_harness.workflow.runner.WorkflowRunner` | LOW | 1 direct importing file (`cli.py`) |
| `agent_harness.config.GateConfig` | LOW | 3 direct importing files (`cli.py`, `runner.py`, `agents/factory.py`) |

The CRITICAL graph root reaches these process families: CLI status, approve,
reject, report, runner status, stream, resume, history, and `_resume_gate`.
The HIGH CLI `run` path directly reaches status, report, approve, and reject.

Implementation design contains this risk by placing durable preflight and
error composition outside `build_graph`; graph semantics remain unchanged
unless implementation evidence proves that an edit is unavoidable.

Explicit HIGH/CRITICAL source-edit confirmation: **confirmed by the user on
2026-07-28**. The confirmation authorizes the scoped harness implementation;
the design constraint to avoid `build_graph` edits remains in force.

### Characterization gate

The existing harness characterization files already covered the required
contracts, so no duplicate tests were added:

```text
uv run pytest tests/test_workflow.py tests/test_graph_validation.py \
  tests/test_convergence_contracts.py tests/test_gate_trace.py \
  tests/test_runner_contracts.py tests/test_durable_fixtures.py -q
```

Result: **67 passed**. Coverage includes topology/reachability, one-target gate
continuations, deterministic request identity, authorized resume, rejection
backtrack, replay/identity rejection, checkpoint-version rejection, and
same-process in-memory runner behavior.

### TDD regression gate

Added failing fixtures before implementation:

- `agent-core/tests/skill_system/test_diagnostics.py`: symlink alias shadow
  noise, catalog Markdown misclassification, and malformed explicit include.
  Baseline result: **3 failed**, each at the intended assertion.
- `agent-docs-sync/tests/test_tools/test_scanner.py`,
  `tests/test_canonical_pipeline.py`, and `tests/test_dependency_baseline.py`:
  test-source leakage, missing execution/compliance split, and tracked cache
  contamination. Baseline result: **3 failed, 12 passed**.

The cache fixture identified **17** tracked bytecode paths; task 5.5 was
expanded from the two files rewritten during verification to all tracked cache
artifacts. Post-change GitNexus detection classified both test-only edits LOW
risk with zero affected execution processes; unrelated pre-existing dirty
symbols remain recorded in the source baseline.

## Implementation and final verification

### Harness lifecycle composition — tasks 2.1–2.4

Implemented one shared CLI resolver and preflight in
`agent-harness/src/agent_harness/cli.py`. All five lifecycle commands now
accept `--config`, require durable PostgreSQL configuration, and reuse the
resolved runner. Protected `run` additionally requires a non-empty approver
allowlist. `approve` and `reject` now support `--json`, and `_resume_gate`
receives the already-configured runner instead of independently loading
defaults. `WorkflowRunner`, its same-process in-memory behavior, and
`build_graph` were not changed.

Expected lifecycle failures are normalized to credential-safe codes including
`run_not_found`, `checkpoint_version_mismatch`, `authorization_failed`,
`decision_expired`, `decision_replayed`, and `decision_mismatch`. JSON actions
redirect incidental stdout to stderr while the public result remains exactly
one JSON document.

Verification:

```text
uv run ruff check src/agent_harness/cli.py tests/test_cli_lifecycle.py
uv run mypy src/agent_harness --strict
uv run pytest -q
```

Result: Ruff passed; strict mypy passed for 41 source files; the full harness
suite passed with one existing real-PostgreSQL skip. Focused lifecycle and
runner tests passed **40/40**. A separate operating-system-process test proves
the default protected run fails before graph construction and returns one
parseable JSON error document.

Post-change GitNexus detection reports 8 changed CLI symbols and 26 affected
flows at CRITICAL risk. The expanded count reflects the intentional shared
composition across `run`, `status`, `report`, `approve`, and `reject`; no graph
or runner symbol changed. Task 2.5 remains open until the PostgreSQL-approved
cross-process unknown-run and completed-stage preservation cases can run.

Task 2.6 updated the README and configuration, workflow, and operations guides
with durable PostgreSQL and approver prerequisites; shared `--config` usage;
implemented `--decision-id`, approve/reject/status/report syntax; JSON behavior;
and the same-process-only boundary for programmatic in-memory runners. The
focused CLI/runner suite remained **40/40 passed** after the documentation edit.

### Agent-core skill diagnostics — tasks 4.1–4.6

Added a shared canonical candidate enumerator used by `SkillLoader` and
`diagnose_profile`. Directory `SKILL.md` sources are always considered; flat
Markdown is considered only with skill frontmatter or an explicit include.
Resolved physical sources are de-duplicated before parsing and shadow analysis,
while distinct same-name sources retain first-directory precedence and one
structured shadow finding. Explicit missing, malformed, excluded, and
scope-inactive includes now produce `included_skill_unloadable` errors.

The doctor JSON path now reads the live CLI JSON flag, routes configured logging
handlers to stderr, and emits one `errors`/`warnings`/`info` envelope on stdout.
Focused verification passed **52/52**, Ruff passed, strict mypy passed for 94
source files, and the complete agent-core suite passed.

Read-only configured-profile command:

```text
uv run agent-core --json skills doctor --profile android-scanner
```

Captured through a subprocess with separate streams: exit 1, exactly one JSON
stdout document, 3 errors, 7 warnings, 2 info records, and 1 operational stderr
line. The errors are three missing explicit includes: `android-scan-rules`,
`scan-workflow`, and `sheet-output-format`. Warnings are six pre-existing
frontmatter validation failures plus one genuine distinct-source
`openspec-update-change` shadow. No developer configuration or credentials were
modified. This replaces the noisy baseline of 18 invalid-file and 125 shadow
occurrences with logical diagnostics.

Post-change GitNexus detects the expected loader/reload and doctor processes.
Its aggregate HIGH result also includes the recorded pre-existing dirty
`AGENTS.md` and user-owned dependency/docker tests; no unrelated production
process was introduced.

### Docs-sync cache hygiene — task 5.5

Removed the exact 17 tracked `.pyc`/`__pycache__` paths identified by the TDD
fixture and removed them from the Git index. `.gitignore` already contains the
repository-wide `__pycache__/` rule. `git ls-files` now returns no Python cache
paths, and `uv run pytest -q tests/test_dependency_baseline.py` passes **3/3**.
GitNexus classifies the aggregate cleanup plus pre-existing generated/test
changes LOW with zero affected processes.

### Docs-sync production boundary and truthful audit — tasks 5.1–5.7

Added a centralized source-scope policy used by scanner and canonical discovery.
Default scans exclude tests, caches, virtual environments, generated metadata,
coverage/build output, and repository metadata while preserving internal
production files as informational evidence. `--include-tests` and
`--include-internal` produce an explicit expanded boundary.

Actionable provenance is deterministic from package exports, configured
`[project.scripts]` entrypoints, deployment/configuration artifacts, skills,
and `doc-mapping.yaml`. Audit now separates `execution_succeeded` from
`documentation_compliant`, publishes actionable/excluded counts and effective
boundary metadata, and retains deprecated `validation_passed` as a compliance
alias. `audit --strict` exits 1 on actionable gaps while informational audit
preserves exit 0.

Verification:

- Focused boundary/audit suite: **35 passed**.
- Complete docs-sync suite: **176 passed**.
- Ruff and format: pass across `src` and `tests`.
- Strict mypy: pass across 45 source files.
- Production discover: exit 0, one JSON document, production boundary,
  47 mapped artifacts.
- Expanded discover: exit 0, one JSON document, expanded boundary,
  82 mapped artifacts.
- Informational audit: exit 0, non-compliant, 36 actionable and 14 informational
  gaps.
- Strict audit: exit 1 with the same parseable report and counts.

GitNexus post-change detection reports the confirmed CRITICAL canonical scope:
70 indexed flows spanning discovery/audit CLI and multi-repository consumers.
The scope matches the approved design; no new service or repository boundary
was introduced.

### Shared quality, coverage, and security gates — tasks 6.1–6.5

All three repositories now have package-correct CI commands for frozen sync,
Ruff, format checking, strict mypy, pytest-cov with term-missing and JSON,
`--cov-fail-under=80`, and a deterministic zero-coverage-module check.
Docs-sync and harness gained CI workflows; the existing core workflow was
corrected from `--cov=src` to `--cov=agent_core`.

Final full-suite coverage:

| Repository | Tests | Coverage | Zero-coverage supported modules |
|---|---:|---:|---:|
| `agent-core` | full suite passed | **82.65%** | 0 |
| `agent-docs-sync` | **185 passed** | **80.06%** | 0 |
| `agent-harness` | full suite passed, 1 PostgreSQL skip | **89.21%** | 0 |

Core behavior tests cover MCP preparation, streaming approval, optional schema
migrations, embedding boundaries, Postgres memory/feedback, and stream writer
behavior. Docs-sync behavior tests cover discovery DAG handlers, state
persistence/overrides, gateway failure/fallback, observability scorers/metrics,
repository readers, and full discover/audit/validate/generate paths. Harness
success-path CLI tests and artifact-store integrity tests restored and exceeded
its 84% baseline.

Applicable Ruff security rules are enabled over production source. Core uses a
documented deterministic subset for embedded credentials and unsafe shell
execution because the broader rule family reports reviewed production
false-positives; docs-sync and harness enable the full family. Test-only
assertion/temp/subprocess exclusions are explicit. Repository tests enforce no
raw Jira/GitLab client imports and no tracked Python caches. All three security
baseline tests pass without a new dependency.

## Final non-database verification — tasks 7.1–7.3 and 7.5–7.8

The final frozen-install and repository-quality matrix passed in all three
repositories. The last coverage rerun supersedes earlier interim counts:

| Repository | Full-suite result | Coverage | Supported modules at 0% |
|---|---:|---:|---:|
| `agent-core` | 555 tests collected; passed | **82.63%** | 0 |
| `agent-docs-sync` | **187 passed** | **80.06%** | 0 |
| `agent-harness` | **212 passed, 1 PostgreSQL skip** | **89.21%** | 0 |

For each repository, `uv sync --frozen`, package-targeted Ruff, Ruff format
checking, strict mypy, the full coverage suite with the 80% hard gate, the
zero-coverage-module check, and the security baseline passed. Strict mypy
covered 94 agent-core, 45 docs-sync, and 41 harness source files.

Process-level agent-core smoke results were deterministic: config emitted valid
JSON and exited 0; health emitted valid degraded JSON and exited 1 as expected
for unavailable optional services; skills list emitted one valid JSON document
with five entries; doctor emitted one valid JSON document and the expected
non-zero diagnostic result; and a disposable generated reviewer scaffold
passed its smoke test (1/1).

Docs-sync production discovery exited 0 with 47 mapped artifacts and expanded
discovery exited 0 with 82. Informational audit exited 0 while reporting 36
actionable and 14 informational gaps. Strict audit exited 1 with the same valid
JSON findings. Check, local validation, and the disposable canonical fixture
pipeline also passed; no write-capable generation touched a production repo.

Strict OpenSpec validation passed for this change and the five affected
canonical capabilities: `agent-core-quality-gate`, `agent-docs-sync`,
`agent-framework-verification`, `agent-harness-runner`, and
`skill-scope-profiles`. The full store additionally reported 156 passing and
69 unrelated legacy failures, which remain outside this change. The canonical
`agent-docs-sync` spec was normalized to the required Purpose/Requirements
shape.

Fresh compare-to-main GitNexus detection matched the approved scope:

- agent-core: 15 symbols and 17 processes, aggregate CRITICAL;
- agent-docs-sync: 57 symbols and 70 processes, aggregate CRITICAL;
- agent-harness: 28 symbols and 26 processes, aggregate CRITICAL.

The detected scope includes the implementation plus the pre-existing dirty
files recorded in the baseline; no unexplained production boundary appeared.

Disposable rollback/re-apply verification passed: harness prior CLI 20/20 and
re-applied CLI 33/33; core prior loader 9/9 and re-applied loader 52/52;
docs-sync prior report 8/8 and re-applied report 19/19. Final repository status
contained only intended change files and the exact recorded pre-existing user
changes. No generated `coverage.json`, tracked bytecode/cache, database, or
temporary artifact remained.

The exact framework tuple remains `langgraph==1.2.9` and
`langgraph-checkpoint-postgres==3.1.0`. The database limitation recorded above
was resolved by the approved Testcontainers verification described next.

## Disposable PostgreSQL lifecycle — tasks 2.5, 3.1–3.5, and 7.4

The user explicitly approved the external test dependency and Docker-backed
disposable database execution. `agent-harness` now carries
`testcontainers[postgres]==4.15.0` in its `uv` dev dependency group; production
dependencies and persistence implementation are unchanged. The existing
untracked `agent-core/docker-entrypoint-initdb.d/20-create-harness-db.sql` and
`agent-harness/tests/test_postgres_integration.py` were inspected and preserved,
then the test was extended without touching the running agent-core database.

Provider evidence:

- Docker server: **29.6.2**.
- Pinned image: `postgres:18.4-trixie`.
- Pulled image identity:
  `postgres@sha256:8ff36f3c66371cba71d20ceedccfc3de9669a68737607888c4ef0af93abe8e39`.
- Testcontainers uses the current
  `testcontainers.community.postgres.PostgresContainer` import and a driverless
  psycopg 3 connection URL.
- An explicit `TDT_POSTGRES_TEST_URL` takes precedence and is verified against
  a second unique schema inside the disposable database; its schema is removed
  on context exit.
- Without the override, every pytest process creates a unique database, schema,
  and workflow run identity. The container context handles bounded readiness
  and cleanup. Missing Docker/backend is a hard test failure, never an
  in-memory fallback.

The shared `agent_core.sdk` async saver setup completed before graph
compilation, evidenced by all three checkpoint tables existing in the isolated
current schema. Separate operating-system processes exercised:

```text
run -> status -> approve spec -> status -> reject design to clarify
    -> status at the regenerated spec gate -> report -> history
```

The same run/thread/native interrupts survived every process boundary. Intake
and context artifact identities remained unchanged across approval and
backtrack, while the allowed clarify/spec route reran. The report remained
readable and bounded history contained the same run identity.

Real-backend negative cases covered unknown run, wrong thread, wrong stage,
wrong artifact digest, wrong native interrupt, unauthorized actor, expired
decision, and replay. The tests hash either the complete isolated checkpoint
schema or the target thread before and after every rejected operation; every
hash remained identical.

Fresh-process/idempotence runs:

- Dedicated PostgreSQL suite: **3 passed, 212 deselected in 8.29s**.
- A second fresh container/process through the final combined suite:
  **215 passed in 12.29s**.
- Earlier lifecycle iterations also passed twice (**2/2 in 17.13s** and
  **2/2 in 9.10s**) before the explicit-provider case was added.

Final harness verification:

- `uv sync --frozen`: pass, 210 packages checked.
- Ruff source/tests: pass; format check: 63 files unchanged.
- Strict mypy: pass across 41 source files.
- Full suite including PostgreSQL: **215 passed**.
- Coverage: **89.54%**, above both the 84% retained baseline and 80% hard gate.
- Supported production modules at 0%: **0**.
- GitNexus compare-to-main: the same approved aggregate CRITICAL scope,
  28 symbols and 26 processes; the Testcontainers work adds no production
  symbol or execution-flow boundary.
- Cleanup: no Testcontainers-labeled container, test database, tracked Python
  cache, repository-local coverage file, or temporary artifact remains. The
  pre-existing healthy `agent-core-local-postgres-1` container was untouched.

## Pre-archive verification remediation

The final verification found one planning-scope contradiction: the delta
security/cache requirement said "every repository" in the broader workspace
inventory while the proposal, design, tasks, and implementation intentionally
cover `agent-core`, `agent-docs-sync`, and `agent-harness`. The delta requirement
now names that exact three-repository set and explicitly defers broader
inventory enforcement to a separate change. This resolves the only CRITICAL
finding without expanding implementation scope.

Both verification suggestions were converted to regression coverage:

- JSON CLI rendering now directly exercises `checkpoint_version_mismatch`,
  `decision_expired`, `decision_replayed`, `decision_mismatch`, and
  `authorization_failed`, including the one-document stdout contract.
- Provider setup now simulates unavailable Docker with no explicit DSN and
  asserts a hard PostgreSQL test failure instead of an in-memory fallback.

The focused remediation suite passed **22/22**. The final complete harness
matrix passed frozen sync, Ruff, format, strict mypy across 41 source files,
zero-coverage enforcement, and **221/221 tests** including disposable
PostgreSQL. Coverage increased to **90.44%**. GitNexus remains at the approved
aggregate CRITICAL scope of 28 symbols and 26 processes; the remediation adds
test coverage only and no production execution-flow boundary. Cleanup again
left no Testcontainers resource, tracked cache, or repository-local coverage
artifact.
