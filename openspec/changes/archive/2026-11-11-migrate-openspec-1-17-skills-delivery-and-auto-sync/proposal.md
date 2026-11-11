# Proposal

## Why

The `openspec` CLI on `iosteam-mac-mini` has upgraded to `@fission-ai/openspec@1.17.0`, while `platform/openspec-store` remains frozen on `1.12.0` generated skills, deprecated `delivery: "both"` `/opsx:*` command shims, stale `1.7.0` governance specs, and no automated maintenance step to reconcile CLI upgrades into checked-in skill trees. Completing the `1.17.0` skills-only migration now eliminates OpenSpec 2.0 command-shim deprecation debt (`Fission-AI/OpenSpec#2022`), restores `PROJECT_ROOT_GUARD` and symlink-containment safeguards in active agent workflows, prevents manual progressive-disclosure edits from breaking `openspec update` idempotency, and establishes cross-node operational parity with `macbook-pro-m5` (`2026-11-11-upgrade-openspec-1-17-and-align-shb-skills`).

## What Changes

- **BREAKING**: Switch machine-global OpenSpec delivery (`~/.config/openspec/config.json`) on `iosteam-mac-mini` from `"delivery": "both"` to `"delivery": "skills"` while retaining `"profile": "custom"` (all 12 canonical workflows) and `"defaultStore": "openspec-store"`.
- **BREAKING**: Retire all 96 generated `/opsx:*` and `opsx-*` command, workflow, and prompt wrapper files across `platform/openspec-store` (`.agents/workflows/`, `.claude/commands/opsx/`, `.factory/commands/`, `.junie/commands/`, `.kilocode/workflows/`, `.kiro/prompts/`, `.pi/prompts/`, `.qoder/commands/`) via OpenSpec `1.17.0`'s native `reconcileCommandFiles()`, and prune the 24 managed command symlinks in `~/Developer/.claude/commands/opsx/` and `~/.claude/commands/opsx/` via `scripts/sync-workspace-agent-skills.py`.
- Regenerate all 96 `SKILL.md` files (12 workflows across 8 active tool adapters: `.agents/skills`, `.claude/skills`, `.factory/skills`, `.junie/skills`, `.kilocode/skills`, `.kiro/skills`, `.pi/skills`, `.qoder/skills`) to `metadata.generatedBy: "1.17.0"`, adopting native tool-transformed skill invocations (`/openspec-<skill>`, `$openspec-<skill>`, `/skill:openspec-<skill>`), `PROJECT_ROOT_GUARD`, and `openspec list --specs --json` discovery.
- Reclassify CLI-generated OpenSpec workflow skills (`metadata.author: "openspec"` with `metadata.generatedBy`) as upstream generator-owned artifacts exempt from manual 500-line local file splitting, and remove the orphaned hand-split `openspec-onboard/references/onboarding-walkthrough.md` files introduced in `f246722e` so `openspec update` stays 100% idempotent.
- Prune emptied OpenSpec command/workflow/prompt directories in `platform/openspec-store` while explicitly preserving non-OpenSpec runtime assets in `.opencode/` and active tool symlink trees in `.agent/skills`, `.goose/skills`, and `.zencoder/skills`.
- Centralize OpenSpec CLI-to-skill `metadata.generatedBy` drift detection (`--check`) and file-locked (`/tmp/openspec-skill-sync.lock`), `DISABLE_UPDATES`-aware `openspec update` reconciliation inside `platform/openspec-store/scripts/sync-workspace-agent-skills.py`, and add a reconcile fallback in `shb/shb-schedule/src/shb_schedule/workflows/workstation_update.py` (`step_skills_refresh`) when `--check` detects drift (`workstation-daily-update.sh` Stage 6 already invokes `--check` then sync then `--check` with zero script edits).
- Update `platform/openspec-store/tests/test_ponytail_skill_reconciliation.py`, `~/Developer/.claude/CLAUDE.md`, and `platform/openspec-store/docs/mac-development-setup.md` to reflect `1.17.0` skills-only delivery (`claude_commands=0`).

### Explicit Non-Goals

- Changing OpenSpec CLI package ownership on `iosteam-mac-mini` from `~/.npm-global/bin/openspec` (`npm-global`) to Homebrew Formula (`/opt/homebrew/bin/openspec` remains forbidden on `iosteam-mac-mini` per `config/workstation-toolchain-manifest.json`).
- Modifying any repository, configuration, or launchd job on `macbook-pro-m5` (already migrated and archived under `d5b4819`).
- Deleting or modifying `platform/openspec-store/.opencode/` (`opencode.json`, `plugins/`, `package.json`), which holds active OpenCode plugin assets rather than OpenSpec command shims.
- Mutating any historical directory under `platform/openspec-store/openspec/changes/archive/`.

### Ownership Boundaries

- **Central OpenSpec Store & Skill Sync (`~/Developer/platform/openspec-store`)**: Owns generated OpenSpec skill trees, `scripts/sync-workspace-agent-skills.py`, unit tests, `evidence.md`, setup runbooks, and main specifications (`allowedEditRoots` during central apply).
- **Operator / Workstation Global Config (`~/.config/openspec/config.json`, `~/.npm-global/bin/openspec`)**: Owns global OpenSpec profile/delivery configuration and single-owner npm CLI installation (`@fission-ai/openspec@1.17.0`).
- **Workspace & User Skill Surfaces (`~/Developer/{.agents,.claude}`, `~/{.agents,.claude,.hermes}`, `~/Developer/.claude/CLAUDE.md`)**: Owns reconciled skill/command symlinks and workspace agent instructions outside `platform/openspec-store`.
- **Scheduled Maintenance Runners (`~/Developer/shb/shb-schedule`, plus existing `~/Developer/scripts/workstation-daily-update.sh` caller)**: `shb-schedule` is an external Git root updated to call `sync-workspace-agent-skills.py` before re-checking parity when `--check` fails; `workstation-daily-update.sh` requires zero edits because Stage 6 already delegates check/reconcile/pause gating to `sync-workspace-agent-skills.py`.

## Capabilities

### New Capabilities

_None._

### Modified Capabilities

- `openspec-runtime-governance`: Replace hardcoded `1.7.0`, `core` profile, and `delivery: both` constraints with version-neutral `@fission-ai/openspec` `@latest` (`1.17.0+` verified baseline), `profile: "custom"` (12 workflows), `delivery: "skills"` with fail-closed `reconcileCommandFiles()` cleanup, and automated CLI-to-skill `metadata.generatedBy` convergence in scheduled maintenance.
- `openspec-agent-surface-parity`: Require all 12 OpenSpec skills across active `platform/openspec-store` adapter trees to match the installed CLI version (`1.17.0+`) with tool-native skill invocations, retire all 96 generated `/opsx:*` / `opsx-*` command/workflow/prompt files, and prune emptied command directories without touching `.opencode/` or active tool symlink trees.
- `workspace-openspec-skill-discovery`: Update the `.claude` native OpenSpec surface contract from skills plus 12 `/opsx:*` commands to skills-only `.claude/skills/openspec-*` discovery (`claude_commands=0`), pruning obsolete managed command symlinks while preserving user-owned non-managed files.
- `agent-skills-standard-and-portability`: Classify CLI-generated OpenSpec workflow skills (`metadata.author: "openspec"` with `metadata.generatedBy`) alongside lockfile-tracked vendor skills as upstream generator-owned artifacts exempt from manual 500-line file splitting (`openspec-onboard/SKILL.md`).

## Impact

- **`platform/openspec-store`**: Updates 96 `SKILL.md` files across 8 tool trees to `1.17.0`, deletes 96 deprecated command/workflow/prompt files (12 legacy `.kilocode/workflows` + 84 command shims), removes 2 orphaned `openspec-onboard/references/onboarding-walkthrough.md` files and emptied command directories, updates `scripts/sync-workspace-agent-skills.py`, `tests/test_ponytail_skill_reconciliation.py`, `docs/mac-development-setup.md`, `evidence.md`, and 4 main specifications.
- **Machine & Workspace Surfaces**: Sets `"delivery": "skills"` in `~/.config/openspec/config.json`, removes 24 managed `/opsx:*` command symlinks and emptied `commands/opsx` directories under `~/Developer/.claude/` and `~/.claude/` without rotating third-party `.skill-snapshots/`, and updates `~/Developer/.claude/CLAUDE.md`.
- **`shb/shb-schedule`**: Updates `step_skills_refresh()` in `src/shb_schedule/workflows/workstation_update.py` (+ unit tests in `tests/test_workstation_update_workflow.py`) to invoke `sync-workspace-agent-skills.py` when `--check` detects OpenSpec skill or symlink drift.
