## 1. Plan qualification and dependency gates

- [x] 1.1 Run focused `openspec validate centralize-mcp-knowledge-servers --strict`, `openspec show centralize-mcp-knowledge-servers --json`, full `openspec validate --strict --all`, and the semantic scenario-preservation review; retain exact outputs and keep structural status separate from engineering approval.
- [x] 1.2 Re-evidence `review-scope.yaml` with the OpenSpec worktree as planning
  owner, `go-microservices` as provider/client-config owner, `mcp-router` as sole
  router server/token-access writer, live user config as approval-gated runtime,
  and explicit credential/generated/unrelated/dirty exclusions.
- [ ] 1.3 Run the five-provider plan review with Hermes, Claude Code, Codex, Antigravity, and fable-5 through their native routes; record actual versions/models, sanitize the evidence bundle, write `review-plan.md`, and resolve every evidence-backed CRITICAL finding before implementation.
- [x] 1.3a Re-run focused show/strict validation and semantic amendment audit;
  record the current full-store aggregate separately (including unrelated named
  failures), refresh `review-plan.md` for the MCP Router app amendment, and
  obtain exact-tree five-lens approval before source changes.
- [x] 1.4 The original reviewed OpenSpec change was committed and integrated in
  the clean main store without overwriting concurrent changes; focused/full
  validation and store commits were retained. The current MCP Router app
  amendment requires a new review and integration task 1.4a.
- [ ] 1.4a Commit this exact reviewed app amendment in its isolated worktree,
  integrate it into current main without overwriting concurrent/untracked
  changes, rerun focused validation and the named full-store aggregate, commit
  the store, and record the resulting revision before implementation apply.
- [x] 1.5 The original provider-child dependency amendment preserving Hermes
  bridge immutability was reviewed and integrated at store revision `104da6b`;
  it did not release live mutation.
- [ ] 1.5a Review and integrate this amendment's bounded existing-token
  access-map ownership while preserving raw-token lifecycle, client bridge,
  transport/listener, router-wide policy, and all Hermes-side immutability.
  No MCP Router token-access mutation is authorized before integration.

## 2. Isolated implementation setup and RED baselines

- [x] 2.1 Create one dedicated `go-microservices` worktree from the approved base, read its nearest guidance, record base/head/toolchain and focused gates, verify the original checkout's dirty state remains untouched, and run `openspec instructions apply --change centralize-mcp-knowledge-servers` from the integrated store.
- [x] 2.1a Capture immutable registry evidence for GitNexus `1.6.9`, `@sentropic/graphify@0.17.1`, `@agentmemory/agentmemory@0.9.28`, and `@agentmemory/mcp@0.9.28`: npm dist-tag, tarball integrity/digest, upstream repository, license, engine constraints, package name, and dependency lock; fail if `latest` changes before implementation approval rather than silently floating.
- [ ] 2.2 Add a fixture-first topology test that models supported JSON, JSONC, TOML, YAML, and MCP Router SQLite server entries; prove RED because current setup accepts direct GitNexus/Graphify/AgentMemory entries alongside the router, while preserving seeded unrelated entries and comments.
- [ ] 2.3 Add a fixture process-inventory test that proves RED when repeated provider process families exist but permits one MCP Router bridge per active client; include parent/client attribution and seeded secret-bearing command arguments that MUST be redacted.
- [x] 2.4 Add a real pinned `@sentropic/graphify@0.17.1` Node.js adapter fixture with two distinct `.graphify/graph.json` project graphs; prove native `serve` is single-graph/no-`project_path` and lacks legacy PR tools, then assert adapter-owned omitted-selector, unknown/missing graph, stale graph, relative/outside-root/symlink-escape, no cross-project fallback, canonical project-to-repository mapping, and compatibility PR-tool routing cases.
- [ ] 2.4a Add a legacy-to-current Graphify migration fixture that preserves `graphify-out/`, builds `.graphify/`, compares graph/query/path/PR behavior, rejects destructive cleanup, and proves exact rollback to the captured legacy command/path/hash identity; do not claim nonexistent npm `graphifyy@0.9.26`.
- [ ] 2.5 Add a GitNexus multi-repository boundary fixture/probe that proves one process can serve an isolated approved registry or filtering proxy, rejects extra/unapproved repositories and stale/ambiguous selections, and proves credential-bearing remote userinfo is absent from client-visible/evidence output.
- [ ] 2.6 Add an isolated AgentMemory boundary fixture that proves RED when the engine is unavailable but a fallback shim returns an empty successful result; define assertions for fail-closed transport, engine identity, expected tool class, two distinct authenticated client identities mapped to server-derived audit attribution (`agentId` where the pinned schema supports it and a reserved concept for `memory_save`), and cross-client tagged write/recall.

## 3. Topology model and redacted diagnostics

- [x] 3.0 Publish the authoritative supported-client matrix (Claude, Cursor, Codex CLI/Desktop, KiloCode, Kiro, Factory, OpenCode, Zed, Kimi, Antigravity, Hermes) with config format, ownership, bridge mechanism, fixture, installed/absent acceptance state, and compatibility-exception behavior; all later inventory and test tasks consume this matrix.
- [x] 3.1 Implement a value-free topology inventory in repository-owned scripts/helpers that accepts explicit config/process inputs, classifies expected bridges separately from direct provider servers, and emits deterministic JSON with client owner, server class, count, health, and redacted path/identity only.
- [ ] 3.2 Implement format-aware read-only client-config discovery for every supported client detected on the host; unsupported formats, symlinks, invalid JSON/JSONC/TOML/YAML, and inaccessible files SHALL be typed blockers rather than guessed or rewritten.
- [ ] 3.3 Integrate topology diagnostics into `knowledge-status`, `knowledge-doctor`, and AgentMemory doctor output so duplicate direct registrations/processes, router child collisions, stale/missing graphs, GitNexus staleness, and AgentMemory fallback mode fail readiness without mutating live state.
- [x] 3.4 Verify GREEN with the focused topology fixtures, `bash -n` for changed shell scripts, redaction assertions against seeded MCP tokens/AgentMemory secrets/authenticated URLs, and repeated deterministic output comparison.

## 4. Router-owned GitNexus and Graphify source behavior

- [x] 4.0 Record latest-stable evidence without installing: upstream desktop
  release identity; installed bundle version/identifier/signing/executable hash
  and running executable identity; CLI npm dist-tag/SRI/shasum/engine/source and
  exact selector; provider pins/integrities; prerelease/floating exclusions.
- [x] 4.0a Create the isolated `mcp-router` worktree, read nearest guidance,
  record base/head/dirty state plus Node/pnpm/lock versions, and retain baseline
  shared tests, Electron typecheck/format/build results.
- [x] 4.0b Add and execute failing shared/Electron/disposable tests before
  production changes. Retain named RED evidence for exact pins, duplicate child
  names, alias ambiguity, token delta preservation, missing/duplicate/expired
  tokens, third-state/replay, command-file owner/mode/symlink/digest rejection,
  lock conflict, safeStorage unavailable, post-step failure injection, cache and
  runtime restoration, and secret disclosure.
- [x] 4.0c Implement the app-native declarative preview/apply/restore transaction
  for bounded knowledge children and existing-token access maps. Use app
  services/repositories, an authenticated single-instance command boundary,
  durable encrypted recovery journal, all-target preflight, exact commit point,
  compensation/manual-recovery state, runtime quiescence/cache refresh/restart,
  and app-owned online backup/restore. Direct external SQLite/shared-config
  writes and raw token lifecycle/value handling are forbidden.
- [x] 4.0d Remove `go-microservices` router SQLite/shared-config apply/restore
  authority while retaining client-config fixture planning; add a cross-repo
  source gate proving only MCP Router app code writes router server/token state.
- [x] 4.0e Run GREEN shared tests and disposable real app repository/service
  integration, including two apply/restore cycles, failure injection after every
  server/token/runtime step, exact logical/metadata identities, safeStorage,
  lifecycle/name-map updates, unrelated-state preservation, and redaction.
- [x] 4.0f Package the transaction-bearing app with a distinct source/build
  identity based on upstream `0.6.3`; retain source commit, lock provenance,
  artifact digest/signature/notarization decision, ASAR integrity, Electron
  fuses, disposable install/start/command smoke, prior-app backup, and rollback
  artifact. Do not call the modified build unmodified upstream `0.6.3`.

- [ ] 4.1 Keep GitNexus on npm latest stable `1.6.9` (reject RC/specialized tags) and replace direct `gitnexus setup -c codex` with a router-owned digest-pinned GitNexus boundary while preserving project-native skills and existing local index writer locks; expose only approved repositories and read-only operations.
- [ ] 4.2 Replace the legacy Python Graphify runtime and two direct registrations with one repository-owned Node.js adapter pinned to `@sentropic/graphify@0.17.1`; host isolated approved graph stores in one MCP process, make `project_path` required, reject invalid paths before graph access, and expose native graph tools plus compatibility PR analysis backed by `review_delta`/`review_analysis` and the mapped repository.
- [ ] 4.3 Build and verify canonical `.graphify/graph.json` artifacts for microservices and mcp-router while preserving legacy `graphify-out/` canaries; switch registration only after compatibility acceptance and retain rollback until final sign-off.
- [ ] 4.4 Update MCP verification to exercise the router path end to end: isolated/filtering-proxy GitNexus `list_repos` plus repository-scoped read calls; Graphify adapter `graph_stats`, `query_graph`, `shortest_path`, `review_delta`, `review_analysis`, and compatibility PR calls for both explicit project roots; outside-root/symlink/missing/stale failures; project-to-repository identity; and adapter/native package identity evidence.
- [ ] 4.5 Verify GREEN with focused tests, real pinned local provider probes, setup-twice idempotency, rollback-preview scope, and assertions that no direct client GitNexus/Graphify entry is created and no unrelated router/client state changes.

## 5. Router-owned AgentMemory and memory ownership

- [ ] 5.0 Upgrade and pin both `@agentmemory/agentmemory` and `@agentmemory/mcp` to `0.9.28`; verify Node.js 20+, engine/API compatibility, hook compatibility, persisted-store schema migration/rollback, MCP tool schemas, and package-lock integrity before changing bootstrap defaults.
- [ ] 5.1 Change AgentMemory bootstrap source so supported MCP clients retain/use MCP Router rather than receiving direct AgentMemory shim entries; preserve Claude/Codex lifecycle hooks, pi extension behavior, project-native skills, and per-agent audit identity. Add a centralized-topology guard/cutover lock so bootstrap refuses direct MCP wiring during and after migration rather than recreating drift.
- [ ] 5.2 Implement engine-backed readiness that checks loopback health, expected engine-backed MCP surface, non-fallback store/generation identity, and a non-sensitive cross-client tagged write/recall; empty fallback results MUST fail readiness.
- [x] 5.3 Add diagnostics/documentation for memory ownership: Hermes native memory for stable user/profile facts, AgentMemory for shared engineering/session context, and no Mem0 activation without a separate reviewed ownership contract; do not migrate or dual-write existing content.
- [ ] 5.4 Verify GREEN with isolated engine/shim tests, bootstrap-twice fixtures, hook/config preservation hashes, cross-client recall acceptance, and failure tests for engine-down/fallback mode with no payload or credential disclosure.

## 6. Backup, synthetic cutover, and rollback

- [ ] 6.1 Implement a preview-only cutover planner that records anchored target identities, regular/symlink/absent kinds, modes, digests, format, target server entries, expected pre/post states, client/process owners, router database schema/identity, and an immutable redacted plan digest without storing secrets.
- [ ] 6.2 Implement complete backup and restore for the bounded mutation scope
  with protected manifests and exact identities. Client files remain owned by
  the client transaction. Router database/shared-token backup and restore MUST
  be invoked only by the MCP Router app-owned encrypted transaction API; external
  automation cannot open/write/replace those files. Verify integrity/schema,
  connection quiescence/reopen, cache reset, and third-state refusal.
- [x] 6.3 Implement format-aware minimal removal of only direct GitNexus/Graphify/AgentMemory entries while preserving MCP Router bridges, JSONC comments, hooks, skills, unrelated MCP servers, credentials, indexes, memory data, and sessions; use native client commands only when their mutation scope is provably exact.
- [x] 6.4 Run two clean synthetic apply cycles and two restore cycles against fixture homes and a disposable router database; assert deterministic post-state, exact pre-state restoration, no duplicate entries, and unchanged canary hashes.
- [x] 6.5 Update rollback preview/apply behavior and tests so provider/router entry changes are distinguished from client bridge removal, old direct registrations can be restored exactly, and no process is killed by the config transaction.

## 7. Documentation and repository-wide verification

- [x] 7.1 Update ADR 0007, `docs/runbooks/knowledge-graphs.md`, `docs/agentmemory.md`, troubleshooting/rollback docs, Make help, and applicable agent guidance to describe the centralized topology, explicit Graphify project routing, engine-backed memory proof, expected per-client bridges, and separate live approval gate.
- [ ] 7.2 Update focused test expectations, the developer-memory verification table (retire direct-registration grep checks), and any capability matrix/schema counts affected by replacing two Graphify registrations and direct AgentMemory/GitNexus setup; regenerate only repository-owned derived artifacts and review their diffs.
- [ ] 7.3 Run provider repository gates plus MCP Router shared tests, Electron
  typecheck/format/build/package, disposable transaction E2E, cross-repo writer
  authority scan, `git diff --check`, and applicable broader gates; retain exact
  exit codes and separate unrelated aggregate failures before completion.
- [ ] 7.4 Run `graphify update .` after source changes, remove any generated GitNexus instruction block that violates agent guidance, run GitNexus change detection/impact on changed shared symbols, and classify unavailable or stale indexes as UNKNOWN rather than LOW.
- [ ] 7.5 Run the required five-provider code review against committed/staged/unstaged/untracked implementation evidence and executed test outputs; fix evidence-backed blockers in at most two review/fix rounds, rebuild evidence after each fix, and commit the implementation only after independent fail-closed approval.

## 8. Live eligibility and explicit execution approval

- [ ] 8.1 **REQUIRES: Sections 1–7 complete and the Hermes dependency in task 1.5 reconciled.** Capture the final redacted live client/router/process inventory, SHA-256 config fingerprints, router database identity, provider versions, token-access shape, per-client MCP Router authorization and stale-token status, owner/principal/writer list, backup/restore references, current graph/index freshness, and AgentMemory engine health without mutation.
- [x] 8.2 Perform read-only provider eligibility probes only: verify the approved package versions/digests, GitNexus freshness, canonical `.graphify/graph.json` metadata, preserved legacy Graphify canaries, and AgentMemory `0.9.28` engine health without installing packages, refreshing indexes, writing memory data, restoring `.env`, starting processes, or changing hooks/configuration; record `BLOCKED` for drift/stale/unhealthy providers.
- [x] 8.3 Mark `prereq-e8d79b8d0a27b45a` superseded and prohibit execution.
  Author an immutable replacement bound to exact MCP Router source commit,
  packaged artifact digest/signature, installed app identity, CLI/provider pins
  and integrity, app/database/shared-config pre/post identities, provider
  prerequisites, exclusions, canaries, encrypted backup manifest, app/config/
  access-map rollback, test-data policy, and owner. Complete disposable
  install/apply/restore rehearsal, obtain separate digest-bound prerequisite
  `GO`, execute only that generation, then rerun 8.1/8.2. Drift invalidates GO.
- [ ] 8.4 Produce the immutable live cutover and committed-state restore generations from the approved post-prerequisite state, run a final preview against live identities, and request separate operator `GO` bound to the plan digest, backup manifest, affected clients, principals, maintenance window, and latest safe rollback start. Do not infer approval from implementation or prerequisite authorization.

## 9. Approval-gated live cutover and acceptance

- [ ] 9.1 **BLOCKED BY: explicit operator `GO` from task 8.4.** Publish the protected cutover lock, quiesce affected client config writers/restarts and automatic bootstrap jobs, stop or prove non-restarting state for affected GUI/CLI clients, verify owner acknowledgements/launchd/cron/process state, publish the complete verified backup manifest, and stop on any drift or unexpected writer.
- [ ] 9.2 Apply only the approved router child definitions and client-entry removals: one pinned GitNexus boundary, one validating multi-project Graphify boundary, one fail-closed engine-backed AgentMemory boundary, and one retained MCP Router bridge per supported client; do not touch unrelated servers or provider data.
- [ ] 9.3 Restart affected clients in bounded groups. For every installed client,
  verify exact running app artifact and bridge CLI, router-mediated provider
  calls, allowed knowledge-child access, denial of unapproved child access,
  preserved unrelated token access, and retained client/token/server identities
  without token values.
- [ ] 9.4 Verify no duplicate direct provider registration or provider process family remains after old sessions exit, while expected per-client bridge processes, hooks, skills, unrelated MCP servers, indexes, sessions, and credentials remain intact.
- [ ] 9.5 If acceptance fails, keep maintenance active and execute approved
  rollback; restore and verify prior application binary/version/signature, CLI
  selectors, database, shared config, token-access maps, client configuration,
  runtime/cache state, and client recovery before reporting containment.
- [ ] 9.6 During immediate and scheduled monitoring, rerun topology and AgentMemory engine-backed health checks so engine-down/fallback mode alerts and blocks closure; after monitoring confirms no bootstrap/client recreates direct servers and memory remains shared, obtain final sign-off, mark only evidenced tasks complete, rerun focused/full OpenSpec validation and semantic review, archive the change, and commit the shared store.
