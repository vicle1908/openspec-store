# Tasks: Add Goose Coding Agent Skill

## Task 1: Create goose Hermes skill
- [x] Create `~/.hermes/skills/autonomous-ai-agents/goose/SKILL.md`
- [x] Include validated readiness commands
- [x] Include validated headless invocation patterns
- [x] Include validated provider overrides
- [x] Include validated system prompt, stats, output formats
- [x] Include validated code review patterns
- [x] Include complexity-adaptive limits (accounting for 55s cold start)
- [x] Include pitfalls and verification checklist
- [x] Validate skill loads with `skill_view(name='goose')`

## Task 2: Update coding-agent-capability-verification skill
- [x] Add goose to CLI Selection Rules
- [x] Add goose probe commands to references/headless-probes.md
- [x] Add goose validated features reference

## Task 3: Update AGENTS.md
- [x] N/A — no coding agent table exists in AGENTS.md

## Task 4: Update memory
- [x] Add goose: v1.45.0, 4 providers, headless mode, 136 MCP tools, code review, ACP

## Task 5: Verify end-to-end
- [x] Skill loads and appears in skills list

## Post-review fixes (6-agent review, 2026-08-08)
- [x] CRITICAL: Fix frontmatter — add version/author/license/platforms, metadata.hermes nesting
- [x] CRITICAL: Fix JSON parsing example in design.md (banner skip + -q flag)
- [x] HIGH: Fix extension count 16→17, skills type builtin→platform
- [x] HIGH: Fix provider models (gpt-5.6-luna, dlg/fable-5-v4-pro)
- [x] HIGH: Fix skills count 14→111
- [x] MEDIUM: Fix proposal AGENTS.md promise (remove, marked N/A in tasks)
- [x] MEDIUM: Validation claims already accurate (⚠️ markers for partial tests)
