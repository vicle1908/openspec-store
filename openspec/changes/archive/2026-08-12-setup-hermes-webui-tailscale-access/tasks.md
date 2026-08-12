# Tasks: setup-hermes-webui-tailscale-access

## 1. Pre-flight

- [x] 1.1 Confirm macOS 26.6.1 ARM64, Python 3.13 available via Homebrew
- [x] 1.2 Confirm Tailscale installed, authenticated, both Mac and iPhone on same tailnet
- [x] 1.3 Confirm port 8787 occupied by Docker adapter (claude-code-provider-adapter)

## 2. Clone and install Hermes WebUI

- [x] 2.1 Clone hermes-webui to ~/Developer/hermes-webui
- [x] 2.2 Create Python 3.13 venv (.venv) and install requirements.txt
- [x] 2.3 Create mode-600 .env with host, port, Python path, password, and forwarded-proto settings

## 3. Free port 8787

- [x] 3.1 Stop Docker adapter container (docker stop)
- [x] 3.2 Remap docker-compose.yml host port 8787→8788 (container port stays 8787)
- [x] 3.3 Recreate adapter container on host port 8788 (docker compose up -d --force-recreate)
- [x] 3.4 Verify adapter healthy on 127.0.0.1:8788
- [x] 3.5 Update adapter-status.sh default to use ADAPTER_URL for host port 8788
- [x] 3.6 Update ~/.claude/profiles/cockpit.json ANTHROPIC_BASE_URL to localhost:8788
- [x] 3.7 Update ~/.omp/agent/models.yml cockpit baseUrl to localhost:8788

## 4. Enable password authentication

- [x] 4.1 Set HERMES_WEBUI_PASSWORD in .env (secrets.token_urlsafe(32))
- [x] 4.2 Set HERMES_WEBUI_TRUST_FORWARDED_PROTO=1 in .env
- [x] 4.3 Set .env permissions to 600
- [x] 4.4 Verify LaunchAgent plist contains no password

## 5. Start Hermes and verify

- [x] 5.1 Start via bootstrap.py --no-browser --skip-agent-install --foreground
- [x] 5.2 Verify Python (not Docker) owns 127.0.0.1:8787
- [x] 5.3 Verify /health returns status=ok
- [x] 5.4 Verify unauthenticated / returns 302→/login
- [x] 5.5 Verify unauthenticated /api/sessions returns 401
- [x] 5.6 Verify correct password login returns 200 + cookie
- [x] 5.7 Verify authenticated /api/sessions returns 200
- [x] 5.8 Verify wrong password returns 401

## 6. Configure Tailscale Serve

- [x] 6.1 Run tailscale serve --bg 8787
- [x] 6.2 Verify serve status shows HTTPS hostname → 127.0.0.1:8787
- [x] 6.3 Verify DNS resolves iosteam-mac-mini.tailc6b508.ts.net → 100.70.16.83

## 7. Install LaunchAgent for auto-start

- [x] 7.1 Create ~/Library/LaunchAgents/com.victory1908.hermes-webui.plist
- [x] 7.2 Validate with plutil -lint
- [x] 7.3 Load via launchctl load -w
- [x] 7.4 Verify launchd state=running, owns port 8787
- [x] 7.5 Verify persistence: kill TERM → launchd restarts new PID

## 8. iPhone acceptance verification

iPhone device-side acceptance has been transferred to a dedicated follow-up
change: `verify-hermes-webui-iphone-access`. The setup change is considered
complete for all server-side infrastructure.

### Server-side infrastructure (completed)

- [x] 8.1 iPhone connected to Tailscale, verify connected (3 pongs via DERP, 168-372ms)

### Device-side acceptance (transferred to verify-hermes-webui-iphone-access)

- [x] 8.2 Create follow-up change for Safari and Hermex device acceptance
