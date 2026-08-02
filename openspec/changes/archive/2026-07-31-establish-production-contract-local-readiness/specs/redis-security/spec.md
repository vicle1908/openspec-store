## MODIFIED Requirements

### Requirement: RS-002: TLS Encryption

TLS SHALL be enabled for all Redis communication in production-contract and
strict modes, and the non-TLS port SHALL be disabled. Production-contract SHALL
use a run-scoped local trust root and workload certificates; strict mode SHALL
consume certificates from the selected non-local certificate provider. Clients
SHALL verify the Redis identity and SHALL present an authorized client
certificate. Local-fast MAY use the documented insecure compatibility path but
MUST NOT produce readiness evidence.

#### Scenario: TLS-only mode starts
- **WHEN** Redis starts in production-contract or strict mode
- **THEN** the non-TLS listener is disabled and the TLS listener has complete certificate, key, CA, and client-authentication inputs

#### Scenario: Client TLS connection succeeds
- **WHEN** an authorized service connects with a certificate trusted by Redis and verifies the Redis identity
- **THEN** the connection uses TLS 1.2 or higher and proceeds to ACL authorization

#### Scenario: Local production-contract certificates are generated
- **WHEN** production-contract startup creates its run-scoped PKI
- **THEN** Redis and client certificates are unique to that run, mounted through secret files, and removed by owned cleanup

#### Scenario: Local-fast Redis evidence is submitted
- **WHEN** Redis uses the local-fast insecure path
- **THEN** aggregate production-contract readiness rejects the artifact

### Requirement: RS-005: Credential Management

Redis passwords, ACL credentials, private keys, and trust material SHALL be
supplied through secret-file mounts in production-contract and through
Kubernetes Secrets backed by the selected secret provider in strict mode. They
MUST NOT appear in ConfigMaps, Compose environment values, command arguments,
rendered configuration, logs, or retained evidence. Local-fast MAY use
disposable environment values only when explicitly selected and labeled
non-evidentiary.

#### Scenario: Kubernetes Secret is mounted
- **WHEN** a strict-mode Redis workload starts
- **THEN** it reads credentials and key material from referenced Secret mounts
- **AND** values are absent from ConfigMaps and observable output

#### Scenario: Compose production-contract secrets are rendered
- **WHEN** `docker compose config` is executed for production-contract
- **THEN** it contains only secret references and mount targets
- **AND** no Redis password, private key, or reusable credential value appears

#### Scenario: Redis secret appears in evidence
- **WHEN** a retained artifact contains a Redis password or private key pattern
- **THEN** redaction validation fails the readiness run and reports only the artifact and secret category

