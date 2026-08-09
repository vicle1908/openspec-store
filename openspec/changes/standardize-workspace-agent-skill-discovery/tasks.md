## 1. Baseline and Governance

- [x] 1.1 Read workspace and repository instructions and inventory Git status across all repositories.
- [x] 1.2 Inspect the existing `workspace-openspec-skill-discovery` main spec and active OpenSpec changes.
- [x] 1.3 Verify official Codex and Claude skill discovery paths and symlink behavior.
- [x] 1.4 Restore Codex-specific governance covering ownership, roles, writers, credentials, and Context7.
- [ ] 1.5 Validate this change's proposal, delta spec, design, and tasks before further mutation.

## 2. Structural Inventory and Provenance

- [ ] 2.1 Inventory direct workspace skill roots containing `SKILL.md` separately from container directories.
- [ ] 2.2 Inventory user-level real directories, workspace symlinks, broken links, stale links, and name collisions.
- [ ] 2.3 Compare project and global `npx skills` lockfiles with actual roots and classify registry-tracked, generated, repository-specific, and local skills.
- [ ] 2.4 Compare duplicate names and content hashes while distinguishing intentional adapter variants.
- [ ] 2.5 Separate skill-setup-owned Git diffs from unrelated Graphify, GitNexus, source, and generated-file changes.

## 3. Tracked Synchronization Ownership

- [ ] 3.1 Move the Codex user-skill manifest and link synchronizer into an owning path tracked by `openspec-store`.
- [ ] 3.2 Expose workspace convenience paths without duplicating authoritative script or manifest content.
- [ ] 3.3 Update synchronizer output to report canonical roots, containers, selected entries, created links, removed stale links, broken links, and conflicts.
- [ ] 3.4 Run synchronization and `--check`; verify seven real global installs are preserved and no broken or conflicting links remain.

## 4. Native Agent Discovery

- [ ] 4.1 From two independent repositories, verify fresh Claude sessions natively invoke an OpenSpec skill without filesystem-search fallback.
- [ ] 4.2 From two independent repositories, verify fresh Claude sessions natively invoke one non-OpenSpec shared skill; add `.claude/skills` symlinks only if required.
- [ ] 4.3 Verify all twelve `/opsx:*` command files and remove unsupported `/opsx:help` documentation.
- [ ] 4.4 From two independent repositories and one nested directory, verify fresh Codex sessions invoke `$openspec-explore` through standard `.agents` discovery.
- [ ] 4.5 Diagnose Graphify discovery using frontmatter validation, duplicate-name checks, fresh-session logs, minimized-artifact testing, and index-budget evidence before changing its artifact.
- [ ] 4.6 Confirm `.codex/skills` contains only system or genuinely Codex-specific skills and no shared copies.

## 5. Documentation and Repository Reconciliation

- [ ] 5.1 Update workspace `AGENTS.md`, `.claude/CLAUDE.md`, `.codex/AGENTS.md`, and reusable skill guidance to match verified behavior.
- [ ] 5.2 Sweep active instructions for obsolete empty-`.claude`, copied-Codex, inaccurate skill-count, unsupported `/opsx:help`, `.Codex`, and mangled-path claims.
- [ ] 5.3 Review tracked per-repository `.claude/skills/gitnexus/*` deletions and keep only deletions backed by native Claude replacement probes.
- [ ] 5.4 Preserve repository-specific skills and unrelated dirty state.

## 6. Final Validation and Archive

- [ ] 6.1 Run focused OpenSpec validation for this change and the governing capability.
- [ ] 6.2 Run `openspec store doctor`, verify OpenSpec version, and run full validation while reporting unrelated baseline failures separately.
- [ ] 6.3 Re-run structural, provenance, link, native-discovery, stale-reference, and Git-diff checks.
- [ ] 6.4 Archive the completed change, validate the merged main spec, and commit/push only store-owned artifacts.
