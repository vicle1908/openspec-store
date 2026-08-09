# Tasks: Hermes MoA Quality Optimization

## Section 1: Clean Up Legacy Config

- [ ] **1.1** Remove legacy flat-level MoA block from config.yaml
  - Command: `hermes config unset moa.reference_models`
  - Command: `hermes config unset moa.aggregator`
  - Command: `hermes config unset moa.degraded_reference_policy`
  - Command: `hermes config unset moa.max_tokens`
  - Command: `hermes config unset moa.fanout`
  - Command: `hermes config unset moa.enabled`
  - Verify: `grep -c 'reference_models' ~/.hermes/config.yaml` — only inside presets

- [ ] **1.2** Remove existing default preset (duplicated models)
  - Command: `hermes moa delete default`
  - Verify: `hermes moa list` shows "No presets configured"

## Section 2: Create Quality-Tiered Presets

- [ ] **2.1** Create `default` preset (balanced quality, 3 diverse models)
  - Reference 1: shopapikey / fable-5 (reasoning_effort: high)
  - Reference 2: cockpit / gpt-5.6-sol (reasoning_effort: high)
  - Aggregator: giaoduc / Advance (reasoning_effort: xhigh)
  - reference_max_tokens: 600
  - fanout: user_turn
  - Verify: `hermes moa list` shows default with 2 references + aggregator

- [ ] **2.2** Create `deep` preset (maximum reasoning)
  - Reference 1: shopapikey / fable-5 (reasoning_effort: xhigh)
  - Reference 2: cockpit / gpt-5.6-sol (reasoning_effort: xhigh)
  - Reference 3: giaoduc / Advance (reasoning_effort: high)
  - Aggregator: shopapikey / fable-5 (reasoning_effort: max)
  - fanout: every_n:3
  - Verify: `hermes moa list` shows deep with 3 references + aggregator

- [ ] **2.3** Create `fast` preset (quick turns)
  - Reference 1: cockpit / gpt-5.6-sol (reasoning_effort: medium)
  - Aggregator: shopapikey / fable-5 (reasoning_effort: high)
  - reference_max_tokens: 300
  - fanout: user_turn
  - Verify: `hermes moa list` shows fast with 1 reference + aggregator

## Section 3: Set Global Defaults

- [ ] **3.1** Set default preset and privacy filter
  - Command: `hermes config set moa.default_preset default`
  - Command: `hermes config set moa.privacy_filter display`
  - Verify: `hermes config get moa.default_preset` returns "default"

## Section 4: Validation

- [ ] **4.1** Verify complete MoA config
  - Command: `hermes moa list` — shows 3 presets, default active
  - Verify no legacy flat-level block remains
  - Verify gpt-5.6-sol appears as cockpit reference in default preset

- [ ] **4.2** Smoke test default preset
  - Start session: `/model default --provider moa`
  - Send test message and verify MoA reference outputs appear
  - Verify tool calls work through the aggregator

- [ ] **4.3** OpenSpec validation
  - Command: `openspec validate hermes-moa-quality-optimization --store openspec-store`
  - Expected: skip_specs validated, artifacts complete
