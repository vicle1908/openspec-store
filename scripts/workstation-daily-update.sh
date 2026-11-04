#!/usr/bin/env bash
# ==============================================================================
# Workstation Daily Maintenance & Tooling Update Runner
# Consolidated check-and-update pipeline across Homebrew, Bun, filtered npm,
# uv tools, coding agent CLIs, skills parity, skill-content refresh, and
# OpenSpec store validation.
#
# Skill-content refresh notes (changes: automate-skill-content-refresh,
# reconcile-ponytail-agent-skills):
#   • `skills update` has NO --dry-run/--check/--json. Unknown flags are ignored
#     and a REAL update is executed, so never pass such a flag expecting a dry
#     run. `--check` mode inspects local registry, symlink parity, and accepted
#     snapshot digests without invoking `skills update`.
#   • A path-ambiguous upstream entry (same skill published at >1 path, e.g.
#     docfork-docs) is reported by the CLI as "Multiple current paths match …
#     skipping them". That is INFORMATIONAL, not stale/broken/failed.
#   • Local byte integrity is verified against `.agents/.skill-snapshots/current/`
#     via `sync-workspace-agent-skills.py --accept-refresh` rather than trusting
#     `skills-lock.json` `computedHash` alone.
#   • The refresh stage reports five outcomes in one line, e.g.
#       drift=1 refreshed=42 already_current=0 path_ambiguous=1 failed=0
#     meaning: post-update drift observed / entries refreshed / already current /
#     path-ambiguous skips / refresh failures.
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
export PATH="${HOME}/.kimi-code/bin:${HOME}/.qoder/entry:${HOME}/.local/bin:/opt/homebrew/bin:/opt/homebrew/sbin:/opt/homebrew/opt/libpq/bin:${HOME}/.pi/agent/bin:${HOME}/.npm-global/bin:${HOME}/.bun/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"
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
# A nonzero exit (incl. timeout 124), fatal error line, incomplete Refreshing N,
# or unrecognized output always wins as a failure.
classify_refresh() {
  local clean="$1" rc="${2:-0}"
  local drift=0 refreshed=0 already=0 ambiguous=0 failed=0
  local has_completion=0 has_recognized_summary=0

  # 1. Refreshed count (completed updates only; summary-first, no double-counting).
  local num_ref=""
  num_ref="$(sed -nE 's/.*Updated ([0-9]+) skill\(s\).*/\1/p; s/.*(^|[^0-9])([0-9]+) skills? (refreshed|updated).*/\2/p; s/.*(refreshed|updated):[[:space:]]*([0-9]+).*/\2/p' <<<"$clean" | head -1)"
  if [[ -n "$num_ref" ]]; then
    refreshed="$num_ref"
    has_completion=1
    has_recognized_summary=1
  elif grep -qE '^[[:space:]]*✓[[:space:]]+Updated[[:space:]]+[^0-9[:space:]]' <<<"$clean"; then
    refreshed="$(grep -cE '^[[:space:]]*✓[[:space:]]+Updated[[:space:]]+[^0-9[:space:]]' <<<"$clean" || true)"
    has_completion=1
    has_recognized_summary=1
  fi

  # 2. Drift (observed update activity: refreshed > 0 or positive activity/drift header).
  local num_drift=""
  num_drift="$(sed -nE 's/.*(^|[^0-9])([1-9][0-9]*) (skills? )?drifted.*/\2/p; s/.*drift:[[:space:]]*([1-9][0-9]*).*/\1/p' <<<"$clean" | head -1)"
  if [[ -n "$num_drift" ]]; then
    drift=1
    has_recognized_summary=1
  elif (( refreshed > 0 )); then
    drift=1
  elif grep -qE 'Found [1-9][0-9]* (global )?update|Refreshing [1-9][0-9]* skill' <<<"$clean"; then
    drift=1
  fi

  # 3. Path-ambiguous entries (informational, never a failure on their own).
  local num_amb=""
  num_amb="$(sed -nE 's/.*(^|[^0-9])([0-9]+) (skills? )?(path )?ambiguous.*/\2/p; s/.*ambiguous:[[:space:]]*([0-9]+).*/\1/p' <<<"$clean" | head -1)"
  if [[ -n "$num_amb" ]]; then
    ambiguous="$num_amb"
    has_recognized_summary=1
  elif grep -qE 'Multiple current paths match' <<<"$clean"; then
    ambiguous="$(grep -cE '^[[:space:]]*[-*•][[:space:]]+' <<<"$clean" || true)"
    if (( ambiguous == 0 )); then
      ambiguous="$(grep -cE 'Multiple current paths match' <<<"$clean" || true)"
    fi
    (( ambiguous == 0 )) && ambiguous=1
    has_recognized_summary=1
  fi

  # 4. Already current (requires explicit up-to-date evidence; never inferred from Checking + ambiguity alone).
  local num_already=""
  num_already="$(sed -nE 's/.*(^|[^0-9])([0-9]+) (project |global )?skills?(\(s\))? already[[:space:]]+(current|up to date).*/\2/p; s/.*(already[[:space:]]+current|already[[:space:]]+up to date):[[:space:]]*([0-9]+).*/\2/p' <<<"$clean" | head -1)"
  if [[ -n "$num_already" ]]; then
    already="$num_already"
    has_recognized_summary=1
  elif grep -qE 'All (project |global )?skills are up to date|(project |global )?skill\(s\) already[[:space:]]+up to date' <<<"$clean"; then
    has_recognized_summary=1
    if (( refreshed == 0 )); then
      already=1
    fi
  fi

  # 5. Failure: nonzero exit, fatal error line, incomplete Refreshing N, or no recognizable summary.
  local num_fail=""
  num_fail="$(sed -nE 's/.*(^|[^0-9])([1-9][0-9]*) (skills? )?(failed|failures).*/\2/p; s/.*failed:[[:space:]]*([1-9][0-9]*).*/\1/p' <<<"$clean" | head -1)"
  if (( rc != 0 )); then
    failed=1
  elif [[ -n "$num_fail" ]]; then
    failed=1
  elif grep -qE '(^|[[:space:]])(Error:|ERR!|fatal:|EACCES|ENOENT)' <<<"$clean"; then
    failed=1
  elif grep -qE 'Found [1-9][0-9]* (global )?update|Refreshing [1-9][0-9]* skill' <<<"$clean" && (( has_completion == 0 )); then
    failed=1
  elif (( has_recognized_summary == 0 )); then
    failed=1
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

  rm -rf "${WORKSPACE_DIR}/data/skills" "${WORKSPACE_DIR}/agent/skills" 2>/dev/null || true
  rmdir "${WORKSPACE_DIR}/agent" 2>/dev/null || true
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

  local snap_manifest="${WORKSPACE_DIR}/.agents/.skill-snapshots/current/manifest.json"
  if (( failed == 0 )); then
    if [[ -f "${STORE_DIR}/scripts/sync-workspace-agent-skills.py" ]]; then
      if ! python3 "${STORE_DIR}/scripts/sync-workspace-agent-skills.py" --accept-refresh 2>&1; then
        echo "    REFRESH FAILED: post-refresh acceptance verification failed"
        failed=1
        if [[ -f "${snap_manifest}" ]]; then
          python3 "${STORE_DIR}/scripts/sync-workspace-agent-skills.py" --recover-from-snapshot 2>&1 || true
        fi
      fi
    fi
  else
    if [[ -f "${STORE_DIR}/scripts/sync-workspace-agent-skills.py" ]] && [[ -f "${snap_manifest}" ]]; then
      python3 "${STORE_DIR}/scripts/sync-workspace-agent-skills.py" --recover-from-snapshot 2>&1 || true
    fi
  fi

  REFRESH_REFRESHED="${refreshed}"
  REFRESH_ALREADY="${already}"
  REFRESH_AMBIGUOUS="${ambiguous}"
  REFRESH_FAILED="${failed}"

  if (( failed == 1 )); then
    if (( rc == 124 )); then
      echo "    REFRESH FAILED: skills update exceeded ${SKILL_REFRESH_TIMEOUT}s bound (terminated)"
    else
      echo "    REFRESH FAILED: skills update returned rc=${rc} (upstream unreachable, acceptance failed, or output unrecognized)"
    fi
  elif (( drift == 1 )); then
    echo "    post-update drift observed: yes; refreshed ${refreshed} entr(y/ies)"
  else
    echo "    post-update drift observed: no; all upstream content already current"
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
pi:Pi:update --all
kimi:Kimi Code:update
ntn:Notion CLI:update"

AGENT_CLI_KNOWN_UNCOVERED="droid goose grok prime-agent happy cursor-agent hermes-agent buzz cce kilo muse qwen herdr omp"

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
    if [[ "${bin}" == "qoder" ]] && [[ "${real_bin}" != "${HOME}/.local"* && "${real_bin}" != "${HOME}/.qoder"* ]]; then
      echo "      - ${label} (${bin}): SKIPPED (target prefix misalignment: active binary resolves to ${real_bin} outside declared standalone roots)"
      continue
    fi

    local pre_real=""
    pre_real="$(realpath "$(command -v "${bin}")" 2>/dev/null || which "${bin}" 2>/dev/null || true)"
    local v_before="" v_after=""
    v_before="$("${bin}" --version 2>&1 | head -1 | strip_ansi || true)"

    local out rc=0
    if [[ "${bin}" == "codex" ]]; then
      out="$(run_with_timeout "${AGENT_UPDATE_TIMEOUT}" codex update 2>&1)" || rc=$?
    elif [[ "${bin}" == "ntn" ]]; then
      out="$(run_with_timeout "${AGENT_UPDATE_TIMEOUT}" ntn update 2>&1)" || rc=$?
    elif [[ "${bin}" == "qoder" && -x "${HOME}/.qoder/entry/qoder" ]]; then
      out="$(run_with_timeout "${AGENT_UPDATE_TIMEOUT}" "${HOME}/.qoder/entry/qoder" update 2>&1)" || rc=$?
    else
      # shellcheck disable=SC2086  # ${args} intentionally word-splits into argv
      out="$(run_with_timeout "${AGENT_UPDATE_TIMEOUT}" "${bin}" ${args} 2>&1)" || rc=$?
    fi
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
      for root_cand in "${HOME}/.npm-global" "${HOME}/.pi" "${HOME}/.kimi-code" "${HOME}/.local" "/opt/homebrew"; do
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

# Maintain code-signing and symlink invariants for TCC-governed binaries
# (goose Cellar symlink, Python.app bundle org.python.python, and python3).
sign_agent_binaries() {
  [[ "$(uname -s)" != "Darwin" ]] && return 0
  if command -v brew &>/dev/null && [[ ! -L "/opt/homebrew/bin/goose" || ! -e "/opt/homebrew/bin/goose" ]] && [[ -d "/opt/homebrew/Cellar/block-goose-cli" ]]; then
    brew unlink block-goose-cli >/dev/null 2>&1 || true
    brew link --overwrite block-goose-cli >/dev/null 2>&1 || true
  fi
  local cert_sha1="65340D85AFD298131C682D8463087891292A2B59"
  if ! security find-identity -v -p codesigning 2>/dev/null | grep -qi "${cert_sha1}"; then
    return 0
  fi
  if [[ -x "/opt/homebrew/bin/python3" ]]; then
    local py_real py_app py_plist
    py_real="$(python3 -c 'import os,sys; print(os.path.realpath(sys.argv[1]))' /opt/homebrew/bin/python3 2>/dev/null || true)"
    if [[ -n "${py_real}" && -f "${py_real}" ]]; then
      py_app="$(dirname "$(dirname "${py_real}")")/Resources/Python.app"
      py_plist="${py_app}/Contents/Info.plist"
      if [[ -d "${py_app}" ]]; then
        if [[ ! -f "${py_plist}" ]]; then
          python3 -c 'import plistlib,sys; p=sys.argv[1]; plistlib.dump({"CFBundleIdentifier":"org.python.python","CFBundleExecutable":"Python","CFBundleName":"Python","CFBundlePackageType":"APPL"}, open(p,"wb"))' "${py_plist}" 2>/dev/null || true
        fi
        codesign -f -s "${cert_sha1}" --identifier "org.python.python" --deep "${py_app}" >/dev/null 2>&1 || true
      fi
      codesign -f -s "${cert_sha1}" --identifier "org.python.python3" "${py_real}" >/dev/null 2>&1 || true
    fi
  fi
  if [[ -L "/opt/homebrew/bin/goose" || -f "/opt/homebrew/bin/goose" ]]; then
    local goose_real
    goose_real="$(python3 -c 'import os,sys; print(os.path.realpath(sys.argv[1]))' /opt/homebrew/bin/goose 2>/dev/null || true)"
    if [[ -n "${goose_real}" && -f "${goose_real}" ]]; then
      codesign -f -s "${cert_sha1}" --identifier "com.block.goose" "${goose_real}" >/dev/null 2>&1 || true
    fi
  fi
}

# Verify active canonical coding agent Mach-O CLI realpaths and shared Python
# automation identities in TCC.db (read-only) with native csreq signature checks.
verify_tcc_provenance() {
  echo "    verifying TCC provenance for active agent Mach-O binaries..."
  local uname_s="${TCC_UNAME_S_OVERRIDE:-$(uname -s)}"
  if [[ "${uname_s}" != "Darwin" ]]; then
    echo "      - non-Darwin platform (${uname_s}); skipping TCC provenance verification"
    return 0
  fi

  local helper="${TCC_PROVENANCE_HELPER:-${STORE_DIR}/scripts/tcc_provenance.py}"
  if [[ ! -f "${helper}" ]]; then
    echo "      - ERROR: TCC provenance helper missing: ${helper}"
    return 1
  fi

  local tcc_db="${TCC_DB_PATH_OVERRIDE:-/Library/Application Support/com.apple.TCC/TCC.db}"
  python3 "${helper}" --db "${tcc_db}" "$@"
}


run_pipeline() {
  echo "======================================================================"
  echo "$(date '+%Y-%m-%d %H:%M:%S %Z') — Workstation Daily Update [MODE=${MODE}]"
  echo "======================================================================"
  if [[ "${MODE}" == "check" ]]; then
    export HOMEBREW_NO_AUTO_UPDATE=1
    export HOMEBREW_NO_INSTALL_CLEANUP=1
  fi

  # Primary Delegation: Durable DBOS Execution via shb-schedule
  if [[ "${MODE}" == "apply" ]] && command -v uv &>/dev/null && [[ -f "${HOME}/Developer/shb/shb-schedule/pyproject.toml" ]]; then
    echo ">>> Dispatching primary execution to durable shb-schedule workflow..."
    if uv run --directory "${HOME}/Developer/shb/shb-schedule" shb-schedule run-now workstation-daily-update; then
      echo ">>> Durable shb-schedule execution completed successfully."
      echo ">>> Telemetry record persisted to ~/Developer/data/updates/."
      return 0
    else
      echo ">>> Warning: shb-schedule workflow degraded or failed. Falling back to native sequential runner..."
    fi
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
        # Graceful POSIX termination for running casks to prevent file locking during upgrade
        local running_casks=( "Tailscale" "warp-svc" "Google Drive" "OneDrive" "Orca" "ChatGPT" "Zed" )
        for p in "${running_casks[@]}"; do
          if pgrep -x "$p" >/dev/null 2>&1; then
            pkill -TERM -x "$p" >/dev/null 2>&1 || true
          fi
        done
        brew upgrade --cask < /dev/null 2>&1 || true
        # Relaunch persistent background utilities
        for app in "Tailscale" "Cloudflare WARP" "OneDrive" "Google Drive"; do
          if [[ -d "/Applications/${app}.app" ]]; then
            open -a "${app}" --background >/dev/null 2>&1 || true
          fi
        done
        if [[ -x "/Applications/Docker.app/Contents/MacOS/install" ]] && [[ -x "${WORKSPACE_DIR}/scripts/docker-service.sh" ]]; then
          if ! docker info >/dev/null 2>&1 || \
             [[ ! -S "/var/run/com.docker.vmnetd.sock" ]] || \
             [[ ! -r "/Library/PrivilegedHelperTools/com.docker.vmnetd" ]] || \
             [[ ! -x "/Library/PrivilegedHelperTools/com.docker.socket" ]]; then
            if "${WORKSPACE_DIR}/scripts/docker-service.sh" start 2>&1; then
              "${WORKSPACE_DIR}/scripts/docker-service.sh" up 2>&1 || true
            fi
          fi
        fi
      fi

      brew cleanup -s 2>&1 || true
      sign_agent_binaries || true
    fi
  fi

  # 1b. Mac App Store Maintenance (Zero Deferral)
  if command -v mas &>/dev/null; then
    echo ""
    echo ">>> Mac App Store Maintenance (Zero Deferral)"
    if [[ "${MODE}" == "check" ]]; then
      echo "    check mode: mas outdated inspection only"
      mas outdated 2>&1 || true
    elif (( PREFLIGHT_FAILED != 0 )); then
      echo "    SKIPPED: mas upgrade suppressed (preflight authority check failed)"
    elif (( GLOBAL_PAUSE != 0 )); then
      echo "    SKIPPED: mas upgrade paused by policy (DISABLE_UPDATES)"
    else
      local mas_outdated_lines
      mas_outdated_lines="$(mas outdated 2>/dev/null || true)"
      if [[ -n "${mas_outdated_lines}" ]]; then
        while IFS= read -r line; do
          [[ -z "${line}" ]] && continue
          local app_id app_name
          app_id="$(awk '{print $1}' <<<"${line}")"
          app_name="$(awk '{$1=""; print $0}' <<<"${line}" | sed 's/^[[:space:]]*//; s/([^(]*)$//' | xargs)"
          [[ -z "${app_id}" || ! "${app_id}" =~ ^[0-9]+$ ]] && continue
          local was_running=0
          if pgrep -x "${app_name}" >/dev/null 2>&1 || pgrep -x "${app_name%% *}" >/dev/null 2>&1; then
            was_running=1
            pkill -TERM -x "${app_name}" >/dev/null 2>&1 || true
            pkill -TERM -x "${app_name%% *}" >/dev/null 2>&1 || true
            sleep 2
          fi
          echo "    Upgrading Mac App Store app: ${app_name} (${app_id})..."
          mas upgrade "${app_id}" < /dev/null 2>&1 || true
          if (( was_running == 1 )); then
            local relaunch_target="${app_name}"
            [[ "${app_name}" =~ Telegram ]] && relaunch_target="Telegram"
            open -a "${relaunch_target}" --background >/dev/null 2>&1 || true
          fi
        done <<<"${mas_outdated_lines}"
      fi
    fi
  fi

  # 2. Bun Runtime & Globals
  echo ""
  echo ">>> [Stage 2/12] Bun Runtime & Globals"
  if command -v bun &>/dev/null; then
    if [[ "${MODE}" == "check" ]]; then
      echo "    check mode: bun global update suppressed"
    elif (( PREFLIGHT_FAILED != 0 )); then
      echo "    SKIPPED: bun global update suppressed (preflight authority check failed)"
    elif (( GLOBAL_PAUSE != 0 )); then
      echo "    SKIPPED: Bun global update paused by policy (DISABLE_UPDATES)"
    else
      mkdir -p "${HOME}/.bun/install/global"
      chmod 700 "${HOME}/.bun/install/global"
      if [[ ! -f "${HOME}/.bun/install/global/package.json" ]]; then
        printf '{"dependencies": {}}\n' > "${HOME}/.bun/install/global/package.json"
      fi
      chmod 600 "${HOME}/.bun/install/global/package.json"
      if jq -e '((.dependencies // {}) + (.devDependencies // {}) + (.optionalDependencies // {})) | length > 0' "${HOME}/.bun/install/global/package.json" >/dev/null 2>&1; then
        bun update -g --save-text-lockfile 2>&1 || true
      else
        if [[ ! -f "${HOME}/.bun/install/global/bun.lock" ]]; then
          printf '{"lockfileVersion": 2, "configVersion": 1, "workspaces": {"": {}}, "packages": {}}\n' > "${HOME}/.bun/install/global/bun.lock"
        fi
      fi
      [[ -f "${HOME}/.bun/install/global/bun.lock" ]] && chmod 600 "${HOME}/.bun/install/global/bun.lock"
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
      uv python upgrade 2>&1 || true
      uv tool upgrade --all 2>&1 || true
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
    sign_agent_binaries || true
    for pi_lens_log in "${HOME}/.pi-lens"/*.log; do
      [[ -f "${pi_lens_log}" ]] || continue
      if (( $(stat -f '%z' "${pi_lens_log}" 2>/dev/null || echo 0) > 5242880 )); then
        : > "${pi_lens_log}"
      fi
    done
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
  TCC_DRIFT=0
  verify_tcc_provenance --bundles || TCC_DRIFT=1

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
      if grep -q "Status:                      DRIFT_DETECTED" <<<"${inv_out}" && ! grep -q "Reconciled Authority Status: RECONCILED" <<<"${inv_out}"; then
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
  if (( TCC_DRIFT != 0 )); then
    echo "DEGRADED: one or more required TCC identities lack verified provenance or csreq signature match."
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
  if (( TCC_DRIFT != 0 || PREFLIGHT_FAILED != 0 || SNAPSHOT_MEASURE_FAILED != 0 || INVENTORY_MEASURE_FAILED != 0 || AGENT_COVERAGE_MEASURE_FAILED != 0 || AUTHORITY_DRIFT_DETECTED != 0 || AGENT_UNDECLARED_COUNT != 0 || SCRIPT_DRIFT != 0 )); then
    echo "$(date '+%Y-%m-%d %H:%M:%S %Z') — DEGRADED [MODE=${MODE}]: required verification or authority checks failed"
    echo "======================================================================"
    return 1
  fi
  echo "$(date '+%Y-%m-%d %H:%M:%S %Z') — Complete [MODE=${MODE}]"
  echo "======================================================================"
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  if [[ "${MODE}" == "check" ]]; then
    run_pipeline
  elif [[ -n "${WORKSTATION_LOG_REDIRECTED:-}" ]]; then
    run_pipeline
  elif [[ -f "${LOG_FILE}" ]] && [[ "$(stat -f '%d:%i' /dev/fd/1 2>/dev/null || true)" == "$(stat -f '%d:%i' "${LOG_FILE}" 2>/dev/null || true)" ]]; then
    run_pipeline
  else
    run_pipeline | tee -a "${LOG_FILE}"
  fi
fi
