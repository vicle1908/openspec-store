# omp-fresh-shell-contract Specification Delta

## MODIFIED Requirements

### Requirement: Antigravity OAuth Credential Hygiene, Throwaway Profile Cleanup, and MCP Timeout

`~/.omp/agent/agent.db` SHALL omit the HTTP 403-rejected `google-antigravity` OAuth credentials (`vicgnome19091@gmail.com`, `ascenddevtwo@gmail.com`, and `phamkive425@gmail.com`) while retaining the 13 healthy accounts, `~/.omp/profiles/` SHALL contain no leftover `omp-fresh-*` smoke profiles, and `~/.omp/agent/mcp.json` (`mode 0600`) SHALL declare `"$schema"`, `"type": "stdio"`, and `"timeout": 300000` on `mcpServers.mcp-router` while preserving `env.MCPR_TOKEN`.

#### Scenario: Rejected Antigravity OAuth account removed and healthy accounts preserved
- **WHEN** `~/.omp/agent/agent.db` is queried read-only for `auth_credentials`
- **THEN** `SELECT COUNT(*) FROM auth_credentials WHERE provider='google-antigravity' AND identity_key IN ('email:vicgnome19091@gmail.com', 'email:ascenddevtwo@gmail.com', 'email:phamkive425@gmail.com')` SHALL equal `0`
- **AND** `SELECT COUNT(*) FROM auth_credentials WHERE provider='google-antigravity' AND disabled_cause IS NULL` SHALL equal `13`
- **AND** fresh OMP session logs under `~/.omp/logs/` SHALL record zero `status=403` Antigravity usage-fetch or model-discovery warnings

#### Scenario: Stale throwaway smoke profiles absent and mcp.json hardened
- **WHEN** `/Users/androidteam/.omp/profiles` and `/Users/androidteam/.omp/agent/mcp.json` are inspected
- **THEN** `/Users/androidteam/.omp/profiles/omp-fresh-cockpit`, `omp-fresh-giaoduc`, and `omp-fresh-shopapikey` SHALL not exist
- **AND** `/Users/androidteam/.omp/agent/mcp.json` SHALL have permissions `0600`, declare `"$schema"`, configure `mcpServers.mcp-router.type == "stdio"` and `mcpServers.mcp-router.timeout == 300000`, and preserve a non-empty `env.MCPR_TOKEN`
