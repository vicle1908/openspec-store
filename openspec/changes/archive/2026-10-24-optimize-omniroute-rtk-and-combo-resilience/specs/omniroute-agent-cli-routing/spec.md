# Spec Delta

## ADDED Requirements

### Requirement: Encapsulated Nested Combo on `muse-spark-1.3`, Auto-Scored Opus Pool on `claude-opus-5.5`, and Loopback API Bridge Port `20129`

OmniRoute SHALL configure `muse-spark-1.3` (`strategy: "priority"`, `nestedComboMode: "execute"`) and `claude-opus-5.5` (`strategy: "auto"`, `nestedComboMode: "flatten"`) with `context_cache_protection: false`, SHALL pin `gemini-4-argon{,-high,-medium,-low}` to the two entitled `Ultra` `agy` accounts (`338764b8` and `0532bad4`), and SHALL set `API_HOST=0.0.0.0` in `docker-compose.override.yml` so host loopback port `20129` serves bridge requests.

#### Scenario: `muse-spark-1.3` executes `gemini-3.8-flash-high` sub-combo without model-pin warning
- **WHEN** Muse Code or a coding client sends a multi-turn request to `"model": "muse-spark-1.3"`
- **THEN** OmniRoute SHALL match `muse-spark-1.3` (`context_cache_protection: false`, `nestedComboMode: "execute"`) and execute `gemini-3.8-flash-high` using its 16-factor `auto` strategy without logging false `provider durably unhealthy — dropping pin` warnings

#### Scenario: `claude-opus-5.5` load-balances and pins across all 8 Opus accounts via `auto` strategy
- **WHEN** a client sends multi-turn requests to `"model": "claude-opus-5.5"`
- **THEN** OmniRoute SHALL score all 8 `agy/claude-opus-5-5-high` accounts using 16-factor `auto` routing (`tierPriority`, `health`, `quota`) and pin multi-turn sessions via `applySessionStickiness` before falling back to `gemini-3.8-flash-high` targets

#### Scenario: Host loopback port `20129` reaches container API bridge
- **WHEN** a client (such as the `cockpit` launcher) sends an HTTP request to `http://127.0.0.1:20129/v1/...`
- **THEN** the container's `apiBridgeServer` (`API_HOST=0.0.0.0`, mapped to host `127.0.0.1:20129:20129`) SHALL accept the connection and relay it to the gateway without dropping the socket
