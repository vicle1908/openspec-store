# k8s-secrets-integration Specification

## ADDED Requirements

### Requirement: External Secrets Operator integration
The platform SHALL provide ExternalSecret resources at `deploy/k8s/base/externalsecret.yaml` that reference a ClusterSecretStore backed by Vault.

#### Scenario: Secret is synced from Vault
- **WHEN** the ExternalSecret is created
- **THEN** the Secret is created with values fetched from Vault

#### Scenario: Secret updates are detected
- **WHEN** a secret value changes in Vault
- **THEN** the ExternalSecret refreshes within the configured interval (default 1h)

### Requirement: ClusterSecretStore for Vault backend
The platform SHALL provide a ClusterSecretStore at `deploy/k8s/base/clustersecretstore.yaml` configured for Kubernetes authentication to Vault.

#### Scenario: Service account authenticates to Vault
- **WHEN** the ExternalSecret controller needs to fetch secrets
- **THEN** it authenticates to Vault using the service account's JWT token

### Requirement: Secret rotation and refresh
The ExternalSecret SHALL configure a refresh interval ensuring secrets are rotated without pod restarts.

#### Scenario: Short-lived credentials are refreshed
- **WHEN** a secret has a TTL in Vault
- **THEN** the ExternalSecret refreshes before expiration

### Requirement: Secret names follow convention
The Secret names SHALL follow the convention `<service-name>-secrets` and contain keys matching environment variable names.

#### Scenario: Application reads secret as environment variable
- **WHEN** the application reads `DATABASE_URL` from the environment
- **THEN** the value comes from the `<service-name>-secrets` Secret

### Requirement: Vault paths per service
Vault SHALL organize secrets by service under the path `secret/data/<service-name>/<secret-type>`.

#### Scenario: Service retrieves database credentials
- **WHEN** the service needs database credentials
- **THEN** the ExternalSecret fetches from `secret/data/<service-name>/database`

### Requirement: Fallback to Kubernetes Secret for local development
The local development overlay SHALL provide static Secret manifests that can be applied when Vault is not available.

#### Scenario: Local development without Vault
- **WHEN** deploying to local kind cluster
- **THEN** the local overlay uses static Secrets instead of ExternalSecrets
