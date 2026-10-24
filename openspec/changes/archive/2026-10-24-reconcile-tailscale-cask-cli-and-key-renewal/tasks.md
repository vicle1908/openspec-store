# Tasks: Reconcile Tailscale Cask CLI Wrapper, Connection State, and Node Key Renewal

## 1. CLI Wrapper & Single-Authority Reconciliation

- [x] 1.1 Inspect `tailscale` binaries on `PATH` and diagnose the `Tailscale/BundleIdentifiers.swift:49: Fatal error: The current bundleIdentifier is unknown to the registry` crash caused by `/opt/homebrew/bin/tailscale` symlinking to `/Applications/Tailscale.app/Contents/MacOS/Tailscale`
- [x] 1.2 Remove `/opt/homebrew/bin/tailscale` symlink and `/tmp/ts-upgrade.log` artifact, verifying `which -a tailscale` resolves exclusively to the `/usr/local/bin/tailscale` shell wrapper (`1.104.2`)

## 2. Tunnel, MagicDNS, and Tailscale Serve Recovery

- [x] 2.1 Bring the `io.tailscale.ipn.macsys.network-extension` (`1.104.2`) daemon online from `BackendState: "Stopped"` to `BackendState: "Running"` via `tailscale up`
- [x] 2.2 Verify `utun2` IPv4/IPv6 assignment (`100.70.16.83`, `fd7a:115c:a1e0::a938:1053`), MagicDNS registration (`tailc6b508.ts.net` → `100.100.100.100`), DERP reachability (`tailscale netcheck`), peer ping (`macbook-pro-ca-l-1`), and Tailscale Serve HTTPS proxy (`https://iosteam-mac-mini.tailc6b508.ts.net` → `http://127.0.0.1:20128`, HTTP `200`)

## 3. Node Key Renewal & Peer-Relay Preference Persistence

- [x] 3.1 Terminate the isolated `chrome-devtools-mcp` Chrome process (`PID 26975`) so macOS URL opens route to the operator's authenticated `victory1908@gmail.com` Chrome instance (`PID 476`)
- [x] 3.2 Trigger Tailscale interactive key renewal (`Tailscale Settings → Accounts → Renew…`) and verify `Self.PublicKey` rotation (`nodekey:875e7cbbafcdf9d9498cc1c1728f5bb4e196c81e6a3889a5cf7b4c059119a108`) and 180-day `Self.KeyExpiry` extension (`2027-04-22T08:37:52Z`)
- [x] 3.3 Re-apply `tailscale set --relay-server-port=41642 --relay-server-static-endpoints="1.54.174.244:41642"` after reauthentication and verify `tailscale debug prefs` retains `RelayServerPort: 41642`, `RelayServerStaticEndpoints: ["1.54.174.244:41642"]`, and `AutoUpdate: {"Check": true, "Apply": true}`

## 4. Specification & Archive Verification

- [x] 4.1 Record live verification outputs in `evidence.md` and validate `reconcile-tailscale-cask-cli-and-key-renewal` with `openspec validate reconcile-tailscale-cask-cli-and-key-renewal --strict --json --store openspec-store`
