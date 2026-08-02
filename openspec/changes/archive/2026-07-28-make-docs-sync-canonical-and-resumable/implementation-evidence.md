# Implementation evidence

## Canonical boundary

- The verified editable `agent-core` is installed through the frozen workspace
  dependency and its full consumer suite passes.
- `ExecutionPlan` is immutable and records every canonical mode's non-secret
  effective options. Public CLI modes compile plans; the removed local-link
  compatibility switch is no longer advertised.
- Repository-root `config.yaml` is a strict, extra-forbidden root schema.
  Legacy/unknown fields fail with redacted migration guidance before gateway or
  write construction. Explicit `DOCS_SYNC_*` overrides are centralized.
- Dry-run update skips gateway and generation-agent construction. Check,
  discover, audit, and validation are deterministic read-only paths.
- Normal generation defaults to `docs/` only. Traversal, symlink escape, Python
  source, and `openspec/specs/` targets are rejected by containment tests.

## Restart safety and writes

- Upstream `StepPersistence(SqliteStepStore(...))` is preflighted at
  `$TDT_HOME/state/agent-docs-sync/steps.sqlite3`; failure is fatal without a
  memory substitute.
- The consumer-owned SQLite approval index stores run/request/repository/path/
  operation/content-digest/expiry identity without prompts or generated bodies.
  Inspection and decisions require a configured actor; decisions are single-use.
- `resume` validates approved status, actor, repository, and current path
  containment, reconstructs the generation agent with the same step store and
  write ledger, then calls the public `BaseAgent.resume()` continuation API
  with the original run ID and native tool-call approval identity.
- The write ledger has additive schema setup and stores run, continuation, path,
  operation, and digest identity. Atomic replacement plus in-progress digest
  reconciliation makes repeated delivery at-most-once.
- Full and incremental paths rediscover documentation after successful writes;
  reports separate execution, compliance, approval, and write status.

## Convergence and rollback

- Caller census found the placeholder `generate_updates` and independent
  discovery builder had test callers only. Both now fail with actionable
  migration guidance to `run_canonical_pipeline`; no public CLI reaches them.
- `generation_enabled` and `resume_enabled` provide a rollback switch while
  leaving check/discover/audit and both SQLite databases intact.

## Verification

- GitNexus refreshed impacts: canonical pipeline CRITICAL (eight public paths),
  config MEDIUM, write tool LOW. Post-change detection reports the expected
  canonical CLI/process fan-out; manual diff review found no unrelated runtime
  path.
- `uv sync --frozen`, Ruff check/format, and strict mypy over source/tests pass.
- 213 tests pass with 80.28% coverage, including CLI subprocess/help, separate-
  process decision, unavailable-store, authority, replay, reconciliation, and
  end-to-end lifecycle fixtures.
- The suite is clean of consumer-owned file-handle leaks. Two remaining
  `ResourceWarning`s report unclosed SQLite connections from the upstream
  Pydantic AI Harness lifecycle under two order-dependent tests; each warning
  disappears when isolated, and no docs-sync connection remains open after its
  owned stores are closed. This is recorded as an upstream follow-up rather
  than suppressed in tests.
- Full-history Gitleaks scan reports no leaks.
