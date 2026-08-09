# Design: Standardize Seven-CLI Review Orchestration

## Architecture

The review workflow operates at two layers:

1. **Skill files** (`~/.hermes/skills/autonomous-ai-agents/{cli}/SKILL.md`) — per-CLI orchestration guides with version-specific flags, smoke test patterns, and troubleshooting
2. **Review references** (`~/.hermes/skills/software-development/openspec-workflow/references/`) — cross-CLI orchestration patterns for OpenSpec change reviews

## Current State (verified 2026-08-09)

### Installed CLIs (all real files, not symlinks)

| CLI | Version | Size | Config Location |
|-----|---------|------|-----------------|
| Claude | 2.1.226 | 17KB | `~/.claude/` |
| Codex | 0.147.0 | 13KB | `~/.codex/` |
| Agy | 1.1.11 | 17KB | `~/.fable-5/` |
| fable-5 | 0.34.0 | 10KB | `~/.config/fable-5/` |
| OpenCode | 1.18.15 | 8KB | `~/.config/opencode/` |
| Pi | 0.84.1 | 20KB | `~/.pi/` |
| Goose | 1.45.0 | 18KB | `~/.config/goose/` |

### Key Flag Corrections

| CLI | Incorrect | Correct | Evidence |
|-----|-----------|---------|----------|
| Agy | `--print` | `-p` (alias for `--print`) | `agy --help` shows `-p` as short alias |
| Pi | `--no-session` | Does not exist | `pi --help` shows no `--no-session` flag |
| Codex | `--json` | `--json` not a direct flag | Use `codex exec` which outputs to stdout |
| Goose | `goose run "prompt"` | `goose run -t "prompt"` | `-t`/`--text` flag required for inline text |

## Design Decisions

### 1. Compact Review Fixture Pattern

Use a <5KB context fixture for CLI reviews, not the full 60KB+ change bundle. The fixture contains:
- Proposal summary (3-5 sentences)
- Key changes made (bullet list)
- CLI status table
- Specific review questions

This avoids the fable-5 stall issue with large contexts and keeps reviews focused.

### 2. Real CLI Verification Protocol

Before dispatching reviews, verify each CLI with a tiny prompt:
```bash
timeout 30 $CLI -p "Reply exactly OK" 2>&1 | head -3
```
Record exit code and output. A CLI that stalls or returns empty is marked UNKNOWN.

### 3. Default Model Policy

All CLIs use their own configured default model. Never pass `-m`, `--model`, or provider overrides. This ensures:
- Each reviewer uses a different model (diversity)
- No configuration conflicts
- Simpler invocation patterns

### 4. Output Contract

Each CLI reviewer returns:
```
VERDICT: APPROVE / APPROVE_WITH_CONDITIONS / REJECT
FINDINGS: list each with severity (CRITICAL/HIGH/MEDIUM/LOW)
RECOMMENDATIONS: specific actionable fixes
```

### 5. Legacy Filename Preservation

Keep `five-provider-review-orchestration.md` filename for backward compatibility with existing skill references and cross-references.

## Merge Semantics

The review workflow is additive — new findings are appended, not replacing. When findings are applied between rounds, the context fixture must be rebuilt with updated artifacts.

## Testing

1. Run each CLI with `timeout 30 $CLI -p "Reply exactly OK"` — verify output + exit code
2. Build compact fixture from proposal + design + tasks
3. Dispatch 7 CLIs in batches of 3 (max concurrent)
4. Record results in structured format
5. Apply any actionable findings
6. Commit
