#!/usr/bin/env bash
# ==============================================================================
# Shell Startup Benchmarking Harness
# Measures cold and warm startup times across repeated runs (default 5 cold, 5 warm),
# computing medians and variance without arbitrary fixed promises.
# Compatible with macOS Bash 3.2+ and Zsh.
# ==============================================================================

set -euo pipefail

RUNS=5
TARGET_SHELL="${SHELL:-/bin/zsh}"
STARTUP_CMD="exit"
OUTPUT_JSON=0
MOCK_COLD=""
MOCK_WARM=""

usage() {
  cat <<EOF
Usage: $(basename "$0") [OPTIONS]

Options:
  --runs N           Number of repeated runs for cold and warm benchmarks (default: 5, min: 5)
  --shell PATH       Shell binary to benchmark (default: \$SHELL or /bin/zsh)
  --command CMD      Command to execute in shell (default: 'exit')
  --json             Output results as structured JSON
  --mock-cold LIST   Comma-separated millisecond timings to mock cold runs (e.g. 120.5,119.2,122.0,121.1,120.0)
  --mock-warm LIST   Comma-separated millisecond timings to mock warm runs (e.g. 45.2,44.9,45.5,45.1,45.0)
  -h, --help         Show this help message
EOF
  exit 1
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --runs)
      RUNS="$2"
      shift 2
      ;;
    --shell)
      TARGET_SHELL="$2"
      shift 2
      ;;
    --command)
      STARTUP_CMD="$2"
      shift 2
      ;;
    --json)
      OUTPUT_JSON=1
      shift
      ;;
    --mock-cold)
      MOCK_COLD="$2"
      shift 2
      ;;
    --mock-warm)
      MOCK_WARM="$2"
      shift 2
      ;;
    -h|--help)
      usage
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage
      ;;
  esac
done

if (( RUNS < 5 )); then
  echo "Error: --runs must be at least 5 for statistically valid medians and variance" >&2
  exit 1
fi

# Measure single execution duration in milliseconds using python3
measure_run() {
  local is_cold="$1"
  python3 -c "
import subprocess, time, sys, os, tempfile

target_shell = sys.argv[1]
cmd = sys.argv[2]
is_cold = sys.argv[3] == '1'

env = os.environ.copy()
if is_cold:
    # Cold run simulation: invalidate completion dump cache if zsh
    env['ZSH_BENCHMARK_COLD'] = '1'

start = time.perf_counter()
try:
    subprocess.run([target_shell, '-i', '-c', cmd], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    elapsed_ms = (time.perf_counter() - start) * 1000.0
    print(f'{elapsed_ms:.2f}')
except Exception as e:
    sys.exit(1)
" "${TARGET_SHELL}" "${STARTUP_CMD}" "${is_cold}"
}

COLD_TIMINGS=()
WARM_TIMINGS=()

if [[ -n "${MOCK_COLD}" && -n "${MOCK_WARM}" ]]; then
  IFS=',' read -r -a COLD_TIMINGS <<< "${MOCK_COLD}"
  IFS=',' read -r -a WARM_TIMINGS <<< "${MOCK_WARM}"
else
  # Collect Cold Runs
  for (( i=1; i<=RUNS; i++ )); do
    t="$(measure_run 1)"
    COLD_TIMINGS+=("${t}")
  done

  # Collect Warm Runs
  for (( i=1; i<=RUNS; i++ )); do
    t="$(measure_run 0)"
    WARM_TIMINGS+=("${t}")
  done
fi

# Calculate statistics and emit report via Python
python3 -c "
import sys, json, statistics

cold_raw = sys.argv[1].split(',')
warm_raw = sys.argv[2].split(',')
target_shell = sys.argv[3]
runs_count = int(sys.argv[4])
output_json = sys.argv[5] == '1'

cold = [float(x.strip()) for x in cold_raw if x.strip()]
warm = [float(x.strip()) for x in warm_raw if x.strip()]

def compute_stats(vals):
    if not vals:
        return {'timings_ms': [], 'median_ms': 0.0, 'mean_ms': 0.0, 'variance': 0.0, 'min_ms': 0.0, 'max_ms': 0.0}
    med = round(statistics.median(vals), 2)
    mean = round(statistics.mean(vals), 2)
    var = round(statistics.variance(vals) if len(vals) > 1 else 0.0, 4)
    return {
        'timings_ms': vals,
        'median_ms': med,
        'mean_ms': mean,
        'variance': var,
        'min_ms': round(min(vals), 2),
        'max_ms': round(max(vals), 2),
    }

cold_stats = compute_stats(cold)
warm_stats = compute_stats(warm)

report = {
    'shell': target_shell,
    'runs_count': runs_count,
    'cold': cold_stats,
    'warm': warm_stats,
}

if output_json:
    print(json.dumps(report, indent=2))
else:
    print('=== Shell Startup Benchmark Results ===')
    print(f'Target Shell: {target_shell} ({runs_count} cold runs, {runs_count} warm runs)')
    print('')
    print('[Cold Runs]')
    print(f'  Timings (ms): {\", \".join(f\"{x:.2f}\" for x in cold_stats[\"timings_ms\"])}')
    print(f'  Median (ms):  {cold_stats[\"median_ms\"]}')
    print(f'  Mean (ms):    {cold_stats[\"mean_ms\"]}')
    print(f'  Variance:     {cold_stats[\"variance\"]}')
    print(f'  Range (ms):   {cold_stats[\"min_ms\"]} - {cold_stats[\"max_ms\"]}')
    print('')
    print('[Warm Runs]')
    print(f'  Timings (ms): {\", \".join(f\"{x:.2f}\" for x in warm_stats[\"timings_ms\"])}')
    print(f'  Median (ms):  {warm_stats[\"median_ms\"]}')
    print(f'  Mean (ms):    {warm_stats[\"mean_ms\"]}')
    print(f'  Variance:     {warm_stats[\"variance\"]}')
    print(f'  Range (ms):   {warm_stats[\"min_ms\"]} - {warm_stats[\"max_ms\"]}')
" "$(IFS=,; echo "${COLD_TIMINGS[*]}")" "$(IFS=,; echo "${WARM_TIMINGS[*]}")" "${TARGET_SHELL}" "${RUNS}" "${OUTPUT_JSON}"

exit 0
