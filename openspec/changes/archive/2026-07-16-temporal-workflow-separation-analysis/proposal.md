# Proposal: Temporal Workflow Architecture - Service Separation Analysis

## Metadata

- **id**: temporal-workflow-separation-analysis
- **created**: 2026-07-16
- **authors**: [architecture review]
- **reviewers**: [architects, platform team]

---

## Summary

After analyzing the current Temporal workflow distribution across all microservices, this proposal recommends **against** creating dedicated workflow services. Instead, we should standardize the existing role-based deployment pattern and fix critical inconsistencies.

---

## Problem Statement

The platform has identified several issues with the current Temporal workflow architecture:

1. **Duplicate Workers**: order-service has 2 workers polling the same task queue
2. **Inconsistent Locations**: Workflows are in different directories across services
3. **Inconsistent Naming**: Activity and task queue naming varies between services

---

## Recommendation

**DO NOT separate workflows into dedicated services.**

The current workflow-to-service mapping aligns with domain ownership. Separating would introduce distributed transaction complexity without proportional benefits.

---

## Proposed Changes

1. Remove duplicate worker in order-service
2. Standardize workflow locations
3. Standardize naming conventions
4. Document best practices

---

## Impact

- **Risk**: Low (cosmetic/structural changes)
- **Effort**: Medium (affects 4 services)
- **Benefit**: Improved maintainability and reduced confusion
