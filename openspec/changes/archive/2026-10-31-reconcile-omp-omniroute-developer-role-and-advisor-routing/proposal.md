# Proposal

## Why

End-to-end verification of `omp` v18.14.1 uncovered two protocol-translation bugs between OMP (`api: openai-responses`) and OmniRoute's `openai-to-gemini.ts` translator (`open-sse/translator/index.ts:566,639,719` and `openai-to-gemini.ts:457,696`) that drop `role: "developer"` system prompts and merge advisor `functionResponse` tool results with subsequent `user` messages. Setting `providers.omniroute.compat.supportsDeveloperRole: false` in `~/.omp/agent/models.yml` and routing `modelRoles.advisor` to `google-antigravity/gemini-3.8-flash:high` in `~/.omp/agent/config.yml` resolves both bugs.

### Non-Goals

- Modifying tracked source files in `/Users/androidteam/Omniroute` or `/opt/homebrew/Cellar/omp/`.
- Changing `modelRoles.default`, `modelRoles.smol`, `modelRoles.plan`, or `modelRoles.judge`.

## What Changes

- Set `providers.omniroute.compat` to `{ supportsReasoningEffort: true, supportsDeveloperRole: false }` in `/Users/androidteam/.omp/agent/models.yml` so OMP sends system prompts with `role: "system"` (which `openai-to-gemini.ts` maps to `systemInstruction`) while preserving `thinking: ["low", "medium", "high"]` on all 5 `omniroute/*gemini-4-argon*` models.
- Route `modelRoles.advisor` to `google-antigravity/gemini-3.8-flash:high` with `retry.fallbackChains.advisor: [omniroute/gemini-3.8-flash-high:high, google-antigravity/gemini-4-argon:high]` in `/Users/androidteam/.omp/agent/config.yml` so multi-turn advisor `advise` tool calls preserve native Gemini `thoughtSignature` and `functionResponse` turn boundaries.

## Capabilities

### New Capabilities
*(None)*

### Modified Capabilities
- `omp-provider-routing`: Update `providers.omniroute.compat.supportsDeveloperRole` to `false` and `modelRoles.advisor` to `google-antigravity/gemini-3.8-flash:high`.

## Impact

- **Ownership Boundaries**: `/Users/androidteam/.omp/agent/{models.yml,config.yml}`, `/Users/androidteam/Developer/platform/openspec-store/openspec/specs/omp-provider-routing/spec.md`, `/Users/androidteam/Developer/wiki/entities/omp.md`, and Notion page `40ac4b21-deb4-8159-b891-cb85a17a2d73`.
