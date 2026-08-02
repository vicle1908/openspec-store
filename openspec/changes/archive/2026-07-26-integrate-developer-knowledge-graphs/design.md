## Context

The workspace has two Git boundaries: the outer microservices repository and
the independent `mcp-router/` repository. The outer repository currently has no
`HEAD`, while `mcp-router/` contains unrelated dirty changes that MUST be
preserved. Agentmemory already owns Codex and Claude lifecycle hooks and remains
the cross-session memory layer.

GitNexus provides a local code-structure graph and MCP tools for symbol context,
impact, traces, and change detection. Graphify provides a separate graph for
code, documentation, specifications, and other supported artifacts, with CLI
queries and optional MCP serving. Neither graph is a replacement for
agentmemory, and neither belongs in production service code.

The pre-implementation 2026-07-26 audit found:

- GitNexus stable and npm `latest` are `1.6.9`; npm `rc` is
  `1.6.10-rc.110`. The release candidate adds Codex hook support and automatic
  post-commit reindex behavior that MUST NOT be attributed to the selected
  stable version.
- Graphify stable and PyPI latest are `graphifyy` `0.9.26`; the active upstream
  branch points at the same release. The workstation started at `0.6.7` and
  was upgraded to the selected `0.9.26`.
- PyPI metadata for `0.9.26` exposes `all` and `postgres` separately:
  `all` includes SQL, MCP, watch, export, media, database, workspace, and
  provider dependencies but omits `psycopg`; its Leiden dependency is selected
  only on Python below 3.13. The complete profile therefore uses
  `graphifyy[all,postgres]` on managed Python 3.12.
- GitNexus `1.6.9` passes `doctor` on darwin/arm64 with Node `26.5.0`.
  Graphify `0.9.26` requires Python 3.10 or newer; Python `3.14.6` and
  `uv` `0.11.32` are available.
- GitNexus is licensed under PolyForm Noncommercial; organizational use for
  this workspace was approved on 2026-07-26. Graphify is Apache-2.0.
- Before setup, GitNexus standard Codex skills existed globally but its MCP
  server was not registered. The implemented state registers the pinned
  GitNexus MCP route and its standard skills; Agentmemory remains the only
  owner of global Codex and Claude lifecycle hooks.

These versions and licenses are reviewed implementation inputs, not a promise
to follow a floating release channel.

## Goals / Non-Goals

**Goals:**

- Provide repeatable, version-pinned setup and diagnostics for both graphs.
- Prefer official skills for agent guidance and official CLIs for every
  mutating or diagnostic operation.
- Keep outer and nested Git repositories independently indexed and hooked.
- Preserve existing Agentmemory hooks, hand-authored guidance, and unrelated
  worktree changes.
- Give agents MCP/skill access to the right graph for code, documentation, and
  prior decisions.
- Make commit freshness visible without making ordinary commits depend on
  network access, an LLM, or a running graph server.
- Make Graphify coverage warnings actionable without turning expected
  non-source or sensitive-file exclusions into false failures.
- Provide a feature-complete local profile plus explicit opt-in profiles for
  credentials, network listeners, external databases, and publishing.
- Define safe output, ignore, rollback, and observability policies.

**Non-Goals:**

- Adding a Go dependency, service, deployment artifact, runtime API, or
  production data store.
- Combining GitNexus and Graphify into one persisted graph format.
- Automatically reindexing GitNexus from a Git hook in the first rollout.
- Enabling Graphify's strict read-blocking mode, adopting GitNexus prerelease
  hook behavior, or installing duplicate search-enrichment hooks.
- Automatically configuring every editor detected on the workstation.
- Committing private indexes, credentials, semantic caches, or generated
  agentmemory state.

## Decisions

### Separate graph ownership

Agentmemory owns experiential memory, GitNexus owns structural code
relationships, and Graphify owns cross-artifact knowledge. A graph query MUST
not be presented as a historical team decision, and an agentmemory recall MUST
not be treated as current source truth without source verification.

### Independent repository indexes

The outer repository is indexed as `microservices`; `mcp-router/` is indexed as
its own repository. The outer `.gitnexusignore` and `.graphifyignore` exclude
`mcp-router/`, generated evidence, caches, and other explicitly approved
non-source trees. GitNexus repository groups MAY provide cross-repository
impact and contract views. Graphify `merge-graphs` is an on-demand local
research operation and is not a shared source-of-truth artifact.

This preserves the repository boundary enforced by `mcp-router/AGENTS.md` and
prevents outer hooks from claiming to maintain the nested repository's graph.

### Pinned, locally runnable tools

The canonical bootstrap MUST verify Node and Python prerequisites, license
approval, and exact tool versions before setup:

- GitNexus `1.6.9`, installed with `npm install --global gitnexus@1.6.9`
  after license approval and invoked by its installed CLI. `npx` remains a
  diagnostic fallback, always with `gitnexus@1.6.9`.
- Graphify `graphifyy[all,postgres]==0.9.26`, installed with managed Python
  3.12 through `uv tool install --python 3.12 --force
  "graphifyy[all,postgres]==0.9.26"`. The `all` extra covers the supported MCP,
  parser, media, workspace, export, database, and LLM-provider dependencies
  except PostgreSQL, whose `postgres` extra is explicitly added. Python 3.12
  satisfies the version marker for the Leiden dependency. Every selected
  module, including Leiden, is imported for real; Leiden uses a bounded
  isolated subprocess with a private matplotlib configuration. The persistent
  interpreter path is embedded into Graphify Git hooks at install time.

The bootstrap MUST be idempotent and MUST report warnings when a tool is
absent, while ordinary repository verification remains usable without either
optional tool.

The update check MAY inspect `npm view gitnexus dist-tags` and the PyPI
metadata, but it MUST never replace the selected stable pins automatically.
An upstream stable or prerelease change creates a review item that repeats
license, CLI-help, hook, and focused end-to-end checks before changing the
pins.

### Graphify extraction coverage and warning policy

Graphify remains code-only in the ordinary Git hook path, while explicit
semantic refresh supports documents, papers, images, media, SQL, office files,
workspace shortcuts, and configured live schemas. The bootstrap MUST install
the official `graphifyy[all,postgres]==0.9.26` environment. Missing imports from
either selected extra are setup failures rather than deferred warnings.

Large graphs MUST use Graphify's no-visualization mode once they exceed the
HTML visualization threshold. This preserves `graph.json` and the textual
report while avoiding an oversized `graph.html` warning and unnecessary
rendering cost.

Refresh diagnostics MUST classify warnings into:

- expected exclusions: sensitive files, unsupported extensions, and explicitly
  allowlisted configuration/data files that produce zero nodes;
- actionable coverage failures: an unknown supported source file producing zero
  nodes, parser installation failure, runtime failure, or a failed extraction.

Expected exclusions remain visible in a bounded summary and do not fail a
refresh. Actionable coverage failures return non-zero and preserve the last
usable graph when Graphify supports atomic output. The allowlist is maintained
by the repository's canonical ignore/configuration source, not by ad hoc
per-run suppression. Sensitive and unsupported warnings MUST name an
untruncated set of files and every name MUST match the corresponding canonical
pattern or extension; otherwise the warning is actionable.

### Feature-complete capability profiles

The feature inventory is based on the pinned upstream CLIs and their official
repositories:

- GitNexus: embeddings, PDG/taint and control/data queries, generated
  community skills, wiki generation, structural checks, route/API/tool maps,
  query/context/impact/trace/cypher/rename/change detection, branch indexes,
  index/remove/augment operations, local UI serving, HTTP/stdio MCP, group
  contract sync, and explicitly gated publishing.
- Graphify: deep/directed extraction, incremental update and watch, local
  query/path/explain/affected/god-node traversal, community labeling,
  multigraph diagnostics, semantic staleness checks, clone/merge/global graph
  operations, tree/call-flow/HTML/no-viz/SVG/GraphML/wiki/Obsidian exports,
  MCP stdio/HTTP and PR triage, PostgreSQL/Cargo ingestion,
  save-result/reflect, and optional PDF/office/video/Google, Neo4j, FalkorDB,
  and LLM-provider extras.

The integration uses three profiles:

1. **full-local** is the default workstation profile. GitNexus bootstrap runs
   `analyze --index-only --embeddings 100000 --pdg` independently in each Git
   root. Later incremental refreshes omit `--embeddings` when a usable vector
   layer already exists so GitNexus preserves it and avoids duplicate vector
   insertion; a missing vector layer triggers a forced bounded bootstrap. The
   explicit 100,000-node cap is a reviewed override of the upstream 50,000-node
   default because the outer repository currently exceeds that default; the
   profile still fails rather than disabling the cap implicitly. It then runs
   structural checks and `group sync workspace`.
   Graphify installs
   `graphifyy[all,postgres]==0.9.26` on managed Python 3.12, keeps ordinary Git
   hooks code-only, exposes explicit semantic/deep commands, reconstructs a
   directed multigraph from Graphify's canonical `_src`/`_tgt` endpoints,
   verifies reciprocal source-to-target edges without collapse, enables local
   exports and reflection, and registers per-root MCP stdio servers.
2. **service-integrations** enables optional Graphify MCP HTTP, Neo4j,
   FalkorDB, PostgreSQL, workspace connectors, LLM providers, GitNexus remote
   embeddings/wiki/publishing, and URL/media ingestion only when explicit
   endpoints and credentials are supplied. Every Graphify command accepts an
   explicit outer/nested selector. The managed HTTP profiles are loopback-only
   and reject downstream `--host` overrides; authenticated remote exposure
   uses the upstream CLI directly.
3. **agent-platforms** installs Graphify's supported platform adapters only for
   an explicit platform list, preserving existing Agentmemory and
   hand-authored surfaces. Codex remains the acceptance client; other
   platforms are opt-in rather than silently modified.

Public publishing, public Gists, remote graph pushes, URL/media ingestion, and
non-loopback HTTP listeners are never enabled by the default profile. Each
profile emits a machine-readable capability matrix so diagnostics distinguish
`enabled`, `disabled-by-policy`, `missing-credential`, `not-configured`, and
`failed`. Every row carries the evidence that determined its state: a
repository-specific successful MCP call, generated output, running owned
process, policy decision, or credential check.

### MCP topology, ports, and single-writer coordination

GitNexus retains one multi-repository stdio MCP registration. Optional
GitNexus HTTP MCP binds `127.0.0.1:3000`; its local web bridge binds
`127.0.0.1:4747`. Graphify registers distinct stdio names for the outer and
nested graphs so a query cannot silently target the wrong file:
`graphify-microservices` and `graphify-mcp-router`. Optional Graphify HTTP MCP
binds `127.0.0.1:8080` for the outer graph and `127.0.0.1:8081` for the nested
graph. Managed profiles reject all host overrides. Direct upstream
non-loopback use is outside the managed profile and requires bearer
authentication plus a successful unauthenticated-rejection test.

Graphify has one refresh owner per Git root:

- hook-owned mode is the default and performs detached code-only updates;
- watch-owned mode is explicitly started for an interactive session and
  suppresses competing hook-launched rebuilds;
- semantic/deep refresh is an explicit foreground operation and MUST acquire
  the same repository-local lock before changing graph output.

Wrapper-owned GitNexus analysis and group synchronization share one workspace
writer lock. A lock conflict remains fail-visible and never triggers automatic
index deletion. Long-lived stdio MCP reads retain upstream GitNexus/LadybugDB
concurrency behavior instead of holding the writer lock for the lifetime of an
agent session; the acceptance probe executes repository-specific reads before
the capability matrix reports them enabled.

### Exports, ingestion, and external side effects

The full-local profile generates ignored local HTML/no-viz, SVG, GraphML,
wiki, Obsidian, call-flow, Cypher, global-graph, benchmark, and reflection
artifacts. Human-readable SVG/wiki/Obsidian/tree/call-flow exports use a
deterministic highest-degree projection capped at 750 nodes when the live graph
is larger, while GraphML and Cypher retain the full graph. Graphs over 5,000
nodes set `GRAPHIFY_VIZ_NODE_LIMIT=0` for
watch/hook rebuilds or use an explicit no-viz export path so the core JSON and
report remain authoritative.

Neo4j/FalkorDB pushes, PostgreSQL extraction, URL/media ingestion, Google
Workspace export, LLM-backed semantic extraction, GitNexus wiki generation,
public Gists, and GitNexus registry publishing require explicit profiles.
Database extraction uses read-only non-production credentials; secrets are
environment references rather than command-line literals or tracked files.
Remote-push and publishing commands always have a separate preview/status
step and are excluded from automatic hooks.

### Skills-first, CLI-first command contract

The agent-facing skill is a thin usage guide; the CLI is the source of truth
for state and evidence. The implementation MUST expose the following
commands (the exact wrapper name may be a Make target or script):

| Operation | Outer Git root | Nested Git root | Notes |
| --- | --- | --- | --- |
| Diagnose | `gitnexus doctor`; `graphify hook status` | same commands from `mcp-router/` | Must be read-only and redacted |
| Index/update | `gitnexus analyze . --index-only --embeddings --pdg`; code-only Graphify hook/update | same commands from `mcp-router/` | Serialize per-root writers; semantic/deep Graphify extraction is explicit |
| Query | `gitnexus query/context/impact/detect-changes`; `graphify query/path/explain` | same commands from `mcp-router/` | Skills name the narrowest useful query |
| Agent setup | `make knowledge-setup-agents`; `make knowledge-setup-project` | wrappers operate independently in `mcp-router/` | Snapshot and validate config before mutation; strict Graphify mode is rejected |
| Git hooks | advisory staged-impact hook plus `graphify hook install` | same, from nested root | Graphify owns post-commit/post-checkout; the staged check is separate |
| Capability status | redacted JSON matrix for GitNexus and Graphify | includes nested root independently | Every feature reports enabled, policy-disabled, unconfigured, credential-blocked, or failed |
| Local MCP | GitNexus plus `graphify-microservices` | `graphify-mcp-router` | Stdio by default; each Graphify server receives one explicit graph path |
| Service integrations | loopback HTTP, LLM, database, connector, and push profiles | same with independent graph paths | Never run from Git hooks; validate credentials and endpoints first |
| Rollback | allowlisted GitNexus uninstall plus Graphify project/hook uninstall | same from nested root | Preview enumerates MCP, project skill/hook, marked guidance, Git hooks, merge driver, advisory hook, and preserved graph/index targets |

`gitnexus analyze --index-only` is intentional: stable GitNexus's Codex
integration receives its skills from `setup`, while the index command does not
rewrite hand-authored `AGENTS.md` or install editor-specific files. Graphify's
project install is the project-local Codex skill and hook owner.

### Agent configuration and hook composition

For the selected stable channel, `gitnexus setup -c codex` owns Codex MCP
registration and global GitNexus skills. GitNexus `1.6.9` does not install
Codex PreToolUse/PostToolUse hooks; those hooks are a prerelease capability and
are explicitly out of scope. Claude setup MAY be documented as a secondary
route, but it is not run by the Codex-first bootstrap.

Graphify `graphify install --project --platform codex` owns the project-local
Codex skill, its marked `AGENTS.md` guidance section, and its soft Codex
`PreToolUse` hook. Strict mode is not selected. The hook MUST fail open and
MUST be installed only after valid project hook JSON is snapshotted. Existing
Agentmemory hooks are global and remain untouched; any existing project hook
entries are preserved by an idempotent merge.

Generated GitNexus/Graphify skill directories are generator-owned. The
hand-authored root and scoped `AGENTS.md` files remain authoritative. Any
generated context section MUST be installed with the upstream marker and
preserved by subsequent refreshes.

### Commit and freshness workflow

The first rollout uses three distinct signals:

1. A repository-scoped, non-mutating `pre-commit` check runs
   `gitnexus detect-changes --scope staged` when an index is available. It is
   advisory and MUST NOT block a commit solely because the optional tool is
   unavailable or stale.
2. Graphify's supported `post-commit` and `post-checkout` hooks append marked
   sections to the effective Git hooks directory, launch a detached
   code-only AST refresh, write bounded output to its local log, and register
   the `graphify` merge driver in `.gitattributes` and Git config. They do not
   make network or LLM calls in the Git process.
3. GitNexus stable `1.6.9` provides no Codex agent stale hook. Staleness is
   therefore reported by the explicit status/refresh commands in this rollout.
   Claude's optional upstream PostToolUse adapter is not a Codex dependency.

No GitNexus post-commit reindex is selected until a later stable release and
measurement prove that it is safe with the local database's single-writer
behavior and does not create competing background work with Graphify.

### Output policy

GitNexus `.gitnexus/` data, registries, and runtime caches remain ignored and
local. Graphify outputs remain local-only for this change, including graph,
report, visualization, export, wiki, Obsidian, Cypher, global-graph, benchmark,
reflection, cost, cache, Python interpreter, and credential-related files. A
future change is required before any generated output becomes trackable.

### Failure and security boundaries

All optional tool failures are fail-open for application development but
fail-visible in the knowledge diagnostics. Hooks MUST be bounded, non-
interactive, and safe when run by GUI Git clients or minimal PATH
environments. Hook output MUST redact tokens and MUST never copy source
credentials into graph artifacts. No network or LLM call is permitted in the
ordinary Git commit path.

### Migration and rollback

Rollout order is:

1. Obtain the GitNexus license decision and establish an intentional outer
   baseline commit so commit freshness has a parent.
2. Add pinned bootstrap/diagnostic entry points, ignore policy, and
   documentation without touching `mcp-router` implementation changes.
3. Install and analyze the outer repository, then install and analyze
   `mcp-router` independently.
4. Configure MCP/skills and preserve existing Agentmemory hooks.
5. Install Graphify Git hooks only after pilot output and latency checks pass.
6. Replace the base Graphify environment with managed Python 3.12 and the
   pinned `all,postgres` extras; validate every selected import.
7. Rebuild both GitNexus indexes with embeddings and PDG, then synchronize and
   verify the `workspace` contract registry.
8. Register the two per-root Graphify stdio MCP servers and enable the
   full-local export, global-graph, benchmark, and reflection workflows.
9. Add service and agent-platform profiles without activating external side
   effects or unrequested adapters.
10. Validate the capability matrix, both Git roots, scoped rollback, and
    restoration.

Rollback removes the project-scoped skill/config entries, removes only the
tool-owned hook sections through the upstream uninstall commands, unregisters
the Graphify merge driver, and deletes local `.gitnexus/`/`graphify-out/`
artifacts when explicitly requested. Before `gitnexus uninstall --force`, the
wrapper MUST parse its dry-run and ensure every removal is the recorded Codex
MCP entry or a bundled `~/.agents/skills/gitnexus-*` path. Any unrelated client
or path aborts the operation. Rollback MUST leave local indexes, Agentmemory
hooks, hand-authored guidance, application code, and unrelated `mcp-router`
changes untouched. Profile rollback also stops only profile-owned listeners and
watchers, removes the two Graphify MCP registrations and selected adapter
surfaces, and leaves credentials themselves untouched. Purging indexes or graph
outputs remains a separate explicit operation.

## Risks / Trade-offs

- **[License]** GitNexus PolyForm Noncommercial may not permit the intended
  workplace use → require an explicit approval gate and keep the integration
  optional until approved.
- **[Hook collision]** Multiple tools may edit the same lifecycle arrays →
  snapshot valid JSON/JSONC first, use Graphify's idempotent project merge, keep
  one GitNexus setup route, and run post-install structural validation.
- **[Nested repository drift]** Outer hooks cannot maintain `mcp-router` →
  install and verify hooks from each Git root independently; use a GitNexus
  group only for read-only cross-repo views.
- **[No initial HEAD]** First-commit freshness comparisons are undefined →
  establish a baseline commit before accepting hook behavior.
- **[Worktree churn]** Asynchronous Graphify output can dirty the checkout →
  keep outputs local during the pilot and measure before tracking artifacts.
- **[Release drift]** Stable and prerelease CLIs expose different hook
  behavior → pin stable versions, record the observed prerelease separately,
  and require a focused revalidation before any upgrade.
- **[Resource contention]** GitNexus and Graphify can both parse a large
  workspace → serialize explicit refresh commands and avoid automatic
  GitNexus reindexing in the first rollout.
- **[Full-extra dependency size]** Graphify media, database, provider, and
  export extras increase install size and native dependency exposure → isolate
  them in managed Python 3.12, verify imports, and keep application modules
  unchanged.
- **[Embedding and PDG cost]** GitNexus embeddings and PDG increase analysis
  time, CPU, memory, and index size → keep the upstream cap as the default,
  use only the reviewed 100,000-node full-local override, bound worker
  settings, and record before/after resource evidence.
- **[Competing Graphify writers]** Hooks, watch, and foreground semantic
  extraction can target the same graph → use one repository-local lock and an
  explicit hook-owned/watch-owned state transition.
- **[External side effects]** Wiki providers, URL/media ingestion, database
  pushes, public Gists, registry publishing, and remote HTTP can disclose data
  or mutate external systems → exclude them from defaults, require profile
  selection plus endpoint/credential checks, and preview before mutation.
- **[MCP ambiguity]** Two Graphify roots can silently answer from the wrong
  graph → register distinct server names with absolute graph paths and verify a
  root-specific sentinel query.
- **[Generated guidance]** Re-running analyzers can overwrite local guidance →
  use `--skip-agents-md` where appropriate and keep canonical human guidance
  separate from generated sections.
- **[Graphify coverage]** Optional parsers and large-graph visualization can
  hide source gaps or create noisy warnings → pin `all,postgres`, disable HTML
  in hook/watch rebuilds, classify expected exclusions, and fail on unknown
  supported-source gaps.

## Resolved rollout decisions and future review

- The owning organization approved GitNexus's PolyForm Noncommercial terms for
  this workspace on 2026-07-26.
- Graphify outputs remain local-only; developers rebuild them locally.
- Codex is the required first-rollout client. Claude and Cursor remain opt-in.
- When GitNexus `1.6.10` becomes stable, should its Codex hooks replace the
  explicit status/refresh flow, or should the advisory CLI contract remain?
