# Design

## Context
OmniRoute manages a set of routing combos in its database, including `gemini-3.8-flash-high` and the newly provisioned `gemini-4-argon` (`id: f1cefc64-7662-4f0a-9234-84f70603cbe4`), which dispatches to `nx/gemini-4-argon` via the OpenAI Responses wire transport. Previously, OMP was configured to call `omniroute/nx/gemini-4-argon:high` directly. Transitioning `modelRoles.default` to the native combo identifier `omniroute/gemini-4-argon:high` aligns OMP with the gateway abstraction and enables gateway-managed account failover. See `proposal.md` for motivation.

## Goals / Non-Goals

**Goals:**
- Declare top-level model `gemini-4-argon` under `providers.omniroute.models` in `~/.omp/agent/models.yml`.
- Assign `modelRoles.default` in `~/.omp/agent/config.yml` to `omniroute/gemini-4-argon:high`.
- Define an explicit fallback chain for `omniroute/gemini-4-argon` in `retry.fallbackChains` mapping to `omniroute/gemini-3.8-flash-high` and `google-antigravity/gemini-3.8-flash:high`.

**Non-Goals:**
- Removing the direct `nx/gemini-4-argon` catalog entry; direct targeting is preserved for troubleshooting and pin-testing.
- Modifying role assignments for `commit` (`omniroute/nx/deepseek-v4.1-flash`) or task/plan roles (`omniroute/gemini-3.8-flash-high`).

## Decisions

### 1. Top-Level Combo Catalog Entry
- **Decision:** Declare `gemini-4-argon` directly under `omniroute.models` with identical thinking effort options (`[low, medium, high]`) and tool support.
- **Rationale:** OmniRoute advertises combos as top-level model IDs on its `/v1/models` and `/v1/responses` endpoints. Declaring the bare name allows OMP to form clean selectors (`omniroute/gemini-4-argon`) without namespace prefix collision.

### 2. Redundant Fallback Coverage
- **Decision:** Maintain fallback chains for both `omniroute/gemini-4-argon` and `omniroute/nx/*` in `config.yml`.
- **Rationale:** Guarantees fail-closed protection regardless of whether a prompt invokes the combo route or direct provider selector.

## Risks / Trade-offs

- **Upstream Relay Latency:** Gemini 4 Argon includes reasoning tokens that add ~10-12s TTFT. *Mitigation:* Explicit fallback chains immediately redirect failed or timed-out requests to `omniroute/gemini-3.8-flash-high`.
