# ADR 002: Named Docker Volume over Bind Mount

## Status

Accepted

## Context

Nexus Repository runs as user `nexus` (UID 200) inside the container. The data directory `/nexus-data` must persist across container restarts. We need to choose between:
- Named Docker volume (Docker-managed)
- Bind mount (host directory mapped into container)

## Decision

We will use a **named Docker volume** (`nexus-data`) for persistence.

## Consequences

### Positive

- **Permission handling**: Docker manages volume permissions; no UID/GID mapping needed on host
- **Restore simplicity**: `docker run --rm -v nexus-data:/data alpine chown -R 200:200 /data` works reliably
- **Portability**: No host path dependencies; works on macOS, Linux, Windows equally
- **Docker-managed lifecycle**: Volume created/destroyed with Compose

### Negative

- **Opaque storage location**: Data lives in Docker's storage directory (`/var/lib/docker/volumes/`)
- **Harder to access directly**: Need `docker run` with volume mount to inspect files
- **Less visible for monitoring**: Host tools can't easily see disk usage

## Alternatives Considered

| Alternative | Rejected Because |
|------------|-----------------|
| Bind mount (`./nexus-data:/nexus-data`) | UID 200 on host may not exist; permission issues common; chown required on host |
| Host directory with matching UID | Requires creating `nexus` user on host; brittle across environments |
| NFS volume | Adds network dependency; unnecessary complexity |
| Volume driver (e.g., rexray) | Overkill for single-host deployment |

## Validation

- ✅ Nexus container starts without permission errors
- ✅ `nexus-data` volume persists after `docker compose down` and `up`
- ✅ Backup script works: `docker run --rm -v nexus-data:/data alpine tar czf backup.tar.gz -C /data .`
