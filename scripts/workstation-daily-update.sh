#!/usr/bin/env bash
# ==============================================================================
# Workstation Daily Maintenance & Tooling Update Runner
# Consolidated check-and-update pipeline across Homebrew, Bun, filtered npm,
# uv tools, coding agent CLIs, skills parity, skill-content refresh, and
# OpenSpec store validation.
#
# Skill-content refresh notes (change: automate-skill-content-refresh):
#   • `skills update` has NO --dry-run/--check/--json. Unknown flags are ignored
#     and a REAL update is executed, so never pass such a flag expecting a dry
#     run. Its only non-mutating drift signal is the summary line it prints
#     BEFORE writing: `Found N update(s)` (global) / `Refreshing N skill(s)`.
#   • A path-ambiguous upstream entry (same skill published at >1 path, e.g.
#     docfork-docs) is reported by the CLI as "Multiple current paths match …
#     skipping them". That is INFORMATIONAL, not stale/broken/failed.
#   • Drift is never judged from the skills-lock.json `computedHash` digest: it
#     is CLI-internal and is not reproducible for multi-file skills.
#   • The refresh stage reports five outcomes in one line, e.g.
#       drift=1 refreshed=42 already_current=0 path_ambiguous=1 failed=0
#     meaning: drift available / entries refreshed / already current /
#     path-ambiguous skips / refresh failures. Drift availability is reported
#     BEFORE any content is replaced, so 'checked, nothing changed' is
#     distinguishable from 'checked and pulled new content'.
#   • Bounds: the refresh runs under SKILL_REFRESH_TIMEOUT (1800s) and each
#     agent updater under AGENT_UPDATE_TIMEOUT (900s). A timeout returns 124 and
#     is reported as a failure (refresh_failed / agent FAILED) rather than
#     stalling the job. Refresh failure DEGRADES the run and is reported in the
#     final summary; it does not abort later stages.
#   • Agent updates: an updater that exits 0 while printing an error (observed:
#     `kilo update` → "Error: Failed to change directory to …") is reported as
#     FAILED, because exit status alone is not evidence of an update.
#   • Manual reproduction: run
#       bash ~/Developer/scripts/workstation-daily-update.sh --check
#     to exercise every stage without applying updates.
# ==============================================================================

set -euo pipefail
umask 022

export HOME="${HOME:-/Users/androidteam}"
export PATH="${HOME}/.npm-global/bin:${HOME}/.bun/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:${HOME}/.local/bin"
export STORE_DIR="${HOME}/Developer/platform/openspec-store"
export WORKSPACE_DIR="${HOME}/Developer"

MODE="apply"
if [[ "${1:-}" == "--check" ]]; then
  MODE="check"
fi

LOG_FILE="${HOME}/Library/Logs/workstation-daily-update.log"
mkdir -p "$(dirname "${LOG_FILE}")"

# Bounds (seconds)
SKILL_REFRESH_TIMEOUT=1800   # 30 min for the whole skills-update invocation
AGENT_UPDATE_TIMEOUT=900     # 15 min per agent CLI updater

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

# Strip ANSI CSI/erase sequences and carriage returns.
strip_ansi() {
  sed -E $'s/\033\\[[0-9;]*[A-Za-z]//g; s/\033\\[[0-9;]*K//g' | tr -d '\r'
}

# PID-aware timeout: macOS-native alternative to GNU timeout (absent by default
# on macOS). Mirrors the proven helper in scripts/knowledge-refresh/.
# Usage: run_with_timeout <seconds> <command> [args...]
# Returns: child exit status, or 124 on timeout.
run_with_timeout() {
  local seconds="$1"
  shift

  local output pid elapsed=0 rc=0
  output="$(mktemp "${TMPDIR:-/tmp}/workstation-timeout.XXXXXX")"

  "$@" >"$output" 2>&1 &
  pid=$!

  while kill -0 "$pid" 2>/dev/null; do
    if (( elapsed >= seconds )); then
      kill -TERM "$pid" 2>/dev/null || true
      sleep 5
      kill -KILL "$pid" 2>/dev/null || true
      wait "$pid" 2>/dev/null || true
      cat "$output"
      rm -f "$output"
      return 124
    fi
    sleep 1
    elapsed=$((elapsed + 1))
  done

  wait "$pid" || rc=$?
  cat "$output"
  rm -f "$output"
  return "$rc"
}

# Classify captured `skills update` output into the five spec outcomes.
# Echoes: "drift=N refreshed=N already_current=N path_ambiguous=N failed=N".
# A nonzero exit (incl. timeout 124) always wins as a failure.
classify_refresh() {
  local clean="$1" rc="${2:-0}"
  local drift=0 refreshed=0 already=0 ambiguous=0 failed=0

  # Drift available BEFORE mutation.
  if grep -qE 'Found [0-9]+ (global )?update|Refreshing [0-9]+ skill' <<<"$clean"; then
    drift=1
  fi

  # Refreshed count: project scope prints a tally, global prints per-skill lines.
  if grep -qE 'Updated [0-9]+ skill' <<<"$clean"; then
    refreshed="$(grep -oE 'Updated [0-9]+ skill' <<<"$clean" | grep -oE '[0-9]+' | head -1)"
  elif grep -qE '^[[:space:]]*✓ Updated [^0-9]' <<<"$clean"; then
    refreshed="$(grep -cE '^[[:space:]]*✓ Updated [^0-9]' <<<"$clean")"
  fi

  # Path-ambiguous entries (informational, never a failure on their own).
  if grep -qE 'Multiple current paths match' <<<"$clean"; then
    ambiguous="$(grep -cE '^[[:space:]]*[[:punct:]] ' <<<"$clean" || true)"
    (( ambiguous == 0 )) && ambiguous=1
  fi

  # Failure: nonzero exit, or no recognizable summary of any kind.
  if (( rc != 0 )); then
    failed=1
  elif ! grep -qE 'Updated [0-9]+ skill|Found [0-9]+ (global )?update|Refreshing [0-9]+ skill|Multiple current paths match|^[[:space:]]*✓ Updated ' <<<"$clean"; then
    failed=1
  fi

  # Already current: recognized summary, no drift, nothing refreshed, no skips.
  if (( failed == 0 )) && (( drift == 0 )) && (( refreshed == 0 )) && (( ambiguous == 0 )); then
    already=1
  fi

  printf 'drift=%d refreshed=%d already_current=%d path_ambiguous=%d failed=%d\n' \
    "$drift" "$refreshed" "$already" "$ambiguous" "$failed"
}

# Refresh upstream skill content into the canonical store.
# Reports the five outcomes and records them. Never fails the pipeline: a
# transient network fault or timeout must not suppress later stages.
refresh_skill_content() {
  local raw rc=0

  raw="$(cd "${WORKSPACE_DIR}" && run_with_timeout "${SKILL_REFRESH_TIMEOUT}" \
    skills update -y 2>&1)" || rc=$?

  local clean
  clean="$(printf '%s' "$raw" | strip_ansi)"

  local result
  result="$(classify_refresh "$clean" "$rc")"
  echo "    ${result}"

  local drift refreshed already ambiguous failed
  drift="$(sed -nE 's/.*drift=([0-9]+).*/\1/p' <<<"$result")"
  refreshed="$(sed -nE 's/.*refreshed=([0-9]+).*/\1/p' <<<"$result")"
  already="$(sed -nE 's/.*already_current=([0-9]+).*/\1/p' <<<"$result")"
  ambiguous="$(sed -nE 's/.*path_ambiguous=([0-9]+).*/\1/p' <<<"$result")"
  failed="$(sed -nE 's/.*failed=([0-9]+).*/\1/p' <<<"$result")"

  REFRESH_REFRESHED="${refreshed}"
  REFRESH_ALREADY="${already}"
  REFRESH_AMBIGUOUS="${ambiguous}"
  REFRESH_FAILED="${failed}"

  if (( failed == 1 )); then
    if (( rc == 124 )); then
      echo "    REFRESH FAILED: skills update exceeded ${SKILL_REFRESH_TIMEOUT}s bound (terminated)"
    else
      echo "    REFRESH FAILED: skills update returned rc=${rc} (upstream unreachable or output unrecognized)"
    fi
  elif (( drift == 1 )); then
    echo "    drift available: yes; refreshed ${refreshed} entr(y/ies)"
  else
    echo "    drift available: no; all upstream content already current"
  fi

  if (( ambiguous > 0 )); then
    echo "    path-ambiguous (informational, not stale/broken/failed): ${ambiguous} entr(y/ies)"
    grep -E 'Multiple current paths match' <<<"$clean" | sed 's/^/      /' || true
  fi

  # Deliberate asymmetry with the parity stage: report, do not abort.
  return 0
}

# Declared covered set of agent CLIs with a scriptable update verb.
# Format: "<bin>:<label>:<update args>". `droid` is intentionally excluded
# (native binary, no discoverable update subcommand) and is reported uncovered.
AGENT_CLI_COVERED="claude:Claude Code:update
codex:OpenAI Codex:update
opencode:OpenCode:upgrade
auggie:Auggie:update --skip-confirmation
qoder:Qoder:update
pi:Pi:update --self"

AGENT_CLI_KNOWN_UNCOVERED="droid goose grok prime-agent happy cursor-agent hermes-agent buzz cce kilo"

# Update every covered agent CLI that is installed; report the declared set and
# any installed agent CLI left uncovered. Each updater is time-bounded.
agent_cli_coverage() {
  local deny_roster="${1:-${DENY_ROSTER:-}}"
  local paused_roster="${2:-${PAUSED_ROSTER:-}}"
  echo "    covered set: $(cut -d: -f1 <<<"${AGENT_CLI_COVERED}" | paste -sd, -)"

  local bin label args
  while IFS=: read -r bin label args; do
    [[ -z "${bin}" ]] && continue
    if ! command -v "${bin}" &>/dev/null; then
      echo "      - ${label} (${bin}): not installed, skipped"
      continue
    fi

    # Pre-mutation safety and policy guards
    if (( GLOBAL_PAUSE != 0 )); then
      echo "      - ${label} (${bin}): update paused by policy (DISABLE_UPDATES), skipped"
      continue
    fi
    local is_paused=0 p_item
    if [[ -n "${paused_roster}" ]]; then
      while IFS= read -r p_item; do
        [[ -z "${p_item}" ]] && continue
        if [[ "${bin}" == "${p_item}" ]]; then
          is_paused=1
          break
        fi
      done <<<"${paused_roster}"
    fi
    if (( is_paused != 0 )); then
      echo "      - ${label} (${bin}): update paused by policy (DISABLE_UPDATES), skipped"
      continue
    fi
    local is_denied=0 d_item
    while IFS= read -r d_item; do
      [[ -z "${d_item}" ]] && continue
      if [[ "${bin}" == "${d_item}" ]]; then
        is_denied=1
        break
      fi
    done <<<"${deny_roster}"
    if (( is_denied != 0 )); then
      echo "      - ${label} (${bin}): SKIPPED (authority gate: tool in deny roster due to drift, target misalignment, or conflict)"
      continue
    fi

    local real_bin
    real_bin="$(realpath "$(command -v "${bin}")" 2>/dev/null || which "${bin}")"
    if [[ "${bin}" == "codex" ]] && [[ "${real_bin}" != "${HOME}/.npm-global"* ]]; then
      echo "      - ${label} (${bin}): SKIPPED (target prefix misalignment: active binary resolves to ${real_bin} outside declared prefix ${HOME}/.npm-global)"
      continue
    fi

    local pre_real=""
    pre_real="$(realpath "$(command -v "${bin}")" 2>/dev/null || which "${bin}" 2>/dev/null || true)"
    local v_before="" v_after=""
    v_before="$("${bin}" --version 2>&1 | head -1 | strip_ansi || true)"

    local out rc=0
    # shellcheck disable=SC2086  # ${args} intentionally word-splits into argv
    out="$(run_with_timeout "${AGENT_UPDATE_TIMEOUT}" "${bin}" ${args} 2>&1)" || rc=$?
    out="$(printf '%s' "$out" | strip_ansi)"
    printf '%s\n' "$out" | tail -3 | sed 's/^/        /'

    # Some agents exit 0 while printing an error and doing nothing,
    # so exit status alone is not sufficient evidence of a successful update.
    # Anchored to explicit error markers at the start of a line to avoid
    # matching a benign mention of these words in a progress line.
    if (( rc == 124 )); then
      echo "      - ${label} (${bin}): FAILED (exceeded ${AGENT_UPDATE_TIMEOUT}s bound)"
      AGENT_FAILED=1
    elif (( rc != 0 )); then
      echo "      - ${label} (${bin}): FAILED (rc=${rc})"
      AGENT_FAILED=1
    elif grep -qiE '^[[:space:]]*(error|fatal)[: ]|failed to [a-z]' <<<"$out"; then
      echo "      - ${label} (${bin}): FAILED (rc=0 but reported an error)"
      AGENT_FAILED=1
    else
      v_after="$("${bin}" --version 2>&1 | head -1 | strip_ansi || true)"
      local active_path active_real=""
      active_path="$(command -v "${bin}" 2>/dev/null || true)"
      if [[ -n "${active_path}" ]]; then
        active_real="$(realpath "${active_path}" 2>/dev/null || which "${bin}" 2>/dev/null || true)"
      fi
      local known_root=""
      for root_cand in "${HOME}/.npm-global" "${HOME}/.pi" "${HOME}/.local" "/opt/homebrew"; do
        if [[ -n "${pre_real}" && "${pre_real}" == "${root_cand}"* ]]; then
          known_root="${root_cand}"
          break
        fi
      done
      if [[ -z "${v_after}" ]] || grep -qiE '^[[:space:]]*(error|fatal)[: ]|failed' <<<"${v_after}"; then
        echo "      - ${label} (${bin}): FAILED (post-update version probe empty or reported error: '${v_after}')"
        AGENT_FAILED=1
      elif [[ ! -x "${active_real}" ]]; then
        echo "      - ${label} (${bin}): FAILED (post-update active executable missing or not executable: ${active_real})"
        AGENT_FAILED=1
      elif [[ -n "${known_root}" && "${active_real}" != "${known_root}"* ]]; then
        echo "      - ${label} (${bin}): FAILED (post-update active executable outside known active root ${known_root}: ${active_real})"
        AGENT_FAILED=1
      elif [[ -n "${v_before}" && "${v_before}" == "${v_after}" ]]; then
        echo "      - ${label} (${bin}): update completed; local version unchanged (${v_after}) [active: ${active_path} -> ${active_real}] (idempotent, currency unverified)"
      else
        echo "      - ${label} (${bin}): updated (${v_before} -> ${v_after}) [active: ${active_path} -> ${active_real}] (local version changed, currency unverified)"
      fi
    fi
  done <<<"${AGENT_CLI_COVERED}"

  # Report any installed agent CLI outside the declared set.
  local known
  for known in ${AGENT_CLI_KNOWN_UNCOVERED}; do
    if command -v "${known}" &>/dev/null; then
      echo "      - uncovered: ${known} (installed, managed by Homebrew or package manager)"
    fi
  done
}

# Declared script provenance manifest (executed path, recorded path, authority).
SCRIPT_MANIFEST="${STORE_DIR}/config/script-provenance-manifest.tsv"

# Compare each executed script against its recorded mirror by CONTENT digest.
# Content only: mode and mtime are deliberately ignored, so a chmod is not drift.
# Never writes to either copy; reporting drift must not repair it.
# Sets SCRIPT_DRIFT (0 = none, 1 = drift or missing record) and counts.
detect_script_drift() {
  SCRIPT_DRIFT=0
  SCRIPT_DRIFT_COUNT=0
  SCRIPT_MISSING_COUNT=0
  SCRIPT_CHECKED=0

  if [[ ! -r "${SCRIPT_MANIFEST}" ]]; then
    echo "      - manifest not readable: ${SCRIPT_MANIFEST}"
    SCRIPT_DRIFT=1
    return 0
  fi

  local exec_path rec_path _authority
  while IFS=$'\t' read -r exec_path rec_path _authority; do
    # Skip comments and blank lines
    [[ -z "${exec_path}" || "${exec_path}" == \#* ]] && continue

    local name
    name="$(basename "${exec_path}")"

    if [[ ! -f "${exec_path}" ]]; then
      echo "      - ${name}: MISSING executed copy (${exec_path})"
      SCRIPT_MISSING_COUNT=$((SCRIPT_MISSING_COUNT + 1))
      SCRIPT_DRIFT=1
      continue
    fi

    if [[ "${rec_path}" == "-" || -z "${rec_path}" ]]; then
      echo "      - ${name}: NO RECORDED COPY"
      SCRIPT_MISSING_COUNT=$((SCRIPT_MISSING_COUNT + 1))
      SCRIPT_DRIFT=1
      continue
    fi

    local rec_abs="${STORE_DIR}/${rec_path}"
    if [[ ! -f "${rec_abs}" ]]; then
      echo "      - ${name}: recorded copy absent (${rec_path})"
      SCRIPT_MISSING_COUNT=$((SCRIPT_MISSING_COUNT + 1))
      SCRIPT_DRIFT=1
      continue
    fi

    SCRIPT_CHECKED=$((SCRIPT_CHECKED + 1))

    # Content digest only. shasum reads bytes; mode/owner/mtime are ignored.
    local exec_digest rec_digest
    exec_digest="$(shasum -a 256 "${exec_path}" 2>/dev/null | awk '{print $1}')"
    rec_digest="$(shasum -a 256 "${rec_abs}" 2>/dev/null | awk '{print $1}')"

    if [[ -z "${exec_digest}" || -z "${rec_digest}" ]]; then
      echo "      - ${name}: could not digest one or both copies"
      SCRIPT_DRIFT=1
      SCRIPT_DRIFT_COUNT=$((SCRIPT_DRIFT_COUNT + 1))
      continue
    fi

    if [[ "${exec_digest}" == "${rec_digest}" ]]; then
      echo "      - ${name}: in sync"
    else
      echo "      - ${name}: DRIFTED (executed ${exec_digest:0:12} != recorded ${rec_digest:0:12})"
      SCRIPT_DRIFT=1
      SCRIPT_DRIFT_COUNT=$((SCRIPT_DRIFT_COUNT + 1))
    fi
  done <"${SCRIPT_MANIFEST}"

  echo "    checked=${SCRIPT_CHECKED} drifted=${SCRIPT_DRIFT_COUNT} missing_record=${SCRIPT_MISSING_COUNT}"
  return 0
}

run_pipeline() {
  echo "======================================================================"
  echo "$(date '+%Y-%m-%d %H:%M:%S %Z') — Workstation Daily Update [MODE=${MODE}]"
  echo "======================================================================"
  if [[ "${MODE}" == "check" ]]; then
    export HOMEBREW_NO_AUTO_UPDATE=1
    export HOMEBREW_NO_INSTALL_CLEANUP=1
  fi

  # Pre-flight Authority & Mutation Safety Check
  PREFLIGHT_FAILED=0
  DENY_ROSTER=""
  DENY_ROSTER_BREW_FORMULAE=""
  DENY_ROSTER_BREW_CASKS=""
  DENY_ROSTER_NPM=""
  PAUSED_ROSTER=""
  GLOBAL_PAUSE=0
  if [[ -f "${STORE_DIR}/scripts/inventory-workstation-toolchain.py" ]]; then
    local pre_out pre_rc=0
    pre_out="$(python3 "${STORE_DIR}/scripts/inventory-workstation-toolchain.py" --json 2>/dev/null)" || pre_rc=$?
    if (( pre_rc == 0 )) && [[ -n "${pre_out}" ]]; then
      local parse_rc=0
      parse_out="$(python3 -c '
import sys, json, os
sys.path.insert(0, sys.argv[1])
from toolchain_updater_registry import is_truthy_pause, is_global_pause_active
try:
    data = json.load(sys.stdin)
    items = data["authority_reconciliation"].get("items", [])
    deny_all, deny_brew_formulae, deny_brew_casks, deny_npm, paused = [], [], [], [], []
    global_pause = is_global_pause_active()
    for it in items:
        name = it.get("name")
        if not name:
            continue
        drift = it.get("drift_status")
        writer = it.get("writer", "")
        auth = it.get("authority", "")
        chan = it.get("selected_channel", "") or ""
        if drift in ("unknown", "target_misalignment", "conflict"):
            deny_all.append(name)
            if "cask" in auth or "cask" in writer or "cask" in chan:
                deny_brew_casks.append(name)
            elif "formula" in auth or "brew" in writer or "brew" in auth:
                deny_brew_formulae.append(name)
            if "npm" in writer or "npm" in auth:
                deny_npm.append(name)
        auto_cfg = it.get("auto_updates_config", {})
        for k in ("DISABLE_UPDATES", "env.DISABLE_UPDATES", "DISABLE_AUTOUPDATER", "env.DISABLE_AUTOUPDATER"):
            val = auto_cfg.get(k)
            if is_truthy_pause(val):
                paused.append(name)
                global_pause = True
                break
    print("STATUS:" + data["authority_reconciliation"].get("status", "unknown"))
    print("GLOBAL_PAUSE:" + ("1" if global_pause else "0"))
    print("ALL:")
    for x in deny_all: print(x)
    print("BREW_FORMULAE:")
    for x in deny_brew_formulae: print(x)
    print("BREW_CASKS:")
    for x in deny_brew_casks: print(x)
    print("NPM:")
    for x in deny_npm: print(x)
    print("PAUSED:")
    for x in paused: print(x)
except Exception:
    sys.exit(1)
' "${STORE_DIR}/scripts" <<<"${pre_out}")" || parse_rc=$?

      if (( parse_rc == 0 )) && [[ -n "${parse_out}" ]]; then
        local auth_status
        auth_status="$(sed -n "s/^STATUS://p" <<<"${parse_out}" | head -1)"
        GLOBAL_PAUSE="$(sed -n "s/^GLOBAL_PAUSE://p" <<<"${parse_out}" | head -1)"
        GLOBAL_PAUSE="${GLOBAL_PAUSE:-0}"
        if (( GLOBAL_PAUSE == 0 )); then
          local env_pause_val
          for env_pause_val in "${DISABLE_UPDATES:-0}" "${DISABLE_AUTOUPDATER:-0}"; do
            local norm_p
            norm_p="$(echo "${env_pause_val}" | tr "[:upper:]" "[:lower:]" | xargs)"
            case "${norm_p}" in
              1|true|yes|on|enabled)
                GLOBAL_PAUSE=1
                break
                ;;
            esac
          done
        fi
        DENY_ROSTER="$(sed -n "/^ALL:/,/^BREW_FORMULAE:/{ /^ALL:/d; /^BREW_FORMULAE:/d; p; }" <<<"${parse_out}")"
        DENY_ROSTER_BREW_FORMULAE="$(sed -n "/^BREW_FORMULAE:/,/^BREW_CASKS:/{ /^BREW_FORMULAE:/d; /^BREW_CASKS:/d; p; }" <<<"${parse_out}")"
        DENY_ROSTER_BREW_CASKS="$(sed -n "/^BREW_CASKS:/,/^NPM:/{ /^BREW_CASKS:/d; /^NPM:/d; p; }" <<<"${parse_out}")"
        DENY_ROSTER_NPM="$(sed -n "/^NPM:/,/^PAUSED:/{ /^NPM:/d; /^PAUSED:/d; p; }" <<<"${parse_out}")"
        PAUSED_ROSTER="$(sed -n "/^PAUSED:/,\$ { /^PAUSED:/d; p; }" <<<"${parse_out}")"

        if [[ "${auth_status}" == "reconciled" ]]; then
          echo ">>> Pre-flight Authority & Safety Check: verified (reconciled)"
        else
          echo ">>> Pre-flight Authority & Safety Check: verified (${auth_status}, mutation gating active)"
        fi
      else
        PREFLIGHT_FAILED=1
        echo ">>> Pre-flight Authority & Safety Check: FAILED (JSON parse error or missing authority_reconciliation)"
      fi
    else
      PREFLIGHT_FAILED=1
      echo ">>> Pre-flight Authority & Safety Check: FAILED (inventory reporter error)"
    fi
  else
    PREFLIGHT_FAILED=1
    echo ">>> Pre-flight Authority & Safety Check: FAILED (inventory reporter missing: ${STORE_DIR}/scripts/inventory-workstation-toolchain.py)"
  fi

  # 1. Homebrew
  echo ""
  echo ">>> [Stage 1/12] Homebrew Maintenance"
  if [[ "${MODE}" == "check" ]]; then
    echo "    check mode: brew update suppressed"
    HOMEBREW_NO_AUTO_UPDATE=1 HOMEBREW_NO_INSTALL_CLEANUP=1 brew outdated --formula 2>&1 || true
    HOMEBREW_NO_AUTO_UPDATE=1 HOMEBREW_NO_INSTALL_CLEANUP=1 brew outdated --cask --greedy 2>&1 || true
  else
    if (( PREFLIGHT_FAILED != 0 )); then
      echo "    SKIPPED: broad formula/cask upgrades suppressed (preflight authority check failed)"
    elif (( GLOBAL_PAUSE != 0 )); then
      echo "    SKIPPED: Homebrew maintenance paused by policy (DISABLE_UPDATES)"
    else
      brew update 2>&1 || true
      if [[ -n "${DENY_ROSTER_BREW_FORMULAE}" ]]; then
        local deny_form_csv
        deny_form_csv="$(paste -sd, - <<<"${DENY_ROSTER_BREW_FORMULAE}")"
        echo "    SKIPPED: formula upgrades suppressed (authority drift/conflict/misalignment detected: ${deny_form_csv})"
      else
        brew upgrade --formula 2>&1 || true
      fi

      if [[ -n "${DENY_ROSTER_BREW_CASKS}" ]]; then
        local deny_cask_csv
        deny_cask_csv="$(paste -sd, - <<<"${DENY_ROSTER_BREW_CASKS}")"
        echo "    SKIPPED: cask upgrades suppressed (authority drift/conflict/misalignment detected: ${deny_cask_csv})"
      else
        brew upgrade --cask 2>&1 || true
      fi

      brew cleanup -s 2>&1 || true
    fi
  fi

  # 2. Bun Runtime & Globals
  echo ""
  echo ">>> [Stage 2/12] Bun Runtime & Globals"
  if command -v bun &>/dev/null; then
    if [[ "${MODE}" == "check" ]]; then
      echo "    check mode: bun upgrade suppressed"
    elif (( PREFLIGHT_FAILED != 0 )); then
      echo "    SKIPPED: bun upgrade suppressed (preflight authority check failed)"
    elif (( GLOBAL_PAUSE != 0 )); then
      echo "    SKIPPED: Bun upgrade paused by policy (DISABLE_UPDATES)"
    else
      bun upgrade 2>&1 || true
    fi
  fi

  # 3. Global NPM Packages (Filtered to exclude local git packages and authority-denied tools)
  echo ""
  echo ">>> [Stage 3/12] Global NPM Packages (Filtered)"
  if [[ "${MODE}" == "check" ]]; then
    npm outdated -g --prefix "${HOME}/.npm-global" 2>&1 || true
  elif (( PREFLIGHT_FAILED != 0 )); then
    echo "    SKIPPED: global npm upgrades suppressed (preflight authority check failed)"
  elif (( GLOBAL_PAUSE != 0 )); then
    echo "    SKIPPED: global npm upgrades paused by policy (DISABLE_UPDATES)"
  else
    # Parse outdated npm packages, strictly excluding private/git packages, known native governed packages, and tools active outside ~/.npm-global
    local npm_filter='^prime-agent(@[^@]*)?$|^@anthropic-ai/claude-code(@[^@]*)?$'
    if [[ -n "${DENY_ROSTER_NPM}" ]]; then
      while IFS= read -r denied_npm_tool; do
        [[ -z "${denied_npm_tool}" ]] && continue
        case "${denied_npm_tool}" in
          codex)
            npm_filter="${npm_filter}|^(@openai/codex)(@[^@]*)?$"
            ;;
          qoder|qodercli)
            npm_filter="${npm_filter}|^(@qoder-ai/qodercli|@qoder-ai/qoder)(@[^@]*)?$"
            ;;
          kilo)
            npm_filter="${npm_filter}|^(@kilocode/cli|kilo)(@[^@]*)?$"
            ;;
          auggie)
            npm_filter="${npm_filter}|^(@augmentcode/auggie|auggie)(@[^@]*)?$"
            ;;
          pi)
            npm_filter="${npm_filter}|^(@earendil-works/pi-coding-agent|pi)(@[^@]*)?$"
            ;;
          bru)
            npm_filter="${npm_filter}|^(@usebruno/cli|bru)(@[^@]*)?$"
            ;;
          *)
            npm_filter="${npm_filter}|^(${denied_npm_tool})(@[^@]*)?$"
            ;;
        esac
      done <<<"${DENY_ROSTER_NPM}"
    fi
    local real_codex
    real_codex="$(realpath "$(command -v codex)" 2>/dev/null || which codex 2>/dev/null || true)"
    if [[ -n "${real_codex}" && "${real_codex}" != "${HOME}/.npm-global"* ]]; then
      npm_filter="${npm_filter}|^(@openai/codex)(@[^@]*)?$"
    fi
    OUTDATED_PKGS=$(npm outdated -g --parseable --prefix "${HOME}/.npm-global" 2>/dev/null | awk -F: '{pkg=$4; sub(/@[^@]*$/, "", pkg); print (pkg != "" ? pkg : $4)}' | grep -v -E "${npm_filter}" || true)
    if [[ -n "${OUTDATED_PKGS}" ]]; then
      echo "Updating eligible global npm packages: ${OUTDATED_PKGS}"
      # shellcheck disable=SC2086
      npm install -g ${OUTDATED_PKGS} --prefix "${HOME}/.npm-global" 2>&1 || true
    else
      echo "All eligible global npm packages are up-to-date."
    fi
  fi

  # 4. Python / uv Tools
  echo ""
  echo ">>> [Stage 4/12] Python / uv Tools"
  if command -v uv &>/dev/null; then
    if [[ "${MODE}" == "check" ]]; then
      uv tool list 2>&1 || true
    elif (( PREFLIGHT_FAILED != 0 )); then
      echo "    SKIPPED: uv tool upgrades suppressed (preflight authority check failed)"
    elif (( GLOBAL_PAUSE != 0 )); then
      echo "    SKIPPED: uv tool upgrades paused by policy (DISABLE_UPDATES)"
    else
      uv tool upgrade graphifyy 2>&1 || true
      uv tool upgrade tavily-cli 2>&1 || true
    fi
  fi

  # 5. Coding Agent CLIs (declared covered set; each update time-bounded)
  echo ""
  echo ">>> [Stage 5/12] Coding Agent CLIs (covered set)"
  # Called directly (not via $(...)) so the function's AGENT_FAILED assignment
  # survives; a command substitution would run it in a subshell and lose it.
  AGENT_FAILED=0
  if [[ "${MODE}" == "check" ]]; then
    echo "    supported/covered set: $(cut -d: -f1 <<<"${AGENT_CLI_COVERED}" | paste -sd, -)"
    local agent_bin
    while IFS=: read -r agent_bin _ _; do
      [[ -z "${agent_bin}" ]] && continue
      if command -v "${agent_bin}" &>/dev/null; then
        echo "    installed: ${agent_bin} ($(${agent_bin} --version 2>&1 | head -1))"
      fi
    done <<<"${AGENT_CLI_COVERED}"
    echo "    (check mode: no agent CLI updates applied)"
  elif (( PREFLIGHT_FAILED != 0 )); then
    echo "    SKIPPED: agent CLI updates suppressed (preflight authority check failed)"
  else
    agent_cli_coverage "${DENY_ROSTER}" "${PAUSED_ROSTER}"
  fi

  # 6. Cross-Agent Skills Synchronization & Parity
  echo ""
  echo ">>> [Stage 6/12] Cross-Agent Skills Parity Check"
  SYNC_FAILED=0
  if [[ -f "${STORE_DIR}/scripts/sync-workspace-agent-skills.py" ]]; then
    if ! python3 "${STORE_DIR}/scripts/sync-workspace-agent-skills.py" --check 2>&1; then
      echo "Skills out of sync. Reconciling..."
      if [[ "${MODE}" == "apply" ]]; then
        if (( GLOBAL_PAUSE != 0 )); then
          echo "    SKIPPED: skills reconciliation paused by policy (DISABLE_UPDATES)"
        else
          python3 "${STORE_DIR}/scripts/sync-workspace-agent-skills.py" 2>&1 || true
          if ! python3 "${STORE_DIR}/scripts/sync-workspace-agent-skills.py" --check 2>&1; then
            SYNC_FAILED=1
          fi
        fi
      else
        SYNC_FAILED=1
      fi
    fi
  fi
  if [[ "${SYNC_FAILED}" -ne 0 ]]; then
    echo "ERROR: skills out of sync after reconciliation — unresolved or malformed skill entries remain."
  fi

  # 7. Script provenance drift (executed copy vs recorded mirror)
  echo ""
  echo ">>> [Stage 7/12] Script Provenance Drift Check"
  SCRIPT_DRIFT=0
  detect_script_drift
  if (( SCRIPT_DRIFT != 0 )); then
    echo "    WARNING: executed scripts differ from their recorded mirrors (or lack a record)."
    echo "    Reported only — neither copy is modified. Reconcile deliberately after review."
  else
    echo "    No script drift found: every executed script matches its recorded mirror."
  fi

  # 8. Snapshot Store Growth Bounds
  echo ""
  echo ">>> [Stage 8/12] Snapshot Store Growth Bounds"
  SNAPSHOT_STORE_EXCEEDED=0
  SNAPSHOT_MEASURE_FAILED=0
  if [[ -f "${STORE_DIR}/scripts/measure-snapshot-growth.py" ]]; then
    local snap_out snap_rc=0
    snap_out="$(run_with_timeout 60 python3 "${STORE_DIR}/scripts/measure-snapshot-growth.py" 2>&1)" || snap_rc=$?
    echo "${snap_out}"
    # A nonzero exit means the measurement could not be produced. That is a
    # DIFFERENT fact from a measured breach, so it keeps its own flag: the
    # summary must never claim a ceiling breach that was never measured.
    if (( snap_rc != 0 )); then
      SNAPSHOT_MEASURE_FAILED=1
    elif grep -q "Status: EXCEEDED" <<<"${snap_out}"; then
      SNAPSHOT_STORE_EXCEEDED=1
    fi
  else
    SNAPSHOT_MEASURE_FAILED=1
    echo "ERROR: reporter missing: ${STORE_DIR}/scripts/measure-snapshot-growth.py"
  fi

  # 9. Toolchain Inventory & Prefix Reconciliation
  echo ""
  echo ">>> [Stage 9/12] Toolchain Inventory & Prefix Reconciliation"
  PREFIX_SPLIT_DETECTED=0
  INVENTORY_MEASURE_FAILED=0
  AUTHORITY_DRIFT_DETECTED=0
  if [[ -f "${STORE_DIR}/scripts/inventory-workstation-toolchain.py" ]]; then
    local inv_out inv_rc=0
    inv_out="$(run_with_timeout 60 python3 "${STORE_DIR}/scripts/inventory-workstation-toolchain.py" 2>&1)" || inv_rc=$?
    echo "${inv_out}"
    local has_inv_header=0
    grep -q "=== Workstation Prefix Reconciliation ===" <<<"${inv_out}" && has_inv_header=1
    if (( inv_rc != 0 )) || (( has_inv_header == 0 )); then
      INVENTORY_MEASURE_FAILED=1
    else
      if grep -q "Status:                      SPLIT_DETECTED" <<<"${inv_out}"; then
        PREFIX_SPLIT_DETECTED=1
      fi
      if grep -q "Status:                      DRIFT_DETECTED" <<<"${inv_out}"; then
        AUTHORITY_DRIFT_DETECTED=1
      fi
    fi
  else
    INVENTORY_MEASURE_FAILED=1
    echo "ERROR: reporter missing: ${STORE_DIR}/scripts/inventory-workstation-toolchain.py"
  fi

  # 10. Agent CLI Coverage Reconciliation
  echo ""
  echo ">>> [Stage 10/12] Agent CLI Coverage Reconciliation"
  AGENT_UNDECLARED_COUNT=0
  AGENT_COVERAGE_MEASURE_FAILED=0
  if [[ -f "${STORE_DIR}/scripts/reconcile-agent-cli-coverage.py" ]]; then
    local rec_out rec_rc=0
    rec_out="$(run_with_timeout 60 python3 "${STORE_DIR}/scripts/reconcile-agent-cli-coverage.py" 2>&1)" || rec_rc=$?
    echo "${rec_out}"
    local has_header=0
    grep -q "=== Workstation Agent CLI Coverage Reconciliation ===" <<<"${rec_out}" && has_header=1

    if (( rec_rc == 0 )) && (( has_header == 1 )); then
      AGENT_UNDECLARED_COUNT=0
    elif (( rec_rc == 1 )) && (( has_header == 1 )) && ! grep -qi "Traceback" <<<"${rec_out}"; then
      local parsed_count
      parsed_count="$(sed -n 's/.*Undeclared Count:[[:space:]]*\([0-9][0-9]*\).*/\1/p' <<<"${rec_out}" | head -1)"
      if [[ -n "${parsed_count}" ]] && (( parsed_count > 0 )); then
        AGENT_UNDECLARED_COUNT="${parsed_count}"
      else
        AGENT_COVERAGE_MEASURE_FAILED=1
      fi
    else
      AGENT_COVERAGE_MEASURE_FAILED=1
    fi
  else
    AGENT_COVERAGE_MEASURE_FAILED=1
    echo "ERROR: reporter missing: ${STORE_DIR}/scripts/reconcile-agent-cli-coverage.py"
  fi

  # 11. Upstream skill-content refresh (runs AFTER parity, BEFORE validation)
  echo ""
  echo ">>> [Stage 11/12] Skill Content Refresh (canonical store)"
  REFRESH_REFRESHED=0
  REFRESH_ALREADY=0
  REFRESH_AMBIGUOUS=0
  REFRESH_FAILED=0
  if command -v skills &>/dev/null; then
    if [[ "${MODE}" == "check" ]]; then
      # Non-mutating: report the covered/upstream surface without pulling.
      # `skills update` has no dry-run flag, so check mode must not invoke it.
      echo "    (check mode: no skill content applied)"
      echo "    canonical store: ${WORKSPACE_DIR}/.agents/skills"
      echo "    upstream-locked entries: $(python3 -c "import json,sys;print(len(json.load(open('${WORKSPACE_DIR}/skills-lock.json'))['skills']))" 2>/dev/null || echo unknown)"
      echo "    NOTE: run without --check to refresh; drift is reported by the refresh stage"
    elif (( GLOBAL_PAUSE != 0 )); then
      echo "    SKIPPED: skill content refresh paused by policy (DISABLE_UPDATES)"
    else
      refresh_skill_content || true
      echo "    summary: refreshed=${REFRESH_REFRESHED} already_current=${REFRESH_ALREADY} path_ambiguous=${REFRESH_AMBIGUOUS} failed=${REFRESH_FAILED}"
    fi
  else
    echo "    skills CLI not found — skipping content refresh"
  fi

  # 12. OpenSpec Store Validation Gate
  echo ""
  echo ">>> [Stage 12/12] OpenSpec Store Strict Validation"
  if command -v openspec &>/dev/null; then
    openspec validate --all --strict --store openspec-store 2>&1 || {
      echo "WARNING: OpenSpec validation reported issues."
    }
  fi

  echo ""
  echo "======================================================================"
  # Reported degradations (non-fatal). Parity stays fail-closed below.
  if (( REFRESH_FAILED != 0 )); then
    echo "DEGRADED: skill content refresh failed (rc/timeout); upstream may be unreachable."
  fi
  if [[ "${AGENT_FAILED}" -ne 0 ]]; then
    echo "DEGRADED: one or more agent CLI updates failed."
  fi
  if (( SCRIPT_DRIFT != 0 )); then
    echo "DEGRADED: executed scripts drifted from their recorded mirrors (or lack a record)."
  fi
  if (( SNAPSHOT_STORE_EXCEEDED != 0 )); then
    echo "DEGRADED: one or more Git snapshot stores exceed declared size ceilings."
  fi
  if (( PREFIX_SPLIT_DETECTED != 0 )); then
    echo "DEGRADED: npm global prefix split detected (effective prefix != declared prefix)."
  fi
  if (( AGENT_UNDECLARED_COUNT != 0 )); then
    echo "DEGRADED: undeclared agent CLI installations detected."
  fi
  if (( AUTHORITY_DRIFT_DETECTED != 0 )); then
    echo "DEGRADED: version-authority drift or target-misalignment detected."
  fi
  if (( SNAPSHOT_MEASURE_FAILED != 0 )); then
    echo "DEGRADED: snapshot-store measurement could not be produced (reporter failed); store state is unknown, not clear."
  fi
  if (( INVENTORY_MEASURE_FAILED != 0 )); then
    echo "DEGRADED: toolchain inventory measurement could not be produced (reporter failed); prefix state is unknown, not clear."
  fi
  if (( AGENT_COVERAGE_MEASURE_FAILED != 0 )); then
    echo "DEGRADED: agent-CLI coverage measurement could not be produced (reporter failed); coverage state is unknown, not clear."
  fi
  if (( PREFLIGHT_FAILED != 0 )); then
    echo "DEGRADED: pre-flight authority check failed; mutating stages were suppressed."
  fi
  if [[ "${SYNC_FAILED}" -ne 0 ]]; then
    echo "$(date '+%Y-%m-%d %H:%M:%S %Z') — FAILED [MODE=${MODE}]: unresolved skill links remain"
    echo "======================================================================"
    return 1
  fi
  echo "$(date '+%Y-%m-%d %H:%M:%S %Z') — Complete [MODE=${MODE}]"
  echo "======================================================================"
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  if [[ "${MODE}" == "check" ]]; then
    run_pipeline
  else
    run_pipeline | tee -a "${LOG_FILE}"
  fi
fi
