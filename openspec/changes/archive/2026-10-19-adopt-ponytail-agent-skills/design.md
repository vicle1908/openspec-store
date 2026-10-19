# Design

## Context

See `proposal.md` — Why for motivation.

The workstation operates 22 coding agent CLIs across 20+ repositories under `/Users/androidteam/Developer`, governed by `platform/openspec-store`. Source-level inspection of `/opt/homebrew/Cellar/skills/1.7.2/libexec/lib/node_modules/skills/dist/cli.mjs` and the workstation maintenance pipeline reveals four operational constraints that shape this design:

1. **Skills CLI Lockfile Resolution (`~/Developer/skills-lock.json` vs `~/Developer/.agents/skills-lock.json`)**:
   - In `skills` v1.7.2 (`cli.mjs:1093`), `getLocalLockPath(cwd)` is hardcoded to `join(cwd, "skills-lock.json")`. Both `skills add` and `skills update -y` (invoked from `cwd = /Users/androidteam/Developer` by `shb-schedule/src/shb_schedule/workflows/workstation_update.py:step_skills_refresh` and `~/Developer/scripts/workstation-daily-update.sh` Stage 11) read and write `/Users/androidteam/Developer/skills-lock.json`.
   - Meanwhile, `/Users/androidteam/Developer/.agents/skills-lock.json` is maintained as a companion workspace lockfile mirror (referenced by `workspace-openspec-skill-discovery/spec.md`). Keeping both files synchronized when adding new workspace skills ensures both live `skills update -y` runs and `.agents/skills-lock.json` audits see the same `ponytail*` entries.
2. **Project Agent Target Selection in `skills` v1.7.2 (`runAdd` and `updateProjectSkills`)**:
   - In `cli.mjs:2196` (`shouldSkipProjectAgentSymlink`) and `cli.mjs:7953-8060` (`updateProjectSkills`), project-scope updates in `/Users/androidteam/Developer` target `Universal` (`.agents/skills/`), `Claude Code` (`.claude/skills/`, `createProjectSkillsDirByDefault: true`), and `Hermes Agent` (`.hermes/skills/`, because `~/Developer/.hermes` exists). `codex`, `gemini-cli`, `opencode`, `pi`, `kimi-code-cli`, and `zed` are classified as `Universal` agents (`skillsDir: ".agents/skills"`), so `skills` never writes into `~/Developer/.codex/skills/`.
   - Passing `--agent universal claude-code hermes-agent -y` during initial `skills add` matches the exact target set that `skills update -y` uses on subsequent refreshes and guarantees symlink mode (`uniqueDirs.size === 3`: canonical directory in `~/Developer/.agents/skills/<name>` with relative symlinks `../../.agents/skills/<name>` in `~/Developer/.claude/skills/` and `~/Developer/.hermes/skills/`), even when ambient `AI_AGENT=hermes-agent` is set in the shell environment.
3. **Disambiguation of `.openclaw/skills/` During `skills update -y`**:
   - Upstream `DietrichGebert/ponytail` contains both `skills/<name>/SKILL.md` and `.openclaw/skills/<name>/SKILL.md`.
   - During `skills update -y`, `updateProjectSkills` (`cli.mjs:8005`) calls `discoverSkills(tempDir, void 0, { fullDepth: true, includeDuplicateNames: true })`, which finds both paths. However, because `supportsAppendedSubpath("DietrichGebert/ponytail")` is `true`, `cli.mjs:8012` passes `{ exactPathDisambiguates: true }` to `resolveSkillLocations` (`cli.mjs:7422`), which resolves `"skillPath": "skills/<name>/SKILL.md"` before checking `candidates.length > 1`. Thus, `skills update -y` updates `DietrichGebert/ponytail` cleanly with zero `Multiple current paths match` warnings.
4. **Existing Hook, Statusline, and Code-Intelligence Stack**:
   - `~/.claude/settings.json` binds `statusLine` to `/Users/androidteam/.orca/agent-hooks/claude-statusline.sh` and runs 3 hooks per lifecycle event (AgentMemory + iTerm2 `cc-status` + Orca `claude-hook.sh`), with 16 noisy ECC hooks disabled via `ECC_DISABLED_HOOKS` (`hooks-policy/spec.md`).
   - Codebase symbol discovery and blast-radius analysis are already served by **GitNexus** (20 indexed repos) and **Graphify**, while wire-level prompt/output compression is handled by **OmniRoute** (`RTK` + `Caveman`).

## Goals / Non-Goals

**Goals:**
- Install all six official `DietrichGebert/ponytail` skills (`ponytail`, `ponytail-review`, `ponytail-audit`, `ponytail-debt`, `ponytail-gain`, `ponytail-help`) via `/opt/homebrew/bin/skills` into `~/Developer/.agents/skills/` with lockfile entries in both `~/Developer/skills-lock.json` and `~/Developer/.agents/skills-lock.json`.
- Expose all six skills at both workspace scope (`~/Developer/.claude/skills/`, `~/Developer/.hermes/skills/`) and user scope (`~/.agents/skills/`, `~/.claude/skills/`) via `sync-workspace-agent-skills.py`.
- Guarantee zero-friction frequent updates via `npx skills update` / `skills update -y` by keeping upstream `SKILL.md` files unmodified.
- Prevent any collision with Orca's `statusLine`, AgentMemory/Codex hooks, OMP extensions, or `.codex/skills/` isolation.

**Non-Goals:**
- Installing Ponytail's Claude/Codex marketplace plugin (`hooks/claude-codex-hooks.json`, `hooks/claude-band.json`, `ponytail-statusline.sh`) or Pi/OMP extension (`pi-extension/index.js`).
- Modifying `shb-schedule`, `workstation-daily-update.sh`, or `sync-workspace-agent-skills.py` code.

## Decisions

### Decision 1: Adopt Official Skills Tier via `skills add --agent universal claude-code hermes-agent -y`
- **Choice:** Install using `/opt/homebrew/bin/skills add DietrichGebert/ponytail --skill '*' --agent universal claude-code hermes-agent -y` from `/Users/androidteam/Developer`, then sync the resulting `ponytail*` lock entries from `~/Developer/skills-lock.json` into `~/Developer/.agents/skills-lock.json`.
- **Rationale:**
  1. `DietrichGebert/ponytail`'s official `INSTALL.md` ("Skills CLI" section) documents `npx skills add DietrichGebert/ponytail --skill '*'` as the official skills-only installation method across agents.
  2. Explicitly targeting `universal claude-code hermes-agent` satisfies `agent-skill-distribution/spec.md` ("explicit agent selection") and matches the exact three project surfaces (`Universal`, `Claude Code`, `Hermes Agent`) that `skills update -y` (`updateProjectSkills` in `cli.mjs:7953-7964`) updates in `/Users/androidteam/Developer`.
  3. Omitting `--full-depth` ensures initial installation selects `skills/<name>/SKILL.md` (not `.openclaw/skills/<name>/SKILL.md`), which records `"skillPath": "skills/<name>/SKILL.md"` in `skills-lock.json` so future `skills update -y` runs disambiguate via `exactPathDisambiguates: true`.
- **Alternatives Considered:**
  - *Full Claude/Codex/OMP plugin marketplace install*: Rejected because `.claude-plugin/plugin.json` loads `hooks/claude-codex-hooks.json` (spawning Node.js on every `SessionStart`, `SubagentStart`, and `UserPromptSubmit`, plus running `ponytail-map.js` regex scans that duplicate GitNexus/Graphify) and `hooks/claude-band.json` / `ponytail-statusline.sh` (which nudges overwriting `~/.claude/settings.json` `statusLine`, breaking Orca's `claude-statusline.sh`).
  - *Global `npx skills add -g`*: Rejected because workspace-shared skills are canonically tracked in `~/Developer/.agents/skills/` and refreshed by `shb-schedule` / `workstation-daily-update.sh` from `~/Developer/skills-lock.json`, then linked into `~/.agents/skills/` and `~/.claude/skills/` via `sync-workspace-agent-skills.py`. If installed as real directories in `~/.agents/skills/` via `-g`, `sync-workspace-agent-skills.py` would report `user_agents.conflicts` (`workspace-openspec-skill-discovery/spec.md` Scenario: "Existing global installations are preserved / collision fails verification").

### Decision 2: Keep All Six Upstream `SKILL.md` Files Unmodified
- **Choice:** Install all six upstream skills (`ponytail`, `ponytail-review`, `ponytail-audit`, `ponytail-debt`, `ponytail-gain`, `ponytail-help`) verbatim without local edits.
- **Rationale:**
  1. Direct inspection of upstream `DietrichGebert/ponytail` v5.3.2 confirms all six `SKILL.md` files use valid YAML folded block scalars (`description: >`) with decoded UTF-8 byte lengths between 135 and 380 bytes—well below the 800-byte advisory and 1,024-byte hard limit in `skill-index-hygiene/spec.md`.
  2. None of the six `skills/<name>/` directories contain `.claude-plugin` or `.cursor-plugin` subdirectories (`NON_OFFICIAL_ENTRY_DIRS` in `sync-workspace-agent-skills.py`).
  3. Keeping upstream files unmutated guarantees that frequent `npx skills update` / `skills update -y` runs compare `latestHash === skill.entry.computedHash` (`cli.mjs:8039`) cleanly and fast-skip when up to date or overwrite cleanly when upstream releases a new version.
- **Alternatives Considered:** Cherry-picking a subset of the 6 skills or locally editing `SKILL.md` frontmatter. Rejected because local edits break `computedHash` idempotency on `skills update -y` and get overwritten on every upstream refresh.

### Decision 3: Fan Out to User Scope via `codex-user-skill-manifest.txt` and `claude-user-skill-manifest.txt`
- **Choice:** Append `ponytail`, `ponytail-audit`, `ponytail-debt`, `ponytail-gain`, `ponytail-help`, and `ponytail-review` to `platform/openspec-store/config/codex-user-skill-manifest.txt` and `platform/openspec-store/config/claude-user-skill-manifest.txt`, then run `python3 ~/Developer/platform/openspec-store/scripts/sync-workspace-agent-skills.py`.
- **Rationale:** `sync-workspace-agent-skills.py` creates symlinks in `~/.agents/skills/<name>` and `~/.claude/skills/<name>` pointing to `/Users/androidteam/Developer/.agents/skills/<name>`. Because they are symlinks, every future `npx skills update` in `~/Developer/` immediately updates all user-scope agents (Claude Code, Codex, OMP, Pi, Kimi Code, Grok Build, Goose, OpenCode, Qoder) without re-running `sync-workspace-agent-skills.py`.

## Risks / Trade-offs

- **[Risk] Lockfile divergence between `~/Developer/skills-lock.json` and `~/Developer/.agents/skills-lock.json`** → Mitigation: Synchronize the 6 `ponytail*` entries into `~/Developer/.agents/skills-lock.json` alongside `~/Developer/skills-lock.json` during installation and verify both files contain all 6 entries.
- **[Risk] Upstream adds a new skill or changes `SKILL.md` description length beyond 1,024 bytes in a future release** → Mitigation: `sync-workspace-agent-skills.py --check` and `skill-index-hygiene` validation catch malformed entries or oversized descriptions after `skills update -y`, while `skills-lock.json` provides deterministic rollback provenance.
- **[Risk] Accidental invocation of `.claude-plugin` or `statusLine` setup** → Mitigation: Only `skills/<name>/SKILL.md` directories are materialized by `skills add`; `hooks/` and `.claude-plugin/` are never copied into `.agents/skills/` or `.claude/plugins/`.

## Migration Plan

1. In `/Users/androidteam/Developer`, run:
   ```bash
   /opt/homebrew/bin/skills add DietrichGebert/ponytail --skill '*' --agent universal claude-code hermes-agent -y
   ```
2. Verify that `~/Developer/.agents/skills/{ponytail,ponytail-audit,ponytail-debt,ponytail-gain,ponytail-help,ponytail-review}/SKILL.md` exist, `~/Developer/.claude/skills/ponytail*` and `~/Developer/.hermes/skills/ponytail*` are relative symlinks, and `~/Developer/skills-lock.json` contains all 6 entries; synchronize those 6 entries into `~/Developer/.agents/skills-lock.json`.
3. Add the 6 `ponytail*` skill names to `platform/openspec-store/config/codex-user-skill-manifest.txt` and `platform/openspec-store/config/claude-user-skill-manifest.txt`.
4. Run `python3 ~/Developer/platform/openspec-store/scripts/sync-workspace-agent-skills.py` and verify `sync-workspace-agent-skills.py --check` exits `0` (`malformed_entries=0`, `conflicts=0`, `broken=0`).
5. Verify recurring update mechanics by running `/opt/homebrew/bin/skills update ponytail ponytail-review ponytail-audit ponytail-debt ponytail-gain ponytail-help -y` in `/Users/androidteam/Developer` and confirming `✓ All project skills are up to date` with exit code `0`.
6. **Rollback:** Run `/opt/homebrew/bin/skills remove ponytail ponytail-audit ponytail-debt ponytail-gain ponytail-help ponytail-review -y` in `/Users/androidteam/Developer`, remove the 6 entries from `~/Developer/.agents/skills-lock.json`, revert the 6 lines in `codex-user-skill-manifest.txt` and `claude-user-skill-manifest.txt`, and re-run `sync-workspace-agent-skills.py`.
