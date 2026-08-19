## 1. GitNexus knowledge refresh fixes

- [x] 1.1 Add 2-stage fallback chain (repair-fts → force) to `refresh-knowledge-indexes.sh` `gitnexus_refresh()` function
- [x] 1.2 Fix `knowledge-status.sh` version detection (2>&1 → 2>/dev/null in `tool_version()`)
- [x] 1.3 Re-index all 13 failing repos (incrementalInProgress flag)
- [x] 1.4 Install missing post-merge hook on tdt-scheduler

## 2. Graphify skill updates

- [x] 2.1 Update graphify to 0.9.46 (`uv tool install graphifyy@latest`)
- [x] 2.2 Update graphify skills across 7 platforms (codex, hermes, pi, copilot, opencode, gemini, agents)
- [x] 2.3 Verify all 8 platforms at 0.9.46

## 3. AgentMemory configuration

- [x] 3.1 Install agentmemory skills (`npx skills add rohitg00/agentmemory -y`)
- [x] 3.2 Re-register hooks with upgrade-safe paths (`agentmemory connect claude-code --with-hooks`)
- [x] 3.3 Add agentmemory skills to Claude's skills directory

## 4. Skill directory restructuring

- [x] 4.1 Move universal skills (tavily-*, brightdata-*, search, etc.) from workspace to global hub
- [x] 4.2 Create symlinks from workspace → global for universal skills
- [x] 4.3 Verify workspace-specific skills (gitnexus-*, openspec-*) are real in workspace and symlinked from global
- [x] 4.4 Remove stale Codex processes (~960MB reclaimed)
- [x] 4.5 Remove stale Happy MCP processes

## 5. Documentation updates

- [x] 5.1 Symlink `~/.claude/CLAUDE.md` → `~/Developer/AGENTS.md`
- [x] 5.2 Update AGENTS.md: fix knowledge-refresh paths, store stats, graphify version
- [x] 5.3 Archive `fix-gitnexus-refresh-fallback-and-graphify-skill-sync` change
- [x] 5.4 Copy archived change to openspec-store

## 6. Verification

- [x] 6.1 Verify all 20 repos have post-merge hooks
- [x] 6.2 Verify 16 repos indexed today
- [x] 6.3 Verify knowledge-status.sh clean output
- [x] 6.4 Verify all tools available (gitnexus 1.6.9, graphify 0.9.46, openspec 1.9.0, agentmemory 0.9.29)
- [x] 6.5 Verify AgentMemory server healthy
