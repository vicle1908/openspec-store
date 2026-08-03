# Proposal: 5-Provider Review Gates

## Intent

Enhance the OpenSpec workflow with multi-provider review gates that leverage 5 different AI coding agents (Hermes, Claude Code, Codex, Antigravity, fable-5) to review changes at two critical points: after planning and after implementation.

## Problem

Single-agent review has blind spots. A security vulnerability might be missed by an architecture-focused reviewer. An edge case might slip past a performance-oriented check. Multi-provider consensus catches what individual agents miss.

OpenSpec's current workflow has `/opsx:verify` for post-implementation validation, but it's a single-agent check. Pre-implementation review is manual (human reads artifacts). Neither leverages the diversity of available AI providers.

## Scope

**In scope:**
- `openspec-plan-review` skill: 5-provider review of change artifacts (proposal, specs, design, tasks)
- `openspec-code-review` skill: 5-provider review of implementation code against specs
- Review prompt templates for each provider with specialized lenses
- Structured output format (`review-plan.md`, `review-code.md`)
- Documentation for workflow integration points

**Out of scope:**
- Custom schema changes (optional future enhancement)
- Modifying OpenSpec CLI behavior
- Provider authentication setup (assumed already configured)
- Automated review triggers (manual invocation initially)

## Why Now

The workspace has 5 authenticated AI providers available:
1. **Hermes** (fable-5 via shopapikey) - Host session, full context
2. **Claude Code** (fable-5 via shopapikey) - Strong at security analysis
3. **Codex CLI** (gpt-5.6-luna via cockpit) - Strong at code quality
4. **Antigravity** (fable-5-3.6-flash) - Google's code analysis
5. **fable-5** (fable-5 AI) - fable-5 reasoning capabilities

All providers have working Hermes skills and can run non-interactively. The infrastructure is ready; the integration is missing.

## Non-Goals

- Replace `/opsx:verify` (it remains useful for quick single-agent checks)
- Enforce review on all changes (skills are optional, user-controlled)
- Create a custom schema (deferred to future change if needed)
- Implement automated CI/CD integration (manual invocation first)
