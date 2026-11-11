# Tasks

## 1. Preflight Baseline & Global Skills-Only Configuration

- [x] 1.1 Record pre-migration baseline on `iosteam-mac-mini` and verify single-owner CLI authority (`which -a openspec` returns only `/Users/androidteam/.npm-global/bin/openspec` at `1.17.0+`, `openspec validate --all --store openspec-store` and `openspec validate --changes --strict --store openspec-store` exit `0` with `160` pre-existing warning main specs recorded under `--all --strict`, and `uv run ~/Developer/platform/openspec-store/scripts/sync-workspace-agent-skills.py --check` exits `0`).
- [x] 1.2 Set machine-global OpenSpec delivery to skills-only via `openspec config set delivery skills` and verify `openspec config list --json` reports `"profile": "custom"`, `"delivery": "skills"`, `"defaultStore": "openspec-store"`, and all 12 canonical workflows.

## 2. OpenSpec Store `1.17.0` Skill Regeneration & Directory Hygiene

- [x] 2.1 Run `openspec update /Users/androidteam/Developer/platform/openspec-store` under `"delivery": "skills"` and verify all 96 `SKILL.md` files across the 8 active tool trees (`.agents/skills`, `.claude/skills`, `.factory/skills`, `.junie/skills`, `.kilocode/skills`, `.kiro/skills`, `.pi/skills`, `.qoder/skills`) report `generatedBy: "1.17.0"` while all 96 unmodified `/opsx:*` and `opsx-*` command/workflow/prompt files are removed cleanly with zero `kept` or `unchecked` entries.
- [x] 2.2 Remove the orphaned hand-split `references/onboarding-walkthrough.md` files (and empty `references/` directories) under `platform/openspec-store/.agents/skills/openspec-onboard/` and `platform/openspec-store/.claude/skills/openspec-onboard/`, then re-run `openspec update --dry-run --json /Users/androidteam/Developer/platform/openspec-store` to verify `"changes": []` idempotency.
- [x] 2.3 Remove emptied command-shim directories (`.agents/workflows`, `.claude/commands/opsx`, `.claude/commands`, `.factory/commands`, `.junie/commands`, `.kilocode/workflows`, `.kiro/prompts`, `.pi/prompts`, `.qoder/commands/opsx`, `.qoder/commands`) in `platform/openspec-store`, verifying `platform/openspec-store/.opencode/` and tool symlink trees (`.agent/skills`, `.goose/skills`, `.zencoder/skills`) remain untouched.
- [x] 2.4 Update `platform/openspec-store/docs/mac-development-setup.md` and `~/Developer/.claude/CLAUDE.md` to document OpenSpec `1.17.0+` `"delivery": "skills"` and `/openspec-<skill>` / `$openspec-<skill>` workflow invocations, verifying zero stale claims that 12 generated `/opsx:*` command files are installed.

## 3. Skill Synchronizer Convergence & Unit Tests (`platform/openspec-store`)

- [x] 3.1 Update `platform/openspec-store/scripts/sync-workspace-agent-skills.py` to:
  1. Return `Result([], [], [], [])` early in `reconcile_links()` when `not destination.is_dir() and not desired`, prune emptied `commands/opsx/` directories via `rmdir()` when `not desired and not check`, and never report `missing-destination` on `--check` when `desired` is empty.
  2. Implement OpenSpec generator parity across all 8 adapter trees: in `--check` mode, fail closed if `openspec` is present and any OpenSpec skill's `metadata.generatedBy` differs from `openspec --version`; in normal mode, acquire an exclusive `fcntl.flock` on `/tmp/openspec-skill-sync.lock`, check `os.environ.get("DISABLE_UPDATES")`, and run `openspec update` when `metadata.generatedBy != cli_version` before linking.
  3. Verify `uv run ruff check platform/openspec-store/scripts/sync-workspace-agent-skills.py` exits `0`.
- [x] 3.2 Update `platform/openspec-store/tests/test_ponytail_skill_reconciliation.py` to test absent `commands/opsx/` passing `--check` with zero conflicts when `claude_commands=0`, generator drift detection on `--check`, file-locked reconcile when drifted, and `DISABLE_UPDATES=1` suppression, verifying `uv run --project ~/Developer/platform/openspec-store pytest tests/test_ponytail_skill_reconciliation.py -q` passes.
- [x] 3.3 Execute `uv run ~/Developer/platform/openspec-store/scripts/sync-workspace-agent-skills.py` followed by `--check` (without `--accept-refresh`), verifying the 24 managed command symlinks and emptied `commands/opsx/` directories under `~/Developer/.claude/` and `~/.claude/` are pruned, `claude_commands=0`, `malformed_entries=0`, snapshot history is preserved, and `bash ~/Developer/scripts/workstation-daily-update.sh --check` passes with zero script drift.
## 4. Maintenance Runner Parity (`shb-schedule`)

- [x] 4.1 Update `~/Developer/shb/shb-schedule/src/shb_schedule/workflows/workstation_update.py` (`step_skills_refresh`) and `~/Developer/shb/shb-schedule/tests/test_workstation_update_workflow.py` so that if `python3 sync-workspace-agent-skills.py --check` returns non-zero, it invokes `python3 sync-workspace-agent-skills.py` (which runs locked `openspec update` + link sync) before re-running `--check`, verifying `env -u PYTHONPATH uv run --project ~/Developer/shb/shb-schedule pytest -q` passes.

## 5. End-to-End Integration Verification & Archive Readiness Gate

- [x] 5.1 Author `evidence.md` recording executed CLI paths, `1.17.0` generator provenance across all 8 tool trees, zero `kept`/`unchecked` command files, clean `sync-workspace-agent-skills.py --check` (`claude_commands=0`), and untouched status on concurrent change `harden-omniroute-update-oci-burst-pacing-and-storage-hygiene`.
- [x] 5.2 Run full verification gates: `uv run --project ~/Developer/platform/openspec-store pytest -q`, `uv run ~/Developer/platform/openspec-store/scripts/verify-workstation-toolchain.py`, `openspec store doctor`, `openspec doctor --store openspec-store --json`, `uv run ~/Developer/platform/openspec-store/scripts/validate-archive-readiness.py --change migrate-openspec-1-17-skills-delivery-and-auto-sync --store ~/Developer/platform/openspec-store --strict`, `openspec validate --all --store openspec-store`, `openspec validate --changes --strict --store openspec-store`, and confirm `openspec validate --all --strict --store openspec-store` introduces zero new failing main specs (`<= 160`).

## Workflow follow-up

- Commit external repository changes in `~/Developer/shb/shb-schedule` with isolated pathspecs once verified.
- Sync delta specifications and archive `migrate-openspec-1-17-skills-delivery-and-auto-sync` via `/openspec-archive-change` (`--store openspec-store`), then commit `~/Developer/platform/openspec-store` with isolated pathspecs excluding unrelated in-progress changes.
