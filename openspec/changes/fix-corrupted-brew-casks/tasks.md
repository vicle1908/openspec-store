## 1. Pre-flight Checks

- [x] 1.1 Confirm all corrupted casks are identified and categorize them — run `for app in /Applications/*.app; do [ ! -f "$app/Contents/Info.plist" ] && echo "CORRUPTED: $app"; done` and verify the 8 corrupted apps: 5 brew casks (VS Code, Ollama, Chrome, Postman, Warp), 1 Stably AI Orca, 2 sideloaded iOS apps (AutoForward Messages, Nicegram)

## 2. Reinstall Corrupted Homebrew Casks

- [x] 2.1 ~~Reinstall Orca~~ — SKIPPED: Homebrew `orca` cask is Plotly Orca (different app); user's Orca is Stably AI Orca. Handled in Phase 4.
- [x] 2.2 Reinstall Visual Studio Code: `brew reinstall --cask --force visual-studio-code` — verify `/Applications/Visual Studio Code.app/Contents/Info.plist` exists and `defaults read "/Applications/Visual Studio Code.app/Contents/Info.plist" CFBundleExecutable` returns `Code`
- [x] 2.3 Reinstall Ollama: `brew reinstall --cask --force ollama-app` — verify `/Applications/Ollama.app/Contents/Info.plist` exists and `defaults read /Applications/Ollama.app/Contents/Info.plist CFBundleExecutable` returns `Ollama`
- [x] 2.4 Reinstall Google Chrome: `brew reinstall --cask --force google-chrome` — verify `/Applications/Google Chrome.app/Contents/Info.plist` exists and `defaults read "/Applications/Google Chrome.app/Contents/Info.plist" CFBundleExecutable` returns `Google Chrome`
- [x] 2.5 Reinstall Postman: `brew reinstall --cask --force postman` — verify `/Applications/Postman.app/Contents/Info.plist` exists and `defaults read /Applications/Postman.app/Contents/Info.plist CFBundleExecutable` returns `Postman`
- [x] 2.6 Reinstall Warp: `brew reinstall --cask --force warp` — verify `/Applications/Warp.app/Contents/Info.plist` exists and `defaults read /Applications/Warp.app/Contents/Info.plist CFBundleExecutable` returns `stable`

## 3. Post-fix Verification (Homebrew Casks)

- [x] 3.1 Run full scan: `for app in /Applications/*.app; do [ ! -f "$app/Contents/Info.plist" ] && echo "STILL CORRUPTED: $app"; done` — confirm no brew-managed apps remain corrupted
- [x] 3.2 Run `brew doctor` and confirm no new warnings about Caskroom metadata or `.upgrading/` directories for the 5 fixed casks

## 4. Restore Stably AI Orca

- [ ] 4.1 Verify the Orca bundle in `.upgrading/` is complete: `ls -la /opt/homebrew/Caskroom/orca/1.4.196.upgrading/Orca.app/Contents/MacOS/Orca` and `defaults read /opt/homebrew/Caskroom/orca/1.4.196.upgrading/Orca.app/Contents/Info.plist CFBundleIdentifier` returns `com.stablyai.orca`
- [ ] 4.2 Remove the corrupted empty shell: `rm -rf /Applications/Orca.app`
- [ ] 4.3 Copy the complete bundle: `cp -R "/opt/homebrew/Caskroom/orca/1.4.196.upgrading/Orca.app" /Applications/Orca.app`
- [ ] 4.4 Verify restoration: `defaults read /Applications/Orca.app/Contents/Info.plist CFBundleIdentifier` returns `com.stablyai.orca` and `defaults read /Applications/Orca.app/Contents/Info.plist CFBundleShortVersionString` returns `1.4.197`
- [ ] 4.5 Clean up the stale Caskroom entry: `rm -rf /opt/homebrew/Caskroom/orca/`

## 5. Sideloaded iOS Apps (Manual Guidance)

- [ ] 5.1 **AutoForward Messages** (`com.autoforward.teleforwarder` v1.0.55): Corrupted — `Wrapper/Runner.app/Info.plist` exists but `Runner` executable is missing. **Action required:** Reinstall from the original source (developer site or AltStore/Sideloadly). App data in `~/Library/Containers/D483BCEB-39D6-40E1-8F55-1B0614B23EDA/` is preserved.
- [ ] 5.2 **Nicegram** (`app.nicegram` v2.5.9): Corrupted — `Wrapper/Telegram.app/Info.plist` exists but `Telegram` executable is missing. **Action required:** Reinstall from the App Store (Nicegram is available on the Mac App Store) or from the developer's site. App data in `~/Library/Containers/2CFF69EF-513E-4FF9-8CB6-AC5A0A05C214/` is preserved.
- [ ] 5.3 After reinstalling sideloaded apps, verify: `for app in "AutoForward Messages" "Nicegram"; do test -f "/Applications/$app.app/Contents/Info.plist" || test -f "/Applications/$app.app/Wrapper/Runner.app/Info.plist" || test -f "/Applications/$app.app/Wrapper/Telegram.app/Info.plist" && echo "✓ $app: bundle present" || echo "✗ $app: still missing"; done`

## 6. Final Verification

- [ ] 6.1 Run full scan one more time: `for app in /Applications/*.app; do [ ! -f "$app/Contents/Info.plist" ] && [ ! -f "$app/Wrapper/Runner.app/Info.plist" ] && [ ! -f "$app/Wrapper/Telegram.app/Info.plist" ] && echo "STILL CORRUPTED: $app"; done` — confirm zero corrupted apps remain
- [ ] 6.2 Run `brew doctor` — confirm no Caskroom metadata warnings for any of the 6 brew-managed apps
