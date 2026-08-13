## MODIFIED Requirements

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

#### Scenario: no-flag default resolves to Giaoduc

When a fresh login zsh shell runs `omp --no-session -p "reply only: pong"` without `--model`
Then the default role SHALL resolve to Giaoduc Advance and return `pong` with exit 0.
