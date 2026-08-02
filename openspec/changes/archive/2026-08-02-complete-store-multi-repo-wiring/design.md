## Architecture

### Command Resolution (Official Precedence)

```
1. --store <id>              ← explicit flag always wins
2. nearest openspec/         ← walking up from cwd
3. store: pointer            ← in config.yaml
4. defaultStore              ← global config (already set)
5. current dir               ← fallback
```

This change activates layer 3. Layer 4 is already active from the previous change.

### Per-Repo Store Pointers

Create `openspec/config.yaml` with `store: openspec-store` in:

| Repo | Has local openspec/? | Notes |
|------|---------------------|-------|
| go-microservices/ | No | Has .claude/skills/ |
| tdt-core/ | No | Python, has CLAUDE.md |
| tdt-sheets/ | No | Python, has CLAUDE.md |
| webhook-receiver/ | No | Python |
| jira-daily-reports/ | No | Python |
| ai-harness-skills/ | Yes (schemas/) | Preserve existing schemas/ |
| ops-automation-suite/ | No | Python |
| agent-docs-sync/ | No | Has CLAUDE.md |

### Git Remote

```bash
git -C ~/Developer/openspec-store remote add origin <url>
```

Update `.openspec-store/store.yaml`:
```yaml
remote: git@github.com:org/openspec-store.git
```

### File Relocation

Move to `docs/governance/`:
- `openspec/AGENTS.md` (update line 19: `openspec/config.yaml` ref)
- `openspec/INDEX.md`
- `openspec/AUDIT_INDEX.md`, `ALIGNMENT_SUMMARY.md`, `SPEC_TO_CODE_ALIGNMENT_AUDIT.md`, `AUDIT_COMPLETION_SUMMARY.txt`
- `openspec/reports/`

Cross-reference audit: AGENTS.md references `openspec/config.yaml` (line 19)
and `scripts/config/agent-skill-surfaces.json` (line 49). Config.yaml references
"AGENTS.md" generically (not by path). Active changes reference AGENTS.md by
name only. Safe to move.

## Alternatives

**Skip store pointers, rely on defaultStore:** Works but is lowest precedence.
Store pointers are the recommended pattern and make the relationship explicit.

**Defer git remote:** Possible but blocks team onboarding. Low risk to add now.
