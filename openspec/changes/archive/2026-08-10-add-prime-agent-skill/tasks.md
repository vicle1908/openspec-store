# Tasks: Add Prime Agent Coding CLI Skill

## 1. Create skill file

- [x] 1.1 Create `~/.hermes/skills/autonomous-ai-agents/prime-agent/SKILL.md` with YAML frontmatter and all sections from design.md. Use verified flags: `-p`, `-nt`, `-ns`, `-ne`, `-c`, `-r`, `--mode`, `--provider`, `--model`, `--thinking`, `--autonomous`.
- [x] 1.2 Verify skill loads via `skill_view(name='prime-agent')`.

## 2. Verify skill content against installed tool

- [x] 2.1 Run readiness commands: `command -v prime-agent`, `--version`, `model list`, `doctor`.
- [x] 2.2 Run preferred orchestration: `prime-agent -p --provider shopapikey --model fable-5 --no-session -nt -ns -ne "Reply: SKILL_OK"`.
- [x] 2.3 Verify all 3 providers work through the skill's recommended patterns.
- [x] 2.4 Verify autonomous mode: `prime-agent --autonomous --autonomous-max-turns 1 -p --provider shopapikey --model fable-5 "Reply: AUTO_OK"`.

## 3. Validate and commit

- [x] 3.1 Run `openspec validate add-prime-agent-skill --store openspec-store`.
- [x] 3.2 Run `python3 ~/Developer/openspec-store/scripts/sync-workspace-agent-skills.py` to sync workspace skills.
- [x] 3.3 Commit skill file with message "docs: add prime-agent coding CLI skill".
