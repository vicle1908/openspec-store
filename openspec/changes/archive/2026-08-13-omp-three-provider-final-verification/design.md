# Design: omp-three-provider-final-verification

Evidence-only. Records the final fresh-shell verification of all three omp
providers through the Homebrew-only installation. No configuration changes.

## Verification environment

- Homebrew-only omp binary: `/opt/homebrew/bin/omp` (v17.2.15)
- Fresh shell: `/bin/zsh -lic`
- Disposable profiles used for all explicit `--model` selector tests
- Live profile used only for default-role resolution (no `--model` flag)

## Provider transports

| Provider | baseUrl | api | model |
|---|---|---|---|
| cockpit | `http://localhost:51006/v1` | `openai-responses` | `gpt-5.6-luna` |
| giaoduc | `https://api.giaoduc.online` | `anthropic-messages` | `Advance` |
| shopapikey | `https://api.phanmemvip.shop` | `anthropic-messages` | `fable-5` |

## Fresh-shell test results

| Test | Selector | Result |
|---|---|---|
| cockpit :high | `cockpit/gpt-5.6-luna:high` | pong, exit 0 |
| cockpit :max | `cockpit/gpt-5.6-luna:max` | pong, exit 0 |
| shopapikey | `shopapikey/fable-5` | pong, exit 0 |
| giaoduc | `giaoduc/Advance` | pong, exit 0 |
| live default | (no `--model` flag) | pong, exit 0 |

## Shopapikey transient 403

During an earlier verification pass, shopapikey returned HTTP 403 with a
provider-side message indicating the API key was temporarily blocked due to
high burst traffic. The retry window was approximately 55 minutes or after
08:28 VN time on 2026-08-13. The subsequent verification in this session
confirmed the throttle had cleared and all three providers returned
successful responses. This is an upstream provider condition, not a
local configuration issue.

## Post-test drift check

- `models.yml` hash: `e223d68e0598fdef178db9be02cc23f0` (unchanged)
- `config.yml` hash: `238154c5ec2c29deffb95ef3f725db25` (unchanged)
- Both files mode 644
- Role map: `default: cockpit/gpt-5.6-luna:high`, `smol: shopapikey/fable-5`,
  `slow: cockpit/gpt-5.6-luna:max`, `plan: cockpit/gpt-5.6-luna:max`,
  `commit: shopapikey/fable-5`, `task: giaoduc/Advance`
- `modelRoles` absent from `models.yml`

## Stale residue

`~/node_modules/@oh-my-pi/` contains stale transitive residue (69 entries,
not in lockfile, not referenced by any active direct package). This is
**not** a second executable — Bun reports no installed direct omp package and
`~/.bun/bin/omp` is absent. The directory is non-functional residue; deleting
it is a separate optional cleanup, not part of this verification.
