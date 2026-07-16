# FR-EVAL-001 Aligned Predictions

- `FR-ID`: `FR-EVAL-001`
- `Title`: Aligned predictions
- `Phase`: Phase 5 - E1 Pilot
- `Development Order`: 22
- `Priority`: P0
- `Prerequisites`: `FR-DATA-005`, `FR-TRAIN-003`, `FR-REP-001`, `FR-REP-002`
- `Affected Packages`: `src/particleml/metrics.py`, `schemas/prediction.schema.json`, `tests/test_metrics.py`
- `Prototype Phase`: Yes
- `Source Type`: SRS baseline
- `Original SRS Section`: Software Requirements Specification §4, FR-EVAL-001

## Goal

Make per-jet predictions directly comparable across A-D, scales, seeds, and models on one fixed test identity set.

## Requirement Description

Every successful formal evaluation shall retain exactly one finite signal score and binary target for every fixed test jet in stable order, accompanied by stable jet identity, payload hash, and schema-valid metadata.

## High-Level Requirements

- Store metadata in `prediction.json` and payload in NPZ, Parquet, or HDF5.
- Validate row count, unique identities, binary targets, finite scores, and payload hash.
- Preserve exact ordered test identities and targets across paired conditions.
- Bind predictions to run record, split, subset, preprocessing, model, and code identity.

## Inputs

- Successful run checkpoint, fixed test view, resolved evaluation configuration, and validation-selected threshold data.

## Outputs

- Completed prediction metadata and payload under `predictions/<run-id>/`.

## Implementation Constraints

- Do not reorder or deduplicate silently during publication.
- Truth/audit fields beyond the binary target are excluded.

## Failure and Degradation

- Duplicate, missing, reordered, target-disagreeing, non-finite, or hash-mismatched payloads fail with `PREDICTION_*`.
- A failed prediction artifact makes the run ineligible for metrics and reporting.

## Acceptance Criteria

- Every fixed test jet appears exactly once in stable order.
- Metadata validates against schema version 1.0.0 with unknown properties rejected.
- Cross-condition identity and target equality checks pass before paired analysis.
- Payload-byte changes invalidate the recorded hash.

## Minimum Verification

- Prediction schema fixtures and identity order, duplicate, missing, target mismatch, non-finite, and payload-hash tests.
- E1 aligned A/D prediction smoke in RunPod.

## Out of Scope

- Aggregated-only scores without per-jet retained predictions.
- Comparing conditions on different test identities.

## Notes

- Schema source: `schemas/prediction.schema.json`.
