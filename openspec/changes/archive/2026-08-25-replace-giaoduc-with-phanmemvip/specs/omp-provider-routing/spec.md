# omp-provider-routing Delta

## REMOVED Requirements

### Requirement: Provider declaration

**Reason**: The giaoduc provider block is retired and replaced by phanmemvip.
The requirement is rebuilt below with the provider set changed to shopapikey,
phanmemvip, and cockpit; the "shopapikey and giaoduc unchanged" scenario is
intentionally dropped because giaoduc no longer exists.

**Migration**: The rebuilt requirement is re-added in this same delta under
ADDED Requirements with a phanmemvip Responses-endpoint scenario replacing the
giaoduc scenario.


### Requirement: No modification to external systems

**Reason**: This requirement was a change-scoped constraint of the original
OMP provider-onboarding change, which deliberately touched only
`~/.omp/agent/`. The giaoduc → phanmemvip migration intentionally spans
Hermes, Claude Code profiles/launchers, goose, grok, pi, prime-agent, and
tdt-core surfaces, so a blanket "no external modification" rule contradicts
the migration's purpose.

**Migration**: Cross-surface consistency for this migration is governed by the
`replace-giaoduc-with-phanmemvip` change's tasks and by the updated
provider-routing, MoA, credential-registry, and Claude profile/routing
requirements. Future OMP-only changes MAY reintroduce a similarly scoped
constraint in their own change artifacts.

## ADDED Requirements

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

## MODIFIED Requirements

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
(`fable-5`, `gpt-5.6-sol`, `gpt-5.6-luna`) confirmed by response metadata.
The `[1m]` suffixed variants SHALL NOT be used until isolated-profile
testing proves omp parses bracket notation correctly.

#### Scenario: model ID in response

Given `shopapikey/fable-5` is selected
When a prompt is sent
Then the response `model` field SHALL contain `fable-5`.

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

Given `shopapikey/fable-5` is assigned to `smol` and `commit`
When invoked through omp
Then the response SHALL contain "pong" and exit 0, subject to provider-side rate limits.

#### Scenario: third-provider task model works

Given `phanmemvip/gpt-5.6-sol:xhigh` is assigned to `task`
When invoked through omp
Then the response SHALL contain "pong" and exit 0.

#### Scenario: no-flag default resolves to native Cockpit

When a fresh login zsh shell runs `omp --no-session -p "reply only: pong"` without `--model`
Then the default role SHALL resolve to native Cockpit `gpt-5.6-luna:max` and return `pong` with exit 0.

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
Then each role selector, including `phanmemvip/gpt-5.6-sol:xhigh`, SHALL return "pong" with exit code 0.
