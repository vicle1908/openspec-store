## 1. Planning Integration

- [x] 1.1 Add planning_guidance field to LlmConfig
- [x] 1.2 Update _apply_config to load planning.guidance from config.yaml
- [x] 1.3 Add planning configuration to config.yaml with cache_ttl
- [x] 1.4 Test planning capability with real classification tasks

## 2. SubAgents Integration

- [x] 2.1 Add harness_config parameter to DiscoveryAgent
- [x] 2.2 Add harness_config parameter to ValidationAgent
- [x] 2.3 Add subagents configuration to config.yaml
- [x] 2.4 Implement validator subagent delegation

## 3. Guardrails Integration

- [x] 3.1 Implement doc_path_guard function for path validation
- [x] 3.2 Add guardrails configuration to config.yaml
- [x] 3.3 Integrate guardrails into DiscoveryAgent
- [x] 3.4 Test guardrails with various input scenarios

## 4. DynamicWorkflow Upgrade

- [x] 4.1 Replace basic WorkflowBuilder with DynamicWorkflow
- [x] 4.2 Implement dynamic routing based on state
- [x] 4.3 Add conditional execution for classify step
- [x] 4.4 Test workflow with complex scenarios

## 5. Testing

- [x] 5.1 Write unit tests for planning integration
- [x] 5.2 Write unit tests for subagents integration
- [x] 5.3 Write unit tests for guardrails integration
- [x] 5.4 Write integration tests for DynamicWorkflow

## 6. Documentation

- [x] 6.1 Update docs/configuration.md with agent-core integration
- [x] 6.2 Update docs/reference/discovery-api.md with new features
- [x] 6.3 Add examples for planning, subagents, guardrails usage
