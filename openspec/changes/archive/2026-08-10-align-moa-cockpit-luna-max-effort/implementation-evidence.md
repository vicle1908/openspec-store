# Implementation Evidence: Cockpit Luna Max- Effort Alignment

Evidence captured on 2026-08-10. Credentials, authorization headers, and secret values are excluded.

## Pre-Change Ground Truth

- Hermes Agent: v0.20.0 (2026.8.3).
- Primary route: `model.provider: moa`, `model.default: default`.
- Before mutation, `default` had a cockpit Luna reference at `high`, an extra `giaoduc:Advance` reference, and a `shopapikey:fable-5` aggregator.
- Before mutation, `deep` used cockpit `gpt-5.6-sol` as reference and aggregator; `fast` used cockpit `gpt-5.6-sol` as its reference at `medium`.
- The OpenSpec canonical store had three unrelated untracked change directories. They were not edited or staged.
- A clean isolated worktree was created from `main` at `/Users/androidteam/Developer/.worktrees/openspec-moa-luna-max-effort`.

## Provider Health

Sanitized direct non-streaming checks passed both before and after mutation:

| Provider/model | Post-change result | HTTP | Post-change latency |
|---|---|---:|---:|
| cockpit / `gpt-5.6-luna` | PASS | 200 | 1427 ms |
| shopapikey / `fable-5` | PASS | 200 | 951 ms |
| giaoduc / `Advance` | PASS | 200 | 1701 ms |

Each response contained a usable choices result. No credential values or authorization headers were printed.

## Applied Configuration

The target was built from the verified pre-change backup and written atomically after the Hermes complex-value setter serialized the first attempted mapping as a YAML string. The final on-disk YAML parses `moa` as a mapping.

Final target:

- `providers.cockpit.model`: `gpt-5.6-luna`.
- `moa.privacy_filter`: `display`.
- `default`: references `shopapikey:fable-5` high and `cockpit:gpt-5.6-luna` max; aggregator cockpit Luna max; ref cap 600; output cap 4096; temperatures 0.6/0.4; `user_turn`.
- `deep`: references `shopapikey:fable-5` xhigh, cockpit Luna max, and `giaoduc:Advance` high; aggregator cockpit Luna max; ref cap 800; output cap 8192; temperatures 0.6/0.3; `every_n:3`.
- `fast`: reference cockpit Luna max; aggregator `shopapikey:fable-5` high; ref cap 300; output cap 4096; temperatures 0.6/0.4; `user_turn`.
- Existing `degraded_reference_policy: loud`, enabled flags, and provider/model one-million-token context declarations preserved.
- No MoA slot contains `context_length`.
- Fallback chain remains independent: `shopapikey:fable-5`, `giaoduc:Advance`, `cockpit:gpt-5.6-luna`.

`hermes moa list`, `hermes config get moa`, `hermes config check`, and the YAML assertion suite all passed after mutation. `hermes config check` reports only the existing config schema update notice (`33 -> 34`), with no required-field error.

## Real MoA Smoke Test

Fresh command:

```text
hermes chat -Q --provider moa -m default --source moa-luna-max-smoke --max-turns 8
```

Session: `20260810_112950_bb4831`.

Session-store evidence:

1. User requested terminal `printf "MOA_LUNA_TOOL_OK\\n"` and exact final text.
2. Assistant message `110368` emitted a real `terminal` function call.
3. Tool message `110369` returned `MOA_LUNA_TOOL_OK` with exit code 0.
4. Assistant message `110371` returned `MOA_LUNA_SMOKE_OK`.

This proves the Luna-backed default aggregator requested and continued after a real tool result.

## Code-Path Verification

No Hermes source patch was made. Installed source inspection confirmed:

- `cli.py` resolves `requested_provider == "moa"` and builds the MoA client with `provider: moa`, `base_url: moa://local`.
- `chat_completion_helpers.py` routes `agent.provider == "moa"` through the in-process MoA facade.
- `run_agent.py` preserves the primary client path for MoA.

The configuration change uses the existing virtual-provider implementation; no compatibility shim or upstream source modification is needed.

## Stale-Reference Classification

- Active `~/.hermes/config.yaml` contains no cockpit-backed MoA slot using `gpt-5.6-sol`; the provider model default is Luna. The cockpit model catalog retains Sol as a discoverable non-selected model and is not removed by this change.
- Current runbook and the successor canonical spec are updated to Luna/max.
- The change proposal/design/delta intentionally mention Sol as the pre-change baseline and acceptance target; those are historical evidence, not stale operational configuration.
- Generic `agent-core-model-resolution` specification scenarios use Sol as model-resolution fixtures and are unrelated to the Hermes MoA profile; they were not rewritten.
- Archived historical changes are preserved and not edited.

## Rollback

Backup created before mutation:
`/Users/androidteam/.hermes/backups/config-before-luna-fix-20260810-105918.yaml`

The backup matched the pre-change config SHA-256 at creation. It remains outside Git. Rollback means restoring that file atomically and rerunning config, provider, and MoA smoke validation.
