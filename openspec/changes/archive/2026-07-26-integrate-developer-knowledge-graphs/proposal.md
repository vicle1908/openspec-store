## Why

Agents currently have persistent session memory through agentmemory, but no
repository-local structural index for code impact, call-chain, and
cross-document questions. GitNexus and Graphify can provide complementary
knowledge graphs, but they must be integrated deliberately because the
workspace contains two Git repositories, existing agentmemory hooks, generated
agent surfaces, a previously outdated local Graphify installation, and no
outer-repository `HEAD` yet.

## What Changes

- Add a developer code-intelligence capability that defines the ownership and
  boundary between agentmemory, GitNexus, and Graphify.
- Adopt a skills-first, CLI-driven workflow: skills guide agent use, while
  pinned CLI commands remain the observable and reproducible execution path.
- Add reproducible workstation bootstrap, status, refresh, update-check, and
  diagnostic entry points for stable, pinned GitNexus and Graphify versions.
- Address Graphify extraction warnings by enabling the pinned SQL parser extra,
  suppressing oversized HTML visualization while retaining graph data, and
  classifying expected exclusions separately from actionable coverage failures.
- Expand the integration to a feature-complete envelope: enable local
  embeddings, PDG/taint analysis, deep and directed extraction, exports,
  watch/reflect workflows, MCP access, and repository-group contract views;
  expose credentialed, networked, database, and publishing features only
  through explicit opt-in profiles.
- Index the outer microservices repository and the nested `mcp-router`
  repository independently; exclude the nested repository and generated
  artifacts from the outer graph.
- Configure GitNexus MCP and its standard Codex skills through the stable CLI,
  without relying on unreleased Codex hook behavior or replacing Agentmemory.
- Configure Graphify's project-scoped Codex skill and soft `PreToolUse` hook,
  then use its supported post-commit/post-checkout Git hooks only after output
  and latency policy is established.
- Add a repository-scoped, advisory GitNexus staged-impact pre-commit hook and
  explicit stale-index diagnostics for commits made outside an agent session.
- Define whether Graphify outputs are tracked only after measuring graph size,
  determinism, rebuild time, and worktree churn; keep local indexes and
  credentials out of version control.
- Document license approval, stable-channel update policy, nested-repository
  operation, hook composition, failure behavior, rollback, and live
  verification.

## Capabilities

### New Capabilities

- `developer-code-intelligence`: Repository-local GitNexus and Graphify
  knowledge graphs, MCP/skill access, nested Git-boundary handling, lifecycle
  hooks, commit freshness checks, output policy, and diagnostics for supported
  developer agents.

### Modified Capabilities

None. The existing `developer-memory` capability remains the owner of
cross-session memory and its Agentmemory server; this change only composes with
its already-installed hooks and MCP configuration.

## Impact

- Developer tooling under `scripts/`, `tools/`, and root `Makefile` targets.
- Root and nested repository guidance, ignore files, hook configuration, and
  documentation/ADR surfaces.
- Codex MCP, project skills, and hook configuration; existing Agentmemory MCP
  and lifecycle hooks must remain intact. Other agents are documented but are
  not automatically configured by the initial rollout.
- Local GitNexus `.gitnexus/` indexes and Graphify `graphify-out/` artifacts;
  no production service, Go package, public API, database schema, or runtime
  deployment changes.
- The independent `mcp-router/` Git repository, which requires separately
  scoped setup and verification.
- External developer tools: stable GitNexus `1.6.9` (with explicit PolyForm
  Noncommercial approval recorded for this workspace) and stable Graphify `graphifyy`
  `0.9.26` (Apache-2.0), installed in an isolated managed Python 3.12
  environment as `graphifyy[all,postgres]==0.9.26`. The `all` extra supplies
  the supported parser, export, MCP, database, media, workspace, and provider
  extras except PostgreSQL, which is added explicitly; Python 3.12 also enables
  the version-gated Leiden dependency. Observed prereleases such as GitNexus
  `1.6.10-rc.110` are not selected automatically.
- Local listeners use distinct loopback ports and generated outputs remain
  ignored. Remote listeners, database pushes, LLM calls, URL/media ingestion,
  public Gists, and registry publishing require explicit profiles and
  credentials.
