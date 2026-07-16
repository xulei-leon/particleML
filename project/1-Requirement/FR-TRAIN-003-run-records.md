# FR-TRAIN-003 Run Records

- `FR-ID`: `FR-TRAIN-003`
- `Title`: Run records
- `Phase`: Phase 5 - E1 Pilot
- `Development Order`: 20
- `Priority`: P0
- `Prerequisites`: `FR-TRAIN-002`, `FR-REP-001`, `FR-REP-002`
- `Affected Packages`: `src/particleml/experiment.py`, `src/particleml/contracts.py`, `schemas/run-record.schema.json`, `tests/test_experiment.py`
- `Prototype Phase`: Yes
- `Source Type`: SRS baseline
- `Original SRS Section`: Software Requirements Specification §4, FR-TRAIN-003

## Goal

Retain a complete, machine-valid provenance and outcome record for every attempted formal training run.

## Requirement Description

Each attempt shall emit a final `run-record.json` conforming to JSON Schema Draft 2020-12 version 1.0.0, whether successful, failed, timed out, or interrupted.

## High-Level Requirements

- Record code, data, split, subset, preprocessing, index, checkpoint, condition, hyperparameters, seeds, and resolved configuration.
- Record image/dependency lock, Python/PyTorch/CUDA/driver, GPU model/VRAM, timing, peak memory, storage, logs, artifacts, and metrics when valid.
- For failures, include stable code/message and available evidence without success-only metrics.
- Reject unknown properties at defined schema boundaries.
- Validate before publication and aggregation.

## Inputs

- Resolved `RunSpec`, environment record, execution events, artifact hashes, metrics, or failure information.

## Outputs

- Immutable `runs/<run-id>/run-record.json` and completion marker.

## Implementation Constraints

- UTC timestamps end in `Z`; hashes are lowercase 64-character SHA-256.
- Credentials, tokens, and signed URLs must not enter records or logs.

## Failure and Degradation

- Schema-invalid records cannot be published as completed or consumed downstream.
- If run-record finalization fails after execution starts, retain partial logs and a structured orchestration failure.

## Acceptance Criteria

- Representative success, failure, timeout, and interruption fixtures validate.
- Required provenance is present and cross-artifact hashes agree.
- Unknown fields and invalid conditional combinations are rejected.
- Every E1-E3 attempted condition has exactly one visible final outcome record.

## Minimum Verification

- Valid/invalid schema fixtures and `contracts validate` tests.
- Environment, artifact-hash, success/failure conditional, unknown-property, and secret-redaction tests.

## Out of Scope

- Inferring a successful result from logs or configuration alone.
- Editing failed records into successful ones.

## Notes

- Schema source: `schemas/run-record.schema.json`.
