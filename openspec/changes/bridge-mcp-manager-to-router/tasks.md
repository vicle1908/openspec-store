## Tasks

### 1. Implementation
- [ ] Add `ToolAnnotationMapper` class to `agent_core/_ai/mcp.py` — maps MCP annotations to AuthorityClass
- [ ] Add `configure_from_config(config: AgentConfig)` method to MCPManager — reads mcp_servers URLs and creates MCPToolset instances
- [ ] Add `mcp_servers: list[str]` field to AgentConfig in `agent_core/_ai/config.py`
- [ ] Add tool name disambiguation — prefix tool names with server identifier
- [ ] Write delta spec for mcp-integration (standards compliance, annotation mapping)

### 2. Testing
- [ ] Test: readOnlyHint tool → READ authority class
- [ ] Test: destructiveHint tool → appropriate high-authority class
- [ ] Test: unknown annotations → conservative READ default
- [ ] Test: tool name disambiguation (no collisions across servers)
- [ ] Test: configure_from_config reads URLs and creates MCPToolset instances
- [ ] Run full agent-core test suite (704+ tests)

### 3. Verification
- [ ] ruff check src/agent_core/_ai/
- [ ] mypy src/agent_core/_ai/ --strict
- [ ] openspec validate bridge-mcp-manager-to-router --store openspec-store
