# Implementation Evidence

Evidence captured on 2026-08-09. Credential values, authorization headers, and complete provider configuration blocks are intentionally excluded.

## Ground Truth

- Hermes Agent: v0.20.0 (2026.8.3), config schema v33.
- Primary model: `moa:default`.
- Presets: exactly `default`, `deep`, and `fast`.
- Privacy filter: `display`; trace saving disabled.
- Delegation and auxiliary compression resolve through `moa:default`.
- All MoA-used providers and models declare `context_length: 1000000`; MoA slots contain no context field.

## Warning Investigation

### `Active in config: (off)`

Source inspection:

- `hermes_cli/moa_cmd.py` prints `(off)` when normalized `moa.active_preset` is empty.
- `hermes_cli/runtime_provider.py` independently resolves `requested_provider == "moa"` to the local MoA virtual provider.
- `agent/agent_init.py` constructs the MoA facade when the selected provider is `moa`.

Conclusion: the line reports the optional `moa.active_preset` override, not primary-model deactivation. `model.provider: moa` plus `model.default: default` remains the active default route.

### Stale direct-model endpoint fields

The pre-change `model.base_url` and `model.key_env` described Antigravity. Source inspection showed the MoA resolver constructs `base_url: moa://local` and a placeholder virtual credential; real references/aggregators resolve through `providers.<name>`. Both stale fields were removed with `hermes config unset`.

### Duplicate-primary fallback

A backend-identity probe compared current `moa/default/moa://local` with fallback `moa/default` and returned `should_skip_candidate == True`. Hermes would skip that entry and advance. It was removed; the chain now begins with the first independent direct provider.

## Configuration Validation

A `yaml.safe_load` assertion script passed all of:

- exact primary `model == {provider: moa, default: default}`;
- exact preset names and every model/reasoning/token/temperature/cadence setting;
- valid cockpit spelling `gpt-5.6-sol` and no `fable-5.6-sol` in active config;
- no legacy flat MoA keys;
- no slot-level context fields;
- provider and used-model context declarations equal 1,000,000;
- fallback order is `shopapikey:fable-5`, `giaoduc:Advance`, `cockpit:gpt-5.6-luna`;
- stale direct-model `base_url` and `key_env` are absent.

`hermes config check` exited 0. `hermes config get model`, `hermes config get moa`, `hermes moa list`, and `hermes fallback list` returned normalized structured state matching the specification.

## Provider Inference

Sanitized non-streaming checks:

| Provider/model | Result | HTTP | Notes |
|---|---|---:|---|
| cockpit / `gpt-5.6-sol` | PASS | 200 | response contained role/content/reasoning/tool-call fields |
| shopapikey / `fable-5` | PASS | 200 | response contained role/content/reasoning/tool-call fields |
| giaoduc / `Advance` | PASS | 200 | first batch observed a transient 502; bounded retry succeeded on the next independent check |

No secret values were printed or retained.

## Real MoA Tool-Call Smoke

Command route: fresh quiet session with `--provider moa -m default`, source `moa-doc-sync-smoke`, maximum 8 turns.

Session ID: `20260809_125933_805257`.

Transcript evidence:

1. user requested terminal `printf "MOA_TOOL_OK\n"` and an exact final response;
2. assistant message `99299` emitted a real `terminal` function call;
3. tool message `99300` returned `MOA_TOOL_OK`, exit code 0;
4. assistant message `99301` continued after the tool result and returned `MOA_SMOKE_OK`.

This proves aggregator tool-call ownership and post-tool continuation. A shell command executed outside the session was not used as evidence.

## Documentation Drift Classification

Current canonical specs/docs contained no MoA-specific stale provider assignments. Three current matches for `claude-opus-4.8` belong to unrelated generic agent/dependency examples and are not MoA drift. Archived changes retain historical old-model references by design; archived artifacts were not rewritten.

## OpenSpec Validation

- Focused strict validation: PASS.
- `openspec show sync-hermes-moa-config-docs --json`: PASS, eight ADDED requirements parsed.
- Strict main-spec validation: 339/339 PASS.
- Full-store baseline validation: 346/347 PASS. The sole failure is the unrelated pre-existing active change `align-jti-skill-runtime-contract`, whose MODIFIED deltas omit existing scenarios across `fix-rca-fix-status-detection`, `impact-sheet-integration`, and `jti-classification-accuracy`. This change does not own or modify those files.
- Store doctor: PASS, no store issues.
- Owned-document relative links: PASS.
- Owned-artifact secret-shape scan: PASS.
- `git diff --check`: PASS.

## Safety and Rollback

A local backup was created under `~/.hermes/backups/` before mutation. Source and backup SHA-256 values matched. The path and hash are local operational evidence and are not committed into a public spec. The backup contains configuration only and remains outside the OpenSpec repository.

## Post-Archive Validation

- Archive created: `openspec/changes/archive/2026-08-09-sync-hermes-moa-config-docs/`.
- Canonical spec created: `openspec/specs/hermes-moa-configuration/spec.md` with eight requirements.
- Archived task state: 23 complete, 0 incomplete.
- Focused canonical spec strict validation: PASS.
- Strict main-spec validation after archive: 340/340 PASS.
- Full-store baseline after archive: 346/347 PASS; the only failure remains the unrelated pre-existing `align-jti-skill-runtime-contract`.
- Store doctor: PASS.
- Archive and worktree path checks: PASS; active change directory absent.
