# Design

## Context

See `proposal.md - Why` for motivation. On `iosteam-mac-mini` (`100.70.16.83`), `@fission-ai/openspec` is already installed at `1.17.0` under `~/.npm-global/bin/openspec` (governed by `config/npm-global-tools.json` and `config/workstation-toolchain-manifest.json`), while peer workstation `macbook-pro-m5` (`100.106.143.78`) already completed its `1.17.0` skills-only cutover (`2026-11-11-upgrade-openspec-1-17-and-align-shb-skills`, commit `d5b4819`).

Four concrete codebase invariants on `iosteam-mac-mini` shape how this migration executes:

1. **Global configuration & command-shim debt**: `~/.config/openspec/config.json` currently declares `"profile": "custom"` (all 12 canonical workflows), `"defaultStore": "openspec-store"`, and `"delivery": "both"`. Under `platform/openspec-store`, `openspec update --dry-run --json` detects 8 tool trees with skills (`.agents`, `.claude`, `.factory`, `.junie`, `.kilocode`, `.kiro`, `.pi`, `.qoder` = 96 `SKILL.md` files at `generatedBy: "1.12.0"`) plus 8 command/workflow/prompt directories holding 96 generated wrapper files, with 24 symlinks exposed in `~/Developer/.claude/commands/opsx/` and `~/.claude/commands/opsx/`.
2. **Manual split collision in `openspec-onboard`**: Commit `f246722e` (`2026-11-08-reconcile-agentskills-and-uv-compliance`) split `.agents/skills/openspec-onboard/SKILL.md` and `.claude/skills/openspec-onboard/SKILL.md` into `references/onboarding-walkthrough.md` to satisfy the 500-line locally-authored skill cap. However, `openspec update` unconditionally overwrites `SKILL.md` from `dist/core/templates/workflows/onboard.js` (~606 lines), orphaning `references/onboarding-walkthrough.md` and violating `openspec update` idempotency.
3. **Directory ownership separation in `platform/openspec-store`**: `.agent/skills`, `.goose/skills`, and `.zencoder/skills` hold 3 live git-tracked tool symlinks (`brightdata-cli`, `data-feeds`, `search`); `.opencode/` contains 3,657 active OpenCode plugin/runtime files (`opencode.json`, `plugins/`, `package.json`, `node_modules/`) and is NOT an OpenSpec command directory; the 8 emptied OpenSpec command/workflow/prompt directories are safe to prune.
4. **Multi-root transaction boundaries**: Central OpenSpec `allowedEditRoots` covers `~/Developer/platform/openspec-store`. Host configuration (`~/.config/openspec/config.json`), workspace/user symlinks (`~/Developer/{.agents,.claude}`, `~/{.agents,.claude}`), and `~/Developer/shb/shb-schedule` are distinct execution surfaces with separate Git histories; `~/Developer/scripts/workstation-daily-update.sh` Stage 6 already delegates check/reconcile/pause gating to `scripts/sync-workspace-agent-skills.py` and needs zero edits.

## Goals / Non-Goals

**Goals:**
- Achieve zero-diff idempotent `openspec update` execution on `platform/openspec-store` under `"delivery": "skills"` at `@fission-ai/openspec@1.17.0`.
- Preserve `sync-workspace-agent-skills.py` non-destructive symlink reconciliation and third-party `.skill-snapshots/{current,previous}` rollback history while retiring managed `/opsx:*` command shims and empty `commands/opsx/` directories cleanly.
- Ensure future daily upgrades of `@fission-ai/openspec` in `~/.npm-global` automatically converge `platform/openspec-store` skills and workspace symlinks under a single exclusive host file lock without duplicate logic across shell and Python runners.

**Non-Goals:**
- Unifying CLI package-manager authority across workstations (`iosteam-mac-mini` keeps `npm-global`; `macbook-pro-m5` keeps Homebrew Formula).
- Removing active secondary IDE skill trees (`.factory/skills`, `.junie/skills`, `.kilocode/skills`, `.kiro/skills`, `.pi/skills`, `.qoder/skills`) whose `SKILL.md` targets are actively maintained by `openspec update`.
- Editing `~/Developer/scripts/workstation-daily-update.sh` or rotating `.skill-snapshots/` via `--accept-refresh` (since `openspec-*` skills are not tracked in `skills-lock.json`).

## Decisions

### D1: Adopt `"delivery": "skills"` Globally and Handle Empty `commands/opsx/` Destinations Cleanly in `reconcile_links()`
- **Choice**: Run `openspec config set delivery skills` (updating `~/.config/openspec/config.json`) while keeping `profile: "custom"` and `defaultStore: "openspec-store"`, then run `openspec update /Users/androidteam/Developer/platform/openspec-store` followed by `uv run scripts/sync-workspace-agent-skills.py`. In `reconcile_links()` (`sync-workspace-agent-skills.py:L377-454`), return `Result([], [], [], [])` early when `not destination.is_dir() and not desired`, and remove `destination` via `destination.rmdir()` when `not desired and not check` and zero entries remain after unlinking managed symlinks.
- **Rationale**: In OpenSpec `1.17.0`, `reconcileCommandFiles()` (`dist/core/shared/command-reconcile.js`) fingerprint-checks every on-disk command/workflow/prompt file against released OpenSpec templates (`isReleasedGeneratedContent`) before unlinking, deleting all 96 unmodified shims while keeping any hand-edited file (`kept`/`unchecked`). Once `store/.claude/commands/opsx/*.md` is empty (`claude_commands == {}`), `reconcile_links()` unlinks only symlinks whose `realpath` resolves inside `store/.claude/commands/opsx` (leaving non-managed files untouched), removes the emptied `commands/opsx/` folder without calling `mkdir` on empty `desired`, and returns clean status (`0` conflicts) on subsequent `--check` runs when `commands/opsx/` is absent.
- **Alternatives considered**:
  - *Keep `"delivery": "both"`*: Rejected because `/opsx:*` command shims are deprecated upstream ahead of OpenSpec 2.0 (`Fission-AI/OpenSpec#2022`), double the generated file count (192 vs 96), and leave `iosteam-mac-mini` diverged from `macbook-pro-m5`.
  - *Delete `commands/opsx/` outside `reconcile_links()` without updating lines 377–380*: Rejected because `reconcile_links()` currently returns `missing-destination:<path>` on `--check` whenever `destination` is absent, even when `desired` is empty.

### D2: Exempt Generator-Owned OpenSpec Skills by Spec Contract Without Dead Parser Code
- **Choice**: Update `agent-skills-standard-and-portability/spec.md` to exempt CLI-generated OpenSpec workflow skills (`metadata.author: openspec` + `metadata.generatedBy`) alongside `skills-lock.json` vendor skills from manual 500-line local splitting, and delete the orphaned `openspec-onboard/references/onboarding-walkthrough.md` files (and empty `references/` directories) in `.agents/skills/` and `.claude/skills/`. Do NOT add a separate 500-line exemption parser to `sync-workspace-agent-skills.py`.
- **Rationale**: `sync-workspace-agent-skills.py:L255-316` enforces frontmatter field whitelisting, `<= 1024`-byte descriptions, and no `/Users/` paths—it has no 500-line check, and OpenSpec `1.17.0` (`skill-generation.js:L113-123`) already emits only the 6 allowed YAML fields with ~200-byte descriptions. Fixing the spec rule and deleting the orphaned split files achieves 100% `openspec update` idempotency with zero dead code.
- **Alternatives considered**:
  - *Add `is_generator_owned_skill()` helper in `sync-workspace-agent-skills.py`*: Rejected as YAGNI because no code path in `sync-workspace-agent-skills.py` checks body line counts.

### D3: Single-Source Locked CLI-to-Skill Convergence Inside `sync-workspace-agent-skills.py`
- **Choice**: Implement OpenSpec CLI-to-skill convergence once inside `platform/openspec-store/scripts/sync-workspace-agent-skills.py`:
  1. Resolve `openspec` on `PATH` (`~/.npm-global/bin/openspec`), read `openspec --version`, and compare against `metadata.generatedBy` across `store/.agents/skills/openspec-*/SKILL.md` and `store/.claude/skills/openspec-*/SKILL.md`.
  2. In `--check` mode: if any OpenSpec skill's `metadata.generatedBy` differs from `openspec --version`, print `openspec_generator_drift=cli:<v>,skills:<found>` and fail closed (`return 1`) without mutating disk.
  3. In normal (reconcile) mode: acquire an exclusive `fcntl.flock` on `/tmp/openspec-skill-sync.lock` around OpenSpec generation + link sync. When `metadata.generatedBy != cli_version`, check `os.environ.get("DISABLE_UPDATES")` (skipping mutation if paused) and verify `delivery == "skills"` in `~/.config/openspec/config.json`, then run `openspec update <store>` (surfacing any `kept`/`unchecked` entries) before running `reconcile_links()`.
  4. In `~/Developer/shb/shb-schedule/src/shb_schedule/workflows/workstation_update.py` (`step_skills_refresh`, lines 1221–1231): if `python3 sync-workspace-agent-skills.py --check` returns non-zero, invoke `python3 sync-workspace-agent-skills.py` to reconcile `openspec update` + symlinks and re-run `--check`. `~/Developer/scripts/workstation-daily-update.sh` Stage 6 (`L988-1004`) already implements this exact `--check` $\rightarrow$ `GLOBAL_PAUSE`-gated reconcile $\rightarrow$ `--check` loop and requires zero edits.
- **Rationale**: Eliminates triplicated version-parsing logic across Bash and two Python repos, avoids unnecessary edits to `workstation-daily-update.sh` and `config/script-provenance-manifest.tsv`, honors `DISABLE_UPDATES`, and prevents concurrent `launchd` and `shb-schedule` runs from reading half-written `SKILL.md` files during `openspec update`.
- **Alternatives considered**:
  - *Duplicate `openspec --version` vs `generatedBy` checks in `workstation-daily-update.sh`, `workstation_update.py`, and `sync-workspace-agent-skills.py`*: Rejected due to 3-way maintenance drift and unlocked concurrent file writes.

### D4: Transaction, Evidence & Commit Isolation Across Roots
- **Choice**: Sequence implementation across explicit boundaries:
  1. **Host & Store Generation**: Update `~/.config/openspec/config.json` $\rightarrow$ run `openspec update` in `platform/openspec-store` $\rightarrow$ prune orphaned `openspec-onboard/references/` and emptied command dirs (keeping `.opencode/` and tool symlink trees intact) $\rightarrow$ update `sync-workspace-agent-skills.py` & `test_ponytail_skill_reconciliation.py` $\rightarrow$ run `sync-workspace-agent-skills.py` and `--check` (without `--accept-refresh`, preserving `.skill-snapshots/previous/`).
  2. **External Scheduler Root**: Update `~/Developer/shb/shb-schedule` (`step_skills_refresh` reconcile fallback + unit tests) and verify with `uv run pytest`.
  3. **Docs, Evidence & Archive**: Update `~/Developer/.claude/CLAUDE.md` and `platform/openspec-store/docs/mac-development-setup.md`, author `evidence.md`, run `validate-archive-readiness.py --strict`, `openspec validate --all --store openspec-store` (zero failures), and confirm strict main-spec warnings do not exceed the pre-migration baseline (`<= 160`), then sync specs, archive, and commit each Git repository with isolated pathspecs excluding concurrent change `harden-omniroute-update-oci-burst-pacing-and-storage-hygiene`.

```
+-----------------------------------------------------------------------------------+
| iosteam-mac-mini OpenSpec 1.17.0 Skills-Only Convergence Flow                     |
+-----------------------------------------------------------------------------------+
|                                                                                   |
|  workstation-daily-update.sh (Stage 6)       shb-schedule (step_skills_refresh)   |
|                \                                       /                          |
|                 v                                     v                           |
|          [ sync-workspace-agent-skills.py (/tmp/openspec-skill-sync.lock) ]       |
|                 |                                     |                           |
|    cli != generatedBy (& !DISABLE_UPDATES)            | reconcile_links()         |
|                 v                                     v                           |
|       [ openspec update <store> ]          ~/Developer/{.agents,.claude}/skills   |
|        - 96 SKILL.md @ 1.17.0              ~/{.agents,.claude}/skills             |
|        - deletes 96 /opsx:* shims          - prunes 24 links & empty commands/opsx|
+-----------------------------------------------------------------------------------+
```

## Risks / Trade-offs

- **Muscle memory for `/opsx:*` slash commands in Claude Code or TUI clients** $\rightarrow$ Mitigation: Update `~/Developer/.claude/CLAUDE.md` and `docs/mac-development-setup.md` with the 1.17.0 native `/openspec-<skill>` and `$openspec-<skill>` invocations; Claude Code natively autocompletes `/openspec-*` from `.claude/skills/openspec-*`.
- **Concurrent active change `harden-omniroute-update-oci-burst-pacing-and-storage-hygiene` in `platform/openspec-store`** $\rightarrow$ Mitigation: `openspec update` touches only tool adapter directories, never `openspec/changes/` or `openspec/specs/`. Stage and commit using explicit pathspecs so unrelated active change files are never disturbed.
- **Overlapping `launchd` and `shb-schedule` maintenance runs** $\rightarrow$ Mitigation: Exclusive `fcntl.flock` on `/tmp/openspec-skill-sync.lock` serializes `openspec update` and symlink reconciliation so readers never observe partially written `SKILL.md` frontmatter.
- **`openspec update` during unattended maintenance leaves uncommitted skill updates in `platform/openspec-store` when a new npm release lands** $\rightarrow$ Mitigation: That dirty diff in `.agents/skills` / `.claude/skills` is deterministic generator output (`generatedBy` bump) and surfaces cleanly in `git status` for review while passing `sync-workspace-agent-skills.py --check` and `openspec validate --all --strict`.

## Migration Plan

1. Record pre-migration baseline (`openspec --version`, `openspec config list --json`, `openspec validate --all --store openspec-store` = 462/462 pass, `openspec validate --changes --strict --store openspec-store` = pass, `openspec validate --all --strict --store openspec-store` = 160 pre-existing warning specs ratchet, `sync-workspace-agent-skills.py --check` = pass).
2. Switch global config to `"delivery": "skills"` via `openspec config set delivery skills` and verify `~/.config/openspec/config.json`.
3. Run `openspec update /Users/androidteam/Developer/platform/openspec-store`, verify `kept == []` and `unchecked == []`, remove orphaned `openspec-onboard/references/onboarding-walkthrough.md` files, and remove empty legacy/command directories while keeping `.opencode/` untouched.
4. Update `scripts/sync-workspace-agent-skills.py` (empty-destination `reconcile_links` handling + locked `openspec --version` vs `metadata.generatedBy` check/reconcile) and `tests/test_ponytail_skill_reconciliation.py`, then run `sync-workspace-agent-skills.py` and `--check` (`claude_commands=0`, no `--accept-refresh`).
5. Update `shb/shb-schedule/src/shb_schedule/workflows/workstation_update.py` (`step_skills_refresh` reconcile fallback on `--check` failure + unit tests) and verify `workstation-daily-update.sh --check` passes with zero edits or script drift.
6. Update `~/Developer/.claude/CLAUDE.md` and `platform/openspec-store/docs/mac-development-setup.md`, write `evidence.md`, and run `pytest`, `validate-archive-readiness.py --strict`, `openspec validate --all --store openspec-store`, `openspec validate --changes --strict --store openspec-store`, and the `<= 160` strict main-spec non-regression check.
7. **Rollback**: If any gate fails before archival, run `openspec config set delivery both`, `git -C ~/Developer/platform/openspec-store checkout -- .agents .claude .factory .junie .kilocode .kiro .pi .qoder .agent .goose .zencoder scripts tests docs`, and `uv run ~/Developer/platform/openspec-store/scripts/sync-workspace-agent-skills.py` to restore all 12 `/opsx:*` command symlinks and `1.12.0` skills intact.
