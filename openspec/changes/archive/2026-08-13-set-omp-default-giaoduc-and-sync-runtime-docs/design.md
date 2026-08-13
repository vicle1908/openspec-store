# Design: set-omp-default-giaoduc-and-sync-runtime-docs

## Ground truth

| Field | Value |
|---|---|
| models.yml hash | `747167245051c2fe546636b98beb112a` |
| config.yml hash | `00539e9fa8b643768fe927e158eba229` |
| default role | `giaoduc/Advance` |
| smol role | `shopapikey/fable-5` |
| slow role | `cockpit/gpt-5.6-luna:max` |
| plan role | `cockpit/gpt-5.6-luna:max` |
| commit role | `shopapikey/fable-5` |
| task role | `giaoduc/Advance` |
| Homebrew omp | v17.3.0 at `/opt/homebrew/bin/omp` |
| Cockpit endpoint | `http://localhost:51006/v1`, `openai-responses` |
| contextWindow (×3) | 1,000,000 |

Fresh-login-zsh acceptance passed for the default and every explicit selector.
No live YAML mutation is needed. The configuration is correct.

## Documentation drift

Three archived main specs are stale:

1. **omp-fresh-shell-contract** line 59: requirement says "SHALL resolve to
   `cockpit/gpt-5.6-luna:high`" — must become `giaoduc/Advance`.
2. **omp-provider-routing** line 152: scenario assumes Cockpit is assigned to
   `default` — must become Giaoduc.
3. **omp-installation-management** line 4: hardcodes v17.2.15 — must become
   evidence-based version tracking.

Archives remain historical. We do not rewrite archive evidence.

## Spec strategy

For omp-fresh-shell-contract:
- REMOVED: "Native Cockpit default role" requirement (wrong default)
- ADDED: "Giaoduc default role" requirement (correct default)

For omp-provider-routing:
- MODIFIED: "Capability-based role allocation" requirement — update all
  scenario expectations from Cockpit default to Giaoduc default. Copy every
  existing scenario verbatim, change only the role expectations.

For omp-installation-management:
- MODIFIED: "Canonical omp binary resolution" requirement — replace pinned
  v17.2.15 with evidence-based version that matches the Homebrew formula.

## Commit hygiene

Stage only the coherent omp archive/spec lineage:
- `openspec/specs/omp-*/spec.md` (4 main specs)
- `openspec/specs/coding-agent-credential-loading/spec.md`
- `openspec/changes/archive/2026-08-1*` (all omp archives)
- `openspec/changes/set-omp-default-giaoduc-and-sync-runtime-docs/`

Exclude:
- `openspec/changes/complete-agent-llm-config-integration/`
- `openspec/specs/provider-model-profile-resolution/spec.md`
- Any unrelated reconciliation archives
