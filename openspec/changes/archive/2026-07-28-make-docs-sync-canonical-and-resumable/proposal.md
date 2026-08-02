## Why

`agent-docs-sync` has a useful deterministic auditor, but its generation path accepts configuration it does not load, exposes CLI options it ignores, can retain write authority during dry-run, and loses approval continuations across process restart. These gaps make the claimed canonical write pipeline unsafe and operationally incomplete.

## What Changes

- Establish one repository-root configuration schema and reject or migrate unsupported legacy sections and unknown keys.
- Make every public CLI option affect the canonical pipeline or remove it with actionable migration guidance.
- Enforce dry-run by constructing a read-only composition with no write-capable tools.
- Restrict normal writes to configured documentation roots; source and OpenSpec promotion remain separate explicit-authority operations.
- Compose upstream SQLite-backed step persistence beneath `$TDT_HOME/state/agent-docs-sync/` and add pending/list/approve/deny/resume CLI lifecycle operations.
- Add an idempotent write ledger keyed by continuation/tool call, normalized path, operation, and content digest.
- Rediscover generated files before validation and report execution, compliance, approval, and write outcomes separately.
- Unify discovery mapping fields and persistence, then remove or delegate duplicate pipeline, builder, memory, and placeholder generation paths.
- **BREAKING**: Ignored compatibility flags and legacy configuration keys will no longer be silently accepted; unsupported forms will fail with migration guidance.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `agent-docs-sync`: Extend the canonical pipeline contract with truthful configuration and CLI behavior, zero-authority dry-run, durable approval/resume, idempotent writes, rediscovery, and production-path convergence.

## Non-Goals

- Allowing general Python source edits from normal docs-sync operation.
- Building another workflow checkpoint abstraction or conflating step persistence with LangGraph checkpoints.
- Making LLM generation mandatory for deterministic discovery or audit.
- Rewriting documentation content outside an approved continuation.

## Impact

- Repository: `agent-docs-sync`; dependency on the clarified `agent-core` consumer contract.
- Primary modules: configuration, CLI, canonical pipeline, generation composition, path policy, approval projection, validation/reporting, and persistent state.
- GitNexus rates `run_canonical_pipeline` CRITICAL: 10 impacted symbols across 8 CLI/process paths (`check`, `discover`, `update`, `sync`, `audit`, validation, multi-repo, and sync-all). `DocsSyncConfig` is MEDIUM with 10 impacted symbols; `WriteDocTool` is LOW.
- CRITICAL-root implementation must be incremental behind characterization and negative-path tests, with post-change detection.
- No new dependency is expected if the installed upstream SQLite store is used; any additional package requires approval.
- Mobile applications are unaffected.
