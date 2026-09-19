# Tasks: Workstation Health and Tooling Maintenance

## 1. Package Managers & Runtime Upgrades

- [x] 1.1 Upgrade global npm packages and verify registry dist-tags (`npm@12.0.2`, `codex`, `openspec`, `cline`, `gitnexus`)
- [x] 1.2 Verify Bun runtime is on latest upstream release (`v1.4.2`)
- [x] 1.3 Upgrade pnpm to latest release via Corepack (`11.23.0` -> `12.4.2`)
- [x] 1.4 Upgrade outdated Homebrew casks and formulae (`copilot-cli`, `droid`, `gcloud-cli`, `postman-cli`, `intellij-idea`)
- [x] 1.5 Clean package manager build caches (`uv cache clean`, `~/.npm/_npx`)

## 2. Unmanaged Application & CLI Migration

- [x] 2.1 Inventory installed unmanaged applications in `/Applications`
- [x] 2.2 Migrate eligible standalone applications to Homebrew casks (`discord`, `zalo`, `lark`, `instantview`, `hermes-desktop`, `google-drive`)
- [x] 2.3 Migrate standalone `/usr/local/bin` CLI tools to native Homebrew formulae (`gitlab-runner`, `fastlane`, `openspec`)
- [x] 2.4 Re-link and repair damaged Homebrew caskroom/cellar packages (`cockpit-tools`, `antigravity-cli`, `goose`)

## 3. Storage Reclamation & Safety Gate Verification

- [x] 3.1 Audit reclaimable storage across system and developer directories
- [x] 3.2 Partition cleanup candidates into Tier 1 (safe caches), Tier 2 (review-first), and Tier 3 (protected stateful assets)
- [x] 3.3 Obtain explicit operator approval for Tier 1 and Tier 2 candidate paths
- [x] 3.4 Execute approved deletions and verify >30 GiB net storage reclamation (reclaimed ~36 GiB, capacity 91% -> 83%)
- [x] 3.5 Verify critical Tier 3 assets remain untouched (`Docker.raw`, named database volumes, Chrome profiles, `.venv`s)

## 4. LaunchAgent & Daemon Health Remediation

- [x] 4.1 Audit listening ports and identify non-zero exit status user LaunchAgents
- [x] 4.2 Remediate `com.tdt.webhook-receiver` missing `.venv/bin/uvicorn` binary via `uv sync`
- [x] 4.3 Remediate `Antigravity Tools` binary name discrepancy via bundle symlink
- [x] 4.4 Verify `com.omniroute.update-check` image digest verification logic
- [x] 4.5 Verify `workstation-tool-update.sh` preflight check passes with exit code 0

## 5. System Health & Workspace Cleanliness Audit

- [x] 5.1 Audit macOS kernel, security posture (SIP, Gatekeeper, FileVault), and memory pressure
- [x] 5.2 Audit developer workspace git repositories (cleanliness, branch conventions, stashes)
- [x] 5.3 Verify OpenSpec store validation (`openspec validate --all`: 411 items passed)
- [x] 5.4 Reconcile knowledge-refresh inventory and verify SHA-256 approval digests
