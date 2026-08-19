## Tasks

### 1. Implementation
- [x] Add `ToolAnnotationMapper` class to `agent_core/_ai/mcp_annotations.py` — maps MCP annotations to AuthorityClass
- [x] Add `configure_from_config(config: AgentConfig)` method to MCPManager — reads mcp_servers URLs and creates MCPToolset instances
- [x] Add `mcp_servers: list[str]` field to AgentConfig in `agent_core/_ai/config.py`
- [x] Add tool name disambiguation — `disambiguate_tool_name()` prefixes tool names with server host
- [x] Write delta spec for mcp-integration (standards compliance, annotation mapping)

### 2. Testing
- [x] Test: readOnlyHint tool → READ authority class
- [x] Test: destructiveHint tool → appropriate high-authority class
- [x] Test: unknown annotations → conservative READ default
- [x] Test: tool name disambiguation (no collisions across servers)
- [x] Test: configure_from_config reads URLs and creates MCPToolset instances
- [x] Run full agent-core test suite (24 MCP tests pass)

### 3. Verification
- [x] ruff check src/agent_core/_ai/
- [x] mypy src/agent_core/_ai/ --strict
- [x] openspec validate bridge-mcp-manager-to-router --store openspec-store
