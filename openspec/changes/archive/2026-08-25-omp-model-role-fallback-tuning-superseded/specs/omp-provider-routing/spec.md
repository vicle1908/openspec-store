# omp-provider-routing Specification (Delta)

## MODIFIED Requirements

### Requirement: Capability-based role allocation

omp `modelRoles` in `config.yml` SHALL be assigned based on observed
omp catalog capabilities, not upstream provider marketing claims.
Every selector MUST reference a `provider/model` id present in the
effective catalog at apply time. The thinking-level suffixes `:high`
and `:max` SHALL only be used for providers where they were validated
through omp smoke testing. Per the workstation's high-effort direction,
every `google-antigravity/gemini-3.7-flash` selector assigned to a role
or listed in a fallback chain SHALL carry an explicit `:high` suffix.

The role bindings SHALL be:

| role | selector |
| --- | --- |
| `default` | `openrouter/stealth/ox-alpha:max` |
| `slow` | `cockpit/gpt-5.6-luna:max` |
| `plan` | `cockpit/gpt-5.6-sol:max` |
| `task` | `giaoduc/Advance:xhigh` |
| `advisor` | `cockpit/gpt-5.6-sol:xhigh` |
| `smol` | `google-antigravity/gemini-3.7-flash:high` |
| `tiny` | `google-antigravity/gemini-3.7-flash:high` |
| `commit` | `shopapikey/fable-5:low` |
| `vision` | `google-antigravity/gemini-3.7-flash:high` |

#### Scenario: cheap roles bound to antigravity flash at high effort
- **WHEN** the config is parsed
- **THEN** `smol`, `tiny`, and `vision` SHALL each resolve to `google-antigravity/gemini-3.7-flash:high`

#### Scenario: heavy roles keep proven assignments
- **WHEN** the config is parsed
- **THEN** `slow` SHALL resolve to `cockpit/gpt-5.6-luna:max`, `plan` to `cockpit/gpt-5.6-sol:max`, `advisor` to `cockpit/gpt-5.6-sol:xhigh`, `default` to `openrouter/stealth/ox-alpha:max`, `task` to `giaoduc/Advance:xhigh`, and `commit` to `shopapikey/fable-5:low`

#### Scenario: thinking-level selectors work
- **WHEN** `cockpit/gpt-5.6-luna:high` is invoked through omp as a validated explicit selector
- **THEN** the response SHALL contain "pong" and exit 0

#### Scenario: max thinking level works
- **WHEN** `cockpit/gpt-5.6-luna:max` (assigned to `slow`), `cockpit/gpt-5.6-sol:max` (assigned to `plan`), and `openrouter/stealth/ox-alpha:max` (assigned to `default`) are invoked through omp
- **THEN** each response SHALL contain "pong" and exit 0

#### Scenario: commit model works at low effort
- **WHEN** `shopapikey/fable-5:low` assigned to `commit` is invoked through omp
- **THEN** the response SHALL contain "pong" and exit 0, subject to provider-side rate limits

#### Scenario: lightweight model works
- **WHEN** `google-antigravity/gemini-3.7-flash:high` assigned to `smol` and `shopapikey/fable-5:low` assigned to `commit` are invoked through omp
- **THEN** each response SHALL contain "pong" and exit 0, subject to provider-side rate limits

#### Scenario: antigravity flash roles work at high effort
- **WHEN** `google-antigravity/gemini-3.7-flash:high` assigned to `smol`, `tiny`, and `vision` is invoked through omp
- **THEN** the response SHALL contain "pong" and exit 0

#### Scenario: third-provider task model works
- **WHEN** `giaoduc/Advance:xhigh` assigned to `task` is invoked through omp
- **THEN** the response SHALL contain "pong" and exit 0

#### Scenario: no-flag default resolves to native Cockpit
- **WHEN** a fresh login zsh shell runs `omp --no-session -p "reply only: pong"` without `--model`
- **THEN** the default role SHALL resolve to `openrouter/stealth/ox-alpha:max` and return `pong` with exit 0

### Requirement: Existing omniroute preserved

The OmniRoute provider block in `models.yml` SHALL remain unchanged and
available in the `/model` picker. OmniRoute SHALL NOT be assigned to
any `modelRoles` entry in `config.yml`, and no `omniroute/*` selector
SHALL appear in any `retry.fallbackChains` list while omniroute is
designated unused.

#### Scenario: omniroute still works after change
- **WHEN** `omp models` is executed
- **THEN** `omniroute` models SHALL appear with identical metadata

#### Scenario: no role points at OmniRoute
- **WHEN** `config.yml` is inspected programmatically
- **THEN** no `modelRoles` value SHALL contain the string `omniroute`

#### Scenario: no fallback chain points at OmniRoute
- **WHEN** `retry.fallbackChains` is read
- **THEN** no list SHALL contain any selector beginning with `omniroute/`

### Requirement: Isolated profile validation

Both `models.yml` and `config.yml` SHALL be validated in an isolated
omp profile before live application. The test profile SHALL contain
both files. The `modelRoles` key SHALL NOT appear in `models.yml`.
The isolated smoke test SHALL cover all nine final role selectors
(`default`, `slow`, `plan`, `task`, `advisor`, `smol`, `tiny`,
`commit`, `vision`), including the new
`google-antigravity/gemini-3.7-flash:high` binding. All nine selectors
SHALL pass before any live mutation; a failing selector — including
`giaoduc/Advance:xhigh` rejecting with `401 invalid_api_key` — blocks
apply until its credential is repaired and the direct smoke test passes.

#### Scenario: isolated profile includes both files
- **WHEN** the isolated profile directory is inspected
- **THEN** both `models.yml` and `config.yml` SHALL be present

#### Scenario: isolated profile smoke test covers all nine role selectors
- **WHEN** `omp --profile <test> --no-session --model <selector> -p "reply only: pong"` is run for each of the nine role selectors
- **THEN** each SHALL return "pong" with exit code 0

#### Scenario: isolated profile smoke test
- **WHEN** `omp --profile <test> --no-session --model <selector> -p "reply only: pong"` is run
- **THEN** each of the nine role selectors SHALL return "pong" with exit code 0

## ADDED Requirements

### Requirement: Default fallback chain ordered by current success evidence

The inherited `default` chain SHALL place currently-succeeding providers
ahead of providers with unresolved credential failures. `giaoduc/Advance`
SHALL NOT be the first fallback while its API-key failure is unverified.

#### Scenario: default chain ordering
- **WHEN** the `default` fallback chain is read
- **THEN** it SHALL equal, in order: `cockpit/gpt-5.6-luna`, `shopapikey/fable-5`, `giaoduc/Advance`, `google-antigravity/gemini-3.7-flash:high`

### Requirement: Model-keyed chains cover the cockpit pair

Each active cockpit selector SHALL have a model-selector-keyed chain that
first tries the sibling cockpit model (covering single-model failures) and
then a non-cockpit provider (covering provider-level outages).

#### Scenario: luna fails
- **WHEN** `cockpit/gpt-5.6-luna` requests fail through the retry budget
- **THEN** the runtime SHALL next attempt `cockpit/gpt-5.6-sol`, then `shopapikey/fable-5`

#### Scenario: sol fails
- **WHEN** `cockpit/gpt-5.6-sol` requests fail through the retry budget
- **THEN** the runtime SHALL next attempt `cockpit/gpt-5.6-luna`, then `shopapikey/fable-5`

### Requirement: Antigravity wildcard coverage

A `google-antigravity/*` wildcard chain key SHALL exist so every
antigravity model — in any role — falls back along the documented
provider-swap pattern before leaving the family's substitutes.

#### Scenario: flash fails on a cheap role
- **WHEN** `google-antigravity/gemini-3.7-flash:high` fails while serving `smol`
- **THEN** the runtime SHALL attempt the `google-antigravity/*` chain: `google/*` (id-swap, skipped if absent), then `google-vertex/*` (id-swap), then `shopapikey/fable-5`

### Requirement: Giaoduc failure does not strand the task role

Because `task` binds directly to `giaoduc/Advance`, a model-keyed
`giaoduc/Advance` chain SHALL route runtime failures to proven providers
without touching omniroute. This requirement defines fallback recovery
behavior only; its scenario is a resilience check and SHALL NOT
substitute for the primary selector's acceptance test in the isolated
profile smoke test, nor permit marking that acceptance test complete
while the direct selector fails.

#### Scenario: task-role giaoduc call returns 401 at runtime
- **WHEN** `giaoduc/Advance` rejects with `401 invalid_api_key` during subagent work after a previously passing acceptance test
- **THEN** the runtime SHALL next attempt `shopapikey/fable-5`, then `cockpit/gpt-5.6-sol`
