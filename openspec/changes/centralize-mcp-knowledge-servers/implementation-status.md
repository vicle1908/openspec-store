# Implementation Status: centralize-mcp-knowledge-servers

**Implementation repository:** `/Users/androidteam/Developer/.worktrees/centralize-mcp-knowledge-servers`

**Committed source before current safe-source slice:**

- `94e7f36 feat(knowledge): centralize MCP provider boundaries`
- `c9cb6f8 feat(knowledge): harden cutover transaction fixtures`
- `111279a fix(knowledge): harden registry evidence parsing`
- `5cd3493 docs(knowledge): clarify centralized provider operations`

**Committed safe-source slice:** `2edd362 feat(knowledge): complete safe MCP centralization fixtures`

- Exact npm v3 provider lock and registry-evidence binding.
- Topology matrix/inventory expansion: 12 focused tests.
- Transaction planner expansion: 18 focused tests.
- Native Graphify compatibility/migration fixture: 3/3 tests.
- Native AgentMemory compatibility fixture: 2/2 tests.
- AgentMemory boundary and ownership correction: 11/11 tests.
- Documentation corrections for the actual AgentMemory `0.9.28` seven-tool fallback surface and non-overlapping memory ownership.

Current Graphify and AgentMemory disposable native-package probes, focused source
tests, guidance validation, syntax checks, and strict OpenSpec validation pass
against implementation commit `2edd362`. Ignored registry evidence was
regenerated and matched that exact commit plus the committed lock digest.
No native GitNexus process, real AgentMemory engine/store, registry-mediated
provider call, or live cutover has run. Five-provider review round one found
security/evidence/documentation issues; the source fixes and conservative task
reconciliation passed the final exact-tree narrow review.

## Evidence-backed completed source scope

- Isolated implementation worktree and fixture-first source changes.
- Router-owned GitNexus filtering proxy with approved-repository, read-only,
  payload-bound, and redaction tests.
- Graphify Node adapter source contract with canonical project routing,
  required `project_path`, package/runtime enforcement, stale-graph rejection,
  and compatibility PR tools.
- AgentMemory 0.9.28 router-only bootstrap, cutover lock, engine-backed fixture
  readiness, schema-aware server-derived audit attribution, and explicit memory
  ownership diagnostics/docs. Real engine/store and cross-client recall remain
  outside disposable package/shim evidence.
- Supported-client matrix, value-free config/process topology inventory,
  duplicate provider-family detection, parent/client attribution, typed
  blockers, redaction, deterministic output, and explicit-manifest status/doctor
  path.
- Memory ownership diagnostics/docs distinguish Hermes native memory from
  shared AgentMemory context, block Mem0 without a reviewed contract, and
  prohibit migration/dual-write.
- Cutover preview/apply/restore fixtures with anchored pre/post state, protected
  evidence, multi-target preflight, JSONC comment preservation, SQLite online
  backup/integrity/schema identity, and exact restoration.
- Read-only npm registry evidence for all four exact provider pins, normalized
  from npm's dotted `dist.integrity` key, protected as mode 0600 beneath a mode
  0700 ignored state directory and bound to source commit plus Node/npm runtime.
- ADR, runbook, troubleshooting, Make help, and guidance updates.
- First-round five-provider implementation review found and drove fixes for
  publication symlink safety, topology owner spoofing, AgentMemory shim/tool
  alignment, registry SRI binding, and direct-wiring documentation. Round two
  review is required before this slice is committed.
- `make validate-documentation` remains non-zero because ignored coverage
  summaries and retained local acceptance evidence are absent; content/link
  checks passed.

## Verified commands

- `make knowledge-test`
- `make agentmemory-test`
- `make validate-agent-guidance`
- Bash syntax and ShellCheck for changed shell scripts
- Python compilation and Node syntax checks
- `git diff --check`
- `openspec validate centralize-mcp-knowledge-servers --strict`

## PARTIAL / BLOCKED tasks

- **Task 2.4 — COMPLETE:** disposable exact-package native `serve` plus adapter
  fixtures prove single-graph native behavior, native tool inventory, required
  adapter `project_path`, isolation, negative paths, and compatibility tools.
- **Task 2.4a — PARTIAL:** disposable native `migrate-state` proves preservation,
  idempotency, graph/query/path parity, and fixture rollback. PR parity and
  rollback to a captured real legacy command/path/hash identity are absent.
- **Task 2.6 — PARTIAL:** fallback/tool-schema, engine identity, post-start
  engine-down, and schema-aware attribution fixtures pass. No real tagged
  cross-client write/recall against one canonical engine has run.
- **Tasks 4.3–4.5 — BLOCKED:** current host has legacy `graphify 0.9.31`;
  `@sentropic/graphify@0.17.1` is absent. Canonical real-project graph refresh,
  router integration, and real legacy rollback require prerequisite approval.
- **Task 5.0 — PARTIAL:** source pins and fixtures are complete; real package
  installation/store schema migration evidence is not authorized.
- **Tasks 5.1, 5.2, and 5.4 — PARTIAL:** router-only bootstrap, cutover lock,
  hooks/config preservation, fallback rejection, and disposable package/shim
  evidence pass. Retained pi/project-skill evidence and real engine/store
  tagged recall/schema migration remain absent. **Task 5.3 is COMPLETE.**
- **Tasks 6.1–6.2 — PARTIAL:** regular/absent/SQLite identities, protected
  evidence, owner/mode preservation, fail-atomic publication, third-state
  refusal, and symlink rejection pass. The task wording also requires planning
  and exact restoration of symlink targets, which this implementation rejects.
- **Tasks 6.3–6.5 — COMPLETE:** JSON/JSONC/TOML/YAML/SQLite minimal removal,
  generic nested-provider detection, preservation canaries, two apply/restore
  cycles, provider/router/client scope evidence, no-process-kill behavior, and
  compensation after injected later-target publication errors pass. This does
  not claim cross-file atomicity under SIGKILL or power loss.
- **Tasks 7.3–7.5 — PARTIAL:** focused source gates and delegated fail-closed
  reviews pass. Documentation validation lacks ignored coverage/local-smoke
  artifacts; full five-provider implementation review remains outstanding.
- **Task 1.5 — COMPLETE:** the independently reviewed dependency amendment is
  integrated in the shared store. It preserves every Hermes MCP Router bridge
  field except the separately approved parallel-call declaration and limits
  this change to the named provider-child state.
- **Sections 8–9 — BLOCKED:** dependency reconciliation does not authorize live
  MCP Router/client/provider/config/process mutation. The separately bound
  prerequisite/cutover plan and operator `GO` have not been requested or granted.

## Safety statement

No live MCP Router database/configuration, supported-client config, provider
index, AgentMemory store, credential, or provider process was mutated by the
source implementation and fixture work.
