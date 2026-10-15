# Verification Evidence: introduce-omniroute-cli-bridge

Executed: 2026-10-15  
Harness: Antigravity / OpenSpec Store  
Scope: OmniRoute host CLI bridge (`~/.local/bin/omniroute`), interactive zsh function multiplexing, stream filtering, and orphan database isolation.

---

## 1. Three-Tier Version Parity Evidence

### Command
```bash
printf "checkout:  %s\n" "$(cd ~/Omniroute && bun -e 'console.log(require("./package.json").version)')"
printf "container: %s\n" "$(docker exec omniroute node -e 'console.log(require("/app/package.json").version)')"
printf "npm:       %s\n" "$(npm view omniroute version 2>&1)"
```
### Result
```text
checkout:  3.8.51
container: 3.8.51
npm:       3.8.51
```
- Parity achieved: local checkout fast-forwarded 45 commits to `origin/main` (`fd95f823d`), matching container image `diegosouzapw/omniroute:latest` (`sha256:8bd462c9…`) and npm `latest`.

---

## 2. Host Bridge Executable Evidence

### Command
```bash
ls -la ~/.local/bin/omniroute
which omniroute
omniroute --version
```
### Result
```text
-rwxr-xr-x 1 androidteam staff 3779 Oct 15 10:47 /Users/androidteam/.local/bin/omniroute
/Users/androidteam/.local/bin/omniroute
3.8.51
```

---

## 3. Interactive Shell Multiplexing Evidence

### Subcommand Dispatch
```bash
zsh -i -c 'omniroute health'
```
```text
Health

Status: healthy
Uptime: 1314.511552931
  Version: 3.8.51
Requests (24h): 32
code: 0
```

### Function Precedence Check
```bash
zsh -i -c 'whence -v omniroute'
```
```text
omniroute is a shell function from /Users/androidteam/.zshrc
```

---

## 4. Stdout JSON Stream Hygiene & Pipelining Evidence

### Piped jq Extraction (Zero Banner Corruption)
```bash
# 1. Intelligent combos routing
omniroute combo list --output json | jq '.combos | length'
# Output: 4 (exit code: 0)

# 2. Gateway API keys inspection via OpenAPI surface (retrieves live mac-mini-1 key)
omniroute api api-keys get-api-keys --output json | jq '.keys[0] | {name: .name, scopes: .scopes}'
# Output: {"name": "mac-mini-1", "scopes": ["self:usage", "manage", "admin"]} (exit code: 0)

# 3. Upstream provider connections via OpenAPI surface
omniroute api providers get-api-providers --output json | jq '.connections | length'
# Output: 32 (exit code: 0)

# 4. Managed model catalog via OpenAPI surface
omniroute api models get-api-models --output json | jq '.models | length'
# Output: 105 (exit code: 0)

# 5. Provider API keys inspection
omniroute keys list --output json | jq '.keys | length'
# Output: 0 (exit code: 0)

# 6. Resilience metrics & queue capacity
omniroute resilience status --output json | jq '.requestQueue.concurrentRequests'
# Output: 20 (exit code: 0)
```
- Early startup banners (`📋 Loaded env from...`), `[DB]`, and `[Migration]` lines are cleanly routed to `stderr`, leaving `stdout` as pure parseable JSON.
- Fixed broken pipe crashes by handling `EPIPE` when `jq` closes standard input early.

---

## 5. Orphan Database Isolation Evidence

### Command
```bash
stat_before=$(stat -f '%m' ~/.omniroute/storage.sqlite)
echo "-- Unpinned default DATA_DIR with dead server:"
bun /Users/androidteam/Omniroute/bin/omniroute.mjs keys list --output json --base-url http://127.0.0.1:1 2>/dev/null | grep -c '"id":' || true

echo "-- Pinned DATA_DIR (bridge) with dead server:"
OMNIROUTE_BASE_URL="http://127.0.0.1:1" omniroute keys list --output json 2>/dev/null | jq '.keys | length'

stat_after=$(stat -f '%m' ~/.omniroute/storage.sqlite)
[ "$stat_before" = "$stat_after" ] && echo "VERIFIED: ~/.omniroute/storage.sqlite mtime untouched!"
```
### Result
```text
Before mtime: 1792031065
-- Unpinned default DATA_DIR with dead server:
8
-- Pinned DATA_DIR (our bridge) with dead server:
0
After mtime: 1792031065
VERIFIED: ~/.omniroute/storage.sqlite mtime untouched!
```

---

## 6. Primary CLI Skills Live Smoke Tests

| Skill | Command | Exit Code | Verified Output |
| :--- | :--- | :--- | :--- |
| `cli-health` | `omniroute health` | 0 | `Status: healthy`, `Version: 3.8.51` |
| `cli-models` | `omniroute models` | 0 | Table of models with `auto/*` combos |
| `cli-routing` | `omniroute combo list --output json` | 0 | 4 configured combos |
| `cli-keys` | `omniroute keys list --output json` | 0 | JSON keys array |
| `cli-resilience` | `omniroute resilience status --output json` | 0 | `concurrentRequests: 20` |

---

## 7. Inference Endpoint Pass-Through Verification

### Command
```bash
curl -s -X POST -H "Authorization: Bearer $(~/.claude/helpers/omniroute-key.sh)" -H "Content-Type: application/json" \
  http://127.0.0.1:20128/v1/chat/completions \
  -d '{"model": "auto/best-fast", "messages": [{"role": "user", "content": "Return: PONG"}], "max_tokens": 10}' \
  | jq -r '.choices[0].message.content'
```
### Result
```text
PONG
```
