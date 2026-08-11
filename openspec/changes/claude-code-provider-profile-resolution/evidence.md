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

```json
// Before
{ "model": "Advance[1m]", ... }

// After
{ "autoCompactEnabled": ..., "env": { "API_TIMEOUT_MS": ..., ... }, ... }
// No "model" key. No ANTHROPIC_BASE_URL in env.
```

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

| Launcher | _claude_require_token | --settings | profile path |
|---|---|---|---|
| shopapikey() | HERMES_CUSTOM_SHOPAPIKEY_API_KEY | yes | $HOME/.claude/profiles/shopapikey.json |
| giaoduc() | HERMES_CUSTOM_GIAODUC_API_KEY | yes | $HOME/.claude/profiles/giaoduc.json |
| cockpit() | HERMES_CUSTOM_COCKPIT_API_KEY | yes | $HOME/.claude/profiles/cockpit.json |

`grep -c '_claude_model_default' ~/.zshrc` → 0 (old helper fully removed).
`grep -c '_claude_with_profile' ~/.zshrc` → 4 (1 definition + 3 call sites).
`grep -c '--settings' ~/.zshrc` → 3 (one per launcher).

### Auth token injection

Each launcher exports only `ANTHROPIC_AUTH_TOKEN` in its subshell from `$HERMES_CUSTOM_*_API_KEY`. Token never written to profile JSON. Verified by wire capture showing `authorization: present` header.

## Wire-level capture evidence

Local capture server on port 19999, profile temporarily patched to point to `http://127.0.0.1:19999`, real `claude --settings` invoked.

### shopapikey

```
wire model: fable-5
output_config.effort: xhigh
authorization: present (pmv_t81Mr35G6...)
captured requests: 2
```

Note: `system_model` and `result` fields were not parseable due to iTerm2 OSC escape sequences in Claude's JSON stdout. Wire request body was captured and verified independently.

### giaoduc

```
wire model: Advance
output_config.effort: xhigh
authorization: present
captured requests: 2
```

Same parser caveat as shopapikey.

### cockpit (gpt-5.6-luna)

```
wire model: gpt-5.6-luna
output_config.effort: max
authorization: present
captured requests: 2
```

Same parser caveat as shopapikey.

## Real launcher smoke

### giaoduc (full end-to-end)

`zsh -lic 'giaoduc --print --output-format json "Return exactly GIAODUC_PROFILE_LIVE"'`:

```
exit_code: 0
system_model: Advance[1m]
result_subtype: success
is_error: False
modelUsage: ['Advance[1m]']
```

JSON output parsed after stripping iTerm2 OSC escape sequences via `sed 's/\x1b\]1337;[^[:cntrl:]]*\x07//g'`.

### shopapikey and cockpit

Real launcher smoke for shopapikey and cockpit was NOT performed through the full `zsh -lic` pipeline. Only wire-level local capture tests were completed. This is an honest gap in the evidence record.

## OpenSpec validation

```
openspec validate claude-code-provider-profile-resolution --store openspec-store → valid
openspec validate --all --store openspec-store → 358 passed, 0 failed
```

## Cockpit model spelling

The implementation uses `gpt-5.6-luna` because the cockpit provider accepted it. The user initially proposed `fable-5.6-luna`, but the provider rejected it with `model_not_available`.

## What is NOT proven

1. shopapikey and cockpit real launcher smoke through `zsh -lic` (only wire capture performed).
2. shopapikey real launcher smoke through `zsh -lic` (only wire capture performed).
3. Provider-side 1M context window capacity (only client-side `[1m]` selector acceptance proven).
