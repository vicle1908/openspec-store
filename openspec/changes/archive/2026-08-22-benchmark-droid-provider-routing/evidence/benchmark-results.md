# Benchmark Results

## Summary

Phase 2 benchmark is **inconclusive**. No quality or role conclusions are supported.

## What Was Established

| Question | Answer | Evidence |
|---|---|---|
| Do the 3 active providers work through Droid? | ✅ Yes | Phase 1 health probes: text, tools, streaming, env-var auth |
| Is the baseline available? | ❌ No | OmniRoute port 20128 not listening |
| Can S3 multi-turn be tested? | ❌ No | `droid exec --session-id` fails on turn 2 |
| Is there a trustworthy quality dataset? | ❌ No | Pilot data destroyed during cleanup; harness repeatedly edited |

## Pilot Data (Historical — Not Usable)

A pilot with 22 records was collected before the harness was finalized. It showed:

| Provider | S1 | S2 | S4 | S5 | S6 | S7 |
|---|---|---|---|---|---|---|
| cockpit | ✅ | ✅ | 3/3 | 2/3 | ✅ | 3/3 |
| giaoduc | ✅ | ❌ | 0/3 | 1/3 | ✅ | 3/3 |
| shopapikey | ✅ | ✅ | 0/3 | 1/3 | ✅ | 0/3 |

**This data is not usable for routing decisions because:**
1. The harness was modified after collection
2. Quality scenario prompts triggered tool-use, causing Anthropic adapter output loss
3. Empty results were scored as 0 instead of classified as `adapter_output_unavailable`
4. No repetitions were completed
5. The data was destroyed and cannot be re-verified

## Known Issues

1. **Anthropic adapter output loss**: Quality prompts that trigger Droid tool-use produce `subtype=success` with empty `result` on Claude-Fable providers. This is an adapter-level issue, not a model capability issue.
2. **Empty output classification**: Scoring functions treated empty output as score 0 rather than a distinct failure class (`adapter_output_unavailable`).
3. **Cockpit intermittent auth**: Earlier authentication failures were not fully characterized before the pilot.
4. **Fixture path guard**: The `prepare_fixtures()` function rejected `/tmp/droid-benchmark` because `/tmp` resolves to `/private/tmp` on macOS.

## Recommendations

- No routing changes should be made based on this evidence.
- A new benchmark change should be created with inline fixture prompts and tool-disable for quality scenarios.
- Baseline OmniRoute should be diagnosed in a separate infrastructure change.
- S3 multi-turn should be tested with a different CLI surface (e.g., Factory App).
