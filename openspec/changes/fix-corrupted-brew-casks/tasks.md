## 1. Pre-flight Checks

- [ ] 1.1 Confirm all 6 corrupted casks are identified and verify no other apps are affected — run `for app in /Applications/*.app; do [ ! -f "$app/Contents/Info.plist" ] && echo "CORRUPTED: $app"; done` and confirm only the expected 6 brew-managed apps appear (AutoForward Messages and Nicegram are non-brew, excluded from this fix)

## 2. Reinstall Corrupted Casks

- [ ] 2.1 Reinstall Orca: `brew reinstall --cask --force orca` — verify `/Applications/Orca.app/Contents/Info.plist` exists and `defaults read /Applications/Orca.app/Contents/Info.plist CFBundleExecutable` returns `Orca`
- [ ] 2.2 Reinstall Visual Studio Code: `brew reinstall --cask --force visual-studio-code` — verify `/Applications/Visual Studio Code.app/Contents/Info.plist` exists and `defaults read "/Applications/Visual Studio Code.app/Contents/Info.plist" CFBundleExecutable` returns `Code`
- [ ] 2.3 Reinstall Ollama: `brew reinstall --cask --force ollama-app` — verify `/Applications/Ollama.app/Contents/Info.plist` exists and `defaults read /Applications/Ollama.app/Contents/Info.plist CFBundleExecutable` returns `Ollama`
- [ ] 2.4 Reinstall Google Chrome: `brew reinstall --cask --force google-chrome` — verify `/Applications/Google Chrome.app/Contents/Info.plist` exists and `defaults read "/Applications/Google Chrome.app/Contents/Info.plist" CFBundleExecutable` returns `Google Chrome`
- [ ] 2.5 Reinstall Postman: `brew reinstall --cask --force postman` — verify `/Applications/Postman.app/Contents/Info.plist` exists and `defaults read /Applications/Postman.app/Contents/Info.plist CFBundleExecutable` returns `Postman`
- [ ] 2.6 Reinstall Warp: `brew reinstall --cask --force warp` — verify `/Applications/Warp.app/Contents/Info.plist` exists and `defaults read /Applications/Warp.app/Contents/Info.plist CFBundleExecutable` returns `stable`

## 3. Post-fix Verification

- [ ] 3.1 Run full scan: `for app in /Applications/*.app; do [ ! -f "$app/Contents/Info.plist" ] && echo "STILL CORRUPTED: $app"; done` — confirm no brew-managed apps remain corrupted
- [ ] 3.2 Run `brew doctor` and confirm no new warnings about Caskroom metadata or `.upgrading/` directories
