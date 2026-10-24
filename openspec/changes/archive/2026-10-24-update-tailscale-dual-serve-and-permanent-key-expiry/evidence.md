# Evidence: update-tailscale-dual-serve-and-permanent-key-expiry

**Date:** 2026-10-24
**Change:** `update-tailscale-dual-serve-and-permanent-key-expiry`

---

## 1. Permanent Key Expiry Verification (`KeyExpiry: null` / `Never`)

```
$ tailscale debug netmap | jq '.SelfNode | {ID, StableID, Name, Key, KeyExpiry, Expired}'
{
  "ID": 7913897482312279,
  "StableID": "nxbJehfDo421CNTRL",
  "Name": "iosteam-mac-mini.tailc6b508.ts.net.",
  "Key": "nodekey:875e7cbbafcdf9d9498cc1c1728f5bb4e196c81e6a3889a5cf7b4c059119a108",
  "KeyExpiry": null,
  "Expired": null
}
```

Tailscale macOS GUI (`window 3718` detail view for `iosteam-mac-mini`):
- `statictext [ref=e361]: "Key expiry"`
- `statictext [ref=e362]: "Never"`

## 2. Dual-Port Tailscale Serve (`:443` OmniRoute & `:8443` Hermes WebUI)

```
$ tailscale serve --bg --https=8443 http://127.0.0.1:8787
Available within your tailnet:

https://iosteam-mac-mini.tailc6b508.ts.net:8443/
|-- proxy http://127.0.0.1:8787

$ tailscale serve status --json
{
  "TCP": {
    "443": {
      "HTTPS": true
    },
    "8443": {
      "HTTPS": true
    }
  },
  "Web": {
    "iosteam-mac-mini.tailc6b508.ts.net:443": {
      "Handlers": {
        "/": {
          "Proxy": "http://127.0.0.1:20128"
        }
      }
    },
    "iosteam-mac-mini.tailc6b508.ts.net:8443": {
      "Handlers": {
        "/": {
          "Proxy": "http://127.0.0.1:8787"
        }
      }
    }
  }
}
```

## 3. Peer Connectivity & Double-NAT Relay Socket Verification

```
$ netstat -an -p udp | grep -E '41641|41642'
udp6       0      0  *.41642                *.*                               
udp4       0      0  *.41642                *.*                               
udp4       0      0  *.41641                *.*                               
udp6       0      0  *.41641                *.*                               

$ tailscale ping -c 2 iphone-15-pro-max
pong from iphone-15-pro-max (100.118.93.42) via 192.168.10.67:41641 in 8ms

$ tailscale ping -c 2 macbook-pro-ca-l-1
pong from macbook-pro-ca-l-1 (100.101.64.56) via DERP(sin) in 105ms
pong from macbook-pro-ca-l-1 (100.101.64.56) via DERP(sin) in 107ms
```
