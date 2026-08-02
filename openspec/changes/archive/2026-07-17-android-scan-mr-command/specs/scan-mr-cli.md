# scan-mr & scan-branch CLI Specification

## scan-mr Command

```
code-daily-scan scan-mr [OPTIONS]
```

### `--mr-iid` (required)

```bash
--mr-iid INTEGER
```

The GitLab MR IID (e.g., `23318`). Must be a positive integer.

**Behavior if omitted:** `typer.BadParameter` is raised: `--mr-iid is required`.

### `--platform` (required)

```bash
--platform TEXT
```

Target platform: `android` or `ios`.

### `--feature` (optional)

```bash
--feature TEXT
```

Filter changed files to a specific package/path prefix.

- Android example: `--feature "com/tdt/pmobile3/ewallet"`
- iOS example: `--feature "Modules/Profile/Ewallet"`

When specified, only files containing this path prefix are scanned.

## scan-branch Command

```
code-daily-scan scan-branch [OPTIONS]
```

### `--source-branch` (required)

```bash
--source-branch TEXT
```

Source branch to scan (e.g., `modules/ewallet/develop_newdesignsystem`).

### `--target-branch` (required)

```bash
--target-branch TEXT
```

Base/target branch to compare against (e.g., `modules/ewallet/develop`).

### `--platform` (required)

```bash
--platform TEXT
```

Target platform: `android` or `ios`.

### `--feature` (optional)

```bash
--feature TEXT
```

Filter changed files to a specific package/path prefix (same as `scan-mr`).

## Common Options

### `--project` (optional)

```bash
--project TEXT
```

The GitLab project identifier. Accepts numeric ID or path (e.g., `poems-team/poems-mobile3-android`).

**Default:** inferred from the local repo's `git remote get-url origin`.

### `--repo-path` (optional)

```bash
--repo-path PATH
```

Path to the repository to scan.

**Default:** resolved from config → `~/.tdt/config.yaml`.

### `--dry-run` (optional, flag)

```bash
--dry-run / --no-dry-run
```

Preview findings without writing to the spreadsheet.

**Default:** `--no-dry-run`.

### `--post-comment` (scan-mr only, optional, flag)

```bash
--post-comment / --no-post-comment
```

If set, post a summary comment on the MR.

**Default:** `--no-post-comment`.

## Output

All output is JSON to stdout. Example:

```json
{
  "command": "scan-branch",
  "mode": "live",
  "status": "ok",
  "recorded_at": "2026-06-11T10:00:00+07:00",
  "branch": {
    "source_branch": "modules/ewallet/develop_newdesignsystem",
    "target_branch": "modules/ewallet/develop",
    "project": "pspl/poems-mobile3-android",
    "project_id": "232",
    "tab_name": "BRANCH-modules-ewallet-develop-newdesignsystem-ComTdtPmobile3Ewallet",
    "feature": "ComTdtPmobile3Ewallet"
  },
  "scan": {
    "findings_count": 169,
    "by_priority": {"P0": 121, "P1": 48, "P2": 0, "P3": 0}
  },
  "sheet_write": {
    "dry_run": false,
    "tab_name": "BRANCH-modules-ewallet-develop-newdesignsystem-ComTdtPmobile3Ewallet",
    "total_findings": 169,
    "summary": {"P0": 121, "P1": 48, "P2": 0, "P3": 0, "Total": 169}
  }
}
```

## Exit Codes

| Code | Meaning |
|------|---------|
| `0` | Scan completed successfully (findings or not) |
| `1` | General error (invalid args, unexpected exception) |
| `2` | MR/branch not found or API error |

## Examples

```bash
# Basic MR scan
code-daily-scan scan-mr --mr-iid 23318

# MR scan with feature filter
code-daily-scan scan-mr --mr-iid 23318 --feature "com/tdt/pmobile3/ewallet"

# MR scan with comment posting
code-daily-scan scan-mr --mr-iid 23318 --post-comment

# Dry run preview
code-daily-scan scan-mr --mr-iid 23318 --dry-run

# Branch comparison with feature filter
code-daily-scan scan-branch \
  --source-branch modules/ewallet/develop_newdesignsystem \
  --target-branch modules/ewallet/develop \
  --feature "com/tdt/pmobile3/ewallet"

# iOS branch scan
code-daily-scan scan-branch \
  --source-branch HuuThanh/Task/EW-Update \
  --target-branch develop \
  --feature "Modules/Profile/Ewallet"
```
