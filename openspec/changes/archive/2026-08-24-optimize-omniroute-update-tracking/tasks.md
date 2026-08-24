## 1. Create check-upstream.sh

- [x] 1.1 Write `~/Omniroute/scripts/check-upstream.sh` (compare local vs remote digest via Docker Hub API, write flag file + log + macOS notification)
- [x] 1.2 Make executable: `chmod +x ~/Omniroute/scripts/check-upstream.sh`
- [x] 1.3 Test manually: run the script, verify flag file created at `~/.omniroute/update-available`, verify log entry in `~/.omniroute/update-check.log`

## 2. Create update.sh

- [x] 2.1 Write `~/Omniroute/scripts/update.sh` (snapshot → pull → deploy → verify → log → clear flag → notify)
- [x] 2.2 Make executable: `chmod +x ~/Omniroute/scripts/update.sh`
- [x] 2.3 Test: run the script, verify snapshot created in `~/.omniroute/snapshots/`, container updated, healthy, login works, flag cleared

## 3. Create LaunchAgent

- [x] 3.1 Write `~/Library/LaunchAgents/com.omniroute.update-check.plist` (StartInterval 43200, runs check-upstream.sh)
- [x] 3.2 Load: `launchctl bootout gui/$(id -u)/com.omniroute.update-check 2>/dev/null; launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.omniroute.update-check.plist`
- [x] 3.3 Verify: `launchctl list | grep omniroute.update` shows the agent loaded

## 4. Update Documentation

- [x] 4.1 Update `openspec-store/openspec/config.yaml` OmniRoute section: document the tracking mechanism + update workflow
- [x] 4.2 Update memory `omniroute-docker-deployment.md`: add update tracking facts

## 5. Archive

- [x] 5.1 `openspec validate optimize-omniroute-update-tracking --type change --strict --store openspec-store`
- [x] 5.2 `openspec archive optimize-omniroute-update-tracking --store openspec-store --yes`
- [x] 5.3 Commit archived change dir + config.yaml only
