# Technical Design: Standardize Goose Workstation Runtime with OmniRoute

## Context

See `proposal.md` for motivation. Goose CLI (`v1.54.0`) is configured with `active_provider: custom_omniroute` (`~/.config/goose/custom_providers/custom_omniroute.json`), routing requests to OmniRoute on `127.0.0.1:20128`. However, `~/.config/goose/config.yaml` retains residual Cockpit Tools configuration on port `51006`, declares an un-aligned `1,000,000` token limit without auto-compaction rules, and has overly permissive file modes (`0755` directory, `0644` files). 

Per official Goose documentation (`/opt/goose-docs/docs/guides/sessions/smart-context-management.md` and `docs/guides/environment-variables.md`):
1. **Model Context Resolution Precedence**:
   - Tier 1: Explicit `context_limit` in model configuration (`custom_providers/custom_omniroute.json`).
   - Tier 2: Specific environment variable (`GOOSE_PLANNER_CONTEXT_LIMIT`).
   - Tier 3: Global environment variable (`GOOSE_CONTEXT_LIMIT`).
   - Tier 4: Model-specific name pattern matching.
   - Tier 5: Global default (128,000 tokens).
2. **Auto-Compaction & Strategy**:
   - `GOOSE_AUTO_COMPACT_THRESHOLD`: Percentage threshold (0.0 to 1.0, default 0.8) where Goose automatically condenses conversation history.
   - `GOOSE_CONTEXT_STRATEGY`: Strategy for handling limits (`summarize`, `truncate`, `clear`, `prompt`). Headless CLI uses `summarize` by default, but setting it explicitly guarantees consistency across interactive sessions.
   - `GOOSE_TOOL_CALL_CUTOFF`: Number of tool calls to keep in full detail before summarizing older tool outputs.
3. **Reasoning & Thinking Output**:
   - `GEMINI3_THINKING_LEVEL`: Officially supported setting (`low`, `high`) for Gemini 3 models.
   - `GOOSE_CLI_SHOW_THINKING`: Setting to `1` renders reasoning blocks in CLI responses.

## Goals / Non-Goals

**Goals:**
- Atomically align `~/.config/goose/config.yaml` context window limits to 1,048,576 tokens and establish auto-compaction parameters.
- Sanitize legacy OpenAI host and base URL parameters away from Cockpit port `51006` to point to OmniRoute loopback `http://localhost:20128/v1` and standard path `chat/completions`.
- Update `~/.config/goose/custom_providers/custom_omniroute.json` model definitions to declare `context_limit: 1048576` and `timeout_seconds: 600` for `gemini-3.8-flash-high` (Tier 1 precedence) and prune decommissioned routes.
- Enforce mode `0700` on Goose configuration directories and mode `0600` on configuration files.
- Validate non-interactive execution with a real sentinel prompt through the OmniRoute gateway.

**Non-Goals:**
- Modifying or adding individual stdio MCP servers in `config.yaml`; all MCP tooling remains multiplexed via `mcp-router`.
- Modifying OmniRoute Docker daemon, compose topology, or combo routing definitions.
- Changing configurations for any other coding agent harnesses.

## Decisions

### 1. Zero-Hairpin Local Loopback Ingress
- **Decision**: Configure `custom_omniroute.json` and fallback `OPENAI_BASE_URL` with `http://localhost:20128/v1` rather than the remote Tailscale endpoint (`https://iosteam-mac-mini.tailc6b508.ts.net/v1`).
- **Rationale**: On this host (`androidteam`), OmniRoute runs directly as a local Docker container bound to `127.0.0.1:20128`. Using local loopback eliminates Tailscale NAT hairpinning, DNS resolution latency, and external interface dependencies.
- **Alternatives Considered**: Tailscale MagicDNS endpoint. Rejected due to unnecessary network hops for intra-host inference.

### 2. Retain Multiplexed MCP Integration via mcp-router
- **Decision**: Keep `mcp-router` as the sole stdio MCP extension in Goose.
- **Rationale**: Goose's `config.yaml` already registers `mcp-router` (`cmd: npx -y @mcp_router/cli@latest connect`), which dynamically multiplexes 84+ ecosystem tools (GitNexus, Graphify, AgentMemory, Exa, Tavily). Defining individual stdio servers would spawn redundant daemon processes and introduce symbol registration conflicts.
- **Alternatives Considered**: Adding discrete `gitnexus`, `graphify`, and `agentmemory` stdio extensions. Rejected because `mcp-router` already routes to all three.

### 3. Context Window & Auto-Compaction Parameters
- **Decision**: Set `context_limit: 1048576` in `custom_omniroute.json` (Tier 1 model config precedence) and configure in `config.yaml`:
  ```yaml
  GOOSE_CONTEXT_LIMIT: 1048576
  GOOSE_PLANNER_CONTEXT_LIMIT: 1048576
  GOOSE_MAX_TOKENS: 65536
  GOOSE_AUTO_COMPACT_THRESHOLD: 0.8
  GOOSE_CONTEXT_STRATEGY: summarize
  GOOSE_TOOL_CALL_CUTOFF: 10
  GOOSE_CLI_SHOW_THINKING: 1
  GOOSE_THINKING_EFFORT: high
  GEMINI3_THINKING_LEVEL: high
  ```
- **Rationale**: Antigravity's `gemini-3.8-flash-high` natively supports 1,048,576 tokens. Compacting at the 80% threshold (`GOOSE_AUTO_COMPACT_THRESHOLD: 0.8`, ~838k tokens) under `GOOSE_CONTEXT_STRATEGY: summarize` with `GOOSE_TOOL_CALL_CUTOFF: 10` condenses earlier turns and tool outputs into a summary, reserving over 210,000 tokens of generation headroom and avoiding upstream 400 token overflow errors.

### 4. Atomic Backup and Rollback Discipline
- **Decision**: Before applying edits to `config.yaml` and `custom_omniroute.json`, generate timestamped mode `0600` backups outside Git (`~/.config/goose/config.yaml.bak-<timestamp>`).
- **Rationale**: Ensures compliance with OpenSpec failure-recovery requirements. If YAML/JSON syntax parsing fails, the original files can be restored immediately without data loss.

### 5. Non-Interactive Verification Harness
- **Decision**: Execute sentinel validation via `goose run --no-session --text "..."`.
- **Rationale**: `goose doctor` attaches to an interactive TTY and blocks waiting on stdin when extensions load. `goose run --no-session` runs headless in single-turn print mode, returning an actionable exit code and verifiable output.

### 6. Endpoint and Dialect Path Normalization
- **Decision**: Update `OPENAI_BASE_URL` and `OPENAI_HOST` to `http://localhost:20128/v1`, normalize `OPENAI_BASE_PATH` to `chat/completions` (replacing legacy `v1/response`), and configure `timeout_seconds: 600` in `custom_omniroute.json`.
- **Rationale**: Cockpit Tools previously injected port `51006` and singular path `v1/response`, which returns HTTP 404 from OmniRoute. Aligning `OPENAI_BASE_PATH` with `chat/completions` guarantees seamless fallback resolution for Goose's native OpenAI provider engine, while `timeout_seconds: 600` prevents premature client-side aborts during deep reasoning phases on large contexts.

## Risks / Trade-offs

- **Risk: Auto-compaction loss of fine-grained history**: Summarizing context after ~838k tokens discards raw tool responses from early turns.
  - *Mitigation*: The `summarize` strategy preserves key decisions and architectural context while freeing generation headroom.
- **Risk: YAML syntax corruption in Goose configuration**: Goose CLI fails fast if `config.yaml` is malformed.
  - *Mitigation*: Pre-mutation backups and post-mutation `goose info` validation verify YAML structure before operational handover.
