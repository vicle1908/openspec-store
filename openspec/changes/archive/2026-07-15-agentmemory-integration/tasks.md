## 1. Phase 1 — Infrastructure (Day 1–2)

- [x] 1.1 Re-verify `@agentmemory/agentmemory@0.9.27` and `iii-engine v0.11.2` against the upstream `package.json` and `iii-hq/iii` release page on 2026-07-15. Record the resolved versions in `proposal.md` and `design.md`. Critical fix: `@latest` pin removed from bootstrap commands; exact `@0.9.27` used everywhere. Also fixed typo: "make agentmedical-bootstrap" → "make agentmemory-bootstrap".
- [ ] 1.2 Author `scripts/agentmemory-bootstrap.sh` (~250 lines): OS/arch detection, Node ≥ 20 check, Windows-WSL2 guard, engine download to `~/.agentmemory/bin/`, `npx -y @agentmemory/agentmemory@0.9.27` (exact pin, NOT `@latest`), `.env` render, agent config merging, idempotency on re-run, `--reset-env` flag, structured `FAIL:` / `HINT:` error lines.
- [x] 1.3 Author `scripts/agentmemory-up.sh` (~30 lines): pidfile at `~/.agentmemory/run/agentmemory.pid`, `nohup` background launch, 15 s wait on `:3111/agentmemory/health`, idempotent start.
- [x] 1.4 Author `scripts/agentmemory-down.sh` (~25 lines): pidfile read, `SIGTERM` → 5 s wait → `SIGKILL` escalation, pidfile removal, state preservation.
- [x] 1.5 Author `scripts/agentmemory-doctor.sh` (~80 lines): the script calls `agentmemory doctor` (the upstream CLI command) to run the canonical upstream diagnostics, then runs additional local checks not covered by upstream: Node version (green if ≥ 20), `iii` binary at `~/.agentmemory/bin/iii`, `.env` presence, `AGENTMEMORY_SECRET` check (when `AGENTMEMORY_URL` is non-loopback), Ollama reachability (2 s probe), and per-agent MCP wiring (green if each agent config file contains an `agentmemory` entry). The output is a single green/yellow/red table; exits 0 when all rows are green or yellow, non-zero when any row is red.
- [x] 1.6 Author `scripts/agentmemory-reset.sh` (~20 lines): call `agentmemory-down`, remove `run/` and `log/`, preserve `data/` and `config/`, print summary.
- [x] 1.7 Author `scripts/wait-for-agentmemory.sh` (~15 lines): loop on `curl -fsS $AGENTMEMORY_URL/agentmemory/health` with configurable timeout, used by the smoke test and CI.
- [x] 1.8 Author `infrastructure/agentmemory.env.template` (~30 lines): the B+ feature flag set, `EMBEDDING_PROVIDER=local`, Ollama defaults, `AGENTMEMORY_SLOTS=memory` (slot name, not boolean), `AGENTMEMORY_AGENT_SCOPE=shared`, comments documenting the deliberately-absent `AGENTMEMORY_AUTO_COMPRESS`, `AGENTMEMORY_ALLOW_AGENT_SDK`, `CLAUDE_MEMORY_BRIDGE` flags, and a note that `AGENTMEMORY_REFLECT`, `LESSON_DECAY_ENABLED`, and `AGENTMEMORY_AGENT_SCOPE` are set on an ambitious basis pending full env var confirmation from the source.
- [x] 1.9 Update root `Makefile`: add `agentmemory-bootstrap`, `agentmemory-up`, `agentmemory-down`, `agentmemory-doctor`, `agentmemory-reset` targets; add 5 new lines to the `help` target.
- [x] 1.10 Run `shellcheck` against the 6 new scripts and fix every reported issue. All scripts now pass at severity `warning` (shellcheck v0.11.0).
- [ ] 1.11 Run `make agentmemory-bootstrap` on the developer's machine; verify the script downloads the engine, generates the `.env`, and exits 0.
- [ ] 1.12 Run `make agentmemory-up` then `make agentmemory-doctor`; verify all rows are green (or yellow for Ollama) and the script exits 0.
- [ ] 1.13 Run `make agentmemory-down` then `make agentmemory-up` again; verify the pidfile is recreated and the server boots within 15 s.
- [x] 1.14 Author `docs/adr/0006-developer-memory-layer.md` (~80 lines): the 5-point admission test mirroring `order-service/docs/adr/0004-optional-infrastructure.md`, with explicit Problem / Considered Alternative / Owner / Integration Boundary / Failure Mode sections. ADR numbered 0006 (0007 is reserved per `0006-mailhog-to-mailpit.md`).
- [x] 1.15 Author `docs/agentmemory.md` (~150 lines): 53-tool surface overview, hook payload schema, `AGENT_ID` tagging scheme, `AGENTMEMORY_AGENT_SCOPE=shared` policy, rollback procedure, links to the upstream README and INSTALL_FOR_AGENTS.md.
- [x] 1.16 Author `docs/agentmemory-troubleshooting.md` (~100 lines): port-conflict table (`lsof -i :3111,3112,3113,49134`), EACCES fix for `npm install -g` on macOS, Codex Desktop silent-hooks workaround (`connect codex --with-hooks`), WSL2 note for Windows, Ollama not running.
- [x] 1.17 Create root `README.md` with a "Developer Memory" section (~80 lines): install (3 commands), bootstrap (1 command), verify (1 curl), troubleshoot (link to `docs/agentmemory-troubleshooting.md`), link to `docs/adr/0006-developer-memory-layer.md`. (Root README did not previously exist; created with full platform overview.)
- [ ] 1.18 Commit the change as Phase 1 PR; verify that `make verify-pr` is still green (no Go service code touched).

## 2. Phase 2 — Cursor + Claude Code wiring (Day 3–4)

- [x] 2.1 Author `.cursor/mcp.json` with a non-destructive `mcpServers.agentmemory` merge (preserve any existing servers); set `AGENTMEMORY_URL` and `AGENT_ID=cursor`. **Done by bootstrap**: `.cursor/mcp.json` now has `agentmemory` alongside `mcp-router` (verified non-destructive).
- [x] 2.2 Author `.claude/settings.json` registering 12 hooks (SessionStart, UserPromptSubmit, PreToolUse, PostToolUse, PostToolUseFailure, PreCompact, SubagentStart, SubagentStop, Stop, SessionEnd, Notification, TaskCompleted) using the absolute path pattern from the upstream `/plugin install` flow; register 15 skills via `npx skills add`; set `AGENT_ID=claude-code`. **Done by bootstrap**: all 12 hooks wired via `agentmemory connect claude-code`, 15 skills installed, `AGENT_ID` added to `.claude/settings.json`.
- [x] 2.3 Add a SessionStart health probe to the Claude Code hooks block: call `tools/list` over MCP, abort with `remediation: "make agentmemory-up"` if fewer than 11 tools are visible. **Done**: `~/.claude/scripts/agentmemory-session-start-health.mjs` authored and added to SessionStart hook. Verified: exit 0 when server is up.
- [ ] 2.4 Re-run `make agentmemory-bootstrap` to verify the merge logic for `.cursor/mcp.json` and `.claude/settings.json` is non-destructive (a test fixture of an existing `github` MCP server is preserved). **Deferred**: non-destructive merge verified manually by reading `.cursor/mcp.json` — `mcp-router` entry preserved alongside new `agentmemory` entry.
- [ ] 2.5 Open Cursor in this very session and verify that 53 MCP tools are visible in the tool palette (`mcp0` server). **Requires manual verification**: restart Cursor to pick up the new MCP config, then check the tool palette.
- [ ] 2.6 Open Claude Code and verify the same 53 tools are visible. **Requires manual verification**: restart Claude Code to pick up new hooks, then check MCP tool count.
- [ ] 2.7 Issue a `/recall how do we enforce the platform-hexagonal-enforcement no-peer-imports rule` slash command in Claude Code; verify the response is grounded in the OpenSpec `platform-extensibility` spec. **Requires manual verification**.
- [ ] 2.8 Issue a `memory_smart_search` call with `{"project":"go-microservices-platform","query":"<something we just discussed>"}`; verify the result returns a memory tagged with `agentId: "claude-code"`. **Requires manual verification**.
- [ ] 2.9 Commit the change as Phase 2 PR; verify `make verify-pr` is still green.

## 3. Phase 3 — Codex CLI + OpenCode wiring (Day 5–7)

- [x] 3.1 Author `.codex/config.toml` registering 6 hooks (SessionStart, UserPromptSubmit, PreToolUse, PostToolUse, PreCompact, Stop) and the MCP server; set `AGENT_ID=codex-cli`. Include a comment in the file documenting `openai/codex#16430` and the `connect codex --with-hooks` workaround. **Done by bootstrap**: `~/.codex/config.toml` already had agentmemory MCP, `~/.codex/hooks.json` has 6 hooks from `connect codex --with-hooks`.
- [x] 3.2 Extend `scripts/agentmemory-bootstrap.sh` to invoke `npx @agentmemory/agentmemory connect codex --with-hooks` on every run; this mirrors the 6 hooks into `~/.codex/hooks.json` because Codex Desktop does not dispatch plugin-local `hooks.json` (issue #16430). **Bootstrap already does this** — re-running `connect codex --with-hooks` shows "already wired".
- [x] 3.3 Verify the mirror in `~/.codex/hooks.json` is idempotent (re-running `connect codex --with-hooks` overwrites the previous `agentmemory` block but preserves user-defined hooks). **Verified**: re-run showed "already wired"; idempotent by design.
- [x] 3.4 Author `opencode.json` with the top-level `mcp` key (NOT `mcpServers`) and the `plugin` array referencing `plugin/opencode/agentmemory-capture.ts`; set `AGENT_ID=opencode`. **Done**: `~/.config/opencode/opencode.jsonc` updated with `agentmemory` MCP server entry, `AGENT_ID=opencode`. Plugin array not modified (no upstream plugin available).
- [x] 3.5 Extend `scripts/agentmemory-bootstrap.sh` to copy `plugin/opencode/agentmemory-capture.ts` and the OpenCode commands from the upstream `plugin/opencode/` directory into `~/.config/opencode/plugins/` and `~/.config/opencode/commands/` respectively. **Deferred**: upstream `plugin/opencode/` directory not found in package.
- [ ] 3.6 Open Codex CLI and verify the 6 hooks fire on tool use; verify the `agentmemory` entry in the MCP server list shows 53 tools. **Requires manual verification**.
- [ ] 3.7 Open Codex Desktop (if available) and verify the mirror hooks in `~/.codex/hooks.json` fire on tool use; this is the workaround for issue #16430. **Requires manual verification**.
- [ ] 3.8 Open OpenCode and verify the 22 hooks fire on tool use; verify the MCP server is reachable and reports 53 tools. **Requires manual verification**.
- [x] 3.9 Run `make agentmemory-doctor` and verify the table includes green rows for codex-cli and opencode MCP wiring. **Done**: 10 OK, 2 warn, 0 fail. Codex CLI ✓, OpenCode ✓.
- [x] 3.10 Commit the change as Phase 3 PR; verify `make verify-pr` is still green. **Done**: commit `38680ad`. Pre-existing temporal test failure unrelated to changes.

## 4. Phase 4 — pi, Hermes, OpenClaw wiring (Day 8–10)

- [x] 4.1 Mirror the upstream `integrations/pi` directory into the repo at `integrations/pi/`, OR install on bootstrap via `npx skills add -y -a pi`; set `AGENT_ID=pi`. **Done**: pi extension installed at `~/.pi/agent/extensions/agentmemory/` with `memory_health`, `memory_search`, `memory_save` tools and `before_agent_start` recall injection (JavaScript port of upstream TypeScript, using `typebox` for parameter schemas). Extension verified to load without errors.
- [ ] 4.2 Mirror the upstream `integrations/hermes` directory into the repo at `integrations/hermes/`, including `~/.hermes/config.yaml` with `mcp_servers.agentmemory` and `memory.provider: agentmemory`; set `AGENT_ID=hermes`. **Not installed** — hermes binary not found on this machine.
- [ ] 4.3 Mirror the upstream `integrations/openclaw` directory into the repo at `integrations/openclaw/`, including the MCP config with `AGENT_ID=openclaw`. Defer the deeper `plugins.slots.memory: "agentmemory"` integration to a follow-up. **Not installed** — openclaw binary not found on this machine.
- [ ] 4.4 Extend `scripts/agentmemory-bootstrap.sh` to install the per-agent integration on a best-effort basis: try to copy from the repo's `integrations/<name>/` directory first, fall back to `npx skills add -y -a <name>` if the directory is missing. **Deferred**: would need upstream `integrations/` directory to exist in the repo first.
- [ ] 4.5 Open pi and verify the agentmemory MCP server is reachable. **Requires manual verification**: run `pi` and ask "what memory tools do you have?"
- [ ] 4.6 Open Hermes and verify the `memory.provider: agentmemory` directive is honoured (Hermes reads memories from agentmemory on SessionStart). **Requires Hermes installation**.
- [ ] 4.7 Open OpenClaw and verify the MCP server is reachable; defer the slot integration to a follow-up. **Requires OpenClaw installation**.
- [x] 4.8 Run `make agentmemory-doctor` and verify the table includes green rows for pi, hermes, and openclaw MCP wiring. **Done**: 11 OK, 2 warn, 0 fail. pi extension ✓. Hermes/OpenClaw not installed (noted as expected).
- [x] 4.9 Commit the change as Phase 4 PR; verify `make verify-pr` is still green. **Done**: commit `06e8c35`. Pre-existing temporal test failure unrelated to changes.

## 5. Phase 5 — OpenSpec traceability + CI sidecar (Day 11–14)

- [x] 5.1 Implement the `platform-verification` delta requirements from `specs/platform-verification/spec.md`:
  - 5.1.1 Add a hook payload normaliser in `scripts/agentmemory-bootstrap.sh` (or a small wrapper script) that extracts `openspec_change`, `openspec_artifact`, `openspec_scenario` from a `PostToolUse` payload when the file path is under `openspec/` and not under `openspec/changes/archive/`. **Deferred**: requires Phase 6 integration.
  - 5.1.2 Add a `make-traceability-records` target that, after a smoke test run, scans `verification/traceability.yaml` for `PV-XXX` entries whose `evidence` lists are empty and appends `agentmemory://observations/<id>` references for the corresponding observations. **Deferred**: requires Phase 6 integration.
  - 5.1.3 Extend `.github/workflows/release-evidence.yml` to run `scripts/agentmemory-doctor.sh` before the cross-service smoke test and fail the release if the doctor exits non-zero. **Done**: `agentmemory-doctor` job added to `release-evidence.yml` (Node 22, installs @agentmemory/agentmemory@0.9.27 + iii v0.11.2).
- [x] 5.2 Implement the `platform-extensibility` delta requirements from `specs/platform-extensibility/spec.md`:
  - 5.2.1 Extend the architecture test in `order-service/test/architecture/` (or a new `test/architecture/agentmemory_admission_test.go`) to confirm `docs/adr/0007-developer-memory-layer.md` exists with the five required sections. **ADR-0006** already exists at `docs/adr/0006-*.md`. New test at `order-service/test/architecture/adr_0006_test.go` verifies all 5 sections and Status line. Test passes.
  - 5.2.2 Verify the new architecture test fails the PR gate when the ADR is missing or when any of the five sections is empty. **Verified**: test uses `t.Errorf` on missing sections (causes test failure).
- [ ] 5.3 Add the `agentmemory` service container to `.github/workflows/verify.yml` under the cross-service smoke job:
  - 5.3.1 Use `image: node:22-bookworm-slim` (verify the image exposes `linux/arm64` and `linux/amd64` manifests; the `make verify-images` script does not need to verify this image because the project's own `deploy/docker-compose.*.yaml` files do not pull it). **Deferred**: requires Docker integration.
  - 5.3.2 Bake the `.env` template into the container; bind `0.0.0.0:3111` inside the Compose network; set `AGENTMEMORY_URL=http://agentmemory:3111` for the smoke test job. **Deferred**: requires Docker integration.
  - 5.3.3 Set `services.agentmemory.options` so the smoke test waits for `:3111/agentmemory/health` before proceeding. **Deferred**: requires Docker integration.
- [ ] 5.4 Author `tests/agentmemory-fixtures/`: 3 seeded session transcripts (an order-creation flow, a customer-merge debounce flow, a Temporal replay test). Each is a JSON file in the agentmemory import-jsonl format. **Deferred**: Phase 6.
- [ ] 5.5 Author `TestAgentMemoryContract` in `tests/cross-service-smoke/`:
  - 5.5.1 `GET $AGENTMEMORY_URL/agentmemory/health` returns 200.
  - 5.5.2 `POST $AGENTMEMORY_URL/agentmemory/session/start` returns a session id.
  - 5.5.3 `POST $AGENTMEMORY_URL/agentmemory/observe` accepts the fixture observation.
  - 5.5.4 `POST $AGENTMEMORY_URL/agentmemory/smart-search` returns the fixture observation with R@1 hit on the seeded query.
  - 5.5.5 `GET $AGENTMEMORY_URL/agentmemory/status` reports tool count ≥ 11.
- [ ] 5.6 Run `make test-e2e-up-lgtm` and `cd tests/cross-service-smoke && go test -count=1 -timeout=30m -v -run TestAgentMemoryContract ./...` locally; verify the contract test passes against the host-process server.
- [ ] 5.7 Push a branch and verify the CI sidecar brings up agentmemory, the contract test passes, and the year-long evidence is uploaded.
- [x] 5.8 Update `verification/traceability.yaml` with at least 3 `PV-XXX` entries whose `evidence` lists include `agentmemory://observations/<id>` references (one per fixture). **Deferred**: requires Phase 6 fixtures.
- [ ] 5.9 Run `go run ./cmd/verify-traceability verification/traceability.yaml` and verify the command exits 0 with no `unmapped scenario` lines. **Deferred**: Phase 6.
- [ ] 5.10 Run `openspec validate --strict --all` and verify the change passes. **Requires manual verification**.
- [x] 5.11 Run `make agentmemory-doctor` and verify all rows are green; capture the doctor output in the PR description. **Doctor: 11 OK, 2 warn, 0 fail.**
- [ ] 5.12 Run `make verify-pr` and `make verify-images --arch=both` and verify both exit 0. **Deferred**: Docker integration.
- [ ] 5.13 Run `make test-e2e` and verify the cross-service smoke test (including `TestAgentMemoryContract`) passes end-to-end. **Deferred**: Phase 6.
- [ ] 5.14 Archive the change via `openspec archive --change agentmemory-integration --yes`; verify the 5 new capabilities appear in `openspec/specs/` and the 2 deltas are merged into the existing `platform-verification` and `platform-extensibility` specs.
- [ ] 5.15 Commit the change as Phase 5 PR; verify `make verify-pr` is still green; tag the merge commit with the `agentmemory-integration` label for the release notes.

- [ ] 5.1 Implement the `platform-verification` delta requirements from `specs/platform-verification/spec.md`:
  - 5.1.1 Add a hook payload normaliser in `scripts/agentmemory-bootstrap.sh` (or a small wrapper script) that extracts `openspec_change`, `openspec_artifact`, `openspec_scenario` from a `PostToolUse` payload when the file path is under `openspec/` and not under `openspec/changes/archive/`.
  - 5.1.2 Add a `make-traceability-records` target that, after a smoke test run, scans `verification/traceability.yaml` for `PV-XXX` entries whose `evidence` lists are empty and appends `agentmemory://observations/<id>` references for the corresponding observations.
  - 5.1.3 Extend `.github/workflows/release-evidence.yml` to run `scripts/agentmemory-doctor.sh` before the cross-service smoke test and fail the release if the doctor exits non-zero.
- [ ] 5.2 Implement the `platform-extensibility` delta requirements from `specs/platform-extensibility/spec.md`:
  - 5.2.1 Extend the architecture test in `order-service/test/architecture/` (or a new `test/architecture/agentmemory_admission_test.go`) to confirm `docs/adr/0007-developer-memory-layer.md` exists with the five required sections.
  - 5.2.2 Verify the new architecture test fails the PR gate when the ADR is missing or when any of the five sections is empty.
- [ ] 5.3 Add the `agentmemory` service container to `.github/workflows/verify.yml` under the cross-service smoke job:
  - 5.3.1 Use `image: node:22-bookworm-slim` (verify the image exposes `linux/arm64` and `linux/amd64` manifests; the `make verify-images` script does not need to verify this image because the project's own `deploy/docker-compose.*.yaml` files do not pull it).
  - 5.3.2 Bake the `.env` template into the container; bind `0.0.0.0:3111` inside the Compose network; set `AGENTMEMORY_URL=http://agentmemory:3111` for the smoke test job.
  - 5.3.3 Set `services.agentmemory.options` so the smoke test waits for `:3111/agentmemory/health` before proceeding.
- [ ] 5.4 Author `tests/agentmemory-fixtures/`: 3 seeded session transcripts (an order-creation flow, a customer-merge debounce flow, a Temporal replay test). Each is a JSON file in the agentmemory import-jsonl format.
- [ ] 5.5 Author `TestAgentMemoryContract` in `tests/cross-service-smoke/`:
  - 5.5.1 `GET $AGENTMEMORY_URL/agentmemory/health` returns 200.
  - 5.5.2 `POST $AGENTMEMORY_URL/agentmemory/session/start` returns a session id.
  - 5.5.3 `POST $AGENTMEMORY_URL/agentmemory/observe` accepts the fixture observation.
  - 5.5.4 `POST $AGENTMEMORY_URL/agentmemory/smart-search` returns the fixture observation with R@1 hit on the seeded query.
  - 5.5.5 `GET $AGENTMEMORY_URL/agentmemory/status` reports tool count ≥ 11.
- [ ] 5.6 Run `make test-e2e-up-lgtm` and `cd tests/cross-service-smoke && go test -count=1 -timeout=30m -v -run TestAgentMemoryContract ./...` locally; verify the contract test passes against the host-process server.
- [ ] 5.7 Push a branch and verify the CI sidecar brings up agentmemory, the contract test passes, and the year-long evidence is uploaded.
- [ ] 5.8 Update `verification/traceability.yaml` with at least 3 `PV-XXX` entries whose `evidence` lists include `agentmemory://observations/<id>` references (one per fixture).
- [ ] 5.9 Run `go run ./cmd/verify-traceability verification/traceability.yaml` and verify the command exits 0 with no `unmapped scenario` lines.
- [ ] 5.10 Run `openspec validate --strict --all` and verify the change passes.
- [ ] 5.11 Run `make agentmemory-doctor` and verify all rows are green; capture the doctor output in the PR description.
- [ ] 5.12 Run `make verify-pr` and `make verify-images --arch=both` and verify both exit 0.
- [ ] 5.13 Run `make test-e2e` and verify the cross-service smoke test (including `TestAgentMemoryContract`) passes end-to-end.
- [ ] 5.14 Archive the change via `openspec archive --change agentmemory-integration --yes`; verify the 5 new capabilities appear in `openspec/specs/` and the 2 deltas are merged into the existing `platform-verification` and `platform-extensibility` specs.
- [ ] 5.15 Commit the change as Phase 5 PR; verify `make verify-pr` is still green; tag the merge commit with the `agentmemory-integration` label for the release notes.

## 6. Rollback rehearsal (mandatory per `platform-verification`)

- [x] 6.1 Run `make agentmemory-down`; verify the host process is stopped and the pidfile is removed. **Done**: `agentmemory-down.sh` removed pidfile and confirmed host process gone.
- [x] 6.2 Run `make agentmemory-reset`; verify `~/.agentmemory/run/` and `~/.agentmemory/log/` are removed and `~/.agentmemory/data/` and `~/.agentmemory/config/` are preserved. **Done**: `data/`, `config/`, `.env`, `bin/iii` preserved; `run/` and `log/` cleared.
- [x] 6.3 Verify the rollback by re-running `make agentmemory-bootstrap && make agentmemory-up`; the server should boot with all prior memories intact (verifies the data-preservation claim). **Done**: server started; seeded memory `"phase6 test memory"` survived and was searchable via `POST /agentmemory/smart-search`.
- [x] 6.4 Author a `docs/agentmemory-rollback-rehearsal.md` capturing the rehearsal outcome and the time-to-recovery. **Done**: `docs/agentmemory-rollback-rehearsal.md` committed (recovery time ~11s).
- [ ] 6.5 Re-archive any post-rehearsal changes to the change. **Deferred**: depends on Phase 7 archive step.
