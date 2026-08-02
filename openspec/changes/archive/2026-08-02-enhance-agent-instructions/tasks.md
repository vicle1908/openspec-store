# Tasks: Enhance Agent Instructions

## Section 1: Root AGENTS.md Enhancements

- [x] 1.1 Add project overview (2-line tech stack summary) after the H1 heading
- [x] 1.2 Add Prerequisites section after Repository Map (Go version, Docker, kind, openspec, graphify)
- [x] 1.3 Replace stale "no commit history yet" text with Conventional Commit format template
- [x] 1.4 Add Agent Instruction Files navigation table listing all 5 subdirectory guides
- [x] 1.5 Add Common Pitfalls section with top 4 high-impact gotchas
- [x] 1.6 Verify root AGENTS.md word count stays within 200–550 range (actual: 542)

## Section 2: CLAUDE.md Reconciliation

- [x] 2.1 Add `@AGENTS.md` import at top of root CLAUDE.md for cross-agent portability
- [x] 2.2 Preserve existing graphify content below the import
- [x] 2.3 Verify CLAUDE.md loads correctly (no syntax errors)

## Section 3: Orphan Cleanup

- [x] 3.1 Remove `tools/agentguide/mcp-router.AGENTS.md` (orphaned file)
- [x] 3.2 Verify agentguide validator still passes (6 guides, 0 violations)

## Section 4: Validation

- [x] 4.1 Run `make validate-agent-guidance` — 6 guides, 60 checks, 0 violations
- [x] 4.2 Run `openspec validate enhance-agent-instructions --store openspec-store` — valid
- [x] 4.3 Run `openspec validate --strict --all --store openspec-store` — 94 passed, 0 failed
