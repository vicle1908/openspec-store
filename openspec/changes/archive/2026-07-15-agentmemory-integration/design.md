## Context

The microservices monorepo is a Go-only platform: 6 services (one mature — `order-service` — plus 4 newer under `services/` and a shared `platform/` Go module), 29 normative capability specs, a 5-day cross-service smoke test, and a multi-agent developer experience with 11 agent config directories already present at the repo root. The project operates on the OpenSpec spec-driven workflow with strict rules (SHALL/MUST, four-hash `#### Scenario:`, every requirement testable, dependency versions verified against current official documentation on the day the change is applied).

`rohitg00/agentmemory` (25.1k★, 1,423+ tests, 53 MCP tools, 95.2% R@5 on LongMemEval-S, Apache-2.0) is a persistent-memory engine for AI coding agents. It runs on top of the `iii` engine (a worker/function/trigger runtime), pins `iii-engine v0.11.2` exactly, exposes a REST + MCP API on port 3111, and a real-time viewer on port 3113. It auto-captures every tool use via per-agent lifecycle hooks (12 for Claude Code, 6 for Codex CLI, 22 for OpenCode, MCP-only for Cursor Desktop), compresses + embeds observations locally with the bundled `all-MiniLM-L6-v2` model, and injects the right context on the next SessionStart within a configurable token budget. The 53-tool MCP surface spans search, governance, snapshots, leases, signals, sentinels, mesh sync, facets, and verify; the 7-tool shim fallback is a silent regression that an agent will not notice without an explicit health probe.

The project already invests heavily in the developer-experience layer (OpenSpec, `make help`, cross-service smoke, OTel-aware logger, ADR-driven admission for vendor SDKs). The integration must add the agentmemory layer without violating any of the existing OpenSpec rules of the road, must not add a Docker service (the user explicitly chose host-process deployment), and must not break the project's hard arm64 requirement even though agentmemory runs on the host (not in a container).

## Goals / Non-Goals

**Goals:**

- Install and run agentmemory as a host process (not a Docker service) on every developer machine, with a one-shot `make agentmemory-bootstrap` target that detects OS/arch, pins the engine, generates the `.env`, and wires all 7 supported agents in a single command.
- Expose the full 53-tool MCP surface plus the 15 upstream skills to every connected agent, scoped to a single `project=microservices-platform` namespace, tagged per-agent with `AGENT_ID`.
- Wire all 7 supported agents (Cursor, Claude Code, Codex CLI, OpenCode, pi, Hermes, OpenClaw) with non-destructive merges into each agent's native config file, using the standard `mcpServers.agentmemory` block from the upstream README.
- Default to the B+ feature tier (Production + slots + reflect + inject-context) with `AGENTMEMORY_TOOLS=all`, `GRAPH_EXTRACTION_ENABLED=true`, `SNAPSHOT_ENABLED=true`, `AGENTMEMORY_SLOTS=memory` (slot name, not boolean), `AGENTMEMORY_REFLECT=true`, `AGENTMEMORY_INJECT_CONTEXT=true`, `LESSON_DECAY_ENABLED=true`, `AGENTMEMORY_AGENT_SCOPE=shared`, and a local Ollama server (`qwen2.5-coder:7b`) as the zero-cost LLM provider.
- Detect the 7-tool MCP shim fallback at SessionStart and refuse to start the agent loop when fewer than 11 tools are visible, surfacing `make agentmemory-doctor` as the remediation path.
- Provide a CI sidecar service container that brings up the same agentmemory contract in `.github/workflows/verify.yml` for the cross-service smoke test, so the contract is verifiable in CI without violating the host-process choice on developer machines.
- Add a `platform-verification` delta that requires every `PostToolUse` hook payload touching a file under `openspec/` to carry the active change name, artifact path, and scenario ID, and to record an `agentmemory://observations/<id>` reference in `verification/traceability.yaml` for each captured observation that maps to a verification ID.
- Add a `platform-extensibility` delta that requires the agentmemory integration to be treated as first-class OpenSpec capabilities and to have a 5-point admission ADR at `docs/adr/0007-developer-memory-layer.md`.

**Non-Goals:**

- Adding agentmemory to any `deploy/docker-compose.*.yaml` file (host-process deployment only).
- Modifying any Go service code (`order-service`, `services/*`, `platform/*`).
- Modifying `openspec/config.yaml` rules (the existing rules already cover the addition).
- Setting `AGENTMEMORY_AUTO_COMPRESS=true` (Stop-hook-only, controls cost).
- Setting `AGENTMEMORY_ALLOW_AGENT_SDK=true` (Stop-hook recursion risk per the upstream README; opt-in only).
- Setting `CLAUDE_MEMORY_BRIDGE=true` (deferred to a follow-up; not in B+ scope).
- Setting `OBSIDIAN_AUTO_EXPORT=true` (out of scope for the dev-experience layer).
- Wiring Windows native (Zed pre-1.3.x, native Windows agentmemory install); Windows is documented as WSL2-only.
- Wiring Droid (Factory.ai), Continue.dev, Cline CLI, Roo Code, Goose, Aider, Warp, Qwen Code, Kiro, Antigravity — these are supported by upstream but deferred to a follow-up to keep Phase 1 tractable.
- Adopting the `iii-sandbox` worker (sandbox-everything refactor is mid-flight on the engine per the upstream README).
- Adopting the `iii-pubsub` worker for multi-instance memory (only relevant for a remote agentmemory server, which is out of scope for the host-process deployment).
- Replacing the existing `platform-observability` (OTel + Grafana LGTM) layer with agentmemory's `iii-observability` worker — the two coexist, and the project keeps its own OTel Collector as the single egress for service telemetry.

## Decisions

### Decision 1: Host-process deployment, not Docker

**Choice**: Run agentmemory as a host process. State lives in `~/.agentmemory/`. The engine binary is fetched to `~/.agentmemory/bin/`. There is no `agentmemory` service in any `deploy/docker-compose.*.yaml` file.

**Why**: The user explicitly chose host deployment in the explore phase. Upstream's own README treats `npx @agentmemory/agentmemory` as the canonical install path. The host-process choice means the server is owned by the developer, not by the test stack; it survives `make clean`; and it does not consume a slot in the project's `make verify-images` gate (which is for *container* images).

**Alternatives considered**:
- **Docker Compose service**: rejected because the user chose host. Would have added an arm64 image-pinning obligation to `scripts/verify-images.sh` and would have made the agentmemory state part of the volume-managed test stack, which is wrong for a long-lived developer-experience tool.
- **Hybrid (dev on host, CI in Compose)**: rejected because the smoke test in CI uses the same `localhost:3111` contract as the dev experience. A sidecar service container in `.github/workflows/verify.yml` is the cleanest way to provide that contract in CI without adding a service to the project's own Compose files.

### Decision 2: Pinned `iii-engine v0.11.2`

**Choice**: Pin `iii-engine` to `v0.11.2` exactly. Override with `AGENTMEMORY_III_VERSION` is permitted but requires the developer to acknowledge the upstream README's caveat that `v0.11.6+` introduces a new sandbox-everything model that agentmemory has not been refactored for.

**Why**: The upstream README states the pin explicitly and warns against the newer engine. The bootstrap script must refuse to install `v0.11.6+` without explicit confirmation. A future PR can lift the pin once the upstream refactor lands; for now, the pin is a contract.

**Alternatives considered**:
- **Unpinned (latest stable)**: rejected because the upstream README is unambiguous that the protocol is mid-flight.
- **Pin v0.11.0**: rejected because the upstream `iii-sdk` line targets `^0.11.0` and `v0.11.2` is the version agentmemory was tested against.

### Decision 3: B+ feature tier, not "kitchen sink" or "core"

**Choice**: B+ = full server (53 tools, not 7) + `AGENTMEMORY_TOOLS=all` + `GRAPH_EXTRACTION_ENABLED=true` + `SNAPSHOT_ENABLED=true` + `CONSOLIDATION_ENABLED=true` (default-on) + `AGENTMEMORY_SLOTS=memory` + `AGENTMEMORY_REFLECT=true` + `AGENTMEMORY_INJECT_CONTEXT=true` + `LESSON_DECAY_ENABLED=true`. **Not** `AGENTMEMORY_AUTO_COMPRESS=true` (Stop-hook only). **Not** `AGENTMEMORY_ALLOW_AGENT_SDK=true` (Stop-hook recursion risk). **Not** `CLAUDE_MEMORY_BRIDGE=true` or `OBSIDIAN_AUTO_EXPORT=true`.

**Why**: The user explicitly chose B+ in the explore phase. The B+ tier delivers the cognitive layer (recall, smart-search, graph, snapshots, slots, reflect, decay) without paying the Stop-hook recursion cost or the 5–10× token-spend multiplier of `AGENTMEMORY_AUTO_COMPRESS=true`. The `shared` agent scope (default) keeps the cross-agent context value intact while preserving per-agent auditability.

**Alternatives considered**:
- **Kitchen sink (C tier)**: rejected because `AGENTMEMORY_ALLOW_AGENT_SDK=true` and `AGENTMEMORY_AUTO_COMPRESS=true` both have well-documented risks in the upstream README. The user explicitly opted out of the "all features" reading that would include these.
- **Core (A tier, 7-tool shim only)**: rejected because the user explicitly chose B+ to get the full cognitive layer.

### Decision 4: Local Ollama (`qwen2.5-coder:7b`) as the default LLM provider

**Choice**: Default the LLM provider to a local Ollama server at `http://localhost:11434/v1` with `qwen2.5-coder:7b` as the model. `OPENAI_API_KEY=ollama` (any non-empty placeholder), `OPENAI_BASE_URL=http://localhost:11434/v1`, `OPENAI_MODEL=qwen2.5-coder:7b`. Bootstrap script detects Ollama with a 2 s curl probe; absence is a yellow warning, not a failure.

**Why**: Zero-cost path that runs entirely on the developer's hardware. The upstream README recommends `qwen2.5-coder:7b` for code-shaped sessions. The bootstrap script should not require an LLM key to install (the server can run with the no-op LLM provider, just with reduced capability), so the warning is informational.

**Alternatives considered**:
- **OpenRouter (DeepSeek-V4-Pro)**: ~$0.46 per 35h of active use, higher quality. Acceptable as an override but not the default because the zero-cost path is the right onboarding default.
- **OpenAI gpt-4o-mini**: ~$5 per 35h, premium quality. Out of budget for always-on background work.
- **No LLM (no-op)**: BM25-only, no semantic compression. Degrades the B+ feature tier significantly. Acceptable for a one-day trial; not a good default.

### Decision 5: One-shot bootstrap, idempotent re-runs, no Compose integration

**Choice**: `make agentmemory-bootstrap` is the single entry point. It is a shell script at `scripts/agentmemory-bootstrap.sh` that:
1. Detects OS/arch, refuses to run on Windows without WSL2.
2. Verifies Node ≥ 20.
3. Downloads the pinned `iii-engine` tarball for the host OS/arch to `~/.agentmemory/bin/`.
4. Runs `npx -y @agentmemory/agentmemory@0.9.27` once globally (exact pin, NOT `@latest` — see Decision 2); the bare `agentmemory` command is on PATH after this.
5. Renders `~/.agentmemory/.env` from `infrastructure/agentmemory.env.template` (chmod 600).
6. Runs `npx skills add rohitg00/agentmemory -y -a '*'` to install the 15 skills in every installed agent.
7. Merges the `mcpServers.agentmemory` entry into each agent's native config file (Cursor, Claude Code, Codex CLI, OpenCode, pi, Hermes, OpenClaw), preserving any existing entries.
8. Prints a green `curl -fsS http://localhost:3111/agentmemory/health` for verification.

The script is idempotent. Re-running reports "agentmemory already bootstrapped" and exits 0 unless `--reset-env` is passed (which backs up the existing `.env` to `~/.agentmemory/.env.bak-<ts>` and regenerates).

**Why**: One entry point is the only way to guarantee every developer on the team has the same agentmemory version, the same pinned engine, the same `.env` feature flags, and the same MCP wiring. The script is a single artifact that can be reviewed in a PR and tested with `make agentmemory-bootstrap && make agentmemory-doctor`.

**Alternatives considered**:
- **Per-agent install scripts**: rejected because it spreads the install logic across 7 files and makes upgrades error-prone.
- **Documented manual install (README only)**: rejected because the user explicitly chose `make` target in the explore phase.

### Decision 6: Shared agent scope, not isolated

**Choice**: `AGENTMEMORY_AGENT_SCOPE=shared` (default). Writes are tagged with `agentId` but recall does not filter by it. Every agent sees every other agent's writes; the audit log records who said what.

**Why**: The user explicitly chose shared in the explore phase. The cross-agent context is the *point* of agentmemory — architect can see what developer noted, reviewer can see what researcher found, and every row records the origin. The audit log + per-agent `?agentId=<role>` query parameter provide the per-role view when needed, without paying the cost of full isolation (which would break the "one memory across agents" pitch).

**Alternatives considered**:
- **Isolated scope**: rejected because it would prevent the cross-agent recall that the user wants. A developer can opt into isolated mode by editing `~/.agentmemory/.env`; the bootstrap script documents this in a comment.

### Decision 7: SessionStart probe enforces ≥ 11 tools

**Choice**: The `agentmemory-mcp-wiring` capability includes a SessionStart health probe that calls `tools/list` over MCP and aborts the agent loop with a clear remediation message if fewer than 11 tools are visible.

**Why**: The 7-tool MCP shim fallback is a silent regression: the shim returns 7 tools when the full server is unreachable, and an agent will not notice the difference without an explicit check. The probe turns a silent capability reduction into a hard failure with a `make agentmemory-doctor` remediation path.

**Alternatives considered**:
- **Lazy detection (only on the first tool call)**: rejected because by then the agent has already started processing a user prompt, and the failure mode is confusing.
- **Doctor-only check (no SessionStart probe)**: rejected because the developer would not see the issue until they ran `make agentmemory-doctor` manually.

### Decision 8: `openspec` deltas on `platform-verification` and `platform-extensibility`

**Choice**: Two delta specs, no breaking changes to existing requirements.

**`platform-verification` delta (ADDED)**:
- `PostToolUse` hook payloads that touch a file under `openspec/` SHALL carry `openspec_change`, `openspec_artifact`, `openspec_scenario`.
- `verification/traceability.yaml` SHALL record `agentmemory://observations/<id>` references for in-scope observations.
- The release gate SHALL run `scripts/agentmemory-doctor.sh` and SHALL fail the release if the doctor exits non-zero.

**`platform-extensibility` delta (ADDED)**:
- The 5 agentmemory capabilities are first-class OpenSpec capabilities and SHALL go through the OpenSpec workflow.
- A new ADR SHALL be authored at `docs/adr/0007-developer-memory-layer.md` documenting the 5-point admission test.

**Why**: The hook-driven captures have no traceability link to the OpenSpec system that authorises the change. The delta closes that gap. The extensibility delta treats the agentmemory integration as a first-class capability so future changes go through the same workflow as any other change in the repo.

**Alternatives considered**:
- **No deltas (purely additive specs)**: rejected because the hook payload contract is a normative requirement that belongs in `platform-verification` (which is the spec for "what verification evidence is required").
- **A new `agentmemory-verification` capability**: rejected because the verification contract is cross-cutting (it touches every hook payload, not just agentmemory-internal events) and belongs in the existing verification spec.

### Decision 9: CI sidecar uses `node:22-bookworm-slim`

**Choice**: The CI sidecar in `.github/workflows/verify.yml` runs `node:22-bookworm-slim` with the `.env` template baked in. The image is hosted on Docker Hub; the sidecar binds `0.0.0.0:3111` inside the Compose network; the smoke test job sets `AGENTMEMORY_URL=http://agentmemory:3111`.

**Why**: `node:22-bookworm-slim` is the official upstream-recommended base for agentmemory. The image exposes `linux/arm64` and `linux/amd64` manifests (verified against Docker Hub on 2026-07-15), satisfying the project's hard arm64 requirement. The sidecar is the only consumer of the image in CI; the project's own `deploy/docker-compose.*.yaml` files do not pull it (host-process deployment), so `make verify-images` does not need to verify it.

**Alternatives considered**:
- **Pull a pre-built agentmemory image**: rejected because the upstream README explicitly states "no pre-built agentmemory image required" and provides `node:22-bookworm-slim` as the base.
- **Skip the CI sidecar and let the smoke test skip memory assertions**: rejected because the cross-service smoke test is the only place to verify the contract end-to-end.

### Decision 10: 5-point ADR mirrors `0004-optional-infrastructure.md`

**Choice**: The new ADR at `docs/adr/0007-developer-memory-layer.md` mirrors the structure of `order-service/docs/adr/0004-optional-infrastructure.md`. The architecture test for vendor-SDK admission is extended to confirm the ADR exists with the five required sections.

**Why**: The existing 5-point test is the project's canonical admission format. A different format for this ADR would be inconsistent and would not be picked up by the architecture test. The extension to the test is one line and reuses the existing test infrastructure.

**Alternatives considered**:
- **No ADR**: rejected because `platform-extensibility` already requires every vendor SDK (and every "infrastructure") to have an ADR.
- **A lighter ADR (3 points)**: rejected because the project's existing convention is 5 points.

## Risks / Trade-offs

- **[R1] Engine protocol churn** — `iii-engine v0.11.2` is pinned, but the upstream is mid-refactor on `v0.11.6+` for the new sandbox-everything model. → **Mitigation**: pin is in `agentmemory-feature-flags` spec; future change lifts it. The bootstrap script warns on any version other than `0.11.2`.
- **[R2] `AGENTMEMORY_ALLOW_AGENT_SDK` Stop-hook recursion** — the upstream README explicitly disables this by default and warns that it caused unbounded Stop-hook recursion. → **Mitigation**: never set this flag in the template; the `agentmemory-feature-flags` spec requires it to be absent; CI doctor asserts it.
- **[R3] LLM provider is not running** — the Stop-hook compression pass becomes a no-op if Ollama is not running or no API key is set. → **Mitigation**: yellow warning, not a failure; `make agentmemory-doctor` reports the state; the spec accepts reduced capability.
- **[R4] `import-jsonl` is a one-shot, but `cleanupPeriodDays: 30` deletes old Claude Code transcripts** — pre-existing sessions older than 30 days are already gone before any import. → **Mitigation**: the auto-capture hooks are the default path; the import-jsonl is documented in `docs/agentmemory.md` as a recovery tool, not a primary path.
- **[R5] Agent memory state is OUTSIDE the repo** — `~/.agentmemory/` is on the developer's home directory; `git status` cannot see it. → **Mitigation**: the bootstrap script adds `~/.agentmemory/` to the developer's global gitignore; `make agentmemory-doctor` checks that the state is present; `make agentmemory-reset` is the explicit destructive path.
- **[R6] Multi-agent shared mode may surface cross-agent context that the developer did not write** — Cursor, Claude Code, and Codex CLI all see each other's writes. → **Mitigation**: `?agentId=<role>` query parameter scopes any single call; per-row `agentId` in the audit log records origin; `memory_governance_delete` is the deletion path. Documented in `docs/agentmemory.md`.
- **[R7] 53 tools is a lot** — 53 MCP tools in the agent's tool palette is a real cognitive load. → **Mitigation**: the 11 core tools cover ≥95% of session-to-session recall; the 42 extended tools are organised by category in the upstream `agentmemory-mcp-tools` reference skill; the SessionStart probe ensures the full set is available when the developer wants it.
- **[R8] Codex Desktop silent hooks** — `openai/codex#16430` blocks plugin-local `hooks.json` dispatch on Codex Desktop, so the plugin is half-broken there. → **Mitigation**: `agentmemory connect codex --with-hooks` mirrors the hooks into `~/.codex/hooks.json`; the bootstrap script runs this on every invocation; the `agentmemory-mcp-wiring` spec requires the mirror to be in place.
- **[R9] `iii-sandbox` is not adopted** — code that comes out of `memory_recall` runs in the agent's process, not an isolated microVM. → **Mitigation**: out of scope for B+; documented as a follow-up.
- **[R10] `iii-pubsub` is not adopted** — multi-instance memory is not supported; the host-process server is single-instance. → **Mitigation**: out of scope for the host-process deployment; a future change adds `iii-pubsub` and `iii-cron` and a `deploy/docker-compose.agentmemory.yaml` overlay for teams that want a shared team memory.
- **[R11] The bootstrap script is a shell script, not a Go binary** — every developer is running it from the repo, and it is in shell. → **Mitigation**: the script is reviewed in the PR; `shellcheck` runs in CI (the existing project already runs `shellcheck` on every PR per `platform-verification`); the script is idempotent and re-runnable.
- **[R12] The Makefile `help` target grows** — 5 new `agentmemory-*` targets are added to the help text. → **Mitigation**: the help text is alphabetised; the `platform-extensibility` delta requires the help target to be updated in the same PR as any new target.
- **[R13] OpenSpec change archive may take a long time** — 5 new capabilities + 2 deltas = 7 spec files, all with full `#### Scenario:` blocks. → **Mitigation**: the specs are authored up-front in this proposal; the archive step is a `git mv`; `openspec validate --strict --all` is the gate.

## Migration Plan

The change is additive at the developer-experience layer; there is no data migration.

**Day 0 (this PR)**: Author the change in OpenSpec (proposal + 7 specs + design + tasks), merge with `openspec validate --strict --all` green.

**Day 1 (Phase 1)**: Land the infrastructure:
- `scripts/agentmemory-{bootstrap,up,down,doctor,reset,wait-for}.sh` (~600 lines of bash total).
- `infrastructure/agentmemory.env.template` (~30 lines).
- 5 `Makefile` targets and 5 `make help` lines.
- Root `README.md` "Developer Memory" section (~80 lines).
- `docs/agentmemory.md` and `docs/agentmemory-troubleshooting.md` (~250 lines combined).
- `docs/adr/0007-developer-memory-layer.md` (the 5-point ADR).
- Verify on this developer's machine.

**Day 3 (Phase 2)**: Land Cursor + Claude Code wiring:
- `.cursor/mcp.json` (merge `mcpServers.agentmemory`).
- `.claude/settings.json` (12 hooks, 15 skills, MCP server).
- Verify that 53 tools are visible in this very session.

**Day 5 (Phase 3)**: Land Codex CLI + OpenCode wiring:
- `.codex/config.toml` (6 hooks, 15 skills, MCP server) + the `connect codex --with-hooks` workaround documented in the bootstrap.
- `opencode.json` (22 hooks, plugin, MCP server).
- Mirror into `~/.codex/hooks.json` and `~/.config/opencode/plugins/agentmemory-capture.ts`.

**Day 8 (Phase 4)**: Land pi, Hermes, OpenClaw wiring:
- `integrations/pi/`, `integrations/hermes/`, `integrations/openclaw/` (or `~/.pi/agent/extensions/agentmemory/`, `~/.hermes/config.yaml`, OpenClaw MCP config).
- Optional: deeper slot integration for Hermes (`memory.provider: agentmemory`) and OpenClaw (`plugins.slots.memory: "agentmemory"`).

**Day 11 (Phase 5)**: Land OpenSpec traceability + CI sidecar:
- `platform-verification` delta (added to the existing spec).
- `platform-extensibility` delta (added to the existing spec).
- `.github/workflows/verify.yml` (add the `agentmemory` service container).
- `tests/cross-service-smoke/` (add `TestAgentMemoryContract`).
- `tests/agentmemory-fixtures/` (3 seeded session transcripts).
- `verification/traceability.yaml` (add `agentmemory://` references for in-scope observations).
- OpenSpec change → archive via `openspec archive --change agentmemory-integration --yes`.

**Rollback**:

The whole change is contained in:
1. `Makefile` (5 new targets, 5 new help lines)
2. `scripts/agentmemory-{bootstrap,up,down,doctor,reset,wait-for}.sh`
3. `infrastructure/agentmemory.env.template`
4. `.cursor/mcp.json`, `.claude/settings.json`, `.codex/config.toml`, `opencode.json`, plus the per-agent integration dirs
5. `.github/workflows/verify.yml` (the sidecar block)
6. `tests/cross-service-smoke/` (the `TestAgentMemoryContract` addition)
7. `tests/agentmemory-fixtures/` (the fixture corpus)
8. `verification/traceability.yaml` (the `agentmemory://` references)
9. `README.md` (the "Developer Memory" section)
10. `docs/agentmemory.md`, `docs/agentmemory-troubleshooting.md`, `docs/adr/0007-developer-memory-layer.md`
11. The 7 new `openspec/changes/agentmemory-integration/specs/*/spec.md` files (and the 2 deltas under `openspec/changes/agentmemory-integration/specs/{platform-verification,platform-extensibility}/spec.md`)

A single revert PR removes all of the above. Rollback procedure:

1. `make agentmemory-down` — stops the host process.
2. Revert the PR.
3. Optional: `make agentmemory-reset` to remove `~/.agentmemory/run/` and `~/.agentmemory/log/` while preserving `~/.agentmemory/data/` and `~/.agentmemory/config/` for recovery.
4. `git log -- openspec/changes/agentmemory-integration/` — verify the change is gone.

**Memories are NOT deleted on rollback.** `memory_audit` provides a complete record of what was captured if rollback is triggered by a privacy incident. The audit log lives in the named state directory and can be diffed against the project scope before any explicit `memory_governance_delete` is run. If the rollback is privacy-driven, the additional step is:

5. `curl -fsS -X POST $AGENTMEMORY_URL/agentmemory/governance/delete -d '{"project":"microservices-platform","scope":"all"}'` — purges all memories in the project namespace, with the deletion recorded in the audit log.

## Open Questions

- **Q1. Should the integration include `iii-cron` for scheduled lifecycle tasks?** — the upstream README mentions nightly consolidation, weekly snapshots, and decay sweeps as cron-driven. Without `iii-cron`, these run only when the server is running (which is most of the time on a dev machine, but not 100%). Decision deferred to a follow-up; B+ is fine without it.
- **Q2. Should the `agentmemory-team-share` capability be in v1?** — the upstream MCP surface includes `memory_team_share` and `memory_team_feed`. The `AGENTMEMORY_AGENT_SCOPE=shared` setting already gives cross-agent recall on a single machine, but `memory_team_share` is for cross-machine team sharing. Out of scope for the host-process deployment; deferred to a follow-up that adopts `iii-pubsub` and a shared server.
- **Q3. Should we replace `CLAUDE_MEMORY_BRIDGE` with a one-way sync to OpenSpec?** — the upstream `memory_claude_bridge_sync` tool syncs to `CLAUDE.md` (or `MEMORY.md`). The OpenSpec traceability delta is the project-native equivalent. A future change could write a custom iii function that syncs to `openspec/changes/<change>/memory.md` instead of `MEMORY.md`. Out of scope for v1.
- **Q4. Should the `iii-observability` worker be enabled in the host-process server?** — the upstream `iii-config.yaml` ships with `iii-observability` enabled by default. With `exporter: memory`, traces stay in the engine. With `exporter: otlp`, traces go to a real OTel collector. The project's own OTel Collector is at `otel-collector:4317` in the LGTM overlay; the host-process server cannot reach it. Decision: keep `exporter: memory` (default); the agentmemory viewer on `:3113` is the debug UI. Future change: pipe agentmemory traces to the project's collector via a sidecar process.
- **Q5. Should we author a Go client for the agentmemory REST API?** — the upstream `iii-sdk` is published on crates.io, npm, and PyPI but NOT on pkg.go.dev. A Go client would need to be hand-written (the REST surface is documented in the upstream README; ~30 endpoints, all JSON). A Go client would let services query `mem::smart-search` from Go code (e.g., the `TestAgentMemoryContract` could be a Go test instead of a curl test). Out of scope for v1; deferred to a follow-up.
- **Q6. Should the integration include `agentmemory` in the project's `make verify-pr` chain?** — the `verify-pr` target runs `platform-verify` + `services-verify`. Adding `agentmemory-verify` would run `make agentmemory-doctor` as part of the PR gate. Currently the doctor is a local-only check; the CI sidecar in `verify.yml` is the CI equivalent. Decision: leave the PR gate alone; the CI sidecar covers the contract; the doctor is for local triage.
- **Q7. Should the `opencode.json` plugin be vendored or fetched on bootstrap?** — the upstream `plugin/opencode/agentmemory-capture.ts` is ~300 lines of TypeScript. Vendoring adds 300 lines to the repo; fetching on bootstrap adds a network dependency. Decision: fetch on bootstrap (`npx skills add -y -a opencode` covers the skills; the plugin file is a separate `cp` step). Documented in `scripts/agentmemory-bootstrap.sh`.
- **Q8. What is the rollback for a privacy incident that spans multiple developers?** — `memory_audit` is per-server. If developer A captures a memory and developer B's server has the same `project=microservices-platform` namespace, the audit logs do not cross. Decision: out of scope for the host-process deployment (each developer has their own server); the audit log is per-developer. A future change with `iii-pubsub` and a shared server adds team-wide audit.
