# Tasks: MoA Config Quality Tuning

## Section 1: Provider Health Verification

- [x] **1.1** Test cockpit fable-5.6-sol inference
  - Command: `curl -s http://localhost:51006/v1/chat/completions ...`
  - Verify: ✅ Response received, model confirmed

- [x] **1.2** Test shopapikey fable-5 inference
  - Verify: ✅ Live (tested earlier this session)

- [x] **1.3** Test giaoduc Advance inference
  - Verify: ✅ Live (tested earlier this session)

## Section 2: Implement Config Changes

- [x] **2.1** Replace entire MOA config via Python yaml.safe_load → modify → yaml.dump
  - Remove `context_length` from all preset slots
  - Add `max_tokens` to all presets (default: 4096, deep: 8192, fast: 4096)
  - Add `reference_temperature: 0.6` to all presets
  - Add `aggregator_temperature: 0.4` to default/fast, `0.3` to deep
  - Upgrade default/deep aggregator to cockpit:fable-5.6-sol
  - Add `reference_max_tokens: 800` to deep preset
  - Verify: `hermes moa list` shows correct structure

## Section 3: Verification

- [x] **3.1** Verify `hermes moa list` output
  - All 3 presets present
  - default/deep aggregator is cockpit:gpt-5.6-sol
  - fast aggregator is shopapikey:fable-5
  - No `context_length` in preset slots

- [x] **3.2** Verify no stale fields in config.yaml
  - `grep context_length ~/.hermes/config.yaml` — only in provider sections, not presets

- [x] **3.3** OpenSpec validation
  - Command: `openspec validate moa-config-quality-tuning --store openspec-store`

- [x] [historical] **3.4** Smoke test in new session
  - Switch to `/model default --provider moa`
  - Verify MoA pipeline works with new aggregator


---

> **Historical record:** This change was archived with 1 incomplete task(s) (7/8 completed). The remaining tasks were not implemented or were superseded by subsequent changes.
