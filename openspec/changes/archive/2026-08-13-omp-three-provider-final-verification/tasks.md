# Tasks: omp-three-provider-final-verification

Evidence-only change documenting final fresh-shell verification of all three omp providers through Homebrew-only installation.

## 1. Fresh-shell verification (completed)

- [x] 1.1 Homebrew-only binary: `/opt/homebrew/bin/omp` (v17.2.15)
- [x] 1.2 Fresh shell resolves single omp binary
- [x] 1.3 `cockpit/gpt-5.6-luna:high` → pong, exit 0
- [x] 1.4 `cockpit/gpt-5.6-luna:max` → pong, exit 0
- [x] 1.5 `shopapikey/fable-5` → pong, exit 0 (after transient 403 cleared)
- [x] 1.6 `giaoduc/Advance` → pong, exit 0
- [x] 1.7 Live default role (no `--model`) → pong, exit 0

## 2. Post-test invariant checks (completed)

- [x] 2.1 `models.yml` hash unchanged: `e223d68e0598fdef178db9be02cc23f0`
- [x] 2.2 `config.yml` hash unchanged: `238154c5ec2c29deffb95ef3f725db25`
- [x] 2.3 Role map exact match verified
- [x] 2.4 `modelRoles` absent from `models.yml`
- [x] 2.5 Cockpit `baseUrl` and `api` verified

## 3. Cleanup (completed)

- [x] 3.1 Disposable profiles removed
- [x] 3.2 Temporary files removed
- [x] 3.3 No live config modified

## 4. Documentation

- [x] 4.1 Design.md written
- [x] 4.2 Tasks.md written
