# Proposal

## Why

The `openspec` CLI on `iosteam-mac-mini` has upgraded to `@fission-ai/openspec@2.0.0` and partially rewritten `platform/openspec-store` on disk into OpenSpec 2.0's shared `.agents/skills/` layout, leaving 97 unstaged and 24 untracked changes uncommitted while global config (`~/.config/openspec/config.json`), `sync-workspace-agent-skills.py`, unit tests, setup runbooks, and canonical specifications still enforce the retired `1.17.0` `"delivery": "skills"` and 8-copy (`96 SKILL.md`) contract. Reconciling and committing the OpenSpec 2.0 shared skill layout now restores repository hygiene, eliminates retired `delivery` config and multi-hop symlink blind spots in `sync-workspace-agent-skills.py`, and aligns `iosteam-mac-mini` with `macbook-pro-m5` (`2026-11-13-migrate-openspec-2-shared-skill-layout`).

## What Changes

- **BREAKING**: Retire the deprecated `"delivery"` key from machine-global OpenSpec configuration (`~/.config/openspec/config.json`) on `iosteam-mac-mini`, retaining `"profile": "custom"`, all 12 canonical workflows, and `"defaultStore": "openspec-store"`.
- **BREAKING**: Adopt OpenSpec `2.0.0`'s shared skill layout in `platform/openspec-store`:
  - Consolidate the 12 canonical OpenSpec workflow `SKILL.md` files (`metadata.generatedBy: "2.0.0"`) once under `platform/openspec-store/.agents/skills/openspec-*/SKILL.md` alongside `.agents/skills/.openspec-target` (`claude own-files`, `codex`, `factory`, `junie`, `kilocode`, `kiro own-files`, `pi`, `qoder`).
  - Replace physical OpenSpec skill copies under `.claude/skills/` and `.kiro/skills/` with 24 committed relative directory symlinks (`../../.agents/skills/openspec-*`) required by OpenSpec 2.0 `SKILL_LINKED_TOOL_IDS`.
  - Remove all 60 redundant per-host OpenSpec `SKILL.md` copies across `.factory/skills/`, `.junie/skills/`, `.kilocode/skills/`, `.pi/skills/`, and `.qoder/skills/` while preserving tracked Bright Data skill symlinks (`brightdata-cli`, `data-feeds`, `search`) and `.opencode/` runtime assets.
- Upgrade `platform/openspec-store/scripts/sync-workspace-agent-skills.py` and `tests/test_ponytail_skill_reconciliation.py` for OpenSpec `2.0.0` topology convergence:
  - Remove the retired `openspec-delivery-mismatch` gate on `"delivery"`, the unused module-level `OPEN_SPEC_NAMES` glob, `OPENSPEC_ADAPTER_SKILL_TREES`, and the obsolete `1.17` `kept: / unchecked: / failures: ` stdout parser.
  - Validate the 2.0 shared topology in `sync-workspace-agent-skills.py`: verify `.agents/skills/.openspec-target` exists and retains `"claude own-files"`, all 12 canonical `.agents/skills/openspec-*/SKILL.md` generator versions match `openspec --version`, relative symlinks resolve for `own-files` targets (`.claude/skills/openspec-*`, `.kiro/skills/openspec-*`), zero `openspec-*` entries exist across all other `.<dir>/skills/` folders in the store, `openspec` subprocesses receive isolated `HOME`/`XDG_CONFIG_HOME` overrides when `--home-dir`/`--openspec-config` are set, and `openspec update --dry-run --json <store>` reports empty `changes`, `notes`, and `failures` in both `--check` and post-`update` reconcile modes.
  - Fix multi-hop symlink ownership detection in `reconcile_links()` (`_is_managed`) using the parent-resolved immediate target (`raw.parent.resolve() / raw.name`) plus `os.path.realpath()` so `~/Developer/.claude/skills/openspec-*`, `~/.claude/skills/openspec-*`, and `~/.agents/skills/openspec-*` remain recognized as managed links even when two-hop chains break under symlinked macOS `/tmp` or `/var` roots.
- Update `platform/openspec-store/docs/mac-development-setup.md` and `~/Developer/.claude/CLAUDE.md` (if needed) to document the OpenSpec `2.0.0` shared `.agents/skills/` + `.openspec-target` + `own-files` symlink layout and retired `delivery` setting.

### Explicit Non-Goals

- Changing OpenSpec CLI installation ownership on `iosteam-mac-mini` away from `~/.npm-global/bin/openspec` (`@fission-ai/openspec@2.0.0`, `npm-global` authority in `config/workstation-toolchain-manifest.json`).
- Modifying any repository, global config, or LaunchAgent on `macbook-pro-m5` (already completed and archived in `shb-specs` commit `a87d7a6`).
- Modifying `~/Developer/scripts/workstation-daily-update.sh` or `~/Developer/shb/shb-schedule/src/shb_schedule/workflows/workstation_update.py`, both of which already delegate OpenSpec parity check and file-locked reconciliation to `sync-workspace-agent-skills.py`.
- Touching the concurrent active OpenSpec change `add-tailscale-media-relay-for-ios-and-peers/`, deleting `.opencode/` runtime assets, removing non-OpenSpec Bright Data symlinks (`brightdata-cli`, `data-feeds`, `search`), or mutating historical `openspec/changes/archive/` directories.

### Ownership Boundaries

- **Central OpenSpec Store & Skill Synchronizer (`~/Developer/platform/openspec-store`)**: Owns `.agents/skills/.openspec-target`, the 12 canonical `.agents/skills/openspec-*/SKILL.md` files, the 24 `.claude/skills/openspec-*` and `.kiro/skills/openspec-*` relative symlinks, removal of the 60 retired per-host copies, `scripts/sync-workspace-agent-skills.py`, `tests/test_ponytail_skill_reconciliation.py`, `docs/mac-development-setup.md`, main specifications, and `evidence.md`.
- **Machine-Global OpenSpec Configuration (`~/.config/openspec/config.json`, `~/.npm-global/bin/openspec`)**: Owns removal of the retired `"delivery"` field while preserving `"profile": "custom"`, all 12 workflows, `"defaultStore": "openspec-store"`, telemetry state, and single-owner npm-global CLI execution (`2.0.0`).
- **Workspace & User Skill Surfaces (`~/Developer/{.agents,.claude}/skills`, `~/{.agents,.claude,.hermes}/skills`)**: Reconciled via `sync-workspace-agent-skills.py` without rotating third-party `.skill-snapshots/{current,previous}/`.

## Capabilities

### New Capabilities

_None._

### Modified Capabilities

- `openspec-runtime-governance`: Update target CLI baseline to `2.0.0+`, remove retired `"delivery"` configuration enforcement from `~/.config/openspec/config.json` and `sync-workspace-agent-skills.py`, and require shared `.agents/skills/` + `.openspec-target` + `own-files` symlink + `openspec update --dry-run --json` convergence.
- `openspec-agent-surface-parity`: Replace the `1.17.0` 8-tree physical copy contract (`96 SKILL.md` files) with OpenSpec `2.0.0`'s single shared `.agents/skills/openspec-*` canonical set (`12 SKILL.md` files), `.openspec-target` tool inventory, `24` relative symlinks for `claude` and `kiro`, and retirement of redundant per-host OpenSpec copies.
- `workspace-openspec-skill-discovery`: Update Claude and multi-agent OpenSpec discovery from `1.17.0` `"delivery": "skills"` copies to `2.0.0` shared `.agents/skills/` canonical skills linked through `.claude/skills/openspec-*`, and require multi-hop symlink ownership tracking across workspace and user skill roots.

## Impact

- **`platform/openspec-store`**: Reconciles and commits 12 updated `.agents/skills/openspec-*/SKILL.md` files (`2.0.0`), `.agents/skills/.openspec-target`, 24 relative symlinks in `.claude/skills/` and `.kiro/skills/`, 60 deleted per-host OpenSpec `SKILL.md` files across `.factory`, `.junie`, `.kilocode`, `.pi`, and `.qoder`, updated `scripts/sync-workspace-agent-skills.py` + `tests/test_ponytail_skill_reconciliation.py`, `docs/mac-development-setup.md`, `evidence.md`, and 3 main specs.
- **Machine Global Config**: Removes retired `"delivery": "skills"` from `~/.config/openspec/config.json`.
- **Workspace & Scheduled Maintenance**: Both `workstation-daily-update.sh` (Stage 6) and `shb-schedule` (`step_skills_refresh`) automatically enforce the upgraded OpenSpec `2.0.0` topology checks via `sync-workspace-agent-skills.py --check`.
