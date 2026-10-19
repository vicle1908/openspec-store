# workstation-remote-and-agent-permissions Spec Delta

## ADDED Requirements

### Requirement: Herdr multiplexer daemon and companion notifier SHALL maintain full macOS TCC permissions

The workstation SHALL retain verified Accessibility, Screen Recording, and Full Disk Access grants for Herdr and the existing shared host Python automation identities. These grants MUST be classified as host automation authority, not as dependencies of notifier polling or transcript reads. Automation verification SHALL identify its tested receiver explicitly.

#### Scenario: Herdr server executable holds valid grants
- **WHEN** the active Herdr executable is audited
- **THEN** its path-based identity SHALL have allowed Accessibility, Screen Recording, and Full Disk Access records whose signing requirements accept that executable
- **AND** a database row alone MUST NOT be reported as functional proof for every child process

#### Scenario: In-pane verification identifies the tested sender and receiver
- **WHEN** an authorized probe inside a Herdr pane checks Accessibility, Screen Recording, protected read access, and AppleEvents to System Events
- **THEN** the report SHALL record the pane context, actual results, and System Events as the receiver
- **AND** the result MUST NOT imply authorization for arbitrary AppleEvents receivers or root/SIP bypass

#### Scenario: Shared Python grants are not misattributed to the notifier
- **WHEN** the active Python automation executable and applicable framework bundle identity are audited
- **THEN** their existing three-service policy SHALL be verified against their current signing identities
- **AND** documentation SHALL state that the notifier uses configured files, Herdr queries, and outbound delivery, not Accessibility or screen capture

#### Scenario: Authorization audit does not weaken security
- **WHEN** verification or remediation runs
- **THEN** it MUST NOT modify TCC records, relax authorizationdb rights, grant/revoke permissions, or bypass consent as a verification side effect

### Requirement: Post-upgrade TCC provenance verification SHALL include Herdr and active agent CLIs

Scheduled and manual checks SHALL detect required executable, service, and signing-identity failures. A clean result SHALL require a nonempty, fully verified target set. Canonical agents require Accessibility and Screen Recording; Herdr, OMP and the existing shared Python automation identities additionally require Full Disk Access. Required Darwin verification errors MUST NOT be classified as successful skips.

#### Scenario: All required identities satisfy their role policy
- **WHEN** all required executables resolve, exist, and have allowed records satisfying their current code identity and required services
- **THEN** both maintenance runners SHALL report a clean provenance result
- **AND** their output SHALL identify verified identities and no missing required targets

#### Scenario: Signature changes at the same path
- **WHEN** a required executable no longer satisfies a granted record's stored signing requirement
- **THEN** verification SHALL report drift even if the path and authorization integer are unchanged
- **AND** missing or malformed signing requirements MUST NOT pass

#### Scenario: Required executable or service is missing
- **WHEN** a required name cannot resolve, its executable is missing, the target set is empty, or a required grant is absent or denied
- **THEN** verification SHALL report a non-clean result identifying the failure
- **AND** missing Full Disk Access for Herdr or a declared shared automation identity MUST NOT pass

#### Scenario: Required verification infrastructure fails on Darwin
- **WHEN** TCC data is absent, unreadable or corrupt, native identity evaluation is unavailable, or verifier output is invalid
- **THEN** the scheduler SHALL report non-success and the fallback SHALL return nonzero
- **AND** non-Darwin checks MAY be reported as explicitly not applicable without claiming grants were verified

#### Scenario: Reporter failure cannot be masked by aggregate success
- **WHEN** a required reporter fails, returns malformed data, or reports inventory drift, target misalignment or unknown authority
- **THEN** the aggregate maintenance result SHALL be non-successful and retain the reason

### Requirement: Herdr verification SHALL respect supported macOS consent behavior

Verification SHALL distinguish current authorization from future consent or reminder behavior. It MUST NOT promise permanent reminder suppression based on private replayd plist values, mutate that plist, or install a recurring suppression workaround. Existing private values SHALL be recorded only as historical unsupported state.

#### Scenario: Private timestamp values already exist
- **WHEN** prior far-future strings are found in ScreenCaptureApprovals.plist
- **THEN** the report SHALL state that their presence does not prove runtime interpretation or permanent suppression
- **AND** remediation SHALL leave them unchanged unless a separate exact mutation is authorized

#### Scenario: macOS requests renewed consent
- **WHEN** macOS presents a permission or capture reminder
- **THEN** the workflow SHALL retain normal operator consent handling rather than suppress or automatically approve the request
