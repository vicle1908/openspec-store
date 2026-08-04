## 1. Evidence Collection

- [x] 1.1 Record installed Pi version, binary path, core help surface, installed packages, and non-secret effective defaults.
- [x] 1.2 Audit official pi.dev documentation for print/JSON modes, providers/models, sessions, context files, skills, extensions, and programmatic usage.
- [x] 1.3 Distinguish Pi core behavior from extension-provided flags and locally installed package behavior.

## 2. Skill Authoring

- [x] 2.1 Create `~/.hermes/skills/autonomous-ai-agents/pi/SKILL.md` with peer-matched frontmatter and structure.
- [x] 2.2 Document readiness checks, installation/update, authentication-safe checks, and preferred `pi -p` orchestration.
- [x] 2.3 Document model/provider selection, tool scoping, sessions, JSON output, context controls, extensions, skills, and interactive mode.
- [x] 2.4 Document complexity-adaptive timeout guidance, worktree isolation, external verification, and common pitfalls.

## 3. Verification

- [x] 3.1 Validate skill frontmatter, size, required sections, and related-skill references.
- [x] 3.2 Run a bounded Pi print-mode smoke probe without exposing credentials or mutating repositories.
- [x] 3.3 Reload the new skill and scan it for stale, contradictory, or unsupported guidance.
- [x] 3.4 Write `verification.md` with exact commands, outputs, and limitations.

## 4. OpenSpec Closure

- [x] 4.1 Run strict validation for `add-pi-coding-agent-skill` and all shared specs.
- [x] 4.2 Run `openspec store doctor` and confirm store changes belong to this change.
- [x] 4.3 Archive the completed change and commit the shared OpenSpec store.
