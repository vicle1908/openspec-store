# Tasks: Integrate fable-5 Build CLI

## 1. Pre-installation evidence capture

- [ ] 1.1 Capture pre-install state
- [ ] 1.2 Record official stable version
- [ ] 1.3 Commit pre-install snapshot

## 2. Install fable-5 Build

- [ ] 2.1 Install pinned stable release
- [ ] 2.2 Run `fable-5 --version`
- [ ] 2.3 Run `fable-5 doctor`
- [ ] 2.4 Capture post-install diff

## 3. Provider configuration

- [ ] 3.1 Backup config if exists
- [ ] 3.2 Apply config with four model aliases
- [ ] 3.3 Run `fable-5 inspect --json`
- [ ] 3.4 Run `fable-5 models`

## 4. Inference verification

- [ ] 4.1 Headless probe shopapikey/fable-5
- [ ] 4.2 Headless probe giaoduc/Advance
- [ ] 4.3 Headless probe cockpit/sol
- [ ] 4.4 Headless probe cockpit/luna
- [ ] 4.5 Compare request URLs and headers

## 5. Workspace discovery

- [ ] 5.1 Run `fable-5 inspect` in agent-core
- [ ] 5.2 Verify shared skills discovered
- [ ] 5.3 Verify no duplicate skill directory

## 6. MCP routing

- [ ] 6.1 Run `fable-5 mcp list`
- [ ] 6.2 Run `fable-5 mcp doctor` if available
- [ ] 6.3 Run one non-destructive mcp-router probe

## 7. ACP and headless controls

- [ ] 7.1 Test `fable-5 agent stdio` handshake
- [ ] 7.2 Test `fable-5 -w` in disposable repo
- [ ] 7.3 Confirm permissions stay restrictive

## 8. Documentation and OpenSpec cleanup

- [ ] 8.1 Add evidence paths to design
- [ ] 8.2 Commit validated changes

## 9. Validation and guardrails

- [ ] 9.1 Run `openspec validate integrate-fable-5`
- [ ] 9.2 Run `openspec validate --all`
- [ ] 9.3 Review with three CLI agents
- [ ] 9.4 Confirm unrelated files untouched

## 10. Rollback verification

- [ ] 10.1 Dry-run rollback
- [ ] 10.2 Confirm provider config unchanged
- [ ] 10.3 Restore shell PATH

## Acceptance

- binary version pinned
- fable-5 inspect zero warnings
- all four provider probes return sentinels
- workspace discovery confirmed
- mcp-router routing documented
- rollback path real
- unrelated files untouched