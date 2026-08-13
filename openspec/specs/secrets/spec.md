## Purpose
Ensures sensitive values such as API keys and tokens are automatically redacted from tool output so they are never leaked in logs, chat transcripts, or shell output.

## Requirements

### Requirement: secrets.enabled
`secrets.enabled` SHALL be set to `true` in `~/.omp/agent/config.yml`. When enabled, the harness scans tool output for patterns matching known secret formats and replaces matches with a redacted placeholder before delivering the output to the user or persisting it.

#### Scenario: API key appears in tool output
- **WHEN** a tool invocation returns output containing a string that matches a registered secret pattern (e.g. an API key, bearer token, or password)
- **THEN** the matching value SHALL be replaced with `<REDACTED>` (or equivalent masked token) before the output is displayed or stored

#### Scenario: secrets.enabled is false
- **WHEN** `secrets.enabled` is explicitly set to `false` in `config.yml`
- **THEN** secrets SHALL appear unredacted in all tool output, and the harness SHALL emit a warning log entry indicating that secret redaction is disabled

#### Scenario: No secrets present in output
- **WHEN** tool output does not contain any strings matching registered secret patterns
- **THEN** the output SHALL be delivered unchanged with no redaction overhead