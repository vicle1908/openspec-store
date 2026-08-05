# Evaluation Report

Date: 2026-08-05

## Executive Summary

The live Pi setup is powerful but unusually broad. Core Pi v0.83.0 is extended by seven global packages plus one custom global `agentmemory` extension, with direct MCP exposure from `mcp-router` and a default trusted root of `/Users/androidteam/Developer`. The environment supports subagents, MCP proxy and direct tools, web research, live code diagnostics, inter-session messaging, custom providers, GitNexus augmentation, and a custom memory service. It also has three high-priority hardening issues: inline secrets stored in world-readable config files, overbroad project trust, and an oversized direct MCP surface that contradicts the adapter's own prompt-cost warning.[1][2][3][4][5][9][10][11][12][13][14][15][17]

## Verified Live Configuration

### Pi core and global settings

- Pi version is `0.83.0`, with default provider `shoapikey`, default model `fable-5`, default thinking `xhigh`, websocket transport, and compaction enabled at `reserveTokens=16384` / `keepRecentTokens=20000`.[1][2][9]
- `defaultProjectTrust` is not explicitly set, so noninteractive unresolved projects fall back to `ask`, which means project-local resources are ignored unless the run has a saved trust decision or uses `--approve`.[1][2]
- `enableInstallTelemetry` is disabled, but update checks still occur unless `PI_SKIP_VERSION_CHECK=1` or `PI_OFFLINE=1` are set.[2][4][9]
- `trust.json` trusts `/Users/androidteam/Developer` wholesale, so every repo beneath that path can load project `.pi` resources, install project packages, and execute project extensions once Pi resolves the path as trusted.[1][2]

### Providers and models

- The configured default provider `shoapikey` points at `api.phanmemvip.shop` using an Anthropic-compatible Messages API and exposes model `fable-5` with a manually configured 1M context window and 128k max tokens.
- Additional local gateway providers (`cockpit`, `omniroute`) are configured through localhost endpoints with several manually declared models and large custom context windows.[4][17]
- Provider secrets are stored inline in `~/.pi/agent/models.json`, which is mode `0600`. That file is owner-only readable, but inline-secret storage still increases blast radius compared with environment-only or external secret-helper patterns.[4][17]

### Installed packages and custom extension

The current global package set is:

1. `pi-subagents` 0.40.0 — subagent orchestration, chains, async fleet, intercom bridge, direct MCP child selection, and worktree-aware delegation.[11]
2. `pi-web-access` 0.18.0 — web search, fetch/extract, GitHub cloning, PDFs, YouTube/video analysis, and curator workflow.[12]
3. `pi-intercom` 0.9.2 — local brokered session messaging and supervisor escalation patterns.[15]
4. `pi-setup-custom-providers` 1.0.1 — provider/model discovery and configuration wizard.[17]
5. `pi-lens` 3.8.74 — LSP diagnostics, structural analysis, formatting/autofix, language-aware agent tools, and project review intelligence.[13]
6. `pi-mcp-adapter` 2.20.1 — proxy/direct MCP tools, OAuth, UI surfaces, config imports, and MCP scripting.[10]
7. `pi-gitnexus` 0.6.4 — GitNexus graph augmentation and seven explicit graph tools.[14]

Additionally, a custom `agentmemory` global extension is loaded from `~/.pi/agent/extensions/agentmemory/`. It registers `memory_health`, `memory_search`, and `memory_save`, injects search results into the system prompt before agent runs, and attempts to persist observations to a local service at `http://localhost:3111`. The service is currently unreachable, so the extension is loaded but effectively degraded.[17]

## Supported Additional Features Beyond Core Pi

### 1. Subagents and chains

Core Pi intentionally omits built-in subagents, but the installed `pi-subagents` package adds:

- builtin agents (`scout`, `researcher`, `planner`, `worker`, `reviewer`, `context-builder`, `oracle`, `delegate`)
- chain files (`.chain.md`, `.chain.json`)
- background/foreground runs
- worktree-based isolation
- nested delegation caps
- direct MCP child selection in child frontmatter via `mcp:<server>`
- per-agent memory and extension allowlists.[11]

A live print-mode `subagent doctor` probe reported the extension as generally healthy, discovered 9 executable builtin agents and 10 skills, but also revealed a print-mode lifecycle problem: the doctor output timed out after printing instead of exiting cleanly. This suggests some print-mode subagent flows should be treated as long-running unless bounded externally.

### 2. MCP proxy, direct tools, prompts, scripting, and UI

`pi-mcp-adapter` is the most important additional capability in this setup. Official docs describe proxy mode as the default and direct tools as an optional prompt-cost tradeoff.[10] The live config instead uses:

- `~/.pi/agent/mcp.json`
- import compatibility from `cursor` and `claude-code`
- one explicit server `mcp-router`
- `directTools: true`
- a literal inline `MCPR_TOKEN` in the `env` block
- default `toolPrefix: "server"`, yielding names like `mcp_router_brave_web_search`.[10][17]

Verified behavior:

- The direct tool name is `mcp_router_brave_web_search`, not `brave_web_search`.[10][17]
- `--tools mcp_router_brave_web_search` successfully allows that direct MCP tool in Pi print mode.
- `--tools read` filters the direct MCP tool out; the model reported it unavailable and returned the requested sentinel. This disproves the prior claim that Pi `--tools` cannot filter direct MCP tools.
- Using the `mcp` proxy tool also works and can discover the exact direct-tool name.[10]

The adapter supports much more than we originally documented:

- host-config imports (`cursor`, `claude-code`, `claude-desktop`, `opencode`, `vscode`, `windsurf`, `codex`)
- lazy/eager/keep-alive/lazy-keep-alive server lifecycles
- per-tool approval gates
- output guards
- direct-tool freezing
- MCP prompts as slash commands
- elicitation dialogs
- MCP UI surfaces with optional native Glimpse rendering on macOS
- `mcpScript` for JS-based multi-call MCP workflows.[10]

### 3. Web research and extraction

`pi-web-access` provides a substantial built-in research surface: `web_search`, `fetch_content`, `get_search_content`, `source_check`, search curator UI, GitHub repo cloning, YouTube/video understanding, PDF extraction, and multiple provider fallbacks.[12]

Live config uses `~/.pi/web-search.json` with provider `exa`, plus configured `exaApiKey`, `perplexityApiKey`, and `geminiApiKey`, GitHub cloning enabled, and curator workflow on. That file is mode `0644`, which means the secrets inside are world-readable to the local account namespace. This is the clearest immediate hardening problem in the Pi setup.[12][17]

### 4. Diagnostics, structural analysis, and code-quality tooling

`pi-lens` adds an extensive diagnostics and project-intelligence surface beyond core Pi:

- `lens_diagnostics`, `lsp_diagnostics`, `lsp_navigation`
- AST-aware search/replace and outlines
- `module_report`, `read_symbol`, `read_enclosing`, `symbol_search`
- formatter/autofix hooks
- read-before-edit guard and review-graph intelligence.[13]

It also supports per-user `~/.pi-lens/config.json`, per-project `.pi-lens.json`, CLI flags, and environment variables with explicit precedence. No local Lens config file exists here, so the install is currently running on defaults.[13][17]

### 5. Inter-session coordination

`pi-intercom` adds local 1:1 messaging, ask/reply flows, keyboard shortcuts, broker auto-start, child supervisor escalation, attachment transport, and extension channels.[15] No explicit intercom config file exists, so defaults apply. Because `pi-subagents` now provides native supervisor messaging even without `pi-intercom`, this package remains useful mainly for user-driven and peer-session coordination rather than as a hard dependency of child runs.[11][15]

### 6. Knowledge-graph augmentation

`pi-gitnexus` is installed and provides both automatic augmentation of read/search results and seven explicit graph tools, but it depends on `gitnexus` being installed and the repo being indexed first.[14] This is useful for graph-rich code exploration, but it is not zero-config in a fresh repo.

### 7. Custom provider management

`pi-setup-custom-providers` provides a TUI wizard for local/remote provider discovery and compatibility settings across Ollama, fable-5.cpp, LM Studio, OpenRouter, Together, Groq, DeepSeek, Mistral, Anthropic, fable-5, and other gateways.[17] It is useful because this host already relies heavily on custom provider definitions.

## Security and Performance Assessment

### High-priority issues

1. **World-readable secrets in `~/.pi/web-search.json`** — mode `0644` with inline API keys for Exa, Perplexity, and fable-5. This should be corrected immediately.[12][17]
2. **World-readable MCP config with inline token** — `~/.pi/agent/mcp.json` is mode `0644` and contains a literal `MCPR_TOKEN` in `env`. The file should be owner-only and ideally should reference an environment variable instead of storing the token inline.[10][17]
3. **Overbroad trusted root** — trusting `/Users/androidteam/Developer` means every repo under that tree can load `.pi/settings.json`, `.pi/extensions`, `.pi/skills`, `.mcp.json`, install project packages, and execute project code when trusted resources exist.[1][2][17]
4. **Excessive direct MCP prompt footprint** — the adapter itself recommends direct tools for targeted sets of 5–20 and warns about 75+ direct tools. The current setup resolves 77 direct tools from `mcp-router`, which increases context overhead and weakens Pi's “minimal prompt” advantage.[10][17]
5. **Gateway file-descriptor leak is outside Pi but affects Pi evaluation** — the repeated `Errno 24` failures were caused by the Hermes gateway process holding ~300 FDs with many repeated `state.db` / `state.db-wal` handles, not by a proliferation of Pi child processes. This means future Pi validation inside Hermes can become flaky until the gateway issue is fixed.

### Medium-priority issues

6. **Inline secrets in `models.json`** — protected by mode `0600`, but still not ideal operationally.[17]
7. **`agentmemory` extension loaded while service is down** — harmless but noisy, and it silently degrades a global context-injection feature.[17]
8. **`pi-web-access` broad provider surface** — useful, but every enabled provider expands operational and secret-management complexity.[12]
9. **No explicit `defaultProjectTrust` policy** — currently implicit `ask` is safe for unknown repos, but because the Developer root is already trusted, the practical protection is much weaker than the docs imply.[1][2][17]

### Strengths

- The setup already supports an unusually rich Pi ecosystem: subagents, MCP, research, diagnostics, graph analysis, intercom, custom providers, and memory augmentation.[10][11][12][13][14][15][17]
- Compaction is enabled and reasonably conservative for long sessions.[1][2]
- Pi core itself remains aligned with official design principles: minimal tool core, trust gating for local resources, no fake sandbox, and strong extensibility.[1][2][3][4][5][6][7][8][9]

## Configuration Recommendations

### Immediate

1. Change `~/.pi/web-search.json` and `~/.pi/agent/mcp.json` to mode `0600` and migrate inline secrets to environment-variable references where supported.[10][12][17]
2. Reduce trust from `/Users/androidteam/Developer` to only the few project roots that genuinely need project-local Pi resources.[1][2]
3. Replace `directTools: true` on `mcp-router` with a targeted list or switch back to proxy mode plus a small curated direct set. Examples: search, docs, and 1–2 GitNexus tools only.[10]
4. Keep `defaultProjectTrust` explicit in `settings.json` (`"never"` or `"ask"`) so unattended/headless runs have a reviewed default.[1][2]

### Near-term

5. Add an explicit `pi-lens` config if you want deterministic behavior for formatting, tests, or context injection across repos.[13]
6. Either bring `agentmemory` up reliably or disable/remove the extension so global prompt injection does not depend on a dead local service.[17]
7. Consider project-local `.mcp.json` for repo-scoped MCP servers and keep Pi-owned `.pi/mcp.json` only for Pi-specific overrides.[10]
8. If subagents are a primary workflow, add explicit `subagents.defaultModel`, `defaultExtensions`, and concurrency limits instead of relying on ambient global discovery.[11]

### Optional feature expansion

9. Evaluate MCP UI flows and `mcpScript` for data-heavy or multi-step MCP tasks; both are supported by the installed adapter but not yet part of our Hermes Pi skill guidance.[10]
10. Evaluate whether `pi-web-access` should be the preferred web research path for Pi subagent `researcher` runs instead of relying on MCP search tools, especially when source-check artifacts matter.[11][12]

## Corrections to Prior Pi Guidance

The prior Pi skill and archived verification asserted that Pi's `--tools` does not filter MCP tools and that MCP tools are always available independently of `--tools`. Live verification disproved that for direct MCP tools exposed by `pi-mcp-adapter`:

- direct tool names are adapter-generated (`mcp_router_brave_web_search`)
- `--tools` can allowlist those direct names
- omitting the direct name from `--tools` filters it out
- proxy-mode MCP access remains separately governed by the `mcp` tool and adapter config.[10][17]

The durable rule is:

- for **direct MCP tools**, use Pi's generated names in `--tools` / `--exclude-tools`
- for **proxy MCP access**, control exposure through the adapter config (`directTools`, `includeTools`, `excludeTools`, `disableProxyTool`, approvals) rather than relying on the core CLI alone.[10]

## Sources
[1] https://pi.dev/docs/latest/usage — Pi Usage
[2] https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/settings.md — Pi Settings
[3] https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/security.md — Pi Security
[4] https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/packages.md — Pi Packages
[5] https://pi.dev/docs/latest/extensions — Pi Extensions
[9] https://pi.dev/news/releases — Pi Releases
[10] https://github.com/nicobailon/pi-mcp-adapter — pi-mcp-adapter
[11] https://github.com/nicobailon/pi-subagents — pi-subagents
[12] https://github.com/nicobailon/pi-web-access — pi-web-access
[13] https://github.com/apmantza/pi-lens — pi-lens
[14] https://github.com/tintinweb/pi-gitnexus — pi-gitnexus
[15] https://github.com/nicobailon/pi-intercom — pi-intercom
[17] https://rywalker.com/research/pi — Independent Pi Evaluation
