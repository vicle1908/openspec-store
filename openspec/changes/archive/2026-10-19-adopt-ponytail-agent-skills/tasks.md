# Tasks

## 1. Upstream Ponytail Skills Installation and Lockfile Synchronization

- [x] 1.1 Install all six official `DietrichGebert/ponytail` skills (`ponytail`, `ponytail-review`, `ponytail-audit`, `ponytail-debt`, `ponytail-gain`, `ponytail-help`) from `/Users/androidteam/Developer` using `/opt/homebrew/bin/skills add DietrichGebert/ponytail --skill '*' --agent universal claude-code hermes-agent -y`, and verify that each canonical directory exists at `~/Developer/.agents/skills/<name>/SKILL.md` with exact uppercase `SKILL.md` casing.
- [x] 1.2 Verify that `~/Developer/skills-lock.json` records all six `ponytail*` skills with `"source": "DietrichGebert/ponytail"`, `"sourceType": "github"`, and `"skillPath": "skills/<name>/SKILL.md"`, synchronize those six entries into `~/Developer/.agents/skills-lock.json`, and verify via Python that both lockfiles parse cleanly and every `ponytail*` `SKILL.md` frontmatter description decodes to $\le 1,024$ UTF-8 bytes.
- [x] 1.3 Verify that workspace project symlinks resolve at `~/Developer/.claude/skills/ponytail*` and `~/Developer/.hermes/skills/ponytail*` (`../../.agents/skills/<name>`), while `~/Developer/.codex/skills/` remains untouched (containing only `.system/` and `migrate-to-codex`).

## 2. Multi-Agent Discovery Manifests and Symlink Reconciliation

- [x] 2.1 Add `ponytail`, `ponytail-audit`, `ponytail-debt`, `ponytail-gain`, `ponytail-help`, and `ponytail-review` to `~/Developer/platform/openspec-store/config/codex-user-skill-manifest.txt` and `~/Developer/platform/openspec-store/config/claude-user-skill-manifest.txt`, and verify both manifests contain no duplicate entries.
- [x] 2.2 Run `python3 ~/Developer/platform/openspec-store/scripts/sync-workspace-agent-skills.py` to reconcile user-scope symlinks, then run `python3 ~/Developer/platform/openspec-store/scripts/sync-workspace-agent-skills.py --check` and verify it exits with code `0` (`malformed_entries=0`, `conflicts=0`, `broken=0`) and that `~/.agents/skills/ponytail*` and `~/.claude/skills/ponytail*` resolve to `/Users/androidteam/Developer/.agents/skills/ponytail*`.

## 3. Recurring Update Compatibility and Non-Interference Verification

- [x] 3.1 Execute `/opt/homebrew/bin/skills update ponytail ponytail-review ponytail-audit ponytail-debt ponytail-gain ponytail-help -y` in `/Users/androidteam/Developer` and verify it exits with code `0`, reports `✓ All project skills are up to date`, keeps `~/Developer/skills-lock.json` valid, and prints zero `Multiple current paths match` warnings.
- [x] 3.2 Verify hook and statusline non-interference by inspecting `~/.claude/settings.json`, `~/Developer/.claude/settings.json`, and `~/.codex/hooks.json` to confirm `statusLine` remains bound to `/Users/androidteam/.orca/agent-hooks/claude-statusline.sh` and no `~/.claude/.ponytail-active`, `~/.claude/ponytail-statusline.sh`, or Ponytail hook entries were added.

## Workflow follow-up

- Validate the change and store strictly via `/Users/androidteam/.npm-global/bin/openspec validate adopt-ponytail-agent-skills --strict --json --store openspec-store`.
- Record execution verification in `evidence.md` during `/opsx:apply` before archiving.
