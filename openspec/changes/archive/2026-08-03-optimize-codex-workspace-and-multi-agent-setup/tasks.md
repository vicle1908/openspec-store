## 1. Establish workspace and repository boundaries

- [x] 1.1 Capture `/Users/androidteam/Developer` as the authoritative Codex workspace root, each child Git root, HEAD, dirty-state fingerprint, closest `AGENTS.md`, language/toolchain, and focused verification commands.
- [x] 1.2 Build and review a redacted repository map covering all listed Go, Node, Python, shared-data, worktree, and `openspec-store` paths; distinguish Git repositories from shared directories and caches.
- [x] 1.3 Record the workspace-root Codex session identity and effective configuration. Treat direct child launches as compatibility probes and do not require identical effective project configuration.
- [x] 1.4 Inventory `Developer/.codex`, `Developer/.agents/skills`, child `.codex`/`.agents/skills`, manifests, hooks, Graphify outputs, GitNexus state, and host `~/.codex`, classifying ownership before edits.

## 2. Normalize host and workspace Codex ownership

- [x] 2.1 Treat the existing provider/auth/profile/notification settings in `~/.codex` as authoritative no-touch state; remove redundant workspace `model_provider`, `model_providers`, `notify`, and `profiles` blocks only after a presence-only host-setting check, without comparing, modifying, or printing the canonical credential.
- [x] 2.2 Keep workspace execution policy, MCP Router, AgentMemory hooks, multi-agent defaults, custom agents, and root-scoped guidance under `/Users/androidteam/Developer/.codex`; do not rely on parent-directory inheritance for child Git roots.
- [x] 2.3 Set the workspace-root baseline to `approval_policy = "never"` and `sandbox_mode = "danger-full-access"`, and document the deliberate unrestricted profile.
- [x] 2.4 Validate configuration parsing, project-root identity, ignored-key warnings, active instructions, and effective policy from the workspace-root session and at least two direct child-root compatibility probes.

## 3. Credential-preserving cleanup preparation

- [x] 3.1 Record `~/.codex` credential and authentication state as explicitly out of scope without reading, comparing, printing, rotating, revoking, migrating, replacing, deleting, or overwriting values.
- [x] 3.2 Add redacted-output checks for commands, diffs, reports, and retained evidence so no credential value is emitted during workspace normalization.
- [x] 3.3 Classify redundant credential-bearing workspace copies by category and path without reading or comparing values; remove only explicitly approved copies after presence-only confirmation that the canonical host setting exists.
- [x] 3.4 Produce a dry-run allowlist for workspace `.codex` cleanup that keeps `~/.codex` and ambiguous paths untouched and preserves config, hooks, agents, skills, rules, managed mirrors, store artifacts, and unrelated work.

## 4. Configure bounded, target-aware multi-agent roles

- [x] 4.1 Configure `[agents]` in the workspace-root surface with `enabled = true`, `max_concurrent_threads_per_session = 8`, default subagent model `gpt-5.6-terra`, medium reasoning, and only documented/current fields.
- [x] 4.2 Create `Developer/.codex/agents/workspace_explorer.toml`, `reviewer.toml`, `verifier.toml`, and `docs_researcher.toml` with explicit authority, inherited full-access policy, target context, output contract, and write ownership.
- [x] 4.3 Add workspace delegation guidance requiring every worker to read the target repository's closest `AGENTS.md`, inspect Git status, identify toolchain and verification commands, and report the target before acting.
- [x] 4.4 Run a three-role read-only smoke workflow for repository discovery, review, and documentation research; wait for all requested results and verify concise evidence plus interruption handling.
- [x] 4.5 Run a disposable, non-destructive full-access delegation smoke workflow; verify inherited `never` approval, `danger-full-access`, full Router exposure, target ownership, and primary-agent integration.
- [x] 4.6 Verify that overlapping writes are rejected or serialized, the concurrency cap is enforced, and no custom role silently overrides the built-in `explorer` role.

## 5. Preserve and verify MCP Router capability

- [x] 5.1 Keep the complete configured MCP Router tool surface in the workspace-root configuration with the existing `~/.codex` credential unchanged and bounded startup/tool timeouts; do not add a Codex-side deny list or write approval gate.
- [x] 5.2 Verify live Router client identity, router version, `/Users/androidteam/Developer` in `allowedDirectories`, tool discovery, and one harmless routed search; record router-owned blocked commands separately.
- [x] 5.3 Verify filesystem, process, PDF, search, and router-configuration tools are exposed without executing a destructive probe; distinguish Router guardrails from Codex policy.
- [x] 5.4 Check `/Users/androidteam/Developer/mcp-router` checkout version, dependency installation state, branch/dirty status, and focused checks independently of live routed capability.

## 6. Enforce shared OpenSpec store and skill ownership

- [x] 6.1 Verify `openspec-store` registration, `defaultStore`, store health, Git remote/status, and current active-change inventory; keep planning artifacts only in the store.
- [x] 6.2 Run `openspec list --json` or equivalent root metadata checks from Developer, `go-microservices`, `mcp-router`, and a Python repository; require the store path/id and record actual resolution source.
- [x] 6.3 Scan child repositories for accidental planning roots; preserve only the documented `ai-harness-skills/openspec/schemas/` code dependency and do not create `openspec/specs` or `openspec/changes` elsewhere.
- [x] 6.4 Reconcile `go-microservices` manifests and lockfiles through the owning skill workflow; verify all 12 canonical `.agents/skills` to `.codex/skills` mirrors byte-for-byte and preserve their invocation contracts.
- [x] 6.5 Verify all 12 workspace OpenSpec skill copies against the canonical managed source without hand-editing generated files or running destructive migration.

## 7. Verify knowledge surfaces and repository readiness

- [x] 7.1 Update Graphify package/skill metadata through its owning workflow, point each repository entry at the current graph output, and classify missing paths as degraded.
- [x] 7.2 Refresh GitNexus indexes for actual sibling repositories using the pinned workflow; repair nested-repository assumptions and configure groups only after membership verification.
- [x] 7.3 Run direct Graphify/GitNexus MCP probes and classify each capability as configured, indexed, live, degraded, or ready.

## 8. Final root-aware verification, cleanup, and handoff

- [x] 8.1 Run workspace-root `codex doctor --json`, feature/config/MCP/agent/hook/skill diagnostics and retain redacted evidence; run direct child probes only to document compatibility behavior.
- [x] 8.2 Re-run Router identity, discovery, read-only search, directory-scope, and mutation-boundary checks from the workspace-root session without inspecting or printing credential values.
- [x] 8.3 Apply approved cleanup only to allowlisted workspace paths after ownership and presence-only confirmation; recheck permissions, retained-file hashes, canonical `~/.codex` preservation, and the rollback manifest.
- [x] 8.4 Run `make validate-agent-guidance`, `make agent-skills-verify ROOT=both`, focused knowledge checks, and repository-owned validation where available.
- [x] 8.5 Run targeted strict validation for this change, then full-store strict validation; classify unrelated `enhance-mcp-config` failures separately and do not edit that change.
- [x] 8.6 Inspect store and workspace Git status, classify every dirty path as change-owned or unrelated, and hand off `$openspec-verify-change` as the next command without archiving the change.
