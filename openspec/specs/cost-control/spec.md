## Purpose
Prevents accidental use of expensive or unintended providers and redirects common shell utilities to their specialized tool equivalents, reducing cost and improving output quality.

## Requirements

### Requirement: disabledProviders
`disabledProviders` SHALL be a list of provider names in `config.yml`. Any provider listed in `disabledProviders` SHALL be excluded from role routing and model selection, and the session SHALL fall back to the next available provider for that role.

#### Scenario: Disabled provider is referenced in a role
- **WHEN** a role's provider list contains a provider that appears in `disabledProviders`
- **THEN** that provider SHALL be skipped and the session SHALL use the next available (non-disabled) provider in the role's fallback sequence

#### Scenario: No available providers after disabling
- **WHEN** all providers configured for a role are listed in `disabledProviders`
- **THEN** the session SHALL emit an error indicating no available providers remain for that role, and SHALL NOT silently fall back to an unintended provider

#### Scenario: Empty disabledProviders
- **WHEN** `disabledProviders` is an empty list or absent from `config.yml`
- **THEN** all configured providers SHALL remain available for routing

### Requirement: bashInterceptor — read tool redirection
`bashInterceptor` SHALL intercept shell commands `cat` and `head`/`tail` when invoked via the bash tool, and redirect them to the `read` tool instead. This ensures consistent output formatting and avoids raw shell output leaking into the session.

#### Scenario: cat is invoked in bash
- **WHEN** the bash tool receives a command beginning with `cat ` targeting a file path
- **THEN** the harness SHALL intercept the command and route it to the `read` tool with the equivalent file path, returning the read tool's formatted output

#### Scenario: head or tail is invoked in bash
- **WHEN** the bash tool receives a command using `head` or `tail` on a file
- **THEN** the harness SHALL intercept the command and route it to the `read` tool with appropriate offset/limit parameters derived from the head/tail arguments

### Requirement: bashInterceptor — grep tool redirection
`bashInterceptor` SHALL intercept shell commands `grep` and `rg` when invoked via the bash tool, and redirect them to the `grep` tool instead. This provides structured search results with file context rather than raw line output.

#### Scenario: grep is invoked in bash
- **WHEN** the bash tool receives a command using `grep` with a pattern and target path(s)
- **THEN** the harness SHALL intercept the command and route it to the `grep` tool with equivalent pattern and path arguments

#### Scenario: rg is invoked in bash
- **WHEN** the bash tool receives a command using `rg` with a pattern and target path(s)
- **THEN** the harness SHALL intercept the command and route it to the `grep` tool with equivalent pattern and path arguments

#### Scenario: Intercepted command has no valid equivalent
- **WHEN** a `grep` or `rg` command cannot be mapped to the `grep` tool (e.g. piping from stdin, exotic flags not supported)
- **THEN** the harness SHALL execute the original shell command without interception and log that the command bypassed the interceptor