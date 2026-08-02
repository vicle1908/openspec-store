## 1. Configuration Layer

- [x] 1.1 Create `agent-docs-sync/config.yaml` with gateway and agent settings
- [x] 1.2 Create `src/agent_docs_sync/llm/__init__.py`
- [x] 1.3 Create `src/agent_docs_sync/llm/config.py` with LlmConfig dataclass
- [x] 1.4 Implement config loading (app config overrides global)
- [x] 1.5 Add LITELLM_API_KEY to ~/.tdt/.env
- [x] 1.6 Create config validation (validate URL, model availability)
- [x] 1.7 Implement configuration precedence (env > app > global > defaults)

## 2. Gateway Layer

- [x] 2.1 Create gateway factory function using LiteLLMGateway.from_env()
- [x] 2.2 Implement gateway health check (validate proxy reachable)
- [x] 2.3 Add timeout configuration (from config.yaml)
- [x] 2.4 Implement gateway error handling (connection refused, timeout)
- [x] 2.5 Add model validation (check model available on proxy)

## 3. GenerationAgent

- [x] 3.1 Create `src/agent_docs_sync/agents/__init__.py`
- [x] 3.2 Create `src/agent_docs_sync/agents/generation.py`
- [x] 3.3 Implement `build_generation_agent()` using BaseAgent
- [x] 3.4 Register tools: read_doc, write_doc, parse_source
- [x] 3.5 Add validate_write_path and audit_doc_writes hooks
- [x] 3.6 Create generation_flavor with prompts and tool_policy

## 4. LangGraph Workflow

- [x] 4.1 Update `src/agent_docs_sync/workflows/sync_pipeline.py`
- [x] 4.2 Import WorkflowBuilder, NodeDescriptor, EdgeDescriptor from agent-core
- [x] 4.3 Create TOOL nodes for detect_changes, analyze_impact, validate, report
- [x] 4.4 Create AGENT node for generate_updates (GenerationAgent)
- [x] 4.5 Wire edges: detect → analyze → generate → validate → report
- [x] 4.6 Set entry point to detect_changes
- [x] 4.7 Add PostgresSaver checkpointer

## 5. Graceful Degradation

- [x] 5.1 Add retry logic (2 attempts) for GenerationAgent
- [x] 5.2 Implement fallback skip mode
- [x] 5.3 Add timeout handling (180s per attempt)
- [x] 5.4 Create error reporting in sync report

## 6. Global Budget

- [x] 6.1 Integrate with agent-core BudgetTracker
- [x] 6.2 Add budget_usd parameter to agent.run()
- [x] 6.3 Track token usage in sync report
- [x] 6.4 Add cost summary to final report

## 7. Integration Testing

- [x] 7.1 Test config loading with app overrides
- [x] 7.2 Test GenerationAgent creation
- [x] 7.3 Test workflow execution with mock LLM
- [x] 7.4 Test graceful degradation (LLM unavailable)
- [x] 7.5 Test durable execution with PostgresSaver

## 8. Documentation

- [x] 8.1 Update README.md with LLM configuration
- [x] 8.2 Create docs/llm-configuration.md
- [x] 8.3 Update docs/architecture.md with agent layer
