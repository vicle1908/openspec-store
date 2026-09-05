# Design: Cloud Drive Migration

## Decision 1: iCloud projects → ~/Developer (mv, not cp+rm)

Move `project/vds/` (6.7G) and `project/microservices/` (604M) from iCloud to `~/Developer/` using `mv`. Since both source and destination are on the same APFS volume (`/Users/androidteam/`), `mv` is a fast directory-entry update, not a data copy. This is safer than `cp -r` + `rm -rf` because it's atomic — if the move fails partway, the source remains intact.

**Verification:** `ls ~/Developer/vds/` and `ls ~/Developer/microservices/` must list contents. `ls ~/Library/Mobile Documents/com~apple~CloudDocs/project/` must NOT contain `vds` or `microservices`.

## Decision 2: Delete iCloud build artifacts individually

Delete each artifact individually rather than blanket `rm -rf` to avoid accidentally removing unrelated files. The artifacts are:

- `compileDebugKotlin/` (824K) — Android build cache
- `compileKotlin/` (520K) — Android build cache
- `ksp/` (20K) — KSP annotation processor output
- `sparse/` (80K) — TypeScript type definitions
- `inventory/` (12K) — Kotlin test stub
- `com 2/` (52K) — Example directory
- `camunda/`, `camunda7/`, `camunda-async/` — Empty stubs
- `airbridge/` (12K), `tmz/` (8K) — Stubs

**Verification:** Each path must not exist after deletion.

## Decision 3: Google Drive TDT (1) — full delete

Delete `~/My Drive/TDT (1)/` entirely (2.9G). This is a stale duplicate of `~/My Drive/tdt/` missing 4 items. No content is lost.

**Verification:** `ls ~/My\ Drive/TDT\ \(1\)/` must fail (not found).

## Decision 4: Google Drive VinID — full delete (no migration)

Delete `~/My Drive/VinID/` entirely (2.3G). User confirmed: no migration to `~/Developer/` needed. This Android tracking module from `gitlab.id.vin` is no longer required.

**Verification:** `ls ~/My\ Drive/VinID/` must fail (not found).

## Decision 5: Google Drive tdt/ — surgical delete (keep documentation)

Delete code repos from `~/My Drive/tdt/` while preserving documentation repos. The items to **KEEP** (documentation):

- `tdt-meta/` (300M) — metadata
- `poems-mobile3-docs/` (225M) — documentation
- `tdt-python-source-package/` (20M) + `.zip` (10M) — source package
- `git-remotes/` (12M) — git remote configs
- `git-bundles/` (8.4M) — git bundles
- `data/` (22M) — data files
- `reports/` (696K) — reports
- `workflow-dag/` — workflow documentation
- Various `.md` files — documentation
- `About This Mac.png`, `Content from Macintosh HD - 2024-02-13.zip`

Everything else is a code repo to delete (~6.3G total). Implementation: list all items in `~/My Drive/tdt/`, compare against the keep-list, delete the rest.

**Verification:** `ls ~/My\ Drive/tdt/tdt-meta/` must exist. `ls ~/My\ Drive/tdt/mcp-router/` must not exist.

## Decision 6: Desktop/Documents cleanup — delete all stubs

Delete all 0B and near-empty stubs from Desktop and Documents. These are migration artifacts from a previous iCloud Desktop sync setup. Keep only substantive items:

- Desktop: keep `Cline/`, `Codex/`, `Adobe/`, `Kitematic/`, `Continental/`, `png` (8K)
- Documents: keep `Cline/`, `Codex/`, `Adobe/`, `Continental/`, `Kitematic/`
- Delete `tdt-python-source-package` from Desktop (132K)

**Verification:** `ls ~/Desktop/` and `ls ~/Documents/` must contain only non-stub items.

## Decision 7: Delete go-microservices-cleanup bundle

Delete `~/Developer/go-microservices-cleanup-20260817.bundle` (1.4G). This is a one-time backup bundle from a cleanup operation on 2026-08-17. The go-microservices repo is in git, so the bundle is redundant.

**Verification:** `ls ~/Developer/go-microservices-cleanup-20260817.bundle` must fail.
