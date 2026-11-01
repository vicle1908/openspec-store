# Verification Evidence: `harden-pi-v1-4-tool-preservation-and-runtime-config`

**Date**: 2026-10-31
**Status**: Verified & Validated
**Pi Version**: `1.4.0` (`/Users/androidteam/.pi/agent/bin/pi`)

---

## 1. Summary of Verification Gates

| Task | Subsystem / Invariant | Verification Command / Method | Observed Result | Status |
|---|---|---|---|---|
| **1.1** | Pre-flight backup | `stat -f '%Lp %N' /tmp/pi-harden-backup /tmp/pi-harden-backup/*` | Directory mode `700`; all secret-bearing files (`settings.json`, `models.json`, `web-search.json`, `agentmemory-index.js`) backed up with mode `600` | Pass |
| **1.2** | `container-entrypoint-compat.sh` & `ensure-muse-wire-compat.sh` update | `git -C ~/Omniroute status --porcelain` + `bash -n` | `TRACKED_MODS=0`; `SYNTAX_OK` | Pass |
| **1.3** | Live `omniroute` container patch & `/v1/responses` preservation | `bash ~/Omniroute/scripts/ensure-muse-wire-compat.sh` + `docker inspect omniroute` + live `subagent({ action: "list" })` | `HEALTH=healthy`, `IDEMPOTENT=already_ok`, `MARKERS_OK=true`; `subagent({ action: "list" })` returned all 13 builtin agents (15 lines) verbatim | Pass |
| **2.1** | `pi-web-access` `searchRouting` & Firecrawl availability (`~/.pi/agent/web-search.json`) | `zsh -c` Node probe against `gemini-search.ts` & `firecrawl.ts` | `MODE=600`, `FIRECRAWL_AVAILABLE=true`, `SEARCH_ROUTING={"providers":["exa","brave","tavily"],"fallbackOn":["transient","quota","network","invalid-response"]}` | Pass |
| **2.2** | `~/.pi/pi-gitnexus.json` (`autoAugment: false`) & `agentmemory/index.js` `[GitNexus active]` interception + child-subagent network isolation | `loadExtensionsCached` Node test covering parent session, `<active_agent name="scout"/>` boundary, and `PI_SUBAGENT_CHILD=1` | `{"mode":"600","caseA_forceSystemPrompt":null,"caseA_guidelinesCount":2,"caseA_hasGitNexusGuideline":true,"caseB_preservedActiveAgent":true,"caseC_childHttpCalls":0,"caseC_childHasToolGuidance":true}` | Pass |
| **3.1** | `~/.pi/agent/models.json` `compat` flags (`supportsMidConvoSystemMessages`, `supportsLongCacheRetention`) | `python3 -m json.tool ~/.pi/agent/models.json` + `stat -f '%Lp'` + `pi --list-models` | Valid JSON, mode `600`, all 6 custom providers and 13 models resolve cleanly | Pass |
| **3.2** | `~/.pi/agent/settings.json` (`skills` exclusions + `advertise: true`) & `~/.pi/agent/trust.json` | `DefaultPackageManager.resolve()` + `discoverAgents()` + `sync-workspace-agent-skills.py --check` | `{"enabledSkills":165,"disabledSkills":44,"totalAgents":13,"advertisedAgents":["oracle","researcher","reviewer","scout","worker"]}`; `sync-workspace-agent-skills.py --check` exited `0` (`malformed_entries=0`, `snapshot_check=ok`) | Pass |
| **3.3** | `workstation-daily-update.sh` >5 MB `~/.pi-lens/*.log` truncation & mirror parity | `shasum -a 256` + `bash -n` | Identical SHA-256 `a103173f6b976982015164c1df800db7d13ac2f96427b7fa254c2857b3d3d04e`; `SYNTAX_OK` | Pass |
| **3.4** | Hermes Pi skill, Wiki entity & Notion sync (`3efc4b21-deb4-8129-b9c3-d7c22a453212`) | `bash ~/Developer/scripts/knowledge-refresh/sync-notion-knowledge.sh --section entities` | `Successfully updated page 3efc4b21-deb4-8129-b9c3-d7c22a453212 for 'Pi'` (`NOTION_SYNC_OK`, `rc=0`) | Pass |
| **4.1** | End-to-end `pi -p --mode json --no-session --approve` probe & `verify-workstation-toolchain.py` | Live `pi -p` probe (`subagent` `list` + `read` `settings.json`) + `verify-workstation-toolchain.py` | `FINAL_REPLY: BUILTIN_COUNT=13 HAS_SCOUT=yes HAS_WORKER=yes HAS_ORACLE=yes`, `SUBAGENT_LIST_LINES: 15`, `HAS_AUGMENT_BANNER: False`; `OVERALL_STATUS: PASS` (`5/5` checks passed) | Pass |
