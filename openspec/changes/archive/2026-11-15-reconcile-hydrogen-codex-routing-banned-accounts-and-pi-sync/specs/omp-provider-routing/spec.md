# Spec Delta

## MODIFIED Requirements

### Requirement: Default Role Allocation to Gemini 4 Argon Combo

In `~/.omp/agent/config.yml`, `modelRoles.default` SHALL be assigned to `omniroute/gemini-4-carbon`, `modelRoles.plan` to `google-antigravity/gemini-4-argon:high`, `modelRoles.advisor` to `google-antigravity/gemini-3.8-flash:high` (retaining native `google-antigravity` multi-turn `thoughtSignature`/`functionResponse` preservation across active Flash-entitled Pro OAuth accounts after pruning banned rows from `~/.omp/agent/agent.db`), `modelRoles.task`, `modelRoles.smol`, `modelRoles.vision`, and `modelRoles.slow` to `omniroute/gemini-4-hydrogen:high`, `modelRoles.commit` to `omniroute/gemini-4-hydrogen:low`, and `modelRoles.tiny` to `omniroute/gemini-4-hydrogen-low:low`.

#### Scenario: Default turn execution via combo
- **WHEN** OMP executes turns under `default`, `task`, `smol`, `vision`, `slow`, `commit`, `advisor`, or `tiny` role selection
- **THEN** `default` SHALL route to `omniroute/gemini-4-carbon`, `smol`/`vision`/`slow`/`task` to `omniroute/gemini-4-hydrogen:high`, `commit` to `omniroute/gemini-4-hydrogen:low`, `tiny` to `omniroute/gemini-4-hydrogen-low:low`, and `advisor` to `google-antigravity/gemini-3.8-flash:high`
- **AND** `~/.omp/agent/agent.db` (`auth_credentials` where `provider = 'google-antigravity'`) SHALL exclude all 8 banned OAuth accounts (`vicgnome19094`, `vicgnome19096`, `vicgnome19088`, `ghtkmobile`, `vicgnome19095`, `vicgnome19092`, `vicle1908`, `hongsonle19081952`), leaving the 5 active non-banned rows (`id IN (2, 6, 10, 14, 15)`)
- **AND** `retry.fallbackChains` SHALL preserve failover to `omniroute/gemini-3.8-flash-high:high` and `google-antigravity/gemini-3.8-flash:high` without unmonitored fallback errors

#### Scenario: Live config role alignment with specification
- **WHEN** `~/.omp/agent/config.yml` is inspected
- **THEN** `modelRoles.default` SHALL equal `'omniroute/gemini-4-carbon'`, `modelRoles.plan` SHALL equal `'google-antigravity/gemini-4-argon:high'`, `modelRoles.judge` SHALL equal `'typesafe/jev-1.14.0'`, `modelRoles.advisor` SHALL equal `'google-antigravity/gemini-3.8-flash:high'`, `modelRoles.task`/`smol`/`vision`/`slow` SHALL equal `'omniroute/gemini-4-hydrogen:high'`, `modelRoles.commit` SHALL equal `'omniroute/gemini-4-hydrogen:low'`, and `modelRoles.tiny` SHALL equal `'omniroute/gemini-4-hydrogen-low:low'`
- **AND** `retry.fallbackChains.advisor` SHALL equal `['omniroute/gemini-4-hydrogen:high', 'omniroute/gemini-3.8-flash-high:high']`
- **AND** `retry.fallbackChains.smol` SHALL equal `['google-antigravity/gemini-4-hydrogen-high:high', 'omniroute/gemini-3.8-flash-high:high', 'google-antigravity/gemini-3.8-flash:high']`
