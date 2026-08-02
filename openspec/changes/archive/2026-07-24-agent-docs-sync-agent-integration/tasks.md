## 1. Update Command Integration

- [x] 1.1 Add agent imports to update command
- [x] 1.2 Create agent invocation after analyze_impact
- [x] 1.3 Build task string for doc generation
- [x] 1.4 Call agent.run() with task
- [x] 1.5 Handle agent result (success/failure)
- [x] 1.6 Close gateway connection after use

## 2. Sync Command Integration

- [x] 2.1 Update sync command to use build_sync_pipeline(use_agent=True)
- [x] 2.2 Remove direct workflow function calls
- [x] 2.3 Verify WorkflowBuilder executes with agent node
- [x] 2.4 Handle workflow completion

## 3. Error Handling

- [x] 3.1 Add try/except for agent.run() calls
- [x] 3.2 Log agent errors appropriately
- [x] 3.3 Continue with remaining steps on agent failure
- [x] 3.4 Report partial results if agent fails

## 4. Testing

- [x] 4.1 Test update command with agent
- [x] 4.2 Test sync command with agent
- [x] 4.3 Test agent failure handling
- [x] 4.4 Verify check/validate remain deterministic
- [x] 4.5 Verify LLM calls are made
