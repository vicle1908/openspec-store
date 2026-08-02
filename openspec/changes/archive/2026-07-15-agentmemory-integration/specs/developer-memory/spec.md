# developer-memory Specification

## ADDED Requirements

### Requirement: agentmemory is reachable on localhost during local development
The agentmemory REST + MCP server SHALL be reachable at `http://localhost:3111` on every developer machine after `make agentmemory-bootstrap` has completed successfully. The server SHALL bind `127.0.0.1:3111` for the REST + MCP endpoint and `127.0.0.1:3113` for the real-time viewer; neither port SHALL be published to a routable interface.

#### Scenario: Bootstrap completes on a fresh machine
- **WHEN** a developer runs `make agentmemory-bootstrap` on a supported macOS arm64 host with Node ≥ 20 installed
- **THEN** the script installs `@agentmemory/agentmemory@^0.9.27`, generates `~/.agentmemory/.env` from `infrastructure/agentmemory.env.template`, fetches the `iii-engine v0.11.2` binary to `~/.agentmemory/bin/`, and exits 0 with a printed `curl -fsS http://localhost:3111/agentmemory/health` verification command

#### Scenario: Health endpoint responds
- **WHEN** a developer curls `http://localhost:3111/agentmemory/health` after bootstrap
- **THEN** the endpoint returns HTTP 200 with a JSON body of `{"status":"ok","uptime_s":<number>}` and exits 0

#### Scenario: Viewer is loopback-only
- **WHEN** the agentmemory server starts
- **THEN** port 3113 is bound to `127.0.0.1` and a request to a non-loopback interface on `:3113` from another host on the LAN is refused at the TCP level

### Requirement: All writes are scoped to the microservices-platform project
Every write to the agentmemory server SHALL carry a `project` field with the value `microservices-platform`. The MCP shim, the agent wiring, and the bootstrap script SHALL inject this value automatically. A request that omits or overrides the `project` field SHALL be rejected with HTTP 400 and the canonical `invalid_project` error.

#### Scenario: observe carries the project namespace
- **WHEN** a hook issues `POST /agentmemory/observe` with `{"project":"microservices-platform","session_id":"<uuid>","tool":"Read","input":"<path>","output":"<body>"}`
- **THEN** the server stores the observation under the `microservices-platform` project and a subsequent `POST /agentmemory/smart-search` with `{"project":"microservices-platform","query":"<q>"}` returns the observation

#### Scenario: Observe without a project is rejected
- **WHEN** a hook issues `POST /agentmemory/observe` with no `project` field
- **THEN** the server returns HTTP 400 with `{"error":"invalid_project","message":"project is required"}` and the observation is NOT stored

### Requirement: All connected agents see at least 11 core MCP tools
Every connected agent (Cursor, Claude Code, Codex CLI, OpenCode, pi, Hermes, OpenClaw) SHALL be able to call the agentmemory MCP server and SHALL see at least the 11 core tools: `memory_recall`, `memory_save`, `memory_smart_search`, `memory_sessions`, `memory_profile`, `memory_timeline`, `memory_file_history`, `memory_relations`, `memory_export`, `memory_compress_file`, `memory_patterns`. A SessionStart health probe SHALL detect fewer than 11 tools and refuse to start the agent loop, surfacing a clear remediation message that points to `make agentmemory-doctor`.

#### Scenario: Full server exposes 53 tools
- **WHEN** the full agentmemory server is running (not the 7-tool MCP shim fallback) and an agent calls `tools/list` over MCP
- **THEN** the response contains at least 53 tools and includes all 11 core tools plus the extended set (`memory_consolidate`, `memory_claude_bridge_sync`, `memory_graph_query`, `memory_sentinel_create`, `memory_snapshot_create`, `memory_lease`, `memory_signal_send`, `memory_signal_read`, `memory_facet_query`, `memory_verify`, `memory_audit`, `memory_governance_delete`, `memory_team_share`, `memory_team_feed`, `memory_action_create`, `memory_action_update`, `memory_frontier`, `memory_next`, `memory_routine_run`, `memory_checkpoint`, `memory_mesh_sync`, `memory_sketch_create`, `memory_sketch_promote`, `memory_crystallize`, `memory_diagnose`, `memory_heal`, `memory_sentinel_trigger`)

#### Scenario: SessionStart probe detects the shim fallback
- **WHEN** only the MCP shim is running (no full server reachable via `AGENTMEMORY_URL`) and the SessionStart probe calls `tools/list`
- **THEN** the response contains exactly 7 tools, the probe exits non-zero with `remediation: "run \`make agentmemory-up\` to start the full server"`, and the agent loop aborts before any user prompt is processed

#### Scenario: Doctor surfaces a tool-count mismatch
- **WHEN** `make agentmemory-doctor` runs and the tool count is < 11
- **THEN** the output includes the line `tools: <n>/53 (expected ≥11, full server not running)` highlighted in yellow or red

### Requirement: CI sidecar provides the same contract
A sidecar `agentmemory` service SHALL be present in the `verify.yml` workflow under the smoke-test job, running `node:22-bookworm-slim` with the `.env` template baked in. The sidecar SHALL bind `0.0.0.0:3111` inside the Compose network and SHALL expose the same 11 core tools and full 53-tool surface as the developer host process. The smoke test SHALL be the only consumer of the CI sidecar.

#### Scenario: CI sidecar health is green
- **WHEN** `.github/workflows/verify.yml` runs the cross-service smoke job and the sidecar is up
- **THEN** `curl -fsS http://agentmemory:3111/agentmemory/health` returns HTTP 200 within 60 s of the sidecar starting and the smoke test proceeds

#### Scenario: CI sidecar is the only consumer
- **WHEN** the smoke test job completes (success or failure)
- **THEN** the sidecar is shut down by the workflow's `services:` block and no other workflow job references it
