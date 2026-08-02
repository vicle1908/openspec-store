## ADDED Requirements

### Requirement: MLflow experiment logging via hooks
The system SHALL log agent runs to MLflow via a hook pack registered on `HookPoint.RUN` AFTER. The hook pack SHALL log parameters (`agent_name`, `model`, `skill`, `max_iterations`) and metrics (`latency_ms`, `iterations`, `success`) from the hook context and `AgentResult`. This integrates with the existing hook system (hooks fire at `agent.py:336-337`).

#### Scenario: Agent run logged as MLflow experiment
- **WHEN** agent `reviewer` runs with model `gpt-4o` and completes successfully
- **THEN** an MLflow run exists with params `agent_name=reviewer, model=gpt-4o` and metrics `success=1.0, latency_ms=<value>`

#### Scenario: MLflow not configured
- **WHEN** `MLFLOW_TRACKING_URI` is not set (checked via `ObservabilitySettings.mlflow_tracking_uri`)
- **THEN** the MLflow hook pack is a no-op and agent runs complete normally

### Requirement: MLflow Docker Compose service (local only)
The system SHALL deploy MLflow as a Docker Compose service with:
- Image: `ghcr.io/mlflow/mlflow:3.14.0`
- Command: `mlflow server --backend-store-uri postgresql://mlflow:${MLFLOW_DB_PASSWORD}@mlflow-postgres:5432/mlflow --artifacts-destination s3://mlflow --serve-artifacts --host 0.0.0.0 --port 5000`
- Environment:
  - `AWS_ACCESS_KEY_ID=minio` (local MinIO)
  - `AWS_SECRET_ACCESS_KEY=miniosecret` (local MinIO)
  - `MLFLOW_S3_ENDPOINT_URL=http://minio:9000` (local MinIO)
  - `MLFLOW_S3_IGNORE_TLS=true` (local MinIO, no TLS)
- Dependencies: `mlflow-postgres` (PostgreSQL 16), shared MinIO instance (`minio`)
- Health check: `curl -f http://localhost:5000/health`
- Ports: `5000:5000`

No cloud credentials required. All artifact storage uses local MinIO.

#### Scenario: MLflow server starts successfully
- **WHEN** `docker compose up -d mlflow-server` is run
- **THEN** MLflow UI is accessible at `http://localhost:5000` and health check returns 200

#### Scenario: MLflow connects to PostgreSQL
- **WHEN** MLflow server starts
- **THEN** it connects to `mlflow-postgres:5432` and creates the `mlflow` database schema

#### Scenario: MLflow stores artifacts in local MinIO
- **WHEN** an agent run logs artifacts to MLflow
- **THEN** artifacts are stored in MinIO bucket `mlflow` at `http://minio:9000` (no cloud access needed)

### Requirement: Experiment logging per agent run
The system SHALL log each agent run as an MLflow experiment run with parameters (agent_name, model, skill, max_iterations, temperature) and metrics (latency_ms, cost_usd, tokens_prompt, tokens_completion, iterations, success, tool_success_rate).

#### Scenario: Agent run logged as experiment
- **WHEN** agent `reviewer` runs with model `gpt-4o` and completes successfully
- **THEN** an MLflow run exists with params `agent_name=reviewer, model=gpt-4o` and metrics `success=1.0, latency_ms=<value>`

#### Scenario: Experiment tags recorded
- **WHEN** an agent run uses tools `jira_get, git_diff`
- **THEN** the MLflow run has tag `tools_used=jira_get,git_diff`

### Requirement: Prompt Registry for agent system prompts
The system SHALL register agent system prompts in the MLflow Prompt Registry with version control (commit messages), aliases (production, challenger), and diff viewing.

#### Scenario: Register prompt
- **WHEN** `MLflowClient.register_prompt("reviewer-system", template="You are...", commit_message="Initial")` is called
- **THEN** a prompt named `reviewer-system` version 1 exists in MLflow Prompt Registry

#### Scenario: Version prompt
- **WHEN** `MLflowClient.register_prompt("reviewer-system", template="You are an expert...", commit_message="More specific")` is called
- **THEN** prompt `reviewer-system` has version 2 with diff viewable in MLflow UI

#### Scenario: Load prompt by alias
- **WHEN** `MLflowClient.load_prompt("reviewer-system:production")` is called
- **THEN** the prompt version tagged with alias `production` is returned

### Requirement: Prompt optimization
The system SHALL support automatic prompt optimization via `mlflow.genai.optimize_prompts()` using GEPA or DSPy engines. Optimization runs SHALL be tracked as MLflow experiments with before/after comparison.

#### Scenario: Optimize prompt
- **WHEN** `MLflowClient.optimize_prompt("reviewer-system", data=dataset, scorers=[Correctness()])` is called
- **THEN** a new prompt version is created with improved template, and the optimization run is logged to MLflow with comparison metrics

### Requirement: GenAI evaluation with scorers
The system SHALL support running evaluations via `mlflow.genai.evaluate()` with built-in scorers (Correctness, Safety, RelevanceToQuery), TruLens scorers (PlanAdherence, ExecutionEfficiency, ToolSelection), and custom @scorer decorators.

#### Scenario: Run evaluation with built-in scorers
- **WHEN** `MLflowClient.evaluate(data=dataset, predict_fn=agent.run, scorers=[Correctness()])` is called
- **THEN** evaluation results are logged to MLflow with per-sample scores and aggregate metrics

#### Scenario: Run evaluation with custom scorer
- **WHEN** a custom `@mlflow.genai.scorer` function is defined and passed to `evaluate()`
- **THEN** the scorer is executed against each trace and results are logged to MLflow

### Requirement: Model registry for agent configurations
The system SHALL support registering agent configurations (flavors, tool policies, iteration limits) in the MLflow Model Registry with lifecycle stages (None → Staging → Production → Archived).

#### Scenario: Register agent config
- **WHEN** `MLflowClient.register_agent_config("reviewer-agent", config={...})` is called
- **THEN** a registered model `reviewer-agent` exists in MLflow Model Registry

#### Scenario: Promote to production
- **WHEN** `MLflowClient.promote_to_production("reviewer-agent", version=1)` is called
- **THEN** model version 1 has stage `Production` in MLflow UI

### Requirement: Evaluation datasets
The system SHALL support creating and managing evaluation datasets in MLflow for systematic agent testing. Datasets SHALL contain input/expected_output pairs and be version-controlled.

#### Scenario: Create evaluation dataset
- **WHEN** `MLflowClient.create_eval_dataset("reviewer-eval-v1", source="eval_cases.jsonl")` is called
- **THEN** a dataset `reviewer-eval-v1` exists in MLflow with the uploaded test cases

#### Scenario: Run evaluation against dataset
- **WHEN** `MLflowClient.evaluate_against_dataset("reviewer-eval-v1", predict_fn=agent.run, scorers=[...])` is called
- **THEN** evaluation results are logged with per-sample scores and aggregate pass rates
