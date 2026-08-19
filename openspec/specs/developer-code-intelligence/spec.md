# Developer Code Intelligence

## Purpose

Define the repository contract for optional, skills-first GitNexus and Graphify developer knowledge graphs, including safe setup, independent Git-root operation, verification, lifecycle hooks, generated-state policy, and scoped rollback.

## Requirements

### Requirement: Stable skills and CLI contract

The repository SHALL use the official agent skills as guidance and the pinned official CLIs as the source of truth for setup, indexing, querying, status, and rollback. The selected stable versions SHALL be GitNexus `1.6.9` and Graphify-Labs Graphify package `graphifyy` `0.9.42`, installed with Python 3.12 and invoked through the `graphify` CLI. Unrelated Graphify packages or alternate providers MUST NOT be selected implicitly.

#### Scenario: Pinned tools are diagnosed

- **WHEN** a developer runs the knowledge-tool diagnostic
- **THEN** it reports the exact GitNexus and Graphify versions, Python/Node prerequisites, upstream source, and the recorded license decision

#### Scenario: Upstream has a newer stable or prerelease

- **WHEN** the update check finds a newer PyPI or npm release
- **THEN** it reports the candidate and keeps the selected pins unchanged until license, CLI-help, hook, and focused end-to-end checks are approved

#### Scenario: The workstation has the old Graphify tool

- **WHEN** the diagnostic finds Graphify older than `0.9.42` or another version
- **THEN** it reports the mismatch and the bootstrap offers the pinned Graphify-Labs PyPI package `graphifyy[all,postgres]==0.9.42` with Python 3.12 without changing application dependencies

#### Scenario: Optional tooling is absent

- **WHEN** a developer runs ordinary repository verification without either optional tool
- **THEN** application verification remains usable and the knowledge diagnostic emits a bounded actionable warning

#### Scenario: GitNexus license approval is absent

- **WHEN** GitNexus is installed but no approved PolyForm Noncommercial decision is recorded
- **THEN** mandatory setup is refused, the blocker is named, and existing agent configuration remains unchanged

### Requirement: Graphify extraction coverage and warning policy

Graphify refreshes SHALL use Graphify-Labs `graphifyy[all,postgres]==0.9.42` with Python 3.12 and the reviewed optional parser/database/MCP dependency profile. Refresh diagnostics SHALL classify expected unsupported, sensitive, and allowlisted zero-node inputs separately from actionable parser, runtime, migration, or unknown-source coverage failures. Generated state SHALL use `graphify-out/`; any older state remains a read-only migration canary until acceptance.

#### Scenario: SQL source coverage is enabled

- **WHEN** the pinned Graphify environment is bootstrapped and refreshed
- **THEN** the PostgreSQL/SQL ingestion dependencies in the reviewed optional profile are installed at the `0.9.42` package lock and SQL files are not skipped solely because a parser is absent

#### Scenario: The graph exceeds the HTML visualization threshold

- **WHEN** a refresh produces more nodes than the configured visualization limit
- **THEN** Graphify preserves `graphify-out/graph.json` and the textual report, generates or omits the static studio according to the reviewed threshold policy, and emits no fatal visualization warning

#### Scenario: Expected files are excluded

- **WHEN** Graphify encounters sensitive files, unsupported extensions, or allowlisted configuration/data files that produce zero nodes
- **THEN** the diagnostic records a bounded classified exclusion without treating it as a refresh failure

#### Scenario: Unknown source coverage fails

- **WHEN** a supported source file produces zero nodes and is not allowlisted, or a required parser dependency cannot be installed at the pinned package lock
- **THEN** the refresh exits non-zero with a redacted actionable reason and preserves the last usable graph

### Requirement: Feature-complete local graph capabilities

The integration SHALL install, expose, and verify the complete feature set supported by the pinned tools. GitNexus SHALL support embeddings, PDG-backed control/data and taint queries, generated repository skills, structural checks, route/API analysis, branch-aware indexes, local HTTP UI/MCP, wiki generation, and repository-group contract synchronization. Graphify-Labs `graphifyy` `0.9.42` SHALL support structural and semantic extraction, directed and incremental/watch workflows, the reviewed optional dependency profile, local exports, ontology/reconciliation workflows, multi-project MCP access through one validating router-owned boundary, graph query/path/explain/summary, and supported local ingestion sources.

#### Scenario: GitNexus full local analysis is enabled

- **WHEN** a repository is refreshed in the full local profile
- **THEN** GitNexus bootstraps a missing vector layer within the reviewed 100,000-node full-local cap and preserves a usable existing vector layer during later incremental refreshes,
  reports embedded symbols for non-empty supported roots, returns a usable PDG result rather than a missing-layer response for supported languages, runs structural checks, and exposes the resulting capabilities through its CLI and MCP tools

#### Scenario: GitNexus repository-group capabilities are enabled

- **WHEN** both Git roots are indexed and the workspace group is synchronized
- **THEN** group status, contract links, cross-repository query, and impact operations are available without collapsing the independent local indexes

#### Scenario: Graphify full local pipeline is enabled

- **WHEN** a repository is refreshed in the full local profile
- **THEN** Graphify's code-only commit refresh remains deterministic while its explicit semantic command supports deep and directed extraction, incremental updates, cluster workflows, local query/path/explain, global-graph updates, save-result/reflect feedback, and configured local exports

#### Scenario: Graphify MCP and export capabilities are enabled

- **WHEN** the corresponding local feature profile is selected
- **THEN** one router-owned Graphify adapter provides explicit multi-project routing to canonical `graphify-out/graph.json` artifacts even though native Graphify serves one graph per process
- **AND** callers select a project by its canonical absolute project root rather than by relying on duplicate tool names or server ordering
- **AND** Graphify can generate HTML/no-viz, SVG, GraphML, wiki, Obsidian, Neo4j, and FalkorDB artifacts plus MCP pull-request triage output without placing generated state under version control

#### Scenario: Requested Graphify project is unavailable

- **WHEN** a caller selects a project whose canonical root graph is missing, corrupt, stale beyond policy, or outside approved workspace roots
- **THEN** the call returns a typed unavailable or stale result for that project
- **AND** the router MUST NOT silently route the call to another Graphify server or graph

#### Scenario: Graphify project path escapes the approved root

- **WHEN** a caller supplies a relative, outside-root, or symlink-escaping `project_path`
- **THEN** the validating boundary rejects the call before forwarding it to Graphify
- **AND** no graph or repository outside the approved workspace roots is disclosed

#### Scenario: Graphify project selector is omitted

- **WHEN** a repository-sensitive Graphify call omits `project_path`
- **THEN** the validating boundary rejects the call before invoking the native Graphify server
- **AND** the native startup graph is never used as an implicit fallback

#### Scenario: Graphify project graph is missing or stale

- **WHEN** the selected canonical project graph is missing, corrupt, or stale according to the declared freshness policy
- **THEN** the validating boundary returns a typed unavailable or stale result before invoking Graphify
- **AND** no alternate project graph is selected

#### Scenario: Graphify PR operation selects a project

- **WHEN** a caller invokes compatibility `list_prs`, `get_pr_impact`, or `triage_prs` for an approved project
- **THEN** the validating adapter uses the canonical repository identity and the selected graph's `review_delta`/`review_analysis` results
- **AND** graph impact and PR/worktree data refer to the same project
- **AND** a mismatched explicit repository selector is rejected

#### Scenario: Upgraded Graphify lacks native multi-project or PR tools

- **WHEN** capability discovery on Graphify-Labs `graphifyy` `0.9.42` confirms native serving is single-graph and lacks legacy PR tools
- **THEN** the router-owned adapter provides required project selection and compatibility PR-analysis schemas
- **AND** cutover is blocked if graph/query/review parity cannot be proven for both repositories

#### Scenario: Watch mode coordinates with Git hooks

- **WHEN** interactive Graphify watch mode owns refresh for a Git root
- **THEN** the post-commit and post-checkout paths do not start a competing rebuild, and stopping watch restores the documented hook-owned mode

#### Scenario: Credentialed or networked features are selected

- **WHEN** a developer requests LLM, HTTP, database, workspace-connector, remote-push, or publishing features
- **THEN** setup requires an explicit profile, validates endpoint/credential presence, binds HTTP services to loopback by default, redacts secrets, and refuses public publishing or non-loopback exposure without an explicit confirmation gate

#### Scenario: The full Graphify environment is installed

- **WHEN** the full Graphify tool profile is bootstrapped
- **THEN** it uses Python 3.12, installs Graphify-Labs `graphifyy[all,postgres]==0.9.42` with the reviewed optional language/database/MCP dependencies, verifies `graphify update`, `graphify extract`, and required parser/export features, and reports any required unavailable dependency as a setup failure

#### Scenario: Legacy Graphify state is migrated

- **WHEN** the workstation contains existing Graphify state under `graphify-out/` with captured command/runtime identity
- **THEN** the upgrade preserves that state, validates the upgraded `graphifyy` command against a canary repository, and compares graph identity plus representative query results
- **AND** rollback can restore the previous pinned `graphifyy` package without deleting the generated graph

#### Scenario: Capability state is inspected

- **WHEN** a developer runs the knowledge capability diagnostic
- **THEN** it emits a redacted machine-readable matrix for every GitNexus and Graphify feature with one of `enabled`, `disabled-by-policy`, `missing-credential`, `not-configured`, or `failed`

#### Scenario: Feature profiles are repeated and rolled back

- **WHEN** setup or rollback runs twice for any capability profile
- **THEN** setup remains duplicate-free and rollback removes only the selected profile's tool-owned processes, registrations, generated files, and secret references while preserving local indexes unless purge was explicitly chosen

### Requirement: Skills-first agent integration

The repository SHALL expose project-scoped Graphify skills and CLI-backed usage instructions, and SHALL expose GitNexus and Graphify MCP tools to supported clients through one MCP Router setup route. Skill installation SHALL be idempotent, generator-owned files SHALL be marked as such, and strict read-blocking behavior SHALL remain disabled. Native Graphify and GitNexus project skill layouts SHALL take precedence over a shared directory-level skill symlink. Direct per-client GitNexus or Graphify MCP setup MUST NOT be the canonical route.

#### Scenario: Codex setup is performed

- **WHEN** a developer runs the reviewed knowledge-server setup workflow
- **THEN** MCP Router owns one GitNexus multi-repository server and one Graphify multi-project server
- **AND** supported clients receive or retain one authorized MCP Router connection
- **AND** project-native Graphify and GitNexus skills remain available without adding direct duplicate MCP servers

#### Scenario: Setup is repeated

- **WHEN** the same setup commands run twice against valid configuration files
- **THEN** MCP Router servers, client bridge entries, skills, guidance sections, and Graphify hook entries are not duplicated

#### Scenario: Existing project hook JSON is invalid

- **WHEN** Graphify project setup encounters invalid `.codex/hooks.json`
- **THEN** setup stops before writing, reports the file as a manual repair blocker, and preserves the invalid file byte-for-byte

#### Scenario: Graphify strict mode is requested

- **WHEN** a setup command includes Graphify strict mode
- **THEN** the bootstrap rejects it for this rollout and directs the developer to the default soft hook

#### Scenario: Native project skill layouts are preserved

- **WHEN** Graphify and GitNexus install their project-native skill surfaces
- **THEN** `.agents/skills` remains the canonical shared surface while `.claude/skills` remains a real directory containing the native Graphify, GitNexus, generated, OpenSpec, and hand-authored layouts

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
### Requirement: Non-destructive configuration and MCP verification

The integration SHALL preserve existing AgentMemory lifecycle hooks, hand-authored guidance, unrelated MCP servers, client credentials, and unrelated configuration. GitNexus and Graphify setup SHALL modify only their marked source-of-truth and router-owned entries. Verification SHALL cover the MCP Router endpoint or bridge, router server identity, child server identity, tool discovery, canonical repository routing, freshness, and representative read-only tool calls before setup is declared successful. Repository readiness for freshness SHALL reflect recorded index commit equality with repository HEAD, not timestamp recency alone. A repository whose recorded indexed revision does not equal the current HEAD SHALL NOT be reported as ready for freshness-dependent operations.

#### Scenario: Existing Agentmemory hooks are present

- **WHEN** Codex or Claude configuration already contains AgentMemory hooks
- **THEN** setup leaves those entries semantically unchanged and changes only the approved MCP routing entries

#### Scenario: GitNexus stable Codex setup is inspected

- **WHEN** the selected GitNexus `1.6.9` setup completes
- **THEN** exactly one router-owned GitNexus MCP boundary serves an isolated approved registry or validated filtered view and exposes only the approved repository set and operations
- **AND** no supported client starts another direct GitNexus MCP server

#### Scenario: GitNexus client operation allowlist is enforced

- **WHEN** an ordinary client requests GitNexus tools through MCP Router
- **THEN** only the reviewed read-only allowlist is exposed
- **AND** mutation, setup, group synchronization, and administrative tools are rejected at the boundary

#### Scenario: GitNexus registry contains an unapproved repository

- **WHEN** the native global registry contains a repository outside the approved exposure set
- **THEN** the router-owned boundary excludes it from repository discovery and rejects direct selection
- **AND** the native unrestricted registry is not exposed directly to clients

#### Scenario: MCP is live

- **WHEN** the developer starts an authorized client and queries the router-exposed GitNexus repository list plus Graphify statistics for each approved project
- **THEN** each server responds for the intended repository or project and reports source freshness
- **AND** freshness evidence SHALL not rely solely on recent refresh activity; recorded indexed revision equality with repository HEAD SHALL be the primary signal when recorded revision is available
- **AND** a repository whose recorded indexed revision does not equal HEAD SHALL be reported as stale for freshness
- **AND** the calls prove tool execution through MCP Router rather than only configuration presence

#### Scenario: Duplicate tool name would be ambiguous

- **WHEN** two enabled router child servers advertise the same unqualified Graphify tool name
- **THEN** readiness fails before client cutover
- **AND** the integration requires one multi-project Graphify server or an independently verified collision-safe namespace mechanism

#### Scenario: Repository metadata contains embedded credentials

- **WHEN** GitNexus repository metadata contains userinfo or credential-like material in a remote URL
- **THEN** MCP output and retained evidence redact the complete userinfo and credential value
- **AND** verification fails if an unredacted credential-bearing URL reaches a client-visible result

#### Scenario: Tool-owned integration is removed

- **WHEN** the documented targeted uninstall path runs
- **THEN** router-owned GitNexus/Graphify MCP entries, skills, guidance markers, and hooks in the approved scope are removed while AgentMemory hooks, unrelated router servers, client bridges, and hand-authored guidance remain
