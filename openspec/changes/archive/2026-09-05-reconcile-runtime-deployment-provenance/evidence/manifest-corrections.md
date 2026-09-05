# Manifest Corrections

## ai-review manifest
- workspace_root: `~/.tdt` → `~/Developer` (source repos live there)
- source_root: stale deploy-source dir → `~/Developer/ai-review`
- pid: 28405 → 66918 (live PID)

## webhook-receiver manifest
- workspace_root: `~/Developer/tdt` (deleted) → `~/Developer`

## Post-fix verification
- com.tdt.ai-review PID 66918, exit 0
- com.tdt.webhook-receiver PID 667, exit 0
