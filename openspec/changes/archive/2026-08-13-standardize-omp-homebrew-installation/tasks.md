# Tasks: standardize-omp-homebrew-installation

## 1. Pre-removal baseline

- [x] 1.1 Record `models.yml` hash: `e223d68e0598fdef178db9be02cc23f0`
- [x] 1.2 Record `config.yml` hash: `238154c5ec2c29deffb95ef3f725db25`
- [x] 1.3 Record Bun omp path: `~/.bun/bin/omp` (exists, symlink to `~/node_modules/@oh-my-pi/pi-coding-agent/dist/cli.js`)
- [x] 1.4 Record Homebrew omp path: `/opt/homebrew/bin/omp` (exists, native binary 122MB)
- [x] 1.5 Record `~/package.json` has 3 `@oh-my-pi/*` deps

## 2. Back up package-manager state

- [x] 2.1 Backed up `~/package.json` as `package.json.bun-backup-20260813_100505`
- [x] 2.2 Backed up `~/bun.lock` as `bun.lock.bun-backup-20260813_100505`

## 3. Remove Bun omp packages

- [x] 3.1 `cd ~ && bun remove @oh-my-pi/pi-coding-agent @oh-my-pi/pi-natives @oh-my-pi/pi-natives-darwin-arm64` — removed 3 packages
- [x] 3.2 Verify: `~/package.json` now has 5 deps, zero `@oh-my-pi/*` remnants
- [x] 3.3 Verify: `~/.bun/bin/omp` no longer exists
- [x] 3.4 Verify: `gitnexus`, `pyright`, `yaml-language-server` still installed

## 4. Verify Homebrew is sole installation

- [x] 4.1 Fresh shell: `command -v omp` → `/opt/homebrew/bin/omp`
- [x] 4.2 Fresh shell: `which -a omp | sort -u` → single path
- [x] 4.3 Fresh shell: `omp --version` → `omp/17.2.15`

## 5. Functional acceptance

- [x] 5.1 `omp --no-session -p "reply only: pong"` → pong, exit 0
- [x] 5.2 Default role: `cockpit/gpt-5.6-luna:high`

## 6. Configuration untouched

- [x] 6.1 `models.yml` hash: `e223d68e0598fdef178db9be02cc23f0` (unchanged)
- [x] 6.2 `config.yml` hash: `238154c5ec2c29deffb95ef3f725db25` (unchanged)
- [x] 6.3 Both files remain mode 644
- [x] 6.4 Role map unchanged

## 7. Closeout

- [x] 7.1 Strict validation passed
- [x] 7.2 Scoped diff check passed
- [x] 7.3 Homebrew-only binary resolution verified
- [x] 7.4 Functional acceptance passed
