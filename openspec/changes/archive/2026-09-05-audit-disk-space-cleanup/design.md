## Context

See `proposal.md` for motivation. The workstation has a primary APFS data filesystem plus a separate Nicegram wrapper mount and possible cloud/FUSE paths. Existing evidence is command output only; no mutation is authorized.

## Goals / Non-Goals

**Goals:**

- Preserve device/filesystem identity with every size claim.
- Use bounded per-root measurements and metadata-only age scans.
- Separate allocated bytes from sparse-file logical size.
- Require exact target approval before any cleanup command.
- Prefer application-native cleanup for Docker and Xcode/Simulator-managed data.

**Non-Goals:**

- No automatic deletion, Trash emptying, cache purge, Docker pruning, or repository cleanup.
- No generic recursive deletion of application state or synced data.
- No interpretation of APFS free capacity as recoverable cleanup space.

## Decisions

- Treat `/Users/androidteam/.Trash`, npm/pnpm caches, and Docker’s reported reclaimable images/volumes as candidate classes, not approved targets.
- Treat `Docker.raw` as a managed VM disk and never as a direct file-deletion target.
- Treat Photos, My Drive, DriveFS, Chrome, agent-memory, Hermes state, active repositories, and global package installations as user/state data.
- Treat CoreSimulator caches as Xcode/Simulator-managed; any cleanup must use supported tooling with Xcode and Simulator state considered.
- Record only path, device/filesystem, allocated size, logical size when relevant, date, and risk; redact contents and credentials.

## Risks / Trade-offs

- Cache cleanup can increase later download/build time.
- Docker volume cleanup can destroy persistent data despite being marked reclaimable; each volume requires inspection and approval.
- Trash contents may include recoverable work; age does not establish disposal intent.
- Cloud-sync paths may have local allocation and remote retention semantics that differ; use the provider application before changing them.
- Sparse VM files make logical `stat` size misleading; `du`/Docker-native reports must drive recovery estimates.
