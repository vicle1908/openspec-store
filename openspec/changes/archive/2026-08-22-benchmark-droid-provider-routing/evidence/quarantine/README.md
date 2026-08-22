# Benchmark Evidence Incident

## What happened

1. 32 calibration records and 18 partial repeat-2 records were collected.
2. The data was identified as unreliable due to multiple harness defects (see below).
3. During cleanup, the quarantine file was accidentally overwritten with a freshly created empty canonical file.
4. The original JSONL records are destroyed and must not be represented as preserved evidence.
5. The benchmark restarts from zero after harness correction.

## Harness defects identified

- S3 (multi-turn recall): `droid exec --session-id` does not continue context; all providers scored 0.
- S4 (planning): Scoring regex too strict; models format steps differently.
- S5/S7 (keyword matching): Scoring functions miss valid findings that models express with different vocabulary.
- S6 (code edit): No hallucination penalty; model could "edit" files without actually fixing bugs.
- Reasoning effort: All scenarios used `--reasoning-effort none`, contradicting the approved design.
- Excerpts: Only 120 characters retained — insufficient for audit.
- Baseline: OmniRoute at localhost:20128 is dead; all baseline runs fail with "Exec failed".

## Status

Benchmark restarted from zero after harness repair. Previous records excluded from all conclusions.
