# omp-provider-routing Delta

## MODIFIED Requirements

### Requirement: Canonical model IDs

Model IDs in `models.yml` SHALL use the canonical upstream identifiers
(`Claude-Fable`, `gpt-5.6-sol`, `gpt-5.6-luna`) confirmed by response metadata.
The `[1m]` suffixed variants SHALL NOT be used until isolated-profile
testing proves omp parses bracket notation correctly.

#### Scenario: model ID in response

Given `shopapikey/Claude-Fable` is selected
When a prompt is sent
Then the response `model` field SHALL contain `Claude-Fable`.

#### Scenario: phanmemvip model ID in response

Given `phanmemvip/gpt-5.6-sol` is selected
When a prompt is sent
Then the response SHALL identify model `gpt-5.6-sol`.

### Requirement: Capability-based role allocation

omp `modelRoles` in `config.yml` SHALL be assigned based on observed
omp catalog capabilities, not upstream provider marketing claims.
The thinking-level suffixes `:high`, `:xhigh`, and `:max` SHALL only be used
for providers where they were validated through omp smoke testing.

#### Scenario: thinking-level selectors work

Given `cockpit/gpt-5.6-luna:high` is a validated explicit selector
When invoked through omp
Then the response SHALL contain "pong" and exit 0.

#### Scenario: max thinking level works

Given `cockpit/gpt-5.6-luna:max` is assigned to `slow`, `plan`, and `default`
When invoked through omp
Then the response SHALL contain "pong" and exit 0.

#### Scenario: lightweight model works

Given `shopapikey/Claude-Fable` is assigned to `smol` and `commit`
When invoked through omp
Then the response SHALL contain "pong" and exit 0, subject to provider-side rate limits.

#### Scenario: third-provider task model works

Given `phanmemvip/gpt-5.6-sol:xhigh` is assigned to `task`
When invoked through omp
Then the response SHALL contain "pong" and exit 0.

#### Scenario: no-flag default resolves to native Cockpit

When a fresh login zsh shell runs `omp --no-session -p "reply only: pong"` without `--model`
Then the default role SHALL resolve to native Cockpit `gpt-5.6-luna:max` and return `pong` with exit 0.

## ADDED Requirements

### Requirement: phanmemvip SHALL be consumed via the OpenAI Responses API only

Every consumer that routes the phanmemvip provider SHALL use the OpenAI Responses API (`POST /v1/responses`, or the consumer's equivalent Responses dialect). No consumer SHALL route phanmemvip through the Anthropic Messages protocol.

#### Scenario: OMP phanmemvip uses Responses

Given the phanmemvip provider block in `models.yml`
Then its `api` SHALL be `openai-responses`
And its `baseUrl` SHALL be `https://api.phanmemvip.shop/v1`.

#### Scenario: goose phanmemvip uses the OpenAI engine

Given `~/.config/goose/custom_providers/custom_phanmemvip.json`
Then its `engine` SHALL be `openai`
And goose SHALL route `gpt-5.6-sol` through the Responses format.
