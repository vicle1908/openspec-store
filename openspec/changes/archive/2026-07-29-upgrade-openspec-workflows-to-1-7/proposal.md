## Why

The workstation runs OpenSpec 1.7.0, but the repository still governs and
distributes 1.6.0-generated workflows. That split leaves 144 checked-in skills
(132 across eleven generator-managed tool surfaces plus twelve canonical
`.agents` copies) and their tool-specific command surfaces without the 1.7
archive-safety fixes, correct invocation syntax, operation guidance, or a
reproducible CLI version contract, while CI either installs an unpinned release
or silently skips validation when the command is missing.

## What Changes

- Establish one repository-owned OpenSpec version contract and use it for local
  surface generation, manifests, documentation checks, and CI installation.
- Regenerate every managed OpenSpec skill and command with the approved 1.7
  CLI and the repository's complete twelve-workflow profile, including safe
  inline archive sync, runtime-neutral prompts, correct per-tool invocations,
  Codex skills-only delivery, and the Kimi Code path migration.
- Declare the exact eleven generator-managed tools as repository policy and
  synchronize their 132 generated skills with the twelve separately owned
  `.agents/skills` canonical copies as one reviewed 144-skill inventory.
- Add a fail-closed, reviewable regeneration workflow that refuses to run while
  workstation package maintenance is active, when the installed CLI does not
  match the approved pin, or when the expected tool inventory, profile,
  workflows, and delivery settings are not active. Treat complete
  post-generation verification as authoritative because the upstream updater
  can report an individual tool failure and continue processing other tools.
- Add project-specific apply and archive operation guidance without treating
  advisory guidance as a substitute for repository policy or verification.
- Extend validation so stale generator metadata, unsupported invocation forms,
  legacy managed paths, unsafe archive delegation, manifest drift, missing CLI
  pins, and skipped CI validation fail with actionable diagnostics.
- Document when `skip_specs: true` is legitimate, require meaningful Purpose
  text for new capability deltas, and preserve the rule that instruction,
  workflow, CI, and governance changes require capability deltas.
- Keep repository-local OpenSpec planning. Stores and a machine-wide default
  store remain out of scope while their upstream contract is beta and the
  nearest repository root is healthy.
- **Goals:** make the CLI, generated surfaces, manifest, documentation, and CI
  agree on one reviewed release; eliminate the known archive race and stale
  tool syntax; keep regeneration repeatable and non-destructive.
- **Non-goals:** change application APIs, service behavior, data ownership,
  deployment topology, or runtime dependencies; adopt custom schemas or
  external planning stores; install every newly supported AI tool; archive or
  alter unrelated active changes.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `agent-skill-distribution`: Require version-aligned, generator-owned OpenSpec
  surfaces across supported agents, deterministic profile inputs, reviewed
  tool-path migrations, manifest refresh, and rollback-safe regeneration.
- `agent-instruction-governance`: Require current OpenSpec invocation,
  operation-guidance, `skip_specs`, generated-ownership, and archive-safety
  guidance without hand-editing managed copies.
- `platform-verification`: Require an exactly pinned OpenSpec CLI in CI and
  fail-closed strict validation instead of an unpinned bootstrap or skip.
- `documentation-currency`: Detect stale OpenSpec generator versions,
  tool-specific invocation drift, legacy managed paths, and mismatches between
  the approved pin, generated skills, and manifest.

## Impact

- **Repository surfaces:** OpenSpec configuration and scoped guidance;
  generated skills, commands, workflows, and prompts for Antigravity, Claude,
  Codex, Cursor, Factory, Kilo Code, Kimi Code, Kiro, Oh My Pi, OpenCode, and
  Pi; the shared `.agents/skills` canonical copies; skill policy and manifest;
  documentation validators and tests; root maintenance targets or scripts;
  and GitHub Actions OpenSpec installation and validation steps.
- **Dependencies:** `@fission-ai/openspec` is pinned to the currently verified
  1.7.0 release. Future upgrades require the same npm and official-documentation
  review rather than silently following `latest` in CI.
- **Compatibility:** the complete custom profile remains enabled. Codex uses
  `$openspec-*` skills and has no generated custom prompts; Kimi-generated files
  move from `.kimi/` to `.kimi-code/`. Hand-authored files in legacy tool
  directories and unrelated agent integrations remain untouched.
- **Rollout:** verify the workstation package-maintenance lock is absent and
  its latest successful report plus the CLI are stable, verify the configured
  tools and global profile, snapshot managed surfaces, regenerate and review
  migrations, refresh policy and manifests, then require complete focused and
  repository-wide validation before accepting the new surfaces.
- **Rollback:** restore only the captured OpenSpec-owned surfaces, policy,
  manifest, configuration, validator, and workflow files as one coherent
  version set. Never retain a 1.7 CLI pin with 1.6-generated instructions, or
  roll back unrelated agent, service, deployment, credential, cache, or user
  state.
