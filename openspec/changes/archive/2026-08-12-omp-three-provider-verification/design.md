# Design: omp-three-provider-verification

## Verification scope

This change documents the real CLI verification of all three omp providers
and records the final corrected state. No live configuration changes.

## Evidence summary

### Fresh-shell tests (all via `/bin/zsh -lic`)

| Test | Selector | Result |
|---|---|---|
| 1 | `cockpit/gpt-5.6-luna:high` | pong, exit 0 |
| 2 | `cockpit/gpt-5.6-luna:max` | pong, exit 0 |
| 3 | `shopapikey/fable-5` | pong, exit 0 |
| 4 | `giaoduc/Advance` | pong, exit 0 |
| 5 | Live default (no `--model`) | pong, exit 0 |

### Invariant checks (11/11 PASS)

- 4 providers present (cockpit, giaoduc, omniroute, shopapikey)
- cockpit: `baseUrl=http://localhost:51006/v1`, `api=openai-responses`
- shopapikey: `api=anthropic-messages`
- giaoduc: `api=anthropic-messages`
- No provider references adapter ports (8787 or 8788)
- Exact 6-role map matches proposal
- No OmniRoute assigned to any role
- OmniRoute block preserved (3 models, equivalence)
- `modelRoles` absent from `models.yml`
- All 3 custom `apiKey` values are env-var references
- No plaintext secrets

### Default-role drift investigation

The `default` role was observed as `giaoduc/Advance` instead of the expected
`cockpit/gpt-5.6-luna:high`. A disposable-profile persistence test proved
the `--model` flag does NOT mutate `config.yml`. The actual cause of the
earlier drift remains **unknown**.

### Permission restoration

`config.yml` was changed to mode 600 during the earlier direct rewrite.
This contradicts the archived evidence that both live files were mode 644.
Restored to 644; hash unchanged at `238154c5ec2c29deffb95ef3f725db25`.

## Duplicate installations

Two omp binaries exist:
- `~/.bun/bin/omp` → Bun-managed (fresh shell picks this)
- `/opt/homebrew/bin/omp` → Homebrew Cellar

Both at version 17.2.15. Standardizing to one installation is a non-blocking
follow-up.
