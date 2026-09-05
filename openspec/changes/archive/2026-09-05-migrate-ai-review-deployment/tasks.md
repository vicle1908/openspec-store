## Tasks

- [x] **1. Capture pre-migration evidence**
  - Save the current plist: `cp ~/Library/LaunchAgents/com.tdt.ai-review.plist ~/Developer/tdt/deployments/ai-review/pre-migration-com.tdt.ai-review.plist`
  - Record process status: `launchctl list | grep tdt.ai-review` and `ps aux | grep ai-review`
  - Record port 8090: `lsof -i :8090 | head -5`
  - Verify current source directory structure: `ls -la ~/Developer/tdt/deployments/ai-review/{app,deps,bin,state}/`
  - **Verification**: Pre-migration plist backup exists, process is running, port 8090 is listening

- [x] **2. Copy deployment directories to `~/.tdt/deployments/ai-review/`**
  - Create target shell: `mkdir -p ~/.tdt/deployments/ai-review/{app,deps,bin,state}`
  - Copy app: `cp -a ~/Developer/tdt/deployments/ai-review/app/ ~/.tdt/deployments/ai-review/app/`
  - Copy deps: `cp -a ~/Developer/tdt/deployments/ai-review/deps/ ~/.tdt/deployments/ai-review/deps/`
  - Copy bin: `cp -a ~/Developer/tdt/deployments/ai-review/bin/ ~/.tdt/deployments/ai-review/bin/`
  - Copy state: `cp -a ~/Developer/tdt/deployments/ai-review/state/ ~/.tdt/deployments/ai-review/state/`
  - **Verification**: `diff -rq ~/Developer/tdt/deployments/ai-review/{app,deps,bin,state} ~/.tdt/deployments/ai-review/{app,deps,bin,state}` returns no differences (excluding `.venv`)

- [x] **3. Update hardcoded paths in `deps/agent-harness/pyproject.toml`**
  - Replace uv.sources paths in `~/.tdt/deployments/ai-review/deps/agent-harness/pyproject.toml`:
    - `path = "/Users/androidteam/Developer/tdt/deployments/ai-review/deps/agent-core"` → `path = "/Users/androidteam/.tdt/deployments/ai-review/deps/agent-core"`
    - `path = "/Users/androidteam/Developer/tdt/deployments/ai-review/deps/tdt-core"` → `path = "/Users/androidteam/.tdt/deployments/ai-review/deps/tdt-core"`
  - Use: `sed -i '' 's|/Users/androidteam/Developer/tdt/deployments/ai-review/deps/|/Users/androidteam/.tdt/deployments/ai-review/deps/|g' ~/.tdt/deployments/ai-review/deps/agent-harness/pyproject.toml`
  - **Verification**: `grep -n 'Developer/tdt' ~/.tdt/deployments/ai-review/deps/agent-harness/pyproject.toml` returns zero matches; `grep -n '.tdt/deployments' ~/.tdt/deployments/ai-review/deps/agent-harness/pyproject.toml` shows both source paths updated

- [x] **4. Update hardcoded path in `bin/ai-review-launcher.sh`**
  - Replace the `.venv/bin/uvicorn` path in the `exec` line:
    - `sed -i '' 's|/Users/androidteam/Developer/tdt/deployments/ai-review/app/.venv|/Users/androidteam/.tdt/deployments/ai-review/app/.venv|g' ~/.tdt/deployments/ai-review/bin/ai-review-launcher.sh`
  - **Verification**: `grep 'exec ' ~/.tdt/deployments/ai-review/bin/ai-review-launcher.sh` shows the new path; `grep -c 'Developer/tdt' ~/.tdt/deployments/ai-review/bin/ai-review-launcher.sh` returns 0

- [x] **5. Run `uv sync` at new location**
  - `cd ~/.tdt/deployments/ai-review/app && uv sync`
  - Verify the venv was created: `ls ~/.tdt/deployments/ai-review/app/.venv/bin/python`
  - Verify certifi cacert.pem exists at the expected path referenced by the plist: `test -f ~/.tdt/deployments/ai-review/app/.venv/lib/python3.14/site-packages/certifi/cacert.pem && echo OK`
  - **Verification**: `.venv/` exists with python binary, uvicorn binary, and certifi cacert.pem all present

- [x] **6. Write fresh LaunchAgent plist**
  - Write `~/Library/LaunchAgents/com.tdt.ai-review.plist` with all paths pointing to `~/.tdt/deployments/ai-review/`:
    - ProgramArguments: `~/.tdt/deployments/ai-review/bin/ai-review-launcher.sh`
    - WorkingDirectory: `~/.tdt/deployments/ai-review/app`
    - StandardOutPath: `~/.tdt/deployments/ai-review/logs/ai-review.stdout.log`
    - StandardErrorPath: `~/.tdt/deployments/ai-review/logs/ai-review.stderr.log`
    - PATH: `.venv/bin` prefix under new path
    - SSL_CERT_FILE / REQUESTS_CA_BUNDLE: certifi path under new `.venv`
  - Verify plist is valid XML: `plutil -lint ~/Library/LaunchAgents/com.tdt.ai-review.plist`
  - **Verification**: `plutil -lint` returns OK; `grep -c 'Developer/tdt' ~/Library/LaunchAgents/com.tdt.ai-review.plist` returns 0; all 7 path references use `~/.tdt/deployments/ai-review/`

- [x] **7. Restart service and verify health**
  - Unload old service: `launchctl bootout gui/$(id -u) ~/Library/LaunchAgents/com.tdt.ai-review.plist 2>/dev/null; sleep 2`
  - Ensure old process is dead: `kill $(lsof -ti :8090) 2>/dev/null; sleep 1`
  - Load new service: `launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.tdt.ai-review.plist`
  - Wait and poll for health: `for i in 1 2 3 4 5 6 7 8 9 10; do curl -sf http://127.0.0.1:8090/health && break; sleep 3; done`
  - Record process status: `launchctl list | grep tdt.ai-review`
  - Record port: `lsof -i :8090 | head -5`
  - **Verification**: curl returns 200, launchctl shows PID and exit status 0, port 8090 is listening, stderr log is clean

- [x] **8. Save post-migration evidence and commit**
  - Save post-migration plist: `cp ~/Library/LaunchAgents/com.tdt.ai-review.plist ~/.tdt/deployments/ai-review/post-migration-com.tdt.ai-review.plist`
  - Save health check output to `~/.tdt/deployments/ai-review/state/migration-evidence.txt` with: timestamp, process PID, port status, curl health output
  - Commit state directory: `cd ~/.tdt/deployments/ai-review && git init && git add state/ && git commit -m "ai-review: pre-migration state snapshot"`
  - **Verification**: evidence file exists with timestamp and health data; git log shows the commit
