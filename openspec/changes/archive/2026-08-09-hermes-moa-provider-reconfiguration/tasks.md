# Tasks: Hermes MoA Provider Reconfiguration

## Section 1: Clean Up Broken Config

- [x] [historical] **1.1** Remove the legacy flat-level moa block from config.yaml
  - Command: `hermes config unset moa.reference_models`
  - Command: `hermes config unset moa.aggregator`
  - Command: `hermes config unset moa.degraded_reference_policy`
  - Command: `hermes config unset moa.max_tokens`
  - Command: `hermes config unset moa.fanout`
  - Command: `hermes config unset moa.enabled`
  - Verify: `grep -c 'reference_models' ~/.hermes/config.yaml` should only show inside presets

- [x] [historical] **1.2** Remove the broken default preset
  - Command: `hermes moa delete default`
  - Verify: `hermes moa list` shows "No presets configured"

## Section 2: Create New Presets

- [x] [historical] **2.1** Create `default` preset (balanced quality)
  - Command: `hermes moa configure default`
  - Configure interactively:
    - Reference 1: giaoduc / Advance
    - Reference 2: shopapikey / fable-5
    - Aggregator: shopapikey / fable-5
    - reference_max_tokens: 600
    - fanout: user_turn
    - enabled: true
  - Verify: `hermes moa list` shows default preset with correct models

- [x] [historical] **2.2** Create `fast` preset (quick & cheap)
  - Command: `hermes moa configure fast`
  - Configure interactively:
    - Reference 1: giaoduc / Advance
    - Aggregator: shopapikey / fable-5
    - reference_max_tokens: 300
    - fanout: user_turn
    - enabled: true
  - Verify: `hermes moa list` shows fast preset

- [x] [historical] **2.3** Create `deep` preset (maximum reasoning)
  - Command: `hermes moa configure deep`
  - Configure interactively:
    - Reference 1: giaoduc / Advance (reasoning_effort: high)
    - Reference 2: shopapikey / fable-5 (reasoning_effort: high)
    - Aggregator: shopapikey / fable-5 (reasoning_effort: xhigh)
    - fanout: per_iteration
    - enabled: true
  - Verify: `hermes moa list` shows deep preset

## Section 3: Set Global Defaults

- [x] [historical] **3.1** Set default preset and privacy filter
  - Command: `hermes config set moa.default_preset default`
  - Command: `hermes config set moa.privacy_filter display`
  - Verify: `hermes config get moa.default_preset` returns "default"

## Section 4: Validation

- [x] [historical] **4.1** Verify complete MoA config structure
  - Command: `hermes moa list` — shows 3 presets, default active
  - Command: `hermes config get moa` — clean YAML, no legacy block
  - Verify no references to openai-codex or openrouter remain

- [x] [historical] **4.2** Smoke test default preset
  - Command: Start interactive session, switch to `/model default --provider moa`
  - Send a test message and verify response includes MoA reference outputs
  - Verify tool calls still work (MoA preserves full agent loop)

- [x] [historical] **4.3** OpenSpec validation
  - Command: `openspec validate hermes-moa-provider-reconfiguration --store openspec-store`
  - Expected: specs skipped (skip_specs: true), artifacts complete


---

> **Historical record:** This change was archived with 9 incomplete task(s) (0/9 completed). The remaining tasks were not implemented or were superseded by subsequent changes.
