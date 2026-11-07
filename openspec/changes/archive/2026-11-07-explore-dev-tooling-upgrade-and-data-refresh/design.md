# Design: Workspace Dev Tooling Upgrade and Data Refresh

## Architecture & Ecosystem Topology

The developer workspace (`~/Developer/`) comprises 33 inventoried repositories spanning Go, Python, and TypeScript, backed by shared central knowledge stores:
1. **OpenSpec Store** (`platform/openspec-store/`): Centralized specification authority (`defaultStore`).
2. **Knowledge Refresh Pipeline** (`scripts/knowledge-refresh/`): GitNexus code intelligence (1.6.12) and Graphify AST graphs (0.9.103).
3. **Daily Toolchain & Telemetry Engine** (`scripts/workstation-daily-update.sh`): Generates daily execution records under `data/updates/YYYY-MM-DD.json`.
4. **OmniRoute Inference Bridge** (port `20128`): Core AI gateway with authenticated `/v1/models` endpoint and keyless loopback completions.
5. **LLM Wiki & Notion Knowledge Bridge** (`wiki/` and `scripts/knowledge-refresh/sync-notion-knowledge.sh`): Bidirectional knowledge synchronization.

## Tooling Upgrade Analysis & Target Matrix

| Tool / Subsystem | Current Version | Target Upstream | Authority / Channel | Breaking Changes / Action Plan |
|---|---|---|---|---|
| `graphifyy` | `0.9.95` | `0.9.103` | `uv tool` | Backward-compatible; optimizes AST cache layout under `graphify-out/cache/ast/`. |
| `browser-use` | `0.13.14` | `0.13.14` | `uv tool` | Already at latest release. |
| `infinity-emb` | `0.0.78` | `0.0.78` | `uv tool` | Already at latest release. |
| `tavily-cli` | `0.2.1` | `0.2.1` | `uv tool` | Already at latest release. |
| `claude` | `2.1.319` | `2.1.319` | `claude update` / native | Stable; pinned to latest release. |
| `codex` | `0.167.0` | `0.167.0` | `~/.npm-global` | Latest release; TCC `client_type=0` bundle verified. |
| `opencode` | `1.19.5` | `1.19.5` | System bundle | Re-signed with persistent developer identity. |
| `auggie` | `0.37.0` | `0.37.0` | Binary | Verified stable. |
| `qoder` | `1.1.84` | `1.1.84` | System bundle | Verified stable. |
| `pi` | `1.5.0` | `1.5.0` | `pi update --self` | Verified stable. |
| `kimi` | `2.5.2` | `2.5.2` | Native binary | Verified stable. |
| `ntn` | `0.23.28` | `0.23.28` | Binary / CLI | Verified stable. |
| `gitnexus` | `1.6.12` | `1.6.12` | `~/.npm-global` | Verified stable; 3 repos require re-indexing. |
| `bun` | `1.4.4` | `1.4.4` | `bun upgrade` | Verified latest release. |
| `mas: Telegram` | `12.10` | `13.1.0` | `mas upgrade 747648890` | Requires running process check (`pgrep -x Telegram`) before mutation. |

## Data Refresh Strategy

### 1. Daily Maintenance Telemetry (`2026-11-07.json`)
The telemetry generation script (`workstation-daily-update.sh`) captures structured execution metrics across all 12 stages, persisting results to `~/Developer/data/updates/2026-11-07.json` with permissions mode `0600`.

### 2. Knowledge Index Re-alignment
`knowledge-status.sh --json` indicates that 3 repositories have drifted into `STALE` status:
- `jira-skill`: Requires `gitnexus analyze . --index-only`
- `mcp-router`: Requires `gitnexus analyze . --index-only`
- `openspec-store`: Requires `gitnexus analyze . --index-only`
Graphify indexes will be incrementally synchronized via `graphify update .` using the upgraded `0.9.103` engine.

### 3. Model Catalog & Inference Telemetry
Live models are queried from OmniRoute (`http://127.0.0.1:20128/v1/models`) via Bearer token extracted dynamically by `~/.claude/helpers/omniroute-key.sh`. The query validates 1,000+ available models across Anthropic, Google, and OpenAI providers.

### 4. LLM Wiki & Notion Knowledge Synchronization
Stale entities in `~/Developer/wiki/` (such as `entities/gitnexus.md` and `entities/go-microservices.md`) are refreshed, and `scripts/knowledge-refresh/sync-notion-knowledge.sh --incremental` synchronizes verified documentation to Notion via `ntn`.

## Verification Gates & Determinism Boundaries

1. **Physical Interface DNS Gating**:
   `curl --interface en0` must verify that inactive physical interfaces fail closed without hanging, while active WiFi interface `en1` completes HTTP transactions in <0.5s.
2. **Bun Runtime Evaluation**:
   `bun -e` validates V8/JavaScript execution readiness and platform architecture (`darwin arm64`).
3. **OmniRoute Models Fetch**:
   Python 3.15 script validates connection to port 20128, extracts catalog, and verifies model availability.
4. **Temporal Determinism Replay (45s Bounded Execution)**:
   `ruby scripts/validate-temporal-inventory.rb --self-test` (<5s) followed by `./scripts/test-temporal-replay.sh` (<45s) asserting 8 microservices replay without event history mutation.
