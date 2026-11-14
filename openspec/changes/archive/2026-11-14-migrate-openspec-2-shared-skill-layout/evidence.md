# Verification & Operating Evidence Ledger: migrate-openspec-2-shared-skill-layout

## 1. OpenSpec Single-Owner Authority & Global Configuration Baseline

### 1.1 Single-Owner CLI Executable Verification (`iosteam-mac-mini`)
```bash
which -a openspec && openspec --version && openspec version
```
Output:
```text
/Users/androidteam/.npm-global/bin/openspec
2.0.0
OpenSpec 2.0.0 (npm, global)
```
Verification:
- Only `/Users/androidteam/.npm-global/bin/openspec` is present on `PATH` (no Homebrew formula shadow).
- Backup captured before config mutation: `/tmp/openspec-config.pre-2.0.json` (`mode 0600`).

### 1.2 Global Configuration (`~/.config/openspec/config.json`)
Removed retired `"delivery"` key atomically and verified remaining keys:
```bash
jq '{has_delivery: has("delivery"), profile, defaultStore, workflow_count: (.workflows | length), workflows, completionTipSeen}' ~/.config/openspec/config.json
```
Output:
```json
{
  "has_delivery": false,
  "profile": "custom",
  "defaultStore": "openspec-store",
  "workflow_count": 12,
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
  "completionTipSeen": true
}
```
`openspec doctor --store openspec-store --json` reported `"healthy": true` with `"issues"` absent (`"status": []`).

---

## 2. Store Shared Skill Layout & Directory Hygiene (`platform/openspec-store`)

- `.agents/skills/.openspec-target` contains 8 targets: `claude own-files`, `codex`, `factory`, `junie`, `kilocode`, `kiro own-files`, `pi`, `qoder`.
- All 12 canonical `.agents/skills/openspec-*/SKILL.md` files are physical directories stamped with `metadata.generatedBy: "2.0.0"`.
- `.claude/skills/openspec-*` (12) and `.kiro/skills/openspec-*` (12) are relative symlinks (`../../.agents/skills/openspec-*`), totaling 24 `own-files` symlinks resolving to `.agents/skills/openspec-*`.
- All 60 redundant physical OpenSpec copies across `.factory/skills`, `.junie/skills`, `.kilocode/skills`, `.pi/skills`, and `.qoder/skills` are absent while Bright Data symlinks (`brightdata-cli`, `data-feeds`, `search`) and `.opencode/package.json` remain intact.
- `openspec update --dry-run --json /Users/androidteam/Developer/platform/openspec-store` output:
```json
{"changes": [], "notes": [], "failures": []}
```

---

## 3. Synchronizer, Unit Tests & Integration Gates

### 3.1 Linting & Focused Unit Suite
```bash
uv run --project ~/Developer/platform/openspec-store ruff check \
  ~/Developer/platform/openspec-store/scripts/sync-workspace-agent-skills.py \
  ~/Developer/platform/openspec-store/tests/test_ponytail_skill_reconciliation.py
uv run --project ~/Developer/platform/openspec-store pytest -p no:cacheprovider \
  ~/Developer/platform/openspec-store/tests/test_ponytail_skill_reconciliation.py -q
```
Output:
```text
All checks passed!
20 passed, 13 subtests passed in 2.93s
```

### 3.2 Live Workspace Reconciliation & Check Mode (Snapshot Preservation)
```bash
python3 ~/Developer/platform/openspec-store/scripts/sync-workspace-agent-skills.py
python3 ~/Developer/platform/openspec-store/scripts/sync-workspace-agent-skills.py --check
```
Output (`--check`):
```text
openspec_generator_parity=ok cli=2.0.0
canonical_direct_roots=116 containers=2 codex_selected=71 claude_selected=35 hermes_selected=11 openspec_targets=12 claude_commands=0 check=True
containers=generated,gitnexus
malformed_entries=0
workspace_agents: created=0 removed=0 conflicts=0 broken=0
user_agents: created=0 removed=0 conflicts=0 broken=0
workspace_claude_skills: created=0 removed=0 conflicts=0 broken=0
user_claude_skills: created=0 removed=0 conflicts=0 broken=0
user_hermes_skills: created=0 removed=0 conflicts=0 broken=0
workspace_claude_commands: created=0 removed=0 conflicts=0 broken=0
user_claude_commands: created=0 removed=0 conflicts=0 broken=0
snapshot_check=ok
```
Snapshot manifests stayed unrotated:
- `~/Developer/.agents/.skill-snapshots/current/manifest.json`: `2026-11-14 09:19:47`
- `~/Developer/.agents/.skill-snapshots/previous/manifest.json`: `2026-11-12 08:02:41`

### 3.3 `workstation-daily-update.sh --check`
- Stage 6/12 Cross-Agent Skills Parity Check: `openspec_generator_parity=ok cli=2.0.0`, `malformed_entries=0`, `claude_commands=0`, `snapshot_check=ok`.
- Stage 7/12 Script Provenance Drift Check: `checked=9 drifted=0 missing_record=0`.

---

## 4. Store-Wide Pytest, Toolchain, Doctor & OpenSpec Validation

- **Full `openspec-store` pytest suite** (`uv run --project ~/Developer/platform/openspec-store pytest -p no:cacheprovider ~/Developer/platform/openspec-store/tests -q`):
  `215 passed, 2 skipped, 29 subtests passed in 83.14s`
- **`shb-schedule` downstream caller suite** (`uv run --project ~/Developer/shb/shb-schedule pytest -p no:cacheprovider ~/Developer/shb/shb-schedule/tests/test_workstation_update_workflow.py -q`):
  `49 passed`
- **Isolated real-binary OpenSpec `2.0.0` E2E probes (`/tmp`)**:
  - `1.17.0 -> 2.0.0` released-fingerprint upgrade via real `/Users/androidteam/.npm-global/bin/openspec`: reconciled `12` canonical skills + `.openspec-target` + relative `.claude/skills` symlinks, swept `.pi/skills/openspec-explore`, and passed post-check (`rc=0`).
  - Custom/hand-edited `.claude`/`.pi` files retained on disk and failed closed (`rc=1`) without deleting user content.
  - `DISABLE_UPDATES` (`1`, `TRUE`, ` true `) suppressed `openspec update` in apply mode (`openspec_generator_parity=paused cli=2.0.0`, `rc=0`).
  - Live `~/.config/openspec/config.json` SHA-256 unchanged (`8d3648e28ff76fd14c91a469b6f93b6a595dbcafb6fad138dcc6b0d5f52bfab7`).
- **Toolchain verification** (`python3 ~/Developer/platform/openspec-store/scripts/verify-workstation-toolchain.py`):
  `overall_status: PASS` (`5/5` checks passed; `38 aligned, 0 drift, 0 missing, prefix=reconciled`)
- **`openspec validate --all --store openspec-store`**:
  `Totals: 463 passed, 0 failed (463 items)`
- **`openspec validate --all --strict --store openspec-store`**:
  `Totals: 304 passed, 159 failed (463 items)` (`159 <= 160` pre-existing main-spec baseline; zero new regressions)
- **`openspec validate --changes --strict --store openspec-store`**:
  `Totals: 3 passed, 0 failed (3 items)` (`migrate-openspec-2-shared-skill-layout` valid)
- **Concurrent change preservation**:
  `git -C ~/Developer/platform/openspec-store status --porcelain` partitions cleanly into `128` OpenSpec `2.0.0` entries and `2` untouched concurrent change directories (`?? openspec/changes/add-tailscale-media-relay-for-ios-and-peers/`, `?? openspec/changes/standardize-uv-script-execution-and-toolchain-resilience/`). Archive target `2026-11-14-migrate-openspec-2-shared-skill-layout` has zero collision.
