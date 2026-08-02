## MODIFIED Requirements

### Requirement: Non-destructive configuration and MCP verification

The integration SHALL preserve existing Agentmemory lifecycle hooks,
hand-authored guidance, and unrelated configuration. GitNexus and Graphify
setup SHALL modify only their marked entries, and the bootstrap SHALL verify
the resulting MCP command, repository registry, skill paths, hook ownership,
and orchestration health evidence before declaring setup successful. Every
external CLI and MCP probe MUST have a process-level deadline so a blocked
database or FileProvider read cannot hang the diagnostic.

#### Scenario: Existing Agentmemory hooks are present

- **WHEN** Codex or Claude configuration already contains Agentmemory hooks
- **THEN** setup leaves those entries semantically unchanged and adds only
  tool-owned entries at the intended scope, recording the preserved hashes

#### Scenario: GitNexus stable Codex setup is inspected

- **WHEN** the selected GitNexus stable setup completes
- **THEN** the diagnostic expects MCP and standard skills only, does not claim
  unsupported host hooks, and records the live MCP probe state separately

#### Scenario: MCP is live or degraded

- **WHEN** the developer starts the configured GitNexus or Graphify MCP server
  and probes repository resources
- **THEN** the report either records successful repository discovery and context
  evidence or records a bounded degraded/unavailable result with remediation
  and never claims availability from configuration alone

#### Scenario: A knowledge probe exceeds its deadline

- **WHEN** GitNexus, Graphify, or a configured MCP command does not return
  before the probe deadline
- **THEN** the diagnostic terminates the probe, records a timeout and duration,
  and preserves the remaining independent results

#### Scenario: Tool-owned integration is removed

- **WHEN** a separately reviewed native-tool uninstall path is explicitly
  selected and confirmed
- **THEN** its upstream preview and ownership checks govern removal while the
  orchestration rollback remains uninvolved and Agentmemory entries,
  hand-authored guidance, unrelated tools, and application state remain

### Requirement: Observable diagnostics and scoped rollback

The integration SHALL expose redacted status evidence for tool versions,
repository scope, index freshness, hook registration, MCP reachability,
orchestration health, skipped operations, and failure reasons. Orchestration
rollback SHALL be repository-local, pointer-only, and SHALL preserve native
tool state, application code, Agentmemory hooks, hand-authored guidance,
indexes, and dirty worktree changes. Any native-tool uninstall SHALL remain a
separate explicitly reviewed operation scoped by that tool's ownership model.

#### Scenario: Workspace status is checked

- **WHEN** a developer runs the knowledge status command from the workspace
  root
- **THEN** it reports both Git roots independently, each index's freshness,
  Graphify hook state, MCP registration, group state, and the orchestration
  health evidence status

#### Scenario: Refresh fails on a FileProvider-backed path

- **WHEN** a requested refresh encounters a stale file handle, lock conflict,
  or parser error
- **THEN** it exits non-zero for that requested refresh, emits a bounded
  redacted reason, leaves the previous usable index intact where supported,
  and identifies the compatibility decision or local-mirror remediation

#### Scenario: Rollback is previewed

- **WHEN** a developer requests rollback
- **THEN** only orchestration-owned latest-evidence pointers are listed for
  removal, preserved native-tool and Agentmemory/guidance state is listed, and
  separate uninstall workflows are named without being invoked

#### Scenario: Integration is rolled back

- **WHEN** the pointer-only preview is confirmed and the developer applies
  orchestration rollback
- **THEN** only the latest-evidence pointers are removed, with no mutation of
  GitNexus/Graphify state, Go modules, production manifests, Agentmemory hooks,
  memories, or unrelated `mcp-router/` files

## ADDED Requirements

### Requirement: FileProvider compatibility and graph integrity gate

Before rebuilding a knowledge index on a FileProvider-backed workspace, the
integration SHALL run a non-destructive compatibility gate covering file
hydration/readability, tool-supported state-location behavior, concurrent
reader/writer ownership, output preservation, and rebuild rollback. It MUST
select only a supported in-place state path or a documented local mirror; it
MUST NOT delete an unreadable index as an implicit repair.

#### Scenario: In-place index state is supported

- **WHEN** the compatibility gate proves stable reads, writes, locking, and
  recovery for the selected tool on the workspace filesystem
- **THEN** the integration may retain in-place state and records the exact
  evidence and source identity

#### Scenario: Alternate state location is unsupported

- **WHEN** current upstream documentation and CLI behavior do not provide a
  supported alternate index path
- **THEN** the integration uses the documented local-mirror strategy or remains
  not-ready and does not invent an unsupported relocation flag or symlink

#### Scenario: Graphify incremental update is verified

- **WHEN** a Graphify graph is incrementally updated
- **THEN** deleted sources are pruned, changed sources replace stale nodes,
  edge direction and root-relative source paths are preserved, and the
  read-only graph diagnostic reports dangling, missing, collapsed, and
  self-loop edge counts

#### Scenario: Graph integrity is degraded

- **WHEN** the graph diagnostic reports structural warnings or the output
  shrinks unexpectedly without explicit authorization
- **THEN** the implementation profile is not-ready, the prior usable graph is
  retained where supported, and the report identifies the integrity reason

#### Scenario: GitNexus index does not match source state

- **WHEN** the indexed commit or dirty-state fingerprint does not match the
  probed repository source identity
- **THEN** GitNexus freshness is degraded or unavailable and its query results
  cannot satisfy implementation-readiness evidence
