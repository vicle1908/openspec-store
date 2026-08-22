# Routing Recommendation

## Status: NOT PRODUCED

No routing recommendation is produced because the benchmark evidence is insufficient.

## Evidence Status

- **Provider health**: Established — all 3 active providers pass basic text, tool round-trip, streaming, and env-var credential probes.
- **Quality benchmark**: Inconclusive — pilot data was invalidated and destroyed during cleanup; harness repeatedly modified; quality prompts produced empty outputs on Claude-Fable providers due to tool-use adapter behavior.
- **Role assignment**: Not attempted — no comparable quality dataset exists.

## What Is Known

| Question | Answer |
|---|---|
| Do 3 active providers work through Droid? | ✅ Yes — Phase 1 validated |
| Is there a trustworthy quality dataset? | ❌ No — pilot invalidated |
| Can roles be assigned? | ❌ No — requires quality benchmark |
| Is baseline available? | ❌ No — OmniRoute port 20128 |

## What Is Recommended

- No routing changes should be made.
- A new benchmark change should be created with corrected prompts (inline fixtures, tool-disable for quality scenarios).
- Baseline OmniRoute should be diagnosed in a separate infrastructure change.
- S3 multi-turn should be tested with a different CLI surface.
