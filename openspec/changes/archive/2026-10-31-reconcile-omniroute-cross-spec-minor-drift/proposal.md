# Proposal

## Why

A cross-surface consistency check across all 6 OmniRoute OpenSpec specifications, wiki pages, operational docs, and skills identified three remaining minor cross-spec discrepancies:
1. **`omniroute-agent-cli-routing/spec.md:541`**: The scenario `OmniRoute combo muse-spark-1.3 intercepts bare model requests and preserves namespace tools` still states `context_cache_protection: true` for `muse-spark-1.3`, contradicting lines `706` and `710` of the same spec (`context_cache_protection: false`), `omniroute-compression-and-routing/spec.md:44`, and live SQLite `combos` state.
2. **`omniroute-agent-skills/spec.md:76` vs `:204`**: Line `76` (`Ecosystem Knowledge Hub and Documentation Synchronization`) states `all 22 omni-* REST endpoints`, whereas line `204` (`OmniRoute v3.8.52 Agent Skill Accuracy`) states `23 omni-* REST skills` (`23` `omni-*` + `21` `cli-*` + `1` `agent-onboarding` = `45` total skills).
3. **`claude-code-omniroute-pm-routing/spec.md:13,18,59,69-71`**: Still states that `~/.claude/profiles/omniroute-pm.json` sets top-level `model` to `pm/Claude-Fable` and leaves a truncated `#### Scenario: One launcher per provider surface` header at EOF (line `71`), whereas live `~/.claude/profiles/omniroute-pm.json`, `omniroute-agent-cli-routing/spec.md:449,671`, and `omniroute-agent-skills/spec.md:146` configure `"model": "gemini-3.8-flash-high"` with `modelOverrides: {"gemini-3.8-flash-high": "gemini-3.8-flash-high"}` and `gemini-4-argon*` options in `modelPicker.options`.

## What Changes

- **`omniroute-agent-cli-routing`**: Reconcile `context_cache_protection: false` on `muse-spark-1.3` in `Scenario: OmniRoute combo muse-spark-1.3 intercepts bare model requests and preserves namespace tools`.
- **`omniroute-agent-skills`**: Reconcile `all 23 omni-* REST endpoints` in `Scenario: Operational guide provides actionable agent recipes`.
- **`claude-code-omniroute-pm-routing`**: Reconcile `gemini-3.8-flash-high` as the top-level `model` and `modelOverrides` key in `~/.claude/profiles/omniroute-pm.json` and complete `Scenario: One launcher per provider surface`.

## Capabilities

### New Capabilities

*(None)*

### Modified Capabilities
- `omniroute-agent-cli-routing`: Update `context_cache_protection: true` to `context_cache_protection: false` in the `muse-spark-1.3` scenario.
- `omniroute-agent-skills`: Update `all 22 omni-* REST endpoints` to `all 23 omni-* REST endpoints` in the operational guide scenario.
- `claude-code-omniroute-pm-routing`: Align `omniroute-pm.json` top-level `model` and `modelOverrides` with `"gemini-3.8-flash-high"` and complete the trailing scenario block.

## Impact

- **OpenSpec Store (`/Users/androidteam/Developer/platform/openspec-store`)**: Syncs `omniroute-agent-cli-routing`, `omniroute-agent-skills`, and `claude-code-omniroute-pm-routing` so all 6 OmniRoute main specs are 100% mutually consistent.
- **Managed Skills, User Skills, Wiki & Memory**: Synchronized `omniroute-v3852-config-and-skill-tuning`, `omniroute-sqlite-startup-and-volume-maintenance`, `muse-code-omniroute-setup`, `~/.agents/skills/{omni-combos-routing,cli-routing,omni-settings}`, `wiki/{entities,concepts}/*`, `docs/omniroute-agent-skills.md`, and `memory://root/*`.
