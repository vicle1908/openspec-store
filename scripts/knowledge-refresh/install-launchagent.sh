#!/bin/bash
# install-launchagent.sh — Install the knowledge-refresh LaunchAgent
#
# Reads the plist template, substitutes @HOME@ with the actual home directory,
# validates with plutil, and installs to ~/Library/LaunchAgents/.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TEMPLATE="$SCRIPT_DIR/com.developer.index-refresh.plist.template"
INSTALL_DIR="$HOME/Library/LaunchAgents"
PLIST_NAME="com.developer.index-refresh.plist"
INSTALL_PATH="$INSTALL_DIR/$PLIST_NAME"
LAUNCHAgent_LOG_DIR="$HOME/Developer/.knowledge-refresh"

LABEL="com.developer.index-refresh"
UID_NUM=$(id -u)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
info()  { printf "  [info]  %s\n" "$*"; }
ok()    { printf "  [ok]    %s\n" "$*"; }
fail()  { printf "  [FAIL]  %s\n" "$*" >&2; }

# ---------------------------------------------------------------------------
# Preflight
# ---------------------------------------------------------------------------
if [[ ! -f "$TEMPLATE" ]]; then
    fail "Template not found: $TEMPLATE"
    exit 1
fi

# Ensure the LaunchAgents directory exists
mkdir -p "$INSTALL_DIR"

# Ensure the log directory exists so launchd can write logs
mkdir -p "$LAUNCHAgent_LOG_DIR"

# ---------------------------------------------------------------------------
# Render template → temporary plist
# ---------------------------------------------------------------------------
TMP_PLIST=$(mktemp "${INSTALL_PATH}.tmp.XXXXXX")
trap 'rm -f "$TMP_PLIST"' EXIT

# Replace every @HOME@ with the real home directory
sed "s|@HOME@|$HOME|g" "$TEMPLATE" > "$TMP_PLIST"

info "Rendered template → $TMP_PLIST"

# ---------------------------------------------------------------------------
# Validate with plutil
# ---------------------------------------------------------------------------
if ! plutil -lint "$TMP_PLIST"; then
    fail "plutil validation failed — not installing."
    exit 1
fi
ok "plutil validation passed."

# ---------------------------------------------------------------------------
# Unload any existing LaunchAgent (ignore errors if not loaded)
# ---------------------------------------------------------------------------
if launchctl print "gui/$UID_NUM/$LABEL" &>/dev/null; then
    info "Unloading existing agent: $LABEL"
    launchctl bootout "gui/$UID_NUM/$LABEL" 2>/dev/null || true
    sleep 1
fi

# ---------------------------------------------------------------------------
# Install plist
# ---------------------------------------------------------------------------
cp "$TMP_PLIST" "$INSTALL_PATH"
chmod 600 "$INSTALL_PATH"
ok "Installed to $INSTALL_PATH"

# ---------------------------------------------------------------------------
# Bootstrap with launchctl
# ---------------------------------------------------------------------------
info "Bootstrapping LaunchAgent: $LABEL"
if launchctl bootstrap "gui/$UID_NUM" "$INSTALL_PATH" 2>/dev/null; then
    ok "LaunchAgent bootstrapped successfully."
else
    # Bootstrap may fail if already loaded; fall back to enable
    info "Bootstrap returned non-zero — attempting enable."
    if launchctl enable "gui/$UID_NUM/$LABEL" 2>/dev/null; then
        ok "LaunchAgent enabled."
    else
        fail "Could not bootstrap or enable the LaunchAgent."
        exit 1
    fi
fi

# ---------------------------------------------------------------------------
# Verify
# ---------------------------------------------------------------------------
if launchctl print "gui/$UID_NUM/$LABEL" &>/dev/null; then
    ok "Verification: agent is loaded and active."
else
    fail "Verification: agent does NOT appear loaded."
    exit 1
fi

echo ""
echo "Knowledge-refresh LaunchAgent installed."
echo "  Label:   $LABEL"
echo "  Plist:   $INSTALL_PATH"
echo "  Runs:    daily at 02:30"
echo "  Logs:    $LAUNCHAgent_LOG_DIR/"
echo ""
echo "Useful commands:"
echo "  launchctl print gui/$UID_NUM/$LABEL        # inspect"
echo "  launchctl bootout gui/$UID_NUM/$LABEL       # unload"
echo "  launchctl bootstrap gui/$UID_NUM $INSTALL_PATH  # reload"
