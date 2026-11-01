# Design

## Context

See `proposal.md` — Why for motivation.

This change directly addresses findings from live high-concurrency coding agent verification across the workstation's 16 coding agents and Dockerized OmniRoute v3.8.52 gateway:
- **Two 429 Classes**: Upstream quota exhaustion on `ce95e1cb` (`vicgnome19097@gmail.com`) vs pre-dispatch filter rejections caused by cascade failover storms from banned `20369f65` (`phamkive425@gmail.com`).
- **Tool-Calling Translation Bug**: In OmniRoute's `geminiTools.ts`, incoming requests with `web_search` dropped `functionDeclarations`. Disabling `web_search` in Codex CLI restores full tool execution.

## Goals / Non-Goals

**Goals:**
- Prune banned connection `20369f65` from `gemini-3.8-flash-high`, `claude-opus-5.5`, and `claude-sonnet-5.5` so 0 banned accounts remain in any combo.
- Prune quota-exhausted `ce95e1cb` (0% Gemini weekly quota) from `gemini-3.8-flash-high`, leaving 9 healthy Pro accounts with 87%–100% quota.
- Apply capability-maximizing configurations across all 16 coding agents (subagent planner/oracle/librarian roles, reasoning efforts, thinking levels, multimodal vision, 800K compaction).
- Maintain mode `0600` on provider configs and mode `0644` on `cockpit-model-catalog.json`.

**Non-Goals:**
- Adding `ce95e1cb` back to `gemini-3.8-flash-high` before its weekly quota resets on `2026-11-04T12:54:00Z`.
- Modifying git-tracked source files inside `/Users/androidteam/Omniroute`.

## Decisions

### Decision 1: Account Pruning and Pool Boundaries

- **Choice**:
  - `gemini-3.8-flash-high`: 9 active `g1-pro-tier` accounts (`ea0d6c23`, `38782750`, `a59369ac`, `9d66311f`, `615a4993`, `d71506bf`, `cdac4585`, `d902fb26`, `e85dd569`), excluding exhausted `ce95e1cb` and banned `20369f65`, `d5c3465f`, `47f334b1`.
  - `claude-opus-5.5` & `claude-sonnet-5.5`: 13 active `agy` accounts (10 Pro + 3 Ultra), excluding banned `20369f65`, `d5c3465f`, `47f334b1`. (`ce95e1cb` is retained here because its Claude quota is 94.8% healthy).
- **Rationale**: Upstream 429 errors only happen when an account with 0% quota is sent requests. Pruning `ce95e1cb` from Gemini while keeping it in Claude eliminates 100% of upstream 429s without reducing Claude capacity.

### Decision 2: Codex CLI Tool Protection via `web_search = "disabled"`

- **Choice**: Set `web_search = "disabled"` in `~/.codex/config.toml` (`0600`) and `supports_search_tool: false` in `~/.codex/cockpit-model-catalog.json` (`0644`).
- **Rationale**: OmniRoute's `chunks/37174.js` (`geminiTools.ts`) drops `functionDeclarations` when `googleSearch` is present. Disabling `web_search` prevents Codex from injecting the search tool item, ensuring `shell_command` and MCP tools are faithfully passed to Gemini models.

### Decision 3: Subagent Role and Capability Maximization Matrix

- **Pi**: `modelThinkingLevels` mapped for all 10 OmniRoute combos + Cockpit GPT-6.x models.
- **Prime Agent**: `providerBackupModel` set to `omniroute-responses/claude-sonnet-5.5`; MCP call timeout set to 300s.
- **OpenCode**: `agent.oracle.model` -> `omniroute-responses/claude-opus-5.5`; `agent.librarian.model` -> `omniroute-responses/gemini-3.8-flash-high`.
- **Kilo Code**: `agent.{plan,orchestrator}` -> `omniroute-responses/claude-opus-5.5`; `agent.debug` -> `omniroute-responses/claude-sonnet-5.5`; `agent.code` -> `omniroute-responses/gemini-3.8-flash-high`.
- **Hermes**: `agent.reasoning_overrides` mapped; Mixture-of-Agents (`moa.presets.deep`) configured with `gemini-3.8-flash-high` + `claude-opus-5.5` reference models.
- **Kimi Code**: Multimodal vision enabled (`capabilities = ["thinking", "image_in", "tool_use"]`).
- **Grok Build**: `ui.fork_secondary_model` -> `omniroute-claude-opus-5-5`.
- **Block Goose**: `GOOSE_PLANNER_MODEL` -> `claude-opus-5.5`.
- **Factory Droid**: `compactionTokenLimit` -> `800000`; mission orchestrator -> `custom:OmniRoute-claude-opus-5-5`.
- **Claude Code**: `modelOverrides` mapped for all 10 combos + `claude-opus-4-6` / `claude-sonnet-4-6` -> 5.5.
- **Qwen Code & Zed**: `maxOutputTokens: 65536` on Qwen; thinking enabled and combos pinned in Zed.

## Risks / Trade-offs

- **Risk: Pro Gemini account pool temporarily reduced from 11 to 9** → **Mitigation**: All 9 remaining Pro accounts have 87%–100% remaining quota; 10 concurrent requests succeed in ~5.3s without queueing. When `ce95e1cb` resets on 2026-11-04, it can be re-evaluated.
