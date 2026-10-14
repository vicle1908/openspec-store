# Design

## Context

See `proposal.md` for overall motivation. OmniRoute runs containerized on macOS via Docker Desktop (`omniroute` container on ports `20128` and `20129`). The SQLite database resides on a Docker named volume (`omniroute-data`) mounted at `/app/data/storage.sqlite`.

Currently:
1. OmniRoute ships 45 official agent skills in `/Users/androidteam/Omniroute/skills/`.
2. The workstation maintains 70+ global agent skills in `~/.agents/skills/`, managed via `npx skills`.
3. The active API key `mac-mini-1` (retrieved by `~/.claude/helpers/omniroute-key.sh` from line 24 of `~/.zshenv`) is currently restricted to `["self:usage"]` in `api_keys`, causing OmniRoute's management policy guard (`hasManageScope`) to reject `/api/*` calls with `HTTP 403 Invalid management token`.
4. The host lacks a functional `omniroute` CLI binary on `$PATH`, while REST endpoints on `http://127.0.0.1:20128` are fully responsive.
5. In `~/.zshenv`, lines 15–33 are strictly governed by the OpenSpec spec `standardize-zshenv-shared-secrets` bounded by `# BEGIN shared-agent-secrets` and `# END shared-agent-secrets`.
6. In `~/.zshrc`, line 221 exports `OMNIROUTE_BASE_URL=http://localhost:20128/v1`, while line 223 exports `COPILOT_PROVIDER_BASE_URL=http://localhost:20128/v1`. Because `~/.zshrc` is evaluated after `~/.zshenv` in interactive shells, this startup order overrides any normalized `OMNIROUTE_BASE_URL` with a trailing `/v1`, causing CLI and management tools to produce 404 errors.

## Goals / Non-Goals

**Goals:**
- Install all 45 official OmniRoute skills into `~/.agents/skills/` using `npx skills` targeting the local repository `/Users/androidteam/Omniroute`.
- Update the active API key `mac-mini-1` in `/app/data/storage.sqlite` to grant `["self:usage", "manage", "admin"]` scopes.
- Standardize environment variables in `~/.zshenv` (`OMNIROUTE_URL="http://localhost:20128"`, `OMNIROUTE_BASE_URL="http://localhost:20128"`, and `OMNIROUTE_KEY="$OMNIROUTE_API_KEY"`), placed strictly after line 41 outside `# BEGIN/END shared-agent-secrets`.
- Normalize `~/.zshrc` line 221 to `export OMNIROUTE_BASE_URL=http://localhost:20128`, eliminating the interactive startup order conflict while keeping `COPILOT_PROVIDER_BASE_URL=http://localhost:20128/v1` intact.
- Author an operational guide at `/Users/androidteam/Developer/docs/omniroute-agent-skills.md` detailing all 22 `omni-*` REST skills and update `/Users/androidteam/Developer/wiki/entities/omniroute.md`.

**Non-Goals:**
- Creating or troubleshooting the host CLI binary wrapper (`~/.local/bin/omniroute`) or running `cli-*` commands (strictly deferred to a subsequent change).
- Modifying Docker container definitions, Next.js build configuration, or container entrypoints.
- Changing provider API credentials, upstream model configurations, or active routing combos.

## Decisions

### 1. Local Repository Installation via `npx skills add -g --all`
- **Choice**: Execute `npx skills add /Users/androidteam/Omniroute -g --all`.
- **Rationale**: Local path resolution executes in ~1.0 second compared to ~108 seconds for remote Git cloning. Furthermore, `npx skills` creates symlinks from the local repository directory into `~/.agents/skills/`, ensuring that future git pulls in `~/Omniroute` immediately propagate without manual reinstallation.
- **Alternatives considered**: Cloning from `github.com/diegosouzapw/OmniRoute` (slow, requires network egress, creates decoupled file copies).

### 2. In-Place SQLite Scope Elevation for `mac-mini-1`
- **Choice**: Execute atomic update in container:
  ```bash
  docker exec omniroute node -e "
  const Database = require('better-sqlite3');
  const db = new Database('/app/data/storage.sqlite');
  db.prepare(\"UPDATE api_keys SET scopes = '[\"\"self:usage\"\",\"\"manage\"\",\"\"admin\"\"]' WHERE name = 'mac-mini-1'\").run();
  console.log('Updated scopes:', db.prepare(\"SELECT name, scopes FROM api_keys WHERE name = 'mac-mini-1'\").get());
  "
  ```
- **Rationale**: `mac-mini-1` is already integrated across developer dotfiles (`~/.zshenv`, `~/.claude/helpers/omniroute-key.sh`, and Claude profiles). Elevating its scopes preserves seamless backward compatibility for existing inference launchers while immediately unlocking management endpoints.
- **Cache Invalidation**: OmniRoute caches API key metadata in memory with a 60-second TTL (`CACHE_TTL = 60 * 1000` in `src/lib/db/apiKeys.ts:197`). Scope elevation takes effect automatically within 60 seconds without restarting the container.
- **Alternatives considered**: Generating a new secondary key. Rejected because it would require synchronizing new secret environment variables across multiple agent configs and LaunchAgents.

### 3. Decoupling Skills Adoption from CLI Wrapper Resolution
- **Choice**: Onboard all skills and elevate management permissions in this change, while explicitly documenting that `cli-*` commands depend on the upcoming CLI wrapper change.
- **Rationale**: The user specifically requested addressing skills adoption first and handling CLI wrapper issues in a separate change. `omni-*` skills interact directly with REST endpoints via standard HTTP, requiring no host CLI binary.
- **Alternatives considered**: Bundling the CLI bridge in this change. Rejected per explicit user guidance.

### 4. Canonical URL Normalization and Startup Order Harmonization
- **Choice**:
  1. Export `OMNIROUTE_URL="http://localhost:20128"`, `OMNIROUTE_BASE_URL="http://localhost:20128"`, and `OMNIROUTE_KEY="$OMNIROUTE_API_KEY"` at the bottom of `~/.zshenv` (line 43+, outside `# BEGIN/END shared-agent-secrets`).
  2. Update `~/.zshrc` line 221 from `export OMNIROUTE_BASE_URL=http://localhost:20128/v1` to `export OMNIROUTE_BASE_URL=http://localhost:20128`.
- **Rationale**:
  - `OMNIROUTE_API_KEY` is already present at line 24 inside the managed secrets block. We do not edit lines 15–33 to uphold the `standardize-zshenv-shared-secrets` invariant.
  - In zsh startup sequence, `~/.zshrc` runs after `~/.zshenv` for interactive shells. If line 221 in `~/.zshrc` kept `/v1`, it would clobber the normalized URL in interactive terminals.
  - GitHub Copilot CLI uses `COPILOT_PROVIDER_BASE_URL` on line 223 (`http://localhost:20128/v1`), so normalizing `OMNIROUTE_BASE_URL` on line 221 does not impact Copilot.
  - Setting both `OMNIROUTE_URL` and `OMNIROUTE_BASE_URL` to `http://localhost:20128` without `/v1` guarantees that all management routes (`/api/...`) resolve without 404 errors across both interactive and automated agent subshells.

### 5. Knowledge Hub Synchronization
- **Choice**: Author `docs/omniroute-agent-skills.md` with complete curl recipes and update `wiki/entities/omniroute.md` to reference the adopted skill surface.
- **Rationale**: Align with the repository workspace convention documented in `CLAUDE.md` and `WORKSPACE_TOPOLOGY.md`.

## Risks / Trade-offs

| Risk | Mitigation |
| :--- | :--- |
| Agent attempts to invoke a `cli-*` command before wrapper is implemented | Documentation explicitly marks `omni-*` as active REST surface and details that `cli-*` requires the companion CLI change. |
| SQLite database concurrency conflict during scope update | Container uses SQLite WAL mode on Docker named volume. Update is executed via atomic single-row transaction inside container runtime. |
| Overlapping skill names with existing skills | Inspected current `~/.agents/skills/` catalog (70+ items). All OmniRoute skills use `omni-*` and `cli-*` prefixes, resulting in zero name collisions. |
| Accidental drift of `standardize-zshenv-shared-secrets` | Shell exports are appended strictly to the file trailer (line 43+), keeping the managed block byte-identical. |
| Interactive shell overwriting base URL | Harmonizing `~/.zshrc` line 221 to `http://localhost:20128` prevents interactive shell override conflicts. |
