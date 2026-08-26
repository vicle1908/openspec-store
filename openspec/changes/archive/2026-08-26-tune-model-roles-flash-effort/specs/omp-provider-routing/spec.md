# omp-provider-routing Delta

## ADDED Requirements

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

## MODIFIED Requirements

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
