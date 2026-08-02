## 1. Dependency and CRITICAL-Root Characterization

- [x] 1.1 Confirm harden-agent-core-consumer-contract is complete and install its verified core version into agent-docs-sync.
- [x] 1.2 Refresh the docs-sync GitNexus index and rerun upstream impact for run_canonical_pipeline, DocsSyncConfig, and WriteDocTool; list all affected CLI/process paths and obtain confirmation before editing the CRITICAL pipeline root.
- [x] 1.3 Add characterization and negative-path fixtures for every public CLI mode, ignored option, config location, dry-run mutation attempt, approval interruption, and legacy pipeline entry point.

## 2. Canonical Configuration and Command Plan

- [x] 2.1 Replace the current section-only loader in src/agent_docs_sync/config.py with one strict repository-root schema plus centralized TDT environment overrides and redacted migration errors.
- [x] 2.2 Migrate agent-docs-sync/config.yaml to the canonical non-secret schema and add unknown/legacy-key rejection tests.
- [x] 2.3 Introduce an immutable execution-plan model covering mode, repository, base ref, discovery boundary, LLM policy, durability, authority, and output policy.
- [x] 2.4 Refactor src/agent_docs_sync/cli.py so every advertised option populates the plan or is removed with tested migration guidance.

## 3. Least-Privilege Pipeline Composition

- [x] 3.1 Characterize run_canonical_pipeline, then incrementally consume the typed plan without changing deterministic stage results.
- [x] 3.2 Split read-only and generation composition so dry-run/check/discover/audit cannot construct WriteDocTool, SyncSpecTool, or mutation equivalents.
- [x] 3.3 Restrict generation writes to normalized documentation roots and add traversal, symlink, Python-source, and openspec/specs/ denial tests.
- [x] 3.4 Remove the harness-style sentinel workaround by using the completed core explicit-empty deny-all contract.

## 4. Persistent Approval Lifecycle

- [x] 4.1 Compose upstream StepPersistence with SqliteStepStore at the documented TDT state path and fail preflight when durable storage cannot open.
- [x] 4.2 Add a separate consumer SQLite lifecycle/write ledger with additive schema setup, unique decision constraints, operation keys, and source/request identity fields.
- [x] 4.3 Implement authenticated pending/list inspection without exposing prompts, credentials, or full generated bodies.
- [x] 4.4 Implement approve/deny/resume commands that reconstruct the same agent/store after process restart, validate actor/request/expiry/path/content identity, and call the public upstream continuation API.
- [x] 4.5 Add separate-process tests for approval, denial, unauthorized actor, expiry, replay, mismatched repository, and unavailable store.

## 5. Exactly-Once Writes and Truthful Results

- [x] 5.1 Add transactional operation claiming and atomic file replacement keyed by run, continuation/tool call, path, operation, and content digest.
- [x] 5.2 Add crash/replay/conflict tests proving an approved mutation applies at most once and partial ledger/file states are reconciled safely.
- [x] 5.3 Rediscover repository files and mappings after every successful mutation before validation.
- [x] 5.4 Separate execution, compliance, approval, and write status in JSON/text reports and retain only the documented compatibility alias.
- [x] 5.5 Unify discovery mapping field names and persist canonical mapping/memory state through production execution.

## 6. Legacy Convergence and Verification

- [x] 6.1 Delegate or remove duplicate discovery/generation/memory/builder paths only after import, CLI, GitNexus, and Graphify caller census shows no independent production behavior.
- [x] 6.2 Add an end-to-end fixture for discover, approval interruption, process exit, authorized resume, one write, rediscovery, validation, and report.
- [x] 6.3 Run frozen Ruff, format, strict source-plus-test mypy, full pytest/coverage, secret scan, and all CLI subprocess tests in agent-docs-sync.
- [x] 6.4 Run fresh GitNexus change detection and verify CRITICAL-root impact is limited to intended canonical CLI/process paths.
- [x] 6.5 Exercise rollback by disabling generation/resume while preserving deterministic audit and both SQLite databases for inspection/recovery.
- [x] 6.6 Validate make-docs-sync-canonical-and-resumable with strict OpenSpec validation.
