## MODIFIED Requirements

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
`shopapikey/Claude-Fable:low`. `default` SHALL be bound to
`phanmemvip/gpt-5.6-sol:max`. All other roles (`slow`, `plan`, `task`, `advisor`) SHALL remain byte-unchanged by this change.

#### Scenario: thinking-level selectors work

Given `google-antigravity/gemini-3.7-flash:high` is a validated explicit selector assigned to `smol`, `tiny`, and `vision`
When invoked through omp
Then the response SHALL contain "pong" and exit 0.

#### Scenario: max thinking level works

Given `phanmemvip/gpt-5.6-sol:max` is assigned to `default`, `cockpit/gpt-5.6-luna:max` is assigned to `slow`, and `cockpit/gpt-5.6-sol:max` is assigned to `plan`
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

Given `default` is bound to `phanmemvip/gpt-5.6-sol:max`
When `omp --mode json --no-session -p "reply only: pong"` is run without `--model`
Then the default role SHALL resolve to `phanmemvip/gpt-5.6-sol:max`, return "pong" with exit 0, and emit no fallback events.
