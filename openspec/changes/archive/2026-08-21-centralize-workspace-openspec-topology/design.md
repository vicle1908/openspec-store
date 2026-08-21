## Context

See [proposal.md](proposal.md) for motivation. The registered global configuration already resolves `defaultStore` to `openspec-store`. Fifteen repositories retain only a one-line `openspec/config.yaml` pointer, so they are not independent planning roots and have no local artifacts to migrate. In contrast, `ai-harness-skills/openspec/schemas/harness-13` is a tracked source resource: its CLI source-root discovery, installer, doctor checks, and tests currently depend on the path.

The central store has active changes and unrelated untracked work. Each affected code repository is independently versioned and may have concurrent changes. Cleanup must therefore be a sequence of isolated repository transactions, not a bulk directory removal from the workspace root.

## Goals / Non-Goals

**Goals:**

- Leave `/Users/androidteam/Developer/openspec-store/openspec` as the sole directory that OpenSpec resolves as a planning root.
- Remove each redundant pointer-only directory while proving both explicit `--store openspec-store` and global-default resolution select the shared store.
- Move the harness schema to a package-owned resource path that does not contain a directory named `openspec`, while preserving installed-project schema output under the central OpenSpec workflow where that is part of the harness contract.
- Produce per-repository evidence, reversible commits, and a final workspace topology audit.

**Non-Goals:**

- Moving, rewriting, or archiving any shared-store spec, change, report, or configuration.
- Removing generated configuration, skills, or instructions that are not under a repository-local `openspec/` directory.
- Altering global OpenSpec registration, credentials, remote repositories, or unrelated repository changes.
- Changing the semantics of the `harness-13` schema, its rendered content, or its supported install destinations.

## Decisions

1. **Use the existing global registered store; do not replace it with per-repository links.** `openspec config get defaultStore` already returns `openspec-store`, and the current CLI documents that this is the intended externalized-planning topology. The cleanup will retain explicit `--store openspec-store` in automation and verify unscoped resolution only as a compatibility gate. Creating symlinks or new per-repository `store:` pointers would preserve the ambiguity being removed.

2. **Delete pointer-only directories only after a repository-local preflight.** For each of the fifteen pointer repositories, the implementation will create a dedicated worktree, record HEAD and dirty state, prove the directory contains exactly its tracked pointer, remove it with Git-aware deletion, and confirm a command from that worktree resolves the shared store. A repository with unexpected tracked or untracked children is excluded and reported instead of being removed. This avoids deleting concurrent work or hidden local artifacts.

3. **Relocate the harness schema as package data, not into the shared store.** The `harness-13` schema is application-owned source material, not a workspace planning artifact. It will move to `ai_harness/_bundled/harness-13` (or an equivalently package-owned non-`openspec` resource path chosen by the implementation) and source access will go through one named resource resolver. The CLI, installer, doctor, and resource tests will use that resolver. The existing runtime lookup of an installed project's `openspec/schemas/harness-13` remains unchanged because that is a target-project artifact, not a local planning root.

4. **Require byte-equivalence for the schema migration.** Before deleting the old resource directory, compare every tracked schema/template source with the new package resource and run the focused installer/schema test suite. This retains content behavior while changing only source placement.

5. **Keep one writer per repository and one integration owner.** The shared store change artifacts remain owned by the coordinator. Each code repository has a single worktree writer; no two workers may edit the same repository or shared-store artifact. The coordinator integrates the final topology report only after each repository's evidence is available.

## Risks / Trade-offs

- **[A pointer file is locally customized]** → Check tracked and untracked contents plus dirty state before deletion; preserve and exclude a repository that differs from the audited one-line pointer.
- **[Global default differs for another user or CI]** → Continue to use explicit `--store openspec-store` in workspace automation and record that unscoped use depends on registered global configuration.
- **[Harness resource relocation breaks source or installed modes]** → Add focused red tests for both source checkout discovery and packaged fallback before moving resources; run installer and doctor checks after migration.
- **[Concurrent repository changes are removed or mixed]** → Use per-repository worktrees, scoped paths, Git-aware deletion, and a pre/post dirty fingerprint. Never clean, reset, or stage unrelated paths.
- **[Store cleanup is mistaken for archive authorization]** → Do not archive any existing change as part of this work; completion is a topology and runtime verification result only.

## Migration Plan

1. Snapshot the registered-store configuration, current active shared-store changes, and every local `openspec/` directory's tracked/untracked inventory.
2. Create one branch/worktree per pointer-only repository; remove only `openspec/config.yaml`, verify directory removal, and run a read-only shared-store resolution probe from that worktree.
3. In the `ai-harness-skills` worktree, introduce the package resource resolver and tests, relocate the schema/templates without content changes, update consumers, then remove its `openspec/` directory only after focused tests pass.
4. Run a workspace-wide directory audit, explicit-store and unscoped-resolution probes, store doctor, and strict validation. Preserve results in the change evidence ledger.
5. If any repository fails preflight or verification, revert only that repository's scoped commit or worktree change; retain the central store and all other verified repositories unchanged. The old pointer or schema path can be restored from its isolated Git commit without touching the shared store.
