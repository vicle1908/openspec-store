# Spec Delta

## ADDED Requirements

### Requirement: OmniRoute Gemini 4 Argon Tier Combos SHALL Route Exclusively Through Entitled Ultra Antigravity CLI Connections

OmniRoute SHALL expose four top-level routing combos for Gemini 4 Argon (`gemini-4-argon-high`, `gemini-4-argon-medium`, `gemini-4-argon-low`, and `gemini-4-argon`) using `strategy: "auto"`, `context_length: 1000000`, `context_cache_protection: false`, and `config.candidatePool: ["agy"]`. Each combo SHALL contain exactly two model steps pinned to the two Google AI `Ultra` `agy` CLI connections (`338764b8-1cd7-4946-b789-ee5dad4c5073` and `0532bad4-2486-4286-8f06-510e9c678620`).

#### Scenario: Tier combos resolve exclusively to the two Ultra agy CLI connections
- **WHEN** `omniroute combo list --output json` or `GET /api/combos` is inspected
- **THEN** combos `gemini-4-argon-high`, `gemini-4-argon-medium`, `gemini-4-argon-low`, and `gemini-4-argon` SHALL each be present with `strategy: "auto"`, `context_length: 1000000`, `context_cache_protection: false`, `config.candidatePool: ["agy"]`, `config.resetAwareQuotaCacheTtlMs: 300000`, and `config.resetAwareQuotaCacheMaxStaleMs: 3600000`
- **AND** `gemini-4-argon-high` and `gemini-4-argon` SHALL each define two `kind: "model"` steps with `model: "agy/gemini-4-argon-high"` and `providerId: "agy"` pinned to `connectionId: "338764b8-1cd7-4946-b789-ee5dad4c5073"` (`vinhghtk1908@gmail.com`) and `connectionId: "0532bad4-2486-4286-8f06-510e9c678620"` (`vinhvumobile@gmail.com`)
- **AND** `gemini-4-argon-medium` SHALL define two `kind: "model"` steps with `model: "agy/gemini-4-argon-medium"` and `providerId: "agy"` pinned to those same two `connectionId` values
- **AND** `gemini-4-argon-low` SHALL define two `kind: "model"` steps with `model: "agy/gemini-4-argon-low"` and `providerId: "agy"` pinned to those same two `connectionId` values
- **AND** no step in any of the four combos SHALL reference `agy/gemini-4-argon-disabled` or any `Pro`-tier `agy` connection

#### Scenario: Combo health check and dual-protocol inference succeed across all Argon combos
- **WHEN** `POST /api/combos/test`, `POST /v1/responses`, or `POST /v1/chat/completions` is invoked for `gemini-4-argon-high`, `gemini-4-argon-medium`, `gemini-4-argon-low`, or `gemini-4-argon`
- **THEN** OmniRoute SHALL route the request to an entitled `Ultra` `agy` connection and return HTTP `200` with non-empty completion output and `X-OmniRoute-Combo-Trace` headers
- **AND** tool-calling and multi-turn tool continuation requests on `POST /v1/responses` SHALL complete with `status: "completed"`

#### Scenario: Disabled sentinel or unentitled Pro connection fails closed without polluting Argon combos
- **WHEN** an upstream `Pro`-tier `agy` connection or the `agy/gemini-4-argon-disabled` sentinel is probed directly
- **THEN** upstream Cloud Code returns HTTP `429` (`Resource has been exhausted`)
- **AND** the four Gemini 4 Argon combos SHALL exclude those connections so production combo traffic does not incur `Pro`-account retry stalls

### Requirement: Un-Suffixed Manual Antigravity Gemini 4 Argon Catalog Override SHALL Be Absent

OmniRoute's `agy` provider model catalog SHALL NOT retain a manual un-suffixed `gemini-4-argon` (`source: "manual"`) custom model override, ensuring that only upstream-supported tiered model IDs (`agy/gemini-4-argon-high`, `agy/gemini-4-argon-medium`, `agy/gemini-4-argon-low`) are advertised as callable `agy` chat models while top-level `gemini-4-argon` resolves via the combo engine.

#### Scenario: Manual un-suffixed agy/gemini-4-argon override removed from provider models
- **WHEN** `GET /api/provider-models` and `GET /v1/models` are inspected
- **THEN** no `source: "manual"` custom model entry with `id: "gemini-4-argon"` SHALL exist under the `agy` provider
- **AND** top-level `gemini-4-argon`, `gemini-4-argon-high`, `gemini-4-argon-medium`, and `gemini-4-argon-low` SHALL be advertised in `/v1/models` with `owned_by: "combo"`
