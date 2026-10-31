# Verification Evidence: `optimize-pi-v1-4-runtime-and-ecosystem-alignment`

**Date**: 2026-10-31
**Status**: Verified & Validated
**Pi Version**: `1.4.0` (`/Users/androidteam/.pi/agent/bin/pi`)

---

## 1. Summary of Verification Gates

| Task | Subsystem / Invariant | Verification Command / Method | Observed Result | Status |
|---|---|---|---|---|
| **1.1** | Pre-flight backup | `ls -la /tmp/pi-optimize-backup` | Directory mode `0700`; all secret-bearing files (`zshenv`, `settings.json`, `models.json`, `mcp.json`, `web-search.json`, `agentmemory-index.js`, `container-entrypoint-compat.sh`) backed up with mode `0600` | Pass |
| **1.2** | Shared credentials in `~/.zshenv` | `zsh -c 'test -n "$MCPR_TOKEN" && test -n "$AGENTMEMORY_SECRET" && test -n "$GEMINI_API_KEY"'` + `stat -f '%Lp' ~/.zshenv` | `ALL_THREE_SET` (`rc=0`); `~/.zshenv` mode `600` | Pass |
| **2.1** | Native MCP `codemode` & `toolExposure` (`~/.pi/agent/mcp.json`) | `zsh -c "pi mcp list"` + `grep -q 'mcpr_' ~/.pi/agent/mcp.json` | `mcp-router: connected, 138 tools (codemode, global)` with all 25 Desktop Commander tools marked `[hidden]`; `grep -q 'mcpr_'` exited `1` (no inline literal token); mode `600` | Pass |
| **2.2** | `models.json` schema & `x-omniroute-no-memory: "true"` | `python3 -m json.tool ~/.pi/agent/models.json` + `pi --list-models` | Valid JSON (`0600`) with `$schema`; all 6 custom providers (`cockpit`, `omniroute`, `omniroute-anthropic`, `omniroute-responses`, `phanmemvip`, `shopapikey` = 13 models) resolve cleanly with `x-omniroute-no-memory: "true"` on all 3 OmniRoute providers and aligned `sh/codex-x` `thinkingLevelMap` | Pass |
| **2.3** | `settings.json` schema, `+codemode`/`+tool_search`, & `subagents.agentExcludeDirs` | `discoverAgents("/Users/androidteam/Developer", "both")` | `PROJECT_AGENTS=0 BUILTIN_AGENTS=13` (eliminated all 108 bogus `.skill-snapshots` project subagents); mode `600` | Pass |
| **2.4** | Hermes Pi skill, Wiki entity & Notion sync | `rg -n '0\.84\.1|/opt/homebrew/bin/pi|pi-mcp-adapter|fable-5' ~/.hermes/skills/autonomous-ai-agents/pi/SKILL.md` + `sync-notion-knowledge.sh --section entities` | Zero stale matches (`rc=1`); Notion page `3efc4b21-deb4-8129-b9c3-d7c22a453212` (`Pi`) updated (`rc=0`) | Pass |
| **3.1** | `agentmemory/index.js` secret fallback, 2.5s timeout & cache-safe recall | `env -u AGENTMEMORY_SECRET node ...` | `{"searchCount":3,"hasSystemPromptOverride":false,"hasCustomMessage":true,"userGuidelinesLen":1,"customGuidelinesLen":1,"customReturnedUndefined":true}` (`rc=0`) | Pass |
| **3.2** | `pi-web-access` `~/.pi/agent/web-search.json` (`0600`) migration | `test ! -e ~/.pi/web-search.json` + `stat -f '%Lp' ~/.pi/agent/web-search.json` | Legacy `~/.pi/web-search.json` removed; `~/.pi/agent/web-search.json` is mode `600` with `$ENV_VAR` indirection (`HAS_PPLX=False`, `HAS_AIza=False`) and `exa -> brave -> tavily` routing | Pass |
| **3.3** | `~/.pi-lens/config.json` (`0600`) & log truncation | `stat -f '%Lp' ~/.pi-lens/config.json` + `python3 -m json.tool ~/.pi-lens/config.json` | Mode `600`, valid JSON with `contextInjection: { enabled: true, retain: true, requirePreExistingFixes: false }` and `ignore` globs; `latency.log` (9.9 MB) and `sessionstart.log` (4.9 MB) truncated | Pass |
| **4.1** | OmniRoute `/v1/responses` `bodyAdapter` + `rtk` chunk rules in `container-entrypoint-compat.sh` | `git -C ~/Omniroute status --porcelain` | Zero git-tracked files modified in `~/Omniroute` (`TRACKED_MODS=0`) | Pass |
| **4.2** | Live `omniroute` container patch & `/v1/responses` `read` preservation | `bash ~/Omniroute/scripts/ensure-muse-wire-compat.sh` + `docker inspect omniroute` + live Pi `read` tool on `~/.pi/agent/settings.json` | Container `healthy`, second run returned `already_ok`, and reading `~/.pi/agent/settings.json` returned all 82 lines verbatim with zero RTK line truncation | Pass |
| **5.1** | Artifact & release hygiene | `test ! -e` across all 9 target paths + `pi --version` | `releases/1.3.0` (147 MB), `skills.bak-*`, `backups/`, `*.bak*`, `memory/`, `tdt/`, `projects-memory/`, and `~/Developer/.agentmemory` removed (`T5.1_REMAINING=[]`); `pi --version` = `1.4.0` | Pass |
| **5.2** | `workstation-daily-update.sh` `pi:Pi:update --all` parity | `shasum -a 256` + `bash -n` | Both copies have identical SHA-256 `3a4e6153f034b2dd5642f6784b9ea5750455aa8b4c37c8b7d6448fd48917d4d1` and `bash -n` exited `0` | Pass |
| **5.3** | End-to-end non-interactive Pi probes (`read`, `memory_search`, `codemode`, `subagent`, `effective_config`, `verify-workstation-toolchain.py`) | Live `pi -p --no-session --approve` probes + `python3 platform/openspec-store/scripts/verify-workstation-toolchain.py` | `SETTINGS_SCHEMA=https://pi.dev/schemas/settings.schema.json and MEMORY_OK=yes` (`rc=0`); `WIKI_TOOLS=8` (`rc=0`); `PROJECT_AGENTS=0 and HAS_ORACLE=yes` (`rc=0`); `GLOBAL_COUNT=5` (`rc=0`); `verify-workstation-toolchain.py` (`rc=0`, all checks `PASS`) | Pass |

---

## 2. Recorded Command Outputs

### `pi --version` & `pi list`
```text
1.4.0

User packages:
  npm:pi-subagents
    /Users/androidteam/.pi/agent/npm/node_modules/pi-subagents
  npm:pi-web-access
    /Users/androidteam/.pi/agent/npm/node_modules/pi-web-access
  npm:pi-intercom
    /Users/androidteam/.pi/agent/npm/node_modules/pi-intercom
  npm:pi-lens
    /Users/androidteam/.pi/agent/npm/node_modules/pi-lens
  npm:pi-gitnexus
    /Users/androidteam/.pi/agent/npm/node_modules/pi-gitnexus
```

### `pi mcp list`
```text
mcp-router: connected, 138 tools (codemode, global)
  npx -y @mcp_router/cli@latest connect
  tools: web_search_exa, web_fetch_exa, agent_run, searchGitHub, ask_wiki_question, read_wiki_contents, read_wiki_structure, resolve-library-id, query-docs, tavily_search, tavily_extract, tavily_crawl, tavily_map, tavily_research, js, js_add_node_module_dir, js_reset, turn_ended, wiki_search, wiki_read, wiki_index, wiki_ingest, wiki_links, wiki_stale, memory_recall, ..., get_config [hidden], set_config_value [hidden], read_file [hidden], read_multiple_files [hidden], write_file [hidden], write_pdf [hidden], create_directory [hidden], list_directory [hidden], move_file [hidden], start_search [hidden], get_more_search_results [hidden], stop_search [hidden], list_searches [hidden], get_file_info [hidden], edit_block [hidden], start_process [hidden], read_process_output [hidden], interact_with_process [hidden], force_terminate [hidden], list_sessions [hidden], list_processes [hidden], kill_process [hidden], get_usage_stats [hidden], get_recent_tool_calls [hidden], give_feedback_to_desktop_commander [hidden], ...
  offers resources
```

### End-to-End Non-Interactive `pi -p` Probes & Workstation Toolchain Gate
```text
$ pi -p --no-session --approve "Call read on /Users/androidteam/.pi/agent/settings.json and call memory_search with query OpenSpec, then reply on one line with SETTINGS_SCHEMA=<value of \$schema> and MEMORY_OK=<yes or no>."
SETTINGS_SCHEMA=https://pi.dev/schemas/settings.schema.json and MEMORY_OK=yes

$ pi -p --no-session --approve 'Use the codemode tool to run searchTools("wiki") and return the count of matching tools as WIKI_TOOLS=<N>.'
WIKI_TOOLS=8

$ pi -p --no-session --approve 'Call subagent with action list, then reply on one line with PROJECT_AGENTS=<count of (project) entries> and HAS_ORACLE=<yes or no>.'
PROJECT_AGENTS=0 and HAS_ORACLE=yes

$ pi -p --no-session --approve 'Call effective_config with empty object {}, then reply on one line with GLOBAL_COUNT=<provenanceCounts.global>.'
GLOBAL_COUNT=5

$ python3 /Users/androidteam/Developer/platform/openspec-store/scripts/verify-workstation-toolchain.py
rc=0 (evidence_hash: d632be133a8e4dbc9fee6b4689fc2e2d5ba713158edc903301e5d09e01ffcf25, all checks PASS)
```
