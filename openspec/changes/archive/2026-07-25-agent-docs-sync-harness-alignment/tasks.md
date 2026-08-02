## 1. LlmConfig Update

- [x] 1.1 Add harness_config field to LlmConfig dataclass
- [x] 1.2 Update from_env() to include harness_config default
- [x] 1.3 Update _apply_config() to load harness settings

## 2. Agent Wiring

- [x] 2.1 Pass harness_config to BaseAgent in build_generation_agent()
- [x] 2.2 Test agent creation with harness_config

## 3. Configuration

- [x] 3.1 Add harness section to config.yaml
- [x] 3.2 Configure SummarizingCompaction settings
- [x] 3.3 Configure ClampOversizedMessages settings
- [x] 3.4 Configure DeduplicateFileReads settings

## 4. Testing

- [x] 4.1 Test LlmConfig with harness_config
- [x] 4.2 Test BaseAgent receives harness_config
- [x] 4.3 Test context compaction works
- [x] 4.4 Test full mode with harness enabled
