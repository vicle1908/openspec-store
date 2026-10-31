# Evidence: reconcile-omniroute-cross-spec-minor-drift

## 1. Cross-Surface Audit & Remediation Summary

- **Managed Skills Updated (`~/.omp/agent/managed-skills/`)**:
  - `omniroute-v3852-config-and-skill-tuning/SKILL.md`: Reconciled tier-matched timeouts (`180000`/`60000` on `gemini-4-argon*` & `claude-opus-5.5`, `120000`/`45000` on `claude-sonnet-5.5`, `25000`/`25000` on `gemini-3.8-flash-high` & `muse-spark-1.3`), pure 15-step `claude-opus-5.5` / `claude-sonnet-5.5` pools (`0` `combo-ref` steps, per-account `syncedAvailableModels` `5-5-high` on `38782750`), and `...current.config` preservation.
  - `omniroute-sqlite-startup-and-volume-maintenance/SKILL.md`: Reconciled structural `docker-compose.override.yml` (`0` `environment:` entries), `crypto.scryptSync(secret, "omniroute-field-encryption-v1", 32)` key derivation, and `51` modifications (`N1`–`N3` + `R1`–`R48`) / `60` fail-closed markers across `24` compiled files.
  - `muse-code-omniroute-setup/SKILL.md`: Reconciled `muse-spark-1.3` (`context_cache_protection: false`) and Gate 4b (`MUSE_CODE_REWRITE_V3` `N1` + `48` non-Muse chunk rules / `60` markers).
- **User Custom Skill Blocks, Wiki, Docs & Memory Updated**:
  - `~/.agents/skills/{omni-combos-routing,cli-routing,omni-settings}/SKILL.md`
  - `wiki/entities/{omniroute,muse-code,goose,kimi-code}.md`, `wiki/concepts/omniroute-gemini-4-argon-fleet-routing.md`, `wiki/index.md`, `docs/omniroute-agent-skills.md`
  - `memory://root/{memory_summary.md,MEMORY.md,skills/omniroute-and-omp-operations/SKILL.md}`
- **Live `~/.claude/profiles/omniroute-pm.json` Readback**:
  - `"model": "gemini-3.8-flash-high"`, `"modelOverrides": {"gemini-3.8-flash-high": "gemini-3.8-flash-high"}`, `"apiKeyHelper": "/Users/androidteam/.claude/helpers/omniroute-key.sh"`, `modelPicker.options` exposing `gemini-3.8-flash-high` and `gemini-4-argon*`.
- **Validation**:
  - All 6 OmniRoute specs (`omniroute-runtime-customization`, `omniroute-compression-and-routing`, `omniroute-agent-cli-routing`, `omniroute-closure-integrity`, `omniroute-agent-skills`, `claude-code-omniroute-pm-routing`) pass `openspec validate <spec> --type spec --strict --store openspec-store` (`exit 0`).
  - `python3 /Users/androidteam/Developer/platform/openspec-store/scripts/sync-workspace-agent-skills.py --check` exits `0` (`malformed_entries=0`, `snapshot_check=ok`).
