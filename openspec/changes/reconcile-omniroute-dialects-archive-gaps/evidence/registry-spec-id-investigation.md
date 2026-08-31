# Registry Spec ID Investigation: `sh/Claude-Fable` in canonical spec scenarios

Date: 2026-08-31 · Read-only investigation — no canonical spec is edited by this change.

## Question

The canonical `coding-cli-provider-registry` spec contains scenarios that reference `sh/Claude-Fable` in SH (Responses/Chat) route contexts. Are these legitimate references to a live catalog ID, or contaminated model-ID strings from the same defect that produced the archived final-evidence-manifest's SH rows?

## Findings

### 1. Live catalog state (2026-08-31)

`sh/Claude-Fable` IS a live model ID in the OmniRoute catalog (context 200,000). It exists alongside `pm/Claude-Fable` and `sh/gpt-5.6-sol`. The model is servable via chat-completions (FBC-3 streaming verification from the archived probe matrix) and was verified passing via the versionless chat fallback for codex, goose, omp, and opencode.

### 2. Spec scenario analysis

The `coding-cli-provider-registry` spec scenarios that reference `sh/Claude-Fable`:

- **Goose catalog:** "model list SHALL contain `sh/gpt-5.6-sol` and `sh/Claude-Fable`" — this is a REGISTRATION requirement (the model must be in the catalog), not a routing assertion. The goose catalog lists both. Legitimate.
- **Pi models:** "model list SHALL contain `sh/gpt-5.6-sol` with contextWindow 1050000 and `sh/Claude-Fable` with contextWindow 200000" — a REGISTRATION requirement. The pi `omniroute` provider lists both. Legitimate.
- **Omp aliases:** "model aliases `or-gpt-5-6-sol` (model `sh/gpt-5.6-sol`) and `or-claude-fable` (model `sh/Claude-Fable`)" — a REGISTRATION of both models under the omniroute provider. Legitimate.

### 3. Comparison with the archived manifest defect

The archived final-evidence-manifest's SH rows cited `sh/Claude-Fable` as the model for the SH ROUTE (Responses endpoint), which is wrong — the SH route model is `sh/gpt-5.6-sol`. But the spec scenarios above reference `sh/Claude-Fable` as a REGISTERED MODEL (available for selection), not as the SH route model. These are different assertions.

## Conclusion

The canonical spec scenarios referencing `sh/Claude-Fable` are **legitimate registration requirements**, not contaminated SH-route assertions. The model ID `sh/Claude-Fable` is a valid live catalog ID registered under the `sh/` namespace and servable via chat-completions. The archived manifest's defect (citing it as the SH route model) was specific to the archived evidence file, not the canonical spec. Zero canonical spec contamination exists.
