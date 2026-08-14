## MODIFIED Requirements

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
