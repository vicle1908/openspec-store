## ADDED Requirements

### Requirement: LLM Proxy Configuration

The system SHALL configure connection to LLM proxy endpoint.

#### Scenario: Proxy endpoint configuration
- **WHEN** agent-docs-sync starts
- **THEN** it SHALL read LLM proxy URL from config.yaml or LITELLM_URL env var
- **AND** it SHALL default to http://localhost:20128/v1 if not configured
- **AND** it SHALL validate the endpoint is reachable before starting

#### Scenario: API key configuration
- **WHEN** agent-docs-sync starts
- **THEN** it SHALL read LLM API key from LITELLM_API_KEY environment variable
- **AND** it SHALL NOT store API keys in config.yaml (secrets isolation)
- **AND** it SHALL use Bearer authentication header

#### Scenario: Model selection configuration
- **WHEN** generation_agent.model is set in config.yaml
- **THEN** it SHALL use that model for doc generation
- **AND** it SHALL default to sh/claude-opus-4.8.6 if not configured
- **AND** it SHALL validate model is available on proxy before use

#### Scenario: Timeout configuration
- **WHEN** gateway.timeout_seconds is set in config.yaml
- **THEN** it SHALL use that timeout for LLM requests
- **AND** it SHALL default to 120 seconds if not configured

#### Scenario: Fallback model configuration
- **WHEN** fallback.model is set in config.yaml
- **THEN** it SHALL use that model when primary model fails
- **AND** it SHALL NOT use fallback if not configured

### Requirement: GenerationAgent

The system SHALL provide an LLM-powered agent for documentation generation.

#### Scenario: Agent creation
- **WHEN** the sync workflow runs
- **THEN** it SHALL create a GenerationAgent using BaseAgent
- **AND** it SHALL use LiteLLMGateway.from_env() for LLM connection
- **AND** it SHALL use the model specified in config.yaml

#### Scenario: Agent tools
- **WHEN** the GenerationAgent runs
- **THEN** it SHALL have access to read_doc, write_doc, parse_source tools
- **AND** write_doc SHALL require approval via ApprovalGate

#### Scenario: Agent hooks
- **WHEN** the GenerationAgent runs
- **THEN** it SHALL use validate_write_path hook for write validation
- **AND** it SHALL use audit_doc_writes hook for audit trail

#### Scenario: Agent instructions
- **WHEN** the GenerationAgent runs
- **THEN** it SHALL receive system instructions for doc generation
- **AND** it SHALL include context about code changes and affected docs
- **AND** it SHALL preserve existing prose while updating technical sections

### Requirement: Per-app Configuration

The system SHALL support per-app LLM configuration.

#### Scenario: Config loading
- **WHEN** agent-docs-sync starts
- **THEN** it SHALL load config.yaml from app root
- **AND** it SHALL override global ~/.tdt/config.yaml settings
- **AND** it SHALL read LITELLM_API_KEY from environment

#### Scenario: Gateway configuration
- **WHEN** gateway.base_url is set in config.yaml
- **THEN** it SHALL use that URL for LLM connection
- **AND** it SHALL fall back to LITELLM_URL env var if not set

#### Scenario: Model configuration
- **WHEN** generation_agent.model is set in config.yaml
- **THEN** it SHALL use that model for doc generation
- **AND** it SHALL fall back to default model if not set

#### Scenario: Configuration precedence
- **WHEN** both app config and global config exist
- **THEN** app config SHALL override global config
- **AND** environment variables SHALL override both
- **AND** secrets SHALL only come from environment variables

### Requirement: Graceful Degradation

The system SHALL handle LLM failures gracefully.

#### Scenario: LLM unavailable
- **WHEN** the LLM proxy is unreachable
- **THEN** the system SHALL retry up to 2 times
- **AND** it SHALL fail with clear error message after retries exhausted

#### Scenario: LLM timeout
- **WHEN** the LLM response exceeds timeout_seconds
- **THEN** the system SHALL retry up to 2 times
- **AND** it SHALL fail with timeout error after retries exhausted

#### Scenario: Model not found
- **WHEN** the configured model is not available on proxy
- **THEN** the system SHALL fail with clear error message
- **AND** it SHALL list available models if possible

#### Scenario: Fallback skip mode
- **WHEN** fallback.on_error is "skip"
- **AND** the GenerationAgent fails
- **THEN** the system SHALL skip doc generation
- **AND** it SHALL continue with validation and reporting

#### Scenario: Fallback model mode
- **WHEN** fallback.on_error is "fallback"
- **AND** the primary model fails
- **THEN** the system SHALL retry with fallback model
- **AND** it SHALL succeed if fallback model works

### Requirement: LangGraph Orchestration

The system SHALL use WorkflowBuilder for workflow orchestration.

#### Scenario: Workflow creation
- **WHEN** the sync workflow starts
- **THEN** it SHALL create a WorkflowBuilder instance
- **AND** it SHALL add TOOL nodes for deterministic steps
- **AND** it SHALL add AGENT node for generation step

#### Scenario: Workflow execution
- **WHEN** the workflow runs
- **THEN** it SHALL execute nodes in order: detect → analyze → generate → validate → report
- **AND** it SHALL use PostgresSaver for checkpointing

#### Scenario: Durable execution
- **WHEN** checkpointing is enabled
- **THEN** the system SHALL persist state after each node
- **AND** it SHALL resume from last checkpoint on crash

#### Scenario: Node error handling
- **WHEN** a node fails
- **THEN** the system SHALL apply per-node error handling
- **AND** it SHALL retry if retry_max > 0
- **AND** it SHALL fail workflow if no error handler

### Requirement: Global Budget

The system SHALL track LLM costs globally.

#### Scenario: Budget tracking
- **WHEN** the GenerationAgent makes LLM calls
- **THEN** the system SHALL track token usage and cost
- **AND** it SHALL report total cost in sync report

#### Scenario: Budget limit
- **WHEN** budget_usd is set on agent.run()
- **THEN** the system SHALL enforce the budget limit
- **AND** it SHALL raise GatewayError if exceeded

#### Scenario: Cost reporting
- **WHEN** the sync workflow completes
- **THEN** the system SHALL include cost summary in report
- **AND** it SHALL show tokens used and estimated cost
