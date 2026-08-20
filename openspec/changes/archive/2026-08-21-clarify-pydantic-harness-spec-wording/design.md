## Context

The archived `clarify-pydantic-ai-harness-evidence` correction aligned most
requirement blocks, but the current `agent-compaction` header still says that
configuration fields are not read by `AgentRuntime` without explaining the
typed projection helper, and `agent-core-capabilities` still contains a
`Purpose: TBD` placeholder. The current vendor contract already describes
public SDK forwarding and internal adapter isolation; this correction keeps
that boundary explicit while preserving its scenario labels and the unrelated
requirements in the same spec.

## Goals / Non-Goals

**Goals:**

- Update the three existing capability contracts through one CLI-managed,
  spec-driven correction.
- State that `AgentConfig.runtime_options()` is a typed projection used by
  supported public construction, not an automatic `AgentRuntime` configuration
  reader.
- Name `compaction_enabled=false` and enumerate it among supported public
  runtime options while keeping private aliases/configuration keys separate.
- Keep vendor wording consistent with intentional public SDK forwarding and
  internal adapter isolation.
- Preserve all existing scenario labels, dated archives, active changes, and
  untracked reports.

**Non-Goals:**

- No product source, dependency, lockfile, provider, network, credential,
  deployment, or live-runtime changes.
- No edits to any existing dated archive, including the prior pydantic-ai
  harness corrections.
- No claims of live-provider acceptance or execution-level compaction evidence.
- No mutation of unrelated active changes or the `reports/` directory.

## Decisions

### 1. Use complete modified requirement blocks

Each delta copies every requirement block being modified from the current main
spec and preserves its exact scenario labels. The archive command therefore
updates only the three named contracts while retaining all other requirements.

### 2. Treat projection and construction as distinct boundaries

The public `BaseAgent`/`build_agent` path owns supported typed runtime options,
including `compaction_enabled`. `AgentConfig.runtime_options()` can project
those typed values for that path, but the historical documentation must not
imply that constructing `AgentRuntime` automatically reopens or reads config
fields. Private aliases remain migration-only and are not public API.

### 3. Keep vendor forwarding intentional and adapters isolated

Public SDK facades may intentionally forward upstream runtime types when the
public contract requires identity preservation. Internal modules continue to
use the designated adapter boundary, and focused checks must detect
undocumented internal bypasses without reinstating a blanket prohibition that
would reject the documented SDK facade.

### 4. Archive through the registered store

Use the store-aware `openspec new change`, `status`, `instructions`, strict
validation, and `archive` commands. Inspect the post-archive main specs,
archive paths, and status before writing the requested report or staging files.

## Risks / Trade-offs

- [Risk] A delta could drop a scenario label or unrelated requirement. -> Copy
  complete modified blocks and compare labels before and after archive.
- [Risk] Purpose-level prose is outside requirement-block delta operations. ->
  Verify the archived result explicitly and report any CLI limitation before
  making any out-of-band change.
- [Risk] Focused documentation evidence could be mistaken for runtime proof. ->
  Keep live-provider and live-compaction acceptance explicitly out of scope.
- [Risk] Archive could include unrelated working-tree changes. -> Capture raw
  status before and after, and stage only the requested correction/archive/main
  spec paths and report.

## Migration Plan

1. Author the proposal, three deltas, design, and checked task list in the
   CLI-created change root.
2. Run change-scoped and all-store strict OpenSpec validation before archive.
3. Archive with `openspec archive clarify-pydantic-harness-spec-wording --yes
   --store openspec-store`.
4. Run strict validation again, verify only the three targeted contracts and
   the new dated archive changed, and write the SDD report.
5. Commit only the CLI-created correction/archive/main-spec paths and report.

Rollback is a repository-level revert of the correction commit after review;
do not remove or rewrite any historical archive.

## Open Questions

None.
