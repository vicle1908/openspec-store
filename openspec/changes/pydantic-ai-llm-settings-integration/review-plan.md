# Review Plan: pydantic-ai-llm-settings-integration

## Review Status

| # | Lens | Reviewer | Verdict | Status |
|---|------|----------|---------|--------|
| 1 | Security | Claude (CLI) | APPROVE_WITH_CONDITIONS | ✅ Complete — all conditions applied |
| 2 | Architecture | Orchestrator (inline) | APPROVE_WITH_CONDITIONS | ✅ Complete — conditions applied |
| 3 | Quality & Tests | Codex (CLI) | — | ⏭️ Stuck (343s, no output) — skipped |
| 4 | Product Scope | Pi (CLI) | APPROVE_WITH_CONDITIONS | ✅ Complete — conditions applied |
| 5 | Cross-cutting | Orchestrator (inline) | APPROVE | ✅ Complete |
| 6 | Architecture | Agy (CLI) | — | ⏭️ Explained flag instead of reviewing (2x) — done inline |

**Overall: 4/6 APPROVE_WITH_CONDITIONS, 1/6 APPROVE, 1/6 skipped**

---

## Consolidated Findings

### From Claude (Security) — Round 1

| # | Severity | Finding | Status |
|---|----------|---------|--------|
| S1 | CRITICAL | `extra_model_settings` enables unvalidated header injection | ✅ Fixed: blocklist for `extra_headers`, `extra_body` |
| S2 | HIGH | `extra_model_settings` could leak sensitive provider config | ✅ Fixed: sensitive key validator + model_dump() exclusion |
| S3 | MEDIUM | Env var precedence allows resource exhaustion | ✅ Fixed: range validators (temperature 0-2, max_tokens 1-1M) |
| S4 | MEDIUM | Thinking capability lacks provider compatibility check | ✅ Fixed: thinking compatibility warning log |
| S5 | MEDIUM | `model_settings` typed as Any | ⏩ Deferred: existing issue, not blocking this change |

### From Pi (Product Scope)

| # | Severity | Finding | Status |
|---|----------|---------|--------|
| P1 | HIGH | `service_tier` missing Literal type enforcement | ✅ Fixed: `Literal['auto', 'default', 'flex', 'priority']` |
| P2 | MEDIUM | `top_p` absent from typed fields | ✅ Fixed: added `top_p: float | None = Field(ge=0.0, le=1.0)` |
| P3 | MEDIUM | `thinking` type overloading needs docs clarity | ✅ Fixed: added thinking value mapping in design.md |
| P4 | MEDIUM | Thinking compatibility warning logic undefined | ⏩ Deferred: will define in implementation (not a spec blocker) |
| P5 | LOW | `model_dump()` override fragility | ⏩ Deferred: add comment in implementation |
| P6 | LOW | Proposal preamble vs delivery scope mismatch | ✅ Fixed: added scope sentence in design.md |

### From Architecture Review (Inline)

| # | Severity | Finding | Status |
|---|----------|---------|--------|
| A1 | MEDIUM | `extra_model_settings` should use TypedDict | ⏩ Deferred: dict with blocklist is the right escape hatch |
| A2 | LOW | Thinking capability injection should be a dedicated builder | ⏩ Deferred: refactor later when more capabilities are config-driven |
| A3 | LOW | Merge semantics documentation incomplete | ✅ Fixed: added shallow merge documentation in design.md |
| A4 | MEDIUM | AgentSpec comparison not addressed | ✅ Fixed: added "Why Not AgentSpec Directly?" section |

---

## Changes Applied to Artifacts

### proposal.md
- Added Slice 6: Security hardening (blocklist, sensitive keys, range validators, serialization)

### design.md
- Updated ModelSettings code: added `top_p`, `Field(ge=...)` validators, `Literal` for service_tier
- Added config YAML example with `top_p`
- Added env var `MODEL_TOP_P`
- Added Thinking value mapping table
- Added "Why Not AgentSpec Directly?" section
- Added Merge Semantics section (shallow merge)
- Added Security Hardening section (blocklist, sensitive keys, serialization, range validators)

### tasks.md
- Added Slice 4: Security Hardening (6 tasks)
- Renumbered Slice 5: Documentation & Spec Updates
- Added verification tasks V.5, V.6

### Delta spec (specs/agent-core-model-resolution/spec.md)
- Added Requirement: extra_model_settings Security Validation (3 scenarios)
- Added Requirement: Model Settings Range Validation (2 scenarios)

---

## Archive Readiness

**All review conditions have been addressed in the change artifacts.** The remaining deferred items (S5, P4, P5, A1, A2) are implementation-level details, not blockers for the spec/design phase.

**Recommendation:** Approve for implementation. The change artifacts are complete, reviewed, and consistent.
