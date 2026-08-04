# Plan Review: harden-ci-supply-chain

**Reviewed:** 2026-08-04
**Providers:** Hermes (local), Claude Code (security), Codex (quality), Antigravity (architecture), fable-5/fable-5 (product scope)
**Frozen target:** `origin/main` at `abdc7c12369bbc6b2ff3f10267793912832457ca`

## Verdict: FAIL — plan corrections required before implementation

---

## Provider Execution Evidence

| Provider | Executable | Version | Exit | Verdict |
|---|---|---|---|---|
| Hermes | local analysis | n/a | n/a | FAIL |
| Claude Code | `/opt/homebrew/bin/claude` | 2.1.220 | 0 | PARTIAL |
| Codex | `/opt/homebrew/bin/codex` | 0.146.0 | pending | PARTIAL |
| Antigravity | `/opt/homebrew/bin/agy` | 1.1.10 | 0 | APPROVE_WITH_CORRECTIONS |
| fable-5/fable-5 | `/opt/homebrew/bin/fable-5` | 0.31.1 | 0 | BLOCK |

---

## Alignment Summary

| Edge | Status | Provider | Evidence |
|---|---|---|---|
| Spec ↔ Code | PARTIAL | Hermes | Scope matches workflows but Scorecard/go-module assumptions conflict with repo facts |
| Code ↔ Docs | FAIL | Codex | No docs tasks; retention rationale missing |
| Docs ↔ Skills | FAIL | Antigravity | github-actions-ci skill has incorrect SHA guidance; no Scorecard/Gitleaks procedures |
| Skills ↔ Specs | PARTIAL | fable-5 | Config-only skip correct but workflow procedure changes not propagated |
| Spec ↔ Docs | FAIL | fable-5 | No retention policy rationale; no security policy docs |
| Code ↔ Skills | PARTIAL | Antigravity | Gitleaks Action conflicts with existing Dockerized convention |
| Spec ↔ Tests | FAIL | Hermes | No pin-policy negative tests; no Scorecard compatibility probe; no module verification criteria |
| Code ↔ Tests | UNKNOWN | Codex | No implementation yet |

## Status Counts
- PASS: 0
- PARTIAL: 4
- FAIL: 4
- UNKNOWN: 1
- N/A: 0
- NOT_REVIEWED: 0

---

## Provider Findings

### Hermes (Spec Compliance)

**Assigned Edges:** Spec ↔ Code, Spec ↔ Docs, Spec ↔ Tests

1. **Scorecard Action not viable as designed.** Repository is private, GitHub Advanced Security is not enabled. Official Scorecard docs require GHAS for private repos. The proposed SARIF publishing workflow is not executable.
2. **Blanket artifact retention reduction is not evidence-driven.** Release evidence retains 365 days, deployment/image evidence 90 days. No compliance/audit justification for blanket 30-day cap.
3. **`go mod verify` underspecified.** No root `go.mod`. Must enumerate 17 separate modules and fail if any expected module is missing.
4. **SHA resolution needs exact release provenance.** Must pin to commit behind exact release tag, dereference annotated tags. Major tags are mutable.

### Claude Code (Security)

**Assigned Lens:** Security across all edges

**Primary verdict:** PARTIAL — addresses real supply-chain vectors (CVE-2025-30066, mutable-tag hijacking) but contains implementation-unsafe gaps that would break CI on merge or silently fail to deliver security guarantees.

**Supplemental verdict:** PARTIAL — sound in intent but gaps in licensing, baseline strategy, git history semantics, fail-open/closed behavior, and task specificity.

1. Scorecard Action deployment path unsupported for current repo (private, no GHAS).
2. Gitleaks license/baseline undefined — personal account (no key) must be confirmed. No `.gitleaksignore` or baseline found.
3. `actionlint` validates syntax but not immutable references — pin-policy gate needed.
4. Scorecard publishing imposes workflow restrictions (approved action list, no top-level env, no containers).

### Codex (Quality & Tests)

**Assigned Edges:** Spec ↔ Tests, Code ↔ Tests, Code ↔ Docs

1. Missing docs/skills update tasks for workflow-structural change.
2. Retention policy has no rollback/compliance rationale.
3. Dependabot cooldown absent; automerge should be prohibited for action updates.
4. `go mod verify` must enumerate all 17 module roots.

### Antigravity (Architecture)

**Assigned Edges:** Code ↔ Skills, Docs ↔ Skills

**Verdict:** APPROVE_WITH_CORRECTIONS

1. Scorecard private-repo feasibility must be confirmed first.
2. Gitleaks needs baseline analysis, licensing confirmation, scan range/checkout-depth policy.
3. Pin enforcement needs own CI gate beyond actionlint.
4. Rollout phased and independently reversible: pin → Scorecard baseline → Gitleaks baseline → enforce.

### fable-5/fable-5 (Product Scope)

**Assigned Edges:** Skills ↔ Specs, scope check

**Verdict:** BLOCK

1. Replacing 90/365-day retention with 30 days removes required evidence.
2. Scorecard enforcement inconsistent with triggers/required checks — cannot gate before baseline.
3. Gitleaks assumptions unsupported — licensing, history depth, allowlists undefined.

---

## Required Corrections Before Implementation

1. **Scorecard decision gate** — prerequisite check: enable GHAS, CLI report-only, or skip.
2. **Retention artifact-aware** — keep existing tiers; new artifacts get 30 days with rationale.
3. **SHA pinning complete and deterministic** — pin to release commit, add enforcement CI gate.
4. **`go mod verify` enumerate modules** — define 17-module list, fail if missing.
5. **Gitleaks staged baseline** — licensing, scan range, warn-only first, then enforce.
6. **Dependabot hardened** — cooldown, no automerge for action updates.
7. **Docs/skills/runbooks** — update skills, runbook, rollback procedures, success metrics.
8. **Phased implementation** — pin → Gitleaks baseline → Scorecard baseline → enforce.

---

*Review completed: 2026-08-04*
