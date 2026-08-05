## Context

See `proposal.md` for motivation. The live workstation has one MCP Router listener on loopback port 3282 and multiple authenticated clients. MCP Router already owns local GitNexus, Graphify, and AgentMemory server definitions, while several clients also retain direct definitions. Long-lived client parents have consequently spawned repeated GitNexus, Graphify, and AgentMemory subprocess stacks.

The providers have different native sharing models:

- GitNexus `1.6.9` is the npm `latest` stable release. The `1.6.10-rc.*` and `aptos` dist-tags are prerelease/specialized and are excluded. GitNexus stores independent repository indexes under each `.gitnexus/` directory and discovers them through `~/.gitnexus/registry.json`; one MCP process serves all registered repositories and requires `repo` selection when more than one is available.
- Graphify's maintained package is `@sentropic/graphify@0.17.1` (npm `latest`, Node.js 20+). The legacy `graphifyy@0.10.0` npm package is a compatibility forwarder. npm registry history contains no `graphifyy@0.9.26`; therefore the superseded legacy contract is the captured host command/runtime plus `graphify-out/` path and canary hashes, not that nonexistent package pin. The maintained CLI writes `.graphify/graph.json` and exposes `graphify serve <graph>`. Published `0.17.1` source confirms one graph per native server, no `project_path` argument, and no legacy `list_prs`, `get_pr_impact`, or `triage_prs` tools.
- AgentMemory engine and standalone MCP shim are pinned together at npm `latest` `0.9.28` and require Node.js 20+. When the engine is down, the shim can expose a reduced isolated fallback store. The current engine is down and the local `.env` is absent, while MCP calls return empty fallback results.
- Pinned `0.9.28` schema inspection shows `memory_save` does not accept or forward `agentId`; the boundary therefore appends a reserved server-derived audit concept for saves and injects `agentId` only for native tools whose input schema declares it. Caller-supplied reserved attribution is rejected.
- Hermes native memory is a separate profile/personal-memory facility and is not an AgentMemory transport.

The canonical implementation owner is `go-microservices`: `scripts/knowledge-tools.sh` owns knowledge-tool setup and verification, while `scripts/agentmemory-bootstrap.sh` owns AgentMemory installation and client wiring. The live MCP Router database and user-level client configs are runtime surfaces, not repository source.

The active `optimize-hermes-agent-configuration` change treats the existing MCP Router definition as immutable except for a parallel-call flag. This change therefore cannot mutate Hermes or MCP Router live state until that invariant is reconciled through sequential OpenSpec review.

## Goals / Non-Goals

**Goals:**

- Establish one client-facing MCP topology and one authoritative process per knowledge provider.
- Make the repository bootstrap converge toward that topology instead of recreating direct client servers.
- Preserve independent GitNexus and Graphify indexes while centralizing query transport.
- Fail closed on Graphify ambiguity, stale/missing graphs, AgentMemory fallback mode, credential-bearing metadata, and duplicate direct process families.
- Make live migration reversible and separately authorized.
- Produce deterministic tests and redacted machine-readable evidence.

**Non-Goals:**

- Change provider internals or combine provider indexes.
- Replace MCP Router with a new service or expose it beyond loopback.
- Remove AgentMemory hooks/skills, Hermes native memory, or project-native Graphify/GitNexus skills.
- Purge local indexes, memory data, sessions, or generated evidence.
- Modify `mcp-router` source unless repository-native investigation proves a router defect must be fixed rather than avoided by supported topology. The initial design avoids a source change there.

## Decisions

### D1. MCP Router is the sole client-facing gateway

Each supported MCP client retains exactly one authorized MCP Router connection. MCP Router owns one GitNexus child, one Graphify child, and one AgentMemory shim. A bridge process per active client is expected; provider subprocesses per active client are not.

Alternative: retain direct providers and use MCP Router only for other tools. Rejected because it preserves repeated processes, tool duplication, and fallback-store fragmentation.

Alternative: connect clients directly to provider HTTP endpoints. Rejected because it duplicates authorization/configuration management and bypasses the existing centralized request-log and permission boundary.

### D2. One GitNexus process serves the registry

The router-owned GitNexus process is configured from the reviewed pinned command, not `@latest`. It MUST NOT point directly at the unrestricted user global registry when that registry contains repositories or metadata outside the approved exposure set. The implementation SHALL either provide an isolated registry containing only approved entries or place a validating read-only proxy in front of the native server that filters repository selection and sanitizes every client-visible result. MCP Router server/tool permissions alone are insufficient repository filtering. Runtime exposure defaults to read-only; mutation/group/setup tools remain available only through separately governed local administration paths if required.

GitNexus index writers remain repository-local commands guarded by the existing workspace writer lock. Centralizing MCP reads does not collapse indexes or authorize concurrent analysis.

Client-visible repository metadata is sanitized before evidence retention and before forwarding to clients. An embedded-userinfo remote URL is a failed redaction gate, even if GitNexus otherwise returns a successful query.

Alternative: one GitNexus process per repository. Rejected because GitNexus natively supports a global multi-repo registry and lazy repository discovery.

### D3. One Graphify process provides multi-project routing

MCP Router owns one repository-provided Graphify adapter process pinned to `@sentropic/graphify@0.17.1`. The adapter, not the native CLI, owns multi-project dispatch: it loads or supervises isolated graph stores for the approved `.graphify/graph.json` artifacts, adds required `project_path` to every project-sensitive tool schema, rejects omitted/unknown/relative/outside-root/symlink-escape selectors before graph access, and dispatches to the selected store. The adapter MUST NOT start multiple same-tool-name MCP children behind MCP Router.

The adapter maintains a canonical project-to-repository map. Because `0.17.1` removes the legacy PR tools, the adapter provides a bounded compatibility surface for `list_prs`, `get_pr_impact`, and `triage_prs` by combining approved repository metadata with Graphify `review_delta`/`review_analysis`; it MUST use the repository mapped to the selected project and MUST NOT combine one project's graph with another repository's PR/worktree data. Acceptance exercises native graph tools and compatibility PR tools for both projects. If parity cannot be proven, cutover is blocked rather than silently dropping the canonical capability.

The source-of-truth migration preserves legacy `graphify-out/` as a read-only canary, builds canonical `.graphify/graph.json` artifacts with `@sentropic/graphify@0.17.1`, compares scoped graph/query/PR behavior, and switches registration only after compatibility acceptance. Legacy and dated snapshot directories remain recovery/evidence artifacts until final sign-off and are not active server paths. The process relies on Graphify's per-path cache and file metadata refresh behavior, and acceptance verifies both projects independently.

The previous `graphify-microservices` and `graphify-mcp-router` child definitions are replaced by one `graphify` child. This avoids MCP Router's unqualified tool-name collision instead of depending on server order.

Alternative: retain two children under distinct server names. Rejected because live evidence shows unqualified tool calls can be resolved to the disconnected child despite an explicit project path.

Alternative: run one native `graphify serve` child per project. Rejected because MCP Router's unqualified tool namespace recreates the collision. Alternative: patch MCP Router to namespace every child tool. Deferred because one repository-owned adapter can provide the required stable surface without broadening router release scope.

### D4. AgentMemory health proves engine-backed proxy mode

The single router-owned AgentMemory boundary uses a fail-closed proxy transport rather than the published shim's local fallback behavior. Core writes and reads MUST return engine-unavailable when the canonical engine cannot be reached; they MUST NOT be written to local KV. The boundary receives the authenticated MCP Router client identity through a trusted side channel or maps the authenticated client to a server-side non-secret `agentId`; caller-supplied identity is ignored for audit attribution. The boundary receives only the canonical loopback engine URL and non-secret scoping inputs. Readiness requires:

1. engine health succeeds on port 3111;
2. the MCP surface exposes the expected engine-backed tool class, not only the reduced fallback set;
3. session/store identity is non-empty and consistent across two test clients;
4. two distinct authenticated test clients, each mapped to a distinct server-derived `agentId`, complete tagged non-sensitive write/recall round trips across client boundaries within a configured bounded acceptance timeout.

An empty session list is valid data only after engine-backed identity is proven; it cannot itself establish health. If the engine is unavailable, the router child is reported degraded and cutover is blocked.

Alternative: allow each client shim to fall back independently. Rejected because those stores are not shared and violate the developer-memory contract.

### D5. Memory ownership is explicit

Hermes native memory owns stable user preferences, personal profile facts, and Hermes-specific operational facts. AgentMemory owns shared engineering observations, project decisions, session summaries, and cross-agent handoffs. Mem0 remains disabled/unconfigured until it has a reviewed non-overlapping purpose.

No automatic dual-write is introduced. Existing content is not migrated or deduplicated by this change.

### D6. Repository source changes precede live mutation

`go-microservices` gains one topology model and redacted diagnostics used by setup, doctor, status, tests, and cutover planning. Source functions operate against explicit fixture roots/config paths so regression tests never touch real user config.

The implementation follows vertical RED→GREEN slices:

1. duplicate configuration/process detection;
2. one multi-project Graphify registration and per-project probes;
3. one GitNexus registration and sanitized multi-repo probes;
4. engine-backed AgentMemory verification and router-only client wiring;
5. backup/restore and cutover planning.

No production source is changed before its focused failing fixture test is observed.

### D7. Live cutover is a separate transaction

The source implementation and plan-review approval do not authorize live mutation. The live transaction has four gates:

1. **Eligibility:** source tests/gates pass; exact supported-client matrix exists; canonical graphs and indexes are already current or a separately approved prerequisite generation has completed; AgentMemory engine is healthy or a separately approved prerequisite generation has completed; redacted backups and restore rehearsal pass twice; the active Hermes optimization change is reconciled.
2. **Execution approval:** operator binds `GO` to the exact plan digest, config fingerprints, client/process inventory, MCP Router database identity, child-server definitions, backup manifest, and maintenance window.
3. **Maintenance release:** affected clients are restarted and all cross-client acceptance checks pass while duplicates are absent.
4. **Final sign-off:** a monitoring interval confirms no client recreates direct servers, no scheduled/bootstrap path restores old entries, the AgentMemory engine remains healthy and engine-backed, and repeated topology diagnostics remain clean. Engine-down or fallback-mode detection alerts the operator and keeps final sign-off closed.

Transaction scope is configuration entries only. Provider data/index directories are canaries and must remain unchanged except for separately approved freshness refreshes completed before the cutover transaction.

### D8. Backup and rollback are format-aware

Before mutation, the cutover tool records each target config as regular file, symlink, or absent; preserves mode, digest, and protected payload reference; and records the relevant MCP Router database backup and schema/version. Backups are stored under an ignored mode-0700 evidence root with payload files mode 0600.

JSON, JSONC, TOML, YAML, and SQLite are not rewritten through one generic serializer. Each client uses its native CLI where that CLI can remove only the targeted server safely; otherwise a format-aware editor performs a minimal structural edit and validates the format. JSONC comments must be preserved. Unknown formats or unsupported symlinks fail eligibility.

Rollback restores exact bytes and metadata for files and the router database only when current state matches either the approved pre-state or approved post-state. State identity uses SHA-256 content digest plus object kind, mode, owner/group policy, and symlink text; mtime alone is non-authoritative. Third-state drift stops automated rollback. The SQLite backup uses the SQLite online backup API or a verified quiesced file copy, records database integrity and schema/user version, and refuses restore across an unapproved schema version.

## Risks / Trade-offs

- **[Active OpenSpec conflict]** The Hermes optimization change requires router immutability. → Mark implementation/runtime entry tasks blocked until sequential reconciliation; do not alter its artifacts implicitly.
- **[Router becomes a larger local dependency]** One gateway outage affects all knowledge tools. → Keep loopback supervision, health diagnostics, exact backups, and client fallback to no knowledge tools rather than isolated mutable stores.
- **[One Graphify default graph is privileged]** Calls omitting `project_path` resolve to the startup graph. → Require explicit `project_path` in project-sensitive acceptance and generated guidance; treat omitted project selection as invalid when multiple approved projects exist.
- **[Graph freshness changes after process start]** A stale process may retain prior data. → Verify current Graphify metadata/reload behavior with real calls after each graph refresh; restart only if the pinned version fails the reload fixture.
- **[GitNexus registry contains stale or sensitive metadata]** → Validate registry entries, freshness, allowed roots, and redacted remote URLs before exposure.
- **[AgentMemory fallback appears healthy]** → Prove engine-backed identity and cross-client recall; tool-list success or empty search alone is insufficient.
- **[Client configs are heterogeneous]** → Inventory formats and native ownership first; unsupported clients remain unchanged and block full readiness rather than receiving guessed edits.
- **[Old clients keep old subprocesses alive]** → Count processes by owner before/after restart and wait for bounded graceful exit; do not kill unrelated processes automatically.
- **[Bootstrap reintroduces duplicates]** → Change source-of-truth setup and add idempotency tests before live cleanup.
- **[Credential leakage through diagnostics]** → Redact environment values, headers, userinfo, and command arguments; seed fixture secrets and assert they never appear.

## Migration Plan

### Phase A — Design and provider review

1. Validate focused and full OpenSpec state in the isolated store worktree.
2. Run five-provider plan review and resolve every evidence-backed blocker.
3. Merge and commit the reviewed change into the clean main store before apply.

### Phase B — Source implementation in isolated `go-microservices` worktree

1. Create a dedicated worktree from the intended base; preserve original dirty state.
2. Obtain apply instructions and re-read all context artifacts.
3. Implement each RED→GREEN slice and run focused shell fixtures after each.
4. Update ADR/runbooks/docs and repository guidance.
5. Run shell syntax, focused knowledge/AgentMemory fixtures, agent-guidance validation, relevant repository gates, Graphify update, and independent code review.
6. Commit source changes; keep live config untouched.

### Phase C — Synthetic rehearsal

1. Materialize sanitized fixture copies of every supported client config and a disposable MCP Router database.
2. Apply the cutover plan twice from clean fixtures and compare deterministic post-state.
3. Restore twice and prove exact hashes/modes plus preservation of unrelated servers, hooks, skills, and comments.
4. Start fixture/isolated provider processes and prove one GitNexus, one Graphify, and one AgentMemory shim topology.

### Phase D — Read-only eligibility and separately authorized prerequisites

1. Reconcile the active Hermes optimization change.
2. Without changing live files, indexes, memory data, or processes, capture the supported-client matrix, redacted live inventory, process ownership, config fingerprints, router database identity, child-server definitions, client token access shape, current provider versions/freshness, and backup/restore plan. If a required provider is stale or unhealthy, eligibility is `BLOCKED`, not a license to refresh it.
3. If refresh/start actions are required, create a separately named prerequisite-mutation generation with exact targets, locks, canaries, rollback scope, and test-data policy. Obtain explicit operator approval bound to that generation before refreshing GitNexus/Graphify state or restoring AgentMemory environment/startup. Re-run read-only eligibility after the generation.
4. Produce an immutable cutover plan digest from the post-prerequisite read-only state and request separate live execution approval. This approval does not authorize prerequisite mutation or live cutover implicitly.

### Phase E — Live cutover

1. Quiesce affected client restarts/config writers and freeze bootstrap jobs. Publish a cutover lock under the protected evidence root; repository-owned bootstrap and hook paths MUST refuse MCP configuration mutation while that lock is active. Eligibility records every launchd/cron/client writer, and execution additionally requires affected GUI/CLI clients to be stopped or placed in a verified non-restarting state.
2. Back up complete mutation scope and publish the verified manifest.
3. Configure one pinned GitNexus child, one multi-project Graphify child, and one engine-backed AgentMemory shim in MCP Router.
4. Remove only duplicate direct GitNexus/Graphify/AgentMemory entries from approved clients; retain their MCP Router bridge and all unrelated entries.
5. Restart affected clients in bounded groups and verify after each group.
6. Release maintenance only after all required scopes pass.

### Rollback

- Before router/client activation is complete, restore changed files/database from the exact backup manifest in reverse order.
- After committed cutover, use a separately prepared restore generation containing exact pre-state bytes and metadata; do not improvise edits.
- Preserve provider data/indexes and all evidence during rollback.
- A third-state config, missing backup payload, credential mismatch, or failed client restore stops automation and escalates.

## Verification Matrix

| ID | Scenario | Durable test/gate | Expected assertion | Evidence |
|---|---|---|---|---|
| TOPO-001 | Effective client topology is audited | `knowledge-topology-test --matrix review-scope.yaml` | every declared client has a format fixture; installed and absent states are distinct; unsupported formats block | `artifacts/verification/topology-matrix.json` |
| TOPO-002 | Duplicate direct knowledge server is detected | `knowledge-topology-test --expect-router-only` | expected bridge allowed; direct provider entries fail with owner/class and no secret | `artifacts/verification/topology-duplicates.json` |
| PROC-001 | Duplicate process families are detected | `knowledge-process-test --fixture ps.json` | parentage/executable/flags distinguish one client bridge from direct provider children | `artifacts/verification/process-duplicates.json` |
| GRAPH-001 | Graphify project selector is omitted | `graphify-boundary-test --case omitted-project` | rejected before native invocation; startup graph is not used | `artifacts/verification/graphify-omitted.json` |
| GRAPH-002 | Graphify project path escapes the approved root | `graphify-boundary-test --case path-escape` | relative/outside-root/symlink escape rejected without disclosure | `artifacts/verification/graphify-path-escape.json` |
| GRAPH-003 | Graphify project graph is missing or stale | `graphify-boundary-test --case freshness` | typed unavailable/stale before native invocation; no fallback | `artifacts/verification/graphify-freshness.json` |
| GRAPH-004 | Graphify PR operation selects a project | `graphify-boundary-test --case pr-routing` | graph and PR/worktree data use the same canonical repository; mismatch rejected | `artifacts/verification/graphify-pr-routing.json` |
| GIT-001 | GitNexus registry contains an unapproved repository | `gitnexus-boundary-test --fixture registry-extra.json` | isolated/filtering boundary excludes extra repository and rejects selection | `artifacts/verification/gitnexus-filter.json` |
| GIT-002 | GitNexus client operation allowlist is enforced | `gitnexus-boundary-test --operations read-only` | mutation/setup/group/admin tools unavailable to ordinary clients | `artifacts/verification/gitnexus-allowlist.json` |
| MEM-001 | Canonical AgentMemory engine is unavailable | `agentmemory-boundary-test --engine-down --after-connect` | reads/writes fail closed; local KV unchanged | `artifacts/verification/memory-engine-down.out` |
| MEM-002 | Cross-client shared recall is verified | `agentmemory-boundary-test --two-clients --identity-proof --timeout-policy` | distinct server-derived IDs, same engine identity, bounded cross-client recall | `artifacts/verification/memory-cross-client.out` |
| CFG-001 | Setup is repeated | `knowledge-setup-test --repeat 2` | no duplicate router/provider/bridge entries; unrelated state unchanged | `artifacts/verification/setup-idempotency.json` |
| ROL-001 | Backup/restore is exercised | `knowledge-cutover-test --synthetic --apply 2 --restore 2` | exact bytes/modes/hashes, JSONC comments, SQLite integrity/schema, third-state refusal | `artifacts/verification/rollback-cycles.json` |
| LIVE-001 | Client cutover succeeds | approval-gated live acceptance | router-mediated read-only calls pass; no duplicate providers remain; hooks/skills/indexes preserved | `artifacts/verification/live-acceptance.json` |

Every modified or added specification scenario is mapped by exact scenario name to one of these IDs or to the DM verification table in the developer-memory delta. The semantic audit stores its machine-readable scenario-name comparison alongside this matrix.

## Open Questions

None that may change scope or task ordering. The exact list of live client configuration paths is discovered during eligibility and is an input to the immutable plan, not a design decision.
