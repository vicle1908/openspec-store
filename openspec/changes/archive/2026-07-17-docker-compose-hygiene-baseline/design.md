# Design: Docker Compose Hygiene Baseline

## Current State

### `agent-core/compose.yaml`
- Modern: `name:`, no `version:`, service-based `docker compose exec`, healthchecks everywhere.
- Gap: no explicit `networks:` — uses default bridge (acceptable for local dev).

### `jira-skill/docker-compose.yml`
- Has `networks:`, healthchecks, `restart: unless-stopped`.
- Security issue: `GF_SECURITY_ADMIN_PASSWORD=admin` is a default admin credential.
- Metadata gap: missing `name:`, has `version: '3.8'`.
- Portability gap: `container_name:` on every service prevents `docker compose exec <service>`.

### `bootstrap-nexus-for-mobile/docker-compose.yml`
- Has `ulimits`, healthcheck, `restart: unless-stopped`.
- Metadata gap: missing `name:`, has `version: '3.8'`.
- Portability gap: `container_name:` on both services.

## Proposed Changes

### 1. Security: Grafana credentials

**Current**:
```yaml
environment:
  - GF_SECURITY_ADMIN_USER=admin
  - GF_SECURITY_ADMIN_PASSWORD=admin
```

**Proposed**: Use an `.env`-style placeholder so operators set real credentials.
```yaml
environment:
  - GF_SECURITY_ADMIN_USER=${GF_ADMIN_USER:-admin}
  - GF_SECURITY_ADMIN_PASSWORD=${GF_ADMIN_PASSWORD:-changeme}
```

Default `admin`/`changeme` forces operators to set env vars. Document in README.

### 2. Metadata: add `name:`, drop `version:`

Remove `version: '3.8'` and add:
```yaml
name: jira-skill
```
```yaml
name: nexus-mobile
```

### 3. Portability: remove `container_name:` where not required

`container_name:` is removed from all services except where a downstream tool
depends on the exact name. After audit:

- `jira-skill`: all `container_name:` can be removed — no external tooling hardcodes them.
- `bootstrap-nexus-for-mobile`: same.

Docker Compose v2 generates deterministic names: `{project}_{service}_{index}`.
All scripts should use `docker compose exec <service>` rather than raw names.

### 4. Redis healthcheck fix (bonus)

**Current**:
```yaml
command: redis-server --appendonly yes --requirepass redis_pass
healthcheck:
  test: ["CMD", "redis-cli", "--raw", "incr", "ping"]
```

The healthcheck does not pass `-a redis_pass`, so it will always fail if the
password is honored. Fix:
```yaml
healthcheck:
  test: ["CMD", "redis-cli", "--no-auth-warning", "-a", "redis_pass", "ping"]
```

## Implementation Order

1. Fix Grafana credentials (security — highest priority).
2. Add `name:`, drop `version:` from `jira-silk/docker-compose.yml`.
3. Remove `container_name:` from `jira-skill/docker-compose.yml`.
4. Add `name:`, drop `version:` from `bootstrap-nexus-for-mobile/docker-compose.yml`.
5. Remove `container_name:` from `bootstrap-nexus-for-mobile/docker-compose.yml`.
6. Fix Redis healthcheck password.
7. Update any scripts/docs that hardcode old container names.
