#!/usr/bin/env bash
# Regression tests for process_inventory() exit semantics.
# Validates the fix applied in 909e504.
#
# Usage: bash scripts/knowledge-refresh/tests/test_process_inventory.sh

set -uo pipefail

SCRIPT="/Users/androidteam/Developer/openspec-store/scripts/knowledge-refresh/refresh-knowledge-indexes.sh"
TMPDIR_TEST="$(mktemp -d)"
LOG_FILE="$TMPDIR_TEST/log.txt"
INVENTORY_FILE="$TMPDIR_TEST/inventory.tsv"
trap 'rm -rf "$TMPDIR_TEST"' EXIT

RC_SKIP=10
RC_FAILURE=1

extract_process_inventory() {
    sed -n '/^process_inventory()/,/^}/p' "$SCRIPT"
}

setup_mocks() {
    OVERALL_TIMEOUT=300
    note()     { echo "$*" >> "$LOG_FILE"; }
    warn()     { echo "WARN: $*" >> "$LOG_FILE"; }
    log_line() { echo "LOG: $*" >> "$LOG_FILE"; }
    elapsed()  { echo 1; }
    repo_name() { basename "$1"; }
    is_repo()        { true; }
    is_dirty()       { false; }
    is_merge_state() { false; }
    is_rebase_state() { false; }
    snapshot_graph_outputs() { true; }
    restore_graph_outputs()  { true; }
    acquire_lock()   { true; }
    release_lock()   { true; }
    gitnexus_refresh() { true; }
    graphify_refresh() { true; }
    refresh_worktrees() { true; }
    validate_inventory() { true; }
    log_init()       { true; }
    log_rotate()     { true; }
}

PASS=0
FAIL=0
check() {
    local name="$1" expect="$2" got="$3"
    if [[ "$expect" == "$got" ]]; then
        echo "  PASS: $name"
        PASS=$((PASS + 1))
    else
        echo "  FAIL: $name (expect=$expect got=$got)"
        FAIL=$((FAIL + 1))
    fi
}

setup_mocks
eval "$(extract_process_inventory)"

echo "=== T1: all targets succeed ==="
printf '/tmp/a\tmain\tyes\tyes\n/tmp/b\tmain\tyes\tyes\n/tmp/c\tmain\tyes\tyes\n' > "$INVENTORY_FILE"
process_target() { return 0; }
> "$LOG_FILE"
set +e; process_inventory; rc=$?; set -e
check "exit 0" "0" "$rc"
check "log_status=success" "yes" "$(grep -q 'overall.*success' "$LOG_FILE" && echo yes || echo no)"
check "processed=3" "yes" "$(grep -q 'Processed:.*3' "$LOG_FILE" && echo yes || echo no)"
check "refreshed=3" "yes" "$(grep -q 'Refreshed:.*3' "$LOG_FILE" && echo yes || echo no)"
check "skipped=0" "yes" "$(grep -q 'Skipped:.*0' "$LOG_FILE" && echo yes || echo no)"
check "failed=0" "yes" "$(grep -q 'Failed:.*0' "$LOG_FILE" && echo yes || echo no)"

echo ""
echo "=== T2: skip only ==="
call=0; process_target() { call=$((call+1)); [[ $call -eq 1 ]] && return $RC_SKIP || return 0; }
> "$LOG_FILE"
set +e; process_inventory; rc=$?; set -e
check "exit 0" "0" "$rc"
check "log_status=success" "yes" "$(grep -q 'overall.*success' "$LOG_FILE" && echo yes || echo no)"
check "skipped=1" "yes" "$(grep -q 'Skipped:.*1' "$LOG_FILE" && echo yes || echo no)"
check "failed=0" "yes" "$(grep -q 'Failed:.*0' "$LOG_FILE" && echo yes || echo no)"
check "refreshed=2" "yes" "$(grep -q 'Refreshed:.*2' "$LOG_FILE" && echo yes || echo no)"

echo ""
echo "=== T3: one failure ==="
call=0; process_target() { call=$((call+1)); [[ $call -eq 2 ]] && return $RC_FAILURE || return 0; }
> "$LOG_FILE"
set +e; process_inventory; rc=$?; set -e
check "exit 1" "1" "$rc"
check "log_status=failed" "yes" "$(grep -q 'overall.*failed' "$LOG_FILE" && echo yes || echo no)"
check "processed=3" "yes" "$(grep -q 'Processed:.*3' "$LOG_FILE" && echo yes || echo no)"
check "failed=1" "yes" "$(grep -q 'Failed:.*1' "$LOG_FILE" && echo yes || echo no)"
check "refreshed=2" "yes" "$(grep -q 'Refreshed:.*2' "$LOG_FILE" && echo yes || echo no)"

echo ""
echo "=== T4: all failures ==="
process_target() { return $RC_FAILURE; }
> "$LOG_FILE"
set +e; process_inventory; rc=$?; set -e
check "exit 1" "1" "$rc"
check "log_status=failed" "yes" "$(grep -q 'overall.*failed' "$LOG_FILE" && echo yes || echo no)"
check "failed=3" "yes" "$(grep -q 'Failed:.*3' "$LOG_FILE" && echo yes || echo no)"
check "refreshed=0" "yes" "$(grep -q 'Refreshed:.*0' "$LOG_FILE" && echo yes || echo no)"

echo ""
echo "=== T5: timeout ==="
OVERALL_TIMEOUT=0
export OVERALL_TIMEOUT
process_target() { return 0; }
> "$LOG_FILE"
set +e; process_inventory; rc=$?; set -e
check "exit 0" "0" "$rc"
check "timeout_detected" "yes" "$(grep -q 'overall.*timeout' "$LOG_FILE" && echo yes || echo no)"

echo ""
echo "=== RESULTS: $PASS passed, $FAIL failed ==="
[[ $FAIL -eq 0 ]] && exit 0 || exit 1
