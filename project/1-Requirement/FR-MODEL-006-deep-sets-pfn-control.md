# FR-MODEL-006 Deep Sets/PFN Control

- `FR-ID`: `FR-MODEL-006`
- `Title`: Deep Sets/PFN control
- `Phase`: Phase 7 - E3 and Reporting
- `Development Order`: 24
- `Priority`: P1
- `Prerequisites`: `FR-DATA-005`, `FR-TRAIN-002`, `FR-TRAIN-003`, `FR-EVAL-001`, `FR-EVAL-002`
- `Affected Packages`: `src/particleml/`, `configs/`, `tests/test_baseline.py`
- `Prototype Phase`: No
- `Source Type`: SRS baseline
- `Original SRS Section`: Software Requirements Specification §4, FR-MODEL-006

## Goal

Provide the required publication-strength control for whether the A-versus-D feature ranking persists outside the pretrained OmniLearned measurement system.

## Requirement Description

The repository shall implement a small masked Deep Sets/PFN-style binary classifier using a per-particle MLP, frozen pooling choice, and binary head. It shall reuse the same views, split/subset identities, preprocessing, run records, predictions, and metrics.

## High-Level Requirements

- Consume masks explicitly and exclude padding from pooling.
- Freeze architecture, pooling, parameter count, optimizer, and stopping policy before E3.
- Run A versus D at frozen `n_max` with three seeds.
- Emit the same schema-valid records and aligned predictions as the primary model.
- Do not consume audit/global variables.

## Inputs

- Completed A/D views at frozen `n_max`, common preprocessing, E3 configuration, and three model seeds.

## Outputs

- Baseline checkpoints, run records, aligned predictions, metrics, and paired A-D comparisons.

## Implementation Constraints

- Keep the implementation independently testable and inside the modern Python boundary.
- Do not tune the baseline using test-set outcomes.

## Failure and Degradation

- Mask, shape, identity, configuration, or training failures remain visible as failed E3 run records.
- If the required baseline cannot complete, E3 is formally deferred and claim scope is narrowed.

## Acceptance Criteria

- Mask and padding invariance tests pass.
- A and D complete or retain explicit failures for all three seeds at frozen `n_max`.
- Prediction identities and targets align exactly with the primary fixed test set.
- E3 paired statistics use the standard evaluation contracts.

## Minimum Verification

- `pytest -q tests/test_baseline.py`
- Mask, shape, pooling, parameter/config record, train-smoke, prediction-contract, and matrix-completeness tests in cloud CI.
- Cloud E3 execution for AC-E3-001.

## Out of Scope

- Broad architecture benchmarking.
- Mandatory random-initialized OmniLearned comparisons.

## Notes

- Random-initialized OmniLearned remains optional; Deep Sets/PFN is the required control.
