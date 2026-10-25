## MODIFIED Requirements

### Requirement: OmniRoute Gemini 4 Argon Tier Combos SHALL Route Exclusively Through Entitled Ultra Antigravity CLI Connections

OmniRoute SHALL expose four top-level routing combos for Gemini 4 Argon (`gemini-4-argon-high`, `gemini-4-argon-medium`, `gemini-4-argon-low`, and `gemini-4-argon`) using `strategy: "auto"`, `context_length: 1000000`, `context_cache_protection: false`, `config.targetTimeoutMs: 25000`, and `config.candidatePool: ["agy"]`. Each combo SHALL contain three model steps pinned to the three Google AI `Ultra` `agy` CLI connections (`62af823b-f3d7-4e6b-87a9-98069167d4f6` / `vicgnome19094@gmail.com`, `0532bad4-2486-4286-8f06-510e9c678620` / `vinhvumobile@gmail.com`, and `338764b8-1cd7-4946-b789-ee5dad4c5073` / `vinhghtk1908@gmail.com`).

#### Scenario: Tier combos resolve exclusively to the two Ultra agy CLI connections
- **WHEN** `GET http://127.0.0.1:20128/api/combos` is queried
- **THEN** combos `gemini-4-argon-high`, `gemini-4-argon-medium`, `gemini-4-argon-low`, and `gemini-4-argon` SHALL each be present with `strategy: "auto"`, `context_length: 1000000`, `context_cache_protection: false`, `config.targetTimeoutMs: 25000`, `config.candidatePool: ["agy"]`, `config.resetAwareQuotaCacheTtlMs: 300000`, `config.resetWindowQuotaCacheTtlMs: 300000`, and `config.resetAwareQuotaCacheMaxStaleMs: 3600000`
- **AND** `gemini-4-argon-high` and `gemini-4-argon` SHALL each define three `kind: "model"` steps with `model: "agy/gemini-4-argon-high"`, `providerId: "agy"`, and matching email `label` pinned to `connectionId: "62af823b-f3d7-4e6b-87a9-98069167d4f6"` (`vicgnome19094@gmail.com`), `connectionId: "0532bad4-2486-4286-8f06-510e9c678620"` (`vinhvumobile@gmail.com`), and `connectionId: "338764b8-1cd7-4946-b789-ee5dad4c5073"` (`vinhghtk1908@gmail.com`)
- **AND** `gemini-4-argon-medium` SHALL define three `kind: "model"` steps with `model: "agy/gemini-4-argon-medium"`, `providerId: "agy"`, and matching email `label` pinned to those same three `connectionId` values
- **AND** `gemini-4-argon-low` SHALL define three `kind: "model"` steps with `model: "agy/gemini-4-argon-low"`, `providerId: "agy"`, and matching email `label` pinned to those same three `connectionId` values

#### Scenario: Combo health check and dual-protocol inference succeed across all Argon combos
- **WHEN** `POST /api/combos/test`, `POST /v1/responses`, or `POST /v1/chat/completions` is invoked for `gemini-4-argon-high`, `gemini-4-argon-medium`, `gemini-4-argon-low`, or `gemini-4-argon`
- **THEN** OmniRoute SHALL dispatch to one of the three `Ultra` `agy` connections and return a valid `200 OK` completion

#### Scenario: Disabled sentinel or unentitled Pro connection fails closed without polluting Argon combos
- **WHEN** any of the 12 non-Ultra `agy` CLI connections is inspected or invoked for `gemini-4-argon*`
- **THEN** none of those 12 `connectionId` values SHALL appear in the `models[]` steps of `gemini-4-argon`, `gemini-4-argon-high`, `gemini-4-argon-medium`, or `gemini-4-argon-low`

### Requirement: Encapsulated Nested Combo on `muse-spark-1.3`, Auto-Scored Opus Pool on `claude-opus-5.5`, and Loopback API Bridge Port `20129`

OmniRoute SHALL configure `muse-spark-1.3` (`strategy: "priority"`, `nestedComboMode: "execute"`, `targetTimeoutMs: 25000`) and `claude-opus-5.5` (`strategy: "auto"`, `nestedComboMode: "flatten"`, `targetTimeoutMs: 25000`) with `context_cache_protection: false`, SHALL pin `gemini-4-argon{,-high,-medium,-low}` to the three entitled `Ultra` `agy` accounts (`62af823b`, `0532bad4`, and `338764b8`), and SHALL set `API_HOST=0.0.0.0` in `/Users/androidteam/Omniroute/.env` so host loopback port `20129` serves bridge requests.

#### Scenario: `muse-spark-1.3` executes `gemini-3.8-flash-high` sub-combo without model-pin warning
- **WHEN** a request targets `muse-spark-1.3`
- **THEN** OmniRoute SHALL match `muse-spark-1.3` (`context_cache_protection: false`, `nestedComboMode: "execute"`, `targetTimeoutMs: 25000`) and execute `gemini-3.8-flash-high` using its 16-factor `auto` strategy without logging false `provider durably unhealthy — dropping pin` warnings

#### Scenario: `claude-opus-5.5` load-balances and pins across all 8 Opus accounts via `auto` strategy
- **WHEN** a request targets `claude-opus-5.5`
- **THEN** OmniRoute SHALL score all 8 `agy` Opus accounts using 16-factor `auto` routing (`tierPriority`, `health`, `quota`) and pin multi-turn sessions via `applySessionStickiness` before falling back to `gemini-3.8-flash-high` targets

#### Scenario: Host loopback port `20129` reaches container API bridge
- **WHEN** a request is sent to `http://127.0.0.1:20129/v1/models` or `http://127.0.0.1:20129/v1/responses`
- **THEN** `apiBridgeServer.ts` (`API_HOST=0.0.0.0` inside the container, mapped to `127.0.0.1:20129:20129` on the host) SHALL accept the connection and serve the response
