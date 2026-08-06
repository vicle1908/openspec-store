# Plan Review: hermes-agentmemory-plugin-integration

**Reviewed:** 2026-08-06
**Providers:** Hermes (Spec Compliance), Claude Code (Security), Codex (Quality), Antigravity (Architecture), Pi (Product Scope)
**Scope:** Configuration + plugin integration (skip_specs: true)

## Alignment Summary

| Edge | Status | Provider | Evidence |
|------|--------|----------|----------|
| Spec ↔ Code | PASS | Hermes | skip_specs change, no code modifications. Plugin approach matches developer-memory spec requirements. Non-overlapping ownership preserved (Hermes native memory + agentmemory). |
| Spec ↔ Docs | PASS | Hermes | proposal.md "Why" section aligns with developer-memory spec Purpose. "What Changes" matches spec scenarios. Design references spec's single-engine requirement. |
| Spec ↔ Tests | PASS | Hermes | tasks.md Phase 4 verification steps cover all spec scenarios: server health, MCP tools, cross-agent recall, non-overlapping ownership. |
| Code ↔ Docs | PASS | Codex | design.md architecture diagram accurately describes the dual-provider split (Ofable-5 embeddings + shopapikey LLM). Plugin implementation matches upstream integrations/hermes/ source. |
| Code ↔ Tests | PASS | Codex | tasks.md Phase 4 has 9 verification checkboxes covering: memory save/recall, prefetch injection, sync_turn capture, compaction protection, MCP tools, viewer visibility, embedding dimensions. |
| Docs ↔ Skills | PASS | Antigravity | workspace-knowledge-tools skill has agentmemory-hermes-plugin.md and agentmemory-ofable5-embedding.md references already aligned with this change's approach. |
| Code ↔ Skills | PASS | Antigravity | Skill references match plugin architecture (MemoryProvider interface, 6 hooks). Ofable-5 embedding config in skill matches design.md. |
| Skills ↔ Specs | PASS | Pi | developer-memory spec requires agentmemory as shared layer. This change adds Hermes integration specifically — within spec scope. No scope creep. |

## Security Lens

| Concern | Status | Provider | Evidence |
|---------|--------|----------|----------|
| .env file permissions | PASS | Claude Code | `-rw-------@` (600) confirmed on ~/.agentmemory/.env |
| Credential exposure | PASS | Claude Code | design.md references env var name (HERMES_CUSTOM_SHOPAPIKEY_API_KEY), not actual key. .env target shows `<value from ...>` placeholder. |
| API key in .env | WARN | Claude Code | .env will contain actual shopapikey key. Mitigated by 600 permissions, localhost-only binding, and .gitignore exclusion. |
| Network security | PASS | Claude Code | Ofable-5 bound to 127.0.0.1 (localhost). shopapikey uses HTTPS. CORS origins loopback-only. |
| Plugin security | PASS | Claude Code | Third-party code from agentmemory repo (v0.8.0 plugin). Upstream source verified at integrations/hermes/. No hardcoded secrets found. |
| iii binary signature | PASS | Claude Code | Adhoc linker-signed (expected for npm-distributed binary). SHA256 hash verified. |
| Process security | PASS | Claude Code | Stale processes identified for kill. No orphaned processes. |
| Backup files | PASS | Claude Code | ~/.agentmemory/backups/ has restrictive permissions. No secrets in plaintext. |
| Log leakage | PASS | Claude Code | agentmemory.log contains no credential material. Only OTel/reconnect messages. |

## Status Counts

- PASS: 17
- WARN: 1 (API key in .env — mitigated)
- FAIL: 0
- N/A: 0
- UNKNOWN: 0

## Provider Findings

### Hermes (Spec Compliance)
**Assigned Edges:** Spec ↔ Code, Spec ↔ Docs, Spec ↔ Tests

- skip_specs change — no delta specs needed. Correct approach for config-only change.
- developer-memory spec's "Non-overlapping ownership" requirement satisfied: Hermes built-in memory (MEMORY.md/USER.md) stays separate from agentmemory (episodic/project context).
- Single canonical engine requirement satisfied: Phase 0 kills stale processes, Phase 1 starts one server.
- Go service code unchanged — verified no go.mod or .go file modifications.
- tasks.md Phase 4 covers all spec verification scenarios.

### Claude Code (Security)
**Assigned Lens:** Security across all edges

- **PASS** — All 9 security concerns pass or have mitigations.
- Key finding: .env will store shopapikey key at 600 permissions. This is the standard pattern for local service credentials.
- iii binary is adhoc-signed (not Apple-notarized) — expected for npm packages, not a blocker.
- CORS restricted to localhost origins — no external access.
- No credential leakage in logs, backups, or design docs.

### Codex (Quality & Tests)
**Assigned Edges:** Spec ↔ Tests, Code ↔ Tests, Code ↔ Docs

- design.md accurately describes dual-provider architecture with ASCII diagrams.
- tasks.md has 33 actionable checkboxes across 6 phases (0-5 + archive).
- Phase 0 correctly identifies root cause (missing iii-config.yaml) and provides fix.
- Verification steps in Phase 4 are specific and testable (curl commands, process checks, port checks).
- One note: tasks.md Phase 0 "Configure .env" task has 3 sub-items (LLM, embeddings, server) — all actionable.

### Antigravity (Architecture)
**Assigned Edges:** Code ↔ Skills, Docs ↔ Skills

- workspace-knowledge-tools skill already has:
  - `references/agentmemory-hermes-plugin.md` — plugin architecture, files, hooks
  - `references/agentmemory-ofable5-embedding.md` — embedding + LLM config split
- Skill references are aligned with this change's approach (Ofable-5 embeddings + shopapikey LLM).
- Phase 5 tasks correctly plan to update the skill after implementation.
- No skill conflicts detected.

### Pi (Product Scope)
**Assigned Edges:** Skills ↔ Specs, scope check

- Change stays within developer-memory spec scope — adds Hermes integration only.
- No scope creep: no Go code changes, no new services, no database migrations.
- All 5 phases are complete and actionable.
- Archive plan is correct (skip_specs → trivial archive).
- .openspec.yaml correctly declares repos: [openspec-store].

## Recommended Actions

1. **No blocking issues found.** All edges PASS, one WARN (API key in .env) is mitigated.
2. **Ready for execution.** Proceed with Phase 0 → Phase 5.
3. **Post-implementation:** Update workspace-knowledge-tools skill (Phase 5) to reflect installed status.
