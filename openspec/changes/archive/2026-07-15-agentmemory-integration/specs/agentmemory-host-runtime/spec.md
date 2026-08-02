# agentmemory-host-runtime Specification

## ADDED Requirements

### Requirement: agentmemory runs as a host process, not a Docker service
The agentmemory server SHALL be installed and run as a host process on the developer machine. It SHALL NOT be added to `deploy/docker-compose.yaml`, `deploy/docker-compose.lgtm.yaml`, `deploy/docker-compose.tools.yaml`, or `deploy/docker-compose.arm64.yaml`. The server SHALL be managed by `scripts/agentmemory-up.sh` and `scripts/agentmemory-down.sh` and SHALL write its pidfile to `~/.agentmemory/run/agentmemory.pid`.

#### Scenario: Server is not in Compose
- **WHEN** a developer inspects every `deploy/docker-compose.*.yaml` file
- **THEN** no service named `agentmemory` appears and no image pin for `node:22-bookworm-slim` or `iiidev/iii` appears (those are upstream dependencies, not the project's pins)

#### Scenario: make verify-images does not need to verify the agentmemory image
- **WHEN** `make verify-images --arch=arm64` runs
- **THEN** the script does not need to verify any node or iii image because the agentmemory runtime is a host process, not a container, and the script exits 0 with no new entry

#### Scenario: make agentmemory-up starts the server
- **WHEN** a developer runs `make agentmemory-up` and no server is already running
- **THEN** `scripts/agentmemory-up.sh` writes the pidfile at `~/.agentmemory/run/agentmemory.pid`, starts `npx @agentmemory/agentmemory` in the background, and waits up to 15 s for `curl -fsS http://localhost:3111/agentmemory/health` to return 200 before exiting 0

#### Scenario: make agentmemory-down stops the server
- **WHEN** a developer runs `make agentmemory-down` and the server is running
- **THEN** the script reads the pidfile, sends `SIGTERM`, waits 5 s, escalates to `SIGKILL` if the process is still alive, and removes the pidfile; state in `~/.agentmemory/data/` is preserved

#### Scenario: Idempotent start
- **WHEN** a developer runs `make agentmemory-up` while the server is already running
- **THEN** the script detects the existing pidfile, verifies the health endpoint is still 200, and exits 0 with the message `agentmemory already running on :3111 (pid <pid>)`

### Requirement: iii-engine is pinned to v0.11.2
The agentmemory server SHALL pin the `iii-engine` to `v0.11.2` exactly. The bootstrap script SHALL NOT install a newer or older engine even if one is available on the host. Override with `AGENTMEMORY_III_VERSION` is permitted only when the developer acknowledges the upstream README's v0.11.6+ compatibility caveat.

#### Scenario: Pinned engine is downloaded
- **WHEN** `make agentmemory-bootstrap` runs on a fresh machine
- **THEN** the engine binary at `~/.agentmemory/bin/iii` reports `iii --version` of exactly `0.11.2`

#### Scenario: Newer engine is rejected
- **WHEN** `AGENTMEMORY_III_VERSION=0.11.6` is exported in the shell and `make agentmemory-bootstrap` runs
- **THEN** the script prints a warning to stderr that 0.11.6 is not yet supported by agentmemory, asks for confirmation, and exits non-zero unless the developer types `yes`

#### Scenario: Host OS / arch detection picks the right tarball
- **WHEN** the bootstrap script runs on `darwin arm64`
- **THEN** it downloads `https://github.com/iii-hq/iii/releases/download/iii/v0.11.2/iii-aarch64-apple-darwin.tar.gz`; on `darwin x64` it downloads `iii-x86_64-apple-darwin.tar.gz`; on `linux x64` it downloads `iii-x86_64-unknown-linux-gnu.tar.gz`; on `linux arm64` it downloads `iii-aarch64-unknown-linux-gnu.tar.gz`

### Requirement: State persists under the user's home directory
The agentmemory server SHALL persist all state under `~/.agentmemory/`. The directory layout SHALL be `~/.agentmemory/{bin,data,log,run,lib,config}`. State SHALL survive `make clean` at the repo root and SHALL NOT be committed to git. The bootstrap script SHALL add `~/.agentmemory/` to the per-developer global gitignore.

#### Scenario: State survives make clean
- **WHEN** a developer runs `make clean` at the repo root
- **THEN** `~/.agentmemory/data/` is untouched and the next `make agentmemory-up` boots the server with all prior memories intact

#### Scenario: State is never committed
- **WHEN** `git status` runs in the repo after `make agentmemory-bootstrap`
- **THEN** no file under `~/.agentmemory/` appears in the untracked-files list (because the path is outside the repo), and a developer-level global gitignore excludes the path on a fresh clone

### Requirement: The viewer is loopback-only
The real-time viewer SHALL bind to `127.0.0.1:3113` only. The viewer SHALL NOT publish to a routable interface, SHALL NOT accept connections from non-loopback addresses, and SHALL emit a CSP header with a per-response script nonce and `script-src-attr 'none'`. Auth SHALL be required when `AGENTMEMORY_SECRET` is set, using a `Bearer` token in the `Authorization` header.

#### Scenario: Viewer refuses non-loopback
- **WHEN** the server starts and a request is made to `<lan-ip>:3113` from another machine
- **THEN** the TCP connection is refused at the OS level (port not bound on the routable interface) and the OS logs the refused connection

#### Scenario: Viewer enforces auth when secret is set
- **WHEN** `AGENTMEMORY_SECRET=devsecret` is in `~/.agentmemory/.env` and a developer curls `http://localhost:3113/agentmemory/viewer` without a token
- **THEN** the response is HTTP 401 with `WWW-Authenticate: Bearer`

### Requirement: Bootstrap is idempotent
The `make agentmemory-bootstrap` target SHALL be safe to re-run. Re-running SHALL NOT clobber an existing `~/.agentmemory/.env` file unless the developer explicitly passes `--reset-env`, SHALL NOT re-download the engine if the pinned version is already present, and SHALL update the agent configs only if they are missing the `agentmemory` entry.

#### Scenario: Re-run is a no-op
- **WHEN** a developer runs `make agentmemory-bootstrap` after a successful first run
- **THEN** the script reports `agentmemory already bootstrapped on :3111` and exits 0 with no changes to the filesystem

#### Scenario: Re-run with --reset-env regenerates the .env
- **WHEN** a developer runs `make agentmemory-bootstrap -- --reset-env`
- **THEN** the script saves a backup of the existing `~/.agentmemory/.env` to `~/.agentmemory/.env.bak-$(date +%s)`, regenerates it from the template, and exits 0

#### Scenario: Re-run updates a missing agent config
- **WHEN** a developer runs `make agentmemory-bootstrap` and `.cursor/mcp.json` exists but does not contain an `agentmemory` key
- **THEN** the script merges the `agentmemory` entry into `.cursor/mcp.json`, preserves all other entries, and exits 0
