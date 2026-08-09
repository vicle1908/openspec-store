# Verification Evidence

## Structural inventory

- Workspace canonical collection: 82 direct skill roots containing `SKILL.md`.
- Containers not counted as skills: `generated/`, `gitnexus/`.
- Project `npx skills` lock: 35 tracked entries; global lock: 7 tracked entries.
- Synchronizer check: 20 Codex-selected shared links, 7 Claude-selected shared links, 12 adapter-specific OpenSpec targets, 12 Claude `/opsx:*` commands, zero conflicts, zero broken links, and zero pending mutations.
- Workspace convenience manifests and script directory are symlinks into tracked `openspec-store` sources.

## Native Claude discovery

Fresh Claude sessions were started from `agent-core`, `go-microservices`, and `go-microservices/platform` with filesystem tools unavailable for the discovery probe.

- Claude initialization registered all 12 OpenSpec skills and all 12 `/opsx:*` commands.
- Claude initialization registered `gitnexus-cli`, `gitnexus-debugging`, `gitnexus-exploring`, `gitnexus-guide`, `gitnexus-impact-analysis`, `gitnexus-refactoring`, `graphify`, and `handoff` through personal skill scope.
- OpenSpec explicit invocation completed in one turn with zero tool use from `agent-core` and `go-microservices`.
- Explicit no-tool `/gitnexus-exploring` invocation returned `CLAUDE_GITNEXUS_OK` from both `agent-core` and `go-microservices` with zero tool use.
- The six tracked repository-local GitNexus skill deletions in `agent-core` are byte-identical to their personal Claude replacements and are therefore covered by equivalent personal links to canonical workspace roots.

## Native Codex discovery

Fresh read-only Codex sessions explicitly invoked skills without command, MCP, or filesystem-search events.

- `$openspec-explore` succeeded from `agent-core`, `go-microservices`, and nested `go-microservices/platform`.
- `$gitnexus-exploring` succeeded from `agent-core` and `go-microservices`.
- `.codex/skills` contains only `migrate-to-codex`; shared OpenSpec and GitNexus skills are not copied there.

## Graphify limitation

- Canonical Graphify passes `skills-ref validate`.
- The full canonical Graphify artifact was not selected by fresh Codex sessions through standard user-level `.agents/skills` discovery.
- A minimal valid skill with the same `graphify` name at the same discovery path was selected and invoked successfully with zero tool events.
- Therefore the standard path, name, and discovery mechanism are valid; the incompatibility is within the full artifact or Codex indexing behavior. The evidence does **not** prove a hard parser or 500-line limit.
- Graphify remains canonical in workspace `.agents/skills` and available to Claude, but is intentionally excluded from the Codex manifest pending a separate progressive-disclosure refactor and retest.

## OpenSpec and repository state

- Focused strict validation passes for `standardize-workspace-agent-skill-discovery`.
- `openspec store doctor` reports no issues.
- Full validation reports 348 passes and one unrelated existing failure: `align-jti-skill-runtime-contract`.
- Skill-owned guidance was verified as an exact path-only substitution and committed separately in each owning repository; repository-local GitNexus cleanup was committed only in `agent-core`. Unrelated Graphify, GitNexus index, source, and generated-file changes were not staged.
