# Cleanup legacy giaoduc references across main specs

## Why

The giaoduc retirement and provider migration changed normative requirements via
delta specs, but the surrounding descriptive text and illustrative scenarios in
five main specs still reference giaoduc. These stale references contradict the
retired-provider state and create confusion. This change corrects all remaining
legacy giaoduc text.

## What Changes

- `register-custom-provider-credentials`: update Purpose text from
  `(shopapikey, giaoduc, cockpit)` to `(shopapikey, phanmemvip, cockpit)`.
- `agent-core-model-resolution`: update Purpose text from "the active giaoduc
  Claude-Fable Messages setup" to "the active phanmemvip Codex Responses setup".
- `tdt-env-loader-tdt-home`: update illustrative credential scenario from
  `provider: "giaoduc"` to `provider: "phanmemvip"`.
- `omp-fresh-shell-contract`: update Purpose from "giaoduc/Advance preserved as
  the default role" to current state (shopapikey/Claude-Fable as the fallback
  role).
- `resilience`: update fallback scenario from "giaoduc is the primary provider"
  to current provider topology.

## Capabilities

### New Capabilities
- None.

### Modified Capabilities
- `register-custom-provider-credentials`: Purpose text update.
- `agent-core-model-resolution`: Purpose text update.
- `tdt-env-loader-tdt-home`: illustrative scenario update.
- `omp-fresh-shell-contract`: Purpose text update.
- `resilience`: fallback scenario update.

## Impact

- Main spec text only (5 specs); no behavioral requirement changes.
