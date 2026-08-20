## Context

The prior correction archived the broad pydantic-ai harness contract, but its `vendor-isolation` purpose still describes all imports as confined to `_ai/`, its capability language does not sharply separate public runtime parameters from private compatibility/config aliases, and compaction describes an unnamed disablement. The current consumer environments resolve `pydantic-ai` 2.32.0 and `pydantic-ai-harness` 0.23.0; the supplied implementation identities are agent-core `1de06ca`, `2a560dd`, `03f5a3c`, agent-harness `25f1dd1`, and agent-docs-sync `9c78670`, `4eff50c`.

## Goals / Non-Goals

**Goals:**

- Update the three existing capability contracts through a second CLI-managed correction.
- Make intentional public SDK forwarding and internal adapter isolation the vendor purpose.
- List supported public runtime options and identify private legacy/config aliases as non-public.
- Make `compaction_enabled=false` the named explicit disablement while preserving every existing compaction scenario label.
- Preserve exact provenance, versions, test commands, archive paths, and evidence limitations.

**Non-Goals:**

- No product-code, lockfile, dependency, provider, network, credential, deployment, or live-runtime changes.
- No edits to any existing dated archive, including `2026-08-21-reconcile-pydantic-ai-harness-capability-contract`.
- No claim that deterministic compaction tests prove live compaction behavior, provider acceptance, external-network behavior, or clean-install readiness.
- No mutation of the active `establish-agent-observability-contract` or `align-jti-skill-runtime-contract` changes.

## Decisions

### 1. Use complete modified requirement blocks

The delta copies every requirement block being modified from the current main
specs and preserves all existing scenario labels. This lets the archive
operation merge the correction without dropping prior scenarios or touching
historical archives.

### 2. Treat public and private names as separate contract layers

The supported public boundary is the SDK `BaseAgent`/`build_agent` path and its
typed/runtime options: `target_tokens`, `spend_limit_per_run_usd`,
`spend_limit_per_day_usd`, `enable_planning`, `advisor_model`,
`advisor_max_uses`, and caller-supplied capabilities/authority policy. Legacy
aliases and configuration keys remain migration-only implementation details;
they are not public consumer construction inputs and cannot widen the runtime
contract.

### 3. Name the only supported explicit compaction disablement

Omission continues to receive the documented runtime default. A caller that
needs no compaction must supply `compaction_enabled=false`; a vague
"supported disablement" phrase is insufficient evidence. This correction
records deterministic below-target/above-target and forwarding evidence only.

### 4. Record provenance without converting it into acceptance

The evidence record includes resolved package versions, implementation SHAs,
the exact new harness-forwarding test command and result, strict OpenSpec
validation, and the expected/final archive paths. Version and test results are
reproducible local evidence; they do not imply provider calls, live compaction,
network acceptance, or clean-install parity.

## Risks / Trade-offs

- [Risk] A delta can accidentally remove a retained scenario label. -> Copy complete requirement blocks and validate strict before archive.
- [Risk] Main-spec purpose may remain stale if the archive merge ignores a purpose correction. -> Include the corrected purpose in the vendor delta, verify the post-archive main spec, and stop before commit if it is not applied.
- [Risk] Focused tests can be mistaken for integrated acceptance. -> State exact scope and non-live limitations in both tasks and the evidence report.
- [Risk] CLI sync could include unrelated changes. -> Capture the pre-edit status, inspect changed paths after archive, and stage only CLI-created correction/spec/archive paths plus the requested report.

## Migration Plan

1. Create this change with `openspec new change` in the registered store and author the proposal, three deltas, design, and all-checked tasks.
2. Run strict change validation and archive-readiness validation.
3. Archive with `openspec archive clarify-pydantic-ai-harness-evidence --yes --store openspec-store`, allowing the CLI to sync only the three declared main specs and move the change to `openspec/changes/archive/2026-08-21-clarify-pydantic-ai-harness-evidence/`.
4. Re-run strict validation, inspect the main-spec purpose/requirements, verify archive paths and status, and write the final report.
5. Commit only the CLI-created correction/spec/archive files and the requested report; leave `reports/` and unrelated active changes untouched.

Rollback is a repository-level revert of the correction commit after review;
do not hand-edit or remove existing archives as rollback.

## Open Questions

None. Live-provider and live-compaction evidence are intentionally outside this correction.
