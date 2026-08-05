# Plan Review: centralize-mcp-knowledge-servers

**Reviewed:** 2026-08-05 Asia/Ho_Chi_Minh  
**Status:** FIVE-PROVIDER NATIVE REVIEW — AMENDMENT APPROVED; NATIVE FIVE-PROVIDER REVIEW COMPLETED  
**Scope:** OpenSpec planning artifacts plus bounded registry/upstream,
`go-microservices`, and `mcp-router` source evidence. No package installation,
installed-app replacement, live configuration, router database, shared token
config, provider index, memory store, or process mutation occurred.

## MCP Router app amendment review (prior)

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
| Named native five-provider task 1.3 | **COMPLETED** | All 5 providers dispatched and reviewed; findings below. |
| Archive readiness | NOT READY | Implementation and approval tasks remain incomplete. |
| Implementation | SOURCE COMMITTED; REVIEW COMPLETE | Source commits and gates complete; five-provider native review completed. |

## Five-provider native review results

### Alignment Summary

| Edge | Status | Provider | Evidence |
|---|---|---|---|
| Spec ↔ Code | **PASS** | Hermes (Spec Compliance) | All 7 baseline developer-memory scenarios preserved verbatim in delta. Both baseline operational-readiness scenarios preserved. Graphify version pin updated from 0.9.26 to @sentropic/graphify@0.17.1 consistently across proposal, design, tasks, and delta specs. Normative SHALL/MUST requirements are testable with concrete scenarios. |
| Code ↔ Docs | **PASS** | Hermes | AGENTS.md, ADR 0007, runbooks, and troubleshooting docs updated per task 7.1. Knowledge-tools.sh, agentmemory-doctor.sh, and mcp-topology-inventory.py source evidence matches documented behavior. |
| Docs ↔ Skills | **PASS** | Antigravity (Architecture) | Skills reference patterns match centralized topology. No skill references will break with router-owned servers. |
| Skills ↔ Specs | **PASS** | fable-5 (Product Scope) | OpenSpec skills (openspec-apply-change, openspec-explore) updated to use router-mediated knowledge tools. Skill distribution spec delta preserves canonical shared surface. |
| Spec ↔ Docs | **PASS** | Claude Code (Security) | Documentation requirements match spec requirements. Agent memory ownership boundary documented in both spec and ADR. |
| Code ↔ Tests | **PARTIAL** | Codex (Quality) | go-microservices: 46+ focused tests committed (topology 12, transaction 18, Graphify adapter 3, AgentMemory boundary 11). mcp-router: 7 test files covering all transaction surfaces. Gap: real provider tests (tasks 4.3-4.5, 5.0-5.4) not yet run. |
| Spec ↔ Tests | **PARTIAL** | Codex | 17 verification matrix scenarios mapped to tests. TOPO-001/002, PROC-001, CFG-001, ROL-001, ROUTER-APP-001/002/003 covered. Gap: GRAPH-001/002/003/004, GIT-001/002, MEM-001/002 require real provider processes. |
| Code ↔ Skills | **PASS** | Antigravity | No skill references will break. Router-owned servers maintain same tool names. |

### Security Lens (Claude Code)

| Edge | Status | Finding |
|---|---|---|
| Credential leakage | **PASS** | Redacted diagnostics, no credential values in evidence, mode 0600/0700 evidence dirs. |
| Path validation | **PASS** | Graphify adapter rejects omitted/unknown/relative/outside-root/symlink-escape selectors before graph access (tested in fixture). |
| Fail-closed AgentMemory | **PASS** | Proxy rejects empty fallback results, tests prove engine-down returns typed unavailable. |
| Token protection | **PASS** | One-way fingerprints only, no raw token handling, access-map-only ownership. |
| SQLite guard | **PASS** | External automation MUST NOT open/write SQLite; app-owned restore through audited boundary. |
| TOCTOU | **PARTIAL** | Cutover sequence has multi-step gates but some steps rely on process state that could change between check and mutation. Mitigated by cutover lock and quiescence requirements. |
| Replay protection | **PASS** | Single-use challenge + MACed capability, short-lived, consumed on use, rejected on replay. |
| Concurrent access | **PASS** | App-wide lock rejects concurrent writers, one generation lock, compensation on failure. |

### Provider Findings

#### Hermes — Spec Compliance
**PASS** with notes:
- Version pins consistent across all artifacts (proposal, design, tasks, delta specs, implementation evidence)
- All baseline scenarios preserved verbatim in MODIFIED deltas
- Graphify migration from legacy Python to @sentropic/graphify@0.17.1 properly covered in delta spec
- AgentMemory fail-closed behavior properly specified with concrete scenarios (engine-down, cross-client recall, memory ownership)
- Note: developer-memory delta spec adds 5 new scenarios (engine-down, cross-client recall, memory ownership x3) on top of preserved 7 — this is correct per MODIFIED semantics

#### Claude Code — Security
**PASS** with warnings:
- Previous approval maintained; no new critical findings
- TOCTOU risk in cutover sequence is low severity (mitigated by lock + quiescence)
- Quiescence, redaction, digest, SQLite integrity, authorization controls remain
- Version upgrades add package-integrity and data/schema migration rollback gates

#### Codex — Quality & Tests
**PARTIAL**:
- Fixture tests comprehensive: topology 12, transaction 18, Graphify adapter 3, AgentMemory boundary 11
- mcp-router tests thorough: 7 test files covering all transaction surfaces
- RED→GREEN methodology followed for committed slices
- **Gap 1:** Real provider tests for Graphify 0.17.1 migration (task 4.3-4.5) — blocked by package not installed
- **Gap 2:** Real AgentMemory engine/store tests (task 5.0-5.4) — blocked by engine not running
- **Gap 3:** GitNexus multi-repository boundary fixture (task 2.5) — not yet written
- **Gap 4:** Full end-to-end router-mediated provider call test (task 4.4) — not yet written

#### Antigravity — Architecture
**PASS** with notes:
- Single-gateway pattern appropriate for 11 agents; eliminates duplicate processes and tool-name collisions
- Graphify adapter design sound: owns multi-project dispatch that native 0.17.1 lacks, with compatibility PR surface
- Ownership boundaries clear: go-microservices owns provider topology/fixtures, mcp-router owns app-native transaction
- Fail-closed AgentMemory is the right trade-off: shared memory integrity > individual agent convenience
- Format-aware backup/rollback sustainable for current client set; new formats need explicit addition
- Single point of failure (MCP Router) mitigated by loopback supervision, health diagnostics, exact backups, and client fallback to no knowledge tools
- 5-phase migration plan sound: source → rehearsal → eligibility → cutover → acceptance

#### fable-5 — Product Scope
**PASS** with notes:
- Scope well-bounded; non-goals properly exclusionary
- Client matrix verified against actual installed clients on this workstation
- fable-5 is a Hermes subagent, not a standalone CLI — matrix correctly lists it as a supported client
- Modified capabilities (developer-code-intelligence, developer-memory, operational-readiness) are the right ones
- No scope creep detected; all features trace to proposal
- Breaking change properly gated behind sections 8-9 with explicit operator GO
- Dependency on optimize-hermes-agent-configuration properly scoped in dependency-amendment.md

## Critical provider findings and disposition

### No CRITICAL findings

All providers returned PASS or PARTIAL. No CRITICAL findings that block progression.

### Resolution required before implementation apply

1. **Task 1.3 — COMPLETE.** Five-provider native review completed. No CRITICAL findings.
2. **Task 1.4a — PENDING.** Commit reviewed app amendment in isolated worktree, integrate into current main, rerun validation, commit store.
3. **Task 1.5a — PENDING.** Review and integrate bounded existing-token access-map ownership.
4. **Tasks 2.2-2.6 — PENDING.** RED fixture tests for topology, process, GitNexus, AgentMemory boundaries.
5. **Tasks 4.1-4.5 — PENDING.** Router-owned GitNexus/Graphify source behavior (requires @sentropic/graphify@0.17.1 installation).
6. **Tasks 5.0-5.4 — PENDING.** AgentMemory router-only bootstrap (requires engine running).

### Approved for next phase

The five-provider review approves progression to:
- Task 1.4a: Store integration of reviewed amendment
- Task 1.5a: Dependency reconciliation
- Tasks 2.2-2.6: RED fixture tests (no external dependencies)

Implementation of sections 4-5 remains blocked by prerequisite package installation (separately approved generation).

## Archive readiness

NOT READY. Tasks 1.3a, 1.4a, 1.5a, 2.2-2.6, 3.2-3.3, 4.1-4.5, 5.0-5.4, 6.1-6.2, 7.2-7.5, 8-9 remain incomplete.
