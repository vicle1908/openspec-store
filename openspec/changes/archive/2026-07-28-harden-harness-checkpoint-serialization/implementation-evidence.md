# Implementation Evidence

Recorded: 2026-07-28 (Asia/Ho_Chi_Minh)

## Live reproduction and compatibility

- Backend: disposable local PostgreSQL database `agent_harness` in container `agent-core-local-postgres-1`, host endpoint `127.0.0.1:54329`.
- Framework tuple: `langgraph==1.2.9`, `langgraph-checkpoint-postgres==3.1.0`.
- Live ticket/run: `TDT-LIVE-E2E-20260728` / `run-5991c2bcc8ad`.
- Before the fix, a fresh permissive `agent-harness status --json` emitted six unregistered-type warnings for `Stage`, `ValidationStatus`, `DraftSpec`, `TicketArtifact`, `ClarifyArtifact`, and `ContextArtifact`.
- After the fix, fresh permissive and `LANGGRAPH_STRICT_MSGPACK=true` status processes both exited 0, emitted valid JSON, and emitted no unregistered-type warnings.
- The pre-fix checkpoint remained readable without rewriting it. Native state still has one interrupt at `post_spec_gate`: interrupt `e436717c103a1e1eedf909e1ffe096ad`, decision `gate-02f763cc4252170754738d9f`, artifact digest `e847a87787711510`, expiry `2026-07-28T21:50:01.417543Z`.
- No approve or reject command was submitted to the live run.

## Impact and scope

- Pre-edit GitNexus impact: `create_async_checkpointer` LOW, zero indexed upstream callers or affected processes.
- Pre-edit GitNexus impact: `WorkflowRunner` LOW, one importing file and no affected process.
- `WorkflowRunner._get_graph` was not modified.
- Final GitNexus worktree detection reports CRITICAL aggregate risk because the repositories already contain unrelated skill, CLI, docs, and lifecycle changes. Per-file review isolates this change to the shared async factory and test, the new harness checkpointing module/tests, the runner import binding, and strict PostgreSQL assertions in the pre-existing untracked integration test.

## Verification matrix

| Repository | Frozen sync | Ruff / format | Strict mypy | Full tests | Coverage | Zero-coverage gate |
|---|---|---|---|---:|---:|---|
| `agent-core` | pass | pass | pass, 94 files | 556 passed | 83% | pass |
| `agent-docs-sync` | pass | pass | pass, 45 files | 187 passed | 80% | pass |
| `agent-harness` | pass | pass | pass, 42 files | 228 passed | 90% | pass |

Focused evidence:

- `agent-core`: checkpointer factory tests 3/3.
- `agent-harness`: checkpoint policy now derives the reachable constructor set from `HarnessState` plus its typed evidence union, matches all 33 exact allowlist entries, round-trips all 33 under the strict serializer, and proves an untrusted custom model is not reconstructed.
- `agent-harness`: complete real PostgreSQL integration file under `LANGGRAPH_STRICT_MSGPACK=true` 6/6.
- The real lifecycle test runs run/status/type inspection/approve/reject/report across separate processes, repeats status in permissive mode, checks stderr, and verifies checkpoint continuity.
- A no-gate strict lifecycle completes and reopens all twelve stage artifacts in a fresh process with exact artifact, `Stage`, and `ValidationStatus` runtime types.
- A synthetic checkpoint written by the shared factory without an allowlist is reopened and approved by new strict CLI processes; intake, context, clarify, and spec artifact identities prove completed stages did not replay.
- Strict OpenSpec validation passed for this change and canonical `agent-harness-runner` and `agent-framework-verification` capabilities.

## Operational CLI observations

- `agent-core config --json` succeeded with secrets redacted.
- `agent-core health --json` returned the expected degraded exit because gateway and PostgreSQL are not configured in the default local profile.
- `agent-core skills doctor --json` returned a valid diagnostic document and non-zero exit for external catalog/profile state: three missing explicitly included skills, six invalid skill frontmatter files, and one duplicate `openspec-update-change` definition.
- `agent-docs-sync check`, production `discover`, and `validate` exited 0 without source writes.
- `agent-docs-sync audit --strict` executed successfully but returned its specified non-compliance exit: 36 actionable documentation gaps and 8 Diátaxis violations. This is audit output, not an execution failure.

## Reproducible source identity

### agent-core

- HEAD: `3aff416eca0801ea3a1804892bc5700aac71ebf5`
- Tracked binary diff SHA-256: `71f4e982875838d63ff5c97288a3f1e4cd5b59fe71993069b85b0938951e97d6`
- Untracked inventory: `docker-entrypoint-initdb.d/20-create-harness-db.sql`, `scripts/check_zero_coverage.py`, `src/agent_core/skill_system/candidates.py`, `tests/skill_system/test_diagnostics.py`, `tests/test_security_baseline.py`, `tests/test_supported_zero_coverage_modules.py`.

### agent-docs-sync

- HEAD: `47e37e9a7c055e4db82e391b956a14f6d651d1b1`
- Tracked binary diff SHA-256: `e6da317cf049e181b335b94ce026392d8cec96d351479d4e8164268fa543ff83`
- Untracked inventory: `.github/workflows/ci.yml`, `scripts/check_zero_coverage.py`, `src/agent_docs_sync/source_scope.py`, `tests/test_cli_audit_strict.py`, `tests/test_security_baseline.py`, `tests/test_source_scope.py`, `tests/test_supported_feature_paths.py`.

### agent-harness

- HEAD: `7cb90e66cb8886401b2f0875927a87b06a1d9c23`
- Tracked binary diff SHA-256: `7aae44a07bf1032705c5bd060d8d2f0e58a80f84d1f35d8a06150417b805b95e`
- Untracked inventory: `.github/workflows/ci.yml`, `scripts/check_zero_coverage.py`, `src/agent_harness/checkpointing.py`, `tests/test_artifact_store.py`, `tests/test_checkpointing.py`, `tests/test_cli_lifecycle.py`, `tests/test_dependency_baseline.py`, `tests/test_postgres_integration.py`, `tests/test_security_baseline.py`.

## Rollback

Rollback is source-only: revert the optional serializer parameter/test in `agent-core`, revert the runner import, and remove the harness checkpointing module/tests. There is no PostgreSQL migration, checkpoint rewrite, dependency change, or runtime configuration migration to undo. Existing checkpoint bytes remain compatible with both sides of the change.
