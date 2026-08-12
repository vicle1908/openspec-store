# Proposal: Verify Hermes WebUI iPhone access

## Summary

Verify that Hermes WebUI is reachable from an iPhone over Tailscale and usable
through the Hermex app. This is the device-side acceptance gate for the
`setup-hermes-webui-tailscale-access` change, which completed all server-side
infrastructure setup and deferred iPhone acceptance to this change.

## Why

The server-side setup (Hermes WebUI on port 8787, Tailscale Serve HTTPS,
password auth, launchd persistence) is complete and verified from the Mac Mini.
Device-side acceptance from the iPhone has not yet been confirmed — HTTPS
reachability from Safari and authenticated chat through Hermex remain untested.

## What Changes

- iPhone Safari: open `/health` via Tailscale HTTPS, confirm `status=ok`
- Hermex: configure server URL and password, send authenticated test message
- Document acceptance results

## Out of Scope

- Server-side infrastructure changes (handled in setup change)
- Password rotation or service restarts
