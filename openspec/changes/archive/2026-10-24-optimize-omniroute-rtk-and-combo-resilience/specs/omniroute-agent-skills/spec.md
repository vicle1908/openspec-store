# Spec Delta

## ADDED Requirements

### Requirement: OmniRoute v3.8.52 Agent Skill Accuracy and Clean Workspace Skill Surface

User-installed OmniRoute skills in `~/.agents/skills/` and workspace documentation (`docs/omniroute-agent-skills.md`, `wiki/entities/omniroute.md`) SHALL reflect v3.8.52 endpoints, 23 `omni-*` REST skills, 55 RTK filters, and loopback HTTP `$OMNIROUTE_URL` / `$OMNIROUTE_KEY` conventions while keeping `/Users/androidteam/Omniroute` git-clean and `sync-workspace-agent-skills.py --check` exiting `0`.

#### Scenario: Workspace skill surface validation passes without AstrBot `data/skills` violation
- **WHEN** `python3 ~/Developer/platform/openspec-store/scripts/sync-workspace-agent-skills.py --check` is executed after unlinking redundant symlinks in `~/Developer/data/skills`
- **THEN** it SHALL report `malformed_entries=0`, zero `surface_violations`, and exit with status code `0`

#### Scenario: Installed skills maintain custom block boundary and 500-line budget
- **WHEN** user-scope OmniRoute skills in `~/.agents/skills/` are enhanced with v3.8.52 operational recipes
- **THEN** custom guidance SHALL reside inside `<!-- skill:custom-start -->` and `<!-- skill:custom-end -->` markers and each `SKILL.md` SHALL NOT exceed 500 lines
