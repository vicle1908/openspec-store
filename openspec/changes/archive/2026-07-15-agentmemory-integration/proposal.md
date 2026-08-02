## Why

The microservices platform has 29 normative capability specs, 6 Go services, a 5-day smoke test, and a multi-agent developer experience (Cursor, Claude Code, Codex CLI, OpenCode, pi, Hermes, OpenClaw — all of which are already installed in this monorepo). Today, every one of those agents forgets the platform's decisions at the end of a session: the canonical id parsers, the `iid()` ULID rule, the Debezium connector's `heartbeat.interval.ms=10000` setting, the Temporal `ScheduleToCloseTimeout` floor, the `platform-hexagonal-enforcement` no-peer-imports rule, and the OTel-aware logging convention. The first 5 minutes of every session is spent re-deriving that context from `openspec/config.yaml`, the archived `precise-changes.md`, and the code itself. [rohitg00/agentmemory](https://github.com/rohitg00/agentmemory) — a battle-tested persistent-memory engine (25.1k★, 1,423+ tests, 53 MCP tools, 95.2% R@5 on LongMemEval-S, pinned to `iii-engine v0.11.2`) — eliminates that re-derivation by silently capturing every tool use, compressing + embedding it locally, and injecting the right context on the next SessionStart. This change wires it into this monorepo at the developer-experience layer, above the services, without touching any Go service code, without adding a Docker service, and without breaking the existing OpenSpec rules of the road.

## What Changes

- Install `agentmemory` as a **host process** (NOT a Docker service). The server runs on `localhost:3111` (REST + MCP) and `localhost:3113` (real-time viewer, loopback-only); the `iii-engine v0.11.2` binary auto-fetches to `~/.agentmemory/bin/`.
- Add a **one-shot developer bootstrap** (`make agentmemory-bootstrap`) that detects the host OS/arch, runs `npx @agentmemory/agentmemory@latest`, generates `~/.agentmemory/.env` from a template, and wires all 7 supported agents in a single command.
- Add five new Make targets at the repo root: `agentmemory-up`, `agentmemory-down`, `agentmemory-doctor`, `agentmemory-reset`, and `agentmemory-bootstrap` — all gated on `~/.agentmemory/.env` being present and idempotent on re-run.
- Wire **7 agents** to the same memory server: Cursor (MCP only — no Cursor Desktop hooks), Claude Code (12 hooks + plugin + MCP), Codex CLI (6 hooks + plugin + MCP, plus the `connect codex --with-hooks` workaround for the silent Codex Desktop issue #16430), OpenCode (22 hooks + plugin + MCP), pi (native plugin + MCP), Hermes (memory-provider plugin + MCP), and OpenClaw (native plugin + MCP, with optional deeper slot integration). Each agent writes into the same `project=microservices-platform` namespace tagged with its own `AGENT_ID`.
- Add an **OpenSpec traceability delta** that requires every `PostToolUse` hook payload that touches a file under `openspec/` to carry the active change name, artifact path, and scenario ID, and to record an `agentmemory://observations/<id>` reference in `verification/traceability.yaml` for each captured observation that maps to a verification ID.
- Add a **`memory_smart_search` contract test** to the cross-service smoke stack that asserts at least 11 MCP tools are reachable (the 7-tool shim fallback is a silent capability reduction that the test SHALL detect) and that a seeded fixture observation round-trips through hybrid search.
- Add a **CI sidecar service** (`agentmemory` container in `.github/workflows/ci.yml`) running `node:22-bookworm-slim` with the env template baked in, so the smoke test runs against a real server in CI without violating the "host process" choice on developer machines.
- Document the new flow in the root `README.md` under a "Developer Memory" section (~80 lines): install, bootstrap, verify, troubleshoot.

No existing Go service code, REST contract, Protobuf, or database schema changes. No `openspec/config.yaml` rule changes. No new Go module. The change is a developer-experience layer that sits above the platform and is consumed through MCP + hooks + skills.

## Capabilities

### New Capabilities

- `developer-memory`: the agentmemory server SHALL be reachable on `localhost:3111` during local development and via the CI sidecar during `make test-e2e`; SHALL scope every write to `project=microservices-platform`; SHALL expose ≥11 core MCP tools to every connected agent and all 53 tools when the full server is running; SHALL run a SessionStart health probe that aborts the agent loop if fewer than 11 tools are visible (the 7-tool shim fallback is a silent regression that this check SHALL surface).
- `agentmemory-host-runtime`: the agentmemory server SHALL be installed as a host process, NOT a Docker service; SHALL pin `iii-engine` to `v0.11.2`; SHALL auto-fetch the engine to `~/.agentmemory/bin/` on first run; SHALL persist state under `~/.agentmemory/` (which is outside the repo and survives `make clean`); SHALL bind the viewer to `127.0.0.1:3113` only and SHALL NOT publish `:3113` outside the host; SHALL be reaped by `make agentmemory-down` via a pidfile at `~/.agentmemory/run/agentmemory.pid`.
- `agentmemory-mcp-wiring`: each of the 7 supported agent configurations SHALL contain a non-destructive `mcpServers.agentmemory` entry pointing at `npx -y @agentmemory/mcp` with `AGENTMEMORY_URL` and `AGENT_ID` set; the 15 upstream skills SHALL be installed for every agent via `npx skills add rohitg00/agentmemory -y -a '*'`; the `~/.agentmemory/.env` file SHALL be generated from `infrastructure/agentmemory.env.template` and SHALL NOT be committed; the bootstrap script SHALL be idempotent on re-run.
- `agentmemory-feature-flags`: the `.env` template SHALL set `AGENTMEMORY_TOOLS=all`, `GRAPH_EXTRACTION_ENABLED=true`, `SNAPSHOT_ENABLED=true`, `CONSOLIDATION_ENABLED=true` (default-on), `AGENTMEMORY_SLOTS=memory` (slot name, not boolean), `AGENTMEMORY_REFLECT=true`, `AGENTMEMORY_INJECT_CONTEXT=true`, `LESSON_DECAY_ENABLED=true`, and `AGENTMEMORY_AGENT_SCOPE=shared`; SHALL NOT set `AGENTMEMORY_AUTO_COMPRESS=true` (Stop-hook only — controls cost); SHALL NOT set `AGENTMEMORY_ALLOW_AGENT_SDK=true` (Stop-hook recursion risk per the upstream README); SHALL default the LLM provider to a local Ollama server at `http://localhost:11434/v1` with `qwen2.5-coder:7b` (zero-cost path).
- `agentmemory-bootstrap-script`: the top-level `make agentmemory-bootstrap` target SHALL detect the host OS/arch, run the agentmemory install, generate the `.env` from the template (prompting for any required LLM provider key when the developer opts out of Ollama), wire the calling agent via `npx skills add -y -a '*'`, and print the verification curl command; the script SHALL be re-runnable and SHALL NOT clobber existing wiring.

### Modified Capabilities

- `platform-verification`: delta requirement — any `PostToolUse` hook payload that touches a file under `openspec/` SHALL carry the active change name, the artifact path, and the scenario ID; the verification harness SHALL record an `agentmemory://observations/<id>` reference in `verification/traceability.yaml` for each captured observation that maps to a verification ID. This delta closes the gap where hook-driven captures have no traceability link to the OpenSpec system that authorises the change.
- `platform-extensibility`: delta requirement — the developer-experience memory layer is an OpenSpec-managed addition; the `Makefile` target list is a contract surface and `agentmemory-*` targets are first-class; the `.env` template path (`infrastructure/agentmemory.env.template`) is a contract surface and SHALL NOT be moved without an ADR.

## Impact

### New code (root + scripts)

- `Makefile` — adds 5 targets: `agentmemory-bootstrap`, `agentmemory-up`, `agentmemory-down`, `agentmemory-doctor`, `agentmemory-reset`; extends the `help` target with the new lines.
- `scripts/agentmemory-bootstrap.sh` — detects `uname -s`/`uname -m`, prereqs Node ≥ 20, runs `npx -y @agentmemory/agentmemory@latest`, renders `~/.agentmemory/.env` from the template, runs `npx skills add rohitg00/agentmemory -y -a '*'`, prints `curl -fsS http://localhost:3111/agentmemory/health` for verification.
- `scripts/agentmemory-up.sh` — `nohup npx @agentmemory/agentmemory > ~/.agentmemory/run/agentmemory.log 2>&1 &` with pidfile at `~/.agentmemory/run/agentmemory.pid`; waits for `:3111/agentmemory/health` to return 200 with a 15 s ceiling.
- `scripts/agentmemory-down.sh` — reads the pidfile, sends `SIGTERM`, waits 5 s, escalates to `SIGKILL`, leaves state in `~/.agentmemory/data/` intact.
- `scripts/agentmemory-doctor.sh` — checks Node version, checks `iii` binary, checks `:3111` reachability, checks `:3113` reachability, checks `.env` presence, checks `AGENTMEMORY_SECRET` setting, prints a single green/yellow/red table.
- `scripts/agentmemory-reset.sh` — `agentmemory-down` + delete `~/.agentmemory/run/`; preserve `~/.agentmemory/data/` for recovery.
- `scripts/wait-for-agentmemory.sh` — used by CI and the smoke test; loops on `curl -fsS $AGENTMEMORY_URL/agentmemory/health` with a configurable timeout.
- `infrastructure/agentmemory.env.template` — the B+ feature-flag set; placeholders for `OPENAI_API_KEY` (used only if the developer opts out of Ollama); `EMBEDDING_PROVIDER=local`; `AGENTMEMORY_AGENT_SCOPE=shared`.

### New code (agent configs — files at repo root, NOT in `.claude/`/`.codex/`-style hidden dirs, to match the upstream `connect <agent>` convention)

- `.cursor/mcp.json` — merges `mcpServers.agentmemory` with `AGENTMEMORY_URL` and `AGENT_ID=cursor`.
- `.claude/settings.json` — registers 12 hooks, 15 skills, and the MCP server via the `/plugin install` flow documented in the upstream README; `AGENT_ID=claude-code`.
- `.codex/config.toml` — registers the MCP server, 6 hooks, and 15 skills; `AGENT_ID=codex-cli`. Includes the comment that Codex Desktop hooks are silent until upstream #16430 lands, and the `agentmemory connect codex --with-hooks` workaround.
- `opencode.json` — registers MCP + the `plugin/opencode/agentmemory-capture.ts` plugin (22 hooks); `AGENT_ID=opencode`.
- `.pi/agent/extensions/agentmemory/` — copied from `integrations/pi` (or, if upstream is not vendored, installed via `npx skills add -y -a pi`); `AGENT_ID=pi`.
- `integrations/hermes/` — mirrors `~/.hermes/config.yaml` with `mcp_servers.agentmemory` and `memory.provider: agentmemory`; `AGENT_ID=hermes`.
- OpenClaw MCP config — mirrors the upstream snippet with `AGENT_ID=openclaw`; optional deeper `plugins.slots.memory = "agentmemory"` integration deferred to a follow-up.

### New code (CI + tests)

- `.github/workflows/ci.yml` — adds an `agentmemory` service container running `node:22-bookworm-slim` with the `.env` template baked in; sets `AGENTMEMORY_URL=http://agentmemory:3111` for the smoke test job.
- `tests/cross-service-smoke/` — adds a `TestAgentMemoryContract` that:
  - asserts `GET $AGENTMEMORY_URL/agentmemory/health` returns 200,
  - asserts `POST $AGENTMEMORY_URL/agentmemory/session/start` returns a session id,
  - asserts `POST $AGENTMEMORY_URL/agentmemory/observe` accepts the fixture observation,
  - asserts `POST $AGENTMEMORY_URL/agentmemory/smart-search` returns the fixture observation with R@1 hit on the seeded query,
  - asserts the MCP tool count reported by `GET $AGENTMEMORY_URL/agentmemory/status` is ≥ 11.
- `tests/agentmemory-fixtures/` — a small corpus of 3 session transcripts (an order-creation flow, a debounce-of-customer-merge flow, and a Temporal replay test) that the contract test seeds via `import-jsonl` style endpoints. These are committed to the repo for repeatability.

### New code (documentation)

- `README.md` (root) — new "Developer Memory" section: install, bootstrap, verify, troubleshoot, links to the upstream README and INSTALL_FOR_AGENTS.md.
- `docs/agentmemory.md` — deeper writeup: which 53 tools are exposed, what each hook captures, the `AGENT_ID` tagging scheme, the `AGENTMEMORY_AGENT_SCOPE=shared` policy, the rollback procedure.
- `docs/agentmemory-troubleshooting.md` — port-conflict table, the EACCES fix for `npm install -g` on macOS, the Codex Desktop workaround, the WSL2 note for Windows.

### Modified code

None of the Go service code changes. The change is additive at the developer-experience layer. The only "modified" files in the repo are:

- `Makefile` — additive (5 new targets, 5 new help lines).
- `README.md` — additive ("Developer Memory" section).
- `verification/traceability.yaml` (if it exists; otherwise, deferred) — additive (`agentmemory://` references).
- `openspec/config.yaml` — NO change; the existing rules cover the addition.

### Dependencies (new)

All version pins below were re-verified against the upstream `package.json`, the `iii-hq/iii` release page, the Node release schedule, and the Ollama model library on **2026-07-15**. Versions in parentheses are the latest stable observed at the time of writing; the `^` floor below each is the minimum version known to satisfy the contract.

- `@agentmemory/agentmemory@0.9.27` — pinned exactly, NOT `^0.9.27`; verified against upstream `package.json` on **2026-07-15**. Using `^0.9.27` would allow `0.10.x` installs that may not be compatible with `iii-engine v0.11.2`. The bootstrap script SHALL pin to `@agentmemory/agentmemory@0.9.27` exactly.
- `iii-engine v0.11.2` — pinned exactly; do not use `v0.11.6+` because the upstream README states the new sandbox-everything model is not yet supported. Verified against `iii-hq/iii` releases on **2026-07-15**.
- Node.js `>=20` (we have 26.5 ✓); the bootstrap script verifies and refuses to install on older Node.
- `@xenova/transformers` — auto-installed by agentmemory when `EMBEDDING_PROVIDER=local`; the local `all-MiniLM-L6-v2` model ships with the package.
- Ollama `>=0.5.0` with `qwen2.5-coder:7b` (≈4.7 GB) — the zero-cost default for the LLM-backed compression pass; optional but recommended.
- (Optional, paid) `OPENROUTER_API_KEY` with `deepseek/deepseek-v4-pro` as a higher-quality alternative (~$0.46 per 35h of active use per the upstream benchmark).

### Rollout approach

5 phases, ~2 weeks of incremental rollout. Each phase has its own feature flag and its own rollback boundary.

1. **Phase 1 — Infrastructure (day 1–2)**: `scripts/agentmemory-*.sh`, `infrastructure/agentmemory.env.template`, the 5 `Makefile` targets, the README "Developer Memory" section. Verify on this machine.
2. **Phase 2 — Cursor + Claude Code (day 3–4)**: `.cursor/mcp.json`, `.claude/settings.json`. Verify in this very session that 53 tools are visible.
3. **Phase 3 — Codex CLI + OpenCode (day 5–7)**: `.codex/config.toml` + the `connect codex --with-hooks` workaround, `opencode.json` + the 22-hook plugin.
4. **Phase 4 — pi, Hermes, OpenClaw (day 8–10)**: per-agent integration dirs; optional deeper slot integration for Hermes (`memory.provider`) and OpenClaw (`plugins.slots.memory`).
5. **Phase 5 — OpenSpec traceability + CI sidecar (day 11–14)**: `platform-verification` delta, CI service container, `TestAgentMemoryContract`, the fixture corpus, OpenSpec change → archive.

### Rollback approach

The whole change is contained in `Makefile` + `scripts/` + `infrastructure/` + the 7 agent config files + the CI sidecar + the smoke test addition + the README section + the two doc files. A single revert PR removes it. Rollback procedure:

1. `make agentmemory-down` — stops the host process via the pidfile.
2. Revert the 5 Make targets, the 5 scripts, the `.env` template, the 7 agent config files, the CI sidecar lines, the smoke test addition, the README section, and the two doc files.
3. Optional: `make agentmemory-reset` to remove `~/.agentmemory/run/` while preserving `~/.agentmemory/data/` for recovery.
4. **Memories are NOT deleted on rollback.** `memory_audit` provides a complete record of what was captured if rollback is triggered by a privacy incident — the audit log lives in the named state directory and can be diffed against the project scope before any explicit `memory_governance_delete` is run.

The `agentmemory` integration is one OpenSpec change but two real boundaries: the host process (dev-machine only) and the agent wiring (committed to the repo). Rollback affects both at once and reverts the repo to its pre-change state without losing captured memory.
