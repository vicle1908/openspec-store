# Evidence

## 1. Diagnostic Baseline (Pre-Recovery)

- **Cockpit Tools UI (`v1.4.2`, window `24462`, PID `29831`)**:
  - Attempting **Switch and launch** for `Antigravity` (`v2.34.0`, `/Applications/Antigravity.app/Contents/MacOS/Antigravity`, account `baohiendung326@gmail.com` `ULTRA`) failed with:
    - `写入 macOS Keychain 失败: security: SecKeychainItemModifyContent: The user name or passphrase you entered is not correct.`
    - `security: SecKeychainItemCreateFromContent (<default>): The user name or passphrase you entered is not correct.`
- **System-Wide `login.keychain-db` Probes**:
  - `security list-keychains -d user` → `"/Users/androidteam/Library/Keychains/login.keychain-db"`
  - `SecKeychainGetStatus` (`Security.framework`) → `rc=0`, `status bits: 0x7` (`kSecUnlockStateStatus | kSecReadPermStatus | kSecWritePermStatus`)
  - `security show-keychain-info ~/Library/Keychains/login.keychain-db` (`SecKeychainCopySettings`) → `errSecAuthFailed` (`-25293`)
  - `security find-generic-password -s "gemini" -a "antigravity" -w` → exit `16751923` (`-25293`)
  - `security find-generic-password -s "Chrome Safe Storage" -w` → exit `16751923` (`-25293`)
  - `security add-generic-password -U -s "__omp_keychain_probe__" -a "probe" -w "test"` → `SecKeychainItemCreateFromContent (<default>): The user name or passphrase you entered is not correct.` (`-25293`)
- **`securityd` Unified Log (`log show`)**:
  - `securityd` (`PID 15590`, restarted after `loginwindow` `PID 205` from Oct 22): `0x78dacded00(0x10165ef10) is unlocked; decoding for makeUnlocked()` → `MacOS error: -25337` → `CSSMERR_CSP_INVALID_DATA (-2147415994)` → `CSSMERR_CSP_OPERATION_AUTH_DENIED (-2147416032)` / `CSSMERR_DL_OPERATION_AUTH_DENIED (-2147413984)`.

## 2. Recovery & Post-Recovery Verification

- **Operator Keychain Unlock**:
  - Executed `security lock-keychain ~/Library/Keychains/login.keychain-db` and `security unlock-keychain ~/Library/Keychains/login.keychain-db`.
  - Post-recovery `security show-keychain-info ~/Library/Keychains/login.keychain-db` → `Keychain "/Users/androidteam/Library/Keychains/login.keychain-db" no-timeout`.
- **Cockpit Tools Switch Only (`computer-use`)**:
  - Clicked **Switch only** (`[ref=e32]`) in `Choose client` modal; modal closed with zero errors, banner reported `Switched to baohiendung326@gmail.com` (`Current`, `Switch time: 11/23/2026 04:51 PM`).
  - `security find-generic-password -s "gemini" -a "antigravity"` confirmed `mdat` updated to `20261123095139Z`.
- **Cockpit Tools Switch and Launch with Antigravity 2.0 (`v2.34.0`, `computer-use`)**:
  - Clicked **Switch account** (`[ref=e153]`) → **Switch and launch** (`[ref=e186]`).
  - `~/.antigravity_cockpit/logs/app.log.2026-11-23` (`16:53:51–16:53:52`): closed prior Antigravity `PID 70529`, logged `[Antigravity 2.0] 系统凭据与桌面回退凭据写入完成`, and sent `open -n -a`.
  - Verified Antigravity window `25827` (`PID 75977`, `language_server --override_ide_version 2.34.0` `PID 76017`) running via `computer.windows()` screenshot and `pgrep`.
