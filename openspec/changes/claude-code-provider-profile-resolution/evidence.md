# Evidence: claude-code-provider-profile-resolution

## Diagnosis

### Root cause

`~/.claude/settings.json` contained `"model": "Advance[1m]"` as a global override. Claude Code reads this before processing `--model` flags or subshell environment variables. The old `_claude_model_default` helper only passed `--model` via CLI flag but never exported the required environment variables (`ANTHROPIC_MODEL`, `ANTHROPIC_BASE_URL`, `ANTHROPIC_CUSTOM_MODEL_OPTION`, model alias overrides) that fable-5's resolution pipeline reads.

### Fake-claude probe (before fix)

All three launchers showed env vars as `<unset>` at the child process level:

```
shopapikey → ANTHROPIC_MODEL: <unset>, ANTHROPIC_BASE_URL: <unset>
giaoduc    → ANTHROPIC_MODEL: <unset>, ANTHROPIC_BASE_URL: <unset>
cockpit    → ANTHROPIC_MODEL: <unset>, ANTHROPIC_BASE_URL: <unset>
```

## Fix verification

### settings.json provider-neutral

Evidence: `python3 -c "import json; d=json.load(open(settings.json)); assert 'model' not in d; assert 'ANTHROPIC_BASE_URL' not in d.get('env',{})"` — PASS.

### Profile files

| Profile | model | ANTHROPIC_BASE_URL | ANTHROPIC_MODEL | CLAUDE_CODE_EFFORT_LEVEL | mode | secrets |
|---|---|---|---|---|---|---|
| shopapikey.json | fable[1m] | https://api.phanmemvip.shop | fable[1m] | xhigh | 600 | none |
| giaoduc.json | Advance[1m] | https://api.giaoduc.online | Advance[1m] | xhigh | 600 | none |
| cockpit.json | gpt-5.6-luna[1m] | http://localhost:8787 | gpt-5.6-luna[1m] | max | 600 | none |

Evidence: `python3 -c "..."` assertions PASS for all three. No `ANTHROPIC_AUTH_TOKEN`, `API_KEY`, `TOKEN`, or `SECRET` in any profile env block.

### .zshrc syntax

`zsh -n ~/.zshrc` → exit 0, no errors.

### Launcher wiring

- `grep -c '_claude_model_default' ~/.zshrc` → 0 (old helper fully removed).
- `grep -c '_claude_with_profile' ~/.zshrc` → 4 (1 definition + 3 call sites).
- `grep -c '--settings' ~/.zshrc` → 3 (one per launcher).
- `grep -c '_claude_require_token' ~/.zshrc` → 4 (1 definition + 3 guard calls).
- Cockpit fallback uses `gpt-5.6-luna[1m]` (user-corrected; `fable-5.6-luna` was rejected by provider).

### Auth token injection

Each launcher exports only `ANTHROPIC_AUTH_TOKEN` in its subshell from `$HERMES_CUSTOM_*_API_KEY`. Token never written to profile JSON. Verified by wire capture showing `authorization: present`.

## Wire-level capture evidence

Local capture server on port 19999, profile temporarily patched to point to `http://127.0.0.1:19999`, real `claude --settings` invoked.

### shopapikey

```
wire model: fable-5
output_config.effort: xhigh
authorization: present
captured requests: 2
```

### giaoduc

```
wire model: Advance
output_config.effort: xhigh
authorization: present
captured requests: 2
```

### cockpit

```
wire model: gpt-5.6-luna
output_config.effort: max
authorization: present
captured requests: 2
```

## Fresh-shell smoke (authoritative, latest run)

| Provider | Model | Sentinel | Fresh-shell result |
|---|---|---|---|
| shopapikey | `fable-5[1m]` | `SHOP_LIVE_GATE_7X9K` | PASS — exit 0, is_error=False, modelUsage=fable-5[1m], exact sentinel |
| cockpit | `gpt-5.6-luna[1m]` | `COCKPIT_GPT_1M_FINAL` | PASS — exit 0, is_error=False, modelUsage=gpt-5.6-luna[1m], exact sentinel |
| giaoduc | `Advance[1m]` | `GIAODUC_LIVE_GATE_3M2P` | BLOCKED — model resolution correct (system_model=Advance[1m]), provider returns HTTP 403 API key expired or not found |

### Cockpit `[1m]` fix

The cockpit launcher fallback was corrected from `gpt-5.6-luna` to `gpt-5.6-luna[1m]`. Fresh-shell smoke confirmed `system_model: gpt-5.6-luna[1m]` and `modelUsage: ['gpt-5.6-luna[1m]']`.

### giaoduc status

The giaoduc credential (`$HERMES_CUSTOM_GIAODUC_API_KEY`) is expired or not found. The model resolution and base URL are correct — `system_model: Advance[1m]` was confirmed by the provider before it rejected the expired token. This is a credential refresh issue, not a code defect.

## OpenSpec validation

```
openspec validate claude-code-provider-profile-resolution --store openspec-store → valid
openspec validate --all --store openspec-store → 358 passed, 0 failed
```

## Cockpit model spelling

The implementation uses `gpt-5.6-luna` because the cockpit provider accepted it. The user initially proposed `fable-5.6-luna`, but the provider rejected it with `model_not_available`.

## Not proven

1. Provider-side 1M context window capacity (only client-side `[1m]` selector acceptance proven).
