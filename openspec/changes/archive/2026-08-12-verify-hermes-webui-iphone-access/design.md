# Design: iPhone acceptance verification

## Approach

Acceptance testing is performed from the iPhone itself, not the Mac Mini. The
Mac Mini cannot verify iPhone-side Tailscale connectivity due to hairpin NAT
behavior (HTTPS self-curl times out).

## Verification path

1. iPhone connects to Tailscale (already confirmed via `tailscale ping` —
   3 pongs via DERP relay)
2. Safari opens `https://iosteam-mac-mini.tailc6b508.ts.net/health`
3. Verify JSON response contains `"status":"ok"`
4. Hermex configured with server URL and password
5. Authenticated chat message sent and response received

## Constraints

- iPhone must be on the `victory1908` tailnet (confirmed active)
- DERP relay adds 150–370ms latency (acceptable for chat UI)
- No server-side changes required — infrastructure is complete
