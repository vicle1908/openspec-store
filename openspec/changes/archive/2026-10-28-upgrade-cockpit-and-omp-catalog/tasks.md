# Tasks

## 1. Pre-flight Backup and Bundle Preparation

- [x] 1.1 Capture backup snapshot of current `/Applications/Cockpit Tools.app` to `/Applications/Cockpit Tools.app.bak-1.3.74`
- [x] 1.2 Capture backup snapshot of `~/.antigravity_cockpit` runtime state
- [x] 1.3 Download official `Cockpit.Tools_1.3.75_universal.dmg` release archive from `jlcodes99/cockpit-tools`

## 2. Cockpit Tools v1.3.75 Deployment & Homebrew Tap Sync

- [x] 2.1 Gracefully terminate active `cockpit-tools` process and verify port `51006` is released
- [x] 2.2 Mount release DMG, install new bundle to `/Applications/Cockpit Tools.app`, and strip quarantine extended attributes
- [x] 2.3 Synchronize local tap formula `/opt/homebrew/Library/Taps/jlcodes99/homebrew-cockpit-tools/Casks/cockpit-tools.rb` to version `1.3.75`
- [x] 2.4 Launch `/Applications/Cockpit Tools.app` and verify TCP `127.0.0.1:51006` listener is active
- [x] 2.5 Query `GET http://localhost:51006/v1/models` to confirm advertised models include `gpt-6.1-terra`

## 3. OMP Model Catalog Alignment

- [x] 3.1 Update `~/.omp/agent/models.yml` cockpit provider block with all 10 native chat/coding models and exclude `gpt-image-2.5`
- [x] 3.2 Set `contextWindow: 272000`, `maxTokens: 128000`, and `input: [text]` across all Cockpit models
- [x] 3.3 Configure full reasoning effort levels (`low..ultra`) and tool support on applicable models
- [x] 3.4 Verify `~/.omp/agent/config.yml` model roles and fallback chains maintain resilience

## 4. Smoke Verification and Acceptance

- [x] 4.1 Execute isolated OMP profile smoke test against `cockpit/gpt-6.1-sol` with fallbacks disabled
- [x] 4.2 Execute isolated OMP profile smoke test against new model `cockpit/gpt-6.1-terra`
- [x] 4.3 Verify response metadata reflects requested model attribution without 401 or compaction errors
- [x] 4.4 Remove temporary download and mount artifacts
