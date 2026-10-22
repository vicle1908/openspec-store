#!/usr/bin/env bash
# maccy-setup.sh — Reproducible Maccy (v2.7.1+) workstation setup, verification, and cross-Mac bootstrap
# Usage:
#   ~/Developer/scripts/maccy-setup.sh --check   # Read-only audit of cask, signature, TCC, login item, and preferences
#   ~/Developer/scripts/maccy-setup.sh --apply   # Install/converge Maccy preferences, login item, and restart daemon
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

BUNDLE_ID="org.p0deje.Maccy"
APP_PATH="/Applications/Maccy.app"
EXPECTED_TEAM_ID="MN3X4648SC"
CONTAINER_PLIST="${HOME}/Library/Containers/${BUNDLE_ID}/Data/Library/Preferences/${BUNDLE_ID}.plist"

log() {
  printf "[maccy-setup] %s\n" "$*"
}

has_login_item() {
  osascript -e 'tell application "System Events" to get name of every login item' 2>/dev/null \
    | tr ',' '\n' | sed 's/^[[:space:]]*//;s/[[:space:]]*$//' | grep -qx "Maccy"
}

verify_installation() {
  log "Checking Homebrew cask and application bundle..."
  if ! brew list --cask --versions maccy >/dev/null 2>&1; then
    if [[ "${MODE}" == "apply" ]]; then
      log "Installing Maccy via Homebrew Cask..."
      brew install --cask maccy
    else
      log "ERROR: Maccy Homebrew cask is not installed."
      return 1
    fi
  fi

  local cask_ver bundle_ver team_id
  cask_ver="$(brew list --cask --versions maccy | awk '{print $2}')"
  bundle_ver="$(defaults read "${APP_PATH}/Contents/Info.plist" CFBundleShortVersionString 2>/dev/null || echo "missing")"
  log "Installed cask=${cask_ver}, bundle=${bundle_ver}"

  codesign --verify --deep --strict "${APP_PATH}"
  team_id="$(codesign -dv "${APP_PATH}" 2>&1 | awk -F= '/^TeamIdentifier=/{print $2}')"
  if [[ "${team_id}" != "${EXPECTED_TEAM_ID}" ]]; then
    log "ERROR: Unexpected TeamIdentifier '${team_id}' (expected '${EXPECTED_TEAM_ID}')."
    return 1
  fi
  log "Code signature valid (TeamIdentifier=${team_id})."
}

verify_tcc_permissions() {
  log "Checking macOS TCC permissions (${BUNDLE_ID})..."
  local tcc_db="/Library/Application Support/com.apple.TCC/TCC.db"
  if [[ -r "${tcc_db}" ]]; then
    local rows
    rows="$(sqlite3 "file:${tcc_db}?mode=ro" \
      "SELECT service || '=' || auth_value FROM access WHERE client='${BUNDLE_ID}' AND client_type=0 ORDER BY service;" 2>/dev/null || true)"
    if [[ -n "${rows}" ]]; then
      log "System TCC grants: $(echo "${rows}" | tr '\n' ' ')"
    else
      log "NOTE: No bundle row found in system TCC.db; verify System Settings > Privacy & Security > Accessibility."
    fi
  else
    log "NOTE: System TCC.db not readable by current parent process; verify Accessibility in System Settings."
  fi
}

apply_preferences() {
  # On a fresh Mac, initialize the App Sandbox container before writing defaults
  if [[ ! -d "$(dirname "${CONTAINER_PLIST}")" ]]; then
    log "Initializing App Sandbox container on first install..."
    open -g -a "${APP_PATH}"
    sleep 2
  fi

  log "Stopping Maccy before writing preferences..."
  if pgrep -x "Maccy" >/dev/null 2>&1; then
    killall Maccy 2>/dev/null || true
    sleep 1
  fi

  log "Applying Maccy preferences (${BUNDLE_ID})..."

  # Core History, Search & Paste Ergonomics
  defaults write "${BUNDLE_ID}" historySize -int 999
  defaults write "${BUNDLE_ID}" pasteByDefault -bool true
  defaults write "${BUNDLE_ID}" removeFormattingByDefault -bool true
  defaults write "${BUNDLE_ID}" searchMode -string "mixed"
  defaults write "${BUNDLE_ID}" highlightMatch -string "color"
  defaults write "${BUNDLE_ID}" clearSystemClipboard -bool false
  defaults write "${BUNDLE_ID}" suppressClearAlert -bool false
  defaults write "${BUNDLE_ID}" ignoreEvents -bool false
  defaults write "${BUNDLE_ID}" ignoreOnlyNextEvent -bool false
  defaults write "${BUNDLE_ID}" SUEnableAutomaticChecks -bool true

  # Appearance & Maccy 2.7+ Visual Enhancements
  defaults write "${BUNDLE_ID}" showSearch -bool true
  defaults write "${BUNDLE_ID}" showTitle -bool true
  defaults write "${BUNDLE_ID}" showFooter -bool true
  defaults write "${BUNDLE_ID}" showApplicationIcons -bool true
  defaults write "${BUNDLE_ID}" showRecentCopyInMenuBar -bool true
  defaults write "${BUNDLE_ID}" showHexColorSwatch -bool true
  defaults write "${BUNDLE_ID}" showSpecialSymbols -bool true
  defaults write "${BUNDLE_ID}" imageMaxHeight -int 80
  defaults write "${BUNDLE_ID}" previewDelay -int 700
  defaults write "${BUNDLE_ID}" previewWidth -float 400

  # Carbon Keyboard Shortcuts:
  # - Popup:          Cmd+Shift+C      (carbonModifiers: 768,  carbonKeyCode: 8)
  # - Pin:            Option+P         (carbonModifiers: 2048, carbonKeyCode: 35)
  # - Delete:         Option+Backspace (carbonModifiers: 2048, carbonKeyCode: 51)
  # - Toggle Preview: Control+Space    (carbonModifiers: 4096, carbonKeyCode: 49)
  defaults write "${BUNDLE_ID}" KeyboardShortcuts_popup -string '{"carbonModifiers":768,"carbonKeyCode":8}'
  defaults write "${BUNDLE_ID}" KeyboardShortcuts_pin -string '{"carbonKeyCode":35,"carbonModifiers":2048}'
  defaults write "${BUNDLE_ID}" KeyboardShortcuts_delete -string '{"carbonKeyCode":51,"carbonModifiers":2048}'
  defaults write "${BUNDLE_ID}" KeyboardShortcuts_togglePreview -string '{"carbonKeyCode":49,"carbonModifiers":4096}'

  # Unrestricted Pasteboard Capture Types (Text, Rich Text, HTML, Images, Files)
  defaults write "${BUNDLE_ID}" enabledPasteboardTypes -array \
    "public.png" \
    "public.tiff" \
    "public.utf8-plain-text" \
    "public.file-url" \
    "public.jpeg" \
    "public.html" \
    "public.heic" \
    "public.rtf"

  # No Application Restrictions
  defaults write "${BUNDLE_ID}" ignoredApps -array

  # Transient / Password-Generator Pasteboard Type Filters
  defaults write "${BUNDLE_ID}" ignoredPasteboardTypes -array \
    "net.antelle.keeweb" \
    "com.agilebits.onepassword" \
    "Pasteboard generator type" \
    "de.petermaurer.TransientPasteboardType" \
    "com.apple.is-remote-clipboard" \
    "com.typeit4me.clipping"

  # Secret Sanitization Regular Expressions (NSRegularExpression validated)
  # Note: Strings starting with '(' must be wrapped in <string>...</string> for `defaults write -array`
  # so macOS NextStep plist parser does not treat '(?s)...' as an array tuple.
  defaults write "${BUNDLE_ID}" ignoreRegexp -array \
    '<string>(?s)-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----.*?-----END (?:RSA |EC |OPENSSH )?PRIVATE KEY-----</string>' \
    '<string>(?im)^\s*(?:export\s+)?(?:[A-Z0-9_]+_)?(?:PASSWORD|PASSWD|SECRET|TOKEN|API[_-]?KEY|PRIVATE[_-]?KEY)(?:_[A-Z0-9_]+)?\s*[:=]\s*["'\'']?[^\s"'\'']{8,}["'\'']?\s*$</string>'

  killall cfprefsd 2>/dev/null || true

  if ! has_login_item; then
    log "Registering Maccy in macOS Login Items..."
    osascript -e 'tell application "System Events" to make login item at end with properties {path:"/Applications/Maccy.app", hidden:false}' >/dev/null
  fi

  log "Launching Maccy..."
  open -a "${APP_PATH}"
  sleep 1
}

verify_preferences() {
  log "Verifying active preferences, login item, and process state..."
  if [[ ! -f "${CONTAINER_PLIST}" ]]; then
    log "ERROR: Sandboxed container plist missing at ${CONTAINER_PLIST}"
    return 1
  fi
  plutil -lint "${CONTAINER_PLIST}" >/dev/null

  local hist_size search_mode paste_def rm_fmt hex_swatch spec_sym regexp_dump
  hist_size="$(defaults read "${BUNDLE_ID}" historySize 2>/dev/null || echo "unset")"
  search_mode="$(defaults read "${BUNDLE_ID}" searchMode 2>/dev/null || echo "unset")"
  paste_def="$(defaults read "${BUNDLE_ID}" pasteByDefault 2>/dev/null || echo "unset")"
  rm_fmt="$(defaults read "${BUNDLE_ID}" removeFormattingByDefault 2>/dev/null || echo "unset")"
  hex_swatch="$(defaults read "${BUNDLE_ID}" showHexColorSwatch 2>/dev/null || echo "unset")"
  spec_sym="$(defaults read "${BUNDLE_ID}" showSpecialSymbols 2>/dev/null || echo "unset")"
  regexp_dump="$(defaults read "${BUNDLE_ID}" ignoreRegexp 2>/dev/null || echo "")"

  log "Preferences: historySize=${hist_size}, searchMode=${search_mode}, pasteByDefault=${paste_def}, removeFormattingByDefault=${rm_fmt}, showHexColorSwatch=${hex_swatch}, showSpecialSymbols=${spec_sym}"

  if [[ "${hist_size}" != "999" || "${search_mode}" != "mixed" || "${paste_def}" != "1" || "${rm_fmt}" != "1" || "${hex_swatch}" != "1" || "${spec_sym}" != "1" ]]; then
    log "ERROR: Preference drift detected against workstation profile."
    return 1
  fi

  if [[ "${regexp_dump}" != *"PRIVATE KEY"* || "${regexp_dump}" != *"PASSWORD"* ]]; then
    log "ERROR: ignoreRegexp missing expected secret sanitization rules."
    return 1
  fi

  if ! has_login_item; then
    log "ERROR: Maccy is not registered in macOS Login Items."
    return 1
  fi

  if pgrep -x "Maccy" >/dev/null 2>&1; then
    log "Process status: RUNNING (PID $(pgrep -x Maccy | tr '\n' ' '))"
  else
    log "ERROR: Maccy process is not running."
    return 1
  fi
}

verify_installation
if [[ "${MODE}" == "apply" ]]; then
  apply_preferences
fi
verify_tcc_permissions
verify_preferences
log "Maccy workstation verification complete [MODE=${MODE}]."
