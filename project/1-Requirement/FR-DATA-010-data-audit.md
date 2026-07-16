# FR-DATA-010 Data Audit

- `FR-ID`: `FR-DATA-010`
- `Title`: Data audit
- `Phase`: Phase 3 - CMSSW Extractor and E0
- `Development Order`: 12
- `Priority`: P0
- `Prerequisites`: `FR-DATA-002`, `FR-DATA-003`, `FR-DATA-004`, `FR-DATA-005`, `FR-DATA-006`, `FR-DATA-009`, `FR-REP-001`
- `Affected Packages`: `src/particleml/dataset.py`, `src/particleml/metrics.py`, `src/particleml/cli.py`, `tests/test_audit.py`
- `Prototype Phase`: Yes
- `Source Type`: SRS baseline
- `Original SRS Section`: Software Requirements Specification §4, FR-DATA-010

## Goal

Produce the retained E0 evidence needed to decide whether the CMS corpus, feature decoding, yields, leakage controls, and cloud budget are fit for E0.5 and E1.

## Requirement Description

The system shall aggregate extraction and canonical artifacts into a structured audit covering product availability, labels, features, masks, missingness, counts, leakage, hashes, throughput, storage, yield, and projected cost.

## High-Level Requirements

- Report daughter resolution, label cutflow, finiteness, units, track-state rates, truncation, masks, padding, and class/split/record counts.
- Verify split overlap, A-D identity equivalence, QCD mixture, confound exclusions, and a shuffled-label probe.
- Measure source bytes, CPU/event, wall time, throughput, failures, compact/canonical/view storage, and projected E0/E1/E2 cost with 25% reserve.
- Block E1 when the charged no-track rate exceeds 1% or any mandatory AC-E0-001 item fails.
- Freeze `n_max`, cuts, units, mixture, control, pileup, and missing-track policies in the audit decision.

## Inputs

- Source/split manifests, extraction reports, compact ROOT, canonical HDF5, A-D views, preprocessing state, and cloud resource measurements.

## Outputs

- Schema/contract-validated E0 data, yield, leakage, and cost audit.
- Explicit pass, fail, or review-required status for every AC-E0-001 gate.

## Implementation Constraints

- Values must be computed from retained cloud artifacts, not copied from local notebook state.
- Local execution cannot change formal gate status.

## Failure and Degradation

- Any missing mandatory evidence, invalid unit, non-finite value, overlap, leakage, hash mismatch, or threshold breach fails closed.
- If `10^5` jets per class is infeasible, stop and publish a Research Plan v0.4.x amendment before E0.5.

## Acceptance Criteria

- Every AC-E0-001 checklist item has an evidence path, hash, and result.
- The audit includes measured host performance and cost rather than provider assumptions.
- Charged no-track fraction is computed from track states with denominator validation.
- E0 status blocks downstream orchestration unless all mandatory gates pass.

## Minimum Verification

- `pytest -q tests/test_audit.py` for deterministic fixtures, thresholds, shuffled labels, missing fields, and gate aggregation.
- Qualified-host E0 run retaining manifests, artifacts, logs, measurements, hashes, and `COMPLETED.json`.

## Out of Scope

- Claiming scientific model performance from E0.
- Automatically changing the research protocol in response to failed audits.

## Notes

- Evidence target and exit gate: AC-E0-001.
