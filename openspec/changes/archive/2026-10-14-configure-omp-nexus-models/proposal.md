# Proposal

## Why
OmniRoute recently integrated the Nexus provider (`nx`), making new frontier models available including DeepSeek V4.1 Flash, DeepSeek V4 Pro, and Gemini 4 Argon. OMP currently routes all background and execution roles exclusively to `omniroute/gemini-3.8-flash-high` and `google-antigravity/gemini-3.8-flash:high`, lacking access to the new low-latency reasoning MoE capabilities (`deepseek-v4.1-flash`) and missing deterministic fallback routing for Nexus-backed endpoints.

## What Changes
- Register verified OmniRoute Nexus models (`nx/deepseek-v4.1-flash`, `nx/deepseek-v4-pro`, and provisional `nx/Gemini 4 Argon`) under `providers.omniroute.models` in `~/.omp/agent/models.yml`.
- Reallocate fast/lightweight role `commit` in `~/.omp/agent/config.yml` to `omniroute/nx/deepseek-v4.1-flash`, backed by `omniroute/gemini-3.8-flash-high`.
- Retain `omniroute/gemini-3.8-flash-high` as the primary driver for `default`, `task`, `plan`, `slow`, `advisor`, and background roles (`tiny`, `smol`, `vision`).
- Add `omniroute/nx/deepseek-v4-pro` to the secondary fallback chain for heavy reasoning roles.
- Establish explicit fallback chains in `retry.fallbackChains` for `omniroute/nx/deepseek-v4.1-flash` and `omniroute/nx/Gemini 4 Argon` pointing to `omniroute/gemini-3.8-flash-high` and `google-antigravity/gemini-3.8-flash:high`.
- Keep `nx/Gemini 4 Argon` staged in catalog for manual verification while excluding it from automatic roles until upstream relay parameter handling stabilizes.
- Preserve byte-for-byte all non-OmniRoute provider blocks (`shopapikey`, `phanmemvip`, `cockpit`, `omniroute-anthropic`, `omniroute-chat`) and existing credentials.

## Capabilities

### New Capabilities
None.

### Modified Capabilities
- `omp-provider-routing`: Defines OMP model catalog registration, wire protocol, role assignment, and fallback chains for OmniRoute Nexus provider models.

## Impact
- **OMP Configuration**: Changes affect `~/.omp/agent/models.yml` and `~/.omp/agent/config.yml`.
- **Runtime Performance**: `commit` gains fast MoE reasoning tokens from DeepSeek V4.1 Flash (~6s per commit summary).
- **Resilience**: Explicit fallback chains prevent unmonitored failures; if Nexus upstream fails, calls automatically fall back to the proven Gemini 3.8 Flash combo.
- **Security & Secrets**: Uses existing `OMNIROUTE_API_KEY` environment reference; no raw credentials or database tokens are written to files.
