# Proposal: Add Goose Coding Agent Skill

## Why

Goose (v1.45.0, AAIF/Linux Foundation) is installed and fully configured on this Mac. Verified features include:
- **4 providers** all working: openai (fable-5.6-luna), custom_shopapikey (fable-5), custom_giaoduc (Advance), custom_omniroute (fable-5-pro)
- **16 extensions** enabled: developer (file/shell), analyze, orchestrator, todo, memory, skills, code_execution, summarize, chatrecall, apps, computercontroller, autovisualiser, extensionmanager, tutorial, tom, summon
- **136 MCP tools** via mcp-router integration
- **Headless mode** verified: `goose run -t "..." --no-session -q --max-turns N`
- **Code review** verified: `goose review main...HEAD`
- **ACP server** registered in Zed
- **JSON + streaming output** for programmatic parsing

However, Hermes lacks a dedicated orchestration skill for goose — unlike Claude Code, agy, Pi, OpenCode, and Codex which all have Hermes skills.

## What Changes

1. **New Hermes skill**: `goose` at `~/.hermes/skills/autonomous-ai-agents/goose/SKILL.md`
   - Headless orchestration (validated invocation patterns)
   - Provider override patterns (all 4 providers tested)
   - Code review integration
   - Output format parsing (json, stream-json)
   - Complexity-adaptive limits (accounting for 55s cold start)
   - Pitfalls and verification checklist

2. **Update**: `coding-agent-capability-verification` skill with goose probe commands

3. **Update**: Memory entry for coding agents (no AGENTS.md change needed — no coding agent table exists there)

4. **Update**: Memory entry for coding agents

## Compatibility

- Purely additive — no breaking changes
- Goose already installed and configured
- Existing providers, extensions, and mcp-router unchanged
