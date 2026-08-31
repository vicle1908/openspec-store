# Investigation: coding-cli-provider-registry Model ID Citations

## Question
Does the canonical `coding-cli-provider-registry` spec contain contaminated model-ID strings, or are its citations of `sh/Claude-Fable` legitimate chat-fallback references to a live OmniRoute catalog ID?

## Findings
1. **Catalog Verification:** `sh/Claude-Fable` is a valid, live chat model ID in OmniRoute's `sh` namespace (Anthropic/Claude family served via OpenAI-compatible endpoints), separate from the GPT-5.6 route (`sh/gpt-5.6-sol`).
2. **Registry Spec Analysis:** The `coding-cli-provider-registry` specification deliberately tests both `sh/gpt-5.6-sol` (OpenAI Responses route) and `sh/Claude-Fable` (live Claude model chat fallback) where supported by client capabilities (such as Goose `custom_omniroute_sh` and Pi live providers).
3. **Conclusion:** Zero spec contamination. The canonical `coding-cli-provider-registry` spec is correct and internally consistent. No follow-up spec change is required.
