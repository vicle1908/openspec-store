# Tasks: Add Agent Skills via `npx skills`

## Phase 1: CLI Tool Installation

- [ ] 1.1 Install `@firecrawl/anydoc` globally: `npm install -g @firecrawl/anydoc`
- [ ] 1.2 Verify: `anydoc --help` returns usage info
- [ ] 1.3 Test conversion: create a sample `.docx` and run `anydoc sample.docx`

## Phase 2: Global Skill Installation

- [ ] 2.1 Install anydoc skill: `npx skills add firecrawl/anydoc -g -y`
- [ ] 2.2 Verify skill at `~/.agents/skills/convert-documents-to-markdown/SKILL.md`
- [ ] 2.3 Verify Hermes symlink at `~/.hermes/skills/convert-documents-to-markdown/`
- [ ] 2.4 Install Python skills: `npx skills add wshobson/agents -g -y --skill python-testing-patterns,python-design-patterns,python-performance-optimization`
- [ ] 2.5 Install Go skill: `npx skills add samber/cc-skills-golang@golang-documentation -g -y`
- [ ] 2.6 Install Docker skills: `npx skills add github/awesome-copilot@multi-stage-dockerfile -g -y`
- [ ] 2.7 Install Docker patterns: `npx skills add affaan-m/everything-claude-code@docker-patterns -g -y`

## Phase 3: Verification

- [ ] 3.1 Run `npx skills ls -g` — confirm all 7 skills listed
- [ ] 3.2 Check `~/.hermes/skills/` — confirm all skills symlinked
- [ ] 3.3 Test `convert-documents-to-markdown` with a sample file
- [ ] 3.4 Test Python skills load in Hermes session
- [ ] 3.5 Verify no conflicts with existing Hermes skills

## Phase 4: Documentation

- [ ] 4.1 Update AGENTS.md "Skills" section if needed
- [ ] 4.2 Commit store changes
