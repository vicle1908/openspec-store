# Evidence: optimize-tailscale-client-port-and-relay-config

**Date:** 2026-10-24
**Change:** `optimize-tailscale-client-port-and-relay-config`

---

## 1. Tailnet Policy Update (`randomize-client-port` & `derpMap` Region 3 Suppression)

Updated `https://login.tailscale.com/admin/acls/file` in the authenticated `victory1908@gmail.com` Chrome session (`Saved tailnet policy file` toast confirmed):

```jsonc
	"nodeAttrs": [
		{
			"target": ["autogroup:member"],
			"attr":   ["funnel", "randomize-client-port"],
		},
	],
	"derpMap": {
		"Regions": {
			"3": null,
		},
	},
```

## 2. `magicsock` Rebind, STUN Endpoint Mapping, and DERP 20 Convergence

Executed `tailscale down && sleep 1 && tailscale up && sleep 2 && tailscale set --relay-server-port=41642 --relay-server-static-endpoints="1.54.174.244:41642" && tailscale netcheck`:

```
$ tailscale debug control-knobs | jq '{RandomizeClientPort}'
{
  "RandomizeClientPort": true
}

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

$ tailscale debug netmap | jq '{SelfEndpoints: .SelfNode.Endpoints, HasRegion3: (.DERPMap.Regions["3"] != null), Peers: [.Peers[] | {Name: .Name, Online: .Online, Endpoints: .Endpoints, HomeDERP: .HomeDERP}]}'
{
  "SelfEndpoints": [
    "1.54.174.244:52816",
    "1.54.174.244:1024",
    "192.168.10.78:52816"
  ],
  "HasRegion3": false,
  "Peers": [
    {
      "Name": "macbook-pro-ca-l-1.tailc6b508.ts.net.",
      "Online": true,
      "Endpoints": [
        "27.67.149.107:29369",
        "27.67.149.107:24031",
        "27.67.149.107:7171",
        "27.67.149.107:41641",
        "192.168.8.172:62200"
      ],
      "HomeDERP": 20
    },
    {
      "Name": "iphone-15-pro-max.tailc6b508.ts.net.",
      "Online": true,
      "Endpoints": [
        "1.54.174.244:52744",
        "26.208.249.0:52744",
        "30.17.253.65:52744",
        "135.32.230.173:52744",
        "192.168.10.67:52744",
        "[2401:d800:73f0:63e8:1045:ee1f:ba64:e53b]:52744",
        "[2401:d800:73f0:63e8:18ee:1506:563b:b444]:52744"
      ],
      "HomeDERP": 20
    }
  ]
}

$ tailscale status --json | jq '.Self | {HostName, DNSName, TailscaleIPs, Relay, KeyExpiry, PublicKey}'
{
  "HostName": "iOSTeam Mac Mini",
  "DNSName": "iosteam-mac-mini.tailc6b508.ts.net.",
  "TailscaleIPs": [
    "100.70.16.83",
    "fd7a:115c:a1e0::a938:1053"
  ],
  "Relay": "hkg",
  "KeyExpiry": null,
  "PublicKey": "nodekey:875e7cbbafcdf9d9498cc1c1728f5bb4e196c81e6a3889a5cf7b4c059119a108"
}
```
