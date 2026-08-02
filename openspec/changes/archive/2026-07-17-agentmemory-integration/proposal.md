---
**Status:** Draft  
**Date:** 2026-05-27  
**Author:** Claude Opus 4.6
---

# Agentmemory Integration — Proposal

## Context

Hiện tại mỗi session coding agent (Claude Code, pi, Codex CLI) đều bắt đầu từ zero — không biết
kiến trúc project, decisions trước đó, bugs đã gặp, patterns đã dùng. Mất ~5-15 phút mỗi session
để re-explain context.

**agentmemory** (rohitg00/agentmemory, 18K⭐) là persistent memory engine cho AI coding agents:
- 95.2% retrieval R@5 trên LongMemEval-S benchmark
- 92% fewer tokens vs LLM-summarized (~$10/năm vs $500/năm)
- 0 external DBs (iii-engine with durable state)
- 53 MCP tools + 12 auto hooks
- Hoạt động với Claude Code, Codex CLI, Cursor, Gemini CLI, OpenCode, pi, ...

## Why agentmemory (vs alternatives)

| Aspect | agentmemory | mem0 | Letta/MemGPT | Built-in (CLAUDE.md) |
|--------|------------|------|--------------|---------------------|
| Retrieval R@5 | **95.2%** | 68.5% | 83.2% | N/A (grep) |
| Auto-capture | 12 hooks | manual add() | agent self-edits | manual |
| External DBs | **None** | Qdrant/pgvector | Postgres+vector | None |
| Multi-agent | MCP+REST+leases | API only | Letta only | Per-agent files |
| Setup time | **~2 min** | ~30 min | ~2h | 0 |

## Scope

**In scope:**
- Install `@agentmemory/agentmemory` globally
- Wire MCP server vào Claude Code + pi agent config
- Cấu hình 12 hooks auto-capture
- Set memory lifecycle rules phù hợp TDT workspace
- Integrate với viewer để debug

**Out of scope:**
- Multi-agent coordination (dùng sau)
- Custom iii-engine plugins
- Cloud deployment (self-hosted local là đủ)

## Impact

- **Time savings**: ~10h/tháng không cần re-explain context
- **Token savings**: ~$10/năm vs status quo
- **New npm global package**: +1 (consistent với existing npm globals)
- **New MCP server**: +1 trên port 3111
