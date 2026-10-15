# Proposal

## Why
OmniRoute provisions a native top-level routing combo named `gemini-4-argon` backed by the Nexus provider. OMP's default role was previously pointing directly to `omniroute/nx/gemini-4-argon:high`, bypassing OmniRoute's combo pooling layer and deviating from the ecosystem convention established by `omniroute/gemini-3.8-flash-high`. Standardizing on the `omniroute/gemini-4-argon` combo provides clean gateway-level pooling while maintaining seamless fail-closed fallback.

## What Changes
- Register top-level combo model `gemini-4-argon` under `providers.omniroute.models` in `~/.omp/agent/models.yml`.
- Reallocate `modelRoles.default` in `~/.omp/agent/config.yml` to `omniroute/gemini-4-argon:high`.
- Configure explicit fallback chains for `omniroute/gemini-4-argon` in `retry.fallbackChains` pointing to `omniroute/gemini-3.8-flash-high` and `google-antigravity/gemini-3.8-flash:high`.
- Preserve existing direct selectors (`omniroute/nx/deepseek-v4.1-flash`, `omniroute/nx/gemini-4-argon`, `omniroute/nx/deepseek-v4-pro`) and their respective fallback rules.

## Capabilities

### New Capabilities
None.

### Modified Capabilities
- `omp-provider-routing`: Extends OmniRoute model declarations and default role allocation to support the native `gemini-4-argon` combo route.

## Impact
- **OMP Runtime**: Default turns now invoke `omniroute/gemini-4-argon:high` through OmniRoute's combo engine.
- **Resilience**: If the combo target encounters rate limits or upstream relay errors, OMP automatically fails over to `omniroute/gemini-3.8-flash-high`.
