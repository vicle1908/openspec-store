# Verification & Operating Evidence Ledger: migrate-openspec-1-17-skills-delivery-and-auto-sync

## 1. OpenSpec Single-Owner Authority & Global Configuration Baseline

### 1.1 Single-Owner CLI Executable Verification (`iosteam-mac-mini`)
```bash
which -a openspec && openspec --version
```
Output:
```
/Users/androidteam/.npm-global/bin/openspec
1.17.0
```
Verification:
- Only `/Users/androidteam/.npm-global/bin/openspec` is present on `PATH`.
- No shadow Homebrew binary at `/opt/homebrew/bin/openspec`.
- Exact installed version is `1.17.0`.

### 1.2 Global Configuration (`~/.config/openspec/config.json`)
```bash
openspec config list --json
```
Output:
```json
{
  "featureFlags": {},
  "profile": "custom",
  "delivery": "skills",
  "telemetry": {
    "noticeSeen": true,
    "anonymousId": "d847ba4e-3221-443e-a890-0eee30dbbac5"
  },
  "workflows": [
    "propose",
    "explore",
    "new",
    "continue",
    "apply",
    "update",
    "ff",
    "sync",
    "archive",
    "bulk-archive",
    "verify",
    "onboard"
  ],
  "defaultStore": "openspec-store",
  "completionTipSeen": true
}
```
Verification:
- `delivery` is `"skills"` (migrated from `"both"`).
- `profile` is `"custom"` with all 12 canonical workflows retained.
- `defaultStore` is `"openspec-store"`.

---

## 2. Store Skill Regeneration & Directory Hygiene (`platform/openspec-store`)

### 2.1 Tool Adapter Skill Trees & Command File Retirement
`openspec update /Users/androidteam/Developer/platform/openspec-store` output:
```
Upgrading to the new OpenSpec

Files to remove (cleaned up by reconcileCommandFiles()):
  ✓ Removed .kilocode/workflows/opsx-*.md (12 files)
  ✓ Removed .claude/commands/opsx/*.md (12 files)
  ✓ Removed .factory/commands/opsx-*.md (12 files)
  ✓ Removed .junie/commands/opsx-*.md (12 files)
  ✓ Removed .kiro/prompts/opsx-*.md (12 files)
  ✓ Removed .pi/prompts/opsx-*.md (12 files)
  ✓ Removed .qoder/commands/opsx/*.md (12 files)
  ✓ Removed .agents/workflows/opsx-*.md (legacy)

✓ Updated: Antigravity, Claude Code, Codex, Factory Droid, Junie, Kilo Code, Kiro, Pi, Qoder (v1.17.0)
Removed: 84 command files (delivery: skills) + 12 legacy (.kilocode/workflows) = 96 total command files removed
Failures: 0, Kept: 0, Unchecked: 0
```
Verification:
- 96 `SKILL.md` files generated across 8 tool adapter directories (`.agents/skills`, `.claude/skills`, `.factory/skills`, `.junie/skills`, `.kilocode/skills`, `.kiro/skills`, `.pi/skills`, `.qoder/skills`).
- 96 command/workflow/prompt wrapper files deleted cleanly (12 legacy `.kilocode/workflows` + 84 command files across 7 directories).
- Every `SKILL.md` reports `generatedBy: "1.17.0"`.

### 2.2 Orphaned Split Removal & Dry-Run Idempotency
- Unlinked orphaned `references/onboarding-walkthrough.md` from `.agents/skills/openspec-onboard/` and `.claude/skills/openspec-onboard/` (and removed empty `references/` directories).
- `openspec update --dry-run --json /Users/androidteam/Developer/platform/openspec-store`:
```json
{
  "changes": [],
  "notes": [],
  "failures": []
}
```
### 2.3 Directory Hygiene & OpenCode Preservation
- Removed emptied command directories: `.agents/workflows`, `.claude/commands/opsx`, `.claude/commands`, `.factory/commands`, `.junie/commands`, `.kilocode/workflows`, `.kiro/prompts`, `.pi/prompts`, `.qoder/commands/opsx`, `.qoder/commands`.
- Preserved `.opencode/opencode.json` and `.opencode/plugins/` intact.
- Preserved `.agent/skills`, `.goose/skills`, and `.zencoder/skills` holding 3 live git-tracked Bright Data symlinks each (`brightdata-cli`, `data-feeds`, `search` -> `../../.agents/skills/*`).

### 3.1 `sync-workspace-agent-skills.py` Execution
```bash
python3 scripts/sync-workspace-agent-skills.py
```
Output:
```
openspec_generator_parity=ok cli=1.17.0
canonical_direct_roots=116 containers=2 codex_selected=71 claude_selected=35 hermes_selected=11 openspec_targets=12 claude_commands=0 check=False
workspace_claude_commands: created=0 removed=12 conflicts=0 broken=0
workspace_claude_commands.removed=apply.md,archive.md,bulk-archive.md,continue.md,explore.md,ff.md,new.md,onboard.md,propose.md,sync.md,update.md,verify.md
user_claude_commands: created=0 removed=12 conflicts=0 broken=0
user_claude_commands.removed=apply.md,archive.md,bulk-archive.md,continue.md,explore.md,ff.md,new.md,onboard.md,propose.md,sync.md,update.md,verify.md
```
Follow-up `--check`:
```bash
python3 scripts/sync-workspace-agent-skills.py --check
```
Output:
```
openspec_generator_parity=ok cli=1.17.0
canonical_direct_roots=116 containers=2 codex_selected=71 claude_selected=35 hermes_selected=11 openspec_targets=12 claude_commands=0 check=True
malformed_entries=0
workspace_claude_commands: created=0 removed=0 conflicts=0 broken=0
user_claude_commands: created=0 removed=0 conflicts=0 broken=0
snapshot_check=ok
```
Verification:
- All 24 managed command symlinks were removed.
- Emptied directories `/Users/androidteam/Developer/.claude/commands/opsx` and `/Users/androidteam/.claude/commands/opsx` were removed.
- Subsequent `--check` exits `0` with zero `missing-destination` conflicts.
- `snapshot_check=ok` with zero snapshot rotation.

### 3.2 Unit Test Verifications
- `platform/openspec-store`:
  `uv run pytest tests/test_ponytail_skill_reconciliation.py -v`:
  **10 passed, 13 subtests passed** in 1.44s.
- `shb/shb-schedule`:
  `uv run pytest tests/test_workstation_update_workflow.py -k skills_refresh -v`:
  **19 passed** in 20.15s.

---

## 4. Concurrent Change & Archive Readiness

### 4.1 Concurrent Change Isolation
`git status --short` in `platform/openspec-store`:
- `openspec/changes/harden-omniroute-update-oci-burst-pacing-and-storage-hygiene/` remains untouched and untracked for its owning session.

### 4.2 Validation Ratchet Check
- `openspec validate --changes --strict --store openspec-store`: Passed (2/2 valid).
- `openspec validate migrate-openspec-1-17-skills-delivery-and-auto-sync --strict --store openspec-store`: Passed (0 errors, 0 warnings).
- `openspec validate --all --store openspec-store`: Passed (462/462 valid).
- Strict warning non-regression count on `openspec validate --all --strict --store openspec-store`: `160` legacy spec warnings (zero new regressions).
