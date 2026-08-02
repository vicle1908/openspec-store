## Purpose

This specification defines requirements for Pattern Decisions.

## Requirements

### Requirement: Pattern Decision Framework

The harness SHALL use a systematic approach to decide which pattern (rule-based, skill-based, tools-based, agent-based, or combination) to use for each component.

#### Scenario: Pattern selection criteria
- **WHEN** deciding which pattern to use for a component
- **THEN** the following criteria SHALL be evaluated:
  - **Determinism**: Is the behavior deterministic or creative?
  - **LLM dependency**: Does it need LLM reasoning?
  - **External integration**: Does it call external services?
  - **Configuration**: Is it config-driven or code-driven?
  - **Reusability**: Is it reused across stages/agents?

### Requirement: Rule-Based Components

Deterministic behavior that can be expressed as rules SHALL use rule-based patterns.

#### Scenario: Validation rules
- **WHEN** validating artifacts against constraints
- **THEN** the harness SHALL use rule-based patterns:
  - Tier 1 existence checks (mechanical, no LLM)
  - Config validation (required fields, types, ranges)
  - Schema validation (Pydantic models, JSON schema)
  - Gate config validation (approvers list, timeout ranges)

#### Scenario: Gate configuration
- **WHEN** configuring approval gates
- **THEN** the harness SHALL use rule-based patterns:
  - `GateConfig` dataclass with deterministic fields
  - `required: bool` — simple boolean check
  - `approvers: list[str]` — membership check
  - `timeout_seconds: int` — range validation
  - `auto_approve_if: str | None` — condition evaluation (rule-based)

#### Scenario: State routing
- **WHEN** routing between stages
- **THEN** the harness SHALL use rule-based patterns:
  - `CommandResult(goto=...)` — deterministic routing
  - `EdgeCondition` — conditional edges (ALWAYS, ON_SUCCESS, ON_FAILURE)
  - Backtrack depth check — deterministic counter
  - Circuit breaker state — deterministic state machine

### Requirement: Skill-Based Components

Stage-specific instructions and agent specialization SHALL use skill-based patterns.

#### Scenario: Stage skills
- **WHEN** defining how a stage should behave
- **THEN** the harness SHALL define skills per stage:
  ```yaml
  skills:
    clarify:
      name: "clarify-requirements"
      description: "Generate clarifying questions for vague requirements"
      instructions: |
        You are a requirements analyst. Given a ticket and codebase context:
        1. Identify ambiguous requirements
        2. Generate specific questions
        3. Propose acceptance criteria
      allowed-tools: ["gitnexus_query", "graphify_path", "read_file"]
    design:
      name: "design-solution"
      description: "Generate design document for approved requirements"
      instructions: |
        You are a software architect. Given requirements, context, and impact:
        1. Analyze existing patterns
        2. Propose architecture
        3. Document decisions
      allowed-tools: ["gitnexus_query", "gitnexus_context", "graphify_path"]
  ```

#### Scenario: Agent specialization via flavors
- **WHEN** building stage agents
- **THEN** the harness SHALL use Flavor composition:
  ```python
  clarify_flavor = Flavor(
      name="clarify-agent",
      prompts=[FlavorPrompt(content="You are a requirements analyst...")],
      tool_policy=FlavorToolPolicy(
          allow=["gitnexus_query", "graphify_path", "read_file"],
          deny=["shell_execute", "write_file"],  # read-only for clarify
      ),
      defaults=FlavorDefaults(max_iterations=10, timeout_seconds=120.0),
  )
  ```

#### Scenario: Skill profiles
- **WHEN** loading skills for a stage
- **THEN** the harness SHALL use skill profiles:
  ```yaml
  skills:
    active_profile: harness
    profiles:
      harness:
        directories: ["~/.tdt/harness/skills"]
        include: ["clarify-requirements", "design-solution", ...]
        scopes: ["workspace"]
  ```

### Requirement: Tools-Based Components

External service integrations SHALL use tools-based patterns.

#### Scenario: Tool wrappers
- **WHEN** integrating with external services
- **THEN** the harness SHALL implement BaseTool subclasses:
  ```python
  class GitNexusQueryTool(BaseTool[GitNexusQueryArgs]):
      metadata = ToolMetadata(
          name="gitnexus_query",
          description="Query GitNexus for code intelligence",
          side_effecting=False,  # read-only
          requires_approval=False,
      )
      async def execute(self, args: GitNexusQueryArgs) -> ToolResult:
          # Implementation with @resilient_tool
  ```

#### Scenario: Tool registration
- **WHEN** building the tool registry
- **THEN** the harness SHALL use build_toolkit:
  ```python
  from agent_core.sdk import build_toolkit

  tools = [
      GitNexusQueryTool(),
      GitNexusImpactTool(),
      GraphifyPathTool(),
      GraphifyQueryTool(),
      JiraReaderTool(),
      OpenSpecOpsTool(),
      GitLabOpsTool(),
  ]
  registry = build_toolkit(tools, include_builtins=True)
  ```

#### Scenario: Tool policies
- **WHEN** controlling which tools agents can use
- **THEN** the harness SHALL use FlavorToolPolicy:
  ```python
  # Read-only stages (intake, context, impact)
  read_only_policy = FlavorToolPolicy(
      allow=["gitnexus_query", "gitnexus_context", "gitnexus_impact",
             "graphify_query", "graphify_path", "read_file", "grep_search"],
      deny=["write_file", "shell_execute"],
  )

  # Write stages (spec, design, coding)
  write_policy = FlavorToolPolicy(
      allow=["gitnexus_query", "graphify_path", "read_file", "write_file",
             "openspec_new_change", "openspec_validate"],
      deny=["shell_execute"],
  )
  ```

### Requirement: Agent-Based Components

LLM reasoning and creative generation SHALL use agent-based patterns.

#### Scenario: Stage agents
- **WHEN** a stage requires LLM reasoning
- **THEN** the harness SHALL build BaseAgent instances:
  ```python
  from agent_core.sdk import build_agent, ConsumerConfig

  class HarnessConfig(ConsumerConfig):
      consumer_name: str = "agent-harness"

  config = HarnessConfig.from_env()

  clarify_agent = build_agent(
      config=config,
      tools=registry,
      name="clarify-agent",
      instructions="You are a requirements analyst...",
      flavors=[clarify_flavor],
      memory=memory,
  )
  ```

#### Scenario: Agent execution
- **WHEN** a stage agent runs
- **THEN** the harness SHALL use BaseAgent.run():
  ```python
  async def clarify_handler(state: dict) -> dict:
      ticket = TicketArtifact(**state["results"]["intake"])
      context = ContextArtifact(**state["results"]["context"])

      result = await clarify_agent.run(
          f"Generate clarifying questions for: {ticket.title}\n"
          f"Context: {context.model_dump_json()}"
      )

      if result.completed:
          requirement = RequirementArtifact(**parse_output(result.output))
          return {"results": {"clarify": requirement.model_dump()}}
      else:
          return CommandResult(goto="clarify")  # retry
  ```

#### Scenario: Agent with memory
- **WHEN** an agent needs context from prior stages
- **THEN** the harness SHALL inject memory into the agent:
  ```python
  clarify_agent = build_agent(
      config=config,
      tools=registry,
      memory=memory,  # MemoryCapability auto-wired
      instructions="Use memory_retrieve to check past patterns...",
  )
  ```

### Requirement: Hybrid Components

Components that combine multiple patterns SHALL use combination approach.

#### Scenario: Validation orchestrator
- **WHEN** orchestrating validation tiers
- **THEN** the harness SHALL combine rule-based + agent-based:
  ```python
  async def validate_artifact(artifact, state):
      # Tier 1: Rule-based (no LLM)
      tier1_result = await tier1_existence_check(artifact)
      if not tier1_result.passed:
          return tier1_result

      # Tier 2: Agent-based (LLM)
      tier2_result = await tier2_semantic_check(artifact, state)
      if not tier2_result.passed:
          return tier2_result

      # Tier 3: Rule-based (cross-artifact)
      tier3_result = await tier3_structural_check(artifact, state)
      return tier3_result
  ```

#### Scenario: Gate manager
- **WHEN** managing approval gates
- **THEN** the harness SHALL combine rule-based + tools-based:
  ```python
  async def gate_handler(state):
      stage_name = state["gate_pending"]
      gate_config = get_gate_config(stage_name)  # Rule-based config

      if not gate_config.required:
          return state  # Rule-based auto-approve

      # Tools-based: emit approval request
      approval_request = await emit_approval_request(
          stage=stage_name,
          artifact=state["results"][stage_name],
          approvers=gate_config.approvers,
      )

      # Rule-based: checkpoint and wait
      return {"approval_pending": stage_name}
  ```

#### Scenario: Trace builder
- **WHEN** building trace chains
- **THEN** the harness SHALL combine rule-based + tools-based:
  ```python
  async def build_trace(state):
      # Rule-based: deterministic trace construction
      trace_entries = []
      for stage in STAGE_ORDER:
          if stage in state["results"]:
              entry = TraceEntry(
                  stage=stage,
                  artifact_key=stage,
                  timestamp=now(),
                  input_artifacts=get_inputs(stage),  # Rule-based
                  source_refs=state["results"][stage].get("source_refs", []),
                  verified_by=state["results"][stage].get("verified_by", []),
              )
              trace_entries.append(entry)

      # Tools-based: persist to memory
      await memory.store(session, "trace", trace_entries, layer="scratch")
      return trace_entries
  ```

### Requirement: Pattern Selection Matrix

The harness SHALL use this matrix to decide patterns:

| Component | Deterministic? | LLM? | External? | Pattern |
|-----------|---------------|------|-----------|---------|
| Validation rules | Yes | No | No | Rule-based |
| Gate config | Yes | No | No | Rule-based |
| State routing | Yes | No | No | Rule-based |
| Stage skills | No | Yes | No | Skill-based |
| Agent specialization | No | Yes | No | Skill-based |
| Tool wrappers | Yes | No | Yes | Tools-based |
| Tool policies | Yes | No | No | Rule-based |
| Stage agents | No | Yes | No | Agent-based |
| Validation orchestrator | Mixed | Mixed | No | Hybrid |
| Gate manager | Mixed | No | Yes | Hybrid |
| Trace builder | Mixed | No | Yes | Hybrid |
| Memory operations | Yes | No | Yes | Tools-based |
| Observability | Yes | No | Yes | Tools-based |
| CLI commands | Yes | No | No | Rule-based |

#### Scenario: Component pattern selection
- **WHEN** implementing a new component
- **THEN** the harness SHALL evaluate the component against the matrix criteria (deterministic, LLM, external)
- **AND** it SHALL select the pattern matching the criteria combination
- **AND** it SHALL document the pattern choice in the component's docstring

### Requirement: Pattern Documentation

Every component SHALL document which pattern it uses and why.

#### Scenario: Component documentation
- **WHEN** implementing a component
- **THEN** the docstring SHALL include:
  - Pattern used (rule/skill/tool/agent/hybrid)
  - Rationale for pattern choice
  - Dependencies on other patterns

#### Scenario: Example documentation
- **WHEN** documenting a tool wrapper
- **THEN** the docstring SHALL be:
  ```python
  class GitNexusQueryTool(BaseTool[GitNexusQueryArgs]):
      """Query GitNexus for code intelligence.

      Pattern: Tools-based
      Rationale: External service integration, deterministic input/output
      Dependencies: None (standalone tool)
      """
  ```
