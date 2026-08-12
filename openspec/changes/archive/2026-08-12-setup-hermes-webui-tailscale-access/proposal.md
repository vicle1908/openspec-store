# Proposal: Setup Hermes WebUI for iPhone access via Tailscale

## Summary

Install and configure Hermes WebUI on the local Mac Mini, enable password authentication, and expose it securely over Tailscale for iPhone access via Hermex.

## Why

Access Hermes Agent from iPhone (Hermex app) without exposing the server to the public internet. Tailscale provides encrypted peer-to-peer VPN connectivity; the WebUI serves the chat interface.

## What Changes

- Clone and install hermes-webui (Python stack, not Node.js)
- Configure loopback binding with password authentication
- Remap Docker claude-code-provider-adapter from host port 8787→8788 to free the port
- Configure Tailscale Serve for HTTPS access via MagicDNS hostname
- Create launchd LaunchAgent for auto-start persistence
- Verify end-to-end from local machine; iPhone verification deferred to operator

## Out of Scope

- Exposing via Cloudflare or public reverse proxy
- Modifying Hermes Agent config, models, or providers
- Changing the adapter's internal container port or API contract

## Non-goals

- SSH tunnel setup (Tailscale Serve replaces this need)
- Multi-user access (single-operator password auth)
