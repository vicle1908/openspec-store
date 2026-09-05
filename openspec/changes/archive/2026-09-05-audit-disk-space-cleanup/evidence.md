# Read-Only Evidence

## Filesystem boundary

- Primary APFS data filesystem: `/System/Volumes/Data`, 460 GiB total, 363 GiB used, 53 GiB available, 88% capacity at audit time.
- Excluded separate mount: `/Applications/Nicegram.app/Wrapper`, independently reported at 95% capacity.
- APFS available capacity is not counted as reclaimable cleanup data.

## Docker

Command: `docker system df -v`

- Active containers: `omniroute`, `claude-code-provider-adapter-adapter-1`, `omniroute-redis`.
- Images: 6.369 GiB total; 2.092 GiB reported reclaimable.
- Volumes: 1.321 GiB total; 847.6 MiB reported reclaimable.
- Build cache: 34 MiB total; 0 B reported reclaimable.
- Unused image: dangling image ID `420570109d69`, 1.974 GiB unique size; subsequently removed under explicit Docker-only approval.
- Unlinked volumes include TDT PostgreSQL/Redis/ClickHouse/MinIO/MLflow data; no volume deletion is approved.
- Docker VM path: `/Users/androidteam/Library/Containers/com.docker.docker/Data/vms/0/data/Docker.raw`; allocated usage was measured by `du` at approximately 13 GiB, while logical `stat` size was approximately 704 GiB. Direct deletion is prohibited by this change.

## Trash

Command: bounded top-level metadata scan of `/Users/androidteam/.Trash`.

- Total allocated size: approximately 27 GiB.
- Largest measured entries: `content-v2` 4.7 GiB, `node_modules` 3.7 GiB, `archive-v0` 1.9 GiB, `v10` 1.9 GiB, `.venv` 1.0 GiB.
- Large directory modification dates: most 2026-08-24; older retained entries include 2025-12-04 and 2026-07-22.
- The Trash contains developer artifacts, package trees, diagnostic reports, logs, and application data; age does not establish disposal intent.
- No Trash item was deleted or approved for deletion.

## Homebrew

Command: `brew cleanup --dry-run`.

- Output contained deprecation warnings only.
- No removal entries or reclaimable byte count were reported.
- Homebrew is review-only; formula/cask counts are not interpreted as savings.

## Approved Docker action

- Explicit approval was interpreted as authorizing the dangling image only; persistent Docker volumes were not selected individually and were preserved.
- Pre-action target: dangling image `420570109d69`, 1.974 GiB unique size, created 2026-07-30.
- Action: Docker-native `docker image rm 420570109d69` completed successfully.
- Post-action `docker system df`: 4 images, 3 active; 4.395 GiB total; 118.3 MiB reclaimable. Ten volumes remain, with 847.6 MiB reported reclaimable; no volume was removed.
- Post-action `df -h /System/Volumes/Data`: `/dev/disk3s5`, 460 GiB total, 361 GiB used, 55 GiB available, 87% capacity.
- Trash, npm, pnpm, and all persistent Docker volume targets remain unchanged and are not claimed as cleaned.

## Approved non-volume cleanup

- Native `npm cache clean --force` completed; it cleared the npm cache, including `_cacache`; the separately targeted `_npx` directory was removed by the exact approved path command.
- `pnpm store prune` completed and reported 0 B removed; the pnpm store remains approximately 1.9 GiB because no unreferenced packages were found.
- Exact approved paths removed: `/Users/androidteam/.Trash/content-v2`, `/Users/androidteam/.Trash/node_modules`, `/Users/androidteam/.Trash/archive-v0`, `/Users/androidteam/.Trash/v10`, `/Users/androidteam/.Trash/.venv`, `/Users/androidteam/.npm/_npx`, and `/Users/androidteam/.npm/_cacache`.
- Post-cleanup filesystem: `/dev/disk3s5`, 460 GiB total, 347 GiB used, 70 GiB available, 84% capacity.
- Docker remained unchanged after cleanup: 4 images, 3 active containers, 10 volumes; no Docker volume, active container, or VM file was modified.

## Final validation

- `openspec validate audit-disk-space-cleanup --strict --json --store openspec-store` passed with 1 item valid and 0 failures after post-cleanup evidence was recorded.
- OpenSpec change remains scoped to this new change directory; no unrelated workspace paths were modified.
