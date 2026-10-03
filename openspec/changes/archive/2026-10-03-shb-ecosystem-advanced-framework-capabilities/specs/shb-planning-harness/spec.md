# shb-planning-harness Specification Delta

## MODIFIED Requirements

### Requirement: Durable Persistence and State Checkpointing
The planning harness SHALL persist workflow execution state at each node boundary using LangGraph checkpointers, prioritizing file-backed `SqliteSaver` in `~/.shb/harness.db` for multi-session persistence with graceful fallback to `MemorySaver` for ephemeral test executions.

#### Scenario: State checkpoint persistence across stages
- **WHEN** any stage node finishes execution
- **THEN** the checkpointer SHALL save the updated `HarnessState` snapshot keyed by ticket ID (`thread_id`)

#### Scenario: Resumption of interrupted ticket workflow
- **WHEN** an operator requests resumption of an interrupted ticket run via CLI
- **THEN** the harness SHALL reload the latest checkpoint from storage and continue execution from the next pending stage without re-running completed stages

#### Scenario: SQLite state checkpoint persistence across stages
- **WHEN** any stage node finishes execution in the planning lifecycle
- **THEN** the checkpointer SHALL save the updated `HarnessState` snapshot keyed by ticket ID (`thread_id`) to the SQLite checkpoint database

### Requirement: Command-Line Interface Entrypoint
The package SHALL provide an executable command-line interface named `shb-harness` allowing engineers to start, inspect, and resume planning workflows across human-in-the-loop governance milestones.

#### Scenario: Workflow status check
- **WHEN** an engineer executes `shb-harness status --ticket-id <id>`
- **THEN** the CLI outputs the current active stage, completed checkpoints, and artifact locations

#### Scenario: Resumption of paused ticket thread
- **WHEN** an engineer executes `shb-harness resume <ticket-id> --action approve`
- **THEN** the CLI SHALL submit the approval command to the compiled state graph and resume pipeline execution
