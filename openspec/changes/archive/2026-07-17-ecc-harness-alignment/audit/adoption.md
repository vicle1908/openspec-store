# ECC v2.0 Adoption Decisions

Date: 2026-06-27
Baseline SHA: `ec92b528471df708c2384ebbcc82b390b60f535a`
Auditor: openspec-apply-change (agent session)
ECC version: 2.0.0

## Candidates Evaluated

### `orch-build-mvp`
- **Classification**: keep-optional
- **Rationale**: ECC's orchestrator for building MVPs pairs with our OpenSpec `propose`/`apply` workflow. TDT has no direct equivalent (OpenSpec provides structure but not orchestration). Not adopting as the primary MVP workflow — keeping as fallback.
- **Integration plan**:
  - Pairs with: OpenSpec `openspec-propose` skill, `openspec-apply-change` skill
  - Must not shadow: `openspec-propose` (TDT canonical)
  - How to invoke: Available on demand if user explicitly requests ECC orch; otherwise route to `openspec-propose`

### `orch-pipeline`
- **Classification**: keep-optional
- **Rationale**: General orchestration pipeline; TDT OpenSpec workflow is the canonical equivalent.
- **Integration plan**: Available on demand. Not adopted as primary.

### `hookify-rules`
- **Classification**: redundant-to-tdt-skill
- **Rationale**: We have `hookify@claude-plugins-official` already installed. ECC's `hookify-rules` is documentation surface, not a separate CLI.
- **Integration plan**:
  - Pairs with: existing `hookify` CLI plugin
  - Must not shadow: `hookify-list`, `hookify-configure` (plugin's own commands)
  - How to invoke: Not invoked as a skill — the underlying CLI is used directly via Bash

### `context-budget`
- **Classification**: keep-optional
- **Rationale**: ECC's context window management. TDT has agentmemory for session-level context, but no per-session budget enforcement. Useful as a safety net.
- **Integration plan**: Available on demand; not actively wired into TDT workflow.

### `strategic-compact`
- **Classification**: keep-optional
- **Rationale**: ECC's proactive compaction strategy. TDT has its own pre-compact hook but doesn't currently compact proactively.
- **Integration plan**: Could be wired in later if pre-compact becomes too aggressive. For now, keep-optional.

### `verification-loop`
- **Classification**: keep-optional
- **Rationale**: ECC's pre-merge verification ritual. TDT runs `tdt verify` (local verification) but doesn't have an automated loop. Useful reference.
- **Integration plan**: Reference only — TDT OpenSpec `opsx:verify` is canonical.

### `repo-scan`
- **Classification**: keep-optional
- **Rationale**: Generic repo scanner; useful for unfamiliar codebases.
- **Integration plan**: Available on demand; primary repo analysis in TDT is `gitnexus-exploring` skill.

### `skill-stocktake`
- **Classification**: keep-optional
- **Rationale**: ECC's skill inventory tool. TDT has `code-daily-scan` for code scanning but no skill-level audit tool.
- **Integration plan**: Available on demand; useful for the next ECC audit (could replace the ad-hoc ripgrep search we used in Task 3.1).

### `ecc-tools-cost-audit`
- **Classification**: keep-optional
- **Rationale**: Cost tracking for LLM usage. TDT has OpenTelemetry hook packs for cost tracking but no consolidated audit.
- **Integration plan**: Available on demand; TDT's OpenTelemetry hooks are the canonical cost instrumentation.

### `continuous-learning-v2`
- **Classification**: redundant-to-tdt-skill
- **Rationale**: ECC's pattern extraction from sessions writes to `~/.claude/session-data/`. TDT has `agentmemory` (LaunchAgent `com.tdt.agentmemory`) which owns session persistence and learning. Using both creates write conflicts.
- **Integration plan**:
  - **DO NOT enable** continuous-learning-v2
  - TDT canonical: `agentmemory` for session persistence, `recall`/`remember`/`recap` skills for retrieval
  - The ECC hook `stop:evaluate-session` (the only one we keep-default) runs but writes to a different location than agentmemory

### `healthcare-reviewer`
- **Classification**: keep-optional
- **Rationale**: POEMS Mobile 3 is a clinical app; healthcare-reviewer applies to poems-mobile3-ios/android.
- **Integration plan**:
  - Pairs with: `code-reviewer` for cross-cutting concerns, `swift-reviewer`/`kotlin-reviewer` for language-specific
  - Must not shadow: `code-reviewer`, `swift-reviewer`, `kotlin-reviewer`
  - How to invoke: Manually via `Skill(ecc:healthcare-reviewer)` when working on poems-mobile3-ios or poems-mobile3-android

### `loop` (ECC workflow loop)
- **Classification**: keep-optional
- **Rationale**: ECC's autonomous work loop. TDT has `agent-core` scheduler with similar concept.
- **Integration plan**: Available on demand; TDT `agent-core` is canonical for scheduled workflows.

### `babysit` (ECC process monitor)
- **Classification**: keep-optional
- **Rationale**: Monitors a long-running process. Not actively used in TDT.
- **Integration plan**: Available on demand.

## Version Pin Policy Decision

- **Decision**: Pin v2.0.0 with quarterly review
- **Rationale**:
  - Pin prevents silent surface area expansion (was the root cause of this audit's existence)
  - Quarterly review allows us to deliberately evaluate new features when ECC releases them
  - Auto-update was set to `true` in `~/.claude/settings.json` — that's the bug we're fixing
  - Auto-update disabled in this change (Task 6.2)
- **If quarterly review**: next review due: 2026-09-27 (3 months from audit date)

## Summary

| Feature | Decision | TDT Equivalent |
|---|---|---|
| orch-build-mvp | keep-optional | OpenSpec `openspec-propose` |
| orch-pipeline | keep-optional | OpenSpec workflow |
| hookify-rules | redundant-to-tdt-skill | hookify plugin (CLI) |
| context-budget | keep-optional | agentmemory |
| strategic-compact | keep-optional | TDT pre-compact hook |
| verification-loop | keep-optional | OpenSpec `opsx:verify` |
| repo-scan | keep-optional | gitnexus-exploring |
| skill-stocktake | keep-optional | (none — ad-hoc audit) |
| ecc-tools-cost-audit | keep-optional | OpenTelemetry hook packs |
| continuous-learning-v2 | redundant-to-tdt-skill | agentmemory |
| healthcare-reviewer | keep-optional | (none — POEMS Mobile 3 specific) |
| loop | keep-optional | agent-core scheduler |
| babysit | keep-optional | (none) |

Total candidates: 13 | Adopted (active): 0 | Keep-optional: 11 | Redundant-to-tdt-skill: 2 | Deferred: 0 | Rejected: 0

**Key insight**: 11 of 13 candidates are `keep-optional` rather than `adopted`. ECC v2.0.0 doesn't introduce features that would actively replace TDT workflows — TDT overlay (especially OpenSpec, agentmemory, hookify, gitnexus) already covers the same ground. The audit's primary value is the **noise reduction** (15 hooks disabled, 215 skills marked disabled-default).