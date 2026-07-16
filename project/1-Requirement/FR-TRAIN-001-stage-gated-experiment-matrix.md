# FR-TRAIN-001 Stage-Gated Experiment Matrix

- `FR-ID`: `FR-TRAIN-001`
- `Title`: Stage-gated experiment matrix
- `Phase`: Phase 5 - E1 Pilot
- `Development Order`: 18
- `Priority`: P0
- `Prerequisites`: `FR-DATA-010`, `FR-MODEL-004`, `FR-MODEL-005`, `FR-REP-002`
- `Affected Packages`: `src/particleml/experiment.py`, `src/particleml/cli.py`, `configs/`, `tests/test_experiment.py`
- `Prototype Phase`: Yes
- `Source Type`: SRS baseline
- `Original SRS Section`: Software Requirements Specification §4, FR-TRAIN-001

## Goal

Enforce the E0-to-E3 scientific decision sequence and generate complete experiment matrices from frozen configuration rather than manual commands.

## Requirement Description

The orchestrator shall model E0, E0.5, E1, E2, and E3 explicitly and refuse to start a stage until mandatory upstream gate records pass. E1/E2/E3 conditions shall be derived deterministically from approved feature configurations, scales, model conditions, and seeds.

## High-Level Requirements

- Validate prerequisite gate records and artifact hashes before planning or starting work.
- Generate E1 A/D pilot conditions and the complete E2 A-D/scale/three-seed matrix.
- Preserve optional versus mandatory E3 conditions explicitly.
- Reject unapproved matrix changes and hand-entered omissions.
- Provide a dry-run that resolves the matrix without executing or publishing artifacts.

## Inputs

- Versioned experiment YAML, validated gate records, frozen views/subsets, model policy, and seed list.

## Outputs

- Deterministic stage ledger and condition matrix with stable condition identities.
- Gate-block diagnostics or runnable `RunSpec` entries.

## Implementation Constraints

- No automatic retry and no silent condition dropping.
- Matrix changes affecting scale, features, endpoint, or claims follow change control.

## Failure and Degradation

- Missing, failed, stale, or schema-invalid prerequisites fail with `RUN_GATE_BLOCKED`/exit code 8.
- Approved supervised fallback may generate a revised matrix only with narrowed claims.

## Acceptance Criteria

- A stage cannot start with an unmet prior gate.
- E2 matrix cardinality and identities match frozen configuration exactly.
- Dry-run exposes dependencies, hashes, commands, and blocked conditions.
- Failed/optional conditions remain distinguishable in the stage ledger.

## Minimum Verification

- `pytest -q tests/test_experiment.py::test_gate_order_and_matrix`
- Missing/stale gate, matrix completeness, fallback, optional control, and dry-run tests.

## Out of Scope

- Distributed schedulers or online job services.
- Adaptive experiment expansion based on observed test results.

## Notes

- E2 cannot start until E0/E1 measurements support the approved budget with 25% reserve.
