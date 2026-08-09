# Tasks: Hermes MoA Quality Optimization

## Section 1: Clean Up Legacy Config

- [x] **1.1** Remove legacy flat-level MoA block from config.yaml
  - Commands: `hermes config unset moa.reference_models`, `moa.aggregator`, `moa.degraded_reference_policy`, `moa.max_tokens`, `moa.fanout`, `moa.enabled`
  - Verify: ✅ `hermes moa list` shows only presets, no legacy block

- [x] **1.2** Remove old default preset and recreate
  - Command: `hermes config set --force moa` with full preset block
  - Verify: ✅ `hermes moa list` shows 3 presets

## Section 2: Create Quality-Tiered Presets

- [x] **2.1** Create `default` preset (balanced quality, 3 diverse models)
  - Reference 1: shopapikey / fable-5 (reasoning_effort: high)
  - Reference 2: cockpit / fable-5.6-sol (reasoning_effort: high)
  - Aggregator: giaoduc / Advance (reasoning_effort: xhigh)
  - reference_max_tokens: 600, fanout: user_turn
  - All slots: context_length: 1000000
  - Verify: ✅ `hermes moa list` shows correct models

- [x] **2.2** Create `deep` preset (maximum reasoning)
  - Reference 1: shopapikey / fable-5 (reasoning_effort: xhigh)
  - Reference 2: cockpit / gpt-5.6-sol (reasoning_effort: xhigh)
  - Reference 3: giaoduc / Advance (reasoning_effort: high)
  - Aggregator: shopapikey / fable-5 (reasoning_effort: max)
  - fanout: every_n:3
  - All slots: context_length: 1000000
  - Verify: ✅ `hermes moa list` shows 3 references + aggregator

- [x] **2.3** Create `fast` preset (quick turns)
  - Reference 1: cockpit / gpt-5.6-sol (reasoning_effort: medium)
  - Aggregator: shopapikey / fable-5 (reasoning_effort: high)
  - reference_max_tokens: 300, fanout: user_turn
  - All slots: context_length: 1000000
  - Verify: ✅ `hermes moa list` shows fast preset

## Section 3: Set Global Defaults + Context Length

- [x] **3.1** Set default preset and privacy filter
  - Command: `hermes config set moa.default_preset default`
  - Command: `hermes config set moa.privacy_filter display`
  - Verify: ✅ `hermes config get moa.default_preset` returns "default"

- [x] **3.2** Set context_length: 1000000 on all MOA slots
  - All 9 slots (5 references + 3 aggregators + 1 fast aggregator) set to 1000000
  - Verify: ✅ `awk` count confirms 9 context_length entries in MOA section

## Section 4: Validation

- [ ] **4.1** Verify complete MoA config
  - Command: `hermes moa list` — shows 3 presets with correct models
  - Verify cockpit model is gpt-5.6-sol (not fable-5)
  - Verify no legacy flat-level block remains

- [ ] **4.2** Smoke test default preset
  - Start session: `/model default --provider moa`
  - Send test message and verify MoA reference outputs appear
  - Verify tool calls work through the aggregator

- [ ] **4.3** OpenSpec validation
  - Command: `openspec validate hermes-moa-quality-optimization --store openspec-store`
  - Expected: skip_specs validated, artifacts complete
