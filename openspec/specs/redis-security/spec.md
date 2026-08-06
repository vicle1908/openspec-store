# redis-security

## Purpose

Security hardening for Redis deployment: ACL-based authentication, TLS encryption, command restrictions, and network isolation.

## Requirements

### Requirement: RS-001: ACL Users

Redis ACLs SHALL be enabled. Each service SHALL have a dedicated ACL user with only the commands and key patterns it needs. The default user SHALL be disabled in production.

#### Scenario: Catalog Service ACL
Given the `catalog-svc` ACL user
When the catalog-service authenticates
Then it shall only have access to keys matching `catalog:quote:*`
And it shall have `+@read +@write +@fast` permissions
And it shall NOT have `+@dangerous` or `+@admin` permissions

#### Scenario: Notification Service ACL
Given the `notification-svc` ACL user
When the notification-service authenticates
Then it shall only have access to keys matching `notification:*` and `rate:*`
And it shall have `+@read +@write +@fast` permissions

#### Scenario: Default User Disabled
Given the Redis server in production mode
When no explicit user is provided
Then the connection shall be rejected
And the error message shall indicate ACL denial

### Requirement: RS-002: TLS Encryption

TLS SHALL be enabled for all Redis communication. The non-TLS port SHALL be disabled in production. Self-signed certificates SHALL be used for local development; cert-manager SHALL be used in Kubernetes.

#### Scenario: TLS-Only Mode
Given a Redis node with TLS enabled
When the node starts
Then port 6379 (non-TLS) shall be disabled
And port 6380 (TLS) shall be enabled
And `tls-cert-file`, `tls-key-file`, `tls-ca-cert-file` shall be configured

#### Scenario: Client TLS Connection
Given a go-redis client with TLS configuration
When connecting to Redis
Then the connection shall use TLS 1.2 or higher
And the server certificate shall be verified against the CA
And the client certificate shall be presented for mutual TLS

#### Scenario: Local Development Certificates
Given the local development environment
When the cluster starts
Then self-signed certificates shall be generated
And stored in `deploy/certs/redis/`
And mounted into Redis containers

### Requirement: RS-003: Command Restrictions

Dangerous commands SHALL be disabled via `rename-command` in production. The following commands SHALL be restricted: `FLUSHALL`, `DEBUG`, `CONFIG`.

#### Scenario: FLUSHALL Blocked
Given a Redis node with command restrictions
When `FLUSHALL` is executed
Then the error `ERR unknown command` shall be returned
And no data shall be deleted

#### Scenario: CONFIG Blocked
Given a Redis node with command restrictions
When `CONFIG GET *` is executed
Then the error `ERR unknown command` shall be returned
And no configuration shall be exposed

### Requirement: RS-004: Network Isolation

Redis SHALL NOT be exposed to the public internet. In Docker Compose, Redis ports SHALL only be accessible from within the `platform-network`. In Kubernetes, NetworkPolicy SHALL restrict ingress to authorized services only.

#### Scenario: Docker Compose Network
Given the Docker Compose topology
When Redis containers start
Then port 6379/6380 shall only be accessible from `platform-network`
And external access shall be blocked

#### Scenario: Kubernetes NetworkPolicy
Given the Kubernetes deployment
When the NetworkPolicy is applied
Then ingress to Redis pods shall only be allowed from the `go-microservices` namespace
And egress shall be restricted to cluster-internal traffic

### Requirement: RS-005: Credential Management

Redis passwords and ACL credentials SHALL be stored in Kubernetes Secrets (not ConfigMaps). For Docker Compose, credentials SHALL be in environment variables (not hardcoded in compose files).

#### Scenario: Kubernetes Secret
Given the `redis-credentials` Secret
When a Redis pod starts
Then it shall read the password from the Secret
And the password shall NOT be logged or exposed in environment dumps

#### Scenario: Docker Compose Credentials
Given the Docker Compose file
When `docker compose config` is executed
Then passwords shall be referenced via environment variables
And shall NOT appear in the rendered config

### Requirement: RS-006: Inter-Node TLS

Redis cluster nodes SHALL communicate over TLS. The `tls-cluster` directive SHALL be enabled. Node-to-node communication SHALL use mutual TLS with client certificates.

#### Scenario: Cluster TLS
Given a Redis cluster with TLS enabled
When nodes communicate via gossip protocol
Then all gossip messages shall be encrypted
And node identity shall be verified via certificates
