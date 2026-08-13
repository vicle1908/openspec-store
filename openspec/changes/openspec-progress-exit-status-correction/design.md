# Design: openspec-progress-exit-status-correction

## Contract

The OpenSpec command is authoritative for task progress and the Python parser is only a formatter. The shell recipe MUST preserve the command's exit status and MUST NOT print a progress claim when the command fails.

## Pattern

Use a temporary file and explicit status capture so stdout/stderr remain separable and the parser cannot mask failure:

```bash
tmp=$(mktemp)
if openspec instructions apply --change <name> --json --store openspec-store >"$tmp"; then
  python3 - "$tmp" <<'PY'
import json
import sys

with open(sys.argv[1], encoding="utf-8") as f:
    data = json.load(f)
progress = data.get("progress", {})
print(
    f"tasks={progress.get('complete', 0)}/{progress.get('total', 0)} "
    f"remaining={progress.get('remaining', 0)}"
)
PY
else
  rc=$?
  printf 'openspec instructions apply failed (exit=%s)\n' "$rc" >&2
  rm -f "$tmp"
  exit "$rc"
fi
rm -f "$tmp"
```

A shorter `set -o pipefail` pipeline is acceptable only when its parser failure behavior is also explicit. The canonical examples use temporary-file status capture because it preserves stdout/stderr and gives the parser complete JSON.

## Scope

Only the four live documentation examples identified by the audit are changed. The archived predecessor remains untouched. The change is closed with focused validation, full-store validation, scoped commits, archive verification, and post-archive checks.
