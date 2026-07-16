# FR-EVAL-002 Required Metrics

- `FR-ID`: `FR-EVAL-002`
- `Title`: Required metrics
- `Phase`: Phase 5 - E1 Pilot
- `Development Order`: 23
- `Priority`: P0
- `Prerequisites`: `FR-EVAL-001`
- `Affected Packages`: `src/particleml/metrics.py`, `tests/test_metrics.py`
- `Prototype Phase`: Yes
- `Source Type`: SRS baseline
- `Original SRS Section`: Software Requirements Specification §4, FR-EVAL-002

## Goal

Compute the preregistered per-run performance and data-efficiency quantities with explicit numerical edge-case behavior.

## Requirement Description

The evaluator shall compute ROC AUC, background rejection at signal efficiencies 0.30 and 0.50, auxiliary accuracy using a validation-selected threshold, and the guarded data-efficiency summary.

## High-Level Requirements

- Use average-rank/Mann-Whitney ROC AUC and reject a single-class test set.
- Interpolate on full non-dropped ROC points at the two target signal efficiencies.
- Serialize rejection as `null`, not infinity, when observed background efficiency is zero; retain counts.
- Use only a validation-selected accuracy threshold recorded in the run record.
- Omit unstable `auc_gap_fraction` and report raw paired AUC differences instead.

## Inputs

- Validated prediction artifact, validation-selected threshold, frozen `n_max`, and evaluation configuration.

## Outputs

- Deterministic per-run metric record with definitions, edge-case fields, and provenance.

## Implementation Constraints

- No hidden threshold tuning on the test set.
- Metric definitions remain centralized in `metrics.py`, not training or notebooks.

## Failure and Degradation

- Single class, non-finite score, invalid target, or inconsistent counts fails with `METRIC_*`.
- Unstable data-efficiency ratios degrade to the specified raw-difference output, with reason recorded.

## Acceptance Criteria

- Golden fixtures reproduce known AUC and interpolated rejection values.
- Zero-background rejection serializes valid JSON without infinity.
- Accuracy uses the recorded validation threshold.
- Ratio instability follows the denominator and bootstrap rules from specification §8.1.

## Minimum Verification

- Known AUC/rejection/accuracy fixtures, tied-score cases, zero background, single class, non-finite values, and unstable-ratio fallback tests.
- `pytest -q tests/test_metrics.py` in cloud CI.

## Out of Scope

- Unregistered metrics selected after viewing E2 results.
- Test-set threshold optimization.

## Notes

- The data-efficiency summary supports RQ2 and Table T3.
