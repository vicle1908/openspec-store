# Proposal

## Why

Workspace coding agents lack a shared, upstream-maintained skill suite for reuse-first code minimization, blast-radius diff review, whole-repo quality auditing, and deliberate `shortcut:` technical-debt ledger tracking that updates cleanly via `npx skills`. Adopting the official `DietrichGebert/ponytail` skill distribution (`ponytail`, `ponytail-review`, `ponytail-audit`, `ponytail-debt`, `ponytail-gain`, `ponytail-help`) through the canonical `npx skills` (`/opt/homebrew/bin/skills` v1.7.2) workflow provides these capabilities across all agent harnesses while preserving zero-patch upstream upgradeability via `npx skills update` and avoiding collisions with Orca's Claude Code statusline, AgentMemory lifecycle hooks, and GitNexus/Graphify code intelligence.

## What Changes

- Install all six official `DietrichGebert/ponytail` skills (`ponytail`, `ponytail-review`, `ponytail-audit`, `ponytail-debt`, `ponytail-gain`, `ponytail-help`) into the canonical workspace skill root (`~/Developer/.agents/skills/`) using `/opt/homebrew/bin/skills add DietrichGebert/ponytail --skill '*' --agent universal claude-code hermes-agent -y`, recording their upstream GitHub provenance (`"source": "DietrichGebert/ponytail"`, `"skillPath": "skills/<name>/SKILL.md"`) and content hashes in `~/Developer/skills-lock.json` and synchronizing those entries into `~/Developer/.agents/skills-lock.json`.
- Register the six `ponytail*` skill slugs in `platform/openspec-store/config/codex-user-skill-manifest.txt` and `platform/openspec-store/config/claude-user-skill-manifest.txt`, then reconcile user-scope symlinks (`~/.agents/skills/<name>` and `~/.claude/skills/<name>`) via `scripts/sync-workspace-agent-skills.py`.
- Preserve unmodified upstream `SKILL.md` files in `~/Developer/.agents/skills/ponytail*` so frequent on-demand (`npx skills update` / `skills update -y`) and scheduled daily (`shb-schedule` `step_skills_refresh` and `workstation-daily-update.sh` Stage 11) refreshes succeed idempotently via `exactPathDisambiguates` without merge conflicts, path-ambiguity warnings, or malformed-entry failures.
- Enforce an explicit skills-only boundary that omits Ponytail's runtime Node.js lifecycle hooks (`hooks/claude-codex-hooks.json`), regex codebase mapper (`hooks/ponytail-map.js`), Pi/OMP runtime extension (`pi-extension/index.js`), and Claude Code UI band/statusline (`hooks/claude-band.json`, `ponytail-statusline.sh`) so existing Orca statusline telemetry (`~/.orca/agent-hooks/claude-statusline.sh`), AgentMemory hooks, and OMP/Hermes system prompts remain unmutated.

## Non-Goals

- Installing Ponytail's runtime lifecycle hooks (`SessionStart`, `SubagentStart`, `UserPromptSubmit`), which would add per-turn Node.js process overhead on top of AgentMemory, Orca, and iTerm2 `cc-status` hooks and run `ponytail-map.js` redundantly alongside GitNexus and Graphify.
- Installing or enabling Ponytail's Claude Code `band` (`hooks/band/register.tsx`) or `ponytail-statusline.sh`, which would overwrite `~/.claude/settings.json` `statusLine` and break `/Users/androidteam/.orca/agent-hooks/claude-statusline.sh` rate-limit and duration telemetry.
- Installing the Pi/OMP runtime extension (`pi-extension/index.js`), which would inject duplicate `before_agent_start` system prompt sections into OMP sessions.
- Forking, patching, or rewriting upstream `skills/ponytail*/SKILL.md` files locally, which would conflict with frequent `npx skills update` refreshes.

## Affected Ownership Boundaries

- **Workspace Shared Agent Skills (`~/Developer/.agents/skills/`, `~/Developer/skills-lock.json`, & `~/Developer/.agents/skills-lock.json`)**: Canonical project-scope skill directories (`ponytail`, `ponytail-review`, `ponytail-audit`, `ponytail-debt`, `ponytail-gain`, `ponytail-help`) and lockfile provenance across both the CLI-active root lockfile (`~/Developer/skills-lock.json`) and the `.agents` lockfile mirror (`~/Developer/.agents/skills-lock.json`).
- **Workspace Project Agent Mirrors (`~/Developer/.claude/skills/` & `~/Developer/.hermes/skills/`)**: Relative symlinks (`../../.agents/skills/<name>`) created by `skills add` and maintained by `skills update -y`.
- **OpenSpec Central Governance Store (`~/Developer/platform/openspec-store/`)**: User-scope fanout manifests (`config/codex-user-skill-manifest.txt`, `config/claude-user-skill-manifest.txt`), `scripts/sync-workspace-agent-skills.py` verification, and capability specification `openspec/specs/ponytail-agent-skills/spec.md`.
- **User-Scope Multi-Agent Discovery (`~/.agents/skills/` & `~/.claude/skills/`)**: Symlinks pointing to `~/Developer/.agents/skills/ponytail*`, consumed by Claude Code, Codex, OMP, Pi, Kimi Code, Grok Build, Goose, OpenCode, and Qoder.

## Capabilities

### New Capabilities
- `ponytail-agent-skills`: Governs canonical installation, lockfile provenance tracking (`~/Developer/skills-lock.json` and `~/Developer/.agents/skills-lock.json`), multi-agent manifest synchronization, recurring `npx skills update` compatibility, and hook/statusline non-interference for the official `DietrichGebert/ponytail` skill suite.

### Modified Capabilities

## Impact

- All six official Ponytail skills (`/ponytail`, `/ponytail-review`, `/ponytail-audit`, `/ponytail-debt`, `/ponytail-gain`, `/ponytail-help` and `$ponytail*` in Codex) become discoverable across workspace and user-level agent harnesses.
- Frequent upstream updates via `npx skills update` (or `skills update -y` in `~/Developer/` via `shb-schedule` `step_skills_refresh` and `workstation-daily-update.sh` Stage 11) automatically propagate through symlinks to all agents with zero manual re-linking.
- Zero breaking changes or runtime overhead added to Claude Code `statusLine`, Orca telemetry, AgentMemory hooks, OMP extensions, or OmniRoute compression.
