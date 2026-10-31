# Design

## Context

See `proposal.md - Why`.

## Goals / Non-Goals

**Goals:**
- Prevent OmniRoute's `openai-to-gemini.ts` from dropping OMP system prompts by sending `role: "system"` (`supportsDeveloperRole: false`) while keeping `supportsReasoningEffort: true`.
- Prevent multi-turn advisor `advise` tool calls from merging `functionResponse` and `user` text into a single Gemini `user` turn by routing `modelRoles.advisor` to native `google-antigravity/gemini-3.8-flash:high`.

**Non-Goals:**
- Modifying `/Users/androidteam/Omniroute` source files.

## Decisions

1. **`providers.omniroute.compat: { supportsReasoningEffort: true, supportsDeveloperRole: false }`**:
   - In OmniRoute `open-sse/translator/index.ts`, `fromOpenAI` (`openaiToGemini`, line 639) executes before the second `normalizeRoles` pass (`developer -> system`, line 719). Because `openai-to-gemini.ts:457` checks `role === "system"` and ignores `role === "developer"`, any `openai-responses` request with `role: "developer"` loses its `systemInstruction`. Setting `supportsDeveloperRole: false` forces OMP's `L = u.role === "developer" ? e.reasoning && t.supportsDeveloperRole ? "developer" : "system" : u.role` check to emit `role: "system"`, preserving the full system prompt while `supportsReasoningEffort: true` retains `thinking: ["low", "medium", "high"]`.
2. **`modelRoles.advisor: google-antigravity/gemini-3.8-flash:high`**:
   - In OMP's advisor runtime, calling `advise` ends the advisor turn on a `toolResult` (`Delivered.`) without a trailing assistant message. On the next review turn, OMP appends a `user` message directly after `toolResult`. Native `google-antigravity` preserves Gemini `thoughtSignature` and `functionResponse` turn boundaries across multi-turn advisor reviews.

## Risks / Trade-offs

- **[Risk] Google Antigravity OAuth quota exhaustion on advisor** → **Mitigation**: `retry.fallbackChains.advisor` fails over to `omniroute/gemini-3.8-flash-high:high` and `google-antigravity/gemini-4-argon:high`.
