# k8s-hpa-template Specification

## ADDED Requirements

### Requirement: CPU-based autoscaling
The HPA template SHALL target 70% average CPU utilization as the primary scaling metric.

#### Scenario: CPU spike triggers scale-up
- **WHEN** average CPU utilization exceeds 70% for the stabilization window
- **THEN** HPA increases the replica count up to maxReplicas

#### Scenario: CPU normalizes triggers scale-down
- **WHEN** average CPU utilization drops below 70% for the stabilization window
- **THEN** HPA decreases the replica count down to minReplicas

### Requirement: Memory-based autoscaling
The HPA template SHALL include memory utilization as a secondary metric targeting 80% average utilization.

#### Scenario: Memory pressure triggers scale-up
- **WHEN** average memory utilization exceeds 80% for the stabilization window
- **THEN** HPA increases the replica count

#### Scenario: Both metrics considered for scaling decision
- **WHEN** CPU is below threshold but memory is above
- **THEN** HPA uses the metric with the higher utilization for scaling decisions

### Requirement: Configurable min/max replicas
The HPA template SHALL allow configuration of minReplicas and maxReplicas via Kustomize patches per environment.

#### Scenario: Production has higher minReplicas
- **WHEN** the production overlay is applied
- **THEN** minReplicas is set to 3

#### Scenario: Staging has lower minReplicas
- **WHEN** the staging overlay is applied
- **THEN** minReplicas is set to 2

### Requirement: Scale-down stabilization
The HPA template SHALL configure a scale-down stabilization window of 300 seconds to prevent thrashing during volatile traffic patterns.

#### Scenario: Temporary traffic drop does not trigger immediate scale-down
- **WHEN** traffic drops temporarily but will likely recover
- **THEN** HPA waits 300 seconds before scaling down

### Requirement: Scale-up burst policy
The HPA template SHALL configure aggressive scale-up policies allowing 100% increase in pods within 15 seconds to handle traffic spikes.

#### Scenario: Traffic spike triggers rapid scale-up
- **WHEN** traffic increases suddenly
- **THEN** HPA can double the replica count every 15 seconds up to maxReplicas

### Requirement: HPA behavior configuration
The HPA template SHALL use the `behavior` field with explicit scale policies for both scale-up and scale-down.

#### Scenario: Pod-based scaling policy limits absolute changes
- **WHEN** scaling with a large existing replica count
- **THEN** the Pods policy limits the absolute number of pods changed per period
