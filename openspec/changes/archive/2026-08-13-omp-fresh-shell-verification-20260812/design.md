# Design: omp-fresh-shell-verification-20260812

## Fresh-shell environment

- Shell: `/bin/zsh -lic`
- Selected omp: `~/.bun/bin/omp`
- Version: `omp/17.2.15`
- `PI_SMOL_MODEL`, `PI_SLOW_MODEL`, `PI_PLAN_MODEL`: unset
- All three `HERMES_CUSTOM_*_API_KEY` variables: present (values not printed)

## Live configuration

- `models.yml`: `e223d68e0598fdef178db9be02cc23f0`, mode 644
- `config.yml`: `238154c5ec2c29deffb95ef3f725db25`, mode 644
- Cockpit: `http://localhost:51006/v1`, `openai-responses`
- `modelRoles` only in `config.yml`
- No provider base URL references adapter ports 8787 or 8788

## Real CLI results

| Test | Result |
|---|---|
| `cockpit/gpt-5.6-luna:high` in disposable profile | pong, exit 0 |
| `cockpit/gpt-5.6-luna:max` in disposable profile | pong, exit 0 |
| `giaoduc/Advance` in disposable profile | pong, exit 0 |
| live default role, no `--model` | pong, exit 0 |
| `shopapikey/fable-5` in disposable profile | HTTP 403, exit 1 |

The explicit tests used disposable profiles; the live profile was used only
for the no-flag default-role test. After testing, all disposable profiles were
removed and the live hashes remained unchanged.

## Shopapikey blocker classification

Both the Bun-selected omp binary and the Homebrew omp binary produced the same
HTTP 403 from shopapikey. A direct fresh-shell request to
`https://api.phanmemvip.shop/v1/messages` with the configured credential also
returned HTTP 403 with the provider message indicating the API key is
temporarily blocked due to high burst traffic, with a provider-supplied retry
window. This is an upstream credential/rate-limit condition, not an omp
transport or model-resolution failure.

No local routing change is justified. Retry after the provider's stated window
or resolve the provider-side key/burst condition. Credentials were not printed
or rotated.

## Default-role drift

The final live default role is `cockpit/gpt-5.6-luna:high` and returned pong.
A disposable-profile test showed explicit `--model` selection did not mutate
its config file. The earlier drift cause remains unknown.
