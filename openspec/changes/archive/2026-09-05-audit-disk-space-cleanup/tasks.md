## 1. Read-Only Evidence

- [x] 1.1 Capture primary and excluded filesystem/device boundaries with `df -h`; verify the Nicegram wrapper and network/FUSE mounts are not combined with the primary data volume.
- [x] 1.2 Capture bounded per-root size and age evidence for Trash, caches, Docker/Colima VM paths, simulator caches, personal data, and developer artifacts; verify output contains paths, sizes, dates, and no file contents.
- [x] 1.3 Capture `docker system df -v` and volume names; verify only Docker-native reclaimable images/volumes are candidates and Docker.raw is excluded.
- [x] 1.4 Record Homebrew `brew cleanup --dry-run` output; verify no reclaimable byte count is claimed unless the command reports actual removals.

## 2. Approval Gate

- [x] 2.1 Present exact candidate paths, measured allocated sizes, dates, impact, and maximum possible recovery; verify no cleanup command is run.
- [x] 2.2 Obtain explicit approval naming exact Trash entries, Docker resources, or cache paths; verify unchecked cleanup tasks remain unchanged until approval.

## 3. Cleanup and Verification

- [x] 3.1 Execute the explicitly approved dangling Docker image removal using a Docker-native command; verify target `420570109d69` was removed and no volumes, active containers, or VM files were changed.
- [x] 3.2 Execute the explicitly approved Trash and package-cache cleanup commands; verify command scope matched exact approved paths and no personal/state data was included.
- [x] 3.3 Re-run Docker and filesystem measurements after the approved image removal; verify Docker totals changed, persistent volumes remain, and no claim is made that APFS free space itself was reclaimable data.
- [x] 3.4 Re-run per-root measurements after the remaining approved cleanup; verify removed paths are absent, remaining pnpm store is measured, and filesystem usage is recorded by device/path.
- [x] 3.5 Mark the remaining cleanup tasks complete only after post-action evidence and strict validation; retain a record of skipped/unapproved candidates.
