# FR-EVAL-004 Evidence-Derived Reports

- `FR-ID`: `FR-EVAL-004`
- `Title`: Evidence-derived reports
- `Phase`: Phase 7 - E3 and Reporting
- `Development Order`: 27
- `Priority`: P1
- `Prerequisites`: `FR-EVAL-002`, `FR-EVAL-003`, `FR-MODEL-005`, `FR-MODEL-006`, `FR-REP-003`
- `Affected Packages`: `src/particleml/reporting.py`, `tests/test_reporting.py`, report configurations
- `Prototype Phase`: No
- `Source Type`: SRS baseline
- `Original SRS Section`: Software Requirements Specification §4, FR-EVAL-004

## Goal

Generate publication figures, tables, matrix status, and claim eligibility reproducibly from validated evidence only.

## Requirement Description

The reporting service shall aggregate schema-valid run records and prediction/comparison artifacts, preserve planned/failed/incomplete conditions, generate the specified paper evidence, and mark claims eligible only when every mapped requirement and gate passes.

## High-Level Requirements

- Generate T1-T4 and F1-F3 inputs from retained artifacts rather than manual transcription.
- Verify artifact hashes, schema versions, run status, matrix completeness, and prediction alignment before aggregation.
- Show every seed and the declared uncertainty convention.
- Keep failed and missing conditions visible.
- Apply supervised-fallback and deferred-E3 claim narrowing automatically.

## Inputs

- Validated E0-E3 audits, run records, predictions, paired comparisons, traceability mappings, and report configuration.

## Outputs

- Reproducible tables, figures, matrix-status report, and claim-eligibility ledger under `reports/`.

## Implementation Constraints

- Reporting cannot invent results, infer completion from configuration, or accept manual spreadsheet corrections as source data.
- Generated outputs and inputs are content-hashed and completion-marked.

## Failure and Degradation

- Invalid/missing evidence blocks claim-ready status while still allowing an honest incomplete-status report.
- Fallback or deferred controls narrow claim text rather than being hidden.

## Acceptance Criteria

- Aggregation rejects schema-invalid or hash-mismatched inputs.
- Complete, failed, missing, and planned conditions are distinguishable.
- Claim ledger never exceeds the weakest upstream status.
- Rebuilding from identical validated inputs reproduces report content and hashes.

## Minimum Verification

- `pytest -q tests/test_reporting.py`
- Completeness, ineligible-claim, fallback, failed-run visibility, deterministic aggregation, and hash tests.

## Out of Scope

- Manual result editing.
- Claims beyond the controlled CMS 2015 feature-availability study.

## Notes

- Planned evidence is defined in traceability matrix §4.
