# Tasks: agent-device Skill (Callstack Bundled, First-Class)

This change installs the upstream `callstack/agent-device` skill into the **first-class TDT skills root** (`tdt-meta/.agents/skills/agent-device/SKILL.md`) via `npx skills add ... --copy -y`, after the operator installs the matching `agent-device` CLI globally with a pinned version. No custom skill authoring. The Callstack canonical skill is the skill. The skill is **committed to git** (the `--copy` flag is mandatory for portability).

## 1. Operator-Side CLI Install Gate (must succeed before Section 2)

- [x] 1.1 Confirm `node --version` returns `v22.x` or higher — verified `v22.22.3`
- [x] 1.2 Confirm `npm --version` returns a version — verified `10.9.8`
- [x] 1.3 Confirm `npm config get prefix` is on the operator's PATH — verified `/Users/lekhanhvinh/.npm-global` is on `PATH`
- [x] 1.4 Run `which agent-device` to confirm whether a global `agent-device` CLI is already installed — verified not installed (operator gate applies)
- [x] 1.5 Operator prompted to choose pinned version; floor `>= 0.14.0`, latest `0.17.6`; agent MUST NOT run `npm install -g` autonomously — surfaced in ask-question
- [x] 1.6 Operator ran `npm install -g agent-device@0.17.6` (user-approved pinned install; `@latest` not used)
- [x] 1.7 Verify `agent-device --version` — returns `0.17.6`, satisfies floor `>= 0.14.0`
- [x] 1.8 No upgrade blocker (version is above floor)
- [x] 1.9 `agent-device help workflow` returns non-empty version-matched help
- [x] 1.10 Rule documented in spec (`agent-device-skill-install/spec.md` Requirement: "Operator-level CLI install with a pinned version is mandatory") and reinforced in `.agents/INDEX.md` entry (Section 3.3)

## 2. Install the Skill into the First-Class TDT Skills Root

- [x] 2.1 Confirm `npx skills --help` succeeds — verified `skills@1.5.11`
- [x] 2.2 Run `npx skills add callstack/agent-device -a universal -a codex -a cursor --copy -y` from `tdt-meta/` — succeeded; output `Installed 2 skills: agent-device (copied), dogfood (copied)` → all 3 agents resolved to `tdt-meta/.agents/skills/agent-device/`
- [x] 2.3 Skill installed at `tdt-meta/.agents/skills/agent-device/SKILL.md` (~40 lines, `name: agent-device`, references `agent-device help workflow`)
- [x] 2.4 `file` reports `ASCII text, with very long lines (435)` — **regular file, NOT symlink** (`--copy` honored)
- [x] 2.5 Description frontmatter mentions Apple (iOS, tvOS, macOS), Android, snapshots/screenshots, tapping, typing, scrolling, extracting UI info, logs/network/perf evidence, CLI commands
- [x] 2.6 Workspace symlink resolves: `ls -la ~/Developer/tdt/.agents/skills/agent-device/` shows the same `SKILL.md` (1915 bytes)

## 3. Workspace Pointer (`.agents/INDEX.md`, not `AGENTS.md`)

- [x] 3.1 `wc -l tdt-meta/AGENTS.md` → `271` (over 150-line cap, confirmed)
- [x] 3.2 SKIP adding a bullet to `AGENTS.md` per the 150-line cap rule
- [x] 3.3 Added "Mobile Device Automation (2026-06-17)" section to `tdt-meta/.agents/INDEX.md` with the canonical entry (skill path, version gate, operator-only install rule, thin-router scope, MCP opt-in pointer)
- [x] 3.4 Added "In-Flight Projects (1)" sub-section in `tdt-meta/openspec/INDEX.md` with the `agent-device-skill` row registering the four capability names: `agent-device-skill-install`, `agent-device-verify-loop`, `agent-device-command-surface`, `agent-device-mcp-integration`

## 4. Skills Index

- [x] 4.1 Manual edit skipped — `build-skills-index.sh` regenerates `SKILLS_INDEX.md` from `.agents/skills/` and handles the category layout automatically. `agent-device` appears alphabetically between `agent-core-usage` and `agent-onboarding`.
- [x] 4.2 Manual edit skipped — description in the index is auto-derived from the frontmatter (first 180 chars): "Automates Apple-platform apps (iOS, tvOS, macOS) and Android devices. Use when navigating apps, taking snapshots/screenshots, tapping, typing, scrolling, extracting UI info, collecting logs/network/perf evidence, or planning agent-device CLI commands." — Truncated to 180 chars per script logic.
- [x] 4.3 Total skills went from 95 → 103 (not 96) because the same `npx skills add` command also installed `dogfood` (the other bundled skill in `callstack/agent-device`) and the index was already stale relative to other recent skill additions since 2026-06-04. The script auto-handles the count.
- [x] 4.4 Ran `bash config/codex/scripts/build-skills-index.sh` — output: `Index complete: 103 skills indexed; Output: .codex/skills-index.json`
- [x] 4.5 Ran `bash config/codex/scripts/skill-validation-check.sh` — output: `{"status": "success", "message": "103 skills available", "details": {"skill_count": 103, "index_current": true, ...}}`
- [x] 4.6 `jq '.skills[] | select(.name == "agent-device")' .codex/skills-index.json` returns the new entry with `id: agent-device`, full description, and empty `dependencies`/`license`/`compatibility`/`metadata` (no metadata block in Callstack's skill frontmatter, which is expected for a thin router)

## 5. Validation

- [x] 5.1 `openspec validate agent-device-skill --strict` → `Change 'agent-device-skill' is valid` ✓
- [x] 5.2 `diff` of installed `SKILL.md` vs upstream canonical → `DIFF EXIT 0`; SHA-256 `7a1fdc6874791c7e635ea74ecb96eac3dd2332397f49e9c3d9d9a1096b4cd9a0` matches upstream ✓
- [x] 5.3 `agent-device --version` → `0.17.6` ≥ `0.14.0`; `agent-device help workflow` → non-empty output; both pass ✓
- [x] 5.4 `file` reports `ASCII text, with very long lines (435)` — NOT symlink; `--copy` was honored ✓
- [x] 5.5 No Python imports (`import`, `tdt_core`, `agentmemory`) in the skill — it's a pure shell/router SKILL.md ✓
- [x] 5.6 No `package.json` added or modified in workspace root (confirmed via `git status --porcelain`) ✓
- [x] 5.7 No `.cursor/mcp.json` or `.mcp.json` committed (MCP is opt-in, per-operator) ✓
- [x] 5.8 See Section 6 git status (git status is run before commit as part of Section 6)

## 6. Finalize

- [x] 6.1 `git status` confirms only expected changes staged (skill file, 4 spec files, index entries, `INDEX.md` bullet). Pre-existing dirty files (android-pmp-connection-center, jira-catalog-tab, etc.) left un-staged per "protect state" rule.
- [x] 6.2 `git diff --stat` — 15 files changed, 1141 insertions, 78 deletions. Size is within expected range (OpenSpec artifacts + 2 skill files + index updates). `.codex/skills-index.json` is tracked in this repo and legitimately updated by the build script.
- [x] 6.3 Committed inside `tdt-meta/` (never from `~/Developer/tdt/`) with message: `feat(skills): add callstack/agent-device bundled skill for mobile app verification` — SHA `3cb4e9b`
- [x] 6.4 Archive DEFERRED — per task spec, `openspec archive agent-device-skill --yes` will only be run after the skill ships and at least one real device-verification task has used it successfully

## Rollback

If the skill is removed or replaced:

1. Delete `tdt-meta/.agents/skills/agent-device/SKILL.md`
2. Revert the entry in `tdt-meta/.agents/SKILLS_INDEX.md` and the count (96 → 95)
3. Re-run `bash config/codex/scripts/build-skills-index.sh`
4. Revert the `tdt-meta/.agents/INDEX.md` bullet
5. Revert the `tdt-meta/openspec/INDEX.md` capability registration
6. The `agent-device` npm package on the operator machine is independent of the workspace; the user can run `npm uninstall -g agent-device` if they want to remove the tool too

There is no committed `.cursor/mcp.json`, no source-repo change, and no Python code to roll back.
