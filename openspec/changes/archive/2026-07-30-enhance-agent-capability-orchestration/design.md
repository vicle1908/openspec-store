## Context

See `proposal.md` for motivation and scope. The repository already has a
feature-rich `scripts/knowledge-tools.sh`, a machine-readable capability
matrix, two independently named Graphify MCP servers, GitNexus group support,
an agentmemory bootstrap/doctor flow, and generated OpenSpec/skill surfaces.
The missing layer is a bounded readiness contract that distinguishes
configuration from live usability and binds every claim to exact source state.

Research repeated on 2026-07-30 found:

- GitNexus approved/installed stable is `1.6.9`; the release-candidate channel
  is newer but remains excluded by policy.
- The outer GitNexus status can block after reaching its 230 MB
  FileProvider-backed database, and its direct MCP surface was not available in
  the current session. The nested registry metadata remains separate.
- Graphify approved/installed is `0.9.26`; PyPI reports `0.9.30`. Its MCP graph
  remains readable at 23,431 nodes and 37,465 edges. Current upstream guidance
  emphasizes root-relative incremental manifests, replace-on-reextract,
  deletion pruning, direction preservation, and read-only structural graph
  diagnostics.
- agentmemory repository policy/doctor targets `0.9.27`, installed/latest is
  `0.9.28`, and the REST server is stopped. Seven bridge tools are visible but
  no sessions are returned. Current upstream documentation defines
  `AGENTMEMORY_TOOLS=all` as the full 53-tool surface and `core` as eight tools;
  the expected count must be derived from the selected mode and reviewed
  version.
- OpenSpec approved/installed/latest is `1.7.0`.

The design treats these observations as baseline evidence, not permanent
version requirements.

## Goals / Non-Goals

**Goals:**

- Produce one schema-validated, run-scoped health manifest with truthful
  readiness semantics and process-level deadlines.
- Define quick, exploration, and implementation profiles so lightweight status
  remains cheap while execution readiness is comprehensive.
- Recover agentmemory and knowledge-index reliability before expanding optional
  capabilities.
- Make authority routing and fallback deterministic across OpenSpec,
  GitNexus, Graphify, agentmemory, and direct repository inspection.
- Preserve independent Git roots, source attribution, advisory Git hooks,
  generated-surface ownership, and scoped rollback.
- End planning with no unresolved decision that changes implementation scope.

**Non-Goals:**

- No Go service, database, Kafka, Temporal, Protobuf, REST, container-image, or
  deployment contract changes.
- No automatic Graphify/GitNexus database merge and no promotion of inferred
  graph edges or memory to normative truth.
- No automatic upgrade to Graphify `0.9.30`, agentmemory `0.9.28`, or any
  prerelease tool.
- No automatic enabling of LLM compression, public publishing, remote
  embeddings, non-loopback listeners, or credentialed ingestion.
- No direct `mcp-router/` implementation in the first rollout.

## Decisions

### 1. Extend the existing wrapper and support module

`scripts/knowledge-tools.sh` remains the operator-facing lifecycle wrapper.
The existing Python support module will own schema construction, subprocess
deadlines, redaction, source identity, atomic writes, and deterministic exit
status. A JSON Schema under `scripts/config/` will define
`microservices.agent-capability-health/v1`.

This reuses current root selection, locking, MCP probing, capability matrices,
and rollback ownership. It avoids another daemon and another configuration
surface.

Alternative: build a standalone orchestration service. Rejected because the
first problem is local reliability and evidence, not remote coordination.

### 2. Separate profile readiness from individual probe state

The health manifest has two levels:

- probe status: `healthy`, `degraded`, `unavailable`, `blocked`,
  `not-configured`, or `skipped`;
- overall status: `ready`, `ready-with-warnings`, or `not-ready`.

Each profile declares required and optional probe IDs. A profile is ready only
when every required probe is healthy. Optional failures produce
`ready-with-warnings`; a required failure produces `not-ready` and a non-zero
exit.

Profiles:

| Profile | Contract |
|---|---|
| quick | Read-only versions, configuration, source identity, lightweight health/resource discovery |
| exploration | Quick plus live GitNexus/Graphify queries and agentmemory recall availability |
| implementation | Exploration plus strict OpenSpec, skill parity, index freshness/integrity, disposable memory round trip, focused repository gates, and final source-identity match |

Alternative: one universal health command. Rejected because it would either be
too weak for execution or too slow for routine status.

### 3. Make evidence run-scoped, atomic, and attributable

Each run writes under a unique directory in the configured evidence root.
The manifest contains:

- schema and run ID;
- UTC start/end timestamps;
- HEAD commit and deterministic dirty-state fingerprint for relevant paths;
- selected profile and configured deadlines;
- tool approved/installed/latest metadata;
- probe ID, root, required flag, attempts, duration, status, bounded error code,
  and evidence reference;
- explicit change-owned, unrelated dirty, and prohibited-scope path
  classifications for the selected OpenSpec change;
- overall readiness and remediation summary.

The runner writes temporary output and publishes the final manifest only after
all probes terminate and schema validation passes. A latest pointer is updated
only for a successful finalization. Evidence-write failure stops before later
mutating actions.

Alternative: overwrite one status file. Rejected because it loses failure
history and can detach readiness from the source revision that produced it.

### 4. Enforce deadlines outside the probed process

The current support module already uses subprocess and MCP response timeouts,
but `knowledge-doctor` can still block inside a composite shell command. Every
top-level CLI/MCP/REST probe will therefore have an outer process deadline in
addition to protocol-level deadlines. Timeout termination records the elapsed
duration and does not wait indefinitely for a fragile filesystem read.

Only explicitly classified transient probes may retry, using a bounded attempt
count and backoff. Mutating refreshes are never automatically retried after an
unknown partial failure.

### 5. Keep four authority domains and a direct-source fallback

The orchestration skill uses this routing table:

| Evidence | Authority | Fallback |
|---|---|---|
| Intent, scenarios, tasks, acceptance | OpenSpec | Existing artifact files and strict validator |
| Callers, callees, impact, PDG, routes | GitNexus | `rg`, direct source inspection, focused tests |
| Runbooks, architecture concepts, cross-root documents | Graphify | `rg`, direct documents, explicit source locations |
| Prior decisions, lessons, session handoff | agentmemory | Session transcript and current artifacts |

Fallback never becomes evidence that the unavailable specialized probe passed.
When memory or inferred graph evidence conflicts with OpenSpec or source code,
the conflict is reported and the authoritative source wins.

### 6. Use an explicit FileProvider compatibility gate

No current upstream evidence proves an alternate GitNexus state-path flag for
this version. The implementation will not invent one. Before any rebuild it
will run a non-destructive compatibility spike:

1. record current index/graph metadata and source identity;
2. test bounded reads and tool-native status against the existing state;
3. determine whether each reviewed CLI supports a documented alternate output
   or state location;
4. test single writer plus reader exclusion and last-good-output restoration in
   a disposable fixture;
5. choose one supported strategy:
   - in-place only when the compatibility fixture passes; or
   - a local mirror/worktree used for indexing when in-place state is unsafe;
6. leave the profile not-ready when neither strategy is proven.

Unreadable `.gitnexus` state is never deleted as a diagnostic shortcut.
Graphify updates must preserve root-relative manifests, replace changed
sources, prune deleted sources, preserve direction, and run the structural
diagnostic for dangling/missing/collapsed/self-loop edges. Unexpected graph
shrinkage or integrity warnings prevent implementation readiness.

### 7. Verify agentmemory by configuration-aware discovery and cleanup

The quick profile checks REST health and selected mode without mutation. The
implementation profile:

1. discovers `AGENTMEMORY_TOOLS` and reviewed version metadata;
2. compares live tool discovery with the selected mode's documented surface;
3. writes one run-tagged disposable memory through the supported surface;
4. retrieves the exact record;
5. deletes it through governance;
6. verifies deletion or audit evidence.

Failure to clean up the probe produces not-ready evidence and identifies the
record ID without content. Optional Ollama/LLM summarization is reported
separately and is not required for zero-LLM memory health.

### 8. Preserve native ownership and separate rollback surfaces

The orchestration skill is hand-authored and canonical under `.agents/skills`.
Policy records which supported clients receive a shared copy, a native adapter,
or an explicit unsupported result. The skill references native GitNexus,
Graphify, OpenSpec, and Agentmemory guidance; it does not duplicate generated
instructions.

Setup and managed-skill repair/rollback are idempotent across outer and nested
roots. The orchestration health rollback is a separate repository-local action
that removes only its latest-evidence pointers. It does not uninstall native
GitNexus/Graphify integrations or remove canonical/generated skills. Native
tool uninstall and managed-skill rollback keep their own preview, ownership,
root-selection, and confirmation contracts. Hooks perform no unbounded `npx`
installation or network fetch.

### 9. Keep first-rollout consumption repository-local

The first rollout exposes Make/CLI commands and retained manifests. It does not
add an `mcp-router` consumer. After the pilot, a separate nested-repository
change may expose the manifest through MCP if latency, ownership, and
authentication requirements justify it.

This resolves the prior open question and keeps the outer change executable
without crossing the independent Git boundary.

### 10. Keep version review separate from health recovery

Approved pins remain unchanged. Health reports approved, installed, and
latest-known values separately. A Graphify `0.9.30` or agentmemory `0.9.28`
upgrade requires current official documentation, compatibility fixtures,
surface regeneration where applicable, and a separately reviewable change.

## Security and Data Boundaries

- All listeners remain loopback-only.
- Probe output is redacted before persistence; complete environments and global
  client configuration are never stored.
- Disposable memory content contains only a generated probe marker.
- Credentialed, public, remote, database, workspace, and LLM features remain
  optional and outside implementation readiness.
- The health runner may mutate only its run directory and the explicitly
  approved disposable memory probe; quick and exploration profiles remain
  read-only.
- No container image is introduced, so there is no `linux/arm64` image
  compatibility decision.

## Verification Strategy

Fixture coverage will include:

- profile required/optional aggregation and exit codes;
- per-process timeout, bounded retry, and independent-probe continuation;
- atomic evidence finalization, interrupted runs, source-state changes, and
  schema rejection;
- credential redaction and bounded errors;
- FileProvider-style stale reads, writer ownership, local mirror fallback, and
  last-good-output preservation;
- Graphify incremental deletion/replacement/direction/integrity behavior;
- GitNexus missing, stale, healthy, and timeout states;
- agentmemory full/core discovery, server-down behavior, round trip, cleanup
  failure, and audit evidence;
- skill distribution, duplicate-free setup, native-surface preservation, and
  rollback across both roots;
- change-scope classification that separates declared orchestration paths from
  unrelated dirty paths and rejects service, deployment, platform, container,
  and nested-repository implementation paths as change-owned;
- authority conflicts and direct-source fallback.

Implementation acceptance requires change-specific and repository-wide strict
OpenSpec validation, focused knowledge/skill tests, agent guidance validation,
OpenSpec surface verification, and a final implementation-profile manifest
bound to the exact source identity with a passing scope audit.

## Risks / Trade-offs

- **[FileProvider continues to return stale handles]** → Use the compatibility
  gate and local mirror strategy; preserve old state and remain not-ready when
  no supported path is proven.
- **[Multiple MCP processes open one LadybugDB file]** → Enforce refresh
  ownership and prevent readers from entering during a rebuild.
- **[Probe termination leaves a child process]** → Use process-group
  termination, bounded cleanup, and explicit orphan detection in fixtures.
- **[agentmemory verification pollutes durable context]** → Use run-tagged
  minimal content, governance deletion, and cleanup verification.
- **[Graphify inferred edges are treated as facts]** → Preserve evidence type,
  confidence, and source locations; route precise code questions to GitNexus.
- **[Generated skill surfaces drift]** → Change canonical policy/generators and
  run supported refresh/verify flows; never patch generated copies manually.
- **[Health checks become expensive]** → Keep profile separation, bounded
  deadlines, and no implicit semantic extraction or index rebuild.
- **[Latest-version metadata changes during implementation]** → Treat latest as
  observation only; acceptance is bound to approved pins and compatibility
  evidence.
- **[Concurrent dirty work is attributed to this change]** → Maintain an
  explicit change-owned path policy, classify every current dirty path in final
  evidence, reject prohibited owned prefixes, and report unrelated paths without
  mutating or silently claiming them.

## Migration Plan

1. Capture current source identity, tool versions, indexes, hooks, MCP entries,
   skill manifests, and unrelated dirty paths.
2. Add the health schema, fixture model, profile policy, atomic evidence writer,
   and process deadline support.
3. Restore agentmemory service health and verify mode-aware discovery plus
   disposable round-trip cleanup.
4. Run the FileProvider compatibility spike and record the supported in-place
   or local-mirror decision before rebuilding either outer knowledge index.
5. Restore and verify outer and nested GitNexus/Graphify health independently,
   including Graphify integrity diagnostics and source freshness.
6. Add the canonical orchestration skill and verify all selected client/root
   surfaces.
7. Pilot quick and exploration profiles, then enable Prepare/Verify/Handoff and
   the implementation profile.
8. Rehearse pointer-only orchestration rollback twice, verify the separate
   managed-skill/native-tool boundaries, and prove memories, indexes, native
   hooks, guidance, credentials, application files, and unrelated dirty changes
   are preserved.
9. Run all focused and strict validation and retain the final
   implementation-profile manifest for the exact source identity with an
   explicit passing change-scope audit.

Orchestration rollback removes only the latest-evidence pointers created by the
health runner. It preserves historical run directories, schema and runner
code, the canonical orchestration skill, hooks, registrations, cross-tool
links, agentmemory data, knowledge indexes, generated/native skills, and
application code. Removing repair-owned client links or native knowledge-tool
integrations requires the separately reviewed managed-skill or upstream
targeted-uninstall workflow and is never an implicit part of orchestration
rollback.
