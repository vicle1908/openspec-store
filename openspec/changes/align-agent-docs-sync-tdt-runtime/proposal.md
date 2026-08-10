## Why

`agent-docs-sync` currently has a split runtime contract: repository configuration, shared TDT settings, provider credentials, model failover, and LLM outcome reporting are not consistently resolved or surfaced through the canonical CLI. This is now blocking trustworthy real LLM-backed verification: a valid TDT primary can run, but fallback availability, configured iteration limits, generation failures, and exit status are easy to misclassify.

## What Changes

- Make the shared `$TDT_HOME/config.yaml` and `$TDT_HOME/.env` boundary the default source for docs-sync model, provider, credential, and runtime settings, while retaining explicit repository and `DOCS_SYNC_*` overrides.
- Compose the configured primary and fallback model identifiers through the public `agent-core.sdk` factory, failing closed and logging only redacted provider-availability diagnostics when a route lacks credentials.
- Pass effective iteration and timeout limits into the generation agent instead of retaining hard-coded generation limits.
- Preserve generation completion, reason, error, approval, and iteration metadata through the workflow report.
- Normalize nested workflow reports before human-readable output and distinguish execution failure from documentation/generation non-compliance in CLI exit codes.
- Update configuration/CLI documentation and the canonical docs-sync skill with the TDT precedence, secret boundary, fallback behavior, runtime limits, and exit-code contract.
- Add regression and disposable live-acceptance coverage for global config resolution, explicit overrides, provider construction/degradation, report normalization, runtime limits, and failure exit status.

Explicit non-goals:

- Do not copy, print, commit, or provision provider credentials.
- Do not change the global TDT provider registry or agent-core model-factory semantics in this consumer change.
- Do not broaden normal docs-sync write roots or make docs-sync responsible for OpenSpec/source-file promotion.
- Do not claim successful documentation generation when the provider/agent returns an incomplete result.

## Capabilities

### New Capabilities

- `agent-docs-sync-tdt-runtime`: Shared TDT configuration precedence, provider-aware model resolution, runtime limits, and secret-safe degradation for docs-sync.

### Modified Capabilities

- `agent-docs-sync`: Canonical configuration, generation outcome, and truthful CLI reporting requirements are extended to cover the shared TDT runtime and distinct execution/compliance exit outcomes.
- `agent-docs-sync-resilience`: Consumer-side fallback construction and incomplete-generation reporting are aligned with the existing provider resilience contract.

## Impact

- Affected repository: `/Users/androidteam/Developer/agent-docs-sync` (`config.yaml`, config/model/generation workflow modules, CLI/reporting, tests, docs, and canonical `.agents/skills/doc-sync/SKILL.md`).
- Affected shared dependency boundary: public `agent_core.sdk.load_settings()` and `create_fallback_model()` are consumed; agent-core source and the protected TDT credential files remain unchanged.
- Affected operator surface: `docs-sync sync` output and exit codes; configuration precedence and supported environment overrides become explicit.
- Verification must preserve the repository's pre-existing Graphify/GitNexus changes and untracked skill scaffold.
