# omp-provider-routing Specification

## Purpose
Defines the provider blocks, wire transports, credential references, role allocation, and native Cockpit routing for omp (oh-my-pi). All three custom providers use environment-variable credential references and are verified through real CLI smoke tests.

## Requirements

### Requirement: Credential reference by env-var name

Each provider block SHALL reference its credential via the `apiKey:` field
pointing to an environment variable name. The three custom providers
(shopapikey, phanmemvip, cockpit) SHALL use environment-variable references
(`HERMES_CUSTOM_*_API_KEY`). This change SHALL introduce no new plaintext
credentials. The pre-existing `omniroute` credential is explicitly preserved
and outside the credential-migration scope.

#### Scenario: no secrets in config files

Given the provider blocks are written to `models.yml`
When the file is inspected
Then no string matching `pmv_`, `agt_`, or `sk-` SHALL appear in the file.

### Requirement: Anthropic Messages wire protocol

Each provider's transport SHALL match its endpoint's actual protocol.

#### Scenario: protocol match

Given provider blocks in `models.yml`
When inspected programmatically
Then `shopapikey.api` SHALL be `anthropic-messages`
And `phanmemvip.api` SHALL be `openai-responses`
And `cockpit.api` SHALL be `openai-responses`.

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

The OmniRoute provider block in `models.yml` SHALL remain unchanged and
available in the `/model` picker. OmniRoute SHALL NOT be assigned to
any `modelRoles` entry in `config.yml`. OmniRoute SHALL NOT appear in any
`retry.fallbackChains` key or entry; it remains defined in the catalog but
unrouted.

#### Scenario: omniroute still works after change

Given the three new provider blocks are present in `models.yml`
When `omp models` is executed
Then `omniroute` models SHALL appear with identical metadata.

#### Scenario: no role points at OmniRoute

Given `modelRoles` is updated in `config.yml`
When `config.yml` is inspected programmatically
Then no `modelRoles` value SHALL contain the string `omniroute`.

#### Scenario: no fallback chain references OmniRoute

Given `retry.fallbackChains` is updated in `config.yml`
When `config.yml` is inspected programmatically
Then no fallback-chain key and no fallback-chain entry SHALL contain the string `omniroute`.

### Requirement: Isolated profile validation

Both `models.yml` and `config.yml` SHALL be validated in an isolated
omp profile before live application. The test profile SHALL contain
both files. The `modelRoles` key SHALL NOT appear in `models.yml`.
The isolated profile SHALL resolve native-provider credentials
(`openrouter`, `google-antigravity`) by seeding its `agent.db` `auth_*`
tables READ-ONLY from the live profile's `agent.db`; the live `agent.db`
SHALL NOT be mutated by the seeding.

#### Scenario: isolated profile includes both files

Given the isolated profile directory
When inspected
Then both `models.yml` and `config.yml` SHALL be present.

#### Scenario: isolated profile smoke test

Given a temporary profile with proposed `models.yml` and `config.yml`
When `omp --profile <test> --no-session --model <selector> -p "reply only: pong"` is run
Then each of the seven distinct final role selectors — `openrouter/stealth/ox-alpha:max`, `cockpit/gpt-5.6-luna:max`, `cockpit/gpt-5.6-sol:max`, `cockpit/gpt-5.6-sol:xhigh`, `phanmemvip/gpt-5.6-sol:xhigh`, `google-antigravity/gemini-3.7-flash:high`, `shopapikey/Claude-Fable:low` — SHALL return "pong" with exit code 0
And each result SHALL be judged ON the requested selector, so a 401→fallback masquerade (error or model_change lines in the output) SHALL fail the gate.

#### Scenario: native provider credentials resolve in the isolated profile

Given the isolated profile's `agent.db` was seeded READ-ONLY from the live profile's `agent.db` `auth_*` tables
When a native-provider selector (`openrouter/stealth/ox-alpha:max` or `google-antigravity/gemini-3.7-flash:high`) is smoke-tested in the isolated profile
Then the credential SHALL resolve from the seeded `auth_*` tables
And the live `/Users/androidteam/.omp/agent/agent.db` SHALL remain byte-for-byte unmutated by the seeding.

### Requirement: No live config mutation without approval

The live `~/.omp/agent/models.yml` and `~/.omp/agent/config.yml`
SHALL NOT be modified until isolated profile testing succeeds for
all three providers AND the user explicitly approves the rollout.

#### Scenario: live files unchanged during testing

Given isolated profile testing is in progress
When `~/.omp/agent/models.yml` is compared to its pre-change state
Then the files SHALL be byte-for-byte identical.

### Requirement: Capability-based role allocation

omp `modelRoles` in `config.yml` SHALL be assigned based on observed
omp catalog capabilities, not upstream provider marketing claims.
The thinking-level suffixes `:high`, `:xhigh`, and `:max` SHALL only be used
for providers where they were validated through omp smoke testing.
`smol`, `tiny`, and `vision` SHALL be bound to
`google-antigravity/gemini-3.7-flash:high` — the only fast catalog entry
with confirmed image input — with an explicit `:high` suffix on every
flash selector so high-frequency background roles never inherit
`defaultThinkingLevel: xhigh`. `commit` SHALL be bound to
`shopapikey/Claude-Fable:low`. All other roles (`slow`, `plan`, `task`, `advisor`) SHALL remain byte-unchanged by this change. The `default` role SHALL remain untouched by this change; any post-apply rebinding of `default` (e.g., the external concurrent migration to `phanmemvip/gpt-5.6-sol:max`) is outside this requirement's scope.

#### Scenario: thinking-level selectors work

Given `google-antigravity/gemini-3.7-flash:high` is a validated explicit selector assigned to `smol`, `tiny`, and `vision`
When invoked through omp
Then the response SHALL contain "pong" and exit 0.

#### Scenario: max thinking level works

Given `cockpit/gpt-5.6-luna:max` is assigned to `slow`, `cockpit/gpt-5.6-sol:max` is assigned to `plan`, and `openrouter/stealth/ox-alpha:max` is smoke-tested as an explicit selector override (the live `default` binding may have been externally rebound after apply)
When invoked through omp
Then the response SHALL contain "pong" and exit 0.

#### Scenario: lightweight model works

Given `shopapikey/Claude-Fable:low` is assigned to `commit`
When invoked through omp
Then the response SHALL contain "pong" and exit 0, subject to provider-side rate limits.

#### Scenario: third-provider task model works

Given `phanmemvip/gpt-5.6-sol:xhigh` is assigned to `task`
When invoked through omp
Then the response SHALL contain "pong" and exit 0.

#### Scenario: no-flag default resolves to native Cockpit

Given the live `default` role binding is owned by the concurrent migration and may point at any provider
When `omp --no-session --model openrouter/stealth/ox-alpha:max -p "reply only: pong"` is run with an explicit model override
Then the response SHALL be served by `openrouter/stealth/ox-alpha:max` and return "pong" with exit 0, independent of whichever model the live `default` role currently binds.

### Requirement: Per-file atomic replacement with coordinated rollback

Each file (`models.yml`, `config.yml`) SHALL be updated via atomic
rename from a validated temp file. Files SHALL be updated sequentially,
not atomically as a pair. If the second replacement fails, the first
SHALL be restored immediately. If any live verification fails, both
SHALL be restored.

#### Scenario: atomic write

Given the temp files are valid and verified
When `os.rename()` replaces each live file
Then the file permissions SHALL match the original and the file SHALL parse correctly.

#### Scenario: rollback on partial failure

Given `models.yml` was updated but `config.yml` update fails
When the rollback is executed
Then `models.yml` SHALL be restored to its pre-change backup
And its `md5 -q` SHALL match the pre-change baseline.

### Requirement: Rollback capability

Timestamped backups of both `models.yml` and `config.yml` SHALL exist
before live mutation. Restore commands SHALL be documented in `tasks.md`.

#### Scenario: rollback restores baseline

Given backups exist at known paths
When the restore command is executed
Then `md5 -q` of each file SHALL match its pre-change baseline.

### Requirement: Native Cockpit preflight

Before live mutation, the preflight SHALL verify that Cockpit Tools.app
is listening on port 51006 and that native `/v1/responses` succeeds.
The current omp cockpit endpoint SHALL be `http://localhost:51006/v1`
with `api: openai-responses`.
The Claude Code compatibility adapter remains externally owned at host
port 8788 (container port 8787) and SHALL NOT be used by omp.

#### Scenario: port 51006 responds

Given the preflight check
When a valid OpenAI Responses request is sent to `http://localhost:51006/v1/responses`
Then the response SHALL be HTTP 200 with a valid JSON body containing `model: gpt-5.6-luna`.

#### Scenario: current cockpit uses adapter port

Given the pre-change state before this correction
When `models.yml` is inspected programmatically
Then `cockpit.baseUrl` SHALL have been `http://localhost:8788`
And `cockpit.api` SHALL have been `anthropic-messages`.

#### Scenario: no adapter port dependency after change

Given the corrected `models.yml`
When all omp provider base URLs are inspected
Then no omp provider SHALL reference `localhost:8787` or `localhost:8788`.

#### Scenario: omp uses native cockpit

Given the corrected `models.yml`
Then `cockpit.baseUrl` SHALL be `http://localhost:51006/v1`
And `cockpit.api` SHALL be `openai-responses`.

#### Scenario: adapter remains external to omp

Given the adapter Docker Compose mapping `127.0.0.1:8788:8787`
When all omp provider base URLs are inspected
Then no omp provider SHALL reference `localhost:8787` or `localhost:8788`.

### Requirement: No new plaintext credentials

All provider blocks SHALL reference credentials via environment-variable names.
The pre-existing OmniRoute credential is explicitly preserved and outside
the credential-migration scope.

#### Scenario: env-var references only

Given the three custom provider blocks
When `models.yml` is inspected programmatically
Then each `apiKey` value SHALL start with `HERMES_CUSTOM_` and SHALL NOT
match patterns `pmv_`, `agt_`, or `sk-`.

### Requirement: Provider declaration for the active provider set

omp's `models.yml` SHALL declare provider blocks as siblings under `providers:`.
Each provider's `api:` field SHALL match its actual wire transport.

#### Scenario: providers appear in model listing

Given the provider blocks are present in `models.yml`
When `omp models` is executed
Then the output SHALL list models under `shopapikey`, `phanmemvip`, `cockpit`
And the existing `omniroute` models SHALL remain listed unchanged.

#### Scenario: cockpit uses native endpoint

Given the Cockpit provider block in `models.yml`
Then its `baseUrl` SHALL be `http://localhost:51006/v1`
And its `api` SHALL be `openai-responses`
And its `apiKey` SHALL reference `HERMES_CUSTOM_COCKPIT_API_KEY`
And its model list SHALL include `gpt-5.6-luna`.

#### Scenario: shopapikey unchanged

Given the shopapikey provider block
Then its `api` SHALL remain `anthropic-messages`
And its `baseUrl` and model list SHALL be unchanged.

#### Scenario: phanmemvip uses the Responses endpoint

Given the phanmemvip provider block in `models.yml`
Then its `baseUrl` SHALL be `https://api.phanmemvip.shop/v1`
And its `api` SHALL be `openai-responses`
And its `apiKey` SHALL reference `HERMES_CUSTOM_PHANMEMVIP_API_KEY`
And its model list SHALL include `gpt-5.6-sol`.

#### Scenario: giaoduc block removed

Given the migrated `models.yml`
When inspected programmatically
Then no provider block named `giaoduc` SHALL exist
And no model selector SHALL reference `giaoduc`.

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

### Requirement: Fallback chain composition and coverage

`retry.fallbackChains` in `config.yml` SHALL maintain a `default` chain
inherited by roles without their own chain, plus model-selector-keyed
chains. Keys containing `/` SHALL bind a chain to that model across role
reassignment. `provider/*` wildcard keys SHALL cover every model of a
provider, and `provider/*` entries inside a chain SHALL swap provider
keeping the model id, with skipped-if-absent semantics for ids missing on
the target provider. The `default` chain SHALL be exactly
`[phanmemvip/gpt-5.6-sol, shopapikey/Claude-Fable, cockpit/gpt-5.6-sol,
google-antigravity/gemini-3.7-flash:high]` in that order, with the flash
selector as the terminal hop carrying an explicit `:high` suffix. No chain
key or entry SHALL reference `omniroute/*` or `giaoduc/*`.

#### Scenario: default chain order and terminal flash hop

Given `retry.fallbackChains.default` in `config.yml`
When inspected programmatically
Then it SHALL equal `[phanmemvip/gpt-5.6-sol, shopapikey/Claude-Fable, cockpit/gpt-5.6-sol, google-antigravity/gemini-3.7-flash:high]` in that order
And the terminal hop SHALL carry the explicit `:high` thinking suffix
And no entry SHALL contain the string `omniroute`.

#### Scenario: model-keyed chains survive role reassignment

Given the model-keyed chains in `retry.fallbackChains`
When inspected programmatically
Then `phanmemvip/gpt-5.6-sol` SHALL map to `[cockpit/gpt-5.6-sol, shopapikey/Claude-Fable]`
And `cockpit/gpt-5.6-luna` SHALL map to `[cockpit/gpt-5.6-sol, shopapikey/Claude-Fable]`
And `cockpit/gpt-5.6-sol` SHALL map to `[cockpit/gpt-5.6-luna, shopapikey/Claude-Fable]`.

#### Scenario: antigravity wildcard chain follows the documented pattern

Given the `google-antigravity/*` wildcard chain in `retry.fallbackChains`
When inspected programmatically
Then it SHALL map to `[google/*, google-vertex/*, shopapikey/Claude-Fable]`
And `provider/*` entries SHALL swap provider keeping the model id
And ids absent on the target provider SHALL be skipped without error.

#### Scenario: no retired or unused gateway appears in any chain

Given `retry.fallbackChains` in `config.yml`
When inspected programmatically
Then no chain key and no chain entry SHALL contain the string `omniroute`
And no chain key and no chain entry SHALL contain the string `giaoduc`.
