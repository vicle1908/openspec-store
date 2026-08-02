# ADR 005: nginx Reverse Proxy over Direct Nexus Exposure

## Status

Accepted

## Context

Nexus exposes port 8081 by default. We need to decide how clients (developers, CI) access it.

Options:
- Expose nexus:8081 directly on host
- Use nginx reverse proxy on port 80/443
- Use cloud load balancer

**Additional constraint**: The Swift Package Registry API [requires TLS](https://github.com/apple/swift-package-manager/blob/main/Documentation/PackageRegistry/Registry.md) (`https` URI scheme mandatory). This makes the nginx SSL configuration higher priority than originally scoped.

## Decision

We will use **nginx as a reverse proxy** on port 80 (and placeholder for 443). Nexus port 8081 will NOT be bound to the host; it will only be accessible via Docker internal network.

## Consequences

### Positive

- **Single entry point**: All traffic goes through nginx
- **SSL termination ready**: nginx config can be extended with certificates (required for SPM clients)
- **Large upload support**: `client_max_body_size 1G` for AARs and Swift ZIPs
- **Request buffering control**: Disabled for streaming uploads
- **Header injection**: `X-Forwarded-*` headers for proper URL generation
- **Security isolation**: Nexus not directly reachable from host network

### Negative

- **Additional container**: One more service to manage
- **Slightly more latency**: One extra hop
- **Config maintenance**: nginx.conf must be kept in sync
- **SSL cert management**: Required for SPM clients; deferred TLS cert provisioning adds operational step

## Alternatives Considered

| Alternative | Rejected Because |
|------------|-----------------|
| Direct nexus:8081 exposure | No SSL path; no upload size control; direct attack surface |
| Traefik | More complex; overkill for single service |
| Cloud load balancer (AWS ALB) | Requires cloud infrastructure; not self-hosted |
| Application-level SSL in Nexus | Complex configuration; nginx handles this better |

## Validation

- ✅ nginx forwards to nexus:8081 correctly
- ✅ Uploads >100MB succeed (AARs and Swift ZIPs)
- ✅ `docker compose ps` shows only nginx ports exposed on host
