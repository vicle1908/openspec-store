## Why

`/Users/androidteam/Developer` is the intended Codex workspace, but it contains many independent Git repositories and the current configuration mixes workspace behavior with host-owned settings and legacy agent fields. The result is a root session that is powerful but difficult to reason about, while direct child-repository sessions can legitimately load different project configuration.

The change is needed now because the shared `openspec-store` is already registered as the planning home and MCP Router is live, so the workspace can be made deterministic without creating repo-local planning roots or duplicating shared integrations. The design must explicitly distinguish the authoritative workspace-root session from compatibility launches made directly inside a child repository.

## What Changes

- Make `/Users/androidteam/Developer` the authoritative Codex orchestration root for this multi-repository workspace and document the supported launch/dispatch model.
- Keep workspace-owned execution policy, MCP Router, AgentMemory hooks, multi-agent defaults, workspace agents, and workspace skills under `Developer/.codex` and `Developer/.agents/skills`.
- Treat the existing host-owned provider/auth/profile/notification configuration in `~/.codex` as authoritative and unchanged; remove redundant workspace copies only after a presence-only check confirms the canonical host setting, without comparing or updating credential values.
- Keep each child repository as an independent Git, toolchain, `AGENTS.md`, skill, and lifecycle boundary. Direct child launches remain a compatibility path and are not required to have identical effective project configuration.
- Replace the legacy multi-agent cap with `max_concurrent_threads_per_session = 8`, use `gpt-5.6-terra` with medium reasoning for default subagents, and add narrow `workspace_explorer`, `reviewer`, `verifier`, and `docs_researcher` roles.
- Require every delegated agent to receive an explicit target repository or worktree, read its closest `AGENTS.md`, inspect Git status, and report ownership before acting. Parallel writes to overlapping paths remain serialized even with unrestricted execution.
- Preserve the complete MCP Router tool surface and set Codex to `approval_policy = "never"` and `sandbox_mode = "danger-full-access"`. Verify `/Users/androidteam/Developer` as the router directory scope while documenting that router-owned blocked commands remain router guardrails, not a Codex approval gate.
- Make `openspec-store` the only planning home for this workspace. Commands from the workspace root and child repositories SHALL resolve to the registered store; no child repository may gain a local planning root, except the documented `ai-harness-skills/openspec/schemas/` code dependency.
- Preserve the manifest-owned OpenSpec skill mirrors in `go-microservices/.agents/skills` and `go-microservices/.codex/skills`, and make the 12 workflow skills available from the workspace-root skill surface without hand-editing generated copies.
- Add root-aware readiness checks for configuration, MCP handshakes, skill discovery, hooks, store resolution, repository mapping, and knowledge indexes. Keep reports redacted and classify configured, live, degraded, ready, unrelated-dirty, and unverified states separately.
- Add a credential-preserving, allowlisted cleanup plan for stale workspace Codex state. The current credential in `~/.codex` remains unchanged and outside the cleanup target; explicitly approved redundant workspace copies may be removed without rotating or replacing it.

### Non-goals

- No application, service, deployment, or MCP Router product-code changes.
- No wholesale Claude-to-Codex migration, destructive `migrate-to-codex --replace`, or deletion of native Claude surfaces.
- No credential rotation, revocation, migration, replacement, or external account action; the existing credential configuration in `~/.codex` is explicitly out of scope.
- No promise that a Codex process launched directly inside every child Git root inherits the workspace-root project configuration.
- No local `openspec/` planning roots in child repositories and no changes to the unrelated active `enhance-mcp-config` change.
- No parallel implementation writes across overlapping paths; unrestricted execution does not remove ownership or integration duties.

## Capabilities

### New Capabilities

- `codex-workspace-orchestration`: Defines the workspace-root operating model, repository map, target-aware delegation, unrestricted execution, shared MCP exposure, and readiness evidence.

### Modified Capabilities

- `workspace-openspec-skill-discovery`: Makes the workspace-root OpenSpec skill surface explicit while preserving generator-owned repository mirrors and avoiding parent-directory inheritance claims.

## Impact

- Workspace-owned Codex surfaces: `/Users/androidteam/Developer/.codex/`, `/Users/androidteam/Developer/.agents/skills/`, and the workspace `AGENTS.md`.
- Host-owned Codex settings: `~/.codex/config.toml`, `~/.codex/AGENTS.md`, and host authentication/profile/notification state. These existing credential-bearing settings are inputs to the workspace and are not modified by this change.
- Repository-owned surfaces: every child repository's `.git`, closest `AGENTS.md`, toolchain, local `.codex/`, `.agents/skills`, manifests, and verification commands.
- Shared planning: `/Users/androidteam/Developer/openspec-store/openspec/`, including this change; the store remains a normal Git repository and must be committed after approved lifecycle operations.
- Verification depends on Codex diagnostics, live MCP Router calls, AgentMemory hook probes, manifest-owned skill checks, repository map checks, Graphify/GitNexus status, and strict OpenSpec validation.
