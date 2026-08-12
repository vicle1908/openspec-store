## MODIFIED Requirements

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

### Requirement: Anthropic Messages wire protocol

Each provider's transport SHALL match its endpoint's actual protocol.

#### Scenario: protocol match

Given provider blocks in `models.yml`
When inspected programmatically
Then `shopapikey.api` SHALL be `anthropic-messages`
And `giaoduc.api` SHALL be `anthropic-messages`
And `cockpit.api` SHALL be `openai-responses`.

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

## ADDED Requirements

### Requirement: Capability-based role allocation

omp `modelRoles` in `config.yml` SHALL be assigned based on observed
omp catalog capabilities, not upstream provider marketing claims.
The thinking-level suffixes `:high` and `:max` SHALL only be used for
providers where they were validated through omp smoke testing.

#### Scenario: thinking-level selectors work

Given `cockpit/gpt-5.6-luna:high` is assigned to `default`
When invoked through omp
Then the response SHALL contain "pong" and exit 0.

#### Scenario: max thinking level works

Given `cockpit/gpt-5.6-luna:max` is assigned to `slow` and `plan`
When invoked through omp
Then the response SHALL contain "pong" and exit 0.

#### Scenario: lightweight model works

Given `shopapikey/fable-5` is assigned to `smol` and `commit`
When invoked through omp
Then the response SHALL contain "pong" and exit 0.

#### Scenario: third-provider task model works

Given `giaoduc/Advance` is assigned to `task`
When invoked through omp
Then the response SHALL contain "pong" and exit 0.

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
The current live cockpit endpoint SHALL be `http://localhost:8788`
(host port remapped from container port 8787 via Docker Compose).
After the change, no omp provider `baseUrl` SHALL reference either
adapter port (8787 or 8788).

#### Scenario: port 51006 responds

Given the preflight check
When a valid OpenAI Responses request is sent to `http://localhost:51006/v1/responses`
Then the response SHALL be HTTP 200 with a valid JSON body containing `model: gpt-5.6-luna`.

#### Scenario: current cockpit uses adapter port

Given the preflight check
When `models.yml` is inspected programmatically
Then `cockpit.baseUrl` SHALL be `http://localhost:8788`
And `cockpit.api` SHALL be `anthropic-messages`.

#### Scenario: no adapter port dependency after change

Given the proposed `models.yml`
When inspected programmatically
Then no provider `baseUrl` SHALL reference `localhost:8787` or `localhost:8788`.

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
