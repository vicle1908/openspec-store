# Tasks: omp-fresh-shell-verification-20260812

## 1. Fresh-shell preflight

- [x] 1.1 Verify fresh zsh shell resolves omp and reports v17.2.15
- [x] 1.2 Verify all three credential env vars are present without printing values
- [x] 1.3 Verify PI role override env vars are unset
- [x] 1.4 Verify live hashes and role map before tests

## 2. Real CLI tests

- [x] 2.1 `cockpit/gpt-5.6-luna:high` → pong, exit 0
- [x] 2.2 `cockpit/gpt-5.6-luna:max` → pong, exit 0
- [x] 2.3 `giaoduc/Advance` → pong, exit 0
- [x] 2.4 Live default role, no `--model` → pong, exit 0
- [x] 2.5 `shopapikey/fable-5` attempted in disposable profile

## 3. Blocker classification

- [x] 3.1 Same shopapikey 403 reproduced with Bun-selected omp
- [x] 3.2 Same shopapikey 403 reproduced with Homebrew omp
- [x] 3.3 Direct provider request returned HTTP 403
- [x] 3.4 Provider response classified as temporary burst throttle
- [x] 3.5 No local routing or model-resolution change applied

## 4. Safety and cleanup

- [x] 4.1 Explicit selector tests used disposable profiles
- [x] 4.2 Live hashes unchanged after tests
- [x] 4.3 All disposable profiles removed
- [x] 4.4 Temporary probe file removed
- [x] 4.5 Correct role map preserved (`default: cockpit/gpt-5.6-luna:high`)

## Evidence

- Live `models.yml`: `e223d68e0598fdef178db9be02cc23f0`, mode 644
- Live `config.yml`: `238154c5ec2c29deffb95ef3f725db25`, mode 644
- Provider blocker: HTTP 403 temporary burst throttle from shopapikey
- Passing providers: native Cockpit and giaoduc
- Passing default role: native Cockpit

## Status

Verification complete. Shopapikey remains externally blocked until its
provider-side throttle window clears or the provider resolves the key condition.
