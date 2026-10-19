# portable-workstation-toolchain Spec Delta

## ADDED Requirements

### Requirement: Declarative Brewfile and LaunchAgent PATH governance for Herdr

The workstation SHALL declare Herdr's Homebrew package owner separately from its host-local LaunchAgent owner. A staged plist MUST NOT be reported as effective runtime configuration. Applying a changed daemon environment SHALL require explicit operator authorization because restarting Herdr can terminate active pane processes.

#### Scenario: Brewfile declares Herdr formula
- **WHEN** the configured Brewfile is inspected and checked without upgrades
- **THEN** it SHALL declare `brew "herdr"` and report any missing dependency without installing it

#### Scenario: LaunchAgent environment is applied to the actual server
- **WHEN** the operator authorizes reloading the exact Herdr LaunchAgent after preserving relevant work
- **THEN** the replacement server process SHALL contain the configured Homebrew/user-local PATH and report normal server availability
- **AND** plist syntax or `herdr server reload-config` alone MUST NOT satisfy this acceptance condition

#### Scenario: Operator preserves active panes
- **WHEN** the operator declines a disruptive LaunchAgent reload
- **THEN** the workflow SHALL leave the daemon running and report PATH activation as staged but incomplete
- **AND** the corresponding implementation task SHALL remain unchecked

#### Scenario: Package and service ownership remain distinct
- **WHEN** the installed formula lacks a service declaration
- **THEN** the runbook SHALL identify the LaunchAgent as host-local rather than claim `brew services` can create or restart it
- **AND** Herdr package updates SHALL remain owned by `brew upgrade herdr`, with running-server activation handled separately

### Requirement: Herdr built-in agent integrations and skill synchronization

The workstation SHALL retain the official integrations and skill for provisioned agents, preserve separate Pi/OMP roots, and distinguish installed files from active session reporting. Integration installation MUST NOT imply that existing agents loaded hooks or that session restoration was exercised.

#### Scenario: Integrations are installed for provisioned agents
- **WHEN** `herdr integration status` is inspected
- **THEN** `pi`, `omp`, `claude`, `codex`, `copilot`, `devin`, `droid`, `kimi`, `opencode`, `kilo`, `hermes`, `qodercli`, `qwen`, `cursor`, `antigravity-cli`, and `grok` SHALL report their installed versions
- **AND** Pi and OMP extensions SHALL remain in separate resolved directories

#### Scenario: Optional agents remain unprovisioned
- **WHEN** `~/.letta` or `~/.mastracode` is absent
- **THEN** provisioning SHALL leave those directories absent rather than create unused hook roots

#### Scenario: Lifecycle reporting is described accurately
- **WHEN** integration capabilities are documented
- **THEN** the runbook SHALL distinguish the five installed lifecycle reporters from session-only integrations and explain any startup/restart requirement
- **AND** verification SHALL label unexercised activation and restore behavior as unverified without forcing agent restarts

#### Scenario: Official skill is synchronized
- **WHEN** the skill manifests and resolved user skill roots are inspected
- **THEN** both manifests SHALL declare `herdr` and the installed skill SHALL retain its `HERDR_ENV=1` caller guard

### Requirement: Herdr operational documentation SHALL describe notifier privacy and execution behavior accurately

The runbook SHALL document the notifier's three-second default polling, blocked/done states, relay-default delivery, optional direct APNs, and enabled-by-default transcript previews. It SHALL use the installed pane/agent CLI surface and MUST NOT imply that notifications are always delivered directly to Apple.

#### Scenario: Relay-default notification data flow
- **WHEN** APNs direct-mode credentials are not configured
- **THEN** documentation SHALL identify the configured relay path and explain that enabled previews can include transcript snippets in notification bodies
- **AND** verification MUST NOT send a push or disclose transcript contents merely to test documentation
