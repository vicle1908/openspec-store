# Tasks: Add Agent Skills via `npx skills`

## Phase 1: CLI Tool Installation

- [x] 1.1 Install `@firecrawl/anydoc` globally: `npm install -g @firecrawl/anydoc`
- [x] 1.2 Verify: `anydoc --help` returns usage info
- [x] 1.3 Test conversion: created sample `.csv`, ran `anydoc sample.csv` — success

## Phase 2: Global Skill Installation

- [x] 2.1 Install anydoc skill: `npx skills add firecrawl/anydoc -g -y`
- [x] 2.2 Verify skill at `~/.agents/skills/convert-documents-to-markdown/SKILL.md`
- [x] 2.3 Verify Hermes symlink at `~/.hermes/skills/convert-documents-to-markdown/`
- [x] 2.4 Install Python skills: `npx skills add wshobson/agents -g -y --skill python-testing-patterns,python-design-patterns,python-performance-optimization`
- [x] 2.5 Install Go skill: `npx skills add samber/cc-skills-golang@golang-documentation -g -y`
- [x] 2.6 Install Docker skills: `npx skills add github/awesome-copilot@multi-stage-dockerfile -g -y`
- [x] 2.7 Install Docker patterns: `npx skills add affaan-m/everything-claude-code@docker-patterns -g -y`

## Phase 3: Verification

- [x] 3.1 Run `npx skills ls -g` — all 7 skills listed
- [x] 3.2 Check `~/.hermes/skills/` — all 7 skills symlinked
- [x] 3.3 Test `convert-documents-to-markdown` with CSV — success
- [x] 3.4 Python skills load in Hermes (visible in `~/.hermes/skills/`)
- [x] 3.5 No conflicts with existing Hermes skills

## Phase 4: Documentation

- [x] 4.1 AGENTS.md already documents research tools and skills
- [x] 4.2 Commit store changes
