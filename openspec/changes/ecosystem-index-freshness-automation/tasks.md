# Tasks: Ecosystem Index Freshness Automation

## 1. Create workspace refresh script

Create `~/Developer/scripts/refresh-knowledge-indexes.sh` that:
- Discovers repos with `.gitnexus/` or `graphify-out/` under `~/Developer/`
- Runs `gitnexus analyze . --index-only --default-branch main` for GitNexus repos
- Runs `graphify update .` for Graphify repos
- Uses lockfile for concurrency safety
- Logs to `~/Developer/.knowledge-refresh/refresh.log`
- Skips repos in merge/rebase state
- Handles missing CLIs gracefully (skip + warning)

### 1.1 Create log directory

Create `~/Developer/.knowledge-refresh/` directory.

### 1.2 Implement lockfile mechanism

Non-blocking lockfile at `/tmp/knowledge-refresh.lock` with stale detection.

### 1.3 Implement repo discovery

Find repos by checking for `.gitnexus/` and `graphify-out/` directories.

### 1.4 Implement GitNexus refresh

Run `gitnexus analyze . --index-only --default-branch main` with timeout and error handling.

### 1.5 Implement Graphify refresh

Run `graphify update .` with timeout and error handling.

### 1.6 Implement logging

Timestamped entries with repo name, tool, status, duration.

## 2. Create status command

Create `~/Developer/scripts/knowledge-status.sh` that reports freshness across all repos.

### 2.1 Implement status discovery

Same discovery as refresh script.

### 2.2 Implement freshness check

For each repo, check indexed revision vs current HEAD.

### 2.3 Implement formatted output

Table output with repo, tool, last refresh, freshness status.

## 3. Create LaunchAgent

Create `~/Library/LaunchAgents/com.developer.index-refresh.plist` for nightly execution.

### 3.1 Write plist file

Nightly schedule at 02:30 local time with KeepAlive on crash.

### 3.2 Load and verify LaunchAgent

Load the agent and verify it fires correctly.

## 4. Update documentation

### 4.1 Fix AGENTS.md

Remove stale "Weekly crons: graphify freshness (Mon 8AM), wiki lint (Mon 9AM)" claim. Add actual LaunchAgent description.

### 4.2 Update CLAUDE.md

Update staleness warnings to reference the automated refresh mechanism.

## 5. Extend existing spec

Add automation requirements to `openspec/specs/refresh-gitnexus-index-groups/spec.md`.

## Verification

- [ ] `~/Developer/scripts/refresh-knowledge-indexes.sh` runs successfully on all repos
- [ ] `~/Developer/scripts/knowledge-status.sh` reports freshness correctly
- [ ] LaunchAgent loads with `launchctl load ~/Library/LaunchAgents/com.developer.index-refresh.plist`
- [ ] Manual trigger works: `launchctl start com.developer.index-refresh`
- [ ] Log file is created and contains timestamped entries
- [ ] Overlapping runs are prevented by lockfile
- [ ] Missing CLI (gitnexus/graphify) doesn't crash the script
- [ ] AGENTS.md no longer contains stale cron claims
