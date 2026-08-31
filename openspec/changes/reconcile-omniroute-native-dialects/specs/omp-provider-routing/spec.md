## MODIFIED Requirements

### Requirement: Anthropic Messages wire protocol

Each omp provider's transport SHALL match the endpoint and model namespace it serves. The existing direct `shopapikey` provider SHALL remain Anthropic Messages as previously configured. The OmniRoute PM provider SHALL use `api: anthropic-messages`, host-root `baseUrl: http://localhost:20128`, and model `pm/Claude-Fable`. The OmniRoute SH provider SHALL use `api: openai-responses`, `baseUrl: http://localhost:20128/v1`, and model `sh/gpt-5.6-sol` when the native probe passes. When FBC-1 is recorded, a dedicated SH fallback provider SHALL instead use `api: openai-completions`, root `baseUrl: http://localhost:20128`, and the exact model `sh/gpt-5.6-sol`.

#### Scenario: OmniRoute native or proven fallback provider protocol match

- **WHEN** `~/.omp/agent/models.yml` is inspected
- **THEN** the provider containing `pm/Claude-Fable` SHALL declare `api: anthropic-messages` and `baseUrl: http://localhost:20128`
- **AND** the provider containing `sh/gpt-5.6-sol` SHALL declare `api: openai-responses` and `baseUrl: http://localhost:20128/v1` when its native probe passes
- **AND** when FBC-1 is recorded, a dedicated provider containing `sh/gpt-5.6-sol` SHALL declare `api: openai-completions` and root `baseUrl: http://localhost:20128`
- **AND** no Responses provider SHALL use `sh/Claude-Fable` as the corrected Claude route

#### Scenario: protocol match

Given provider blocks in `models.yml`
When inspected programmatically
Then `shopapikey.api` SHALL be `anthropic-messages`
And `phanmemvip.api` SHALL be `openai-responses`
And `cockpit.api` SHALL be `openai-responses`.

### Requirement: Existing omniroute provider SHALL remain available while its stale Claude binding is reconciled

The existing OmniRoute provider SHALL remain selectable and its unrelated model entries, role assignments, fallback chains, and defaults SHALL be preserved. Its stale `sh/Claude-Fable` entry SHALL NOT remain as the authoritative Claude route under an OpenAI Responses provider; the corrected PM model SHALL be exposed through a sibling `anthropic-messages` provider. OmniRoute SHALL remain absent from omp `modelRoles` and `retry.fallbackChains` unless a separate role-allocation approval is recorded.

#### Scenario: corrected OmniRoute catalog remains available

- **WHEN** `omp models` is executed after the reconciliation
- **THEN** the Responses provider SHALL list `sh/gpt-5.6-sol`
- **AND** the Messages provider SHALL list `pm/Claude-Fable`
- **AND** unrelated pre-existing OmniRoute models SHALL remain available unless their live catalog entries are retired

#### Scenario: no implicit role or fallback assignment

- **WHEN** `~/.omp/agent/config.yml` is compared before and after the change
- **THEN** `modelRoles` and fallback chains SHALL be byte-identical
- **AND** no new selector SHALL route through OmniRoute without explicit role approval

### Requirement: Credential reference by env-var name

Every OmniRoute provider added or corrected by this change SHALL reference the `OMNIROUTE_API_KEY` environment variable name through `apiKey` and SHALL not add a literal key. Existing unrelated provider references SHALL remain unchanged.

#### Scenario: OmniRoute providers use external credentials

- **WHEN** the two OmniRoute provider blocks are inspected
- **THEN** both `apiKey` values SHALL equal `OMNIROUTE_API_KEY`
- **AND** no literal credential prefix SHALL appear in the active models file

#### Scenario: no secrets in config files

Given the provider blocks are written to `models.yml`
When the file is inspected
Then no string matching `pmv_`, `agt_`, or `sk-` SHALL appear in the file.
