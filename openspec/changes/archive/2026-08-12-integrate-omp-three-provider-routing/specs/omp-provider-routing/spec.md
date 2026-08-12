## ADDED Requirements

### Requirement: Provider declaration

omp's `models.yml` SHALL declare three new provider blocks alongside the existing
`omniroute` block, using the official `providers:` schema.

#### Scenario: providers appear in model listing

Given the three provider blocks are present in `models.yml`
When `omp models` is executed
Then the output SHALL list models under `shopapikey`, `giaoduc`, and `cockpit`
And the existing `omniroute` models SHALL remain listed unchanged.

### Requirement: Credential reference by env-var name

Each provider block SHALL reference its credential via the `apiKey:` field
pointing to an environment variable name. The three newly added providers SHALL
use environment-variable references (`HERMES_CUSTOM_*_API_KEY`). This change
SHALL introduce no new plaintext credentials. The pre-existing `omniroute`
credential is explicitly preserved and outside the credential-migration scope.

#### Scenario: no secrets in config files

Given the provider blocks are written to `models.yml`
When the file is inspected
Then no string matching `pmv_`, `agt_`, or `sk-` SHALL appear in the file.

### Requirement: Anthropic Messages wire protocol

All three providers use the `anthropic-messages` API transport.
The `api:` field SHALL be set to `anthropic-messages` for each.

#### Scenario: protocol match

Given a provider block with `api: anthropic-messages`
When omp sends a request
Then the request path SHALL end in `/v1/messages`
And the `anthropic-version` header SHALL be present.

### Requirement: Canonical model IDs

Model IDs in `models.yml` SHALL use the canonical upstream identifiers
(`fable-5`, `Advance`, `gpt-5.6-luna`) confirmed by response metadata.
The `[1m]` suffixed variants SHALL NOT be used until isolated-profile
testing proves omp parses bracket notation correctly.

#### Scenario: model ID in response

Given `shopapikey/fable-5` is selected
When a prompt is sent
Then the response `model` field SHALL contain `fable-5`.

### Requirement: Base URL convention verified

The `baseUrl` value for each provider SHALL be validated by isolated-profile
smoke testing. The exact URL (with or without `/v1` suffix) SHALL match
what omp's Anthropic Messages transport actually constructs. If the test
fails, the `baseUrl` SHALL be adjusted and re-tested.

#### Scenario: request reaches the upstream API

Given a provider block with a specific `baseUrl`
When `omp --profile <test> -p "reply: pong" --model <provider>/<model>` is run
Then the upstream API SHALL return HTTP 200 with a valid response.

### Requirement: Conservative metadata

Provider blocks SHALL omit `reasoning`, `contextWindow`, `maxTokens`,
and `cost` fields until isolated-profile testing validates them.

#### Scenario: minimal provider schema

Given a provider block in `models.yml`
Then it SHALL contain only: `baseUrl`, `apiKey`, `api`, `auth`, and `models[]`
And each model entry SHALL contain only: `id`, `name`, `input`.

### Requirement: Existing omniroute preserved

The existing `omniroute` provider block and its role assignments in
`config.yml` SHALL NOT be modified by this change.

#### Scenario: omniroute still works after change

Given the three new provider blocks are added to `models.yml`
When `omp models` is executed
Then `omniroute` models SHALL appear with identical metadata.

### Requirement: Isolated profile validation

Each provider SHALL be tested in an isolated omp profile (`--profile`)
before the configuration is applied to the live `models.yml`.
The test SHALL verify model listing and a single non-interactive prompt.

#### Scenario: isolated profile smoke test

Given a temporary omp profile with the provider blocks
When `omp --profile <temp> models` is executed
Then the provider's models SHALL appear
And `omp --profile <temp> --no-session -p "reply only: pong" --model <provider>/<model>`
SHALL return a response with HTTP-equivalent success.

### Requirement: No live config mutation without approval

The live `~/.omp/agent/models.yml` and `~/.omp/agent/config.yml`
SHALL NOT be modified until isolated profile testing succeeds for
all three providers AND the user explicitly approves the rollout.

#### Scenario: live files unchanged during testing

Given isolated profile testing is in progress
When `~/.omp/agent/models.yml` is compared to its pre-change state
Then the files SHALL be byte-for-byte identical.
