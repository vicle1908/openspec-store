# hermes-runtime-efficiency Specification Delta

## ADDED Requirements

### Requirement: Hermes configuration enforces loop_caps, bounded delegation, and pruned OmniRoute model catalog

`~/.hermes/config.yaml` SHALL maintain explicit `tool_loop_guardrails.loop_caps` (`max_web_searches` and `max_subagents`), enforce the specification's bounded `delegation` limits (`max_concurrent_children: 3`, `max_spawn_depth: 2`, `max_iterations: 50`), and prune unreferenced auto-discovered diffusion/horde model entries (`aihorde/*`) from `providers.omniroute.models` so configuration parsing and prompt overhead remain bounded.

#### Scenario: Hermes config.yaml passes loop_caps, delegation, and catalog hygiene verification
- **WHEN** `~/.hermes/config.yaml` is inspected
- **THEN** `tool_loop_guardrails.loop_caps.max_web_searches` and `tool_loop_guardrails.loop_caps.max_subagents` SHALL be present with finite positive integers
- **AND** `delegation.max_concurrent_children` SHALL equal `3`, `delegation.max_spawn_depth` SHALL equal `2`, and `delegation.max_iterations` SHALL equal `50`
- **AND** `providers.omniroute.models` SHALL contain only active coding and reasoning selectors without `aihorde/*` catalog bloat
