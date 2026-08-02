## 1. Decision, snapshots, and baseline

- [x] 1.1 Record the owning organization's decision on GitNexus PolyForm Noncommercial use; keep the integration optional if approval is denied.
- [x] 1.2 Capture `git status --short --branch`, `git -C mcp-router status --short --branch`, `git config --show-origin --get core.hooksPath`, and normalized hashes of global/project agent configuration before mutation.
- [x] 1.3 Establish or identify an intentional outer-repository baseline commit before validating freshness; preserve all existing outer and `mcp-router` worktree changes.
- [x] 1.4 Confirm Codex as the required acceptance client and document Claude/Cursor as opt-in secondary clients with an owner for each generated surface.
- [x] 1.5 Record the stable upstream snapshot: `npm view gitnexus version dist-tags --json`, PyPI `graphifyy` metadata, official release tags, and the observed GitNexus `1.6.10-rc.110` as out of scope.

## 2. Pinned tooling and diagnostics

- [x] 2.1 Add a version-pinned bootstrap that verifies Node, Python, Git, `npm`, and `uv` prerequisites before installing optional tools.
- [x] 2.2 Install or upgrade GitNexus with `npm install --global gitnexus@1.6.9`; verify `gitnexus -V` and `gitnexus doctor`.
- [x] 2.3 Complete the initial base Graphify upgrade with `uv tool upgrade graphifyy==0.9.26` (or `uv tool install --force graphifyy==0.9.26` when absent); verify `uv tool list` and the packaged skill version. Task 10.1 replaces this base environment with the final full-extra Python 3.12 installation.
- [x] 2.4 Add canonical Make/script entry points for `knowledge-doctor`, `knowledge-status`, `knowledge-refresh`, `knowledge-impact`, `knowledge-update-check`, and `knowledge-rollback`; keep them idempotent, non-interactive, and redacted.
- [x] 2.5 Add diagnostics for missing runtimes, version drift, missing license approval, failed indexes, lock contention, skipped hooks, MCP reachability, and stale indexes without failing unrelated Go verification.

## 3. Repository boundaries and local state

- [x] 3.1 Add outer `.gitnexusignore` and `.graphifyignore` policies that exclude `mcp-router/`, generated evidence, caches, and approved non-source trees.
- [x] 3.2 Add ignore rules for `.gitnexus/`, `graphify-out/` local runtime/cost/cache/interpreter files, and any generator-owned local state.
- [x] 3.3 Implement outer refresh from the outer Git root with `gitnexus analyze . --index-only` and a code-only Graphify CLI refresh.
- [x] 3.4 Implement nested refresh from `mcp-router/` with independent registry names and paths; prove that unrelated dirty changes remain untouched.
- [x] 3.5 Configure and verify an explicit GitNexus group only for on-demand cross-repository research; keep each local index authoritative for its own root.

## 4. Skills and MCP integration

- [x] 4.1 Validate all JSON/JSONC configuration files and save pre-mutation snapshots before setup; stop on invalid project hook JSON.
- [x] 4.2 Run one stable GitNexus route, `gitnexus setup -c codex`, and verify the pinned MCP command, Codex registry entry, and standard global skills; do not install the GitNexus prerelease Codex hook.
- [x] 4.3 Run `graphify install --project --platform codex` independently from the outer root and `mcp-router/`; verify the project `SKILL.md`, references, marked `AGENTS.md` section, and soft `.codex/hooks.json` entry.
- [x] 4.4 Approve newly installed Codex hooks through the supported Codex hook approval flow and verify Graphify's hook-check path fails open.
- [x] 4.5 Repeat setup and prove no duplicate MCP, skill, guidance, Graphify hook, or Agentmemory entries; record the generated-surface ownership.

## 5. Commit and lifecycle hooks

- [x] 5.1 Add an effective-hooks-directory resolver that respects `core.hooksPath`, linked worktrees, and existing hook managers without assuming `.git/hooks`.
- [x] 5.2 Add a marked, advisory pre-commit wrapper that invokes `gitnexus detect-changes --scope staged` when available and never blocks a commit because the optional tool is absent or stale.
- [x] 5.3 From each Git root, run `graphify hook install`; verify marked `post-commit` and `post-checkout` blocks, the pinned interpreter path, the bounded local log, and the `graphify` merge-driver plus `.gitattributes` entry.
- [x] 5.4 Exercise a temporary commit/checkout fixture and prove Graphify refreshes code only, skips merge-family operations, preserves unrelated hook content, and leaves no network/LLM dependency in the Git process.
- [x] 5.5 Explicitly defer any GitNexus automatic post-commit reindex until a stable release and measured single-writer/concurrency test authorize it.

## 6. Graph output pilot

- [x] 6.1 Run a controlled outer Graphify pilot with deterministic, code-only settings and record file count, output size, rebuild duration, and peak resource use.
- [x] 6.2 Repeat the pilot for `mcp-router/` and confirm that outer and nested outputs cannot overwrite one another.
- [x] 6.3 Run repeated refreshes plus commit/checkout simulations to measure determinism, dirty-worktree churn, detached-hook latency, and log redaction.
- [x] 6.4 Decide and document whether curated Graphify outputs are tracked; if approved, track only portable selected files and keep costs, caches, interpreter markers, and credentials ignored.

## 7. Verification and gates

- [x] 7.1 Add focused tests for version/license diagnostics, setup idempotency, invalid JSON protection, ignore-boundary resolution, effective hook resolution, hook merging/uninstall, stale reporting, and redaction.
- [x] 7.2 Verify outer and nested `gitnexus status/list/group` state, Graphify `hook status`/`query` behavior, and MCP repository/context reachability from the supported Codex path.
- [x] 7.3 Verify global Agentmemory hook entries and hand-authored `AGENTS.md` content before and after setup/uninstall using normalized semantic comparisons.
- [x] 7.4 Run `openspec validate --strict --all` and the focused knowledge-tool checks; record environment-dependent skips without claiming application deployment readiness.

## 8. Documentation and rollback

- [x] 8.1 Add the developer-tool runbook and ADR describing ownership boundaries, exact stable pins, prerelease policy, license constraints, skills/CLI commands, hook composition, no-`HEAD` behavior, nested-repository operation, and output policy.
- [x] 8.2 Document normal query/refresh, direct-commit, stale-index recovery, upstream update review, MCP troubleshooting, Codex hook approval, and redacted diagnostics.
- [x] 8.3 Document Graphify project/hook uninstall and GitNexus dry-run validation; remove its Codex MCP and bundled skills only when the preview includes no unrelated client or path.
- [x] 8.4 Test rollback independently from the outer and nested roots, proving Agentmemory hooks, hand-authored guidance, Go modules, production manifests, and unrelated `mcp-router` changes are preserved.

## 9. Verification remediation

- [x] 9.1 Validate the GitNexus uninstall preview and remove all approved GitNexus-owned Codex MCP and skill surfaces during applied rollback.
- [x] 9.2 Make no-`HEAD` freshness reporting authoritative and indeterminate without relaying an upstream up-to-date claim.
- [x] 9.3 Add one guarded Graphify project-setup command that validates JSON, rejects strict mode, installs both roots, and preserves compact canonical guidance.
- [x] 9.4 Aggregate refresh failures across both tools and roots and return non-zero for missing runtimes, locks, or parser failures.
- [x] 9.5 Make configuration snapshots collision-resistant and add focused regression coverage for every remediation.
- [x] 9.6 Align the design, ADR, and runbook with the installed state and remediated command contract.

## 10. Graphify warning remediation

- [x] 10.1 Replace the base Graphify tool with managed Python 3.12 and `uv tool install --python 3.12 --force "graphifyy[all,postgres]==0.9.26"`; verify the SQL, Leiden, MCP, watch, SVG, Neo4j, FalkorDB, PDF, office, video, provider, and PostgreSQL imports supplied by the selected extras.
- [x] 10.2 Set `GRAPHIFY_VIZ_NODE_LIMIT=0` for hook/watch rebuilds of both live graphs and use explicit no-viz output in non-interactive refreshes, retaining `graph.json` and `GRAPH_REPORT.md`.
- [x] 10.3 Define and implement the canonical allowlist for sensitive, unsupported, and expected zero-node configuration/data inputs; emit a bounded classified warning summary.
- [x] 10.4 Fail refreshes for unknown supported-source zero-node files, parser installation failures, and extraction/runtime errors while preserving the last usable graph where supported.
- [x] 10.5 Extend fixture and live-root tests for SQL coverage, oversized graphs, expected exclusions, actionable failures, warning redaction, and non-zero exit behavior.
- [x] 10.6 Align the runbook and ADR with the warning classes, Python 3.12 full-extra pin, no-viz policy, and recovery workflow.

## 11. Feature-complete capability profiles

- [x] 11.1 Add a `full-local` profile that bootstraps each missing GitNexus vector layer with `--index-only --embeddings 100000 --pdg`, preserves usable vectors on later incremental refreshes, proves each non-empty supported root has embedded symbols and a usable PDG result rather than a missing-layer response, runs JSON structural checks, synchronizes `workspace`, and validates every pinned MCP/CLI read feature: query, context, impact/callgraph/PDG, trace, cypher, rename preview, change detection, explain, PDG query, route map, shape check, API impact, tool map, list/index/remove status, branch selection, and group contracts.
- [x] 11.2 Add separately gated GitNexus generated-community-skill, augment, local wiki, remote-embedding, web bridge, and HTTP MCP commands that preserve canonical guidance, store credentials outside the repository, bind loopback by default, and never enable public Gist or registry publishing implicitly.
- [x] 11.3 Add the Graphify full-local commands for deterministic code-only hook refresh, explicit semantic/deep/directed extraction, update/watch/check-update, cluster/label, query/path/explain/affected/god-nodes, multigraph diagnostics, clone/merge/global graphs, benchmark, save-result/reflect, and ignored local exports.
- [x] 11.4 Register `graphify-microservices` and `graphify-mcp-router` as distinct stdio MCP servers, verify their graph paths and tool responses, and remove only their owned entries during rollback.
- [x] 11.5 Implement one refresh-owner lock per Git root so hook-owned, watch-owned, and foreground semantic modes cannot rebuild the same Graphify graph concurrently.
- [x] 11.6 Add local export verification for no-viz/HTML aggregation, SVG, GraphML, wiki, Obsidian, hierarchy tree, call-flow HTML, Neo4j/FalkorDB Cypher, global/merged graphs, benchmark, reflection, and Graphify MCP PR-triage outputs without tracking generated state.
- [x] 11.7 Add a `service-integrations` profile for loopback GitNexus HTTP MCP/UI, remote embeddings and wiki, Graphify HTTP MCP, LLM providers, Neo4j/FalkorDB pushes, read-only non-production PostgreSQL extraction, Google Workspace, and URL/media ingestion; require endpoint/credential validation, redaction, preview, and explicit side-effect confirmation for public Gist/registry publishing.
- [x] 11.8 Add an `agent-platforms` profile that accepts an explicit adapter list, snapshots every target surface, installs only the requested Graphify adapters, and preserves Agentmemory plus hand-authored guidance.
- [x] 11.9 Emit a redacted JSON capability matrix with `enabled`, `disabled-by-policy`, `missing-credential`, `not-configured`, or `failed` for every GitNexus and Graphify feature in both roots.
- [x] 11.10 Add isolated fixtures and live-root acceptance tests for profile idempotency, every capability-matrix row, MCP naming and PR tools, embeddings, PDG/taint, route/API analysis, group contracts, watch/hook locking, diagnostics, clone/merge/global operations, all local exports, service gates, platform adapters, and scoped rollback.

## 12. Final verification alignment

- [x] 12.1 Reconstruct directed Graphify output from canonical source/target endpoints and verify reciprocal directed edges rather than changing metadata flags only.
- [x] 12.2 Make every capability row evidence-bearing and derive its state from live MCP calls, generated output, process state, policy, or credential presence.
- [x] 12.3 Keep managed HTTP profiles loopback-only by rejecting downstream host overrides and test both GitNexus and Graphify listeners.
- [x] 12.4 Route every Graphify service integration through an explicit outer/nested selector with independent graph paths, process names, and ports.
- [x] 12.5 Enforce the canonical sensitive, unsupported-extension, and zero-node allowlists, rejecting unverified or truncated warning sets.
- [x] 12.6 Import Leiden in an isolated bounded subprocess and fail environment verification on import failure or timeout.
- [x] 12.7 Invoke GitNexus context, PDG/taint, route/API, trace, change, rename-preview, group, and structural MCP operations with repository-specific arguments.
- [x] 12.8 Expand rollback preview to enumerate Graphify MCP, project skill/hook, marked guidance, Git hooks, merge driver, advisory hook, and preserved local output/index targets.
- [x] 12.9 Serialize wrapper-owned GitNexus analysis and group synchronization, keep lock conflicts fail-visible, and align documentation with upstream MCP read concurrency.
