## 1. New Tools

- [x] 1.1 Create ReadPyprojectTool (read pyproject.toml)
- [x] 1.2 Create ReadSkillTool (read .agents/skills/)
- [x] 1.3 Create ReadDeploymentTool (read Dockerfile, docker-compose)
- [x] 1.4 Register new tools in ToolRegistry

## 2. Context Compaction

- [x] 2.1 Add harness config to config.yaml
- [x] 2.2 Configure SummarizingCompaction
- [x] 2.3 Configure ClampOversizedMessages
- [x] 2.4 Configure DeduplicateFileReads
- [x] 2.5 Test context compaction with large codebases

## 3. Full Mode CLI

- [x] 3.1 Add --full flag to sync command
- [x] 3.2 Add --full flag to update command
- [x] 3.3 Route to full mode workflow when --full

## 4. Full Mode Workflow

- [x] 4.1 Create full mode pipeline (discovery → analysis → generation → validation)
- [x] 4.2 Implement discovery phase (read all sources)
- [x] 4.3 Implement analysis phase (extract API, map to docs)
- [x] 4.4 Implement generation phase (update/create docs)
- [x] 4.5 Implement validation phase (check links, verify examples)

## 5. Full Mode Output

- [x] 5.1 Implement README.md generation
- [x] 5.2 Implement docs/api/*.md generation
- [x] 5.3 Implement docs/deployment.md generation
- [x] 5.4 Test full mode output

## 6. Testing

- [x] 6.1 Test new tools
- [x] 6.2 Test context compaction
- [x] 6.3 Test full mode workflow
- [x] 6.4 Test full mode output
