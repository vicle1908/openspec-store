# Evidence: reconcile-tailscale-cask-cli-and-key-renewal

**Date:** 2026-10-24
**Change:** `reconcile-tailscale-cask-cli-and-key-renewal`

---

## 1. CLI Wrapper & Cask Authority Verification

Removed the broken `/opt/homebrew/bin/tailscale` symlink (which crashed with `Tailscale/BundleIdentifiers.swift:49: Fatal error: The current bundleIdentifier is unknown to the registry` because `CFBundleGetMainBundle()` resolved `/opt/homebrew/bin` instead of `/Applications/Tailscale.app/Contents`).

```
$ which -a tailscale
/usr/local/bin/tailscale

$ cat /usr/local/bin/tailscale
#!/bin/sh
/Applications/Tailscale.app/Contents/MacOS/Tailscale "$@"

$ tailscale version
1.104.2
  tailscale commit: c3430f0d2b8a1d646ad3ae867e3470bac07f1fe0
  long version: 1.104.2-tc3430f0d2-g598b63867
  other commit: 598b63867959ac210c6a32b7961bb33eb57314db
  go version: go1.27.3 (tailscale/go 7ef7b40364)
```

## 2. Tunnel, MagicDNS, Netcheck, and Tailscale Serve Recovery

Brought `io.tailscale.ipn.macsys.network-extension` (`1.104.2/101.104.2`) from `BackendState: "Stopped"` to `BackendState: "Running"` via `tailscale up`.

```
$ ifconfig | grep -A 3 "inet 100\.70\.16\.83"
	inet 100.70.16.83 --> 100.70.16.83 netmask 0xffffffff
	inet6 fd7a:115c:a1e0::a938:1053 prefixlen 48 
	nd6 options=201<PERFORMNUD,DAD>

$ scutil --dns | grep -A 6 "tailc6b508\.ts\.net"
  search domain[0] : tailc6b508.ts.net
  nameserver[0] : 100.100.100.100
  nameserver[1] : fd7a:115c:a1e0::53
  if_index : 25 (utun2)
  flags    : Supplemental, Request A records, Request AAAA records
  reach    : 0x00000003 (Reachable,Transient Connection)
  order    : 100800

$ tailscale serve status
https://iosteam-mac-mini.tailc6b508.ts.net (tailnet only)
|-- / proxy http://127.0.0.1:20128

$ curl -sS -o /dev/null -w "omniroute_20128_http=%{http_code}\n" http://127.0.0.1:20128/api/monitoring/health
omniroute_20128_http=200
```

## 3. Node Key Renewal & Peer-Relay Preference Persistence

Terminated isolated `chrome-devtools-mcp` Chrome (`PID 26975`), triggered `Tailscale Settings → Accounts → Renew…` via `victory1908@gmail.com` Chrome (`PID 476`), rotated the node key from `nodekey:f51e50dc41cfd0ee4d78bb2cdb75872dcb7f2133c1b77c5bc07f059ea9061052` (expiring `2026-10-25T06:42:19Z`) to `nodekey:875e7cbbafcdf9d9498cc1c1728f5bb4e196c81e6a3889a5cf7b4c059119a108` (expiring `2027-04-22T08:37:52Z`), and re-applied `tailscale set --relay-server-port=41642 --relay-server-static-endpoints="1.54.174.244:41642"`.

```
$ tailscale debug prefs | jq '{WantRunning, RouteAll, CorpDNS, RelayServerPort, RelayServerStaticEndpoints, AutoUpdate}'
{
  "WantRunning": true,
  "RouteAll": true,
  "CorpDNS": true,
  "RelayServerPort": 41642,
  "RelayServerStaticEndpoints": [
    "1.54.174.244:41642"
  ],
  "AutoUpdate": {
    "Check": true,
    "Apply": true
  }
}

$ tailscale status --json | jq '{BackendState, Health, Self: {HostName: .Self.HostName, DNSName: .Self.DNSName, TailscaleIPs: .Self.TailscaleIPs, Online: .Self.Online, KeyExpiry: .Self.KeyExpiry, PublicKey: .Self.PublicKey, Relay: .Self.Relay}}'
{
  "BackendState": "Running",
  "Health": [],
  "Self": {
    "HostName": "iOSTeam Mac Mini",
    "DNSName": "iosteam-mac-mini.tailc6b508.ts.net.",
    "TailscaleIPs": [
      "100.70.16.83",
      "fd7a:115c:a1e0::a938:1053"
    ],
    "Online": true,
    "KeyExpiry": "2027-04-22T08:37:52Z",
    "PublicKey": "nodekey:875e7cbbafcdf9d9498cc1c1728f5bb4e196c81e6a3889a5cf7b4c059119a108",
    "Relay": "hkg"
  }
}
```
