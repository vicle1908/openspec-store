# Preflight Review: optimize-agentmemory-runtime-config

**Reviewer:** Independent worker (read-only, no files modified)
**Date:** 2026-08-21
**Decision:** **needs adjustment** — 3 mandatory fixes, 2 advisory notes

---

## Summary

The change is well-structured, correctly scoped to a single `.env` file, and has clear acceptance criteria. However, the actual live configuration diverges from what the proposal assumes in two material ways, and the documentation of the credential boundary is incomplete. These must be corrected before implementation proceeds.

---

## Mandatory Fixes

### 1. AGENTMEMORY_REFLECT: current value is `true`, not implied `false`

**Current live value:** `AGENTMEMORY_REFLECT=true` (line 14 of `.env`)

**What the change says:** Task 2.1 sets `AGENTMEMORY_REFLECT=false`. The design section 3 says "Leave... LESSON_DECAY_ENABLED... enabled as currently tested" but does not mention reflect at all. The proposal goals section says "preserve the validated... lesson decay."

**Problem:** This is a behavioral regression that is not called out as a decision. The reflect feature is currently enabled and in use. Setting it to `false` disables a working feature. If this is intentional, it must be an explicit decision with rationale in `design.md` §Decisions. If it is unintentional, the task must preserve `AGENTMEMORY_REFLECT=true`.

**Impact:** Disabling reflect silently changes the post-change behavior matrix. Task 3.1 reruns the full feature matrix but the baseline (task 1.3) does not explicitly capture reflect state, so the regression would be invisible.

### 2. Missing 5 environment variables from the allowlist scope

**Current `.env` has 24 active lines.** The change only addresses 12 of them by name:

| Variable | Current Value | In Change? |
|---|---|---|
| `AGENTMEMORY_AGENT_SCOPE` | `shared` | **No** |
| `AGENTMEMORY_VIEWER_PORT` | `11533` | **No** |
| `OPENAI_BASE_URL` | (external endpoint) | **No** |
| `OPENAI_EMBEDDING_BASE_URL` | `http://localhost:11434/v1` | **No** |
| `OPENAI_EMBEDDING_API_KEY` | `ollama` | **No** |

Task 2.1 says "Update only the allowlisted AgentMemory environment entries" but does not define what the full allowlist is, nor does it explicitly declare these 5 as preserved-as-is. Task 2.3 says "verify the effective provider/model/embedding route through non-secret diagnostics" — this implicitly covers them, but the task list does not capture their pre-change fingerprints.

**Fix:** Add these 5 variables to task 1.2's baseline capture and task 2.1's explicit "preserve unchanged" list, or explicitly note they are out of scope with a rationale.

### 3. Credential boundary documentation is incomplete

**The change documents:** "no credential value appears in the artifact" (task 1.2) and "verify the redacted diff contains no credential" (task 2.1).

**What is missing:**
- The `.env` has **two separate credential lines** (`OPENAI_API_KEY` and `OPENAI_EMBEDDING_API_KEY`) with **different values** (external API token vs. local ollama). The change never documents this two-key boundary.
- The `OPENAI_BASE_URL` and `OPENAI_EMBEDDING_BASE_URL` are credential-adjacent (they define the provider routing topology). The change mentions preserving "the default shopapikey/fable-5 and local embedding configuration" but does not document that these are two distinct provider routes on different hosts.
- The `.env.bak` file (2.8K) contains a prior configuration snapshot. The change does not address whether `.bak` creation/rotation is part of the maintenance transaction.

**Fix:** Add to task 1.2: "Record the two-key provider boundary: LLM key → external endpoint, embedding key → localhost ollama. Record that `.bak` is a pre-existing snapshot and confirm it will not be overwritten by the restart."

---

## Advisory Notes (non-blocking)

### A. iii-config.yaml has a third timeout not in scope

`iii-config.yaml` has `default_timeout: 180000` (3 minutes). The change only modifies `.env` timeout values (300s → 90s). If the iii engine enforces its own 180s timeout on LLM calls, a 90s `.env` timeout is subsumed. If the iii timeout is the binding constraint, the `.env` change is cosmetic. Task 3.2 should verify which timeout is actually binding.

### B. Doctor vs. status graph evidence discrepancy

`agentmemory doctor` reports "Graph is empty" (✗). `agentmemory status` reports "1485 nodes, 1390 edges." These may use different definitions (unprocessed observations vs. stored graph). Task 3.1's acceptance matrix should clarify which metric it requires and whether this discrepancy is pre-existing.

### C. AGENTMEMORY_SLOTS=memory semantic gap is correctly identified

The change correctly notes that `AGENTMEMORY_SLOTS=memory` is not the same as `AGENTMEMORY_SLOTS=true` and proposes `false`. This is sound. The follow-up to enable pinned slots should reference the specific write-path behavior difference.

---

## Evidence Captured

- `.env`: 24 active non-comment lines, 45 total lines
- AgentMemory version: 0.9.29
- Launchd service: running (watchdog + server processes active)
- `agentmemory doctor`: 7/9 passing (compression and graph populated failing — pre-existing)
- `agentmemory status`: healthy, 1076 sessions, 15560 observations, 1485 graph nodes
- `iii-config.yaml`: 6 worker definitions, 180000ms default timeout, local kv adapters
- No delta-spec files present (consistent with `skip_specs: true`)

---

## Decision: **needs adjustment**

Three mandatory fixes before implementation:
1. Resolve the `AGENTMEMORY_REFLECT` value discrepancy (currently `true`, change sets to `false` without decision rationale).
2. Add the 5 unaddressed `.env` variables to the baseline capture and explicit-preserve list.
3. Document the two-key provider boundary and `.bak` file handling.

No blockers found in scope isolation, credential safety of the actual edit, or acceptance matrix completeness (beyond the reflect gap).
