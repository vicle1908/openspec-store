# Proposal: 5-Provider Review Gates (Alignment Focus)

## Intent

Enhance the OpenSpec workflow with multi-provider review gates that leverage 5 different AI coding agents (Hermes, Claude Code, Codex, Antigravity, fable-5) to ensure **alignment between specs, code, documentation, and skills** at two critical points: after planning and after implementation.

## Problem

**The Alignment Problem:**

In a multi-repo workspace with 333 specs, 16 code repositories, and 50+ Hermes skills, alignment drifts silently:

1. **Spec ↔ Code drift**: Specs describe behavior the code doesn't implement, or code implements behavior the specs don't describe
2. **Code ↔ Docs drift**: AGENTS.md describes patterns the code doesn't follow, or code uses patterns AGENTS.md doesn't document
3. **Docs ↔ Skills drift**: Skills reference commands or patterns that have changed, or new capabilities aren't documented in skills
4. **Skills ↔ Specs drift**: Skills implement workflows that don't match the spec requirements

Single-agent review catches some drift. Multi-provider consensus catches what individual agents miss because each provider has different strengths:

- **Hermers** sees the full workspace context
- **Claude Code** excels at finding security/auth misalignments
- **Codex** excels at finding performance/test gaps
- **Antigravity** excels at finding architectural inconsistencies
- **fable-5** excels at finding product/UX misalignments

## Scope

**In scope:**
- `openspec-plan-review` skill: 5-provider review of change artifacts for alignment
- `openspec-code-review` skill: 5-provider review of implementation for spec/code/docs/skills alignment
- Alignment check dimensions: spec-code, code-docs, docs-skills, skills-specs
- Structured output with alignment matrix
- Documentation for workflow integration

**Out of scope:**
- Automated alignment修复 (manual intervention required)
- Custom schema changes
- Modifying OpenSpec CLI behavior
- Provider authentication setup

## Why Now

The workspace has grown to:
- **333 specs** across Go microservices and TDT Python repos
- **16 code repositories** with independent lifecycles
- **50+ Hermes skills** with their own documentation
- **5 authenticated AI providers** ready for parallel review

Alignment drift is already happening. For example:
- `agent-core` AGENTS.md mentions "687 tests" but the spec might describe different test coverage
- Skills reference commands that may have changed
- Specs describe behavior that code may not implement

Multi-provider review catches these drifts before they compound.

## Non-Goals

- Replace `/opsx:verify` (it remains useful for quick single-agent checks)
- Enforce review on all changes (skills are optional, user-controlled)
- Create a custom schema (deferred to future change if needed)
- Implement automated CI/CD integration (manual invocation first)
- Auto-fix alignment issues (review reports, human decides)
