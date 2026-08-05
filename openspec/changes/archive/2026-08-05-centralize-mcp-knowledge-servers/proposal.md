## Why

The workstation currently launches duplicate GitNexus, Graphify, AgentMemory, and MCP Router bridge processes from several agent clients, while MCP Router already exists as the shared aggregation boundary. The duplication wastes resources and, more seriously, creates ambiguous Graphify tool routing and isolated AgentMemory fallback stores when the canonical memory engine is unavailable.

## What Changes

- **BREAKING**: Make MCP Router the single client-facing gateway for GitNexus, Graphify, and AgentMemory across supported agents; direct client registrations for those servers are removed after compatibility and rollback gates pass.
- Keep the currently running MCP Router desktop app on latest stable `0.6.3` as
  the authoritative live adapter for coding agents, and pin its published
  stdio bridge to latest stable `@mcp_router/cli@0.2.0` rather than floating.
- Add an app-native declarative preview/apply/restore interface for the bounded
  knowledge-child definitions and coding-agent token access. Automation MUST
  use MCP Router's repository/service layer and MUST NOT edit `mcprouter.db` or
  `shared-config.json` directly.
- Upgrade and pin the three knowledge providers to their latest stable registry releases verified during planning: GitNexus `1.6.9`, `@sentropic/graphify` `0.17.1`, and AgentMemory engine/MCP `0.9.28`. Release candidates and compatibility forwarding packages are not selected as canonical providers.
- **BREAKING**: Migrate Graphify from the preserved legacy runtime/command and `graphify-out/` layout to the maintained Node.js `@sentropic/graphify@0.17.1` runtime and `.graphify/` layout, with compatibility/rebuild evidence before old artifacts are retired. Registry research found no npm `graphifyy@0.9.26` release, so rollback binds to captured command/path/hash identity rather than an impossible package pin.
- Replace the two same-tool-name Graphify MCP registrations with one multi-project Graphify server that routes by an explicit canonical `project_path` and reports unavailable or stale graphs without falling through to another repository.
- Keep one multi-repository GitNexus MCP server backed by the global registry; require explicit repository selection, current index evidence, bounded read-only exposure, and credential-safe repository metadata.
- Keep one AgentMemory MCP shim backed by the canonical engine on loopback port 3111; fail health verification when the engine is unavailable instead of accepting an isolated fallback store as shared memory.
- Separate Hermes personal/profile memory from shared project/session memory and disable or leave unconfigured overlapping memory providers unless a distinct ownership contract is documented.
- Add source-of-truth bootstrap, status, doctor, rollback, and acceptance behavior that detects duplicate direct registrations and repeated server process families without printing credential values.
- Stage live client cleanup behind an immutable redacted inventory, backup, synthetic rehearsal, explicit execution approval, client restart, cross-client smoke tests, and bounded rollback.
- Preserve the reviewed Hermes bridge fingerprint while configuring the MCP
  Router app's provider-child and token-access surfaces through its supported
  app-owned transaction path.

### Non-goals

- Reimplement GitNexus, Graphify, AgentMemory, or replace MCP Router.
- Merge GitNexus and Graphify data models or generated index artifacts.
- Delete local `.gitnexus/`, legacy `graphify-out/`, new `.graphify/`, AgentMemory data, Hermes memory, skills, hooks, sessions, or credentials without an approved migration/retention decision.
- Expose MCP Router, Graphify, AgentMemory, or GitNexus beyond loopback.
- Change application Go services, production deployment manifests, databases, or service dependencies.
- Kill unrelated client processes or rewrite a client configuration that cannot be backed up and restored exactly.
- Archive this change before implementation, focused tests, live acceptance, and retained evidence are complete.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `developer-code-intelligence`: Replace client-owned GitNexus and per-repository Graphify MCP registrations with one router-owned GitNexus server and one router-owned multi-project Graphify server, with explicit repository routing, freshness checks, collision prevention, and end-to-end verification.
- `developer-memory`: Replace per-client AgentMemory MCP shims with one router-owned shim connected to the canonical engine, distinguish engine-backed shared memory from fallback storage, and define memory-system ownership boundaries.
- `operational-readiness`: Require supported agent configurations to use the shared MCP Router gateway, detect duplicate direct knowledge-server registrations and process families, and perform an approval-gated reversible live cutover.

## Impact

- **Provider implementation repository:** `~/Developer/go-microservices`, primarily `scripts/knowledge-tools.sh`, `scripts/agentmemory-bootstrap.sh`, focused shell fixtures, Make targets, developer-memory documentation, the knowledge-graph runbook, and ADR 0007.
- **Adapter implementation repository:** `~/Developer/mcp-router`, limited to
  an app-native declarative configuration transaction that reuses server/token
  repositories, secret storage, lifecycle events, and protected backup/restore.
- **Shared planning repository:** `~/Developer/openspec-store`; this change modifies three existing capability contracts and remains active until live acceptance completes.
- **Live local configuration:** MCP Router database/configuration plus supported clients such as Hermes, Codex/ChatGPT Desktop, Cursor, Claude Code, OpenCode, Zed, Kimi, and Antigravity. Each client is inventoried and changed only during the separately approved cutover phase.
- **Generated local state:** GitNexus registry/index metadata, Graphify root graphs, AgentMemory runtime state, and ignored verification evidence are inspected and preserved; generated indexes are refreshed only through their existing single-writer controls.
- **Compatibility:** Clients continue to use MCP, but GitNexus, Graphify, and AgentMemory tools arrive through MCP Router rather than additional direct server entries. Tool names, repository selectors, and memory ownership become explicit.
- **Security:** Config and process evidence is value-free and redacted. Repository remote metadata must not expose embedded credentials. Loopback binding and existing MCP Router client authorization remain mandatory.
- **Dependencies:** Implementation is blocked until the active Hermes optimization change's MCP invariants are reconciled. Live mutation additionally requires reviewed source changes, synthetic rehearsal, backup/restore proof, and explicit execution approval.
