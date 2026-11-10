# Spec Delta: agentmemory-provider-stability

## ADDED Requirements

### Requirement: Managed AgentMemory LaunchAgent PATH and mesh patch parity across peers

Managed AgentMemory launchd service plists across peer workstations SHALL include `/usr/sbin:/sbin` in `PATH` and omit `AGENTMEMORY_URL` to prevent `readMacProcessExecutable()` process-identity crash loops. When upgrading pinned engine versions, running daemons SHALL be stopped before service restarts, and mesh routing fixes (#1, #2, #3) SHALL be kept in parity across all cluster peers.

#### Scenario: LaunchAgent PATH includes /usr/sbin and omits AGENTMEMORY_URL
- **WHEN** `com.agentmemory.server.plist` on `iosteam-mac-mini` or `local.shb.agentmemory.worker.plist` on `macbook-pro-m5` is loaded by launchd
- **THEN** `EnvironmentVariables.PATH` SHALL contain `/usr/sbin:/sbin` so `readMacProcessExecutable()` resolves `/usr/sbin/lsof` without `ENOENT`
- **AND** `EnvironmentVariables` SHALL omit `AGENTMEMORY_URL` so worker daemons do not crash-loop on self-directed HTTP loopback probes.

#### Scenario: AgentMemory engine pin upgrade stops running daemon before kickstart
- **WHEN** an npm global upgrade of `@agentmemory/agentmemory` bumps `IIPINNED_VERSION` (such as `0.25.0` to `0.25.1`)
- **THEN** workstation update runners SHALL invoke `agentmemory stop` or terminate existing `iii compose` daemon processes before kickstarting launchd services
- **AND** the newly pinned engine binary SHALL start cleanly without port binding collisions or stale process identity locks.

#### Scenario: Mesh routing patches 1, 2, and 3 are maintained in parity across peers
- **WHEN** `@agentmemory/agentmemory@0.9.33` executes mesh replication or peer management across `iosteam-mac-mini` and `macbook-pro-m5`
- **THEN** `dist/index.mjs` on both nodes SHALL enforce Mesh Fix #1 (`syncStartedAt`), Mesh Fix #2 (IPv6 bracket stripping in `isAllowedUrl`), and Mesh Fix #3 (`pinGraphState` in `mem::mesh-remove` and `DELETE /agentmemory/mesh/peers/:id`)
- **AND** bidirectional mesh synchronization over Tailscale L4 port `3111` SHALL operate without unhandled promise rejections or peer removal exceptions.
