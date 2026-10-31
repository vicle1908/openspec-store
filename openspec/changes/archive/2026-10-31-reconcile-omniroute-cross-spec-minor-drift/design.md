# Design

## Context

Following the cross-surface consistency audit across OpenSpec changes, the 6 OmniRoute main specifications, wiki/docs, helper scripts, managed/workspace skills, and memory files:
1. `omniroute-agent-cli-routing/spec.md:541` retained an older `context_cache_protection: true` clause in `Scenario: OmniRoute combo muse-spark-1.3 intercepts bare model requests and preserves namespace tools`, while lines `706,710` and live SQLite `combos` configure `context_cache_protection: false`.
2. `omniroute-agent-skills/spec.md:76` retained `22 omni-* REST endpoints` from v3.8.50 before `omni-context-rtk` brought the `omni-*` REST skill count to `23` (`spec.md:204`).
3. `claude-code-omniroute-pm-routing/spec.md:13,18,59,69-71` still described the pre-cutover `pm/Claude-Fable` default in `~/.claude/profiles/omniroute-pm.json` and had a bodyless trailing `#### Scenario: One launcher per provider surface` header on line `71`, whereas live `~/.claude/profiles/omniroute-pm.json` configures `"model": "gemini-3.8-flash-high"`, `"modelOverrides": {"gemini-3.8-flash-high": "gemini-3.8-flash-high"}`, and `modelPicker.options` for `gemini-3.8-flash-high` and `gemini-4-argon*`.

## Goals / Non-Goals

- **Goals**:
  - Eliminate all remaining cross-spec contradictions across the 6 OmniRoute specifications (`omniroute-runtime-customization`, `omniroute-compression-and-routing`, `omniroute-agent-cli-routing`, `omniroute-closure-integrity`, `omniroute-agent-skills`, `claude-code-omniroute-pm-routing`).
  - Synchronize managed skills (`~/.omp/agent/managed-skills/`), user-level custom skill blocks (`~/.agents/skills/`), wiki pages (`wiki/entities/*`, `wiki/concepts/*`, `wiki/index.md`), operational docs (`docs/omniroute-agent-skills.md`), and `memory://root/*`.
- **Non-Goals**:
  - Mutating live OmniRoute container or SQLite state (already verified aligned).

## Decisions

- **Decision 1**: Reconcile `omniroute-agent-cli-routing`, `omniroute-agent-skills`, and `claude-code-omniroute-pm-routing` via `## MODIFIED Requirements` preserving exact `### Requirement:` and `#### Scenario:` headers while keeping all requirement bodies `<500` characters (`299`–`493` chars).
