# Proposal: 5-Provider Review Gates (Alignment Focus) — REVISED

## Why

The workspace has grown to 333 specs, 16 code repositories, and 50+ Hermes skills. Alignment drifts silently between specs, code, documentation, and skills. Single-agent review catches some drift. Multi-provider consensus catches what individual agents miss.

However, the initial proposal had critical issues identified by all 5 providers:
- `openspec show --json` is not a complete artifact reader
- No trust boundary or least-privilege execution model
- Tests absent from the formal alignment model
- Architecture lens changes between gates
- "Product alignment" not operationally defined
- Six-edge matrix contradicts actual review workflows

This revision addresses all critical findings.

## What Changes

### Revised Architecture

1. **Scope Definition**: Add `review-scope.yaml` per change to define:
   - Affected repositories and paths
   - Base/head revisions
   - Applicable spec IDs
   - Documentation roots
   - Relevant skills
   - Excluded secret/generated paths

2. **Trust Boundary**: Reviewers are read-only with:
   - No write tools, no unrestricted shell
   - No unrelated filesystem access
   - No nested agents, no network access except provider API
   - Sanitized, allowlisted context bundle

3. **Test Alignment**: Add first-class edges:
   - `Spec ↔ Tests`: Requirements → test coverage
   - `Code ↔ Tests`: Implementation → test execution evidence

4. **Consistent Lens**: Each provider has ONE consistent lens across both gates:
   - Hermes: Spec compliance
   - Claude Code: Security
   - Codex: Quality & tests
   - Antigravity: Architecture
   - fable-5: Product scope

5. **Evidence-Based Review**: Collect actual evidence:
   - `uv run pytest --cov` for Python repos
   - `make check-coverage` for Go repos
   - `openspec validate --strict` for specs

### Revised Alignment Matrix

| Edge | Plan Review | Code Review | Evidence Required |
|---|---|---|---|
| Spec ↔ Code | Feasibility check | Implementation check | Requirement → code mapping |
| Code ↔ Docs | Pattern check | Documentation check | API → docs mapping |
| Docs ↔ Skills | Command check | Skill update check | Command → skill mapping |
| Skills ↔ Specs | Workflow check | Workflow alignment | Skill → requirement mapping |
| Spec ↔ Docs | Requirement check | Documentation check | Requirement → docs mapping |
| Code ↔ Skills | API check | Skill compatibility | API → skill mapping |
| Spec ↔ Tests | Coverage check | Test execution | Requirement → test mapping |
| Code ↔ Tests | Coverage check | Test execution | Code → test mapping |

### Revised Provider Assignments

| Provider | Lens | Plan Review | Code Review |
|---|---|---|---|
| Hermes | Spec compliance | Spec ↔ Code, Spec ↔ Docs | Spec ↔ Code, Spec ↔ Tests |
| Claude Code | Security | Security alignment | Security audit |
| Codex | Quality & tests | Spec ↔ Tests, Code ↔ Tests | Code ↔ Tests, Code ↔ Docs |
| Antigravity | Architecture | Code ↔ Skills, Docs ↔ Skills | Code ↔ Skills, Architecture adherence |
| fable-5 | Product scope | Skills ↔ Specs, scope check | Skills ↔ Specs, completeness |

### Revised Status Semantics

| Status | Meaning |
|---|---|
| `PASS` | Evidence confirms alignment |
| `PARTIAL` | Some evidence, gaps remain |
| `FAIL` | Evidence shows misalignment |
| `N/A` | Edge not applicable to this change |
| `UNKNOWN` | Could not verify |
| `NOT_REVIEWED` | Provider did not cover this edge |

### Revised Success Criteria

1. **Alignment drift reduced**: Track alignment issues per change
2. **Evidence collected**: Each edge has supporting evidence
3. **No false positives**: Review finds real issues, not noise
4. **Adoption**: Skills used in at least 50% of high-stakes changes

## Scope

**In scope:**
- Revised `openspec-plan-review` skill with trust boundaries and evidence collection
- Revised `openspec-code-review` skill with test alignment
- `review-scope.yaml` template for change-specific scope
- Alignment matrix with 8 edges and status semantics
- Evidence collection integration (pytest, make, openspec validate)

**Out of scope:**
- Automated alignment fixes (manual intervention required)
- Custom schema changes
- Modifying OpenSpec CLI behavior
- Provider authentication setup

## Why Now (Revised)

The alignment-drift problem is real, but the initial proposal was solution-first. This revision:
1. Defines what we're measuring (8 alignment edges with status semantics)
2. Adds evidence collection (not just opinions)
3. Establishes trust boundaries (security review found critical gaps)
4. Sets success criteria (how we'll measure if it worked)

## Non-Goals (Revised)

- Replace `/opsx:verify` (it remains useful for quick single-agent checks)
- Enforce review on all changes (skills are optional, user-controlled)
- Create a custom schema (deferred to future change if needed)
- Implement automated CI/CD integration (manual invocation first)
- Auto-fix alignment issues (review reports, human decides)
- Review all 333 specs, 16 repos, and 50+ skills (scoped per change)
