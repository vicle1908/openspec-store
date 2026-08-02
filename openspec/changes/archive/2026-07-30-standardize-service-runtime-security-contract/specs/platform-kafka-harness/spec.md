## ADDED Requirements

### Requirement: Kafka clients use encrypted authenticated least-privilege access

Every service producer, consumer, retry/DLQ publisher, topic initializer, and
CDC connector SHALL use encrypted authenticated Kafka access in
`production-contract` and `strict`. Each principal SHALL be authorized only for
its required cluster operations, topics, consumer groups, and transactional IDs.
An anonymous, plaintext, unverified, or over-broad client configuration MUST
fail before the client begins processing. Canonical acceptance of a service
producer or consumer SHALL start with an owning-service operation that creates
the admitted domain fact and SHALL link its outbox event to the exact Kafka
topic, partition, offset, consumer disposition, and durable downstream effect.
Direct Kafka injection MAY be used only as a focused negative or redelivery
fixture and MUST NOT establish end-to-end readiness.

#### Scenario: Authorized consumer joins its canonical group
- **WHEN** a service consumer authenticates with permission for its source topics and canonical group
- **THEN** it joins the group and processes an event caused by an owning-service operation using the existing delivery and idempotency contract
- **AND** evidence links the source outbox event, Kafka coordinates, consumer identity, and durable disposition

#### Scenario: Synthetic Kafka record is accepted
- **WHEN** a directly injected Kafka fixture is consumed successfully without an owning-service transaction and outbox fact
- **THEN** the result remains focused Kafka diagnostic evidence and cannot satisfy canonical operation acceptance

#### Scenario: Consumer uses another service group
- **WHEN** a consumer principal attempts to join a group outside its policy
- **THEN** Kafka denies the operation before records are delivered
- **AND** the denial is not published to a retry topic or DLQ

#### Scenario: Producer writes an unauthorized topic
- **WHEN** a producer principal attempts to write outside its allowed topic set
- **THEN** Kafka denies the record and the caller receives a typed non-retryable authorization failure

#### Scenario: Topic initializer has bounded administration rights
- **WHEN** a topic initializer authenticates successfully
- **THEN** it may reconcile only its declared topics and required configurations
- **AND** it cannot alter unrelated topics or cluster-wide security policy
