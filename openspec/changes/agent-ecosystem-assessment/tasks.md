## 1. Validate Findings

- [x] 1.1 Run `uv run pytest` across all 3 repos — 1,141 pass, 1 skip
- [x] 1.2 Run `uv run ruff check src/` — all clean
- [x] 1.3 Run `uv run <cli> --help` — all 3 work offline
- [x] 1.4 Run `grep -rh 'from agent_core' src/` — coupling depth verified
- [x] 1.5 Run `openspec validate --strict --all` — 350/350 pass
- [x] 1.6 Verify module test ratios — llm_gateway (0.27), foundation (0.35) flagged

## 2. Update SPEC_INDEX Files

- [x] 2.1 Add test metrics section to agent-core SPEC_INDEX.md
- [x] 2.2 Add test metrics section to agent-docs-sync SPEC_INDEX.md
- [x] 2.3 Add test metrics section to agent-harness SPEC_INDEX.md
- [x] 2.4 Add cross-repo coupling notes
- [x] 2.5 Document spec coverage rationale for agent-config and agent-step-persistence

## 3. Commit

- [x] 3.1 Commit SPEC_INDEX updates across 3 repos
- [x] 3.2 Commit store change artifacts
