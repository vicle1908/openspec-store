## 1. Characterization and impact gates

- [x] 1.1 Record the current live `status --json` output, permissive unregistered-type stderr warnings, strict-mode fallback behavior, run identity, PostgreSQL provider, and dirty source identity without deciding the pending gate.
- [x] 1.2 Run fresh GitNexus upstream impact analysis for every existing `agent-core` and `agent-harness` symbol selected for modification; stop for confirmation if any selected symbol is HIGH or CRITICAL.
- [x] 1.3 Add a failing `agent-core` unit test proving the async checkpointer factory must build and forward a serializer with an exact consumer allowlist while preserving setup and resource lifetime.
- [x] 1.4 Add a failing `agent-harness` real-PostgreSQL process-boundary test proving typed artifact reconstruction and rejecting permissive unregistered-type stderr warnings.

## 2. Shared and consumer implementation

- [x] 2.1 Update `agent-core/src/agent_core/orchestration/graph.py` so `create_async_checkpointer` accepts an optional exact MessagePack allowlist and forwards a configured `JsonPlusSerializer` through LangGraph's public saver factory before setup.
- [x] 2.2 Define an explicit trusted checkpoint type allowlist in `agent-harness` covering every custom enum and Pydantic model reachable from `HarnessState`, with focused completeness and no-wildcard tests.
- [x] 2.3 Pass the same allowlist to every durable `create_async_checkpointer` call used by run, stream, status, history, approve/reject resume, and report behavior.
- [x] 2.4 Keep stable CLI errors, JSON/stdout isolation, gate authorization, checkpoint schema, and non-durable behavior unchanged.

## 3. Focused verification

- [x] 3.1 Run `uv run ruff check` and `uv run ruff format --check` for changed files in `agent-core` and `agent-harness`.
- [x] 3.2 Run strict mypy and focused unit/contract suites for the shared factory and durable runner boundary.
- [x] 3.3 Run the required real PostgreSQL lifecycle suite with `LANGGRAPH_STRICT_MSGPACK=true`, proving cross-process run/status/decision/report behavior and zero unregistered-type warnings.
- [x] 3.4 Re-poll live run `run-5991c2bcc8ad` with strict mode using its disposable local PostgreSQL backend, verify compatibility, and leave the pending human gate unchanged unless the user explicitly decides it.

## 4. Three-repository regression and closure evidence

- [x] 4.1 Run frozen sync, format, lint, strict typing, full tests, coverage, security, zero-coverage, CLI, and major-feature checks for `agent-core`, `agent-docs-sync`, and `agent-harness`.
- [x] 4.2 Run strict OpenSpec validation for `harden-harness-checkpoint-serialization` and affected canonical capabilities.
- [x] 4.3 Run GitNexus change detection in each modified repository and confirm only intended checkpoint composition symbols and processes changed.
- [x] 4.4 Record reproducible evidence including repository HEADs, tracked diff hashes, untracked inventories, dependency tuple, strict environment, backend identity, commands, results, warnings, and any unavailable checks.
- [x] 4.5 Document rollback as source reversion only, with no database migration or checkpoint rewrite required, and prepare the change for verification/archive.

## 5. Verification warning closure

- [x] 5.1 Replace self-referential allowlist coverage with state-contract-derived discovery and exhaustive strict serializer round trips for every reachable custom model and enum.
- [x] 5.2 Add a strict real-PostgreSQL process test that completes and reopens all twelve stage artifacts and rejects compatibility warnings in strict and permissive readers.
- [x] 5.3 Add a synthetic pre-allowlist checkpoint fixture written by the legacy shared factory, then resume it in a strict new CLI process without replaying completed stages.
- [x] 5.4 Correct stale design wording, rerun focused/full verification and scope detection, and refresh implementation evidence for warning closure.
