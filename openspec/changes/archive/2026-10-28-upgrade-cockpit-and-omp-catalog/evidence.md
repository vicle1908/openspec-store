# Evidence: upgrade-cockpit-and-omp-catalog

## Change Summary
- **Target**: Cockpit Tools (`/Applications/Cockpit Tools.app`), Homebrew Cask tap formula (`Casks/cockpit-tools.rb`), and Oh My Pi configuration (`~/.omp/agent/models.yml`).
- **Objective**: Upgrade Cockpit Tools from 1.3.74 to 1.3.75, synchronize the local tap formula to prevent downgrade drift, and update OMP's static model catalog to declare all 10 native text/coding models with accurate 272k context windows, 128k output ceilings, `input: [text]`, and schema-compliant reasoning levels (`low..max`).

## Verification Evidence

### 1. Bundle and Version Identification
- **Binary**: `/Applications/Cockpit Tools.app`
- **Installed Version**: `1.3.75` verified via `/usr/libexec/PlistBuddy -c "Print :CFBundleShortVersionString"`
- **Upstream Release Archive**: `Cockpit.Tools_1.3.75_universal.dmg` (SHA-256: `abc7c0ccd326cfb034310fe5c97350c9cdcb8a35ef12903f7ff8f89faa4adb5b`)
- **Quarantine Cleared**: Extended attributes stripped via `xattr -cr "/Applications/Cockpit Tools.app"`
- **Backup Snapshot**: Preserved at `/Applications/Cockpit Tools.app.bak-1.3.74` and `~/.antigravity_cockpit.bak-20261028`

### 2. Service & Port Listener Readiness
- **Listener**: TCP `127.0.0.1:51006` (`LISTEN`), process `cockpit-tools` PID `61162`
- **Models Endpoint**: `GET http://localhost:51006/v1/models` (Bearer `HERMES_CUSTOM_COCKPIT_API_KEY`) returns HTTP 200 with all 10 text/coding models plus specialized endpoint `gpt-image-2.5`.
- **New Model Verified**: `gpt-6.1-terra` verified present with `context_length: 272000` and capabilities `["completion", "tools", "thinking"]`.

### 3. Homebrew Tap Synchronization
- **Formula Path**: `/opt/homebrew/Library/Taps/jlcodes99/homebrew-cockpit-tools/Casks/cockpit-tools.rb`
- **Updated Version**: `version "1.3.75"`
- **Updated Checksum**: `sha256 "abc7c0ccd326cfb034310fe5c97350c9cdcb8a35ef12903f7ff8f89faa4adb5b"`

### 4. OMP Model Catalog & Schema Conformance
- **Configuration File**: `/Users/androidteam/.omp/agent/models.yml`
- **Registered Models**: Exactly 10 models under provider `cockpit`: `gpt-6.1-sol`, `gpt-6.1-terra`, `gpt-6-astra`, `gpt-6-sol`, `gpt-6-luna`, `gpt-5.6-sol`, `gpt-5.6-terra`, `gpt-5.6-luna`, `codex-auto-review`, `gpt-reserve`.
- **Context Ceiling**: Each model specifies `contextWindow: 272000` and `maxTokens: 128000`.
- **Modality**: Each model specifies `input: [text]`. Image generation endpoint `gpt-image-2.5` omitted.
- **Reasoning Levels**: Thinking effort lists strictly adhere to OMP schema: `[low, medium, high, xhigh, max]`.
- **OMP CLI Parsing**: `omp models cockpit --json` exits 0 and parses all 10 models correctly.

### 5. Fallback Resilience
- **Configuration File**: `/Users/androidteam/.omp/agent/config.yml`
- **Fallback Chain**: `retry.fallbackChains['cockpit/*']` configured with `['google-antigravity/gemini-4-argon:high', 'omniroute/gemini-3.8-flash-high:high', 'google-antigravity/gemini-3.8-flash:high']`.
- **Observable Delegation**: When Cockpit gateway responds with 503 (account cooldown), OMP automatically falls back across the chain without session termination.
