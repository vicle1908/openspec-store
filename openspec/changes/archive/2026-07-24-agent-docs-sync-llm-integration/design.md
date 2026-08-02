## Context

agent-docs-sync has a working deterministic pipeline (detect → analyze → validate → report). The generate_updates step is a placeholder that needs LLM integration. We need to add intelligent doc generation using agent-core features while preserving the deterministic steps.

The LLM proxy is **OmniRoute** (https://github.com/diegosouzapw/OmniRoute) — a free, MIT-licensed AI gateway that provides:
- 290+ providers (90+ free)
- OpenAI-compatible API at http://localhost:20128/v1
- Built-in failover, load balancing, semantic caching
- Token compression (15-95% savings)
- Model: sh/claude-opus-4.8.6

We use **LiteLLMGateway** from agent-core to connect to OmniRoute (both are nhà cung cấp dịch vụ AI-compatible).

## Goals / Non-Goals

**Goals:**
- Add LLM-powered doc generation using BaseAgent (pydantic-ai)
- Use WorkflowBuilder (LangGraph) for orchestration
- Per-app configuration (config.yaml overrides global)
- Graceful degradation when LLM unavailable
- PostgresSaver for durable execution

**Non-Goals:**
- LLM for detection/analysis (deterministic is better)
- LLM for validation (deterministic checks suffice)
- Multiple agents (only generation needs LLM)
- Real-time streaming (batch is sufficient)

## Decisions

### Decision 1: Single GenerationAgent (not multi-agent)

Only the generate_updates step needs LLM. Detection, analysis, validation, and reporting are deterministic and don't benefit from LLM.

```
┌─────────────────────────────────────────────────────────┐
│  Detection Phase (Deterministic)                        │
│  ├─ detect_changes: git diff parsing                    │
│  └─ analyze_impact: config-driven mapping               │
│                                                         │
│  Generation Phase (Agent)                               │
│  └─ generate_updates: GenerationAgent (LLM)             │
│                                                         │
│  Validation Phase (Deterministic)                       │
│  ├─ validate: link checking, file existence             │
│  └─ report: formatting                                  │
└─────────────────────────────────────────────────────────┘
```

### Decision 2: Hybrid Workflow (functions + agent nodes)

Use WorkflowBuilder with mixed node types:
- TOOL nodes for deterministic steps (functions)
- AGENT node for generation step (BaseAgent)

### Decision 3: Per-app Configuration

agent-docs-sync/config.yaml overrides global ~/.tdt/config.yaml:
- Gateway connection (base_url)
- Generation agent settings (model, iterations, timeout)
- Fallback behavior

### Decision 4: Graceful Degradation

On LLM failure:
- Retry 2 attempts
- Configurable fallback (fail/skip)
- Timeout 180s per attempt

### Decision 5: PostgresSaver for Durability

Use agent-core's create_checkpointer() for LangGraph checkpointing:
- Crash recovery
- Resume from last completed step
- Already available in TDT ecosystem

## Architecture

```
agent-docs-sync/
├── config.yaml                    # Per-app LLM config
├── src/agent_docs_sync/
│   ├── agents/
│   │   ├── __init__.py
│   │   └── generation.py          # GenerationAgent builder
│   ├── llm/
│   │   ├── __init__.py
│   │   └── config.py              # LlmConfig dataclass
│   ├── workflows/
│   │   ├── __init__.py
│   │   └── sync_pipeline.py       # LangGraph workflow
│   ├── tools/                     # Existing tools (unchanged)
│   └── hooks.py                   # Existing hooks (unchanged)
```

## Configuration

### LLM Proxy Configuration (OmniRoute)

```yaml
# agent-docs-sync/config.yaml

# OmniRoute Gateway Configuration
gateway:
  # Use LiteLLM gateway (OmniRoute is nhà cung cấp dịch vụ AI-compatible)
  provider: "litellm"

  # OmniRoute endpoint
  base_url: "http://localhost:20128/v1"

  # API key from environment (NEVER store in config.yaml)
  # Read from: LITELLM_API_KEY env var

  # Request timeout (seconds)
  # OmniRoute is fast, can use lower timeout
  timeout_seconds: 60

# Generation Agent Configuration
generation_agent:
  # Model to use for doc generation
  # OmniRoute routes to provider automatically
  model: "sh/claude-opus-4.8.6"

  # Or use auto-routing for best provider selection
  # model: "auto/coding"

  # Agent behavior
  max_iterations: 15
  timeout_seconds: 180

  # Tools available to agent
  tools:
    - read_doc
    - write_doc
    - parse_source

  # System instructions for doc generation
  instructions: |
    You are a documentation generator. Extract API signatures, docstrings,
    and type hints from code to generate or update documentation.
    Always preserve existing prose — only update technical sections.

# Fallback Configuration
fallback:
  enabled: true
  on_error: "fail"  # fail | skip
  # Note: OmniRoute has built-in failover, so fallback is optional

# Checkpointing Configuration
checkpointing:
  enabled: true
  # Uses PostgresSaver from agent-core
  # Requires: CRASH_RECOVERY_ENABLED=true, DBOS_DATABASE_URL
```

### Environment Variables

```bash
# ~/.tdt/.env

# OmniRoute Configuration (using LiteLLM gateway)
LITELLM_URL=http://localhost:20128/v1
LITELLM_API_KEY=sk-34375b0ba3dd4298-5522d8-161ab53d

# Optional: Override config values
# GATEWAY_TIMEOUT_SECONDS=60
# GENERATION_AGENT_MODEL=sh/claude-opus-4.8.6
```

### Configuration Precedence

```
┌─────────────────────────────────────────────────────────┐
│  Configuration Precedence (highest → lowest)            │
└─────────────────────────────────────────────────────────┘

  1. Environment variables (LITELLM_*, GATEWAY_*)
         │
         ▼
  2. App config (agent-docs-sync/config.yaml)
         │
         ▼
  3. Global config (~/.tdt/config.yaml)
         │
         ▼
  4. Code defaults
```

### Secrets Isolation

```
┌─────────────────────────────────────────────────────────┐
│  Secrets Management                                     │
└─────────────────────────────────────────────────────────┘

  ✅ SAFE (from environment):
  ├─ LITELLM_API_KEY
  └─ BIFROST_API_KEY

  ❌ UNSAFE (never store in config.yaml):
  ├─ api_key
  ├─ password
  └─ token
```

## Data Flow

```
┌─────────────────────────────────────────────────────────┐
│  Workflow Execution (LangGraph)                         │
└─────────────────────────────────────────────────────────┘

  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
  │   detect    │────▶│   analyze   │────▶│  generate   │
  │   changes   │     │   impact    │     │   updates   │
  │  (TOOL)     │     │  (TOOL)     │     │  (AGENT)    │
  └─────────────┘     └─────────────┘     └──────┬──────┘
                                                  │
                                                  ▼
  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
  │   report    │◀────│  validate   │◀────│   (LLM)     │
  │             │     │             │     │  Generation │
  │  (TOOL)     │     │  (TOOL)     │     │  Agent      │
  └─────────────┘     └─────────────┘     └─────────────┘

  Checkpointing: PostgresSaver (agent-core)
```

## agent-core Integration

| Feature | Usage |
|---------|-------|
| BaseAgent | GenerationAgent with pydantic-ai |
| LiteLLMGateway | LLM connection via from_env() |
| WorkflowBuilder | LangGraph workflow orchestration |
| PostgresSaver | Durable checkpointing |
| ToolRegistry | Doc tools (read_doc, write_doc, etc.) |
| HookRegistry | validate_write_path, audit_doc_writes |
| Flavor | GenerationAgent prompt composition |

## Error Handling

```
┌─────────────────────────────────────────────────────────┐
│  Graceful Degradation Flow                              │
└─────────────────────────────────────────────────────────┘

  GenerationAgent fails
         │
         ▼
  ┌─────────────┐     Yes    ┌─────────────────┐
  │   Retry     ├───────────▶│   Attempt 2     │
  │   (2 max)   │            │                 │
  └──────┬──────┘            └─────────────────┘
         │ No (exhausted)
         ▼
  ┌─────────────┐     Yes    ┌─────────────────┐
  │  Fallback   ├───────────▶│  Skip generate  │
  │  enabled?   │            │  Continue       │
  └──────┬──────┘            └─────────────────┘
         │ No
         ▼
  ┌─────────────┐
  │  Fail with  │
  │  clear error│
  └─────────────┘
```

## Testing Strategy

| Test Type | Scope |
|-----------|-------|
| Unit | GenerationAgent, LlmConfig |
| Integration | WorkflowBuilder with mock LLM |
| E2E | Full pipeline with real proxy |
| Durable | PostgresSaver checkpoint/resume |
