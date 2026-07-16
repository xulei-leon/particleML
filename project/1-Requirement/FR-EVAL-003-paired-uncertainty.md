# FR-EVAL-003 Paired Uncertainty

- `FR-ID`: `FR-EVAL-003`
- `Title`: Paired uncertainty
- `Phase`: Phase 6 - E2 Core Matrix
- `Development Order`: 25
- `Priority`: P0
- `Prerequisites`: `FR-EVAL-001`, `FR-EVAL-002`, `FR-TRAIN-004`
- `Affected Packages`: `src/particleml/metrics.py`, `tests/test_metrics.py`
- `Prototype Phase`: No
- `Source Type`: SRS baseline
- `Original SRS Section`: Software Requirements Specification §4, FR-EVAL-003

## Goal

Quantify feature-configuration differences using paired event-level uncertainty while keeping model-seed variation separate.

## Requirement Description

For each approved scale, the system shall compute A-B, B-C, C-D, C-A, and D-A contrasts on exactly aligned predictions using at least 1,000 fixed-seed, class-stratified paired bootstrap replicates.

## High-Level Requirements

- Join by exact ordered jet identity and verify identical targets before resampling.
- Use NumPy `PCG64`, a recorded bootstrap seed, and the same resampled indices for both conditions and all metrics in a contrast.
- Report the 2.5th and 97.5th percentiles of finite replicate differences.
- Report discarded non-finite replicate count and fail when it exceeds 1%.
- Show every model seed plus mean and sample standard deviation separately from event-bootstrap intervals.

## Inputs

- Validated aligned prediction pairs, contrast list, scale, bootstrap seed, and replicate count.

## Outputs

- Content-addressed paired-comparison artifacts and seed-variation summaries.

## Implementation Constraints

- Do not combine seed variation and event bootstrap into one standard error.
- Five-seed expansion is permitted only for preregistered close comparisons.

## Failure and Degradation

- Identity reorder/duplication/missingness, target disagreement, invalid class composition, or excessive non-finite replicates fails paired analysis.
- Do not fall back to unpaired uncertainty.

## Acceptance Criteria

- All five required contrasts exist for every eligible E2 scale.
- Repeated execution with the same seed produces identical samples and intervals.
- Paired samples preserve class strata and use common indices for both sides.
- Seed-level and event-level uncertainty remain separately labeled.

## Minimum Verification

- Deterministic stratified paired-bootstrap golden fixtures.
- Identity mismatch, target mismatch, discard threshold, percentile, contrast completeness, and seed-summary tests.

## Out of Scope

- Unpaired bootstrap for A-D contrasts.
- Post-hoc seed expansion outside the preregistered rule.

## Notes

- Evidence target: E2/E3 comparison artifacts, Figures F2/F3, and Tables T3/T4.
