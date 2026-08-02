## Context

agent-docs-sync currently handles partial doc updates based on git diff. Users need a "full mode" that reads all source code, deployment configs, skills, and generates comprehensive documentation.

## Goals / Non-Goals

**Goals:**
- Add `--full` flag to CLI commands
- Read all source code, deployment configs, skills
- Integrate harness context compaction for large codebases
- Generate comprehensive docs from all sources
- Update existing docs and create new ones

**Non-Goals:**
- Real-time streaming (batch is sufficient)
- Complex AI reasoning beyond doc generation
- Replacing manual doc writing entirely

## Decisions

### Decision 1: --full Flag Pattern

```bash
# Partial mode (current)
docs-sync sync --repo .

# Full mode (new)
docs-sync sync --full --repo .
```

### Decision 2: Harness Context Compaction

Use agent-core's harness capabilities for context management:

```yaml
# In config.yaml
generation_agent:
  model: "cx/claude-opus-4.8-4.8.5"
  max_iterations: 20
  timeout_seconds: 300

harness:
  context_compaction:
    strategy: "summarizing"
    max_messages: 100
    max_tokens: 20000
    clamp_oversized: true
    clear_tool_results: true
    deduplicate_reads: true
```

### Decision 3: New Tools for Full Mode

```python
# Tools to add
ReadPyprojectTool    → Read pyproject.toml
ReadSkillTool        → Read .agents/skills/**/*.md
ReadDeploymentTool   → Read Dockerfile, docker-compose.yaml
```

### Decision 4: Full Mode Workflow

```
┌─────────────────────────────────────────────────────────┐
│  Full Mode Pipeline                                       │
└─────────────────────────────────────────────────────────┘

  Phase 1: Discovery
  ├─ Read pyproject.toml
  ├─ Read .agents/skills/
  ├─ Read Dockerfile/docker-compose
  ├─ Read openspec/
  └─ Scan src/**/*.py

  Phase 2: Analysis
  ├─ Extract API from source
  ├─ Map source to docs
  ├─ Identify doc gaps
  └─ Generate update plan

  Phase 3: Generation
  ├─ Update README.md
  ├─ Update docs/api/*.md
  ├─ Update docs/guides/*.md
  ├─ Update docs/architecture.md
  └─ Update docs/deployment.md

  Phase 4: Validation
  ├─ Check all links
  ├─ Verify code examples
  └─ Run openspec validate
```

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│  Full Mode Architecture                                   │
└─────────────────────────────────────────────────────────┘

  CLI: docs-sync sync --full
         │
         ▼
  Agent (with context compaction)
  ├─ SummarizingCompaction
  ├─ ClampOversizedMessages
  └─ DeduplicateFileReads
         │
         ▼
  Tools
  ├─ read_doc (existing)
  ├─ write_doc (existing)
  ├─ check_links (existing)
  ├─ parse_source (existing)
  ├─ read_pyproject (NEW)
  ├─ read_skill (NEW)
  └─ read_deployment (NEW)
         │
         ▼
  Output Docs
  ├─ README.md
  ├─ docs/api/*.md
  ├─ docs/guides/*.md
  └─ docs/deployment.md
```

## Testing Strategy

| Test Type | Scope |
|-----------|-------|
| Unit | New tools, context compaction |
| Integration | Full mode workflow |
| E2E | Complete doc generation |
