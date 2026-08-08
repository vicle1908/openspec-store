# Tasks: Add Goose Coding Agent Skill

## Task 1: Create goose Hermes skill
- [x] Create `~/.hermes/skills/autonomous-ai-agents/goose/SKILL.md`
- [x] Include validated readiness commands: `goose --version`, `goose info`, `goose skills list`
- [x] Include validated headless invocation: `goose run -t "..." --no-session -q --max-turns N`
- [x] Include validated provider overrides: `--provider custom_shopapikey --model fable-5`
- [x] Include validated system prompt: `--system "text"`
- [x] Include validated stats: `--stats` (Time to first token, Tokens/sec, Output tokens)
- [x] Include validated output formats: text, json, stream-json with JSON schema
- [x] Include validated code review: `goose review main...HEAD --dry-run`
- [x] Include validated complexity-adaptive limits (accounting for 55s cold start)
- [x] Include pitfalls: cold start ~55s, no --dangerously-skip-permissions, no cost cap, workspace restriction on file reader
- [x] Validate skill loads with `skill_view(name='goose')`

## Task 2: Update coding-agent-capability-verification skill
- [x] Add goose to CLI Selection Rules section with validated flags
- [x] Add goose probe commands to references/headless-probes.md
- [x] Add goose validated features to references/goose-validated-features.md
- [x] Add goose to verification checklist and pitfalls

## Task 3: Update AGENTS.md
- [x] N/A — no coding agent table exists in AGENTS.md; agent info lives in memory

## Task 4: Update memory
- [x] Add goose: v1.45.0, 4 providers, headless mode, 136 MCP tools, code review, ACP in Zed

## Task 5: Verify end-to-end
- [x] Skill loads: `skill_view(name='goose')` — loaded successfully
- [x] Skill listed in `skills_list()` under autonomous-ai-agents category
- [x] Headless smoke test: verified earlier (goose returned "OK")
- [x] Coding agent verification includes goose (CLI Selection Rules + headless-probes.md)

## Validated Test Results (2026-08-08)

| Test | Result | Notes |
|------|--------|-------|
| Default provider (openai/fable-5.6-luna) | ✅ | Cold start 55s, subsequent 14s |
| custom_shopapikey (fable-5) | ✅ | 14s |
| custom_giaoduc (Advance) | ✅ | 14s |
| --system prompt override | ✅ | "BANANA" returned as instructed |
| --stats | ✅ | TTFT 2.58s, 6.38 tok/s, 17 output tokens |
| --output-format json | ✅ | Full conversation + metadata envelope |
| --output-format stream-json | ✅ | Streaming JSON events |
| Coding task (write file) | ✅ | Created test.py, fell back to shell for verification |
| goose review --dry-run | ✅ | Printed review prompt structure |
| goose review (no changes) | ✅ | "no changes to review" |
| goose skills list | ✅ | 14 skills discovered |
| goose recipe list | ✅ | "No recipes found" (system works, no recipes) |
| --no-profile | ✅ | Skips extensions, still works |
