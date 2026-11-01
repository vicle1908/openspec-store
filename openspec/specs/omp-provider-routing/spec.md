# omp-provider-routing Specification

## Purpose
Defines the provider blocks, wire transports, credential references, role allocation, and native Cockpit routing for omp (oh-my-pi). All three custom providers use environment-variable credential references and are verified through real CLI smoke tests.

## Requirements

### Requirement: Credential reference by env-var name

Every OmniRoute provider added or corrected by this change SHALL reference the `OMNIROUTE_API_KEY` environment variable name through `apiKey` and SHALL not add a literal key. Existing unrelated provider references SHALL remain unchanged.

#### Scenario: OmniRoute providers use external credentials

- **WHEN** the two OmniRoute provider blocks are inspected
- **THEN** both `apiKey` values SHALL equal `OMNIROUTE_API_KEY`
- **AND** no literal credential prefix SHALL appear in the active models file

#### Scenario: no secrets in config files

- **GIVEN** the provider blocks are written to `models.yml`
- **WHEN** the file is inspected
- **THEN** no string matching `pmv_`, `agt_`, or `sk-` SHALL appear in the file.

### Requirement: Anthropic Messages wire protocol

Each omp provider's transport SHALL match the endpoint and model namespace it serves (`shopapikey` and `omniroute-anthropic` as `anthropic-messages`; `omniroute`, `phanmemvip`, and `cockpit` as `openai-responses`).

#### Scenario: OmniRoute native or proven fallback provider protocol match

- **WHEN** `~/.omp/agent/models.yml` is inspected
- **THEN** the provider containing `pm/Claude-Fable` SHALL declare `api: anthropic-messages` and `baseUrl: http://localhost:20128`
- **AND** the provider containing `sh/gpt-5.6-sol` SHALL declare `api: openai-responses` and `baseUrl: http://localhost:20128/v1` when its native probe passes
- **AND** when FBC-1 is recorded, a dedicated provider containing `sh/gpt-5.6-sol` SHALL declare `api: openai-completions` and root `baseUrl: http://localhost:20128`
- **AND** no Responses provider SHALL use `sh/Claude-Fable` as the corrected Claude route

#### Scenario: protocol match

- **GIVEN** provider blocks in `models.yml`
- **WHEN** inspected programmatically
- **THEN** `shopapikey.api` SHALL be `anthropic-messages`
- **AND** `phanmemvip.api` SHALL be `openai-responses`
- **AND** `cockpit.api` SHALL be `openai-responses`.

### Requirement: Canonical model IDs

Model IDs in `models.yml` SHALL use the canonical upstream identifiers (`Claude-Fable`, `gpt-5.6-sol`, `gpt-5.6-luna`) confirmed by response metadata. The `[1m]` suffixed variants SHALL NOT be used until isolated-profile testing proves omp parses bracket notation correctly.

#### Scenario: model ID in response

- **GIVEN** `shopapikey/Claude-Fable` is selected
- **WHEN** a prompt is sent
- **THEN** the response `model` field SHALL contain `Claude-Fable`.

#### Scenario: phanmemvip model ID in response

- **GIVEN** `phanmemvip/gpt-5.6-sol` is selected
- **WHEN** a prompt is sent
- **THEN** the response SHALL identify model `gpt-5.6-sol`.

### Requirement: Base URL convention verified

The `baseUrl` value for each provider SHALL be validated by isolated-profile smoke testing. The exact URL (with or without `/v1` suffix) SHALL match what omp's Anthropic Messages transport actually constructs. If the test fails, the `baseUrl` SHALL be adjusted and re-tested.

#### Scenario: request reaches the upstream API

- **GIVEN** a provider block with a specific `baseUrl`
- **WHEN** `omp --profile <test> -p "reply: pong" --model <provider>/<model>` is run
- **THEN** the upstream API SHALL return HTTP 200 with a valid response.

### Requirement: Conservative metadata

Provider blocks SHALL omit `reasoning`, `contextWindow`, `maxTokens`, and `cost` fields until isolated-profile testing validates them.

#### Scenario: minimal provider schema

- **GIVEN** a provider block in `models.yml`
- **THEN** it SHALL contain only: `baseUrl`, `apiKey`, `api`, `auth`, and `models[]`
- **AND** each model entry SHALL contain only: `id`, `name`, `input`.

### Requirement: Existing omniroute preserved

The OmniRoute provider block in `models.yml` SHALL remain unchanged and available in the `/model` picker. OmniRoute SHALL NOT be assigned to any `modelRoles` entry in `config.yml`. OmniRoute SHALL NOT appear in any `retry.fallbackChains` key or entry; it remains defined in the catalog but unrouted.

#### Scenario: omniroute still works after change

- **GIVEN** the three new provider blocks are present in `models.yml`
- **WHEN** `omp models` is executed
- **THEN** `omniroute` models SHALL appear with identical metadata.

#### Scenario: no role points at OmniRoute

- **GIVEN** `modelRoles` is updated in `config.yml`
- **WHEN** `config.yml` is inspected programmatically
- **THEN** no `modelRoles` value SHALL contain the string `omniroute`.

#### Scenario: no fallback chain references OmniRoute

- **GIVEN** `retry.fallbackChains` is updated in `config.yml`
- **WHEN** `config.yml` is inspected programmatically
- **THEN** no fallback-chain key and no fallback-chain entry SHALL contain the string `omniroute`.

### Requirement: Isolated profile validation

Both `models.yml` and `config.yml` SHALL be validated in an isolated omp profile before live application. The test profile SHALL contain both files. The `modelRoles` key SHALL NOT appear in `models.yml`. The isolated profile SHALL resolve native-provider credentials (`openrouter`, `google-antigravity`) by seeding its `agent.db` `auth_*` tables READ-ONLY from the live profile's `agent.db`; the live `agent.db` SHALL NOT be mutated by the seeding.

#### Scenario: isolated profile includes both files

- **GIVEN** the isolated profile directory
- **WHEN** inspected
- **THEN** both `models.yml` and `config.yml` SHALL be present.

#### Scenario: isolated profile smoke test

- **GIVEN** a temporary profile with proposed `models.yml` and `config.yml`
- **WHEN** `omp --profile <test> --no-session --model <selector> -p "reply only: pong"` is run
- **THEN** each of the seven distinct final role selectors — `openrouter/stealth/ox-alpha:max`, `cockpit/gpt-5.6-luna:max`, `cockpit/gpt-5.6-sol:max`, `cockpit/gpt-5.6-sol:xhigh`, `phanmemvip/gpt-5.6-sol:xhigh`, `google-antigravity/gemini-3.8-flash:high`, `shopapikey/Claude-Fable:low` — SHALL return "pong" with exit code 0
- **AND** each result SHALL be judged ON the requested selector, so a 401→fallback masquerade (error or model_change lines in the output) SHALL fail the gate.

#### Scenario: native provider credentials resolve in the isolated profile

- **GIVEN** the isolated profile's `agent.db` was seeded READ-ONLY from the live profile's `agent.db` `auth_*` tables
- **WHEN** a native-provider selector (`openrouter/stealth/ox-alpha:max` or `google-antigravity/gemini-3.8-flash:high`) is smoke-tested in the isolated profile
- **THEN** the credential SHALL resolve from the seeded `auth_*` tables
- **AND** the live `/Users/androidteam/.omp/agent/agent.db` SHALL remain byte-for-byte unmutated by the seeding.

### Requirement: No live config mutation without approval

The live `~/.omp/agent/models.yml` and `~/.omp/agent/config.yml` SHALL NOT be modified until isolated profile testing succeeds for all three providers AND the user explicitly approves the rollout.

#### Scenario: live files unchanged during testing

- **GIVEN** isolated profile testing is in progress
- **WHEN** `~/.omp/agent/models.yml` is compared to its pre-change state
- **THEN** the files SHALL be byte-for-byte identical.

### Requirement: Capability-based role allocation

omp `modelRoles` in `config.yml` SHALL be assigned based on observed omp catalog capabilities, with explicit thinking-level suffixes validated through isolated-profile smoke testing.

#### Scenario: thinking-level selectors work

- **GIVEN** `google-antigravity/gemini-3.8-flash:high` is a validated explicit selector assigned to `smol`, `tiny`, and `vision`
- **WHEN** invoked through omp
- **THEN** the response SHALL contain "pong" and exit 0.

#### Scenario: max thinking level works

- **GIVEN** `phanmemvip/gpt-5.6-sol:max` is assigned to `default`, `cockpit/gpt-5.6-luna:max` is assigned to `slow`, and `cockpit/gpt-5.6-sol:max` is assigned to `plan`
- **WHEN** invoked through omp
- **THEN** the response SHALL contain "pong" and exit 0.

#### Scenario: lightweight model works

- **GIVEN** `shopapikey/Claude-Fable:low` is assigned to `commit`
- **WHEN** invoked through omp
- **THEN** the response SHALL contain "pong" and exit 0, subject to provider-side rate limits.

#### Scenario: third-provider task model works

- **GIVEN** `phanmemvip/gpt-5.6-sol:xhigh` is assigned to `task`
- **WHEN** invoked through omp
- **THEN** the response SHALL contain "pong" and exit 0.

#### Scenario: no-flag default resolves to native Cockpit

- **GIVEN** `default` is bound to `phanmemvip/gpt-5.6-sol:max`
- **WHEN** `omp --mode json --no-session -p "reply only: pong"` is run without `--model`
- **THEN** the default role SHALL resolve to `phanmemvip/gpt-5.6-sol:max`, return "pong" with exit 0, and emit no fallback events.

### Requirement: Per-file atomic replacement with coordinated rollback

Each file (`models.yml`, `config.yml`) SHALL be updated via atomic rename from a validated temp file. Files SHALL be updated sequentially, not atomically as a pair. If the second replacement fails, the first SHALL be restored immediately. If any live verification fails, both SHALL be restored.

#### Scenario: atomic write

- **GIVEN** the temp files are valid and verified
- **WHEN** `os.rename()` replaces each live file
- **THEN** the file permissions SHALL match the original and the file SHALL parse correctly.

#### Scenario: rollback on partial failure

- **GIVEN** `models.yml` was updated but `config.yml` update fails
- **WHEN** the rollback is executed
- **THEN** `models.yml` SHALL be restored to its pre-change backup
- **AND** its `md5 -q` SHALL match the pre-change baseline.

### Requirement: Rollback capability

Timestamped backups of both `models.yml` and `config.yml` SHALL exist before live mutation. Restore commands SHALL be documented in `tasks.md`.

#### Scenario: rollback restores baseline

- **GIVEN** backups exist at known paths
- **WHEN** the restore command is executed
- **THEN** `md5 -q` of each file SHALL match its pre-change baseline.

### Requirement: Native Cockpit preflight

Before live mutation, the preflight SHALL verify that Cockpit Tools.app is listening on port 51006 and that native `/v1/responses` succeeds. The current omp cockpit endpoint SHALL be `http://localhost:51006/v1` with `api: openai-responses`. The Claude Code compatibility adapter remains externally owned at host port 8788 (container port 8787) and SHALL NOT be used by omp.

#### Scenario: port 51006 responds

- **GIVEN** the preflight check
- **WHEN** a valid OpenAI Responses request is sent to `http://localhost:51006/v1/responses`
- **THEN** the response SHALL be HTTP 200 with a valid JSON body containing `model: gpt-5.6-luna`.

#### Scenario: current cockpit uses adapter port

- **GIVEN** the pre-change state before this correction
- **WHEN** `models.yml` is inspected programmatically
- **THEN** `cockpit.baseUrl` SHALL have been `http://localhost:8788`
- **AND** `cockpit.api` SHALL have been `anthropic-messages`.

#### Scenario: no adapter port dependency after change

- **GIVEN** the corrected `models.yml`
- **WHEN** all omp provider base URLs are inspected
- **THEN** no omp provider SHALL reference `localhost:8787` or `localhost:8788`.

#### Scenario: omp uses native cockpit

- **GIVEN** the corrected `models.yml`
- **THEN** `cockpit.baseUrl` SHALL be `http://localhost:51006/v1`
- **AND** `cockpit.api` SHALL be `openai-responses`.

#### Scenario: adapter remains external to omp

- **GIVEN** the adapter Docker Compose mapping `127.0.0.1:8788:8787`
- **WHEN** all omp provider base URLs are inspected
- **THEN** no omp provider SHALL reference `localhost:8787` or `localhost:8788`.

### Requirement: No new plaintext credentials

All provider blocks SHALL reference credentials via environment-variable names. The pre-existing OmniRoute credential is explicitly preserved and outside the credential-migration scope.

#### Scenario: env-var references only

- **GIVEN** the three custom provider blocks
- **WHEN** `models.yml` is inspected programmatically
- **THEN** each `apiKey` value SHALL start with `HERMES_CUSTOM_` and SHALL NOT
match patterns `pmv_`, `agt_`, or `sk-`.

### Requirement: Provider declaration for the active provider set

omp's `models.yml` SHALL declare provider blocks as siblings under `providers:`. Each provider's `api:` field SHALL match its actual wire transport.

#### Scenario: providers appear in model listing

- **GIVEN** the provider blocks are present in `models.yml`
- **WHEN** `omp models` is executed
- **THEN** the output SHALL list models under `shopapikey`, `phanmemvip`, `cockpit`
- **AND** the existing `omniroute` models SHALL remain listed unchanged.

#### Scenario: cockpit uses native endpoint

- **GIVEN** the Cockpit provider block in `models.yml`
- **THEN** its `baseUrl` SHALL be `http://localhost:51006/v1`
- **AND** its `api` SHALL be `openai-responses`
- **AND** its `apiKey` SHALL reference `HERMES_CUSTOM_COCKPIT_API_KEY`
- **AND** its model list SHALL include `gpt-5.6-luna`.

#### Scenario: shopapikey unchanged

- **GIVEN** the shopapikey provider block
- **THEN** its `api` SHALL remain `anthropic-messages`
- **AND** its `baseUrl` and model list SHALL be unchanged.

#### Scenario: phanmemvip uses the Responses endpoint

- **GIVEN** the phanmemvip provider block in `models.yml`
- **THEN** its `baseUrl` SHALL be `https://api.phanmemvip.shop/v1`
- **AND** its `api` SHALL be `openai-responses`
- **AND** its `apiKey` SHALL reference `HERMES_CUSTOM_PHANMEMVIP_API_KEY`
- **AND** its model list SHALL include `gpt-5.6-sol`.

#### Scenario: giaoduc block removed

- **GIVEN** the migrated `models.yml`
- **WHEN** inspected programmatically
- **THEN** no provider block named `giaoduc` SHALL exist
- **AND** no model selector SHALL reference `giaoduc`.

### Requirement: phanmemvip SHALL be consumed via the OpenAI Responses API only

Every consumer that routes the phanmemvip provider SHALL use the OpenAI Responses API (`POST /v1/responses`, or the consumer's equivalent Responses dialect). No consumer SHALL route phanmemvip through the Anthropic Messages protocol.

#### Scenario: OMP phanmemvip uses Responses

- **GIVEN** the phanmemvip provider block in `models.yml`
- **THEN** its `api` SHALL be `openai-responses`
- **AND** its `baseUrl` SHALL be `https://api.phanmemvip.shop/v1`.

#### Scenario: goose phanmemvip uses the OpenAI engine

- **GIVEN** `~/.config/goose/custom_providers/custom_phanmemvip.json`
- **THEN** its `engine` SHALL be `openai`
- **AND** goose SHALL route `gpt-5.6-sol` through the Responses format.

### Requirement: Fallback chain composition and coverage

`retry.fallbackChains` in `config.yml` SHALL maintain a `default` chain inherited by roles without their own chain, plus role-keyed, model-selector-keyed, and `provider/*` wildcard-keyed chains.

#### Scenario: default chain order and terminal flash hop

- **GIVEN** `retry.fallbackChains.default` in `config.yml`
- **WHEN** inspected programmatically
- **THEN** it SHALL equal `[phanmemvip/gpt-5.6-sol, shopapikey/Claude-Fable, cockpit/gpt-5.6-sol, google-antigravity/gemini-3.8-flash:high]` in that order
- **AND** the terminal hop SHALL carry the explicit `:high` thinking suffix
- **AND** no entry SHALL contain the string `omniroute`.

#### Scenario: model-keyed chains survive role reassignment

- **GIVEN** the model-keyed chains in `retry.fallbackChains`
- **WHEN** inspected programmatically
- **THEN** `phanmemvip/gpt-5.6-sol` SHALL map to `[cockpit/gpt-5.6-sol, shopapikey/Claude-Fable]`
- **AND** `cockpit/gpt-5.6-luna` SHALL map to `[cockpit/gpt-5.6-sol, shopapikey/Claude-Fable]`
- **AND** `cockpit/gpt-5.6-sol` SHALL map to `[cockpit/gpt-5.6-luna, shopapikey/Claude-Fable]`.

#### Scenario: antigravity wildcard chain follows the documented pattern

- **GIVEN** the `google-antigravity/*` wildcard chain in `retry.fallbackChains`
- **WHEN** inspected programmatically
- **THEN** it SHALL map to `[google/*, google-vertex/*, shopapikey/Claude-Fable]`
- **AND** `provider/*` entries SHALL swap provider keeping the model id
- **AND** ids absent on the target provider SHALL be skipped without error.

#### Scenario: no retired or unused gateway appears in any chain

- **GIVEN** `retry.fallbackChains` in `config.yml`
- **WHEN** inspected programmatically
- **THEN** no chain key and no chain entry SHALL contain the string `omniroute`
- **AND** no chain key and no chain entry SHALL contain the string `giaoduc`.

### Requirement: Existing omniroute provider SHALL remain available while its stale Claude binding is reconciled

The existing OmniRoute provider SHALL remain selectable and its model entries, role assignments, fallback chains, and defaults SHALL be preserved while exposing `pm/Claude-*` models through a sibling `anthropic-messages` provider.

#### Scenario: corrected OmniRoute catalog remains available

- **WHEN** `omp models` is executed after the reconciliation
- **THEN** the Responses provider SHALL list `sh/gpt-5.6-sol`
- **AND** the Messages provider SHALL list `pm/Claude-Fable`
- **AND** unrelated pre-existing OmniRoute models SHALL remain available unless their live catalog entries are retired

#### Scenario: no implicit role or fallback assignment

- **WHEN** `~/.omp/agent/config.yml` is compared before and after the change
- **THEN** `modelRoles` and fallback chains SHALL be byte-identical
- **AND** no new selector SHALL route through OmniRoute without explicit role approval

### Requirement: OmniRoute Nexus Model Catalog Registration

The OmniRoute provider block in `~/.omp/agent/models.yml` SHALL declare entries for verified Nexus provider models: `nx/deepseek-v4.1-flash`, `nx/deepseek-v4-pro`, and `nx/gemini-4-argon`. Model entries SHALL declare catalog-verified context windows (`900000` for `nx/deepseek-v4.1-flash` and `1000000` for `nx/deepseek-v4-pro` and `nx/gemini-4-argon`), reasoning flags, and input modalities. Non-OmniRoute provider blocks SHALL remain unmutated.

#### Scenario: Nexus models registered in OMP catalog
- **WHEN** `omp models --json` or `~/.omp/agent/models.yml` is inspected
- **THEN** model entries `omniroute/nx/deepseek-v4.1-flash`, `omniroute/nx/deepseek-v4-pro`, and `omniroute/nx/gemini-4-argon` SHALL be present
- **AND** `nx/deepseek-v4.1-flash` SHALL declare `reasoning: true` and `contextWindow: 900000`
- **AND** `nx/deepseek-v4-pro` SHALL declare `reasoning: true` and `contextWindow: 1000000`
- **AND** `nx/gemini-4-argon` SHALL declare `reasoning: true`, `contextWindow: 1000000`, and `input: [text, image]`.

### Requirement: Fast Commit Role Reallocation

The `modelRoles.commit` role in `~/.omp/agent/config.yml` SHALL be assigned to `omniroute/nx/deepseek-v4.1-flash`. The `default`, `task`, `plan`, `slow`, `advisor`, `tiny`, `smol`, and `vision` roles SHALL preserve their existing primary assignments to `omniroute/gemini-3.8-flash-high` and `google-antigravity/gemini-3.8-flash:high`. `nx/Gemini 4 Argon` SHALL NOT be assigned to automatic execution roles while its upstream relay parameter validation is unstable.

#### Scenario: Commit role resolution
- **WHEN** OMP evaluates the `commit` role selector
- **THEN** it SHALL resolve to `omniroute/nx/deepseek-v4.1-flash`
- **AND** `task` and `default` roles SHALL continue resolving to their existing primary models.

### Requirement: Explicit Fail-Closed Fallback Chains for Nexus Models

The `retry.fallbackChains` configuration in `~/.omp/agent/config.yml` SHALL define explicit fallback chains for both `omniroute/nx/deepseek-v4.1-flash` and `omniroute/nx/Gemini 4 Argon`. Each chain SHALL specify `omniroute/gemini-3.8-flash-high` as primary fallback and `google-antigravity/gemini-3.8-flash:high` as secondary fallback.

#### Scenario: Fallback chain structure
- **WHEN** `~/.omp/agent/config.yml` is inspected programmatically
- **THEN** `retry.fallbackChains['omniroute/nx/deepseek-v4.1-flash']` SHALL contain `omniroute/gemini-3.8-flash-high` followed by `google-antigravity/gemini-3.8-flash:high`
- **AND** `retry.fallbackChains['omniroute/nx/Gemini 4 Argon']` SHALL contain `omniroute/gemini-3.8-flash-high` followed by `google-antigravity/gemini-3.8-flash:high`.

### Requirement: Isolated Profile Smoke Gate Verification

Prior to modifying the live `~/.omp/agent/models.yml` and `~/.omp/agent/config.yml` files, proposed changes SHALL be validated in an isolated throwaway profile with empty fallback chains. The isolated profile SHALL verify that `omniroute/nx/deepseek-v4.1-flash` successfully self-serves a completion with exit code 0 and no fallback or error events.

#### Scenario: Isolated profile smoke test
- **WHEN** `omp --profile <test-profile> --no-session --model 'omniroute/nx/deepseek-v4.1-flash' -p 'reply only: pong'` is executed
- **THEN** the process SHALL exit with code 0
- **AND** the response SHALL contain `pong`
- **AND** no `fallback`, `model_change`, or `error` markers SHALL be emitted.

### Requirement: OmniRoute Gemini 4 Argon Combo Model Declaration

The OmniRoute provider block in `~/.omp/agent/models.yml` SHALL declare the top-level combo model `gemini-4-argon` without provider prefix, matching OmniRoute's native combo catalog. The entry SHALL declare `reasoning: true`, effort-based thinking tiers (`low`, `medium`, `high`), tool support, and `input: [text, image]`.

#### Scenario: Combo model registered in OMP catalog
- **WHEN** `omp models --json` is executed
- **THEN** model entry `omniroute/gemini-4-argon` SHALL be present
- **AND** it SHALL declare `reasoning: true` and `contextWindow: 1000000`.

### Requirement: Default Role Allocation to Gemini 4 Argon Combo

In `~/.omp/agent/config.yml`, `modelRoles.default` SHALL be assigned to `omniroute/gemini-4-argon`, `modelRoles.plan` to `google-antigravity/gemini-4-argon:high`, `modelRoles.advisor` to `google-antigravity/gemini-3.8-flash:high`, and `modelRoles.tiny` to `google-antigravity/gemini-3.8-flash:low`, while `modelRoles.smol`, `vision`, `slow`, `commit`, and `task` SHALL resolve to `omniroute/gemini-3.8-flash-high:high`.

#### Scenario: Default turn execution via combo
- **WHEN** OMP executes a turn without an explicit `--model` flag under `default` role selection
- **THEN** the request SHALL route to `omniroute/gemini-4-argon` with `retry.fallbackChains` preserving failover to `omniroute/gemini-3.8-flash-high:high` and `google-antigravity/gemini-3.8-flash:high`
- **AND** the response SHALL be served without unmonitored fallback errors

#### Scenario: Live config role alignment with specification
- **WHEN** `~/.omp/agent/config.yml` is inspected
- **THEN** `modelRoles.default` SHALL equal `'omniroute/gemini-4-argon'`, `modelRoles.plan` SHALL equal `'google-antigravity/gemini-4-argon:high'`, `modelRoles.advisor` SHALL equal `'google-antigravity/gemini-3.8-flash:high'`, `modelRoles.tiny` SHALL equal `'google-antigravity/gemini-3.8-flash:low'`, and `modelRoles.smol` SHALL equal `'omniroute/gemini-3.8-flash-high:high'`
- **AND** `retry.fallbackChains['omniroute/gemini-3.8-flash-high']` and `retry.fallbackChains.smol` SHALL both equal `['google-antigravity/gemini-3.8-flash:high', 'google-antigravity/gemini-4-argon:high']`

### Requirement: Explicit Fail-Closed Fallback for Gemini 4 Argon Combo

The `retry.fallbackChains` configuration in `~/.omp/agent/config.yml` SHALL define an explicit fallback chain for `omniroute/gemini-4-argon` pointing to `omniroute/gemini-3.8-flash-high:high` as primary fallback and `google-antigravity/gemini-3.8-flash:high` as secondary fallback.

#### Scenario: Fallback chain configuration
- **WHEN** `~/.omp/agent/config.yml` is inspected programmatically
- **THEN** `retry.fallbackChains['omniroute/gemini-4-argon']` SHALL equal `['omniroute/gemini-3.8-flash-high:high', 'google-antigravity/gemini-3.8-flash:high']`

### Requirement: Supersession of Pre-OmniRoute Role and Fallback Prohibitions

Canonical OMP routing in `~/.omp/agent/config.yml` SHALL permit validated `omniroute/*` selectors in `modelRoles` and `retry.fallbackChains` whenever backed by explicit fallback chains and isolated-profile smoke verification, superseding earlier bootstrap prohibitions against `omniroute` strings in `config.yml`.

#### Scenario: Validated OmniRoute selectors permitted in fallback chains and roles
- **WHEN** `~/.omp/agent/config.yml` is validated against `omp-provider-routing`
- **THEN** `retry.fallbackChains` entries for `omniroute/gemini-4-argon` and `omniroute/nx/*` pointing to `omniroute/gemini-3.8-flash-high` and `google-antigravity/gemini-3.8-flash:high` SHALL be recognized as compliant
- **AND** `modelRoles` assignments to either `google-antigravity/gemini-4-argon` or `omniroute/gemini-4-argon:high` SHALL be valid when backed by `models.yml` and `retry.fallbackChains`

### Requirement: OMP 18.11.3 prewalk, image budget, and shell completion integration

OMP workstation configuration SHALL support custom gateway `imageCountBudget` declarations in `~/.omp/agent/models.yml`, explicit on-demand `prewalk` configuration (`enabled: false`, `auto: "off"`, `into: "@smol"`, `autoTarget: "@smol"`) in `~/.omp/agent/config.yml`, and guarded Zsh completions in `~/.zshrc`.

#### Scenario: OMP 18.11.3 features are active in shell and agent config
- **WHEN** `~/.omp/agent/config.yml`, `~/.omp/agent/models.yml`, and `~/.zshrc` are inspected
- **THEN** `config.yml` SHALL configure `prewalk` as `{ enabled: false, auto: 'off', into: '@smol', autoTarget: '@smol' }` so prewalk arms only on explicit `--prewalk` or `/prewalk`
- **AND** `models.yml` SHALL declare `imageCountBudget` on custom multimodal gateway models where supported
- **AND** interactive Zsh shells SHALL load `omp completions zsh` behind the `_comps[omp]` guard

### Requirement: OMP OmniRoute Catalog SHALL Declare Tiered Gemini 4 Argon Combo Models

The `providers.omniroute.models` list in `~/.omp/agent/models.yml` SHALL declare top-level combo entries `gemini-4-argon-high`, `gemini-4-argon-medium`, and `gemini-4-argon-low` alongside `gemini-4-argon` and `nx/gemini-4-argon`. Each entry SHALL configure `reasoning: true`, `thinking` effort mode (`efforts: [low, medium, high]` with tier-matched `defaultLevel`), `supportsTools: true`, `input: [text, image]`, `contextWindow: 1000000`, `maxTokens: 65536`, and `imageCountBudget: 20`.

#### Scenario: Tiered Gemini 4 Argon combo selectors registered in OMP catalog
- **WHEN** `omp models --json` and `~/.omp/agent/models.yml` are inspected
- **THEN** selectors `omniroute/gemini-4-argon-high`, `omniroute/gemini-4-argon-medium`, `omniroute/gemini-4-argon-low`, `omniroute/gemini-4-argon`, and `omniroute/nx/gemini-4-argon` SHALL be present
- **AND** each entry SHALL report `reasoning: true`, `contextWindow: 1000000`, and `maxTokens: 65536` matching OmniRoute's Antigravity Argon output cap
- **AND** `thinking.defaultLevel` SHALL equal `high` for `gemini-4-argon-high`, `gemini-4-argon`, and `nx/gemini-4-argon`, `medium` for `gemini-4-argon-medium`, and `low` for `gemini-4-argon-low`

#### Scenario: Isolated-profile and live attribution probes succeed without fallback masquerade
- **WHEN** `omp --mode json --no-session --model "<selector>" -p "reply only: pong"` is executed for `omniroute/gemini-4-argon-high`, `omniroute/gemini-4-argon-medium`, `omniroute/gemini-4-argon-low`, and `omniroute/gemini-4-argon`
- **THEN** each invocation SHALL exit with code `0` and emit `"pong"`
- **AND** assistant event metadata SHALL report `provider: "omniroute"` with zero `retry_fallback_applied` or `retry_fallback_succeeded` events

### Requirement: OMP Fallback Chains SHALL Cover All Gemini 4 Argon Tier Combo Selectors

The `retry.fallbackChains` map in `~/.omp/agent/config.yml` SHALL define explicit fail-closed fallback chains for `omniroute/gemini-4-argon-high`, `omniroute/gemini-4-argon-medium`, `omniroute/gemini-4-argon-low`, and `omniroute/gemini-4-argon`, routing failover to `omniroute/gemini-3.8-flash-high:high` as primary fallback and `google-antigravity/gemini-3.8-flash:high` as secondary fallback.

#### Scenario: Tiered Gemini 4 Argon fallback chains configured in config.yml
- **WHEN** `~/.omp/agent/config.yml` is parsed with a YAML loader
- **THEN** `retry.fallbackChains['omniroute/gemini-4-argon-high']`, `retry.fallbackChains['omniroute/gemini-4-argon-medium']`, `retry.fallbackChains['omniroute/gemini-4-argon-low']`, and `retry.fallbackChains['omniroute/gemini-4-argon']` SHALL each equal `['omniroute/gemini-3.8-flash-high:high', 'google-antigravity/gemini-3.8-flash:high']`
- **AND** existing `modelRoles` assignments SHALL remain aligned with `omp-provider-routing`

### Requirement: Native TypeSafe Jev Judge Role Routing and Fallback Chain

`~/.omp/agent/config.yml` SHALL bind `modelRoles.judge` to `typesafe/jev-1.14.0` without a chat thinking suffix and define `retry.fallbackChains.judge` as `['typesafe/jev-latest', 'typesafe/jev-preview']`, while adding `openrouter`, `lm-studio`, `llama.cpp`, `vscode`, and `ollama` to `disabledProviders` so judgment consumers and chat catalogs never route to unfunded credentials or local embedding endpoints.

#### Scenario: Judge role and fallback chain configured in config.yml
- **WHEN** `~/.omp/agent/config.yml` is parsed with a YAML loader
- **THEN** `modelRoles.judge` SHALL equal `'typesafe/jev-1.14.0'`
- **AND** `retry.fallbackChains.judge` SHALL equal `['typesafe/jev-latest', 'typesafe/jev-preview']`
- **AND** `disabledProviders` SHALL include `'openrouter'`, `'lm-studio'`, `'llama.cpp'`, `'vscode'`, and `'ollama'`

#### Scenario: Live OMP judge catalog and uncached find execution succeed without HTTP 402
- **WHEN** `omp models --kind judge --json` and an uncached `omp find` judgment probe (`OMP_JUDGMENT_CACHE_DB` pointed to a fresh temporary path) are executed
- **THEN** available judge models SHALL resolve exclusively under provider `typesafe` (`typesafe/jev-1.14.0`, `typesafe/jev-latest`, `typesafe/jev-preview`)
- **AND** the judgment probe SHALL complete with `coverage: "complete"`, `stats.requests > 0`, and `stats.failed == 0` with zero `HTTP 402` errors

### Requirement: OMP v18.12.2 Runtime Settings and Legacy Key Hygiene

`~/.omp/agent/config.yml` SHALL configure `isolation.backend: apfs`, `externalThinking: false`, `providers.tinyModelDevice: mlx`, `tui.renderMermaid: true`, and `memories.stage1Concurrency: 2`, and SHALL omit the superseded keys `memories.enabled`, top-level `renderMermaid`, `calc`, and `bashInterceptor.redirects` while preserving `memory.backend: local` and `bashInterceptor.enabled: true`.

#### Scenario: Runtime optimization settings and clean schema in config.yml
- **WHEN** `~/.omp/agent/config.yml` and `omp config` are inspected on `omp v18.14.1`
- **THEN** `isolation.backend` SHALL equal `'apfs'`, `externalThinking` SHALL equal `false`, `providers.tinyModelDevice` SHALL equal `'mlx'`, and `memories.stage1Concurrency` SHALL equal `2`
- **AND** superseded keys `memories.enabled`, top-level `renderMermaid`, `calc`, and `bashInterceptor.redirects` SHALL be absent while `memory.backend: local` and `bashInterceptor.enabled: true` remain active

### Requirement: Cockpit Reasoning Metadata and Wildcard Fallback Chain Coverage

`~/.omp/agent/models.yml` SHALL declare exact native model identifiers for all 10 Cockpit text and coding models, accurate 272,000-token context windows, 128,000-token maximum output limits, `supportsTools: true`, `input: [text]`, and supported thinking effort modes matching the local Cockpit Tools backend (`http://localhost:51006/v1`), and `~/.omp/agent/config.yml` SHALL use `retry.fallbackChains['cockpit/*']` for fail-closed failover resilience.

#### Scenario: Cockpit models declare reasoning efforts and wildcard fallback chain
- **WHEN** `~/.omp/agent/models.yml` and `~/.omp/agent/config.yml` are loaded on OMP start
- **THEN** every model under `providers.cockpit.models` SHALL declare `reasoning: true`, `supportsTools: true`, `input: ['text']`, and `thinking.efforts` equal to `['low', 'medium', 'high', 'xhigh', 'max']`
- **AND** `retry.fallbackChains['cockpit/*']` SHALL equal `['google-antigravity/gemini-4-argon:high', 'omniroute/gemini-3.8-flash-high:high', 'google-antigravity/gemini-3.8-flash:high']` without duplicate `cockpit/gpt-6-astra` or `cockpit/gpt-6.1-sol` keys
- **AND** `retry.fallbackChains['google-antigravity/*']` SHALL equal `['omniroute/gemini-3.8-flash-high:high', 'google-antigravity/gemini-3.8-flash:high']`

#### Scenario: Full Native Model Catalog Declared
- **WHEN** OMP parses `models.yml` for the `cockpit` provider
- **THEN** it SHALL resolve exactly 10 distinct native chat and coding models: `gpt-6.1-sol`, `gpt-6.1-terra`, `gpt-6-astra`, `gpt-6-sol`, `gpt-6-luna`, `gpt-5.6-sol`, `gpt-5.6-terra`, `gpt-5.6-luna`, `codex-auto-review`, and `gpt-reserve`
- **AND** every model SHALL declare `contextWindow: 272000`, `maxTokens: 128000`, `supportsTools: true`, and `input: [text]`
- **AND** all 10 models SHALL declare `efforts: [low, medium, high, xhigh, max]` capped at `max` per OMP schema validation constraints
- **AND** non-chat image generator endpoint `gpt-image-2.5` SHALL be omitted from `providers.cockpit.models`

#### Scenario: Context Window Compaction Protection
- **WHEN** an agent conversation reaches large token volumes on a Cockpit model
- **THEN** OMP's client-side compaction threshold SHALL trigger at or before 220,000 tokens via `compaction.modelThresholds['cockpit/*']` (below Cockpit's 244,800-token auto-compact ceiling)
- **AND** OMP SHALL NOT send requests exceeding 272,000 tokens to the Cockpit endpoint

#### Scenario: Service Downtime Fallback Delegation
- **WHEN** Cockpit Tools is restarting or unavailable on `127.0.0.1:51006` and returns `ECONNREFUSED`
- **THEN** OMP SHALL automatically fail over via the `cockpit/*` fallback chain to `google-antigravity/gemini-4-argon:high` without terminating the agent session

### Requirement: OmniRoute Retired Model Pruning and v18.12.0 Context Window Alignment

`~/.omp/agent/models.yml` SHALL omit all retired `sh/*` model entries under `providers.omniroute.models` and the retired `omniroute-chat` provider block, and SHALL set `contextWindow: 128000` on `nx/deepseek-v4.1-flash` and `contextWindow: 200000` on `providers.omniroute-anthropic.models` (`pm/Claude-Fable`, `pm/Claude-Opus`, `pm/Claude-Sonnet`) to match live OmniRoute `/v1/models` limits under OMP `v18.12.0+` custom catalog precedence.

#### Scenario: Retired sh/* models removed and context windows aligned with live OmniRoute
- **WHEN** `~/.omp/agent/models.yml` and `omp models --json` are inspected against `http://127.0.0.1:20128/v1/models`
- **THEN** no `sh/*` model ID or `omniroute-chat` provider SHALL exist in `~/.omp/agent/models.yml`
- **AND** `omniroute/nx/deepseek-v4.1-flash` SHALL report `contextWindow: 128000` and `omniroute-anthropic/pm/Claude-*` SHALL report `contextWindow: 200000`

### Requirement: OmniRoute No-Memory Headers, Reasoning Compat, and Root Key Hygiene

In `~/.omp/agent/models.yml`, `providers.omniroute` and `providers.omniroute-anthropic` SHALL declare `headers: { "x-omniroute-no-memory": "true" }`, `providers.omniroute` SHALL declare `compat: { supportsReasoningEffort: true, supportsDeveloperRole: false }`, and the unused root `equivalence` key and `promptCache` fields SHALL be absent.

#### Scenario: OmniRoute models retain thinking effort ladder and opt out of gateway memory injection
- **WHEN** `~/.omp/agent/models.yml` and `omp models --json` are inspected
- **THEN** `providers.omniroute.headers['x-omniroute-no-memory']` and `providers.omniroute-anthropic.headers['x-omniroute-no-memory']` SHALL both equal `'true'`
- **AND** `providers.omniroute.compat` SHALL set `supportsReasoningEffort: true` and `supportsDeveloperRole: false` so `omniroute/gemini-4-argon`, `omniroute/gemini-4-argon-high`, `omniroute/gemini-4-argon-medium`, `omniroute/gemini-4-argon-low`, and `omniroute/nx/gemini-4-argon` report `thinking: ["low", "medium", "high"]` instead of `null` in `omp models --json` while sending system prompts with `role: "system"`
- **AND** root key `equivalence` and model-level `promptCache` keys SHALL be absent from `~/.omp/agent/models.yml`

### Requirement: OMP v18.14.1 Background Concurrency, Compaction, and Resilience Tuning

`~/.omp/agent/config.yml` SHALL configure `title.generator: tiny`, `memories.stage1Concurrency: 2`, `contextPromotion.enabled: true`, `compaction` (`reserveTokens: 65536`, `keepRecentTokens: 40000`, `idleEnabled: true`, `asyncEnabled: true`, `dropUseless: true`, `modelThresholds['cockpit/*']: 220000`), `bash` (`gitGuard: true`, `allowCompoundCommands: true`), `lsp` (`enabled: true`, `diagnosticsOnWrite: true`, `diagnosticsOnEdit: true`, `formatOnWrite: true`), and `retry` resilience flags.

#### Scenario: Background settings and compaction prevent Ultra pool starvation
- **WHEN** `~/.omp/agent/config.yml` is parsed with a YAML loader
- **THEN** `title.generator` SHALL equal `'tiny'`, `memories.stage1Concurrency` SHALL equal `2`, `contextPromotion.enabled` SHALL equal `true`, and `lsp` SHALL equal `{ enabled: true, diagnosticsOnWrite: true, diagnosticsOnEdit: true, formatOnWrite: true }`
- **AND** `compaction.reserveTokens` SHALL equal `65536`, `compaction.keepRecentTokens` SHALL equal `40000`, `compaction.idleEnabled` SHALL equal `true`, `compaction.asyncEnabled` SHALL equal `true`, `compaction.dropUseless` SHALL equal `true`, `compaction.modelThresholds['cockpit/*']` SHALL equal `220000`, `bash.gitGuard` SHALL equal `true`, and `bash.allowCompoundCommands` SHALL equal `true`

#### Scenario: Resilience flags and role/wildcard fallback chains are active
- **WHEN** `retry` in `~/.omp/agent/config.yml` is inspected
- **THEN** `retry.rateLimitWalksChain` SHALL equal `true`, `retry.usageAwareFallback` SHALL equal `true`, and `retry.usageReservePolicy` SHALL equal `'auto'`
- **AND** `retry.fallbackChains.advisor`, `retry.fallbackChains.smol`, and `retry.fallbackChains['omniroute/*']` SHALL be defined with validated failover targets

### Requirement: OMP OmniRoute Catalog and Fallback Chains SHALL Include Multi-Account Claude 5.5 and Muse Spark 1.3 Combos

In `~/.omp/agent/models.yml`, `providers.omniroute.models` SHALL declare top-level combo entries `claude-opus-5.5`, `claude-sonnet-5.5`, and `muse-spark-1.3` in place of single-connection `agy/claude-opus-4-6-thinking` and broken OAuth `mc/muse-spark-1.3`, and `~/.omp/agent/config.yml` SHALL define explicit `retry.fallbackChains` entries for those combos plus `deepseek-v4.1-flash` and `kimi-k3.1-pro`.

#### Scenario: Multi-account Claude 5.5 and Muse Spark 1.3 combos registered in OMP catalog
- **WHEN** `~/.omp/agent/models.yml` and `omp models --json` are inspected
- **THEN** `providers.omniroute.models` SHALL include `claude-opus-5.5` (`maxTokens: 65536`), `claude-sonnet-5.5` (`maxTokens: 65536`), `deepseek-v4.1-flash`, `kimi-k3.1-pro`, `muse-spark-1.3` (`maxTokens: 65536`), `gemini-3.8-flash-high`, and `gemini-4-argon{,-high,-medium,-low}` with `reasoning: true`, `thinking: ["low", "medium", "high"]`, `supportsTools: true`, and `contextWindow: 1000000`
- **AND** single-connection `agy/claude-opus-4-6-thinking` and broken `mc/muse-spark-1.3` SHALL be absent from `providers.omniroute.models`

#### Scenario: Fail-closed fallback chains cover Claude 5.5, DeepSeek, Kimi, and Muse combos
- **WHEN** `~/.omp/agent/config.yml` is parsed with a YAML loader
- **THEN** `retry.fallbackChains['omniroute/claude-opus-5.5']`, `retry.fallbackChains['omniroute/claude-sonnet-5.5']`, `retry.fallbackChains['omniroute/deepseek-v4.1-flash']`, `retry.fallbackChains['omniroute/kimi-k3.1-pro']`, and `retry.fallbackChains['omniroute/muse-spark-1.3']` SHALL each route failover to `['omniroute/gemini-3.8-flash-high:high', 'google-antigravity/gemini-3.8-flash:high']`
