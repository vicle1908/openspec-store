# Spec Delta: workstation-tailscale-connectivity

## ADDED Requirements

### Requirement: Cross-node Meta Muse Code and coding CLI parity on macbook-pro-m5

Remote peer `macbook-pro-m5` (`100.106.143.78`) SHALL maintain coding CLI and Meta Muse Code configuration parity with `iosteam-mac-mini` (`100.70.16.83`), routing LLM completions to the central OmniRoute instance via `http://100.70.16.83:20128/v1` with mode-`0600` file-backed credentials (`schema_version: 1`), and participating in bidirectional AgentMemory L4 mesh synchronization over port `3111`.

#### Scenario: Meta Muse Code on macbook-pro-m5 routes to central OmniRoute with file credentials
- **WHEN** `muse` executes commands or completions on `macbook-pro-m5` (`100.106.143.78`)
- **THEN** `~/.config/muse/settings.json` SHALL configure `api_endpoint` pointing to `http://100.70.16.83:20128/v1`
- **AND** `~/.config/muse/auth.json` SHALL exist with permissions `0600`, directory `~/.config/muse` with `0700`, containing `schema_version: 1` (`TBH_CREDENTIAL_BACKEND=file`) without referencing `login.keychain-db` or triggering `SecurityAgent` credential dialogs.

#### Scenario: Bidirectional AgentMemory port 3111 mesh synchronization parity
- **WHEN** AgentMemory mesh synchronization runs between `iosteam-mac-mini` (`100.70.16.83:3111`) and `macbook-pro-m5` (`100.106.143.78:3111`)
- **THEN** Tailscale L4 TCP port `3111` SHALL be reachable bidirectionally over the tailnet without requiring public internet exposure
- **AND** both nodes SHALL execute matching `@agentmemory/agentmemory@0.9.33` runtime code with identical mesh patches.

#### Scenario: Coding CLI versions and toolchain alignment on macbook-pro-m5
- **WHEN** toolchain auditing inspects coding CLIs on `macbook-pro-m5`
- **THEN** installed versions SHALL align with canonical workstation standards: `claude` (single authority `2.1.322`), `ntn` (`0.23.28`), `pnpm` (`12.18.0`), `browser-use` (`1.0.0` GA), `graphify` (`0.9.105` skill sync), and `muse-code` (`1.4.14-R7309.1`).
