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
  - Reference 1: shopapikey / fable-5 (reasoning_effort: high, context_length: 1M)
  - Reference 2: cockpit / gpt-5.6-sol (reasoning_effort: high, context_length: 1M)
  - Aggregator: giaoduc / Advance (reasoning_effort: xhigh, context_length: 1M)
  - reference_max_tokens: 600, fanout: user_turn
  - Verify: ✅ `hermes moa list` shows correct models

- [x] **2.2** Create `deep` preset (maximum reasoning)
  - Reference 1: shopapikey / fable-5 (reasoning_effort: xhigh, context_length: 1M)
  - Reference 2: cockpit / gpt-5.6-sol (reasoning_effort: xhigh, context_length: 1M)
  - Reference 3: giaoduc / Advance (reasoning_effort: high, context_length: 1M)
  - Aggregator: shopapikey / fable-5 (reasoning_effort: max, context_length: 1M)
  - fanout: every_n:3
  - Verify: ✅ `hermes moa list` shows 3 references + aggregator

- [x] **2.3** Create `fast` preset (quick turns)
  - Reference 1: cockpit / gpt-5.6-sol (reasoning_effort: medium, context_length: 1M)
  - Aggregator: shopapikey / fable-5 (reasoning_effort: high, context_length: 1M)
  - reference_max_tokens: 300, fanout: user_turn
  - Verify: ✅ `hermes moa list` shows fast preset

## Section 3: Set Global Defaults + Context Length

- [x] **3.1** Set default preset and privacy filter
  - Command: `hermes config set moa.default_preset default`
  - Command: `hermes config set moa.privacy_filter display`
  - Verify: ✅ `hermes config get moa.default_preset` returns "default"

- [x] **3.2** Set context_length: 1000000 on all MOA slots
  - All 9 slots (5 references + 3 aggregators + 1 fast aggregator) set to 1000000
  - Verify: ✅ awk count confirms 9 context_length entries in MOA section

- [x] **3.3** Set default model to use MOA
  - Command: `hermes config set model.provider moa`
  - Command: `hermes config set model.default default`
  - Verify: ✅ `hermes config get model.provider` returns "moa"
  - Verify: ✅ `hermes config get model.default` returns "default"

- [x] **3.4** Pin all cron jobs to moa:default
  - 4 jobs pinned: weekly-graphify-freshness, weekly-wiki-lint, go-microservices-monthly-assessment, mcp-router-watchdog
  - Command: `hermes cron edit <job_id> --model default --provider moa`
  - Verify: ✅ `hermes cron list` shows all jobs with pinned model/provider

## Section 4: Validation

- [x] **4.1** Verify complete MoA config
  - ✅ `hermes moa list` — 3 presets, default active
  - ✅ cockpit model is gpt-5.6-sol (not fable-5)
  - ✅ no legacy flat-level block remains
  - ✅ model.provider = moa, model.default = default
  - ✅ delegation.provider = moa, delegation.model = default
  - ✅ auxiliary.compression.provider = moa

- [x] **4.2** Provider health check
  - ✅ cockpit gpt-5.6-sol: OK
  - ✅ shopapikey fable-5: OK
  - ✅ giaoduc Advance: OK

- [x] **4.3** OpenSpec validation
  - Command: `openspec validate hermes-moa-quality-optimization --store openspec-store`
  - Result: ✅ "Change 'hermes-moa-quality-optimization' is valid"

- [x] [historical] **4.4** Smoke test (requires new session)
  - Start new session with `/model default --provider moa`
  - Verify MoA reference outputs appear in responses
  - Verify tool calls work through the aggregator


---

> **Historical record:** This change was archived with 1 incomplete task(s) (12/13 completed). The remaining tasks were not implemented or were superseded by subsequent changes.
