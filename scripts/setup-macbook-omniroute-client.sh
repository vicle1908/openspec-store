#!/usr/bin/env bash
# setup-macbook-omniroute-client.sh — Idempotent Cross-Mac Tailscale & OmniRoute Client Setup
# Usage:
#   ~/Developer/scripts/setup-macbook-omniroute-client.sh --check   # Read-only audit of Tailscale, OmniRoute L4 TCP ports, and coding-agent configs
#   ~/Developer/scripts/setup-macbook-omniroute-client.sh --apply   # Backup (0600) + converge client configs to http://100.70.16.83:20128 / :20129
set -euo pipefail

export PATH="/opt/homebrew/bin:/opt/homebrew/sbin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"

MODE="check"
if [[ "${1:-}" == "--apply" ]]; then
  MODE="apply"
elif [[ "${1:-}" == "--check" || -z "${1:-}" ]]; then
  MODE="check"
else
  echo "Usage: $0 [--check | --apply]" >&2
  exit 1
fi

HOST_TS_IP="100.70.16.83"
CLIENT_TS_IP="100.106.143.78"
REAL_HOME="/Users/androidteam"
TARGET_HOME="${HOME}"
BACKUP_ROOT="${TARGET_HOME}/.omniroute/backups/configure-macbook-pro-m5-tailscale-omniroute-client"

log() {
  printf "[omniroute-client] %s\n" "$*" >&2
}

resolve_ts_bin() {
  local ts_bin
  ts_bin="$(command -v tailscale 2>/dev/null || true)"
  if [[ -z "${ts_bin}" && -x "/usr/local/bin/tailscale" ]]; then
    ts_bin="/usr/local/bin/tailscale"
  fi
  if [[ -z "${ts_bin}" || ! -x "${ts_bin}" ]]; then
    log "ERROR: tailscale CLI not found on PATH."
    return 1
  fi
  if [[ -L "${ts_bin}" ]]; then
    local real_target
    real_target="$(python3 -c 'import os,sys; print(os.path.realpath(sys.argv[1]))' "${ts_bin}")"
    if [[ "${real_target}" == *"/Applications/Tailscale.app/Contents/MacOS/Tailscale"* ]]; then
      log "ERROR: ${ts_bin} is a symlink to ${real_target} (must be a shell wrapper or standalone Go CLI so Bundle.main.bundleIdentifier does not crash)."
      return 1
    fi
  fi
  printf "%s\n" "${ts_bin}"
}

resolve_omniroute_key() {
  if [[ -n "${OMNIROUTE_API_KEY:-}" ]]; then
    printf "%s\n" "${OMNIROUTE_API_KEY}"
    return 0
  fi
  local zshenv_file="${TARGET_HOME}/.zshenv"
  if [[ ! -r "${zshenv_file}" && -r "${REAL_HOME}/.zshenv" ]]; then
    zshenv_file="${REAL_HOME}/.zshenv"
  fi
  if [[ -r "${zshenv_file}" ]]; then
    python3 - "${zshenv_file}" <<'PY'
import re, sys
txt = open(sys.argv[1]).read()
m = re.search(r"OMNIROUTE_API_KEY=[\"']?([^\"'\s]+)", txt)
if m:
    print(m.group(1))
PY
  fi
}

check_tailscale_and_serve() {
  local ts_bin
  ts_bin="$(resolve_ts_bin)"
  log "Verified Tailscale CLI binary/wrapper: ${ts_bin}."

  local status_json
  status_json="$("${ts_bin}" status --json)"

  local knobs_json
  knobs_json="$("${ts_bin}" debug control-knobs 2>/dev/null || echo '{}')"

  local role
  role="$(python3 -c '
import json, sys
st = json.loads(sys.argv[1])
knobs = json.loads(sys.argv[2])
bs = st.get("BackendState")
self_node = st.get("Self", {})
online = self_node.get("Online")
ips = self_node.get("TailscaleIPs", [])
expiry = self_node.get("KeyExpiry")
relay = self_node.get("Relay")
rand_port = knobs.get("RandomizeClientPort")
if bs != "Running" or not online:
    sys.exit(f"ERROR: Tailscale BackendState={bs}, Online={online}")
if expiry is not None:
    sys.exit(f"ERROR: KeyExpiry is {expiry} (expected null/Never)")
if rand_port is not True:
    sys.exit(f"ERROR: RandomizeClientPort is {rand_port} (expected True)")
if relay not in ("hkg", "tok"):
    sys.exit(f"ERROR: Self.Relay is {relay} (expected hkg or tok)")
is_local_host_node = ("100.70.16.83" in ips)
is_host = is_local_host_node and (sys.argv[3] == sys.argv[4])
print("host" if is_host else ("client_staged_on_host" if is_local_host_node else "client"))
' "${status_json}" "${knobs_json}" "${TARGET_HOME}" "${REAL_HOME}")"

  log "Tailscale node healthy (role=${role}, BackendState=Running, KeyExpiry=Never, RandomizeClientPort=true, Relay in {hkg,tok})."

  if [[ "${role}" == "host" || "${role}" == "client_staged_on_host" ]]; then
    local serve_json
    serve_json="$("${ts_bin}" serve status --json)"
    python3 -c '
import json, sys
s = json.loads(sys.argv[1])
tcp = s.get("TCP", {})
web = s.get("Web", {})
for port in ["20128", "20129", "20132", "3111"]:
    want = f"127.0.0.1:{port}"
    got = tcp.get(port, {}).get("TCPForward")
    if got != want:
        sys.exit(f"ERROR: Tailscale Serve TCP port {port} -> {got} (expected {want})")
for port in ["443", "8443"]:
    if not tcp.get(port, {}).get("HTTPS"):
        sys.exit(f"ERROR: Tailscale Serve HTTPS port {port} missing")
if not any(":443" in k for k in web) or not any(":8443" in k for k in web):
    sys.exit("ERROR: Tailscale Serve Web handlers missing :443 or :8443")
' "${serve_json}"
    log "Verified 6-port Tailscale Serve topology on host (20128, 20129, 20132, 3111 L4 TCP + 443, 8443 HTTPS)."
  else
    local client_serve_json
    client_serve_json="$("${ts_bin}" serve status --json)"
    python3 -c '
import json, sys
s = json.loads(sys.argv[1])
got = s.get("TCP", {}).get("3111", {}).get("TCPForward")
if got != "127.0.0.1:3111":
    sys.exit(f"ERROR: Client Tailscale Serve TCP port 3111 -> {got} (expected 127.0.0.1:3111)")
' "${client_serve_json}"
    log "Verified Client Tailscale Serve L4 TCP port 3111 -> 127.0.0.1:3111."
    log "Probing DERP/direct ping to ${HOST_TS_IP}..."
    "${ts_bin}" ping --until-direct=false -c 3 "${HOST_TS_IP}" >/dev/null
    log "Tailscale ping to ${HOST_TS_IP} succeeded."
  fi
  printf "%s\n" "${role%%_*}"
}

check_omniroute_endpoints() {
  local api_key
  api_key="$(resolve_omniroute_key)"
  if [[ -z "${api_key}" ]]; then
    log "ERROR: OMNIROUTE_API_KEY could not be resolved."
    return 1
  fi

  python3 - "${HOST_TS_IP}" "${api_key}" <<'PY'
import json, socket, sys, urllib.request

host, key = sys.argv[1], sys.argv[2]

req = urllib.request.Request(f"http://{host}:20128/v1/models", headers={"Authorization": f"Bearer {key}"})
with urllib.request.urlopen(req, timeout=10) as resp:
    data = json.loads(resp.read().decode())
    model_ids = {m.get("id") for m in data.get("data", [])}
    count = len(model_ids)
    required_combos = [
        "gemini-4-carbon",
        "gemini-4-carbon-high",
        "gemini-4-carbon-medium",
        "gemini-4-carbon-low",
        "gemini-4-argon",
        "gemini-4-argon-high",
        "gemini-4-argon-medium",
        "gemini-4-argon-low",
        "gemini-3.8-flash-high",
        "claude-opus-5.5",
        "claude-sonnet-5.5",
        "deepseek-v4.1-flash",
        "kimi-k3.1-pro",
        "muse-spark-1.3",
    ]
    missing_combos = [c for c in required_combos if c not in model_ids]
    if resp.status != 200 or count < 14 or missing_combos:
        sys.exit(f"ERROR: /v1/models status={resp.status}, count={count}, missing={missing_combos}")
    print(f"[omniroute-client] Verified http://{host}:20128/v1/models -> HTTP 200 ({count} models, all 14 required combos present).")

req_20129 = urllib.request.Request(f"http://{host}:20129/v1/models", headers={"Authorization": f"Bearer {key}"})
with urllib.request.urlopen(req_20129, timeout=10) as resp2:
    if resp2.status != 200:
        sys.exit(f"ERROR: :20129/v1/models returned {resp2.status}")
    print(f"[omniroute-client] Verified http://{host}:20129/v1/models -> HTTP 200.")

s = socket.create_connection((host, 20132), timeout=5)
s.close()
print(f"[omniroute-client] Verified tcp://{host}:20132 LiveWS listener -> socket connected.")
PY
}

audit_and_converge_ssh_and_sockets() {
  local ssh_cfg="${TARGET_HOME}/.ssh/config"
  if [[ "${MODE}" == "apply" ]]; then
    mkdir -p "${TARGET_HOME}/.ssh"
    chmod 700 "${TARGET_HOME}/.ssh"
    touch "${ssh_cfg}"
    chmod 600 "${ssh_cfg}"
    if ! grep -q "Host 100.70.16.83 iosteam-mac-mini\* 100.106.143.78" "${ssh_cfg}" 2>/dev/null; then
      cat >> "${ssh_cfg}" <<'EOF'

Host 100.70.16.83 iosteam-mac-mini* 100.106.143.78 100.101.64.56 macbook-pro*
    ServerAliveInterval 15
    ServerAliveCountMax 3
    TCPKeepAlive yes
EOF
      chmod 600 "${ssh_cfg}"
      log "Added Tailnet SSH keepalive block to ${ssh_cfg}."
    fi
  else
    if [[ -r "${ssh_cfg}" ]] && grep -q "ServerAliveInterval 15" "${ssh_cfg}"; then
      log "Verified SSH keepalive rules in ${ssh_cfg}."
    else
      log "WARN: SSH keepalive rules missing in ${ssh_cfg}."
      return 1
    fi
  fi

  local syn_sockets
  syn_sockets="$(lsof -n -P -iTCP 2>/dev/null | grep -E "100\.(106\.143\.78|101\.64\.56):6768 \(SYN_SENT\)" || true)"
  if [[ -n "${syn_sockets}" ]]; then
    log "NOTE: Detected background Orca SYN_SENT dialer to ${CLIENT_TS_IP}:6768 (peer currently asleep/offline)."
  fi
}

audit_or_apply_client_configs() {
  local role="$1"
  if [[ "${MODE}" == "apply" && "${role}" == "host" ]]; then
    log "ERROR: Refusing to run --apply on OmniRoute host (${HOST_TS_IP}) with HOME=${REAL_HOME}."
    return 1
  fi

  python3 - "${MODE}" "${role}" "${TARGET_HOME}" "${BACKUP_ROOT}" "${HOST_TS_IP}" <<'PY'
import hashlib, json, os, re, shutil, stat, sys

mode, role, home, backup_root, host_ip = sys.argv[1:6]

rel_files = [
    ".zshrc",
    ".claude/profiles/omniroute-pm.json",
    ".claude/profiles/cockpit.json",
    ".omp/agent/config.yml",
    ".omp/agent/models.yml",
    ".pi/agent/models.json",
    ".prime/agent/models.json",
    ".hermes/config.yaml",
    ".config/zed/settings.json",
    ".config/opencode/opencode.json",
    ".config/kilo/kilo.jsonc",
    ".config/goose/config.yaml",
    ".config/goose/custom_providers/custom_omniroute.json",
    ".codex/config.toml",
    ".codex/cockpit-model-catalog.json",
    ".config/muse/settings.json",
    ".qwen/settings.json",
    ".kimi-code/config.toml",
    ".grok/config.toml",
    ".factory/settings.json",
]

pattern = re.compile(r"http://(?:localhost|127\.0\.0\.1):(20128|20129)\b")
mfile = os.path.join(backup_root, "sha256-manifest.json")
manifest = {}
drift_count = 0
checked_count = 0

if mode == "apply":
    os.makedirs(backup_root, exist_ok=True)
    os.chmod(backup_root, 0o700)
    if os.path.isfile(mfile):
        manifest = json.loads(open(mfile, "r", encoding="utf-8").read())
for rel in rel_files:
    path = os.path.join(home, rel)
    if not os.path.isfile(path):
        continue
    checked_count += 1
    orig = open(path, "r", encoding="utf-8").read()

    if ":51006" in orig and f"http://{host_ip}:51006" in orig:
        sys.exit(f"ERROR: Corrupted :51006 URL in {path}")
    if ":3282" in orig and f"http://{host_ip}:3282" in orig:
        sys.exit(f"ERROR: Corrupted :3282 URL in {path}")

    if role == "host":
        if not pattern.search(orig) and f"http://{host_ip}:2012" not in orig:
            sys.exit(f"ERROR: Expected OmniRoute URL in {path}")
        continue

    updated = pattern.sub(rf"http://{host_ip}:\1", orig)
    if updated != orig:
        if mode == "check":
            print(f"[omniroute-client] DRIFT: {path} still contains localhost/127.0.0.1:20128 or :20129")
            drift_count += 1
        else:
            bpath = os.path.join(backup_root, rel.replace("/", "__") + ".bak")
            if not os.path.exists(bpath):
                shutil.copy2(path, bpath)
                os.chmod(bpath, 0o600)
            if rel not in manifest:
                digest = hashlib.sha256(orig.encode("utf-8")).hexdigest()
                manifest[rel] = {"backup": bpath, "sha256_before": digest}
            st_mode = stat.S_IMODE(os.stat(path).st_mode)
            with open(path, "w", encoding="utf-8") as f:
                f.write(updated)
            os.chmod(path, st_mode)
            print(f"[omniroute-client] Updated {path} -> http://{host_ip}:20128/:20129")

    after = updated if mode == "apply" else orig
    if rel == ".config/goose/config.yaml" and "OPENAI_BASE_PATH" in orig and "chat/completions" not in after:
        sys.exit("ERROR: goose config.yaml missing chat/completions transport exception")
    if rel == ".grok/config.toml" and "chat_completions" not in after:
        sys.exit("ERROR: grok config.toml missing chat_completions transport exception")
    if rel == ".zshrc" and "shopapikey" in orig and "https://api.phanmemvip.shop" not in after:
        sys.exit("ERROR: .zshrc shopapikey URL was altered")

if mode == "apply" and manifest:
    with open(mfile, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    os.chmod(mfile, 0o600)
    print(f"[omniroute-client] Wrote backup manifest ({len(manifest)} files) to {mfile}")

if mode == "check" and drift_count > 0:
    sys.exit(f"ERROR: {drift_count} file(s) have un-converged localhost OmniRoute URLs.")

print(f"[omniroute-client] Verified {checked_count} configuration file(s) (role={role}, mode={mode}).")
PY
}

ROLE="$(check_tailscale_and_serve)"
check_omniroute_endpoints
audit_and_converge_ssh_and_sockets
audit_or_apply_client_configs "${ROLE}"
log "SUCCESS (${MODE})"
