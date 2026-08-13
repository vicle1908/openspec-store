# omp-provider-routing Specification

## Purpose
Defines the provider blocks, wire transports, credential references, role allocation, and native Cockpit routing for omp (oh-my-pi). All three custom providers use environment-variable credential references and are verified through real CLI smoke tests.
## Requirements
### Requirement: Provider declaration

omp's `models.yml` SHALL declare provider blocks as siblings under `providers:`.
Each provider's `api:` field SHALL match its actual wire transport.

#### Scenario: providers appear in model listing

Given the provider blocks are present in `models.yml`
When `omp models` is executed
Then the output SHALL list models under `shopapikey`, `giaoduc`, `cockpit`
And the existing `omniroute` models SHALL remain listed unchanged.

#### Scenario: cockpit uses native endpoint

Given the Cockpit provider block in `models.yml`
Then its `baseUrl` SHALL be `http://localhost:51006/v1`
And its `api` SHALL be `openai-responses`
And its `apiKey` SHALL reference `HERMES_CUSTOM_COCKPIT_API_KEY`
And its model list SHALL include `gpt-5.6-luna`.

#### Scenario: shopapikey and giaoduc unchanged

Given the shopapikey and giaoduc provider blocks
Then their `api` SHALL remain `anthropic-messages`
And their `baseUrl` and model lists SHALL be unchanged.

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

Each provider's transport SHALL match its endpoint's actual protocol.

#### Scenario: protocol match

Given provider blocks in `models.yml`
When inspected programmatically
Then `shopapikey.api` SHALL be `anthropic-messages`
And `giaoduc.api` SHALL be `anthropic-messages`
And `cockpit.api` SHALL be `openai-responses`.

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

The OmniRoute provider block in `models.yml` SHALL remain unchanged and
available in the `/model` picker. OmniRoute SHALL NOT be assigned to
any `modelRoles` entry in `config.yml`.

#### Scenario: omniroute still works after change

Given the three new provider blocks are present in `models.yml`
When `omp models` is executed
Then `omniroute` models SHALL appear with identical metadata.

#### Scenario: no role points at OmniRoute

Given `modelRoles` is updated in `config.yml`
When `config.yml` is inspected programmatically
Then no `modelRoles` value SHALL contain the string `omniroute`.

### Requirement: Isolated profile validation

Both `models.yml` and `config.yml` SHALL be validated in an isolated
omp profile before live application. The test profile SHALL contain
both files. The `modelRoles` key SHALL NOT appear in `models.yml`.

#### Scenario: isolated profile includes both files

Given the isolated profile directory
When inspected
Then both `models.yml` and `config.yml` SHALL be present.

#### Scenario: isolated profile smoke test

Given a temporary profile with proposed `models.yml` and `config.yml`
When `omp --profile <test> --no-session --model <selector> -p "reply only: pong"` is run
Then each of the six role selectors SHALL return "pong" with exit code 0.

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
The thinking-level suffixes `:high` and `:max` SHALL only be used for
providers where they were validated through omp smoke testing.

#### Scenario: thinking-level selectors work

Given `cockpit/gpt-5.6-luna:high` is a validated explicit selector
When invoked through omp
Then the response SHALL contain "pong" and exit 0.

#### Scenario: max thinking level works

Given `cockpit/gpt-5.6-luna:max` is assigned to `slow`, `plan`, and `default`
When invoked through omp
Then the response SHALL contain "pong" and exit 0.

#### Scenario: lightweight model works

Given `shopapikey/fable-5` is assigned to `smol` and `commit`
When invoked through omp
Then the response SHALL contain "pong" and exit 0, subject to provider-side rate limits.

#### Scenario: third-provider task model works

Given `giaoduc/Advance` is assigned to `task`
When invoked through omp
Then the response SHALL contain "pong" and exit 0.

#### Scenario: no-flag default resolves to native Cockpit

When a fresh login zsh shell runs `omp --no-session -p "reply only: pong"` without `--model`
Then the default role SHALL resolve to native Cockpit `gpt-5.6-luna:max` and return `pong` with exit 0.

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

### Requirement: No modification to external systems

This change SHALL NOT modify Hermes, Claude Code, Cockpit Tools.app,
Docker Compose, adapter-status.sh, start-adapter.sh, the launchd plist,
Claude profiles, agent-core, tdt-core, or any Python agent configuration.

#### Scenario: external files unchanged

Given the change is applied
When the adapter docker-compose.yml, `~/.claude/profiles/*`, `~/.hermes/config.yaml`,
and adapter-status.sh are compared to their pre-change state
Then all SHALL be byte-for-byte identical.
