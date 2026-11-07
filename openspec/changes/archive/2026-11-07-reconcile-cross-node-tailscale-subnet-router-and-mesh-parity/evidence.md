# Evidence: `reconcile-cross-node-tailscale-subnet-router-and-mesh-parity`

## 1. Cross-Node Runtime & Tailscale Serve Convergence

- **Orca Remote Runtime (`~/Library/Application Support/orca/orca-environments.json`)**:
  - Updated `macbook-pro-m5` (`1a5d8115-5451-435e-acc8-dad1117b2c25`) endpoint to `ws://100.106.143.78:6768`.
  - Verified `orca terminal list --environment macbook-pro-m5 --json` exits `0` (`ok: true`, `totalCount: 11`).
- **Tailscale Serve L4 TCP `:3111` & AgentMemory Mesh Sync**:
  - Enabled `/opt/homebrew/bin/tailscale serve --bg --tcp=3111 127.0.0.1:3111` on `macbook-pro-m5` (`100.106.143.78`).
  - Removed stale `http://100.101.64.56:3111` peer (`peer_mw5qshfq_d4d72fb56e79`) and registered `http://100.106.143.78:3111` (`peer_mw6kngsw_9f780b6d97fc`) on `iosteam-mac-mini`.
  - Verified `POST http://localhost:3111/agentmemory/mesh/sync` succeeded (`pulled: 3, pushed: 0, errors: []`).
- **Zero-Configuration `/32` Subnet Routing & Split DNS Verification**:
  - Verified from `iosteam-mac-mini` (`100.70.16.83`):
    - `tailscale dns query gitlab-nhs.shb.com.vn A` -> `172.16.3.10`
    - `tailscale dns query gitlab.shb.com.vn A` -> `10.4.99.40`
    - `tailscale dns query office.shb.com.vn A` -> `10.4.88.33`
    - `tailscale dns query jira.shb.com.vn A` -> `10.4.88.24`
    - `route -n get 172.16.3.10` -> `interface: utun2`
    - `curl -skI https://gitlab-nhs.shb.com.vn` -> `HTTP/2 302` (`location: https://gitlab-nhs.shb.com.vn/users/sign_in`)

## 2. Provisioning Script & Specification Verification

- **`~/Developer/scripts/setup-macbook-omniroute-client.sh --check`**:
  - On `iosteam-mac-mini` (`role=host`): exited `0` (`Verified 6-port Tailscale Serve topology on host (20128, 20129, 20132, 3111 L4 TCP + 443, 8443 HTTPS)`, `Verified 16 configuration file(s)`).
  - On `macbook-pro-m5` (`role=client`): exited `0` (`Verified Client Tailscale Serve L4 TCP port 3111 -> 127.0.0.1:3111`, `Verified 10 configuration file(s)`).
- **OpenSpec Strict Validation**:
  - `openspec validate workstation-tailscale-connectivity --type spec --strict --store openspec-store` exited `0` with `0` warnings.
