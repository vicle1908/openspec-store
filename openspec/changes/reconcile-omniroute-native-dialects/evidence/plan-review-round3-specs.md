# Independent plan review — Round 3, specs/protocols (sub-fffaa2c8)

Reviewer ended without delivering a parent reply (recovered from child transcript by the parent).
Scope: 4 spec deltas, design.md consumer matrix, overlay-contract.json, disposition matrix,
round-2 repair verification, protocol bindings, thinking controls, credential handling, defaults.

## VERDICT: PASS with 3 MINOR findings (all repaired immediately by the parent)

## Findings + repairs

1. **MINOR — Claude-Fable spec internal contradiction.** Requirement prose said PM provider
   uses Messages "at the host-root base URL" while its own scenario + second requirement pin
   `http://localhost:20128/v1` (client appends `/messages`). **Repaired:** prose now states the
   Claude-Fable client-specific base URL `http://localhost:20128/v1` with the explicit effective
   request `POST http://localhost:20128/v1/messages`. Strict validation still passes.

2. **MINOR — codex protected path naming (round-2 finding 3 repair had targeted a wrong
   entry).** The real codex overlay target is `~/.Claude-Fable`; its
   protected_baseline_paths still carried `~/.Claude-Fable:providers` (live key is
   `model_providers`). **Repaired:** path now `~/.Claude-Fable:model_providers`.

3. **MINOR — pi merge_key/template key alignment.** After the round-2 rename, the overlay
   merge_key must reference exactly the template's provider keys. **Repaired/verified:**
   merge_key keys == template keys exactly (`{omniroute-Claude-Fable→PM Messages, omniroute-responses→SH Responses}`),
   equality checked programmatically.

## Verified-consistent (no action)

- All 11 overlay entries match the design consumer matrix and disposition matrix (incl. Claude Code
  excluded = owned by archived change; copilot env-only = no file entry; cline SH-chat-only = FBC-5).
- Codex profile mechanism proven by the retained 3-arm probe (`--profile omniroute` rc=0, negative
  controls rc=1, value-blind).
- Thinking controls per dialect correct across all templates (Claude-Fable budget/thinking for PM;
  Responses reasoningEffort high for SH; fallback thinking subsets justified as non-native).
- omp/Claude-Fable fallback providers use root baseUrl + exact model IDs per their specs.
- Effective-request contracts satisfied per client path-append semantics (@ai-sdk, Claude-Fable,
  droid, goose, omp, pi, prime).
- Credentials: env references everywhere; keyless-loopback placeholders documented and probe-proven.

## Reviewer caveat

The round-3 reviewer's own notes contain a display-layer name-mangling artifact around two
hyphenated identifiers; the parent re-verified every one of its claims programmatically against
the raw files before applying repairs (all three confirmed real, then fixed).
