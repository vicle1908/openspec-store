# Plan Review: centralize-mcp-knowledge-servers

**Reviewed:** 2026-08-05 Asia/Ho_Chi_Minh
**Status:** MCP ROUTER APP AMENDMENT — APPROVED FOR SOURCE IMPLEMENTATION
**Scope:** OpenSpec planning artifacts plus bounded registry/upstream,
`go-microservices`, and `mcp-router` source evidence. No package installation,
installed-app replacement, live configuration, router database, shared token
config, provider index, memory store, or process mutation occurred.

## MCP Router app amendment review

First amendment review returned NO-GO. Evidence-backed blockers were incorporated:

- split writer ownership between provider/client config and MCP Router app state;
- prohibit external router SQLite/shared-config writes and supersede the old
  provider-only generation;
- limit token ownership to existing-token access maps with no token lifecycle or
  raw-value handling;
- require safeStorage fail-closed encrypted recovery, durable journaling,
  all-target preflight, commit point, compensation, runtime/cache restoration,
  and authenticated single-instance command files;
- enforce true RED→GREEN order, disposable packaged-app rehearsal, distinct
  transaction-bearing build identity, release/rollback artifact qualification,
  full per-client access acceptance, and complete app rollback;
- retain exact latest-stable release evidence for desktop `0.6.3`, published CLI
  `0.2.0`, GitNexus `1.6.9`, Graphify `0.17.1`, and AgentMemory `0.9.28`.

Focused strict validation passes. Current full-store strict validation is
348/349 because unrelated `sprint-switch` requirement 12 is invalid; the
aggregate gate is not reported as PASS. Exact-tree re-review is required before
source implementation.

## Latest-stable registry evidence

| Provider | Canonical package/version | Registry evidence | Runtime/migration consequence |
|---|---|---|---|
| GitNexus | `gitnexus@1.6.9` | npm `latest=1.6.9`; RC `1.6.10-rc.153` and `aptos` tags excluded | Already current; retain Node.js 22+, source/digest and license gates. |
| Graphify | `@sentropic/graphify@0.17.1` | npm `latest=0.17.1`; `graphifyy@0.10.0` is only a compatibility forwarder; npm has no `graphifyy@0.9.26` | Breaking migration from captured legacy command/path/hash identity, Node.js 20+, `.graphify/graph.json`, native single-graph `serve`, no legacy PR tools. |
| AgentMemory | `@agentmemory/agentmemory@0.9.28` and `@agentmemory/mcp@0.9.28` | both npm `latest=0.9.28` | Upgrade engine and shim together; verify store/API/hooks/MCP compatibility and retain fail-closed boundary. |

Exact npm SRI and shasum values were captured during planning but are not repeated here; task 2.1a requires immutable retained registry evidence and rejects dist-tag drift before implementation.

## Structural and semantic gates

| Gate | Status | Evidence |
|---|---|---|
| Focused strict OpenSpec validation | PASS | Exact amended change validates. |
| Full strict store validation | NONZERO: 348/349 | Only unrelated `sprint-switch` requirement 12 fails; aggregate is not PASS. |
| MCP Router app semantic audit | PASS | Exact current operational-readiness SHA/scenarios/normative count retained in `mcp-router-app-amendment-audit.json`. |
| Durable scenario/test traceability | REVISED | `ROUTER-APP-001..003`, provider migrations, access-map-only token handling, and package provenance tasks are specified. |
| Delegated five-lens amendment review | APPROVED FOR SOURCE IMPLEMENTATION | First-round blockers were incorporated and final exact-tree narrow review approved. |
| Named native five-provider task 1.3 | PENDING | Do not infer completion from delegated lenses. |
| Archive readiness | NOT READY | Implementation and approval tasks remain incomplete. |
| Implementation | NOT STARTED | Worktree setup/frozen lock only; no source or live state changed. |

## Critical provider findings and disposition

### Hermes spec review

The initial delegated review found version conflict, missing Graphify enforcement, and pre-approval mutation. The latest-stable revision supersedes the earlier temporary `0.9.26` resolution:

- Canonical Graphify target is now maintained `@sentropic/graphify@0.17.1`.
- Published package source was inspected: native `serve` is single-graph, has no `project_path`, and lacks legacy `list_prs`, `get_pr_impact`, and `triage_prs`.
- One repository-owned adapter process therefore owns multi-project selection and a bounded compatibility PR-analysis surface based on native `review_delta`/`review_analysis` plus mapped repository metadata.
- Graphify migration preserves legacy `graphify-out/`, builds `.graphify/`, compares behavior, and blocks cutover if parity is not demonstrated.
- Eligibility remains read-only; package installs, graph rebuilds, engine upgrades/startup, and schema migrations require separately approved prerequisite generations.

The delegated amendment exact-tree re-review approved source implementation; named native five-provider completion remains required before task 1.3 is checked.

### Claude Code security

Previously approved with warnings and no critical findings. Existing quiescence, redaction, digest, SQLite integrity, authorization, and bounded recall controls remain. Version upgrades add package-integrity and data/schema migration rollback gates.

### Codex provider behavior

Earlier findings remain applicable: fail-closed AgentMemory transport, filtered GitNexus registry exposure, runtime Graphify path validation, server-derived memory identity, and canonical project-to-repository mapping. The Graphify adapter is now explicitly required because current native source lacks the legacy multiplexing and PR surfaces.

### Antigravity architecture

Earlier approval-with-warnings is no longer sufficient after the Graphify runtime/package migration; architecture must be re-reviewed. The hard `optimize-hermes-agent-configuration` dependency remains.

### Fifth delegated product-scope lens

The first amendment review completed this lens and its version/scope findings were incorporated. This does not satisfy the separate named native provider evidence required by task 1.3.

## Required final gates

1. Rerun focused/full strict OpenSpec validation and exact baseline scenario preservation.
2. Re-run five-provider plan review against the new package/runtime migration.
3. Reconcile the active Hermes optimization change.
4. Integrate the reviewed change into the clean shared store.
5. During implementation, re-resolve registry dist-tags and stop on drift rather than floating versions.
6. Keep all installs, Graphify rebuild/migration, AgentMemory schema/startup work, and live cutover behind their separately bound approvals.

No credentials, memory payloads, or live configuration values are included in this artifact.
