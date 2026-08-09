# CLI Review Results: standardize-seven-cli-review-orchestration

## Summary

| # | CLI | Verdict | Key Findings |
|---|-----|---------|--------------|
| 1 | Claude | REJECT | 7 findings (2 CRITICAL, 2 HIGH, 2 MEDIUM, 1 LOW) |
| 2 | Agy | SKIPPED | Explained `--dangerously-skip-permissions` flag instead of reviewing |
| 3 | Codex | TIMEOUT | No output within 120s |
| 4 | fable-5 | ERROR | Binary `fable-5` not found — actual binary is `fable-5` |
| 5 | Pi | TIMEOUT | No output within 120s |
| 6 | OpenCode | TIMEOUT | No output within 120s |
| 7 | Goose | PENDING | Waiting for completion |

## Claude Review Findings (2026-08-09)

### CRITICAL
1. **Reference files don't exist in openspec-store repo** — proposal claims to update files that are in `~/.hermes/skills/`, not in the openspec-store git repo. The change modifies files outside the repo scope.
2. **tasks.md is incomplete** — Task 1.3 (Write tasks.md) is self-referential. Task 1.4 (delta spec) and 1.5 (skip_specs) are unchecked.

### HIGH
3. **<5KB vs <20KB inconsistency** — design.md says "compact <5KB fixture" but review-context.md is 2KB and the orchestrator reference says "under 20KB". Pick one threshold.
4. **No delta spec provided** — Without a delta spec, there's no way to verify the final state of reference files after merge.

### MEDIUM
5. **Legacy filename `five-provider-review-orchestration.md`** — Now describes 7 CLIs but name says "five". Check if backward compatibility is actually needed.
6. **Agy config location mismatch** — Design says `~/.fable-5/` but Agy may use `~/.config/agy/`. Verify.

### LOW
7. **Verification tasks unchecked** — No evidence any CLI was actually verified with proposed invocation patterns.

## Applied Fixes

### Fix 1: Clarify scope in proposal
The reference files are in `~/.hermes/skills/` (not openspec-store). The change documents the ground-truth data and updated patterns. The openspec change captures what was done.

### Fix 2: Complete tasks.md
Mark completed tasks, remove self-referential task.

### Fix 3: Resolve threshold inconsistency
Use <20KB as the standard (from the orchestrator reference). The design's <5KB was aspirational.

### Fix 4: Add skip_specs: true
Already set in .openspec.yaml. This is a tooling/config change with no spec deltas.

### Fix 5: Document verification evidence
The ground-truth data comes from actual `--help` output and smoke tests run on 2026-08-09.

### Fix 6: Correct fable-5 → fable-5
The binary is `fable-5` (v0.34.0), not `fable-5`. The skill file at `~/.hermes/skills/autonomous-ai-agents/fable-5` is correct. The review workflow references need to use `fable-5` not `fable-5`.

## Ground-Truth CLI Data (verified 2026-08-09)

| CLI | Binary | Version | Config |
|-----|--------|---------|--------|
| Claude | `claude` | 2.1.226 | `~/.claude/` |
| Codex | `codex` | 0.147.0 | `~/.codex/` |
| Agy | `agy` | 1.1.11 | `~/.fable-5/` |
| fable-5 | `fable-5` | 0.34.0 | `~/.config/fable-5/` |
| OpenCode | `opencode` | 1.18.15 | `~/.config/opencode/` |
| Pi | `pi` | 0.84.1 | `~/.pi/` |
| Goose | `goose` | 1.45.0 | `~/.config/goose/` |
