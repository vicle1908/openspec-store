## ADDED Requirements

### Requirement: Stable skills and CLI contract

The repository SHALL use the official agent skills as guidance and the pinned
official CLIs as the source of truth for setup, indexing, querying, status, and
rollback. The selected stable versions SHALL be GitNexus `1.6.9` and Graphify
package `graphifyy` `0.9.26`; prerelease versions MUST NOT be selected
implicitly.

#### Scenario: Pinned tools are diagnosed

- **WHEN** a developer runs the knowledge-tool diagnostic
- **THEN** it reports the exact GitNexus and Graphify versions, Node/Python
  prerequisites, and the recorded license decision

#### Scenario: Upstream has a newer stable or prerelease

- **WHEN** the update check finds a newer npm or PyPI release
- **THEN** it reports the candidate and keeps the selected pins unchanged until
  license, CLI-help, hook, and focused end-to-end checks are approved

#### Scenario: The workstation has the old Graphify tool

- **WHEN** the diagnostic finds Graphify `0.6.7` or another version
- **THEN** it reports the mismatch and the bootstrap offers the pinned managed
  Python 3.12 `graphifyy[all,postgres]==0.9.26` path without changing
  application dependencies

#### Scenario: Optional tooling is absent

- **WHEN** a developer runs ordinary repository verification without either
  optional tool
- **THEN** application verification remains usable and the knowledge
  diagnostic emits a bounded actionable warning

#### Scenario: GitNexus license approval is absent

- **WHEN** GitNexus is installed but no approved PolyForm Noncommercial decision
  is recorded
- **THEN** mandatory setup is refused, the blocker is named, and existing agent
  configuration remains unchanged

### Requirement: Graphify extraction coverage and warning policy

Graphify refreshes SHALL use `graphifyy[all,postgres]==0.9.26` in an isolated
Python 3.12 environment and SHALL disable HTML visualization for graphs over the
configured visualization threshold while retaining machine-readable graph
output. Refresh diagnostics SHALL classify expected unsupported, sensitive,
and allowlisted zero-node inputs separately from actionable parser, runtime,
or unknown-source coverage failures.

#### Scenario: SQL source coverage is enabled

- **WHEN** the pinned Graphify environment is bootstrapped and refreshed
- **THEN** the SQL parser and every dependency supplied by the `all` and
  `postgres` extras are installed at the same `0.9.26` pin and SQL files are
  not skipped solely because `tree_sitter_sql` is unavailable

#### Scenario: The graph exceeds the HTML visualization threshold

- **WHEN** a refresh produces more nodes than the configured visualization
  limit
- **THEN** Graphify runs with visualization disabled, preserves `graph.json` and
  the textual report, and emits no fatal visualization warning

#### Scenario: Expected files are excluded

- **WHEN** Graphify encounters sensitive files, unsupported extensions, or
  allowlisted configuration/data files that produce zero nodes
- **THEN** the diagnostic records a bounded classified exclusion without
  treating it as a refresh failure

#### Scenario: Unknown source coverage fails

- **WHEN** a supported source file produces zero nodes and is not allowlisted,
  or the SQL parser extra cannot be installed at the pinned version
- **THEN** the refresh exits non-zero with a redacted actionable reason and
  preserves the last usable graph where the upstream tool permits it

### Requirement: Feature-complete local graph capabilities

The integration SHALL install, expose, and verify the complete feature set
supported by the pinned tools. GitNexus SHALL support embeddings, PDG-backed
control/data and taint queries, generated repository skills, structural checks,
route/API analysis, branch-aware indexes, local HTTP UI/MCP, wiki generation,
and repository-group contract synchronization. Graphify SHALL support deep and
directed extraction, incremental/watch workflows, all pinned optional extras,
local exports, per-root MCP stdio access, global graph management, query
feedback/reflection, and supported local ingestion sources.

#### Scenario: GitNexus full local analysis is enabled

- **WHEN** a repository is refreshed in the full local profile
- **THEN** GitNexus bootstraps a missing vector layer within the reviewed
  100,000-node full-local cap and preserves a usable existing vector layer
  during later incremental refreshes,
  reports embedded symbols for non-empty supported roots, returns a usable PDG
  result rather than a missing-layer response for supported languages, runs
  structural checks, and exposes the resulting capabilities through its CLI
  and MCP tools

#### Scenario: GitNexus repository-group capabilities are enabled

- **WHEN** both Git roots are indexed and the workspace group is synchronized
- **THEN** group status, contract links, cross-repository query, and impact
  operations are available without collapsing the independent local indexes

#### Scenario: Graphify full local pipeline is enabled

- **WHEN** a repository is refreshed in the full local profile
- **THEN** Graphify's code-only commit refresh remains deterministic while its
  explicit semantic command supports deep and directed extraction, incremental
  updates, cluster workflows, local query/path/explain, global-graph updates,
  save-result/reflect feedback, and configured local exports

#### Scenario: Graphify MCP and export capabilities are enabled

- **WHEN** the corresponding local feature profile is selected
- **THEN** Graphify provides separately named MCP stdio servers for the outer
  and nested graphs and can generate HTML/no-viz, SVG, GraphML, wiki, Obsidian,
  Neo4j, and FalkorDB artifacts plus MCP pull-request triage output without
  placing generated state under version control

#### Scenario: Watch mode coordinates with Git hooks

- **WHEN** interactive Graphify watch mode owns refresh for a Git root
- **THEN** the post-commit and post-checkout paths do not start a competing
  rebuild, and stopping watch restores the documented hook-owned mode

#### Scenario: Credentialed or networked features are selected

- **WHEN** a developer requests LLM, HTTP, database, workspace-connector,
  remote-push, or publishing features
- **THEN** setup requires an explicit profile, validates endpoint/credential
  presence, binds HTTP services to loopback by default, redacts secrets, and
  refuses public publishing or non-loopback exposure without an explicit
  confirmation gate

#### Scenario: The full Graphify environment is installed

- **WHEN** the full Graphify tool profile is bootstrapped
- **THEN** it uses managed Python 3.12, validates the imports contributed by
  `all` plus `postgres`, including Leiden and PostgreSQL support, and reports
  any unavailable extra as a setup failure

#### Scenario: Capability state is inspected

- **WHEN** a developer runs the knowledge capability diagnostic
- **THEN** it emits a redacted machine-readable matrix for every GitNexus and
  Graphify feature with one of `enabled`, `disabled-by-policy`,
  `missing-credential`, `not-configured`, or `failed`

#### Scenario: Feature profiles are repeated and rolled back

- **WHEN** setup or rollback runs twice for any capability profile
- **THEN** setup remains duplicate-free and rollback removes only the selected
  profile's tool-owned processes, registrations, generated files, and secrets
  references while preserving local indexes unless purge was explicitly chosen

### Requirement: Skills-first agent integration

The repository SHALL expose a project-scoped Graphify Codex skill and
CLI-backed usage instructions, and SHALL expose GitNexus MCP plus its standard
Codex skills through one supported stable setup route. Skill installation SHALL
be idempotent, generator-owned files SHALL be marked as such, and strict
read-blocking behavior SHALL remain disabled.

#### Scenario: Codex setup is performed

- **WHEN** a developer runs `gitnexus setup -c codex` followed by
  `graphify install --project --platform codex`
- **THEN** Codex receives GitNexus MCP and standard skills, the project receives
  Graphify `SKILL.md` plus references, and the Graphify marked `AGENTS.md`
  section and soft `PreToolUse` hook are installed

#### Scenario: Setup is repeated

- **WHEN** the same setup commands run twice against valid configuration files
- **THEN** MCP, skills, guidance sections, and Graphify hook entries are not
  duplicated

#### Scenario: Existing project hook JSON is invalid

- **WHEN** Graphify project setup encounters invalid `.codex/hooks.json`
- **THEN** setup stops before writing, reports the file as a manual repair
  blocker, and preserves the invalid file byte-for-byte

#### Scenario: Graphify strict mode is requested

- **WHEN** a setup command includes Graphify strict mode
- **THEN** the bootstrap rejects it for this rollout and directs the developer
  to the default soft hook

### Requirement: Independent Git-root indexes

The integration SHALL maintain independent GitNexus and Graphify state for the
outer repository and the nested `mcp-router` repository. Outer refresh commands
MUST use `gitnexus analyze . --index-only` and the equivalent Graphify CLI from
the outer root, while nested refresh commands MUST run from `mcp-router/`.
Neither root SHALL write index metadata into the other root.

#### Scenario: Outer repository is refreshed

- **WHEN** the outer knowledge refresh runs
- **THEN** `mcp-router/`, generated evidence, caches, and approved non-source
  trees are excluded and the resulting state is associated with the outer Git
  root

#### Scenario: Nested repository is refreshed

- **WHEN** the nested knowledge refresh runs from `mcp-router/`
- **THEN** it resolves the nested Git root, preserves pre-existing dirty changes,
  and writes no outer-repository index metadata

#### Scenario: Cross-repository research is requested

- **WHEN** an agent needs relationships spanning both repositories
- **THEN** it uses an explicit GitNexus group or an on-demand Graphify merge and
  identifies the source Git root for every result

#### Scenario: One root has no parent commit

- **WHEN** freshness is checked in the outer repository before its first
  intentional baseline commit
- **THEN** the diagnostic reports freshness as indeterminate and does not claim
  the graph is current

### Requirement: Non-destructive configuration and MCP verification

The integration SHALL preserve existing Agentmemory lifecycle hooks,
hand-authored guidance, and unrelated configuration. GitNexus and Graphify
setup SHALL modify only their marked entries, and the bootstrap SHALL verify
the resulting MCP command, repository registry, skill paths, and hook ownership
before declaring setup successful.

#### Scenario: Existing Agentmemory hooks are present

- **WHEN** Codex or Claude configuration already contains Agentmemory hooks
- **THEN** setup leaves those entries semantically unchanged and adds only
  tool-owned entries at the intended scope

#### Scenario: GitNexus stable Codex setup is inspected

- **WHEN** the selected GitNexus `1.6.9` setup completes
- **THEN** the diagnostic expects MCP and standard skills only, and does not
  claim that Codex GitNexus PreToolUse/PostToolUse hooks were installed

#### Scenario: MCP is live

- **WHEN** the developer starts the configured GitNexus MCP server and queries
  the indexed repository list and context resource
- **THEN** the server responds for the intended repository and reports index
  freshness without exposing an unrelated registry entry

#### Scenario: Tool-owned integration is removed

- **WHEN** the documented targeted uninstall path runs
- **THEN** GitNexus/Graphify-owned MCP, skills, guidance markers, and hooks are
  removed while Agentmemory entries and hand-authored guidance remain

### Requirement: Bounded agent and Git lifecycle hooks

The integration SHALL provide an advisory, non-interactive staged-impact
check and SHALL install Graphify's supported Git hooks independently for each
Git root. The ordinary commit path MUST remain usable without a knowledge tool,
network access, an LLM, or a running MCP server.

#### Scenario: Staged changes are inspected

- **WHEN** the repository-scoped pre-commit knowledge check runs with an index
  available
- **THEN** it invokes `gitnexus detect-changes --scope staged`, reports changed
  symbols and affected flows, and does not mutate the index or block the
  commit

#### Scenario: Optional tooling is unavailable during commit

- **WHEN** a developer commits while GitNexus or Graphify is absent, stale, or
  unhealthy
- **THEN** the commit remains non-interactive and succeeds while the diagnostic
  records the skipped check and reason

#### Scenario: Graphify hooks are installed

- **WHEN** `graphify hook install` runs from a Git root
- **THEN** it appends marked `post-commit` and `post-checkout` sections to the
  effective hooks directory, registers its merge driver and `.gitattributes`
  entry idempotently, and preserves unrelated hook content

#### Scenario: Graphify post-commit runs

- **WHEN** a code commit succeeds with the Graphify hook installed
- **THEN** a detached, bounded, code-only AST refresh is launched, no network or
  LLM call runs in the Git process, and failures are written to the redacted
  Graphify hook log

#### Scenario: Graphify hook runs during merge-family operations

- **WHEN** Git invokes the hook during rebase, merge, or cherry-pick
- **THEN** the Graphify hook exits without starting a competing rebuild

#### Scenario: GitNexus prerelease behavior is not enabled

- **WHEN** a developer inspects the initial rollout's commit hooks
- **THEN** no GitNexus automatic post-commit reindex is present, and any stale
  index is recovered through the explicit status and analyze commands

### Requirement: Safe local graph outputs

The integration SHALL keep GitNexus databases, registries, credentials,
semantic caches, Graphify cost/interpreter/cache files, and other local runtime
state out of version control. Graphify output tracking SHALL remain disabled
until a documented pilot verifies size, determinism, rebuild latency, and
worktree behavior.

#### Scenario: Local state is generated

- **WHEN** either repository is analyzed
- **THEN** `.gitnexus/`, Graphify runtime state, caches, cost files, and
  credentials are ignored and no secret is copied into a tracked file

#### Scenario: Pilot output is evaluated

- **WHEN** the controlled output pilot completes for both Git roots
- **THEN** it records file count, output size, rebuild duration, repeatability,
  resource use, and worktree diff before any output is made trackable

#### Scenario: Graph outputs are merged for research

- **WHEN** an on-demand Graphify merge is requested
- **THEN** the merged file is written to an explicitly local path and is not
  treated as either repository's source-of-truth graph

### Requirement: Observable diagnostics and scoped rollback

The integration SHALL expose redacted status evidence for tool versions,
repository scope, index freshness, hook registration, MCP reachability, skipped
operations, and failure reasons. Rollback SHALL be independently executable
from each Git root and SHALL preserve application code, Agentmemory hooks,
hand-authored guidance, and unrelated nested-repository changes.

#### Scenario: Workspace status is checked

- **WHEN** a developer runs the knowledge status command from the workspace root
- **THEN** it reports the outer and nested Git roots independently, each index's
  freshness, Graphify hook status, MCP registration, and any group state

#### Scenario: Refresh fails

- **WHEN** a requested refresh fails because of a missing runtime, lock, or
  parser error
- **THEN** the command exits non-zero for that requested refresh, emits a
  bounded redacted reason, and leaves the previous usable index intact where the
  upstream tool provides that guarantee

#### Scenario: Rollback is previewed

- **WHEN** a developer requests rollback
- **THEN** GitNexus uninstall first prints its dry-run scope and Graphify reports
  its marked files, hooks, merge driver, and local output targets

#### Scenario: Integration is rolled back

- **WHEN** the preview is limited to recorded tool-owned state and the developer
  applies rollback
- **THEN** only GitNexus/Graphify-owned local state and configuration are
  removed, with no mutation of Go modules, production manifests, Agentmemory
  hooks, or unrelated `mcp-router` files
