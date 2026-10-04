# Tasks

## 1. Upgrade Developer Tooling Casks

- [x] 1.1 Upgrade `copilot-cli` via `brew upgrade --cask copilot-cli` and verify version >= 1.0.91
- [x] 1.2 Upgrade `droid` via `brew upgrade --cask droid` and verify version >= 0.233.0
- [x] 1.3 Upgrade `zed` via `brew upgrade --cask zed` and verify version >= 1.22.0
- [x] 1.4 Upgrade `gcloud-cli` via `brew upgrade --cask gcloud-cli` and verify version >= 587.0.0
- [x] 1.5 Upgrade `postman-cli` via `brew upgrade --cask postman-cli` and verify version >= 1.69.0
- [x] 1.6 Upgrade remaining outdated casks (`google-drive`, `lark`, `teamviewer`)

## 2. Upstream Git Agent Fast-Forward

- [x] 2.1 Fast-forward merge `platform/prime-agent` to `origin/main` commit `c24ac227f`
- [x] 2.2 Verify `git -C platform/prime-agent status` reports clean and up to date

## 3. Verification and Evidence

- [x] 3.1 Verify upgraded tool binaries on `$PATH`: `copilot`, `droid`, `zed`, `gcloud`, `postman`
- [x] 3.2 Verify container daemons via `docker ps`
- [x] 3.3 Author `evidence.md` with verifiable output
