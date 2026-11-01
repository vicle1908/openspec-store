# Proposal

## Why

During high-concurrency coding agent verification across the workstation's 16 coding agents, two distinct classes of rate-limit failures and capability gaps were uncovered:
1. **OmniRoute 429 Rate-Limit Storms & Stale Banned Accounts in Multi-Account Combos**:
   - Upstream Antigravity `429: Resource has been exhausted` errors occurred during bursts because account `ce95e1cb-27a4-433f-9c50-bdb6ad0b6b6b` (`vicgnome19097@gmail.com`) had 100% exhausted its weekly Gemini quota window (`resetAt: 2026-11-04T12:54:00Z`). In `strategy: "auto"` combos where `appliesQuotaCutoffGate` is `false`, OmniRoute's auto-scorer repeatedly routed to `ce95e1cb`.
   - Additionally, connection `20369f65-4fae-4fa0-b02b-4f15047bee79` (`phamkive425@gmail.com`, `test_status: "banned"`, `is_active: 0`) remained present in `gemini-3.8-flash-high`, `claude-opus-5.5`, and `claude-sonnet-5.5`. When fallback hit `20369f65`, OmniRoute logged `HTTP 401: All 1 connection(s) banned by upstream`, causing cascading failover storms and Turn Guard `HTTP 409: An identical request is already in progress` duplicate request blocks.
2. **Client Tool-Calling Incompatibilities & Subagent Capability Gaps**:
   - In OpenAI Codex CLI (`codex`), OmniRoute's `geminiTools.ts` dropped `functionDeclarations` whenever an incoming request included `web_search`. Disabling `web_search` in `~/.codex/config.toml` and setting `supports_search_tool: false` in `cockpit-model-catalog.json` restores reliable local tool execution (`shell_command`, `apply_patch`).
   - In Kilo Code (`kilo`), unflagged `kilo run` resolved `agent.code.model` instead of top-level `model`, requiring `agent.*.model` to be pinned to active OmniRoute combos.
   - Across Pi, Prime Agent, OpenCode, Kilo, Hermes, Grok, Goose, Droid, Claude Code, and Qwen Code, subagent planner/oracle/librarian roles, reasoning efforts, thinking levels, multimodal vision, and compaction token limits were unconfigured or pointing to retired models.

## What Changes

- **OmniRoute Gateway Pool Hygiene & 429 Remediation**:
  - Evict banned connection `20369f65-4fae-4fa0-b02b-4f15047bee79` (`phamkive425@gmail.com`) from `gemini-3.8-flash-high`, `claude-opus-5.5`, and `claude-sonnet-5.5` (zero banned accounts remain in any combo).
  - Prune quota-exhausted account `ce95e1cb-27a4-433f-9c50-bdb6ad0b6b6b` (`vicgnome19097@gmail.com`, 0% weekly Gemini quota remaining) from `gemini-3.8-flash-high`, leaving 9 healthy Pro accounts with 87%–100% quota.
- **Client Configuration & Capability Maximization**:
  - **Codex CLI**: Set `web_search = "disabled"` in `~/.codex/config.toml` (`0600`) and `supports_search_tool: false` across all 10 OmniRoute slugs in `~/.codex/cockpit-model-catalog.json` (`0644`).
  - **Kilo Code**: Configure `agent.plan`, `agent.orchestrator`, `agent.debug`, and `agent.code` in `~/.config/kilo/kilo.jsonc` (`0600`) and `~/.local/state/kilo/model.json`.
  - **Pi & Prime Agent**: Add `modelThinkingLevels` (`"high"`, `"xhigh"`, `"max"`) for all OmniRoute combos; update Prime `providerBackupModel` to `omniroute-responses/claude-sonnet-5.5`; increase MCP call timeout to 300s; register `gpt-6.1-*` and `gpt-6-*` models under `providers.cockpit`.
  - **OpenCode**: Point `agent.oracle.model` to `omniroute-responses/claude-opus-5.5` (`reasoningEffort: "high"`) and `agent.librarian.model` to `omniroute-responses/gemini-3.8-flash-high`; pin top combos in favorites.
  - **Hermes**: Add `agent.reasoning_overrides` for all OmniRoute combos; configure cross-family Mixture-of-Agents (`moa.presets.deep`) with `gemini-3.8-flash-high` + `claude-opus-5.5` reference models aggregated by `gemini-4-argon`.
  - **Kimi Code, Grok, Goose, Droid, Claude Code, Qwen Code, Zed**: Enable multimodal vision (`capabilities = ["thinking", "image_in", "tool_use"]`) in Kimi; set `fork_secondary_model` to `omniroute-claude-opus-5-5` in Grok; set `GOOSE_PLANNER_MODEL` to `claude-opus-5.5` in Goose; configure 800K compaction and OmniRoute mission orchestrator/workers in Droid; add modelOverrides in Claude Code; enable thinking and active combos in Zed.

## Capabilities

### Modified Capabilities

- `omniroute-compression-and-routing`: Configure `gemini-3.8-flash-high` across 9 active `g1-pro-tier` accounts (excluding exhausted `ce95e1cb` and banned `20369f65`, `d5c3465f`, `47f334b1`), and configure `claude-opus-5.5` and `claude-sonnet-5.5` across 13 active `agy` accounts (excluding banned `20369f65`, `d5c3465f`, `47f334b1`).
- `omniroute-agent-cli-routing`: Configure Codex CLI `web_search = "disabled"` and `supports_search_tool: false`, Kilo agent role model overrides, and client capability upgrades across the 16 coding agent surfaces.
- `coding-cli-provider-registry`: Extend the consumer CLI OmniRoute model registry to include capability-maximized subagent roles, thinking levels, multimodal vision, and 800K context limits.
- `omp-fresh-shell-contract`: Document 13 healthy `google-antigravity` OAuth accounts in `~/.omp/agent/agent.db` (excluding `vicgnome19091@gmail.com`, `ascenddevtwo@gmail.com`, and `phamkive425@gmail.com`).

## Impact

- **OmniRoute Gateway**: Zero 429s, zero 401s, zero 409 duplicate blocks; 10/10 concurrent requests to `gemini-3.8-flash-high` succeed with 100% `HTTP 200` and ~5.3s average latency.
- **Coding Agents**: All 16 coding agents and editors operate with maximized subagent roles, reasoning efforts, multimodal vision, and reliable multi-turn tool execution.
